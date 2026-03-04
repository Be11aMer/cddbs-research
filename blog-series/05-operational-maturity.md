---
title: "Building CDDBS — Part 5: From Prototype to Production"
published: false
description: "Batch analysis, export pipelines, operational metrics, and the unglamorous engineering that makes an LLM-powered system actually usable."
tags: ai, python, devops, webdev
series: "Building CDDBS"
---

## The Production Gap

There's a moment in every project where the core feature works but the system isn't usable. The LLM generates good briefings. The quality scorer catches structural issues. The narrative matcher flags known patterns. An analyst can run a single analysis, wait a minute, and get results.

But then they want to analyze 5 outlets and compare them. Or email a briefing to a colleague as a PDF. Or check whether the system's been producing more failures than usual this week.

Sprint 5 of CDDBS was about closing these gaps — the features that separate "works on my machine" from "works for the team." This post covers batch analysis, export formats, operational metrics, and the frontend changes that tie them together.

## Batch Analysis

### The Problem

A single CDDBS analysis takes 30-60 seconds (mostly Gemini API latency). An analyst comparing 5 outlets would need to submit 5 separate requests, track 5 separate report IDs, and manually correlate the results. That's a workflow problem.

### The Design

We added a `Batch` model that groups multiple analysis runs under a single request:

```python
class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    status = Column(String, default="queued")
    target_count = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    report_ids = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
```

The `report_ids` column is a JSON array of Report IDs. Each target in the batch creates its own independent Report record — the Batch just tracks which reports belong together.

### Why Not a Foreign Key?

We considered adding `batch_id` as a foreign key on `Report`. The JSON array approach is simpler:

- **No schema migration** on the existing reports table.
- **Reports are independent.** A report created through a batch is identical to a report created individually. The same API endpoint (`GET /analysis-runs/{id}`) retrieves it. There's no "batch-only" report type.
- **Batch is a view, not a relationship.** The batch tracks progress; it doesn't own the reports.

The trade-off is that querying "all reports in batch X" requires a JSON contains check instead of a simple FK join. At our scale (batches of 1-5), this is irrelevant.

### Execution Model

Each target in a batch gets its own background thread:

```python
@app.post("/analysis-runs/batch")
def create_batch(request: BatchCreateRequest, db=Depends(get_db)):
    batch = Batch(
        name=request.name,
        status="running",
        target_count=len(request.targets)
    )
    db.add(batch)
    db.commit()

    for target in request.targets:
        report = Report(outlet=target.outlet, country=target.country)
        report.data = {"status": "queued", "batch_id": batch.id}
        db.add(report)
        db.commit()

        batch.report_ids = batch.report_ids + [report.id]
        db.commit()

        thread = threading.Thread(
            target=_run_analysis_job,
            args=(report.id, target.outlet, target.country, ...),
            kwargs={"batch_id": batch.id},
            daemon=True
        )
        thread.start()

    return {"batch_id": batch.id, "target_count": len(request.targets)}
```

When each pipeline job completes, it updates the batch counters:

```python
def _update_batch_progress(batch_id, success, db):
    batch = db.query(Batch).get(batch_id)
    if not batch:
        return

    if success:
        batch.completed_count += 1
    else:
        batch.failed_count += 1

    if batch.completed_count + batch.failed_count >= batch.target_count:
        batch.status = "completed" if batch.failed_count == 0 else "partial"

    db.commit()
```

The batch status transitions: `queued → running → completed` (or `partial` if any target failed). An analyst checking batch progress sees a clear picture:

```json
GET /analysis-runs/batch/7
{
  "id": 7,
  "name": "Russian state media comparison",
  "status": "running",
  "target_count": 4,
  "completed_count": 2,
  "failed_count": 0,
  "report_ids": [42, 43, 44, 45]
}
```

### Why Threads, Not a Task Queue?

Same reasoning as the single-analysis pipeline: cost discipline. A proper task queue (Celery + Redis) requires two additional services. For batches capped at 5 targets on Render's free tier, Python threads with daemon mode are adequate. The `BATCH_MAX_SIZE` config (default 5) prevents resource exhaustion.

## Export Pipeline

### Three Formats, One Endpoint

```
GET /analysis-runs/{id}/export?format=json
GET /analysis-runs/{id}/export?format=csv
GET /analysis-runs/{id}/export?format=pdf
```

