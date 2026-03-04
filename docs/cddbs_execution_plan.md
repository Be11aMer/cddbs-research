# CDDBS Execution Plan

**Project**: Counter-Disinformation Database System (CDDBS)
**Start Date**: February 3, 2026
**Delivery Model**: 2-week sprints

---

## Project Vision

CDDBS is a system for analyzing media outlets and social media accounts for potential disinformation activity. It uses LLM-based analysis (Gemini) to produce structured intelligence briefings assessing source credibility, narrative alignment, and behavioral indicators across multiple platforms (news outlets, Twitter/X, Telegram).

---

## Sprint Roadmap

### Sprint 1: Briefing Format Redesign (Feb 3-16, 2026) — COMPLETE
**Target**: v1.1.0 | **Status**: Done

- Researched 10 professional intelligence briefing formats
- Designed CDDBS briefing template with 7 mandatory sections
- Created JSON schema (draft-07) for structured output
- System prompt v1.1 with confidence framework and attribution standards
- Frontend mockup with sample RT analysis

### Sprint 2: Quality & Reliability (Feb 17 - Mar 2, 2026) — COMPLETE
**Target**: v1.2.0 | **Status**: Done

- Automated quality scorer (7 dimensions, 70 points)
- Known narratives reference dataset (7 categories, 16 narratives)
- Source verification framework for 5 evidence types
- 41 tests (schema validation + quality scoring)
- System prompt v1.2 with narrative detection + self-validation

### Sprint 3: Multi-Platform Support (Mar 3-16, 2026) — COMPLETE
**Target**: v1.3.0 | **Status**: Done

- Telegram platform analysis and behavioral indicators
- Cross-platform identity correlation framework
- Network analysis enhancement (graph model, community detection)
- Schema v1.2.0 with multi-platform fields and network graph
- Platform adapters (Twitter + Telegram)
- System prompt v1.3 (multi-platform aware)
- API rate limiting design (Twitter v2 + Telegram MTProto)
- 80 tests total (39 new)

### Sprint 4: Production Integration (Mar 1-3, 2026) — COMPLETE
**Target**: v1.4.0 | **Status**: Done

- Integrated Sprints 1-3 research into live `cddbs-prod` application
- Quality scorer wired into analysis pipeline (7 dimensions, 70 points)
- Narrative matcher running against 18 known narratives post-analysis
- 3 new API endpoints (quality, narratives, narratives DB)
- 3 new database tables (briefings, narrative_matches, feedback)
- Frontend: QualityBadge, QualityRadarChart, NarrativeTags components
- Dashboard metrics: Avg Quality + Narratives Detected
- Unplanned: Feedback system, keyboard shortcuts, cold start handling, skeleton loading
- 56 new tests in production (quality: 23, adapters: 22, narratives: 11)

### Sprint 5: Operational Maturity & Data Ingestion (Mar 3-16, 2026)
**Target**: v1.5.0 | **Status**: In Progress

- Twitter API v2 integration (direct account analysis via platform adapter)
- Batch analysis support (multiple outlets in single request)
- Export formats (PDF, JSON, CSV)
- End-to-end integration tests with real API validation
- Analysis monitoring and alerting infrastructure
- Network graph visualization in frontend
- See [docs/sprint_5_backlog.md](sprint_5_backlog.md) for details

### Sprint 6: Scale & Analytics (Mar 17-30, 2026)
**Target**: v1.6.0

- Telegram Bot API integration (wire TelegramAdapter into pipeline)
- Trend detection (quality and narrative trends over time)
- Webhook alerting (Slack/email on failure spikes)
- Performance optimization at scale

### Sprints 7-8: Collaborative Features (Apr 2026)
- User authentication and authorization
- Shared analysis workspaces
- Analyst annotations and comments on briefings
- Documentation and onboarding

### Sprints 9-12: Advanced Features (May-Jul 2026)
- Machine learning model fine-tuning
- Automated monitoring schedules
- API for third-party integration
- Multi-language support

---

## Architecture

### Current Stack (as of v1.4.0)
- **Backend**: FastAPI + uvicorn on Render (Docker)
- **Frontend**: React 18 + TypeScript + MUI 6 + Vite on Render (Nginx)
- **Database**: PostgreSQL 15 (Neon managed, 6 tables)
- **LLM**: Google Gemini 2.5 Flash via google-genai SDK
- **Data Sources**: SerpAPI Google News (Twitter API v2 planned for v1.5.0)
- **Source Code**: GitHub (cddbs-prod + cddbs-research-draft)

### Achieved Architecture (v1.4.0)
- Structured briefing output validated against JSON Schema v1.2
- 7-dimension quality scoring pipeline (70-point rubric)
- Narrative detection against 18 known disinformation narratives
- Platform adapters for Twitter + Telegram (Twitter integration in v1.5.0)
- Background task processing with auto-polling frontend

### Target Architecture (v1.6.0+)
- Multi-platform data ingestion (Twitter API v2 + Telegram Bot API)
- Batch analysis for multiple targets
- Export pipeline (PDF/JSON/CSV)
- Network graph visualization
- Monitoring and alerting infrastructure

---

## Key Principles

1. **Evidence over speed** - Every claim must be traceable to evidence
2. **Confidence transparency** - Always communicate uncertainty honestly
3. **Reproducibility** - Analyses should be reproducible with the same inputs
4. **Professional standards** - Output should meet intelligence community standards
5. **Cost discipline** - Stay within free/low-cost tier limits
