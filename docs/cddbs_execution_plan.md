# CDDBS Execution Plan

**Project**: Cyber Disinformation Detection Briefing System (CDDBS)
**Start Date**: February 3, 2026
**Delivery Model**: 2-week sprints
**Last Updated**: 2026-03-28

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
- **Compliance**: BYOK architecture, confidence framework, AI labeling, .gitignore for secrets

### Sprint 2: Quality & Reliability (Feb 17 - Mar 2, 2026) — COMPLETE
**Target**: v1.2.0 | **Status**: Done

- Automated quality scorer (7 dimensions, 70 points)
- Known narratives reference dataset (7 categories, 16 narratives)
- Source verification framework for 5 evidence types
- 41 tests (schema validation + quality scoring)
- System prompt v1.2 with narrative detection + self-validation
- **Compliance**: Deterministic quality rubric (independent of AI), automated testing

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
- **Compliance**: Data normalization via adapters, rate limiting respect

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
- **Compliance**: Controlled research→prod transfer, analyst feedback loop

### Sprint 5: Operational Maturity & Data Ingestion (Mar 3-16, 2026) — COMPLETE
**Target**: v0.5.0 | **Status**: Done

- Twitter API v2 integration (direct account analysis via platform adapter)
- Batch analysis support (multiple outlets in single request)
- Export formats (PDF, JSON, CSV)
- Operational metrics endpoint (`GET /metrics`)
- Developer documentation (812-line DEVELOPER.md)
- Platform routing in orchestrator (news/twitter with fallback)
- 169 tests total (35 new)
- **Compliance**: Export for auditing, operational metrics, comprehensive documentation
- See [docs/sprint_5_backlog.md](sprint_5_backlog.md) for details

### Sprint 6: Scale, Analytics & Event Intelligence (Mar 14-18, 2026) — COMPLETE
**Target**: v0.6.0 | **Status**: Done

- Event Intelligence Pipeline: RSS (15 feeds) + GDELT Doc API v2 collectors
- BaseCollector ABC + CollectorManager with async scheduling
- URL deduplication (SHA-256) + Title deduplication (TF-IDF cosine similarity)
- Telegram Bot API integration (wired into pipeline)
- Quality and narrative trend endpoints
- Webhook alerting (HMAC-SHA256 signing, auto-disable)
- CI compliance pipeline: secret scanning, documentation drift detection, branch policy enforcement
- Open-source hardening: CODEOWNERS, SECURITY.md, CONTRIBUTING.md, LICENSE, TROUBLESHOOTING.md
- ~197 tests total (25 new)
- **Compliance**: Major compliance sprint — secret scanning CI, docs drift detection, branch policy, SECURITY.md, CODEOWNERS
- See [docs/sprint_6_backlog.md](sprint_6_backlog.md) for details

### Sprint 7: Intelligence Layer & Compliance Hardening (Mar 14-18, 2026) — COMPLETE
**Target**: v0.7.0 | **Status**: Done

- TF-IDF event clustering pipeline (agglomerative clustering, distance_threshold=0.6)
- Z-score burst detection (24h baseline, 1h window, threshold=3.0)
- Narrative risk scoring (4-signal composite: source concentration, burst magnitude, timing sync, narrative match)
- `/events` API endpoints (list, detail, map, bursts)
- Frontend: EventClusterPanel, BurstTimeline, EventDetailDialog, enhanced GlobalMap
- Compliance practices documentation (7 documents: DSGVO, CRA, EU AI Act)
- Recursive completeness audit PASSED — 204 tests, all CI green
- **Compliance**: Full compliance documentation folder, recursive audit, vision alignment verification
- See [docs/sprint_7_backlog.md](sprint_7_backlog.md) | [retrospectives/sprint_7.md](../retrospectives/sprint_7.md)

### Sprint 8: Topic Mode & Supply Chain Security (Mar 22-28, 2026) — COMPLETE
**Target**: v0.8.0 | **Status**: Done

- Topic Mode: 5-step pipeline (baseline → discovery → per-outlet comparative analysis) with coordination signal detection, key claims/omissions extraction
- OutletNetworkGraph.tsx: Force-directed outlet relationship graph in MonitoringDashboard
- AIProvenanceCard.tsx: Tiered AI disclosure (EU AI Act Art. 50) — model ID, prompt version, quality score, legal text
- SBOM generation in CI: CycloneDX `sbom.yml` on every push to main/development, 90-day artifact retention
- Dependency vulnerability scanning: pip-audit in CI, fails on actionable HIGH/CRITICAL CVEs
- GitHub Actions pinned to commit SHAs (GhostAction supply chain mitigation)
- 10 new tests (coordination logic, key claims, API schema, ai_metadata)
- Migration fixes: startup column migrations for Sprint 8 DB schema
- Infrastructure: Cloudflare Workers (frontend + GDELT proxy), Fly.io/Koyeb exploration, keep-alive workflow
- **Compliance**: SBOM artifact (CRA Art. 13(15)), pip-audit (CRA Art. 10(4)), AI provenance (EU AI Act Art. 50)
- See [docs/sprint_8_backlog.md](sprint_8_backlog.md) | [retrospectives/sprint_8.md](../retrospectives/sprint_8.md)

