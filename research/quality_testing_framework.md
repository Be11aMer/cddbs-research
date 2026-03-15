# CDDBS Quality Testing Framework

**Version**: 1.0
**Sprint**: 1 - Briefing Format Redesign
**Task**: 2.5 - Quality Testing

---

## Purpose

Define systematic criteria for evaluating CDDBS intelligence briefing quality. This framework is used to validate v1.1 briefing output against professional standards identified in Task 2.1 research.

---

## Testing Scope

- **Test Set**: 10 RT (Russia Today) affiliated account analyses
- **Comparison**: v1.0 output vs v1.1 output for same inputs
- **Evaluators**: Self-review + 2-3 beta analysts

---

## Quality Dimensions

### 1. Structural Completeness (0-10)

Does the briefing contain all required sections?

| Section | Required | Present? | Score |
|---------|----------|----------|-------|
| Executive summary | Yes | | /1 |
| Key findings (numbered) | Yes | | /1 |
| Subject profile | Yes | | /1 |
| Narrative analysis | Yes | | /1 |
| Behavioral indicators | Yes | | /1 |
| Network context | No | | /1 |
| Confidence assessment | Yes | | /1 |
| Limitations & caveats | Yes | | /1 |
| Methodology note | Yes | | /1 |
| Evidence references | Yes | | /1 |

### 2. Attribution Quality (0-10)

How well are claims attributed to evidence?

| Criterion | Score |
|-----------|-------|
| Every factual claim has a source | /2 |
| Sources are specific (not vague) | /2 |
| Primary vs secondary sources distinguished | /2 |
| Original data referenced where possible | /2 |
| Attribution language is precise | /2 |

### 3. Confidence Signaling (0-10)

How well does the briefing communicate certainty?

| Criterion | Score |
|-----------|-------|
| Overall confidence level stated | /2 |
| Per-finding confidence levels | /2 |
| Confidence factors documented | /2 |
| Hedging language appropriate (not over/under-confident) | /2 |
| Alternative explanations acknowledged | /2 |

### 4. Evidence Presentation (0-10)

How effectively is evidence structured?

| Criterion | Score |
|-----------|-------|
| Evidence supports each key finding | /2 |
| Evidence is concrete (not vague) | /2 |
| Quantitative data included where relevant | /2 |
| Evidence chain is logical | /2 |
| Raw data references provided | /2 |

### 5. Analytical Rigor (0-10)

How sound is the analytical reasoning?

| Criterion | Score |
|-----------|-------|
| Analysis distinguishes fact from assessment | /2 |
| Logical reasoning is sound | /2 |
| Biases acknowledged or mitigated | /2 |
| Scope appropriately bounded | /2 |
| Conclusions follow from evidence | /2 |

### 6. Actionability (0-10)

How useful is the briefing to an analyst?

| Criterion | Score |
|-----------|-------|
| Findings are specific enough to act on | /2 |
| Threat level / priority clearly communicated | /2 |
| Context provided for non-expert readers | /2 |
| Related accounts/campaigns referenced | /2 |
| Next steps or monitoring recommendations | /2 |

### 7. Readability (0-10)

How clear and professional is the writing?

| Criterion | Score |
|-----------|-------|
| Clear, concise language | /2 |
| No jargon without definition | /2 |
| Logical flow between sections | /2 |
| Consistent formatting | /2 |
| Appropriate length (not bloated) | /2 |

---

## Scoring

**Total Score**: ___ / 70

| Rating | Score Range | Interpretation |
|--------|------------|----------------|
| Excellent | 60-70 | Production-ready, meets professional standards |
| Good | 50-59 | Minor improvements needed |
| Acceptable | 40-49 | Functional but needs refinement |
| Poor | 30-39 | Significant issues, not deployment-ready |
| Failing | 0-29 | Fundamental redesign needed |

**Sprint 1 Target**: Average score >= 50 (Good) across 10 test analyses

---

## Test Procedure

### Setup
1. Select 10 RT-affiliated accounts from existing CDDBS database
2. Run each through both v1.0 and v1.1 pipelines
3. Capture raw JSON output and rendered briefing

### Evaluation
1. Score each v1.1 briefing using the rubric above
2. Compare v1.0 vs v1.1 scores for same accounts
3. Document specific improvements and regressions
4. Calculate average scores across all dimensions

### Reporting
1. Create per-briefing scorecards
2. Calculate dimension averages
3. Identify weakest dimensions for Sprint 2 focus
4. Compile delta report (v1.0 vs v1.1)

---

## Test Log

| # | Account | v1.0 Score | v1.1 Score | Delta | Notes |
|---|---------|-----------|-----------|-------|-------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |
| 6 | | | | | |
| 7 | | | | | |
| 8 | | | | | |
| 9 | | | | | |
| 10 | | | | | |
| **Avg** | | | | | |

---

## Dimension Averages

| Dimension | v1.0 Avg | v1.1 Avg | Delta |
|-----------|---------|---------|-------|
| Structural Completeness | | | |
| Attribution Quality | | | |
| Confidence Signaling | | | |
| Evidence Presentation | | | |
| Analytical Rigor | | | |
| Actionability | | | |
| Readability | | | |
| **Overall** | | | |

---

## Beta Tester Instructions

When reviewing a CDDBS briefing, please evaluate:

1. **First impression**: Does this look like a professional intelligence product?
2. **Trust**: Would you trust the conclusions enough to act on them?
3. **Completeness**: Is anything obviously missing?
4. **Clarity**: Is the writing clear and unambiguous?
5. **Confidence**: Do you understand how certain/uncertain the findings are?
6. **Evidence**: Can you trace each claim back to evidence?
7. **Actionability**: Do you know what to do with this information?

Rate each 1-5 and provide free-text comments.