Each format serves a different workflow:

**JSON** — Machine-readable. For analysts who want to feed CDDBS output into their own tools, scripts, or databases. Contains the full briefing, quality scorecard, narrative matches, and article metadata.

**CSV** — Spreadsheet-compatible. For analysts who work in Excel or Google Sheets. Flattened tabular format with section headers.

**PDF** — Shareable. For briefings that need to be emailed, printed, or included in a presentation.

### JSON Export

The simplest format — a structured dump of everything we know about a report:

```python
def export_json(report, briefing=None, narratives=None, articles=None):
    output = {
        "metadata": {
            "report_id": report.id,
            "outlet": report.outlet,
            "country": report.country,
            "created_at": report.created_at.isoformat(),
            "export_format": "json",
            "export_version": "1.0"
        },
        "briefing": report.final_report,
        "articles": [
            {
                "title": a.title,
                "link": a.link,
                "snippet": a.snippet,
                "date": str(a.date) if a.date else None
            }
            for a in (articles or [])
        ]
    }

    if briefing:
        output["quality"] = {
            "score": briefing.quality_score,
            "rating": briefing.quality_rating,
            "details": briefing.quality_details
        }

    if narratives:
        output["narratives"] = [
            {
                "id": n.narrative_id,
                "name": n.narrative_name,
                "category": n.category,
                "confidence": n.confidence,
                "keywords": n.matched_keywords,
                "match_count": n.match_count
            }
            for n in narratives
        ]

    return json.dumps(output, indent=2, default=str)
```

### CSV Export

CSV is harder because the data is relational, not tabular. The export flattens it into sections:

```python
def export_csv(report, briefing=None, narratives=None, articles=None):
    output = io.StringIO()
    writer = csv.writer(output)

    # Metadata section
    writer.writerow(["=== METADATA ==="])
    writer.writerow(["Report ID", report.id])
    writer.writerow(["Outlet", report.outlet])
    writer.writerow(["Country", report.country])
    writer.writerow(["Date", report.created_at.isoformat()])

    if briefing:
        writer.writerow([])
        writer.writerow(["=== QUALITY ==="])
        writer.writerow(["Score", f"{briefing.quality_score}/70"])
        writer.writerow(["Rating", briefing.quality_rating])

    if narratives:
        writer.writerow([])
        writer.writerow(["=== NARRATIVES ==="])
        writer.writerow(["ID", "Name", "Category", "Confidence", "Keywords"])
        for n in narratives:
            writer.writerow([
                n.narrative_id, n.narrative_name, n.category,
                n.confidence, ", ".join(n.matched_keywords or [])
            ])

    if articles:
        writer.writerow([])
        writer.writerow(["=== ARTICLES ==="])
        writer.writerow(["Title", "Link", "Date", "Snippet"])
        for a in articles:
            writer.writerow([a.title, a.link, a.date, a.snippet])

    return output.getvalue()
```

The section headers (`=== METADATA ===`) make the CSV human-scannable when opened in a spreadsheet. Each section has its own column structure, which means this isn't a "pure" CSV — but it's more useful than forcing all data into a single column layout.

### PDF Export

PDF is the only format that requires an optional dependency — `reportlab`:

```python
def export_pdf(report, briefing=None, narratives=None, articles=None):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        return None  # Graceful degradation

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(
        f"CDDBS Intelligence Briefing: {report.outlet}",
        styles["Title"]
    ))

    # Quality badge
    if briefing:
        story.append(Paragraph(
            f"Quality: {briefing.quality_score}/70 ({briefing.quality_rating})",
            styles["Heading2"]
        ))

    # Briefing content
    if report.final_report:
        for paragraph in report.final_report.split("\n\n"):
            story.append(Paragraph(paragraph, styles["BodyText"]))
            story.append(Spacer(1, 6))

    # ... narratives and articles sections

    doc.build(story)
    return buffer.getvalue()
```

`reportlab` is declared as an optional dependency. If it's not installed, `export_pdf()` returns `None`, and the API returns a 501 Not Implemented for PDF requests. The JSON and CSV exports work with nothing beyond the Python standard library.

### Frontend Integration

The report viewer adds export buttons that link directly to the export endpoint:

