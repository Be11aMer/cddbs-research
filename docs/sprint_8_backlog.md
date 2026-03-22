# Sprint 8 Backlog — Topic Mode & Supply Chain Security

**Sprint**: 8 (Apr 15 – Apr 28, 2026)
**Target**: v1.8.0
**Status**: In Progress (Implementation Started 2026-03-22)
**Related**: [Sprint 7 Retrospective](../retrospectives/sprint_7.md) | [Execution Plan](cddbs_execution_plan.md)
**Branch Policy**: Production work branches from `development`, not `main`

---

## Sprint Goals

1. **Topic Mode** — Topic-centric comparative analysis: given a topic, discover which outlets cover it, score divergence from a neutral baseline, and rank by amplification signal
2. **NetworkGraph.tsx** — Ship the outlet relationship graph that has been carried since Sprint 5
3. **SBOM in CI** — Formal Software Bill of Materials (CycloneDX) generated on every release build
4. **Dependency Vulnerability Scanning** — pip-audit integrated into CI; blocks merge on known CVEs
5. **User-facing AI Disclosure** — Visible panel in frontend communicating AI-generated content to end users per EU AI Act Art. 50
6. **Recursive Completeness Check** — Final sprint step verifying all tasks implemented, tested, documented, and gap-free

---

## P0 — Topic Mode Backend

Architecture fully designed in `TOPIC_MODE_PLAN.md`. Implementation follows the step-by-step order defined there.

| # | Task | Effort | Owner | Acceptance Criteria |
|---|------|--------|-------|---------------------|
| 8.1 | `TopicRun` + `TopicOutletResult` ORM models | S | — | Models added to `models.py`; `init_db()` creates tables automatically; `topic_run_id` FK with cascade delete |
| 8.2 | `topic_prompt_templates.py` | S | — | `get_baseline_prompt()` → JSON `{baseline_summary, key_facts, neutral_framing}`; `get_comparative_prompt()` → JSON `{divergence_score, amplification_signal, propaganda_techniques, framing_summary, divergence_explanation}`; includes STRICT RULES block |
| 8.3 | `pipeline/topic_pipeline.py` | L | — | 5-step pipeline: (1) baseline fetch from 4 reference outlets via SerpAPI, (2) Gemini baseline call, (3) broad discovery (top-N domains by frequency), (4) per-outlet comparative analysis with incremental DB commits, (5) finalize status |
| 8.4 | `POST /topic-runs` API endpoint | S | — | Creates TopicRun, fires background task, returns `{id, status}`; validates: topic non-empty, 1 ≤ num_outlets ≤ 20 |
| 8.5 | `GET /topic-runs` API endpoint | S | — | Returns list ordered by created_at DESC; includes outlet_results count per run |
| 8.6 | `GET /topic-runs/{id}` API endpoint | S | — | Returns TopicRun + outlet_results ordered by divergence_score DESC |

---

## P0 — Topic Mode Frontend

| # | Task | Effort | Owner | Acceptance Criteria |
|---|------|--------|-------|---------------------|
| 8.7 | `api.ts` additions | S | — | `CreateTopicRunPayload`, `TopicRunStatus`, `TopicOutletResult`, `TopicRunDetail` interfaces; `createTopicRun()`, `fetchTopicRuns()`, `fetchTopicRun()` functions |
| 8.8 | `NewAnalysisDialog.tsx` mode toggle | M | — | `ToggleButtonGroup` at top ("Outlet" / "Topic"); Topic form: Topic text field + num_outlets + time period; calls correct API based on mode; `onCreated` routes to correct list |
| 8.9 | `TopicRunsTable.tsx` | M | — | Mirrors `RunsTable.tsx`; columns: Topic, Outlets Found, Status, Created, Actions; links to detail view |
| 8.10 | `TopicRunDetail.tsx` | M | — | Baseline reference box; outlet cards ranked by divergence_score; score bar (0-100), amplification chip (low=green, medium=yellow, high=red), propaganda technique chips, framing summary, article links; auto-polls while status="running" |
| 8.11 | `App.tsx` integration | M | — | `"topic-runs"` added to `ViewType`; sidebar nav item (`TravelExploreIcon`); topic runs query; routing logic; `NewAnalysisDialog` receives `onCreated` that refreshes correct list |

