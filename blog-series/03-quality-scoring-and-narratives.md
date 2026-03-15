---
title: "Building CDDBS — Part 3: Scoring LLM Output Without Another LLM"
published: false
description: "How we built a 7-dimension, 70-point quality rubric and a deterministic narrative matcher to evaluate AI-generated intelligence briefings."
tags: ai, python, nlp, security
series: "Building CDDBS"
---

## The Quality Problem

Here's a dirty secret about LLM-powered applications: the hardest part isn't generating output. It's knowing whether the output is good.

You could use a second LLM to evaluate the first one. Some systems do this — "LLM-as-judge" is a popular pattern. But it has a fundamental flaw for intelligence work: LLMs are confidently wrong in correlated ways. If Gemini hallucinates a claim, GPT-4 reviewing that claim might accept it as plausible because it lacks the same context Gemini lacked. You've just automated the rubber stamp.

CDDBS takes a different approach: **structural quality scoring**. We don't ask "is this briefing accurate?" (that requires ground truth we don't have). We ask "does this briefing follow the structural rules that make intelligence products trustworthy?" That's a question we can answer deterministically, with zero LLM calls.

## The 7-Dimension Rubric

The quality scorer evaluates every briefing across 7 dimensions, each worth 10 points:

| Dimension | What It Measures | Why It Matters |
|-----------|-----------------|----------------|
| Structural Completeness | All 7 required sections present | Missing sections = incomplete analysis |
| Attribution Quality | Claims linked to typed evidence | Unattributed claims are unverifiable |
| Confidence Signaling | Uncertainty expressed explicitly | False certainty is the #1 failure mode |
| Evidence Presentation | Evidence structured and specific | Vague evidence is useless evidence |
| Analytical Rigor | Sound reasoning, limitations noted | Prevents overreach and tunnel vision |
| Actionability | Findings are useful to an analyst | A briefing nobody can act on has no value |
| Readability | Clear, professional prose | Technical accuracy means nothing if it's unreadable |

Total: **70 points**. Ratings map to bands:

```
60-70  →  Excellent
50-59  →  Good
40-49  →  Acceptable
30-39  →  Poor
 0-29  →  Failing
```

### Why These Dimensions?

This rubric came from Sprint 1 research. We analyzed briefing formats from 10 professional intelligence organizations: EUvsDisinfo, DFRLab (Atlantic Council), Bellingcat, NATO StratCom COE, Stanford Internet Observatory, Graphika, RAND Corporation, UK DCMS, the Global Engagement Center, and the Oxford Internet Institute.

Key finding: **only 3 of 10 organizations use explicit confidence signaling in their public outputs.** Per-finding confidence levels — where each claim has its own confidence score — is a CDDBS innovation. The rubric is designed to reward this practice because it's the single most important quality signal for an analyst consuming the briefing.

## Scoring Implementation

Let's walk through how each dimension is scored in practice.

### Structural Completeness (10 points)

The simplest dimension: does the briefing contain the sections we asked for?

```python
def score_structural_completeness(briefing_text):
    score = 0
    issues = []
    required_sections = [
        "executive summary", "key findings", "subject profile",
        "narrative analysis", "confidence assessment",
        "limitations", "methodology"
    ]

    text_lower = briefing_text.lower()
    for section in required_sections:
        if section in text_lower:
            score += 1
        else:
            issues.append(f"Missing section: {section}")

    # Bonus points for structured formatting
    if "##" in briefing_text or "**" in briefing_text:
        score += min(3, 10 - score)  # up to 3 bonus for formatting

    return min(score, 10), issues
```

This catches the most common LLM failure: omitting sections. Gemini reliably produces Executive Summary and Key Findings but sometimes drops Limitations or Methodology — the sections that constrain analyst overconfidence.

### Attribution Quality (10 points)

This is where the evidence typing system pays off:

```python
EVIDENCE_TYPES = ["[POST]", "[PATTERN]", "[NETWORK]", "[METADATA]",
                  "[EXTERNAL]", "[FORWARD]", "[CHANNEL_META]"]

def score_attribution_quality(briefing_text):
    score = 0
    issues = []

    # Count evidence-typed attributions
    evidence_count = sum(
        briefing_text.count(etype) for etype in EVIDENCE_TYPES
    )

    if evidence_count >= 8:
        score += 4
    elif evidence_count >= 4:
        score += 2
    else:
        issues.append(f"Only {evidence_count} typed evidence items")

    # Check that findings have evidence
    findings = re.findall(
        r'(?:finding|key finding)[:\s]*(.*?)(?=\n\n|\n#|$)',
        briefing_text, re.IGNORECASE | re.DOTALL
    )
    findings_with_evidence = sum(
        1 for f in findings
        if any(et in f for et in EVIDENCE_TYPES)
    )

    if findings and findings_with_evidence / len(findings) >= 0.8:
        score += 3
    elif findings and findings_with_evidence / len(findings) >= 0.5:
        score += 1
    else:
        issues.append("Most findings lack typed evidence")

    # Check evidence specificity
    if re.search(r'\[PATTERN\].*\d+%', briefing_text):
        score += 2  # PATTERN has specific metrics
    if re.search(r'\[NETWORK\].*@\w+', briefing_text):
        score += 1  # NETWORK names specific accounts

    return min(score, 10), issues
```

