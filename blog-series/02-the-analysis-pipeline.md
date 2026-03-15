---
title: "Building CDDBS — Part 2: Inside the Analysis Pipeline"
published: false
description: "A deep dive into how CDDBS fetches articles, constructs prompts, calls Gemini, and parses structured intelligence briefings from LLM output."
tags: ai, python, llm, backend
series: "Building CDDBS"
---

## The Pipeline Problem

Most LLM tutorials show you how to call an API and print the response. Real systems need more. You need to fetch data from external sources, construct prompts that constrain the output format, parse responses that don't always follow your instructions, persist results to a database, and handle every failure mode gracefully — all without blocking the user.

CDDBS solves this with a 6-stage background pipeline. This post walks through every stage with actual code from the production system.

## Stage 1: Article Fetch

When a user requests an analysis of a media outlet, the first thing we need is content to analyze. CDDBS uses SerpAPI's Google News engine to fetch recent articles.

```python
# src/cddbs/pipeline/fetch.py (simplified)

# Map short date_filter codes to Google News 'when:' query values
_WHEN_MAP = {
    "h": "1h",
    "d": "1d",
    "w": "7d",
    "m": "30d",
    "y": "1y",
}

def fetch_articles(outlet, country, num_articles=3, url=None,
                   api_key=None, time_period=None):
    if not api_key:
        return generate_mock_articles(outlet)

    query = f'"{outlet}"'
    if url:
        clean_url = url.replace("https://", "").replace("http://", "").split("/")[0]
        query = f'"{outlet}" site:{clean_url}'

    # google_news engine does NOT support the tbs parameter.
    # Date filtering must be done via 'when:' operator in the query string.
    if time_period:
        when_value = _WHEN_MAP.get(time_period, time_period)
        query = f"{query} when:{when_value}"

    params = {
        "engine": "google_news",
        "q": query,
        "gl": normalize_country(country),
        "api_key": api_key,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("news_results", [])
```

A few things to note:

**Country normalization.** SerpAPI expects ISO country codes (`us`, `ru`, `gb`), but users type "Russia" or "United States." The `normalize_country()` function maps natural language country names to their codes. Small detail, large UX impact.

**Date filtering.** The SerpAPI `google_news` engine does **not** support the `tbs` parameter. Passing `tbs=qdr:d` silently fails — articles come back unfiltered. The correct approach is the `when:` query operator embedded directly in the search string: `when:1d` for last 24 hours, `when:7d` for last week. We discovered this through silent failures in early testing and patched it in production. This matters because disinformation campaigns often intensify around specific events — an analyst tracking a narrative spike needs yesterday's articles, not last month's.

**Mock fallback.** When no API key is configured, the system generates mock articles rather than crashing. This is critical for local development and testing — you don't want your 142 tests to require a live SerpAPI key.

## Stage 2: Prompt Construction

This is where most of the engineering lives. A raw LLM call with "analyze these articles for disinformation" produces vague, unstructured prose. CDDBS uses a 263-line system prompt that transforms Gemini into a structured intelligence analyst.

### The System Prompt (v1.3)

The system prompt is loaded from a versioned text file:

```python
# src/cddbs/utils/system_prompt.py
_cached_prompt = None

def load_system_prompt():
    global _cached_prompt
    if _cached_prompt:
        return _cached_prompt

    prompt_path = Path(__file__).parent.parent / "data" / "system_prompt_v1.3.txt"
    _cached_prompt = prompt_path.read_text()
    return _cached_prompt
```

Caching matters. This function is called once per analysis run, but in a batch of 5 runs, reading the file 5 times is wasteful. The module-level cache ensures a single read.

### What the System Prompt Enforces

The prompt defines an analyst persona and constrains output across several dimensions:

**7 mandatory sections.** Every briefing must contain: Executive Summary, Key Findings, Subject Profile, Narrative Analysis, Confidence Assessment, Limitations & Caveats, and Methodology. If Gemini omits a section, the quality scorer penalizes it.

**Evidence typing.** Every claim must be attributed using a typed evidence system:

```
[POST]     — Specific social media post with URL
[PATTERN]  — Behavioral pattern with specific metrics
[NETWORK]  — Relationship data with named accounts
[METADATA] — Account metadata (creation date, bio)
[EXTERNAL] — Third-party source with organization name
[FORWARD]  — Telegram forwarding chain with source/delay
[CHANNEL_META] — Telegram channel metadata
```

This isn't decorative. The evidence type system makes hallucination *auditable*. When the LLM tags something as `[POST]`, an analyst can verify whether that post exists. When it says `[PATTERN]`, the metric must be present — "75% retweet ratio" not "high retweet activity."

