# Cybersecurity Disinformation Detection Briefing System (CDDBS)

> An automated intelligence briefing system that monitors, analyzes, and summarizes media narratives to detect and explain disinformation patterns — combining LLM-driven analysis with professional intelligence community standards.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/LLM-Gemini%202.5%20Flash-4285F4?logo=google)](https://ai.google.dev/)
[![Sprint](https://img.shields.io/badge/Sprint-5%20%E2%80%94%20In%20Progress-orange)](docs/sprint_5_backlog.md)

`#disinformation` `#ai-safety` `#nlp` `#media-analysis` `#intelligence-briefing` `#osint` `#information-operations` `#llm` `#democratic-resilience` `#fact-checking` `#narrative-detection` `#telegram` `#twitter` `#media-monitoring`

---

## What is CDDBS?

CDDBS is a research and development project building a system to analyze media outlets and social media accounts for potential disinformation activity. It uses LLM-based analysis (Google Gemini) to produce structured **intelligence briefings** that assess:

- **Source credibility** — behavioral indicators and outlet history
- **Narrative alignment** — matching against 18 known disinformation narratives across 8 categories
- **Cross-platform amplification** — tracking how narratives propagate across news, Twitter/X, and Telegram
- **Quality scoring** — 7-dimension, 70-point rubric for briefing reliability

The system implements a multi-stage pipeline: **Fetch → Analyze → Digest → Translate → Summarize**, adhering to intelligence community briefing standards studied from EUvsDisinfo, DFRLab, Bellingcat, NATO StratCom COE, and others.

---

## Live Application

The current production deployment of CDDBS is hosted on Render.

> **Wake-up sequence** (Render free tier spins down after inactivity):
> 1. Wake backend: visit [cddbs-api.onrender.com](https://cddbs-api.onrender.com/) and wait 30–60 seconds for the status message
> 2. Open frontend: [cddbs-frontend.onrender.com](https://cddbs-frontend.onrender.com/)

**Architecture & Security Model:**
- **BYOK (Bring Your Own Key)**: API keys (SerpAPI + Gemini) are stored only in the user's browser — never on the server
- **Centralized research DB**: PostgreSQL for collaborative verification of disinformation patterns found during the research phase

---

## Try It in Google Colab

No local setup required. Open any notebook directly in Colab:

| Notebook | Description | Open |
|----------|-------------|------|
| `CDDBS_Main.ipynb` | Full refactored pipeline (v1.0) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Be11aMer/cddbs-research-draft/blob/main/notebooks/CDDBS_Main.ipynb) |
| `CDDBS_v0.1.0_POC.ipynb` | Original proof of concept | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Be11aMer/cddbs-research-draft/blob/main/notebooks/CDDBS_v0.1.0_POC.ipynb) |
| `CDDBS_v0.2.0_enhanced.ipynb` | Enhanced pipeline (v0.2) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Be11aMer/cddbs-research-draft/blob/main/notebooks/CDDBS_v0.2.0_enhanced.ipynb) |
| `multi_source_v0.3.0_dev.ipynb` | Multi-source experiment (dev) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Be11aMer/cddbs-research-draft/blob/main/notebooks/experiments/multi_source_v0.3.0_dev.ipynb) |
| `briefing_format_analysis.ipynb` | Briefing format research | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Be11aMer/cddbs-research-draft/blob/main/research/briefing_format_analysis.ipynb) |
| `prompt_optimization.ipynb` | Prompt engineering research | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Be11aMer/cddbs-research-draft/blob/main/research/prompt_optimization.ipynb) |
| `telegram_platform_analysis.ipynb` | Telegram disinformation research | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Be11aMer/cddbs-research-draft/blob/main/research/telegram_platform_analysis.ipynb) |

**Colab Setup (2 steps):**
1. Click the key icon in the left sidebar → add secrets: `GOOGLE_API_KEY` and `SERPER_API`
2. Run all cells → execute: `run_cddbs_analysis('RT', 'rt.com', 'Russia')`

See [docs/API_SETUP.md](docs/API_SETUP.md) for full API key setup instructions.

---

## Project Status & Roadmap

