# EU AI Act Compliance Practices

**Last Updated**: 2026-03-18
**Implemented Across**: Sprints 1-6
**Regulation**: Regulation (EU) 2024/1689 laying down harmonized rules on artificial intelligence
**Key Dates**: Prohibited practices (Feb 2025), GPAI (Aug 2025), High-risk (Aug 2026), Full (Aug 2027)

---

## CDDBS AI Act Risk Classification

### System Description

CDDBS uses Google Gemini (a General-Purpose AI model) to:
1. Analyze news articles and social media content
2. Generate structured intelligence briefings
3. Assess source credibility and narrative alignment

### Risk Assessment

| Factor | Assessment | Rationale |
|--------|-----------|-----------|
| **Annex III listing** | Not listed | Media analysis is not in the high-risk system categories |
| **Autonomous decision-making** | No | All output reviewed by human analyst |
| **Impact on fundamental rights** | Minimal | Analyzes public information; no individual decisions |
| **Transparency needs** | Yes | AI-generated content must be identifiable |
| **Biometric processing** | None | No biometric data processed |

**Classification: Limited Risk System**

Primary obligation: **Transparency** (Art. 50) — persons must be informed when interacting with AI-generated content.

---

## Transparency Measures Implemented

### 1. AI-Generated Content Labeling

Every analysis briefing produced by CDDBS explicitly identifies itself as AI-generated:

```json
{
  "executive_summary": "...",
  "methodology": {
    "model": "gemini-2.5-flash",
    "analysis_type": "ai_assisted_osint",
    "confidence_framework": "three_tier"
  }
}
```

The system prompt (v1.3) instructs the LLM to:
- State that the analysis is AI-generated
- Use confidence tiers: HIGH / MODERATE / LOW
- Attribute every claim to evidence
- Acknowledge limitations and uncertainty

### 2. Confidence Scoring Framework

Implemented in Sprint 1 (system prompt) and Sprint 2 (quality scorer):

| Confidence Tier | Definition | Quality Score Threshold |
|-----------------|-----------|------------------------|
| HIGH | Multiple independent sources, direct evidence | Quality score ≥ 55/70 |
| MODERATE | Limited sources, some indirect evidence | Quality score 35-54/70 |
| LOW | Single source, primarily inference | Quality score < 35/70 |

The 70-point quality rubric scores across 7 dimensions:
1. **Structural completeness** (10 points) — All 7 briefing sections present
2. **Attribution quality** (10 points) — Claims linked to evidence
3. **Confidence calibration** (10 points) — Appropriate uncertainty language
4. **Evidence depth** (10 points) — Multiple source types cited
5. **Analytical rigor** (10 points) — Alternative explanations considered
6. **Actionability** (10 points) — Concrete recommendations provided
7. **Readability** (10 points) — Clear, professional language

### 3. Human Oversight Design

CDDBS implements human-in-the-loop at every decision point:

```
                  AI Analysis
                      │
                      ▼
              ┌───────────────┐
              │ Analyst Review │ ← Human reviews all AI output
              │   Dashboard    │
              └───────┬───────┘
                      │
              ┌───────▼───────┐
              │   Feedback    │ ← Human can flag errors/concerns
              │   System      │
              └───────┬───────┘
                      │
              ┌───────▼───────┐
              │   No Auto     │ ← No automated downstream action
              │   Actions     │
              └───────────────┘
```

Key design decisions:
- **No automated actions**: CDDBS produces briefings, not automated responses. No alerts, blocks, or moderation actions are taken without human decision.
- **Feedback loop**: Sprint 4 implemented a feedback system where analysts can rate and correct AI output.
- **Quality scoring is structural**: The 70-point rubric is deterministic (no AI in the scoring loop), providing an independent quality check on AI output.

### 4. Record Keeping

Every analysis run is persisted with:

| Field | Purpose |
|-------|---------|
| `created_at` | Timestamp of analysis request |
| `completed_at` | Timestamp of analysis completion |
| `target` | The subject analyzed (outlet name/URL) |
| `platform` | Data source used (news/twitter/telegram) |
| `status` | Processing status (pending/running/completed/failed) |
| `briefing_json` | Full structured briefing output |
| `quality_score` | Overall quality score (0-70) |
| `quality_details` | Per-dimension score breakdown |
| `narrative_matches` | Detected narrative alignments with confidence |

This provides a full audit trail of what was analyzed, when, by which model, and what quality level the output achieved.

---

## GPAI Model Usage

CDDBS uses Google Gemini 2.5 Flash, a General-Purpose AI (GPAI) model. Under the AI Act:

| GPAI Obligation | Responsibility | CDDBS Approach |
|-----------------|---------------|----------------|
| Model card / technical documentation | Google (as GPAI provider) | Google publishes Gemini model cards |
| Training data transparency | Google (as GPAI provider) | Not CDDBS's obligation |
| Downstream deployer obligations | CDDBS (as deployer) | Transparency measures, human oversight, record keeping |
| Systemic risk assessment | Google (if Gemini classified as systemic) | Not CDDBS's obligation |

CDDBS's responsibility as a **downstream deployer** is to:
1. Use the GPAI model in compliance with its intended use
2. Implement transparency measures for end users
3. Maintain human oversight
4. Keep records of AI system operations

---

## What CDDBS Does NOT Do (Prohibited Practices - Art. 5)

Documented for completeness and audit purposes:

- **No social scoring**: CDDBS analyzes media outlets, not individuals' social behavior
- **No real-time biometric identification**: No biometric processing of any kind
- **No subliminal manipulation**: Output is transparent analysis, not persuasion
- **No exploitation of vulnerabilities**: Tool designed for security researchers, not targeting vulnerable groups
- **No emotion recognition**: No sentiment analysis of individuals (only aggregate media tone via GDELT metadata)
- **No predictive policing**: No individual risk scoring for law enforcement purposes

---

## Gap Analysis: What's Left for Full AI Act Compliance

| Gap | Priority | Target Sprint |
|-----|----------|--------------|
| Formal AI system registration (if required for limited risk) | Low | When registration portal opens |
| User-facing AI disclosure in frontend UI | Medium | Sprint 8 (with auth) |
| Automated model version tracking | Low | Sprint 9 |
| Formal fundamental rights impact assessment | Low | Before commercial deployment |

---

## Reusable Practices for Other Projects Using GPAI Models

1. **Confidence scoring**: Don't present AI output as certainty. Implement a scoring rubric that rates output quality independently of the AI model.

2. **Human-in-the-loop by architecture**: Design the system so AI output is a *proposal*, not an *action*. The gap between proposal and action is where human oversight lives.

3. **Record everything**: Log what was sent to the AI, what came back, when, and what quality score it received. This is both good engineering and an audit requirement.

4. **Structural quality scoring**: Use deterministic, non-AI scoring to validate AI output. This prevents the "AI validating AI" problem.

5. **Separate the AI model from the application logic**: CDDBS's quality scorer, narrative matcher, and event clustering all work independently of Gemini. If the AI model changes, the quality assurance layer remains.