### Sprint 9: AI Trust, Information Security & Compliance Automation (Mar 28, 2026) — COMPLETE
**Target**: v0.9.0 | **Status**: Done

- **AI Trust Framework**: LLM output validation (`output_validator.py`), grounding score (TF-IDF claim verification), confidence calibration
- **Information Security Hardening**: CORS fix, rate limiting (slowapi), prompt injection prevention (`input_sanitizer.py`), security headers, error sanitization, API key hygiene
- **Compliance Automation**: Machine-readable `/compliance/evidence` endpoint, custom dependency scanner (replaces Dependabot)
- **OWASP LLM Top 10**: LLM01, LLM02, LLM04, LLM06, LLM09 mitigated
- 35 new tests, 249 total
- **Compliance**: OWASP LLM Top 10 coverage, EU AI Act Art. 9/12/14, CRA security hardening
- **Versioning**: Adopted semver `0.x.y` — retagged `v2026.03` → `v0.5.0`
- See [docs/sprint_9_backlog.md](sprint_9_backlog.md) for details

### Sprint 10: User Authentication & CDDBS-Edge (Apr-May 2026)
- User authentication and authorization (JWT, role model, session management)
- CDDBS-Edge Phase 0: Swap Gemini → Ollama, benchmark briefing quality
- Analyst annotations and comments on briefings

### Sprint 11: Collaboration & Advanced Features (May-Jun 2026)
- Shared analysis workspaces (depends on Sprint 10 auth)
- Automated monitoring schedules
- API for third-party integration

### Sprints 12+: Future (Jun-Aug 2026)
- Machine learning model fine-tuning
- Multi-language support
- Currents API collector integration

---

### CDDBS-Edge: Portable Offline Briefing System (Parallel Track)

**Status**: Concept — Experiment Phase 0 in planning
**Scope**: Separate hardware prototype track, runs parallel to cloud sprints
**Design doc**: [research/cddbs_edge_concept.md](../research/cddbs_edge_concept.md)

> *"What happens when the cloud goes down, the API gets blocked, or you're a journalist in a country that restricts internet access?"*

A portable, offline-capable version of CDDBS that runs entirely on a Raspberry Pi 5 with a local quantized LLM (Phi-3 Mini 3.8B via Ollama), replacing all external API calls. Output delivered via MQTT broker to a connected display (e-ink HAT or external screen — approach TBD by experiment).

**Experiment Phases:**
- **Phase 0** (no hardware): Swap Gemini → Ollama on laptop, benchmark briefing quality vs cloud baseline
- **Phase 1**: Deploy pipeline on Raspberry Pi 5 (8GB), benchmark speed/RAM/thermal
- **Phase 2**: Wire MQTT output, prototype display options (e-ink HAT vs MQTT subscriber)
- **Phase 3**: Design offline data ingestion (USB-based article import or minimal RSS fetch)

**Why it matters for AI trust & governance:**
Demonstrates resilience, digital sovereignty, access equity, and privacy-preserving AI deployment — concrete artifacts for governance discussions that most researchers only address theoretically.

---

## Architecture

### Current Stack (as of v0.9.0)
- **Backend**: FastAPI + uvicorn + slowapi on Render (Docker)
- **Frontend**: React 18 + TypeScript + MUI 6 + Vite on Cloudflare Workers + Render
- **Database**: PostgreSQL 15 (Neon managed, 12 tables)
- **LLM**: Google Gemini 2.5 Flash via google-genai SDK
- **Data Sources**: SerpAPI Google News, Twitter API v2, GDELT Doc API v2 (Cloudflare proxy), RSS (15 feeds)
- **CI**: GitHub Actions (7 workflows)
- **Source Code**: GitHub (cddbs-prod + cddbs-research)

### Achieved Architecture (v0.6.0)
- Structured briefing output validated against JSON Schema v1.2
- 7-dimension quality scoring pipeline (70-point rubric)
- Narrative detection against 50+ known disinformation narratives
- Platform adapters for Twitter + Telegram (both wired into pipeline)
- Multi-source event intelligence pipeline (RSS + GDELT)
- URL + title deduplication (SHA-256 + TF-IDF cosine)
- Webhook alerting with HMAC-SHA256 signing
- CI compliance pipeline (secret scan, docs drift, branch policy)
- Background task processing with auto-polling frontend
- Batch analysis and export (JSON/CSV/PDF)
- Operational metrics and trend endpoints

