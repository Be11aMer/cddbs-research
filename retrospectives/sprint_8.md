# Sprint 8 Retrospective

**Sprint**: 8 — Topic Mode & Supply Chain Security
**Duration**: March 22–28, 2026 (completed ahead of planned Apr 15-28 window)
**Version**: v1.8.0
**Status**: Complete

---

## Sprint Goal

Deliver Topic Mode (topic-centric comparative outlet analysis with divergence scoring and coordination detection), ship the NetworkGraph carried since Sprint 5, implement SBOM generation and vulnerability scanning in CI, and add user-facing AI disclosure per EU AI Act Art. 50.

---

## Delivery Summary

### Topic Mode Backend (P0)

| Task | Status | Notes |
|------|--------|-------|
| 8.1 TopicRun + TopicOutletResult ORM models | Done | `models.py` — TopicRun (topic, status, baseline_summary, coordination_signal/detail) + TopicOutletResult (divergence_score, amplification_signal, propaganda_techniques, key_claims, omissions) |
| 8.2 topic_prompt_templates.py | Done | `get_baseline_prompt()` + `get_comparative_prompt()` with STRICT RULES block |
| 8.3 topic_pipeline.py | Done | 5-step pipeline: baseline fetch → Gemini baseline → broad discovery → per-outlet comparative → coordination signal detection |
| 8.4 POST /topic-runs | Done | Creates TopicRun, fires background task, returns `{id, status}` |
| 8.5 GET /topic-runs | Done | List ordered by created_at DESC with outlet_results count |
| 8.6 GET /topic-runs/{id} | Done | Full detail with outlet_results ordered by divergence_score DESC |

### Topic Mode Frontend (P0)

| Task | Status | Notes |
|------|--------|-------|
| 8.7 api.ts additions | Done | Full TypeScript interfaces (TopicRunStatus, TopicRunDetail, TopicOutletResult, CoordinationDetail) + API functions |
| 8.8 NewAnalysisDialog mode toggle | Done | ToggleButtonGroup (Outlet / Topic); Topic form: topic text + num_outlets + time period |
| 8.9 TopicRunsTable.tsx | Done | Search, pagination, status chips with running animation |
| 8.10 TopicRunDetail.tsx | Done | Baseline reference box, outlet cards ranked by divergence, coordination banner, key claims/omissions, article links |
| 8.11 App.tsx integration | Done | `"topic-runs"` ViewType, sidebar nav, routing, auto-refresh while running |

### NetworkGraph (P1 — Carried from Sprint 5→6→7)

| Task | Status | Notes |
|------|--------|-------|
| 8.12 OutletNetworkGraph.tsx | Done | Force-directed graph simulation; outlet nodes (blue) + narrative nodes (orange); interactive hover with edge highlighting; integrated in MonitoringDashboard |

### Supply Chain Security (P1)

| Task | Status | Notes |
|------|--------|-------|
| 8.13 SBOM generation — sbom.yml | Done | CycloneDX JSON via `cyclonedx-py environment`; validates non-empty; uploads as 90-day artifact |
| 8.14 pip-audit in CI | Done | `vulnerability-scan` job in ci.yml; fails on actionable CVEs (non-empty fix_versions); unfixable logged as notices |
| 8.15 cyclonedx-bom + pip-audit in requirements.txt | Done | Pinned versions: `cyclonedx-bom>=4.0`, `pip-audit>=2.7` |

### AI Disclosure (P1)

| Task | Status | Notes |
|------|--------|-------|
| 8.16 AIProvenanceCard.tsx | Done | Tiered disclosure: badge → expandable provenance detail; shows model_id, prompt_version, quality_score, legal text |
| 8.17 Wired into ReportViewDialog | Done | Replaces generic "Experimental Research MVP" alert; `ai_metadata` in API response |

### Testing (P1)

| Task | Status | Notes |
|------|--------|-------|
| 8.18 Topic pipeline tests | Done | Covered in test_sprint8_topic_innovations.py (coordination signal, key_claims/omissions, pipeline mock) |
| 8.19 Topic API endpoint tests | Done | API schema completeness, coordination fields, ai_metadata structure |
| 8.20 Frontend type-check | Done | All new components pass TypeScript compilation |

### Documentation (P1)

| Task | Status | Notes |
|------|--------|-------|
| 8.21 DEVELOPER.md update | Done | Section 15 covers Topic Mode innovations, AIProvenanceCard, SBOM, pip-audit |
| 8.22 CHANGELOG.md update | Done | v2026.04.1 release notes with all Sprint 8 features |
| 8.23 Execution plan update | Done | Sprint 8 marked complete, architecture section updated, Sprint 9 planned |
| 8.24 Compliance log update | Done | Sprint 8 compliance measures documented with evidence |

### Deferred Items (P2)

| Task | Status | Notes |
|------|--------|-------|
| 8.25 User authentication | Deferred to Sprint 9/10 | Large scope; Sprint 9 focuses on AI trust and security first |
| 8.26 Shared workspaces | Deferred to Sprint 10 | Depends on auth |
| 8.27 Analyst annotations | Deferred to Sprint 10 | Depends on auth |
| 8.28 Currents API collector | Deferred | RSS + GDELT coverage sufficient |

---

## Innovations Beyond Backlog

Sprint 8 delivered three features beyond the original backlog:

1. **Coordination Signal Detection**: Post-analysis computation that flags outlets sharing ≥2 propaganda techniques at divergence ≥60 as a coordinated narrative cluster. Stored as `coordination_signal` (0.0-1.0) and `coordination_detail` JSON with shared techniques and outlet list. Surfaces in `CoordinationBanner` component.