**Attribution language rules.** The prompt explicitly defines what language is permitted:

```
"The account posted..."         — observed facts
"This is consistent with..."    — pattern matching
"This suggests..."              — inferences
"We assess with [level]..."     — analytical judgments

FORBIDDEN: "It is clear that", "Obviously", "definitely"
```

This eliminates the LLM's natural tendency to express false certainty — which is the single most dangerous failure mode for an intelligence product.

**Known narrative patterns.** All 18 narrative IDs and their keywords are embedded directly in the system prompt. This gives Gemini a reference frame: it's not guessing what "Ukraine conflict revisionism" looks like; it has specific patterns to match against.

### User Prompt Construction

The user prompt is built from the fetched articles:

```python
# src/cddbs/pipeline/prompt_templates.py (simplified)
def get_consolidated_prompt(outlet, country, articles, url=None):
    article_text = ""
    for i, article in enumerate(articles, 1):
        article_text += f"\n--- Article {i} ---\n"
        article_text += f"Title: {article.get('title', 'N/A')}\n"
        article_text += f"Source: {article.get('link', 'N/A')}\n"
        article_text += f"Snippet: {article.get('snippet', 'N/A')}\n"
        if article.get('full_text'):
            article_text += f"Full Text: {article['full_text']}\n"

    return f"""Analyze the following media outlet for potential
disinformation patterns:

Outlet: {outlet}
Country: {country}
URL: {url or 'N/A'}

Articles collected:
{article_text}

Produce a structured intelligence briefing following the format
specified in your system instructions."""
```

The prompt is deliberately minimal. All the structural constraints live in the system prompt, which is stable across runs. The user prompt just provides the data.

## Stage 3: LLM Call and Response Parsing

The Gemini call is straightforward. The response parsing is not.

```python
# src/cddbs/pipeline/orchestrator.py (simplified)
def call_gemini(prompt, system_prompt, api_key, model="gemini-2.5-flash"):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1
        )
    )
    return response.text
```

**Temperature 0.1.** We want deterministic output. A temperature of 0 gives identical output for identical input; 0.1 adds just enough variation to avoid repetitive phrasing while keeping the structure stable.

### The Parsing Problem

Gemini is asked to return JSON, but it often wraps the response in markdown code blocks, or returns a mix of JSON and prose. The parser handles this with a fallback chain:

```python
def parse_response(raw_text):
    # Try 1: Direct JSON parse
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    # Try 2: Extract from markdown code block
    match = re.search(r'```(?:json)?\s*([\s\S]*?)```', raw_text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try 3: Find first { ... } block
    match = re.search(r'\{[\s\S]*\}', raw_text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Fallback: return raw text as unstructured briefing
    return {"final_briefing": raw_text, "parse_failed": True}
```

Three things to note here:

1. **Never crash on bad output.** The worst case is an unstructured briefing. Still useful — just without individual article analyses.
2. **Markdown stripping.** Gemini loves wrapping JSON in ` ```json ``` ` blocks. The regex handles this transparently.
3. **Greedy JSON extraction.** If the response has prose before and after the JSON, the `\{[\s\S]*\}` regex pulls out the largest JSON object. This handles cases where Gemini adds "Here's the analysis:" before the actual output.

## Stage 4: Database Persistence

After parsing, results are persisted in a single transaction:

```python
# Simplified from orchestrator.py
def persist_results(db, report_id, parsed, articles, outlet):
    report = db.query(Report).get(report_id)
    report.final_report = parsed.get("final_briefing", "")
    report.raw_response = raw_text
    report.data = {
        "status": "completed",
        "articles_analyzed": len(articles),
        "analysis_date": datetime.now(UTC).isoformat()
    }

    # Persist articles
    for article_data in articles:
        article = Article(
            report_id=report_id,
            outlet_id=outlet_record.id,
            title=article_data.get("title"),
            link=article_data.get("link"),
            snippet=article_data.get("snippet")
        )
        db.add(article)

    db.commit()
```

The raw Gemini response is stored alongside the parsed briefing. This is an audit trail — if the quality scorer flags something unexpected, you can go back and see exactly what the LLM returned before parsing.

## Stage 5: Quality Scoring

This stage deserves its own post (Part 3), but the integration point matters here:

```python
# In the pipeline, after persistence
try:
    score_briefing(db, report_id)
except Exception as e:
    print(f"Quality scoring failed: {e}")
    # Non-fatal — briefing is still delivered
```