**Current Phase**: Sprint 5 — Operational Maturity & Data Ingestion (Mar 3–16, 2026)

### Completed

**Phase 1 — MVP** (cddbs-research, original prototype)
- [x] Core analysis pipeline (Fetch → Analyze → Digest → Translate → Summarize)
- [x] LangGraph workflow orchestration
- [x] SerpAPI news discovery + Gemini LLM analysis
- [x] PostgreSQL database integration
- [x] Web interface + production deployment on Render
- [x] BYOK security model

**Sprint 1 — Briefing Format Redesign** (v1.1.0)
- [x] Researched 10 professional intelligence briefing formats (EUvsDisinfo, DFRLab, Bellingcat, NATO StratCom COE, Stanford IO, Graphika, RAND, UK DCMS, GEC, Oxford II)
- [x] CDDBS v1.1 briefing template (7 mandatory sections)
- [x] JSON Schema (draft-07) for structured briefing output
- [x] System prompt v1.1 with confidence framework and attribution standards
- [x] Frontend mockup with sample RT analysis

**Sprint 2 — Quality & Reliability** (v1.2.0)
- [x] Automated quality scorer (7 dimensions, 70-point rubric)
- [x] Known narratives reference dataset (8 categories, 18 narratives)
- [x] Source verification framework (5 evidence types)
- [x] 41 automated tests (schema validation + quality scoring)
- [x] System prompt v1.2 with narrative detection + self-validation

**Sprint 3 — Multi-Platform Support** (v1.3.0)
- [x] Telegram platform analysis and behavioral indicators
- [x] Cross-platform identity correlation framework
- [x] Network analysis (graph model, community detection design)
- [x] Platform adapters for Twitter + Telegram data normalization
- [x] Schema v1.2.0 with multi-platform fields and network graph
- [x] API rate limiting design (Twitter v2 + Telegram MTProto)
- [x] 80 total tests (39 new)

**Sprint 4 — Production Integration** (v1.4.0)
- [x] Quality scorer wired into live analysis pipeline
- [x] Narrative matcher running against 18 known narratives post-analysis
- [x] 3 new API endpoints (quality, narratives, narratives DB)
- [x] 3 new database tables (briefings, narrative_matches, feedback)
- [x] Frontend: QualityBadge, QualityRadarChart, NarrativeTags components
- [x] Dashboard metrics: Avg Quality + Narratives Detected
- [x] Feedback system, keyboard shortcuts, cold start handling
- [x] 56 new production tests

### In Progress

**Sprint 5 — Operational Maturity & Data Ingestion** (v1.5.0)
- [ ] Twitter API v2 adapter wired into pipeline
- [ ] Batch analysis support (multiple outlets in single request)
- [ ] Export formats (PDF, JSON, CSV)
- [ ] End-to-end integration tests with real API validation
- [ ] Analysis monitoring and alerting infrastructure
- [ ] Network graph visualization in frontend

### Upcoming

**Sprint 6 — Scale & Event Intelligence** (v1.6.0, Mar 17–30, 2026)
- [ ] Event Intelligence Pipeline: RSS + GDELT multi-source ingestion
- [ ] Event clustering (TF-IDF agglomerative) + burst detection (z-score)
- [ ] Narrative risk scoring (4-signal composite)
- [ ] Telegram Bot API integration

**Sprint 7 — Intelligence Layer** (Apr 2026)
- [ ] `/events` API endpoints with map visualization
- [ ] EventClusterPanel, BurstTimeline, EventDetailDialog frontend components

**Sprints 7–8 — Collaborative Features** (Apr 2026)
- [ ] User authentication and analyst workspaces
- [ ] Analyst annotations and comments on briefings

**Sprints 9–12 — Advanced Features** (May–Jul 2026)
- [ ] ML model fine-tuning for improved narrative detection
- [ ] Automated monitoring schedules
- [ ] API for third-party integration
- [ ] Multi-language support

---

### CDDBS-Edge — Parallel Experimental Track