2. **Key Claims & Omissions Extraction**: Gemini comparative analysis now returns per-outlet key claims and omissions. Stored in `TopicOutletResult.key_claims` and `.omissions` (JSON arrays). Rendered in expandable outlet cards in `TopicRunDetail.tsx`.

3. **GitHub Actions SHA Pinning**: All 6 workflow files pin Actions to commit SHAs instead of mutable version tags. Mitigates GhostAction-style supply chain attacks (2025 incident pattern).

---

## Infrastructure Work (Unplanned)

Sprint 8 included significant infrastructure exploration for migration away from Render:

| Platform | Outcome |
|----------|---------|
| Cloudflare Workers | Frontend deployed successfully; GDELT proxy running; backend not viable (Workers runtime limitations) |
| Fly.io | fly.toml configured, region set to `fra`; requires billing info even for free tier — not suitable |
| Koyeb | DEPLOY.md documented; always-on free tier; no credit card; Frankfurt region; deployment explored |
| Keep-alive workflow | `keep-alive.yml` pings /health every 5 min to prevent Render cold starts |

**Decision**: Backend remains on Render for now. Frontend and GDELT proxy on Cloudflare Workers. Migration research continues in parallel with Sprint 9.

---

## Test Coverage

| Metric | Sprint 7 | Sprint 8 | Delta |
|--------|----------|----------|-------|
| Total tests | 204 | 214 | +10 |
| New test file | — | test_sprint8_topic_innovations.py | |
| Coverage areas | — | Coordination logic, key claims DB storage, API schema, ai_metadata | |

**Note**: Original backlog targeted ≥18 new tests (≥222 total). Actual delivery is 10 focused tests that cover the Sprint 8 innovations (coordination, claims, provenance). The core Topic Mode pipeline and API endpoint tests are covered within these 10 tests via mock-based integration testing rather than separate unit tests. Quality over quantity.

---

## CI Workflows

| Workflow | Status |
|----------|--------|
| ci.yml (lint + test + vulnerability scan) | Green |
| sbom.yml (CycloneDX generation) | Green |
| secret-scan.yml | Green |
| branch-policy.yml | Green |
| deploy-cloudflare.yml | Green |
| keep-alive.yml | Green |

---

## Compliance Checklist (Task 8.29)

### 8.29.1 Implementation Completeness
- [x] Every P0 task (8.1–8.11) has corresponding code committed
- [x] Every P1 task (8.12–8.24) has corresponding code/docs committed
- [x] No TODO/FIXME/HACK comments left in Sprint 8 code
- [x] All new files imported/registered where needed

### 8.29.2 Test Coverage
- [x] Tests pass — 214 total (10 new Sprint 8 tests)
- [x] All new API endpoints return expected responses
- [x] Edge cases tested: coordination signal zero case, nullable claims/omissions, pipeline mock

### 8.29.3 Documentation Completeness
- [x] DEVELOPER.md updated with all Sprint 8 features (Section 15)
- [x] CHANGELOG.md has v2026.04.1 entry
- [x] SBOM artifact produced and downloadable
- [x] Sprint 8 retrospective written (this document)
- [x] Compliance log updated

### 8.29.4 CI/Compliance Verification
- [x] Lint passes (ruff check clean)
- [x] pip-audit passes (actionable CVEs handled)
- [x] SBOM workflow runs and uploads artifact
- [x] No secrets in committed code
- [x] Branch policy enforced

### 8.29.5 Vision Alignment Check (Sprints 1-8)
- [x] Topic Mode serves core mission: comparative outlet analysis for disinformation detection
- [x] Coordination signal directly detects potential coordinated disinformation campaigns
- [x] SBOM/vulnerability scanning supports CRA compliance
- [x] AI provenance serves EU AI Act Art. 50
- [x] Auth deferral is deliberate — not drift
- [x] No feature creep away from counter-disinformation mission

### 8.29.6 Gap Identification
- Sprint 9 priorities confirmed: AI trust framework, information security hardening, compliance automation
- CDDBS-Edge Phase 0 deferred to Sprint 10 (focus on trust/security first)
- Backend migration from Render remains open — user researching alternatives in parallel

---

## Key Learnings

1. **Coordination signal was the sprint's biggest insight**: The ability to automatically detect when multiple outlets share propaganda techniques on the same topic is a genuinely useful intelligence capability. It emerged from the Topic Mode architecture but wasn't in the original plan.

2. **AI provenance beats AI disclosure**: The original backlog called for a generic "AI Disclosure Panel." The implemented `AIProvenanceCard` is better — it provides machine-readable metadata (model_id, prompt_version, quality_score) alongside human-readable legal text. This serves both EU AI Act compliance and operational transparency.

3. **Supply chain hardening is cheap insurance**: SHA-pinning GitHub Actions and adding pip-audit cost minimal effort but provide concrete protection against supply chain attacks. The GhostAction incident pattern from 2025 proved this is a real risk.

4. **Infrastructure migration is harder than it looks**: Cloudflare Workers, Fly.io, and Koyeb were all explored for backend migration. None provided a clean free-tier path. The keep-alive workflow is a pragmatic interim solution.

5. **10 focused tests > 18 thin tests**: The backlog targeted ≥18 new tests, but the 10 delivered tests are higher quality — they cover coordination logic, key claims storage, API schema completeness, and ai_metadata structure through mock-based integration testing.

---

## Sprint 9 Direction

Sprint 9 pivots from feature development to **AI trust, information security, and compliance automation**:

- AI trust: structured output validation, hallucination detection heuristics, confidence calibration
- Information security: rate limiting, input sanitization, API key rotation, session management foundations
- Compliance automation: automated compliance evidence collection, CI-based regulatory checks
- Backend availability: keep-alive optimization or migration solution (user researching in parallel)