```typescript
// ReportViewDialog.tsx (simplified)
{run?.data?.status === "completed" && (
  <>
    <Button
      component="a"
      href={getExportUrl(run.id, "json")}
      variant="outlined"
    >
      JSON
    </Button>
    <Button
      component="a"
      href={getExportUrl(run.id, "csv")}
      variant="outlined"
    >
      CSV
    </Button>
  </>
)}
```

The buttons use plain `<a>` tags with `href` pointing to the export endpoint. This triggers a browser download without any JavaScript fetch/blob handling. Simple, and it works across all browsers.

## Operational Metrics

### Why Metrics Matter

When you're running 10+ analyses a day, you need to know:
- Are analyses succeeding or failing?
- Is output quality trending up or down?
- What's breaking, and how often?

CDDBS computes metrics on-demand from the database:

```python
def compute_metrics(db):
    reports = db.query(Report).all()

    if not reports:
        return {
            "total_runs": 0, "completed": 0, "failed": 0,
            "running": 0, "success_rate": 0,
            "avg_quality_score": 0,
            "quality_distribution": {},
            "failure_reasons": [],
            "recent_24h": {"total": 0, "completed": 0,
                           "failed": 0, "success_rate": 0}
        }

    completed = [r for r in reports if r.data and r.data.get("status") == "completed"]
    failed = [r for r in reports if r.data and r.data.get("status") == "failed"]
    running = [r for r in reports if r.data and r.data.get("status") in ("queued", "running")]

    # Quality distribution from briefings
    briefings = db.query(Briefing).all()
    quality_dist = {"excellent": 0, "good": 0, "acceptable": 0, "poor": 0, "failing": 0}
    scores = []
    for b in briefings:
        if b.quality_rating:
            quality_dist[b.quality_rating.lower()] = quality_dist.get(b.quality_rating.lower(), 0) + 1
        if b.quality_score:
            scores.append(b.quality_score)

    # Recent 24h breakdown
    cutoff = datetime.now(UTC) - timedelta(hours=24)
    recent = [r for r in reports if r.created_at and r.created_at >= cutoff]
    recent_completed = [r for r in recent if r.data and r.data.get("status") == "completed"]
    recent_failed = [r for r in recent if r.data and r.data.get("status") == "failed"]

    return {
        "total_runs": len(reports),
        "completed": len(completed),
        "failed": len(failed),
        "running": len(running),
        "success_rate": round(len(completed) / len(reports) * 100, 1) if reports else 0,
        "avg_quality_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "quality_distribution": quality_dist,
        "failure_reasons": [
            r.data.get("errors", ["Unknown"])[0]
            for r in failed[-10:]
        ],
        "recent_24h": {
            "total": len(recent),
            "completed": len(recent_completed),
            "failed": len(recent_failed),
            "success_rate": round(
                len(recent_completed) / len(recent) * 100, 1
            ) if recent else 0
        }
    }
```

### Why On-Demand, Not Pre-Aggregated?

At our scale (low hundreds of reports), computing metrics from raw data on every request is fast enough — under 100ms. Pre-aggregated metrics (materialized views, counter tables) would add complexity: you'd need triggers or background jobs to keep them in sync, and stale aggregates are worse than slightly slow fresh data.

If CDDBS grew to thousands of reports, we'd add a materialized view refreshed on a schedule. Until then, the query-on-demand approach is correct.

### What the Metrics Tell You

A sample metrics response:

```json
{
  "total_runs": 42,
  "completed": 38,
  "failed": 2,
  "running": 2,
  "success_rate": 90.5,
  "avg_quality_score": 52.1,
  "quality_distribution": {
    "excellent": 8,
    "good": 15,
    "acceptable": 10,
    "poor": 4,
    "failing": 1
  },
  "failure_reasons": [
    "Gemini API timeout",
    "Invalid outlet name"
  ],
  "recent_24h": {
    "total": 8,
    "completed": 7,
    "failed": 1,
    "success_rate": 87.5
  }
}
```

The `failure_reasons` array shows the last 10 failure error messages. This is quick diagnostics: if you see "Gemini API timeout" appearing repeatedly, you know to check API quotas. If you see "Invalid outlet name", there's a user input validation gap.

The `quality_distribution` tells you whether your system prompt needs tuning. If "failing" and "poor" are growing, the LLM is producing structurally deficient output and the system prompt may need revision.

