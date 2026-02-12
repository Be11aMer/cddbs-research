# cddbs-research-draft

Research and development workspace for the **Counter-Disinformation Database System (CDDBS)**.

This repository contains research notebooks, briefing templates, JSON schemas, and documentation supporting the development of CDDBS — a system for analyzing social media accounts for potential disinformation activity using LLM-based intelligence briefings.

## Repository Structure

```
cddbs-research-draft/
├── .github/workflows/ci.yml       # CI/CD pipeline
├── research/                       # Research notebooks
│   ├── briefing_format_analysis.ipynb
│   └── quality_testing_framework.md
├── templates/                      # Briefing templates & prompts
│   ├── intelligence_briefing.md
│   └── system_prompt_v1.1.md
├── schemas/                        # JSON schemas
│   └── briefing_v1.json
├── mockups/                        # Frontend mockups
│   └── briefing_mockup.html
├── retrospectives/                 # Sprint retrospectives
│   └── sprint_1.md
├── docs/                           # Documentation
│   ├── cddbs_execution_plan.md
│   └── sprint_1_quickstart.md
└── README.md
```

## Current Sprint

**Sprint 1** — Briefing Format Redesign (Feb 3-16, 2026)

Goal: Redesign the CDDBS intelligence briefing output based on professional intelligence analysis standards. See [docs/sprint_1_quickstart.md](docs/sprint_1_quickstart.md) for details.

## Key Deliverables

| File | Task | Description |
|------|------|-------------|
| `research/briefing_format_analysis.ipynb` | 2.1 | Analysis of 10 professional briefing formats with cross-cutting patterns |
| `templates/intelligence_briefing.md` | 2.2 | CDDBS v1.1 briefing template (7 mandatory sections) |
| `schemas/briefing_v1.json` | 2.2 | JSON Schema (draft-07) for structured briefing output |
| `templates/system_prompt_v1.1.md` | 2.4 | System prompt v1.1 with structured output format |
| `research/quality_testing_framework.md` | 2.5 | 7-dimension, 70-point quality rubric |
| `mockups/briefing_mockup.html` | 2.6 | Frontend mockup with sample RT analysis |
| `.github/workflows/ci.yml` | 1.2 | CI pipeline (schema validation, notebook checks) |
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
