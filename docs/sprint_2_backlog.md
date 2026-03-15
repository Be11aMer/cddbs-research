# CDDBS Sprint 2 Backlog

**Sprint**: 2 - Quality & Reliability
**Duration**: February 17 - March 2, 2026
**Version Target**: v1.2.0
**Predecessor**: Sprint 1 (v1.1.0 - Briefing Format Redesign)

---

## Sprint Goal

Implement automated quality scoring, source verification, and improved narrative detection to ensure CDDBS briefings meet professional standards consistently and reliably.

## Success Criteria

- Automated quality scorer validates all briefings against the 70-point rubric
- Known narrative reference dataset covers major Russian disinformation themes
- Source verification framework integrated into the analysis pipeline
- System prompt v1.2 improves narrative detection accuracy
- All tests pass in CI pipeline
- Quality scores for 10 test briefings average >= 50/70

---

## Task Breakdown

### 3.1 — Automated Quality Scoring
**Priority**: P0-critical
**Labels**: backend, model-quality
**Estimate**: 4 hours

Implement a Python tool that validates briefing JSON output against the Sprint 1 quality framework (7 dimensions, 70 points).

**Subtasks**:
- [ ] Parse briefing JSON against schema
- [ ] Score structural completeness (0-10)
- [ ] Score attribution quality (0-10)
- [ ] Score confidence signaling (0-10)
- [ ] Score evidence presentation (0-10)
- [ ] Score analytical rigor (0-10)
- [ ] Score actionability (0-10)
- [ ] Score readability (0-10)
- [ ] Generate scorecard output (JSON + human-readable)

**Acceptance Criteria**:
- [ ] Scorer runs on any valid briefing JSON
- [ ] Produces per-dimension and total scores
- [ ] Identifies specific deficiencies with actionable feedback
- [ ] Integrated into CI pipeline

**Deliverable**: `tools/quality_scorer.py`

---

### 3.2 — Known Narratives Reference Dataset
**Priority**: P0-critical
**Labels**: research, model-quality
**Estimate**: 6 hours

Create a structured reference dataset of known disinformation narratives for automated matching and detection.

**Subtasks**:
- [ ] Catalog Russian state media narratives (from Sprint 1 research)
- [ ] Organize by theme (anti-NATO, anti-EU, Ukraine, sanctions, etc.)
- [ ] Include keywords and phrases for each narrative
- [ ] Add source references (EUvsDisinfo, GEC pillars)
- [ ] Create JSON schema for narrative entries
- [ ] Include confidence indicators for narrative matching

**Acceptance Criteria**:
- [ ] Minimum 20 documented narrative patterns
- [ ] Each pattern has keywords, description, and source reference
- [ ] JSON schema validates all entries
- [ ] Dataset usable by system prompt for narrative matching

**Deliverable**: `data/known_narratives.json`

---

### 3.3 — Source Verification Framework
**Priority**: P1-high
**Labels**: research, model-quality
**Estimate**: 3 hours

Define a systematic framework for verifying sources cited in CDDBS briefings.

**Subtasks**:
- [ ] Define verification levels (automated, manual, external)
- [ ] Create checklist for each evidence type (post, pattern, network, metadata, external)
- [ ] Define what "verified" means for each evidence type
- [ ] Document common verification failures
- [ ] Create verification result schema

**Acceptance Criteria**:
- [ ] Framework covers all 5 evidence types from v1.1 schema
- [ ] Clear pass/fail criteria for each verification check
- [ ] Integrated into quality scoring pipeline

**Deliverable**: `research/source_verification_framework.md`

---

### 3.4 — Sample Briefing Test Fixtures
**Priority**: P0-critical
**Labels**: backend, model-quality
**Estimate**: 3 hours

Create sample briefing JSON files for testing the quality scorer and schema validation.

**Subtasks**:
- [ ] Create high-quality sample (expected score >= 60)
- [ ] Create medium-quality sample (expected score 40-59)
- [ ] Create low-quality sample (expected score < 40)
- [ ] Create minimal valid sample (just required fields)
- [ ] Create invalid sample (schema violations)

**Acceptance Criteria**:
- [ ] All valid samples pass schema validation
- [ ] Invalid sample fails schema validation
- [ ] Quality scores match expected ranges
- [ ] Samples cover different account types (state media, proxy, authentic)

