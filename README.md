# cddbs-research-draft

Research and development workspace for the **Counter-Disinformation Database System (CDDBS)**.

This repository contains research notebooks, briefing templates, JSON schemas, and documentation supporting the development of CDDBS — a system for analyzing social media accounts for potential disinformation activity using LLM-based intelligence briefings.

## Repository Structure

```
cddbs-research-draft/
├── .github/workflows/ci.yml       # CI/CD pipeline (pytest, schema, notebooks)
├── research/                       # Research notebooks
│   ├── briefing_format_analysis.ipynb
│   ├── quality_testing_framework.md
│   ├── source_verification_framework.md
│   └── prompt_optimization.ipynb
├── templates/                      # Briefing templates & prompts
│   ├── intelligence_briefing.md
│   ├── system_prompt_v1.1.md
│   └── system_prompt_v1.2.md
├── schemas/                        # JSON schemas
│   └── briefing_v1.json
├── data/                           # Reference datasets
│   └── known_narratives.json
├── tools/                          # Automated tooling
│   └── quality_scorer.py
├── tests/                          # Test suites
│   ├── fixtures/                   # Test fixture briefings
│   │   ├── high_quality_briefing.json
│   │   ├── medium_quality_briefing.json
│   │   ├── low_quality_briefing.json
│   │   └── minimal_valid_briefing.json
│   ├── test_schema_validation.py
│   └── test_quality_scorer.py
├── mockups/                        # Frontend mockups
│   └── briefing_mockup.html
├── retrospectives/                 # Sprint retrospectives
│   ├── sprint_1.md
│   └── sprint_2.md
├── docs/                           # Documentation
│   ├── cddbs_execution_plan.md
│   ├── sprint_1_quickstart.md
│   └── sprint_2_backlog.md
└── README.md
```

## Current Sprint

**Sprint 2** — Quality & Reliability (Feb 17 – Mar 2, 2026)

Goal: Build automated quality scoring, source verification, known narrative detection, and test infrastructure. See [docs/sprint_2_backlog.md](docs/sprint_2_backlog.md) for details.

## Key Deliverables

### Sprint 2 — Quality & Reliability (v1.2.0)

| File | Task | Description |
|------|------|-------------|
| `tools/quality_scorer.py` | 3.1 | Automated 7-dimension quality scorer (70-point rubric) |
| `data/known_narratives.json` | 3.2 | Known narratives reference dataset (7 categories, 16 narratives) |
| `research/source_verification_framework.md` | 3.3 | Source verification procedures for all 5 evidence types |
| `templates/system_prompt_v1.2.md` | 3.4 | System prompt v1.2 with narrative detection + self-validation |
| `research/prompt_optimization.ipynb` | 3.5 | Prompt optimization research (5 techniques, cost-quality tradeoffs) |
| `tests/test_schema_validation.py` | 3.6 | Schema validation tests (22 tests) |
| `tests/test_quality_scorer.py` | 3.6 | Quality scorer tests (19 tests) |
| `tests/fixtures/` | 3.6 | 4 graded test fixtures (high/medium/low/minimal quality) |
| `.github/workflows/ci.yml` | 3.7 | CI pipeline updated with pytest + quality scoring |
| `retrospectives/sprint_2.md` | 3.9 | Sprint 2 retrospective |

### Sprint 1 — Briefing Format Redesign (v1.1.0)

| File | Task | Description |
|------|------|-------------|
| `research/briefing_format_analysis.ipynb` | 2.1 | Analysis of 10 professional briefing formats with cross-cutting patterns |
| `templates/intelligence_briefing.md` | 2.2 | CDDBS v1.1 briefing template (7 mandatory sections) |
| `schemas/briefing_v1.json` | 2.2 | JSON Schema (draft-07) for structured briefing output |
| `templates/system_prompt_v1.1.md` | 2.4 | System prompt v1.1 with structured output format |
| `research/quality_testing_framework.md` | 2.5 | 7-dimension, 70-point quality rubric |
| `mockups/briefing_mockup.html` | 2.6 | Frontend mockup with sample RT analysis |
| `retrospectives/sprint_1.md` | 2.10 | Sprint retrospective template |

## Research Summary

The briefing format analysis (Task 2.1) studied 10 organizations:
EUvsDisinfo, DFRLab, Bellingcat, NATO StratCom COE, Stanford IO, Graphika, RAND, UK DCMS, GEC, Oxford II.

Key findings:
- Only 3/10 organizations use explicit confidence signaling (major gap)
- Per-finding confidence levels are a CDDBS innovation (none of the 10 do this)
- CDDBS occupies a unique niche: database consistency + policy brief depth
- Mandatory limitations section builds trust (learned from Bellingcat, SIO)

## Related Repositories

- **cddbs-prod** (Codeberg) — Production application code
- **cddbs-research** (GitHub, public) — Published research outputs

> This is a private working repository. Do not push to `cddbs-research` (public).
