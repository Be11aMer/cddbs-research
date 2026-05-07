# Sprint 9 Retrospective

**Sprint**: 9 — AI Trust, Information Security & Compliance Automation
**Duration**: March 28 – April 1, 2026
**Version**: v0.9.0
**Status**: Complete

---

## Sprint Goal

Close the security gaps identified in the Sprint 8 audit (CORS, rate limiting, prompt injection, SSRF), implement an AI trust framework (output validation, grounding score), and automate compliance evidence collection.

---

## Delivery Summary

### AI Trust Framework (P0)

| Task | Status | Notes |
|------|--------|-------|
| 9.1.1 `pipeline/output_validator.py` — structural validation | Done | Validates Gemini JSON responses against expected schema before DB commit; catches missing fields, wrong types, out-of-range values; returns ValidationResult with errors list |
| 9.1.2 Hallucination heuristic: grounding score | Done | TF-IDF cosine similarity between LLM claims and source article text; claims with max similarity < 0.3 flagged "ungrounded"; `grounding_score` (0.0–1.0) per outlet result; per-claim detail with similarity scores |
| 9.1.3 Confidence calibration metrics / `GET /metrics/calibration` | Deferred to Sprint 10 | Requires historical feedback data to be meaningful; endpoint scaffolding added but logic not implemented |
| 9.1.4 Output reproducibility check / `reproducibility_score` | Deferred to Sprint 10 | Requires double-call mechanism; deferred to avoid doubling Gemini costs on every topic run |
| 9.2.1 `TrustIndicator.tsx` frontend component | Deferred to Sprint 10 | Backend grounding_score exists; UI surface deferred to keep Sprint 9 focused on backend hardening |
| 9.2.2 Ungrounded claim highlighting in TopicRunDetail | Deferred to Sprint 10 | Depends on 9.2.1 |
| 9.2.3 Wire TrustIndicator into TopicRunDetail | Deferred to Sprint 10 | Depends on 9.2.1 |

### Information Security Hardening (P0)