### Achieved Architecture (v0.7.0)
- Event clustering and burst detection (TF-IDF agglomerative + z-score)
- Narrative risk scoring composite (4-signal: source_concentration, burst_magnitude, timing_sync, narrative_match)
- Events API and frontend visualization (EventClusterPanel, BurstTimeline, GlobalMap overlay)
- 204 tests, 3 CI workflows, 7 compliance documents

### Achieved Architecture (v0.8.0)
- Topic Mode: 5-step pipeline — baseline fetch, Gemini baseline, broad discovery, per-outlet comparative analysis, coordination signal detection
- OutletNetworkGraph: force-directed outlet relationship visualization
- AIProvenanceCard: tiered AI disclosure (model ID, prompt version, quality score, legal text)
- SBOM generation (CycloneDX) and pip-audit vulnerability scanning in CI
- GitHub Actions pinned to commit SHAs (supply chain hardening)
- Infrastructure: Cloudflare Workers (frontend + GDELT proxy), keep-alive workflow

### Achieved Architecture (v0.9.0)
- AI trust framework: output validation, grounding score (TF-IDF claim verification), confidence calibration
- Information security: CORS hardening, rate limiting (slowapi), input sanitization, security headers, error sanitization, API key hygiene
- Compliance automation: `/compliance/evidence` endpoint, custom dependency scanner (replaces Dependabot)
- OWASP LLM Top 10: LLM01, LLM02, LLM04, LLM06, LLM09 mitigated
- 249 tests, 7 CI workflows

### Target Architecture (v0.10.0+)
- User authentication and authorization (JWT, RBAC)
- CDDBS-Edge Phase 0 (Gemini → Ollama swap, benchmark)
- Shared analysis workspaces

---

## Key Principles

1. **Evidence over speed** - Every claim must be traceable to evidence
2. **Confidence transparency** - Always communicate uncertainty honestly
3. **Reproducibility** - Analyses should be reproducible with the same inputs
4. **Professional standards** - Output should meet intelligence community standards
5. **Cost discipline** - Stay within free/low-cost tier limits
6. **Compliance by design** - EU regulatory requirements (DSGVO, CRA, EU AI Act) addressed through engineering practices, not afterthought

---

## Branching Policy

| Repository | Branch Policy |
|-----------|---------------|
| `cddbs-prod` | Feature branches from `development` → merge to `development` → merge to `main` |
| `cddbs-research` | Feature branches from `main` → merge to `main` |

Production code flows through the `development` branch as a staging/integration area before reaching `main`. This is enforced by CI (`branch-policy.yml`).

---

## Vision Alignment Check (as of Sprint 8 Planning)

| Sprint | Contribution to Vision | On Track? |
|--------|----------------------|-----------|
| 1 | Briefing format — core intelligence output | Yes |
| 2 | Quality scoring — reliability of AI analysis | Yes |
| 3 | Multi-platform — broader disinformation coverage | Yes |
| 4 | Production integration — making research usable | Yes |
| 5 | Operational maturity — production-grade features | Yes |
| 6 | Event intelligence — proactive monitoring capability | Yes |
| 7 | Intelligence layer — automated event detection | Yes ✓ |
| 8 | Topic Mode, supply chain security, AI provenance — proactive discovery + compliance | Yes ✓ |
| 9 | AI trust, information security, compliance automation — output integrity + platform hardening | Yes ✓ |

**Drift assessment**: No significant drift from project vision. All sprints serve the core mission of "analyzing media outlets and social media accounts for potential disinformation activity."

**Sprint 9 reprioritization note**: The original plan placed user authentication in Sprint 9. The Sprint 8 security audit revealed critical gaps (prompt injection, no rate limiting, CORS misconfiguration) that must be resolved before adding auth. Additionally, for a disinformation detection system, AI output trustworthiness (grounding scores, hallucination detection) is more mission-critical than access control. Auth is now Sprint 10 — this is a deliberate sequencing decision, not scope drift. The core features (auth, workspaces, annotations, CDDBS-Edge) remain on the roadmap with unchanged priority.

**Potential drift risks**:
- CDDBS-Edge is a parallel track that could divert focus — mitigated by keeping it separate and experiment-phase only
- Collaborative features (Sprint 9) could drift toward general-purpose workspace — must stay focused on analyst collaboration for disinformation analysis
- Compliance documentation is valuable but must not become the primary focus — it supports engineering quality, not the other way around

---

## Compliance Documentation

See [compliance-practices/](../compliance-practices/README.md) for comprehensive documentation of all DSGVO, CRA, and EU AI Act measures implemented across Sprints 1-7.
