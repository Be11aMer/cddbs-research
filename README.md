# cddbs-research-draft

Research and development workspace for the **Counter-Disinformation Database System (CDDBS)**.

This repository contains research notebooks, briefing templates, JSON schemas, and documentation supporting the development of CDDBS — a system for analyzing social media accounts for potential disinformation activity using LLM-based intelligence briefings.

## Repository Structure

```
cddbs-research-draft/
├── research/                    # Research notebooks
│   └── briefing_format_analysis.ipynb
├── templates/                   # Briefing templates
│   └── intelligence_briefing.md
├── schemas/                     # JSON schemas
│   └── briefing_v1.json
├── retrospectives/              # Sprint retrospectives
├── docs/                        # Documentation
│   ├── cddbs_execution_plan.md
│   └── sprint_1_quickstart.md
└── README.md
```

## Current Sprint

**Sprint 1** — Briefing Format Redesign (Feb 3-16, 2026)

Goal: Redesign the CDDBS intelligence briefing output based on professional intelligence analysis standards. See [docs/sprint_1_quickstart.md](docs/sprint_1_quickstart.md) for details.

## Key Files

| File | Purpose |
|------|---------|
| `research/briefing_format_analysis.ipynb` | Analysis of 10 professional intelligence briefing formats |
| `templates/intelligence_briefing.md` | Draft CDDBS briefing template |
| `schemas/briefing_v1.json` | JSON schema for structured briefing output |
| `docs/cddbs_execution_plan.md` | Full project execution plan |

## Related Repositories

- **cddbs-prod** (Codeberg) — Production application code
- **cddbs-research** (GitHub, public) — Published research outputs

> This is a private working repository. Do not push to `cddbs-research` (public).