---

## P1 — NetworkGraph.tsx (Carried from Sprint 5→6→7)

| # | Task | Effort | Owner | Acceptance Criteria |
|---|------|--------|-------|---------------------|
| 8.12 | `NetworkGraph.tsx` production implementation | M | — | Renders outlet relationship graph from existing data; nodes = outlets, edges = shared narrative matches or cross-references; uses D3 or existing MUI charting; integrated into MonitoringDashboard or dedicated view |

---

## P1 — Supply Chain Security (CI)

| # | Task | Effort | Owner | Acceptance Criteria |
|---|------|--------|-------|---------------------|
| 8.13 | SBOM generation — `sbom.yml` CI workflow | M | — | Runs `cyclonedx-py requirements` on `requirements.txt`; uploads `sbom.json` as workflow artifact on every push to `main` and `development`; artifact retained 90 days |
| 8.14 | Dependency vulnerability scanning — pip-audit in CI | S | — | `pip-audit -r requirements.txt` runs in `ci.yml` after install; workflow fails on any known CVE with severity ≥ HIGH; exceptions documented in `vulnerability-exceptions.txt` |
| 8.15 | Add `cyclonedx-bom` and `pip-audit` to dev-dependencies | S | — | Added to `requirements.txt` under `# dev/CI tools`; versions pinned |

---

## P1 — User-Facing AI Disclosure

| # | Task | Effort | Owner | Acceptance Criteria |
|---|------|--------|-------|---------------------|
| 8.16 | `AIDisclosurePanel.tsx` | S | — | Persistent info panel (collapsible) visible to all users: states that briefings are AI-generated by Gemini, reviewed by human analyst, and may contain errors; links to methodology documentation |
| 8.17 | Wire disclosure into analysis report view | S | — | Panel appears above every briefing/report; cannot be permanently dismissed (reappears per session); fulfils EU AI Act Art. 50 transparency requirement at the UI layer |

---

## P1 — Testing

| # | Task | Effort | Owner | Acceptance Criteria |
|---|------|--------|-------|---------------------|
| 8.18 | Topic pipeline tests | M | — | ≥10 tests: baseline fetch mock, Gemini call mock, discovery domain extraction, per-outlet analysis, incremental commit, error handling (failed outlet), finalize on partial success |
| 8.19 | Topic API endpoint tests | M | — | ≥8 tests: create run, list runs, get detail, detail with outlet_results, empty state, 404, validation errors |
| 8.20 | Frontend type-check | S | — | `npm run build` passes with all new components; no TypeScript errors |

---

## P1 — Documentation

| # | Task | Effort | Owner | Acceptance Criteria |
|---|------|--------|-------|---------------------|
| 8.21 | Update DEVELOPER.md with Sprint 8 features | M | — | New sections: Topic Mode architecture, topic pipeline flow, /topic-runs API, SBOM generation, vulnerability scanning |
| 8.22 | Update CHANGELOG.md | S | — | v1.8.0 release notes with all Sprint 8 features |
| 8.23 | Update execution plan | S | — | Mark Sprint 7 complete, Sprint 8 current; update architecture section |
| 8.24 | Update compliance log | S | — | Sprint 7 compliance marked complete; Sprint 8 SBOM and disclosure measures documented |

---

## P2 — Deferred / Carried Items

| # | Task | Effort | Notes |
|---|------|--------|-------|
| 8.25 | User authentication and authorization | XL | Pushed to Sprint 9 — foundational but large; auth requires session management, JWT, role model, UI changes |
| 8.26 | Shared analysis workspaces | XL | Depends on auth; Sprint 10 |
| 8.27 | Analyst annotations on briefings | L | Depends on auth; Sprint 10 |
| 8.28 | Currents API collector | S | Low priority; RSS + GDELT coverage sufficient |

---

## FINAL STEP — Recursive Completeness Check (Task 8.29)

**This task must be executed last, after all other Sprint 8 tasks are marked done.**

### 8.29 Sprint 8 Recursive Completeness Audit

#### 8.29.1 Implementation Completeness
- [ ] Every P0 task (8.1–8.11) has corresponding code committed
- [ ] Every P1 task (8.12–8.24) has corresponding code/docs committed
- [ ] No TODO/FIXME/HACK comments left in Sprint 8 code
- [ ] All new files imported/registered where needed