| Task | Status | Notes |
|------|--------|-------|
| 9.3.1 CORS hardening | Done | `allow_origins` changed from wildcard to explicit list (`cddbs.pages.dev`, `cddbs.onrender.com`, `localhost:5173`); `allow_credentials=False`; `allow_headers` restricted to `Content-Type` |
| 9.4.1 slowapi rate limiting | Done | 5/min on POST /analysis-runs, 3/min on POST /topic-runs, 5/min on POST /social-media/analyze |
| 9.4.2 Rate limit response handler | Done | HTTP 429 with `Retry-After` header; JSON body `{"detail": "Rate limit exceeded"}` |
| 9.5.1 `utils/input_sanitizer.py` | Done | Strips control characters, zero-width chars, RTL overrides; escapes prompt delimiters (`"""`, `` ``` ``, `---`); filters injection keywords (`IGNORE PREVIOUS INSTRUCTIONS`); per-field max lengths |
| 9.5.2 Wire sanitizer into all prompt templates | Done | Applied to all user-supplied fields in `prompt_templates.py` and `topic_prompt_templates.py` before LLM interpolation |
| 9.5.3 External data sanitization (SerpAPI/GDELT) | Done | SerpAPI titles/snippets and GDELT content truncated and stripped before prompt insertion |
| 9.6.1 Enum validation for constrained fields | Done | `date_filter`, `platform` fields use `Literal` types; Pydantic validates automatically |
| 9.6.2 Webhook URL validation + SSRF prevention | Done | URL format validation; private IP ranges blocked (10.x, 172.16-31.x, 192.168.x, 127.x, 169.254.x); non-HTTP(S) schemes rejected |
| 9.6.3 Outlet name regex validation | Deferred to Sprint 10 | Low-priority gap; existing sanitizer provides adequate coverage |
| 9.7.1 Security headers middleware | Done | `api/security_headers.py` adds X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy, CSP, Cache-Control: no-store |
| 9.8.1 Error response sanitization | Done | Global exception handler returns generic messages; no DB schema, stack traces, or file paths exposed to clients |
| 9.9.1 Remove API keys from request schemas | Done | `serpapi_key` and `google_api_key` removed from all request models; server-side env vars only |
| 9.9.2 API key presence validation at startup | Done | App refuses to start if `GOOGLE_API_KEY` or `SERPAPI_KEY` unset; clear error message pointing to DEVELOPER.md |

### Compliance Automation (P1)

| Task | Status | Notes |
|------|--------|-------|
| 9.10.1 `compliance-report.yml` CI workflow | Superseded | `dependency-scan.yml` was built instead — broader scope: scans Python (pip-audit) + Node.js (npm audit), schedules Mon/Thu, creates GitHub issues for fixable CVEs. Subsumes the compliance artifact intent; dedicated compliance-report.yml moved to Sprint 10 |
| 9.10.2 `GET /compliance/evidence` endpoint | Done | Returns machine-readable JSON: AI model config, security controls inventory, EU AI Act / CRA / DSGVO measure mapping, system statistics |
| 9.10.3 Data retention enforcement / `GET /compliance/retention` | Deferred to Sprint 10 | No retained data at risk yet (pre-1.0); deferred until data accumulates |
| 9.11.1 Update EU AI Act compliance doc | Done | Sprint 9 AI trust measures mapped to Art. 9/12/14 in `compliance-practices/sprint_compliance_log.md` |
| 9.11.2 Update CRA compliance doc | Done | Security hardening measures logged in compliance log |
| 9.11.3 `information_security.md` compliance doc | Deferred to Sprint 10 | OWASP LLM Top 10 mapping documented in DEVELOPER.md Section 16.5; standalone doc deferred |

### Testing (P1)

| Task | Status | Notes |
|------|--------|-------|
| 9.12 Output validator tests | Done | 10 tests covering structural validation, missing fields, out-of-range values, grounding score computation |
| 9.13 Input sanitizer tests | Done | 17 tests covering injection patterns, control character stripping, HTML entity escaping, max length enforcement |
| 9.14 Security hardening tests | Done | 8 tests: CORS config (1), security headers (1), rate limit handler (1), webhook SSRF (2), error sanitization (2), API key hygiene (1) |
| 9.15 Compliance endpoint tests | Partial | `GET /compliance/evidence` covered; retention endpoint not implemented |
| 9.16 Frontend type-check | Done | `npm run build` passes |

### Documentation (P1)

| Task | Status | Notes |
|------|--------|-------|
| 9.17 DEVELOPER.md — Sprint 9 section | Done | Section 16: security hardening, AI trust framework, compliance automation, new files table, OWASP Top 10 coverage |
| 9.18 CHANGELOG.md | Done | v0.9.0 entry with all Sprint 9 features + post-sprint amendments |
| 9.19 Execution plan update | Done | Sprint 9 marked complete; Sprint 9 architecture block updated; Sprint 10 direction noted |
| 9.20 Compliance log update | Done | Sprint 9 compliance measures table added |

### Deferred Items (P2)

| Task | Status | Notes |
|------|--------|-------|
| 9.21 User authentication (JWT + RBAC) | Deferred to Sprint 10 | Core Sprint 10 feature |
| 9.22 Shared analysis workspaces | Deferred to Sprint 11 | Depends on auth |
| 9.23 Analyst annotations | Deferred to Sprint 11 | Depends on auth |
| 9.24 CDDBS-Edge Phase 0 | Deferred to Sprint 10 | Focus on trust/security first |
| 9.25 Backend migration from Render | Ongoing | Keep-alive workflow interim; migration research continues |

---

## Innovations Beyond Backlog

Sprint 9 delivered six major features beyond the original backlog — the intelligence feed extensions that were blocking from earlier sprints and required accumulated architecture to be implemented cleanly.

### 1. Automated Situational Reports (SitRep) with Cross-Source Framing Analysis

`pipeline/sitrep.py` — `generate_sitrep()` + `run_sitrep_cycle()`

Generates AI Situational Reports for high-risk EventClusters automatically. The prompt deliberately reuses the same Gemini call to embed cross-source framing analysis at zero extra API cost when a cluster has ≥3 distinct sources or ≥2 source types.

- Framing analysis captures: per-source framing summary, key claims, omitted facts, emotional language score, bias direction, discrepancies across sources, coordination indicators, framing divergence score
- Gate conditions: `narrative_risk_score ≥ CDDBS_SITREP_MIN_RISK_SCORE` (0.5) AND `article_count ≥ CDDBS_SITREP_MIN_ARTICLES` (5)
- Deduplication: already-briefed clusters are skipped
- Budget cap: `CDDBS_SITREP_MAX_PER_CYCLE` (default 3) Gemini calls per cycle

### 2. Threat Digest — Daily and Quarterly Reports

`pipeline/threat_digest.py` — `generate_daily_digest()` + `generate_quarterly_report()`

Daily digests summarize recent SitReps into an executive-grade threat summary at low token cost. Quarterly reports aggregate the full period and are UI-triggered only (not scheduled) to prevent accidental high-cost runs.

### 3. CddbsScheduler — Unified 4-Job Orchestrator

`scheduler.py` — `CddbsScheduler`

The single authoritative place for all automated background tasks. Starts inside the FastAPI lifespan. Status exposed at `GET /scheduler/status`.

| Job | Env var | Default | Cost |
|-----|---------|---------|------|
| Collector | `CDDBS_COLLECTOR_INTERVAL_HOURS` | 1h | Zero (RSS/GDELT fetch) |
| SitRep | `CDDBS_SITREP_INTERVAL_HOURS` | 12h | Gemini API (gated) |
| Threat Digest | `CDDBS_THREAT_DIGEST_INTERVAL_HOURS` | 24h | Gemini API (low-cost) |
| Source Credibility | `CDDBS_SOURCE_CREDIBILITY_INTERVAL_HOURS` | 24h | Zero (local computation) |

### 4. Source Credibility Index (Phase 4A)

`pipeline/source_credibility.py` — `compute_all_source_credibility(session) -> int`

Per-domain reliability scoring entirely from existing DB data — zero Gemini API cost.

Reliability formula: `1 - (0.40×propaganda + 0.30×framing_divergence + 0.20×coord_norm + 0.10×burst_norm)`

- `propaganda` — `narrative_risk_score` as proxy (no per-article field exists yet)
- `framing_divergence` — how often the source diverges from consensus across SitReps
- `coord_norm` — inferred from `framing_analysis.source_framings` when `coordination_indicators` non-empty
- `burst_norm` — normalized burst participation count

Stores trend direction: `improving` / `stable` / `degrading` based on delta from previous computation.

API: `GET /stats/source-credibility`, `POST /stats/source-credibility/refresh`
Frontend: `SourceCredibilityPanel.tsx`

### 5. GDELT Collector Fix

`collectors/gdelt.py`

Fixed GDELT returning HTML error pages instead of JSON (GDELT's behavior on rate-limited or temporarily unavailable endpoints). The collector now detects non-JSON responses and handles them gracefully. Also wired up `GDELT_PROXY_URL` routing: when set, all GDELT requests go through the Cloudflare Workers proxy (already deployed for the frontend), avoiding direct API exposure and rate-limit issues.

### 6. New Frontend Components

| Component | Purpose |
|-----------|---------|
| `ThreatBriefingsPanel.tsx` | Lists automated SitReps, daily digests, quarterly reports |
| `ThreatBriefingDetail.tsx` | Full SitRep view including framing analysis and source divergence |
| `SourceCredibilityPanel.tsx` | Domain reliability rankings with trend indicators |
| `IntelFeed.tsx` | Real-time article feed from background collectors |
| `CollectorStatusBar.tsx` | Live collector health indicators (RSS + GDELT status) |
| `AnnotatedArticleCards.tsx` | Per-article analysis cards with propaganda scores |

---

## Test Coverage

| Metric | Sprint 8 | Sprint 9 | Delta |
|--------|----------|----------|-------|
| Total tests | 214 | 249 | +35 |
| New test file | — | `test_sprint9_security.py` | |
| Coverage areas | — | Input sanitizer (17), output validator (10), grounding score (6), CORS (1), security headers (1) | |

Beyond-backlog deliverables (SitRep, Threat Digest, Source Credibility) are integration-heavy and tested via the existing pipeline test infrastructure rather than standalone unit tests. Dedicated tests for these modules are a Sprint 10 backlog candidate.

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
| dependency-scan.yml (new — replaces Dependabot) | Green |

---

## Compliance Checklist (Task 9.26)

### 9.26.1 Implementation Completeness
- [x] All P0 security tasks (9.3–9.9) implemented
- [x] Output validation and grounding score (9.1.1–9.1.2) implemented
- [x] Compliance evidence endpoint (9.10.2) implemented
- [x] All new files imported and registered
- [ ] TrustIndicator.tsx (9.2.x) — deferred to Sprint 10
- [ ] Calibration and reproducibility endpoints (9.1.3, 9.1.4) — deferred to Sprint 10
- [ ] Data retention enforcement (9.10.3) — deferred to Sprint 10

### 9.26.2 Test Coverage
- [x] 249 tests passing
- [x] 35 new Sprint 9 tests (input sanitizer, output validator, grounding score, CORS, security headers)
- [x] `npm run build` passes
- [x] Security tests verify: CORS hardening, rate limiting, prompt injection neutralization, SSRF blocking

### 9.26.3 Documentation Completeness
- [x] DEVELOPER.md Section 16 with all Sprint 9 features
- [x] CHANGELOG.md v0.9.0 entry
- [x] DEVELOPER.md Section 17 — Intelligence Feed Extensions (Phase 4A, SitRep, Digest, Scheduler)
- [x] Compliance log Sprint 9 entry
- [x] Sprint 9 retrospective (this document)
- [ ] `information_security.md` standalone compliance doc — deferred to Sprint 10

### 9.26.4 CI/Compliance Verification
- [x] Lint passes (ruff check clean)
- [x] pip-audit passes (no actionable CVEs)
- [x] SBOM workflow runs and uploads artifact
- [x] dependency-scan.yml operational (replaces compliance-report.yml intent)
- [x] No secrets in committed code

### 9.26.5 Vision Alignment
- [x] AI trust framework directly serves the mission: analysts need to trust AI-generated disinformation assessments
- [x] Security hardening protects the platform and prevents adversarial manipulation of the analysis pipeline
- [x] SitRep generation maximises intel value from accumulated event data — direct mission deliverable
- [x] Source Credibility Index creates a living signal for domain reliability — core intelligence capability
- [x] No feature creep: all beyond-backlog work is intelligence pipeline, not general-purpose tooling

### 9.26.6 Gap Identification (Sprint 10 Candidates from Sprint 9)
- TrustIndicator.tsx — frontend surface for grounding score (already in backend)
- Confidence calibration metrics / `GET /metrics/calibration`
- Output reproducibility check / `reproducibility_score` on TopicRun
- `compliance-report.yml` CI artifact (dedicated; dependency-scan.yml broader but distinct)
- Data retention enforcement / `GET /compliance/retention`
- `information_security.md` standalone compliance document
- Tests for SitRep, Threat Digest, Source Credibility pipeline modules

---

## Key Learnings

1. **Security hardening before auth was the right call**: The CORS wildcard + no rate limiting combination was a genuine risk for a system that calls Gemini on every request. Closing those gaps first means Sprint 10's auth implementation lands on a hardened foundation.

2. **Grounding score is the most useful trust signal**: Of the AI trust framework components, the grounding score (TF-IDF claim-source matching) is the most immediately actionable for analysts. Calibration and reproducibility are useful long-term but require data accumulation — sequencing them after grounding was correct.

3. **The SitRep-framing analysis piggyback is a design win**: Embedding framing analysis in the same Gemini call as the SitRep (zero extra cost) rather than a separate call was the right architectural choice. It means framing analysis will accumulate naturally as clusters grow, without requiring a separate scheduling decision.

4. **Phase 4A proves the data flywheel**: Source Credibility Index requires only data already produced by Phases 1–3. This proves the data flywheel works — each phase makes the next one richer at no additional API cost. Phase 4B (network graph enhancement) and 4C (ML predictions) will follow the same pattern once data accumulates.

5. **GDELT reliability needs ongoing attention**: The HTML-error-page issue is a recurring GDELT behavior pattern, not a one-time fix. The Cloudflare proxy routing provides a more stable path, but GDELT's availability should be treated as best-effort, not guaranteed.

6. **Dependency-scan.yml is better than compliance-report.yml would have been**: The custom dependency scanner creates GitHub issues with severity tables — actionable output. A static compliance artifact JSON would have been less useful. Keeping the original intent (evidence of CI compliance) while shipping a more useful form of it is good pragmatic engineering.

---

## Sprint 10 Direction

Sprint 10 has two primary tracks plus carried-over Sprint 9 items:

**Track A — User Authentication (core Sprint 10)**
- JWT-based authentication (no third-party auth provider — keep it simple, stay DSGVO-clean)
- Role model: analyst (read + run analyses) / admin (full access)
- Login UI, protected routes, session management

**Track B — CDDBS-Edge Phase 0**
- Swap Gemini → Ollama on laptop (no hardware yet)
- Benchmark briefing quality vs Gemini baseline (7-section completeness, quality score ≥45/70)
- Go/No-Go decision for Phase 1 (Raspberry Pi deployment)

**Carried over from Sprint 9**
- TrustIndicator.tsx + calibration endpoint + reproducibility score
- `information_security.md` compliance document
- Data retention enforcement
- Tests for SitRep / Threat Digest / Source Credibility modules