The rubric rewards *specific* evidence. A `[PATTERN]` tag alone is worth something, but `[PATTERN] 78% of tweets are retweets from state media` is worth more. The regex checks for numbers after PATTERN tags and account names after NETWORK tags.

### Confidence Signaling (10 points)

The most important dimension for intelligence work:

```python
CONFIDENCE_LEVELS = ["high confidence", "moderate confidence",
                     "low confidence"]

def score_confidence_signaling(briefing_text):
    score = 0
    issues = []
    text_lower = briefing_text.lower()

    # Overall confidence stated
    has_overall = any(level in text_lower for level in CONFIDENCE_LEVELS)
    if has_overall:
        score += 3
    else:
        issues.append("No overall confidence level stated")

    # Per-finding confidence
    findings_section = extract_section(briefing_text, "key findings")
    if findings_section:
        confidence_mentions = sum(
            findings_section.lower().count(level)
            for level in CONFIDENCE_LEVELS
        )
        if confidence_mentions >= 3:
            score += 3
        elif confidence_mentions >= 1:
            score += 1

    # Confidence factors documented
    if "confidence" in text_lower and "factor" in text_lower:
        score += 2

    # No forbidden certainty language
    forbidden = ["obviously", "it is clear that", "definitely",
                 "without a doubt", "undeniably"]
    violations = [f for f in forbidden if f in text_lower]
    if not violations:
        score += 2
    else:
        issues.append(f"Forbidden certainty language: {violations}")

    return min(score, 10), issues
```

This dimension has a dual mechanism: it rewards explicit uncertainty (confidence levels, factors, caveats) and penalizes false certainty (forbidden phrases). An LLM that says "we assess with moderate confidence" gets full marks. One that says "it is clear that" gets docked.

## Narrative Matching: The Other Evaluation Layer

Quality scoring tells you whether the briefing is structurally sound. Narrative matching tells you what it found.

### The Narrative Database

CDDBS maintains a JSON file of 18 known disinformation narratives:

```json
{
  "narratives": [
    {
      "id": "ukraine_001",
      "name": "Ukraine as Nazi/Fascist State",
      "category": "Ukraine Conflict Revisionism",
      "keywords": [
        "nazi", "fascist", "azov", "denazification",
        "bandera", "neo-nazi", "ultranationalist",
        "right sector"
      ],
      "description": "Claims that Ukraine is controlled by Nazi or fascist elements..."
    }
  ]
}
```

Each narrative has a unique ID, a category, and a keyword list. The keywords are chosen to be specific enough to avoid false positives on general political discussion.

### The Matching Algorithm

```python
def match_narratives(text, threshold=2):
    narratives = load_known_narratives()
    matches = []
    text_lower = text.lower()

    for narrative in narratives:
        matched_keywords = [
            kw for kw in narrative["keywords"]
            if kw.lower() in text_lower
        ]

        if len(matched_keywords) >= threshold:
            confidence = (
                "high" if len(matched_keywords) >= 5
                else "moderate" if len(matched_keywords) >= 3
                else "low"
            )
            matches.append({
                "narrative_id": narrative["id"],
                "narrative_name": narrative["name"],
                "category": narrative["category"],
                "confidence": confidence,
                "matched_keywords": matched_keywords,
                "match_count": len(matched_keywords)
            })

    # Deduplicate: keep strongest match per narrative
    seen = {}
    for match in matches:
        nid = match["narrative_id"]
        if nid not in seen or match["match_count"] > seen[nid]["match_count"]:
            seen[nid] = match

    return list(seen.values())
```

### Why Keyword Matching, Not ML?

This is a deliberate design choice with real trade-offs:

**Advantages of keyword matching:**
- Deterministic. Same input always produces same output.
- Auditable. You can see exactly which keywords triggered the match.
- Fast. No model loading, no inference time. Runs in <10ms.
- Offline. No external service dependency.
- Explainable. An analyst can evaluate whether the match is a true positive by reading the keywords.

**Disadvantages:**
- No contextual understanding. "NATO expansion" in a factual news report about a summit and "NATO expansion" in a conspiracy theory about Russian encirclement produce the same match.
- Keyword coverage. If a narrative evolves to use new language, the keywords need manual updating.
- No semantic similarity. Paraphrases of known narratives won't match.

For CDDBS's use case, the advantages win. The system is a *tool for analysts*, not a replacement for them. A false positive with an explanation ("matched on: nazi, azov, denazification") is more useful than an ML prediction with a probability score that can't be interrogated.

### Confidence Calibration

The threshold system maps keyword density to confidence:

```
5+ keywords matched  →  High confidence
3-4 keywords matched →  Moderate confidence
2 keywords matched   →  Low confidence
1 keyword matched    →  Below threshold (not reported)
```