[![Status](https://img.shields.io/badge/status-concept%2Fexperiment-lightgrey)](research/cddbs_edge_concept.md)

> *"What happens when the cloud goes down, the API gets blocked, or you're a journalist in a country that restricts internet access?"*

A portable, offline-capable version of CDDBS built on a **Raspberry Pi 5** running a **local quantized LLM** (Phi-3 Mini 3.8B via Ollama), replacing all cloud API calls. Output delivered via MQTT to an e-ink display or external screen.

**Designed for**: Journalists in restricted-internet environments, field reporting, infrastructure resilience scenarios.

**Experiment roadmap**:
- [ ] Phase 0 — Software-only: Swap Gemini → Ollama on laptop, benchmark briefing quality
- [ ] Phase 1 — Pi deployment: Pipeline on Pi 5 8GB, benchmark speed & RAM
- [ ] Phase 2 — Display: Wire MQTT + Mosquitto, test e-ink HAT vs MQTT subscriber
- [ ] Phase 3 — Offline data ingestion: USB-based article import or minimal RSS fetch design

See [research/cddbs_edge_concept.md](research/cddbs_edge_concept.md) for full evaluation, architecture, and open questions.

---

## Architecture

### Current Stack (v1.4.0)

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI + uvicorn (Docker, Render) |
| Frontend | React 18 + TypeScript + MUI 6 + Vite (Render/Nginx) |
| Database | PostgreSQL 15 (Neon managed, 6 tables) |
| LLM | Google Gemini 2.5 Flash via google-genai SDK |
| Data Sources | SerpAPI Google News (Twitter API v2 planned v1.5.0) |
| Source Code | GitHub (`cddbs-prod` + this repo) |

### Analysis Pipeline

```
Input (outlet / topic / account)
        │
        ▼
   [Fetch]  SerpAPI Google News discovery
        │
        ▼
   [Analyze]  Gemini LLM — narrative evaluation, disinformation markers
        │
        ▼
   [Digest]  Key claims + rhetorical strategy extraction
        │
        ▼
   [Translate]  Multi-lingual support (cross-border narrative tracking)
        │
        ▼
   [Summarize]  Structured intelligence briefing (JSON Schema v1.2)
        │
        ▼
   [Score]  7-dimension quality scorer (70-point rubric)
        │
        ▼
   [Match]  Narrative detection against 18 known disinformation narratives
        │
        ▼
   Output: Professional briefing + quality scorecard + narrative tags
```

---

## Repository Structure

```
cddbs-research-draft/
├── notebooks/                          # Original MVP & POC notebooks
│   ├── CDDBS_Main.ipynb                # Full refactored pipeline (v1.0)
│   ├── CDDBS_v0.1.0_POC.ipynb         # Original proof of concept
│   ├── CDDBS_v0.2.0_enhanced.ipynb    # Enhanced pipeline
│   └── experiments/
│       └── multi_source_v0.3.0_dev.ipynb
├── research/                           # Research notebooks & documentation
│   ├── briefing_format_analysis.ipynb  # 10 professional formats analyzed
│   ├── prompt_optimization.ipynb       # Prompt engineering experiments
│   ├── telegram_platform_analysis.ipynb
│   ├── cross_platform_correlation.ipynb
│   ├── network_analysis.ipynb
│   ├── platform_adapters_demo.ipynb
│   ├── quality_scoring_analysis.ipynb
│   ├── quality_testing_framework.md    # 7-dimension, 70-point rubric design
│   ├── source_verification_framework.md
│   ├── cross_platform_correlation.md
│   ├── network_analysis_framework.md
│   ├── event_intelligence_pipeline.md  # Sprint 6-7 architecture design
│   └── api_rate_limiting.md
├── templates/                          # Briefing templates & prompts
│   ├── intelligence_briefing.md        # CDDBS v1.1 briefing template
│   ├── system_prompt_v1.1.md
│   ├── system_prompt_v1.2.md
│   └── system_prompt_v1.3.md
├── schemas/
│   └── briefing_v1.json               # JSON Schema draft-07 (v1.2.0)
├── data/
│   ├── known_narratives.json          # 8 categories, 18 narratives
│   ├── rss_feeds.json                 # 15 curated OSINT-grade RSS feeds
│   └── sample_outputs/               # Sample briefing outputs from MVP
│       ├── test_POC_0.txt
│       ├── test_v0.2.0_0.txt
│       └── test_v0.2.0_1.txt
├── tools/
│   ├── quality_scorer.py              # 7-dimension automated scorer
│   └── platform_adapters.py          # Twitter + Telegram normalization
├── tests/                             # 80 tests
│   ├── fixtures/                      # 6 test briefing fixtures
│   ├── test_schema_validation.py
│   ├── test_quality_scorer.py
│   └── test_platform_adapters.py
├── mockups/
│   └── briefing_mockup.html          # Frontend mockup (RT sample analysis)
├── docs/                              # Documentation & sprint writeups
│   ├── API_SETUP.md                  # API key setup for Colab
│   ├── cddbs_execution_plan.md       # Full project vision & sprint roadmap
│   ├── sprint_1_quickstart.md
│   ├── sprint_2_backlog.md
│   ├── sprint_3_backlog.md
│   ├── sprint_3_context.md
│   ├── sprint_4_plan.md
│   ├── sprint_4_integration_log.md
│   ├── sprint_5_backlog.md
│   ├── sprint_5_context.md
│   ├── sprint_5_integration_log.md
│   ├── sprint_6_backlog.md
│   └── diagrams/
│       └── POC_workflow.png
├── retrospectives/                    # Sprint retrospectives
│   ├── sprint_1.md
│   ├── sprint_2.md
│   ├── sprint_3.md
│   └── sprint_4.md
├── patches/
│   └── sprint5_production_changes.patch
├── .github/workflows/ci.yml          # CI/CD (pytest, schema, notebooks)
├── requirements.txt                   # Python dependencies
└── LICENSE                           # MIT
```

---

## Research & Writeups

Sprint documentation and research writeups live in [`docs/`](docs/) and [`research/`](research/):

- [Project Vision & Sprint Roadmap](docs/cddbs_execution_plan.md)
- [Event Intelligence Pipeline Architecture](research/event_intelligence_pipeline.md)
- [Briefing Format Analysis](research/briefing_format_analysis.ipynb) — 10 professional formats benchmarked
- [Source Verification Framework](research/source_verification_framework.md)
- [Cross-Platform Correlation](research/cross_platform_correlation.md)
- [Network Analysis Framework](research/network_analysis_framework.md)
- [API Rate Limiting Design](research/api_rate_limiting.md)
- [Sprint Retrospectives](retrospectives/)

### Key Research Findings

**Briefing Format Study (Sprint 1):**
- Only 3/10 organizations use explicit confidence signaling — a major gap
- Per-finding confidence levels are a CDDBS innovation (none of the 10 benchmarked do this)
- CDDBS occupies a unique niche: database consistency + policy brief depth
- Mandatory limitations section builds trust (learned from Bellingcat, SIO)

**Telegram Analysis (Sprint 3):**
- Forwarding chains are more traceable than Twitter retweets (source attribution preserved)
- Channel admin anonymity is the key attribution challenge
- Cross-platform correlation significantly strengthens assessments
- Telegram serves as early warning — new narratives often appear there first before going mainstream

---

## Key Principles

1. **Evidence over speed** — Every claim must be traceable to evidence
2. **Confidence transparency** — Always communicate uncertainty honestly
3. **Reproducibility** — Analyses should be reproducible with the same inputs
4. **Professional standards** — Output should meet intelligence community standards
5. **Cost discipline** — Stay within free/low-cost tier limits

---

## Related Repositories

- **cddbs-prod** (private) — Production application code for live application. (FastAPI backend + React frontend + Postgres db)

---

## License

MIT — see [LICENSE](LICENSE).

---

## Collaboration

CDDBS is an open research prototype for academic and policy collaboration in disinformation analysis, media monitoring, and intelligence automation.

Researchers, journalists, or institutions interested in collaboration, methodological review, or exploring applications in democratic resilience are welcome to reach out:

**Email**: angaben@pm.me

*Suggested GitHub topics: `disinformation`, `ai-safety`, `nlp`, `media-analysis`, `intelligence-briefing`, `osint`, `information-operations`, `llm`, `democratic-resilience`, `fact-checking`, `narrative-detection`, `telegram`, `media-monitoring`, `python`*
