# Source Verification Framework

**Version**: 1.0
**Sprint**: 2 - Quality & Reliability
**Task**: 3.3 - Source Verification Framework

---

## Purpose

Define systematic procedures for verifying each type of evidence cited in CDDBS intelligence briefings. Every evidence reference in a briefing should be verifiable according to this framework.

---

## Verification Levels

| Level | Description | When to Use |
|-------|-------------|-------------|
| **Automated** | Programmatic verification (URL check, schema validation, data format) | Every briefing, every evidence reference |
| **Semi-automated** | Automated check with human review of results | Flagged items from automated checks |
| **Manual** | Human analyst reviews the evidence directly | High-stakes assessments, disputed findings, pre-publication review |

---

## Verification by Evidence Type

### `[POST]` — Social Media Post

A reference to a specific social media post (tweet, Telegram message, etc.).

| Check | Level | Pass Criteria | Failure Action |
|-------|-------|--------------|----------------|
| URL format valid | Automated | Matches platform URL pattern (e.g., `twitter.com/.../status/...`) | Reject reference |
| URL resolves | Automated | HTTP 200 response (or archived version accessible) | Flag as potentially deleted; check archive |
| Content matches claim | Manual | Post content supports the finding it's cited for | Downgrade finding confidence |
| Timestamp within analysis period | Automated | Post date falls within stated analysis period | Flag as out-of-scope |
| Account matches subject | Automated | Post belongs to the account being analyzed (or stated source) | Flag attribution error |
| Archive exists | Automated | Wayback Machine or archive.today snapshot exists | Create archive before publication |

**Verification Result**:
- **Verified**: URL resolves, content matches, timestamp valid, archive exists
- **Partially verified**: Some checks pass, some cannot be confirmed
- **Unverifiable**: URL dead, no archive, content doesn't match
- **Rejected**: Evidence contradicts the finding it's cited for

---

### `[PATTERN]` — Behavioral Pattern

A reference to an observed behavioral pattern with metrics.

| Check | Level | Pass Criteria | Failure Action |
|-------|-------|--------------|----------------|
| Metric is specific | Automated | Contains a number or percentage (not vague language) | Reject; require specific metric |
| Sample size stated | Automated | Number of posts/interactions analyzed is documented | Flag as incomplete |
| Time period stated | Automated | Pattern observation period is specified | Flag as incomplete |
| Statistical significance | Semi-automated | Pattern exceeds baseline rates for authentic accounts | Downgrade confidence if marginal |
| Methodology documented | Manual | How the pattern was detected is described | Flag methodology gap |
| Reproducible | Manual | Another analyst could observe the same pattern with the same data | Flag if bespoke/unreproducible |

**Verification Result**:
- **Verified**: Specific metric, adequate sample size, methodology clear, exceeds baseline
- **Partially verified**: Metric specific but methodology unclear or sample size small
- **Unverifiable**: Vague description, no metrics, no methodology
- **Rejected**: Pattern is within baseline range for authentic accounts

---

### `[NETWORK]` — Network/Relationship Data

A reference to network connections or coordination patterns.

| Check | Level | Pass Criteria | Failure Action |
|-------|-------|--------------|----------------|
| Relationship type specified | Automated | States what kind of relationship (retweet, mention, reply, follow) | Reject; require specificity |
| Connected accounts named | Automated | At least one connected account is specifically identified | Flag if only described generically |
| Interaction count stated | Semi-automated | Number of interactions documented | Flag if vague ("frequently interacts") |
| Directionality clear | Automated | Who amplifies whom is stated | Flag ambiguity |
| Coordination evidence | Manual | Evidence of coordination vs. organic interaction | Flag if could be organic |
| Cross-platform corroboration | Manual | Same relationship pattern observed on multiple platforms | Increases confidence if present |

**Verification Result**:
- **Verified**: Specific accounts named, interaction counts documented, coordination evidence present
- **Partially verified**: Relationships identified but coordination not confirmed
- **Unverifiable**: Generic "network" references without specifics
- **Rejected**: Described relationships are normal/organic interaction patterns

---

### `[METADATA]` — Account Metadata

A reference to account-level metadata (creation date, bio, profile changes).

| Check | Level | Pass Criteria | Failure Action |
|-------|-------|--------------|----------------|
| Data source stated | Automated | Where the metadata was obtained (API, manual, cached) | Flag if unattributed |
| Timestamp of collection | Automated | When the metadata was captured | Flag if undated |
| Data matches current state | Semi-automated | Metadata consistent with current account state | Note if changed since collection |
| Historical data sourced | Semi-automated | For historical claims (bio changes, name changes), source is cited | Flag if no historical evidence |
| Platform-specific validation | Automated | Metadata fields match platform expectations (e.g., Twitter created date format) | Reject if invalid format |

**Verification Result**:
- **Verified**: Data source clear, timestamp present, matches current or documented historical state
- **Partially verified**: Data present but source or timestamp unclear
- **Unverifiable**: No data source, no timestamp
- **Rejected**: Metadata contradicts the finding it supports

---

### `[EXTERNAL]` — Third-Party Source

A reference to an external source (government report, database, news article, academic paper).

| Check | Level | Pass Criteria | Failure Action |
|-------|-------|--------------|----------------|
| Source identified | Automated | Author/organization and publication are named | Reject; require attribution |
| URL provided | Automated | Link to the original source | Flag if no URL |
| URL resolves | Automated | Source is accessible | Flag; check archive |
| Source is credible | Semi-automated | Source is a recognized organization (check against known sources list) | Flag if unknown source |
| Claim matches source | Manual | What the briefing says the source says matches the actual source content | Reject if misrepresented |
| Date is current | Automated | Source is not outdated for the claim being made | Flag if source is significantly older than analysis |

**Verification Result**:
- **Verified**: Source identified, URL resolves, content matches, source is credible
- **Partially verified**: Source identified but URL dead or content match uncertain
- **Unverifiable**: Source not identified or not accessible
- **Rejected**: Source misrepresented or not credible

---

## Aggregate Verification Score

For each briefing, calculate:

| Metric | Formula |
|--------|---------|
| **Verification rate** | Verified references / Total references |
| **Partial rate** | Partially verified / Total |
| **Unverifiable rate** | Unverifiable / Total |
| **Rejection rate** | Rejected / Total |

**Quality Thresholds**:
- **Production-ready**: Verification rate >= 80%, Rejection rate = 0%
- **Needs review**: Verification rate 60-79% or any rejections
- **Unacceptable**: Verification rate < 60%

---

## Common Verification Failures

| Failure Pattern | Frequency | Mitigation |
|----------------|-----------|------------|
| Deleted social media posts | High | Always archive before analysis |
| Vague pattern descriptions ("frequently posts") | High | Require specific metrics in prompt |
| Circular references (CDDBS cites CDDBS) | Medium | Require external corroboration |
| Outdated external sources | Medium | Check publication date |
| Misattributed quotes | Low | Cross-check with original source |
| Hallucinated URLs | High (LLM) | Automated URL validation check |

---

## Integration with Quality Scorer

The source verification results feed into two quality dimensions:

1. **Attribution Quality** (Dimension 2): Scored based on verification rate and specificity
2. **Evidence Presentation** (Dimension 4): Scored based on evidence coverage and verification results

Scoring impact:
- Each **verified** reference: +1 point toward Attribution Quality
- Each **rejected** reference: -2 points (penalizes false evidence more heavily)
- Each **unverifiable** reference: -1 point
- Briefing with 0% verification rate: Attribution Quality score = 0
