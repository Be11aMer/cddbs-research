# Cybersecurity Disinformation Detection Briefing System (CDDBS)

> An automated intelligence briefing system that monitors, analyzes, and summarizes media narratives to detect and explain disinformation patterns — combining LLM-driven analysis with professional intelligence community standards.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/LLM-Gemini%202.5%20Flash-4285F4?logo=google)](https://ai.google.dev/)
[![Sprint](https://img.shields.io/badge/Sprint-9%20%E2%80%94%20Complete-brightgreen)](docs/sprint_9_backlog.md)

`#disinformation` `#ai-safety` `#nlp` `#media-analysis` `#intelligence-briefing` `#osint` `#information-operations` `#llm` `#democratic-resilience` `#fact-checking` `#narrative-detection` `#telegram` `#twitter` `#media-monitoring`

---

## What is CDDBS?

CDDBS is a research and development project building a system to analyze media outlets and social media accounts for potential disinformation activity. It uses LLM-based analysis (Google Gemini) to produce structured **intelligence briefings** that assess:

- **Source credibility** — behavioral indicators and outlet history
- **Narrative alignment** — matching against 50+ known disinformation narratives across 8 categories
- **Cross-outlet coordination** — detecting coordinated narrative pushing across outlets on the same topic
- **Cross-platform amplification** — tracking how narratives propagate across news, Twitter/X, and Telegram
- **Quality scoring** — 7-dimension, 70-point rubric for briefing reliability
- **AI trustworthiness** — grounding scores, output validation, confidence calibration

The system implements a multi-stage pipeline adhering to intelligence community briefing standards studied from EUvsDisinfo, DFRLab, Bellingcat, NATO StratCom COE, and others.

---

## Live Application

| Service | URL |
|---------|-----|
| Frontend (Cloudflare Workers) | [cddbs-frontend.projectsfiae.workers.dev](https://cddbs-frontend.projectsfiae.workers.dev/) |
| Frontend (Render) | [cddbs-frontend.onrender.com](https://cddbs-frontend.onrender.com/) |
| Backend API | [cddbs-api.onrender.com](https://cddbs-api.onrender.com/) |

> **Wake-up sequence** (Render free tier spins down after inactivity):
> 1. Wake backend: visit the API URL and wait 30–60 seconds for the status message
> 2. Open either frontend URL

**Architecture & Security Model:**
- API keys (SerpAPI + Gemini) are stored exclusively in server environment variables
- CORS hardened with explicit origin list (no wildcards)
- Rate limiting on all mutation endpoints
- Input sanitization against prompt injection
- EU AI Act Art. 50 AI provenance disclosure on every analysis

---

## Try It in Google Colab

No local setup required. Open any notebook directly in Colab:

| Notebook | Description | Open |
|----------|-------------|------|
| `CDDBS_Main.ipynb` | Full refactored pipeline (v1.0) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Be11aMer/cddbs-research-draft/blob/main/notebooks/CDDBS_Main.ipynb) |
| `CDDBS_v0.1.0_POC.ipynb` | Original proof of concept | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Be11aMer/cddbs-research-draft/blob/main/notebooks/CDDBS_v0.1.0_POC.ipynb) |
| `CDDBS_v0.2.0_enhanced.ipynb` | Enhanced pipeline (v0.2) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Be11aMer/cddbs-research-draft/blob/main/notebooks/CDDBS_v0.2.0_enhanced.ipynb) |

**Colab Setup (2 steps):**
1. Click the key icon in the left sidebar, add secrets: `GOOGLE_API_KEY` and `SERPER_API`
2. Run all cells, execute: `run_cddbs_analysis('RT', 'rt.com', 'Russia')`

See [docs/API_SETUP.md](docs/API_SETUP.md) for full API key setup instructions.

---

## Project Status & Roadmap

**Current Version**: v0.9.0 (Sprint 9 complete — 2026-03-28)

> Versioning: `0.x.y` semver — major version 0 signals pre-release (personal testing + stakeholder demos). `1.0.0` will be cut when authentication exists and external testers are onboarded.

### Completed Sprints

| Sprint | Version | Focus | Key Deliverables |
|--------|---------|-------|------------------|
| 1 | v0.1.0 | Briefing Format Redesign | 7-section briefing template, JSON Schema, system prompt v1.1 |
| 2 | v0.2.0 | Quality & Reliability | 70-point quality rubric, 18 narratives, 41 tests |
| 3 | v0.3.0 | Multi-Platform Support | Telegram analysis, platform adapters, 80 tests |
| 4 | v0.4.0 | Production Integration | Quality scorer + narrative matcher in pipeline, frontend components, 136 tests |
| 5 | v0.5.0 | Operational Maturity | JSON export, metrics, DEVELOPER.md, CI pipeline, 132 prod tests |
| 6 | v0.6.0 | CI Compliance Pipeline | Secret scan, docs drift, branch policy, SECURITY.md |
| 7 | v0.7.0 | Intelligence Layer | Event clustering, burst detection, narrative risk scoring, events API, 204 tests |
| 8 | v0.8.0 | Topic Mode Innovations | Coordination signal, key claims/omissions, AI provenance, SBOM, pip-audit, 214 tests |
| 9 | v0.9.0 | AI Trust & Security | Input sanitization, output validation, grounding score, rate limiting, security headers, dependency scanner, 249 tests |

### Upcoming

| Sprint | Target | Focus |
|--------|--------|-------|
| 10 | v0.10.0 | User Authentication + CDDBS-Edge Phase 0 |
| 11 | v0.11.0 | Collaboration (analyst annotations, shared workspaces) |
| 12 | v0.12.0 | Advanced features (ML fine-tuning, multi-language) |

---

### CDDBS-Edge — Parallel Experimental Track

[![Status](https://img.shields.io/badge/status-concept%2Fexperiment-lightgrey)](research/cddbs_edge_concept.md)

> *"What happens when the cloud goes down, the API gets blocked, or you're a journalist in a country that restricts internet access?"*

A portable, offline-capable version of CDDBS built on a **Raspberry Pi 5** running a **local quantized LLM** (Phi-3 Mini 3.8B via Ollama), replacing all cloud API calls.

See [research/cddbs_edge_concept.md](research/cddbs_edge_concept.md) for the full concept.

---

## Architecture

### Current Stack (v0.9.0)

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI + uvicorn + slowapi (Render) |
| Frontend | React 18 + TypeScript + MUI 6 + Vite (Cloudflare Workers + Render) |
| Database | PostgreSQL 15 (Neon managed, 12 tables) |
| LLM | Google Gemini 2.5 Flash via google-genai SDK |
| Data Sources | SerpAPI (Google News), GDELT (Cloudflare Workers proxy), RSS feeds |
| CI | GitHub Actions (7 workflows: lint, test, SBOM, pip-audit, dependency scanner, secret scan, docs drift) |

### Analysis Pipeline

```
Input (outlet / topic / account)
        |
        v
   [Fetch]  SerpAPI Google News / GDELT / RSS
        |
        v
   [Sanitize]  Input validation + prompt injection prevention
        |
        v
   [Analyze]  Gemini LLM — narrative evaluation, disinformation markers
        |
        v
   [Validate]  Output schema validation + grounding score computation
        |
        v
   [Score]  7-dimension quality scorer (70-point rubric)
        |
        v
   [Match]  Narrative detection (50+ known disinformation narratives)
        |
        v
   Output: Intelligence briefing + quality scorecard + narrative tags + AI provenance
```

---

## Repository Structure

```
cddbs-research/
├── notebooks/                           # Original MVP & POC notebooks
├── research/                            # Research notebooks & design docs
│   ├── briefing_format_analysis.ipynb   # 10 professional formats analyzed
│   ├── event_intelligence_pipeline.md   # Sprint 6-7 architecture
│   ├── information_security_analysis.md # Sprint 9 security audit
│   ├── cddbs_edge_concept.md           # Offline CDDBS concept
│   └── ...
├── templates/                           # Briefing templates & system prompts
├── schemas/                             # JSON Schema for structured output
├── data/                                # Narratives DB, RSS feeds, samples
├── tools/                               # Quality scorer, platform adapters
├── tests/                               # 80 research-repo tests
├── docs/                                # Sprint backlogs & plans
│   ├── cddbs_execution_plan.md         # Full project vision & roadmap
│   ├── sprint_8_backlog.md
│   ├── sprint_9_backlog.md
│   └── ...
├── retrospectives/                      # Sprint retrospectives
│   ├── sprint_1.md through sprint_8.md
│   └── ...
├── compliance-practices/                # Compliance documentation
│   └── sprint_compliance_log.md        # Per-sprint compliance measures
├── blog/                                # Public-facing writeups
└── .github/workflows/ci.yml
```

---

## Research & Writeups

Sprint documentation and research live in [`docs/`](docs/) and [`research/`](research/):

- [Project Vision & Sprint Roadmap](docs/cddbs_execution_plan.md)
- [Sprint 9 Backlog — AI Trust & Security](docs/sprint_9_backlog.md)
- [Information Security Analysis](research/information_security_analysis.md)
- [Event Intelligence Pipeline Architecture](research/event_intelligence_pipeline.md)
- [Briefing Format Analysis](research/briefing_format_analysis.ipynb) — 10 professional formats benchmarked
- [Sprint Retrospectives](retrospectives/)
- [Compliance Log](compliance-practices/sprint_compliance_log.md) — 9 sprints of compliance measures

### Key Research Findings

**Briefing Format Study (Sprint 1):**
- Only 3/10 organizations use explicit confidence signaling — a major gap
- Per-finding confidence levels are a CDDBS innovation (none of the 10 benchmarked do this)
- CDDBS occupies a unique niche: database consistency + policy brief depth

**Security Audit (Sprint 9):**
- 11 security issues identified across 9 dimensions (4 HIGH, 1 CRITICAL)
- OWASP LLM Top 10 mapping: LLM01, LLM02, LLM04, LLM06, LLM09 applicable to CDDBS
- All HIGH findings resolved; CRITICAL (no auth) deferred to Sprint 10

---

## Compliance & Security

| Framework | Measures |
|-----------|----------|
| EU AI Act | 10 measures (Art. 9, 12, 14, 50 — quality, record-keeping, oversight, transparency) |
| CRA | 12 measures (SBOM, vulnerability scanning, dependency scanner, SHA-pinned Actions) |
| DSGVO | 6 measures (no PII, data minimization, BYOK, secret protection) |
| OWASP LLM Top 10 | 5 risks mitigated (prompt injection, insecure output, model DoS, sensitive info, overreliance) |

See [compliance-practices/sprint_compliance_log.md](compliance-practices/sprint_compliance_log.md) for the full per-sprint compliance log.

---

## Key Principles

1. **Evidence over speed** — Every claim must be traceable to evidence
2. **Confidence transparency** — Always communicate uncertainty honestly
3. **Reproducibility** — Analyses should be reproducible with the same inputs
4. **Professional standards** — Output should meet intelligence community standards
5. **Security by default** — Input validation, output validation, rate limiting from the start

---

## Related Repositories

- **[cddbs-prod](https://github.com/Be11aMer/cddbs-prod)** (private) — Production application code (FastAPI backend + React frontend + PostgreSQL)

---

## License

MIT — see [LICENSE](LICENSE).

---

## Collaboration

CDDBS is an open research prototype for academic and policy collaboration in disinformation analysis, media monitoring, and intelligence automation.

Researchers, journalists, or institutions interested in collaboration, methodological review, or exploring applications in democratic resilience are welcome to reach out:

**Email**: angaben@pm.me