The minimum threshold of 2 is critical. A single keyword like "NATO" could appear in any geopolitical article. Two keywords from the same narrative — "NATO" + "encirclement" — is a much stronger signal.

## Putting It Together: A Scored Report

Here's what the quality + narrative pipeline produces for a hypothetical RT analysis:

```json
{
  "quality": {
    "total_score": 52,
    "rating": "Good",
    "dimensions": {
      "structural_completeness": {"score": 8, "max": 10},
      "attribution_quality": {"score": 7, "max": 10},
      "confidence_signaling": {"score": 8, "max": 10},
      "evidence_presentation": {"score": 7, "max": 10},
      "analytical_rigor": {"score": 8, "max": 10},
      "actionability": {"score": 7, "max": 10},
      "readability": {"score": 7, "max": 10}
    }
  },
  "narratives": [
    {
      "narrative_id": "ukraine_003",
      "name": "Western Provocation Caused Conflict",
      "category": "Ukraine Conflict Revisionism",
      "confidence": "high",
      "matched_keywords": ["NATO", "Maidan", "provocation", "coup", "Western"],
      "match_count": 5
    },
    {
      "narrative_id": "anti_nato_001",
      "name": "NATO Expansion Threatens Russia",
      "confidence": "moderate",
      "matched_keywords": ["NATO expansion", "encirclement", "broken promises"],
      "match_count": 3
    }
  ]
}
```

The analyst sees a 52/70 "Good" rating, knows which dimensions are weak (actionability and readability, both 7/10), and sees two narrative matches with the specific keywords that triggered them. They can then verify: did the articles actually discuss Maidan as a Western-backed coup, or was the keyword match coincidental?

## Frontend: Making Scores Useful

Quality scores are only valuable if analysts can interpret them. The frontend renders two key visualizations:

**Quality Radar Chart.** A custom SVG heptagon (7-sided) showing all dimensions simultaneously. No charting library dependency — just computed SVG paths:

```
        Structural (8)
           ╱  ╲
    Read (7)    Attrib (7)
       │          │
   Action (7)  Confid (8)
       │          │
    Rigor (8)  Evidence (7)
```

**Narrative Tags.** Color-coded pills that expand to show matched keywords:

```
[Ukraine Conflict Revisionism] ● High
  → NATO, Maidan, provocation, coup, Western

[Anti-NATO] ● Moderate
  → NATO expansion, encirclement, broken promises
```

## The Testing Strategy

Quality scoring has the highest test density in the codebase: 23 tests covering all 7 dimensions plus edge cases.

```python
# test_quality.py examples
def test_high_quality_briefing():
    """A well-structured briefing should score 50+."""
    score = score_briefing_text(HIGH_QUALITY_FIXTURE)
    assert score["total_score"] >= 50
    assert score["rating"] in ("Good", "Excellent")

def test_minimal_briefing():
    """A briefing with only basic structure should score 25-40."""
    score = score_briefing_text(MINIMAL_FIXTURE)
    assert 25 <= score["total_score"] <= 40
    assert score["rating"] in ("Poor", "Acceptable")

def test_forbidden_language_penalty():
    """Forbidden certainty language should reduce confidence score."""
    text = "It is clear that this account is spreading propaganda."
    score = score_confidence_signaling(text)
    assert score < 8  # penalty applied
```

The tests use fixture files — real briefing examples at different quality levels (high, medium, low, minimal, telegram, cross-platform). This ensures the scorer produces sensible results across the full range of inputs.

Narrative matching has 11 tests covering keyword thresholds, confidence calibration, deduplication, and edge cases:

```python
def test_below_threshold():
    """A single keyword should not trigger a match."""
    matches = match_narratives("NATO held a summit today.")
    assert len(matches) == 0

def test_moderate_confidence():
    """3-4 keywords should produce moderate confidence."""
    text = "NATO expansion and encirclement, with broken promises"
    matches = match_narratives(text)
    assert matches[0]["confidence"] == "moderate"
```

## Design Principle: Evaluate Structure, Not Truth

The core insight behind CDDBS's quality system is that you can evaluate *process quality* without evaluating *factual accuracy*. A briefing that:

- Includes all 7 sections
- Attributes every claim to typed evidence
- States confidence levels explicitly
- Acknowledges limitations
- Uses professional language

...is more likely to be accurate than one that doesn't. Not because structure guarantees truth, but because the structural requirements force the LLM to do the work that produces accurate output. You can't write `[POST] https://twitter.com/...` without having a specific post to reference. You can't write "We assess with moderate confidence" without implicitly acknowledging uncertainty.

The quality scorer doesn't grade the LLM's homework. It checks whether the LLM showed its work.

---

*Quality scorer implementation: [quality.py](https://github.com/Be11aMer/cddbs-prod/blob/main/src/cddbs/quality.py). Narrative database: [known_narratives.json](https://github.com/Be11aMer/cddbs-prod/blob/main/src/cddbs/data/known_narratives.json).*