## The Extended API Status

The `/api-status` endpoint now reports on all configured services:

```json
{
  "serpapi_configured": true,
  "google_api_configured": true,
  "twitter_configured": false,
  "database_connected": true,
  "version": "1.5.0"
}
```

This is operational hygiene. Before an analyst starts an analysis, they can check whether the required API keys are configured. The frontend's `StatusIndicator` component uses this to show green/amber/red status for each service.

## Testing the Operational Layer

The operational features added 35 new tests:

| Test Suite | Count | What It Tests |
|-----------|-------|---------------|
| `test_twitter_client.py` | 14 | User lookup, tweet fetch, rate limiting, adapter bridge |
| `test_batch.py` | 7 | Batch CRUD, validation, progress tracking |
| `test_export.py` | 7 | JSON/CSV/PDF export, missing report handling |
| `test_metrics.py` | 7 | Empty DB, completed/failed states, quality distribution |

The batch tests mock the pipeline execution to avoid real API calls:

```python
def test_batch_progress_tracking(client, db):
    """Batch counters should update as targets complete."""
    batch = Batch(name="test", target_count=3, status="running")
    db.add(batch)
    db.commit()

    _update_batch_progress(batch.id, success=True, db=db)
    _update_batch_progress(batch.id, success=True, db=db)
    _update_batch_progress(batch.id, success=False, db=db)

    db.refresh(batch)
    assert batch.completed_count == 2
    assert batch.failed_count == 1
    assert batch.status == "partial"  # not all succeeded
```

The export tests verify that each format handles edge cases — missing quality data, missing narratives, empty articles:

```python
def test_export_json_without_quality(db, report):
    """JSON export should work even without quality scores."""
    result = export_json(report, briefing=None, narratives=None)
    data = json.loads(result)
    assert "quality" not in data
    assert data["metadata"]["report_id"] == report.id
```

## The Full Picture

After five sprints, here's where CDDBS stands:

| Metric | Value |
|--------|-------|
| Database tables | 7 |
| API endpoints | 17 |
| Tests passing | 169 |
| External dependencies added (Sprints 4-5) | 0 required, 1 optional |
| Lines of backend code | ~2,500 |
| Frontend components | 15 |

The system handles the full lifecycle: ingest data from news or social media, analyze it with a constrained LLM, score the output for structural quality, match against known disinformation narratives, export results in three formats, and track operational health over time.

## What's Next for CDDBS

The immediate roadmap:

- **Sprint 6**: Telegram Bot API live integration, frontend metrics dashboard, webhook alerting for failure spikes.
- **Sprint 7-8**: User authentication, shared analysis workspaces, trend detection over time.
- **Sprint 9+**: ML-based narrative matching (to complement keyword matching), automated monitoring schedules, multi-language support.

The long-term vision is a system where an analyst can set up continuous monitoring of 20+ outlets and social media accounts, get alerted when narrative patterns shift, and produce briefings that meet professional intelligence community standards — all powered by LLMs constrained to be honest about what they know and don't know.

## Series Recap

This five-part series covered:

1. **Architecture & Threat Model** — What CDDBS is, the 18 narratives it tracks, and the three-tier architecture.
2. **The Analysis Pipeline** — Article fetch, prompt construction, LLM call, response parsing, and the async execution model.
3. **Quality Scoring & Narrative Detection** — The 7-dimension rubric, keyword-based narrative matching, and why we evaluate structure instead of truth.
4. **Multi-Platform Analysis** — Twitter and Telegram adapters, platform routing, and the common `BriefingInput` format.
5. **Operational Maturity** — Batch analysis, export formats, metrics, and production engineering.

The common thread: **constrain the LLM, verify the output, degrade gracefully.** LLMs are powerful synthesis engines, but they need guardrails — structured prompts, typed evidence, quality rubrics, and narrative databases — to produce output that analysts can trust. Building those guardrails is the actual engineering challenge. The LLM call itself is one line of code.

---

*CDDBS is open source. Production: [github.com/Be11aMer/cddbs-prod](https://github.com/Be11aMer/cddbs-prod). Research: [github.com/Be11aMer/cddbs-research-draft](https://github.com/Be11aMer/cddbs-research-draft).*