**Deliverable**: `tests/fixtures/`

---

### 3.5 — Schema Validation & Quality Test Suite
**Priority**: P0-critical
**Labels**: backend
**Estimate**: 4 hours

Build a Python test suite validating the schema and quality scorer.

**Subtasks**:
- [ ] Schema validation tests (valid/invalid JSON)
- [ ] Quality scorer unit tests (per-dimension scoring)
- [ ] Integration tests (full pipeline: JSON → validation → scoring)
- [ ] Regression tests (ensure known samples produce expected scores)
- [ ] CI integration (pytest runs in GitHub Actions)

**Acceptance Criteria**:
- [ ] All tests pass
- [ ] Coverage includes all 7 quality dimensions
- [ ] CI pipeline runs tests on every push

**Deliverable**: `tests/`

---

### 3.6 — System Prompt v1.2
**Priority**: P1-high
**Labels**: model-quality
**Estimate**: 4 hours

Revise the system prompt to improve narrative detection accuracy and quality scoring.

**Subtasks**:
- [ ] Add known narratives reference for in-context matching
- [ ] Improve attribution language enforcement
- [ ] Add explicit instructions for limitations section
- [ ] Improve confidence calibration instructions
- [ ] Add output validation instructions (self-check before output)

**Acceptance Criteria**:
- [ ] Prompt produces briefings scoring >= 50/70 on quality rubric
- [ ] Narrative detection correctly identifies known patterns
- [ ] Confidence levels are well-calibrated (not over/under-confident)
- [ ] Limitations section is substantive (not boilerplate)

**Deliverable**: `templates/system_prompt_v1.2.md`

---

### 3.7 — Prompt Optimization Research
**Priority**: P2-medium
**Labels**: research, model-quality
**Estimate**: 4 hours

Research and document prompt engineering techniques for improving analysis quality.

**Subtasks**:
- [ ] Test chain-of-thought prompting for analysis quality
- [ ] Test structured output enforcement strategies
- [ ] Compare quality across different Gemini model versions
- [ ] Document what works and what doesn't
- [ ] Propose prompt architecture for v1.2

**Acceptance Criteria**:
- [ ] Research notebook with findings
- [ ] Comparison table: technique → quality impact
- [ ] Recommended prompt architecture documented

**Deliverable**: `research/prompt_optimization.ipynb`

---

### 3.8 — CI Pipeline Enhancement
**Priority**: P1-high
**Labels**: backend
**Estimate**: 2 hours

Update GitHub Actions CI to run the full test suite.

**Subtasks**:
- [ ] Add pytest execution to CI
- [ ] Add quality scorer validation on sample fixtures
- [ ] Add schema validation for all JSON files
- [ ] Add narrative dataset validation

**Acceptance Criteria**:
- [ ] CI runs all tests on push
- [ ] Failed tests block merge
- [ ] Quality score thresholds enforced

**Deliverable**: `.github/workflows/ci.yml` (updated)

---

### 3.9 — Sprint 2 Retrospective
**Priority**: P2-medium
**Labels**: documentation
**Estimate**: 1 hour

Document Sprint 2 outcomes and lessons learned.

**Deliverable**: `retrospectives/sprint_2.md`

---

## Sprint 2 Summary

| Task | Priority | Estimate | Deliverable |
|------|----------|----------|-------------|
| 3.1 Automated Quality Scoring | P0 | 4h | `tools/quality_scorer.py` |
| 3.2 Known Narratives Dataset | P0 | 6h | `data/known_narratives.json` |
| 3.3 Source Verification Framework | P1 | 3h | `research/source_verification_framework.md` |
| 3.4 Sample Briefing Fixtures | P0 | 3h | `tests/fixtures/` |
| 3.5 Test Suite | P0 | 4h | `tests/` |
| 3.6 System Prompt v1.2 | P1 | 4h | `templates/system_prompt_v1.2.md` |
| 3.7 Prompt Optimization Research | P2 | 4h | `research/prompt_optimization.ipynb` |
| 3.8 CI Pipeline Enhancement | P1 | 2h | `.github/workflows/ci.yml` |
| 3.9 Sprint Retrospective | P2 | 1h | `retrospectives/sprint_2.md` |
| **Total** | | **31h** | |