The `try/except` is load-bearing. Quality scoring is a post-processing step that adds value but isn't required for the core product. If the briefing text is malformed or the scorer has a bug, the analyst still gets their report.

## Stage 6: Narrative Matching

Same pattern — non-fatal enrichment:

```python
try:
    match_narratives_from_report(db, report_id)
except Exception as e:
    print(f"Narrative matching failed: {e}")
```

The narrative matcher reads the full report text, scans for keyword hits across all 18 narratives, deduplicates, and creates `NarrativeMatch` rows. Details in Part 3.

## The Async Execution Model

The entire pipeline runs as a FastAPI background task:

```python
@app.post("/analysis-runs")
def create_analysis_run(
    request: RunCreateRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
):
    # Create placeholder report
    report = Report(outlet=request.outlet, country=request.country)
    report.data = {"status": "queued"}
    db.add(report)
    db.commit()

    # Schedule pipeline as a background task
    background_tasks.add_task(
        _run_analysis_job,
        report_id=report.id,
        outlet=request.outlet,
        country=request.country,
        # ... other params
    )

    return {"id": report.id, "status": "queued"}
```

The frontend polls for completion:

```typescript
// Frontend: TanStack React Query with conditional polling
const { data: run } = useQuery({
  queryKey: ["run", runId],
  queryFn: () => fetchRun(runId),
  refetchInterval: (query) => {
    const status = query.state.data?.data?.status;
    return status === "completed" || status === "failed"
      ? false  // stop polling
      : 3000;  // poll every 3 seconds
  }
});
```

Why FastAPI `BackgroundTasks` instead of Celery? Cost discipline. Celery requires a message broker (Redis or RabbitMQ), which means another service to deploy and pay for. FastAPI's built-in `BackgroundTasks` runs the job in the same process after the HTTP response is sent — zero extra infrastructure. For our throughput (single-digit concurrent analyses on Render free tier), this is entirely adequate. If CDDBS needed to handle hundreds of concurrent analyses, we'd switch to a proper task queue. Until then, the simplest solution that works is the right one.

## Platform Routing

Sprint 5 added a layer on top of Stage 1 — platform routing. Instead of always fetching from SerpAPI, the pipeline can now route to different data sources:

```python
def _fetch_for_platform(platform, outlet, country, num_articles,
                        url, serpapi_key, twitter_bearer_token,
                        date_filter):
    if platform == "twitter":
        try:
            from src.cddbs.pipeline.twitter_client import (
                fetch_twitter_data, briefing_input_to_articles
            )
            briefing_input = fetch_twitter_data(
                handle=outlet,
                num_posts=num_articles or 10,
                bearer_token=twitter_bearer_token
            )
            if briefing_input and briefing_input.posts:
                return briefing_input_to_articles(briefing_input)
        except Exception as e:
            print(f"Twitter fetch failed ({e}), falling back")

    # Default: SerpAPI news search
    return fetch_articles(outlet, country, num_articles=num_articles,
                          url=url, api_key=serpapi_key,
                          time_period=date_filter)
```

The fallback is the key pattern. If the Twitter API is down, rate-limited, or misconfigured, the pipeline silently falls back to SerpAPI news search. The analyst gets articles either way — possibly from a different source than requested, but never an empty result.

## Error Handling Philosophy

CDDBS follows a consistent error philosophy: **degrade gracefully, never crash.**

| Stage | Failure Mode | Behavior |
|-------|-------------|----------|
| Article fetch | No API key | Return mock articles |
| Article fetch | API error | Return empty list |
| LLM call | Timeout / error | Report marked "failed" |
| Response parsing | Invalid JSON | Raw text used as briefing |
| Quality scoring | Scorer bug | Skipped, briefing still delivered |
| Narrative matching | Matcher bug | Skipped, briefing still delivered |
| Twitter fetch | Rate limited | Fall back to SerpAPI |

The only stage that can mark a report as "failed" is the LLM call itself. Everything else degrades. This means analysts almost always get something useful, even when things go wrong.

## What's Next

This post covered the data flow — from article fetch to database persistence. The next post goes deep on the quality scoring system: how we evaluate LLM output across 7 dimensions without using another LLM, and how the narrative matcher detects known disinformation patterns using deterministic keyword analysis.

---

*The full pipeline implementation is in [orchestrator.py](https://github.com/Be11aMer/cddbs-prod/blob/main/src/cddbs/pipeline/orchestrator.py). The system prompt is versioned at [system_prompt_v1.3.txt](https://github.com/Be11aMer/cddbs-prod/blob/main/src/cddbs/data/system_prompt_v1.3.txt).*