#### 8.29.2 Test Coverage
- [ ] `pytest tests/ -v` passes — ≥222 total tests (≥18 new Sprint 8 tests)
- [ ] `npm run build` succeeds (frontend type-check)
- [ ] All new API endpoints return expected responses
- [ ] Edge cases tested: failed Gemini call, partial pipeline completion, zero outlets discovered

#### 8.29.3 Documentation Completeness
- [ ] DEVELOPER.md updated with all Sprint 8 features
- [ ] CHANGELOG.md has v1.8.0 entry
- [ ] SBOM artifact produced and downloadable
- [ ] Sprint 8 retrospective — deferred to sprint close
- [ ] Compliance log updated

#### 8.29.4 CI/Compliance Verification
- [ ] Lint passes (ruff check clean)
- [ ] pip-audit passes (no HIGH/CRITICAL CVEs unexcepted)
- [ ] SBOM workflow runs and uploads artifact
- [ ] No secrets in committed code
- [ ] Branch policy: PR targets development branch

#### 8.29.5 Vision Alignment Check (Sprints 1-8)
- [ ] Topic Mode serves core mission: comparative outlet analysis for disinformation detection ✓
- [ ] SBOM/vulnerability scanning supports CRA compliance ✓
- [ ] AI disclosure serves EU AI Act Art. 50 ✓
- [ ] Auth deferral is deliberate — not drift
- [ ] No feature creep away from counter-disinformation mission

#### 8.29.6 Gap Identification
- [ ] Document any gaps found
- [ ] Confirm Sprint 9 candidates: user auth, shared workspaces
- [ ] Confirm CDDBS-Edge Phase 0 readiness

---

## Acceptance Criteria (Sprint-Level)

### Topic Mode
- [ ] Analyst can enter a topic ("NATO expansion eastward"), select 5 outlets, and receive ranked divergence scores within 90 seconds
- [ ] Discovery correctly excludes reference outlets (reuters.com, bbc.com, apnews.com, afp.com)
- [ ] Partial results visible in UI before pipeline completes (incremental commits)
- [ ] Each outlet result shows: divergence score (0-100), amplification signal (low/medium/high), propaganda techniques, framing summary, article links

### Supply Chain Security
- [ ] `sbom.json` artifact downloadable from every CI run on main/development
- [ ] CI fails on merge if `pip-audit` finds HIGH or CRITICAL CVEs without documented exception

### UI Compliance
- [ ] AI disclosure panel visible on every briefing view without user opt-in
- [ ] Panel text explicitly names Gemini as the AI model and instructs analyst review

### Quality
- [ ] ≥18 new tests (≥222 total passing)
- [ ] All CI workflows green
- [ ] No documentation drift

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Gemini API latency for 5+ outlet pipeline (10+ calls) | Per-outlet incremental commits + UI auto-poll; user sees progress; pipeline doesn't block |
| SerpAPI rate limits during broad discovery (40-result query) | Single broad query per topic run; per-outlet queries = num_outlets; well within free tier |
| pip-audit false positives blocking CI | `vulnerability-exceptions.txt` allows documented, reviewed exceptions; review process in CONTRIBUTING.md |
| SBOM size / CI artifact bloat | CycloneDX JSON for ~30 deps is ~50KB; 90-day retention; no issue |
| NetworkGraph.tsx scope creep | Scope to existing data (outlet narrative matches); no new backend endpoints required |

---

## Tech Stack (Minimal New Dependencies)

| Package | Purpose | Tier |
|---------|---------|------|
| `cyclonedx-bom` | SBOM generation | Dev/CI only |
| `pip-audit` | Vulnerability scanning | Dev/CI only |

No new runtime dependencies. Topic Mode uses existing SerpAPI + google-genai SDK + SQLAlchemy.

---

## Definition of Done

- All P0 and P1 tasks completed and tested
- Recursive completeness check (8.29) executed and all items checked
- CI green on all workflows (ci.yml, branch-policy.yml, secret-scan.yml, sbom.yml)
- DEVELOPER.md and CHANGELOG.md updated
- Sprint 8 retrospective written
- Compliance log updated
- No regression in Sprint 1-7 functionality
- Production patch exported to `patches/sprint8_production_changes.patch`
