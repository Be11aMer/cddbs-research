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
│   ├── prompt_optimization.ipynb
│   ├── telegram_platform_analysis.ipynb
│   ├── cross_platform_correlation.md
│   ├── network_analysis_framework.md
│   └── api_rate_limiting.md
├── templates/                      # Briefing templates & prompts
│   ├── intelligence_briefing.md
│   ├── system_prompt_v1.1.md
│   ├── system_prompt_v1.2.md
│   └── system_prompt_v1.3.md
├── schemas/                        # JSON schemas
│   └── briefing_v1.json            # v1.2.0 (multi-platform)
├── data/                           # Reference datasets
│   └── known_narratives.json       # 8 categories, 18 narratives
├── tools/                          # Automated tooling
│   ├── quality_scorer.py
│   └── platform_adapters.py
├── tests/                          # Test suites (80 tests)
│   ├── fixtures/                   # Test fixture briefings
│   │   ├── high_quality_briefing.json
│   │   ├── medium_quality_briefing.json
│   │   ├── low_quality_briefing.json
│   │   ├── minimal_valid_briefing.json
│   │   ├── telegram_channel_briefing.json
│   │   └── cross_platform_briefing.json
│   ├── test_schema_validation.py
│   ├── test_quality_scorer.py
│   └── test_platform_adapters.py
├── mockups/                        # Frontend mockups
│   └── briefing_mockup.html
├── retrospectives/                 # Sprint retrospectives
│   ├── sprint_1.md
│   ├── sprint_2.md
│   └── sprint_3.md
├── docs/                           # Documentation
│   ├── cddbs_execution_plan.md
│   ├── sprint_1_quickstart.md
│   ├── sprint_2_backlog.md
│   ├── sprint_3_backlog.md
│   └── sprint_3_context.md
└── README.md
```

## Current Sprint

**Sprint 3** — Multi-Platform Support (Mar 3-16, 2026)

Goal: Extend CDDBS to support Telegram analysis, cross-platform identity correlation, enhanced network analysis, and robust API handling. See [docs/sprint_3_backlog.md](docs/sprint_3_backlog.md) for details.

## Key Deliverables

### Sprint 3 — Multi-Platform Support (v1.3.0)

| File | Task | Description |
|------|------|-------------|
| `research/telegram_platform_analysis.ipynb` | 4.1 | Telegram disinformation research (platform comparison, indicators) |
| `research/cross_platform_correlation.md` | 4.2 | Cross-platform identity resolution framework |
| `research/network_analysis_framework.md` | 4.3 | Graph-based network analysis design |
| `schemas/briefing_v1.json` | 4.4 | Schema v1.2.0 (cross-platform identities, network graph, Telegram fields) |
| `tools/platform_adapters.py` | 4.5 | Twitter + Telegram data normalization adapters |
| `tests/fixtures/telegram_channel_briefing.json` | 4.6 | Telegram channel test fixture (RT English) |
| `tests/fixtures/cross_platform_briefing.json` | 4.6 | Cross-platform entity test fixture |
| `tools/quality_scorer.py` | 4.7 | Updated scorer (new evidence types, cross-platform bonus) |
| `data/known_narratives.json` | 4.8 | Updated: 8 categories, 18 narratives, Telegram patterns |
| `templates/system_prompt_v1.3.md` | 4.9 | Multi-platform prompt (Twitter + Telegram + cross-platform) |
| `research/api_rate_limiting.md` | 4.10 | API rate limiting design (Twitter v2 + Telegram MTProto) |
| `tests/test_platform_adapters.py` | 4.11 | Platform adapter tests (22 tests) |
| `retrospectives/sprint_3.md` | 4.13 | Sprint 3 retrospective |

### Sprint 2 — Quality & Reliability (v1.2.0)

| File | Task | Description |
|------|------|-------------|
| `tools/quality_scorer.py` | 3.1 | Automated 7-dimension quality scorer (70-point rubric) |
| `data/known_narratives.json` | 3.2 | Known narratives reference dataset |
| `research/source_verification_framework.md` | 3.3 | Source verification procedures for all 5 evidence types |
| `templates/system_prompt_v1.2.md` | 3.4 | System prompt v1.2 with narrative detection + self-validation |
| `research/prompt_optimization.ipynb` | 3.5 | Prompt optimization research |
| `tests/` | 3.6 | Schema validation + quality scorer tests |
| `retrospectives/sprint_2.md` | 3.9 | Sprint 2 retrospective |

### Sprint 1 — Briefing Format Redesign (v1.1.0)

| File | Task | Description |
|------|------|-------------|
| `research/briefing_format_analysis.ipynb` | 2.1 | Analysis of 10 professional briefing formats |
| `templates/intelligence_briefing.md` | 2.2 | CDDBS v1.1 briefing template (7 mandatory sections) |
| `schemas/briefing_v1.json` | 2.2 | JSON Schema (draft-07) for structured briefing output |
| `templates/system_prompt_v1.1.md` | 2.4 | System prompt v1.1 |
| `research/quality_testing_framework.md` | 2.5 | 7-dimension, 70-point quality rubric |
| `mockups/briefing_mockup.html` | 2.6 | Frontend mockup with sample RT analysis |

## Research Summary

The briefing format analysis (Task 2.1) studied 10 organizations:
EUvsDisinfo, DFRLab, Bellingcat, NATO StratCom COE, Stanford IO, Graphika, RAND, UK DCMS, GEC, Oxford II.

Key findings:
- Only 3/10 organizations use explicit confidence signaling (major gap)
- Per-finding confidence levels are a CDDBS innovation (none of the 10 do this)
- CDDBS occupies a unique niche: database consistency + policy brief depth
- Mandatory limitations section builds trust (learned from Bellingcat, SIO)

Sprint 3 extended analysis to Telegram:
- Forwarding chains are more traceable than Twitter retweets (source attribution preserved)
- Channel admin anonymity is the key attribution challenge
- Cross-platform correlation strengthens assessments (evidence from multiple platforms)
- Telegram serves as early warning — new narratives often appear there first

## Related Repositories

- **cddbs-prod** (Codeberg) — Production application code
- **cddbs-research** (GitHub, public) — Published research outputs

> This is a private working repository. Do not push to `cddbs-research` (public).
