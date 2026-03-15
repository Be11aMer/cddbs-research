# CDDBS Sprint 5 Backlog

**Sprint**: 5 — Operational Maturity & Data Ingestion
**Duration**: March 3-16, 2026
**Version Target**: v1.5.0
**Predecessor**: Sprint 4 (v1.4.0 — Production Integration)

---

## Sprint Goal

Make CDDBS operationally mature: wire live data ingestion via Twitter API v2, support batch analysis of multiple outlets, add export capabilities (PDF/JSON/CSV), implement end-to-end integration tests, and add monitoring/alerting for production reliability.

## Success Criteria

- Twitter API v2 adapter is wired into the pipeline for direct account analysis
- Batch analysis endpoint accepts multiple outlets in a single request
- Export endpoint generates PDF, JSON, and CSV reports
- End-to-end integration test runs against real Gemini API with fixture validation
- Analysis failure monitoring with configurable alerting
- All existing tests pass (56+) plus new integration and export tests
- Network graph data visualized in frontend (basic force-directed graph)

---

## Task Breakdown

### 5.1 — Wire Twitter API v2 Adapter into Pipeline
**Priority**: P0-critical
**Labels**: backend, integration
**Estimate**: 6 hours

Connect the existing `TwitterAdapter` (from `adapters.py`) to the live pipeline so CDDBS can analyze Twitter/X accounts directly, not just via SerpAPI news.

**Subtasks**:
- [ ] Add Twitter API v2 client to `src/cddbs/pipeline/` (OAuth 2.0 bearer token)
- [ ] Implement `fetch_tweets(handle, count, bearer_token)` in a new `twitter_client.py`
- [ ] Wire `TwitterAdapter.normalize()` output into `run_pipeline()` as an alternative data source
- [ ] Add `platform` field to `RunCreateRequest` (`"news"` default, `"twitter"` optional)
- [ ] Route pipeline based on platform: news → SerpAPI fetch, twitter → Twitter API fetch
- [ ] Add `TWITTER_BEARER_TOKEN` to config.py (optional, graceful skip if missing)
- [ ] Handle rate limiting with exponential backoff (respect 429 + `x-rate-limit-reset`)
- [ ] Store `platform` on Report and Briefing records

**Acceptance Criteria**:
- [ ] `POST /analysis-runs` with `platform: "twitter"` fetches tweets via API v2
- [ ] TwitterAdapter normalizes tweet data into BriefingInput format
- [ ] Rate limits handled without crashing pipeline
- [ ] Falls back to "API key not configured" error if no bearer token

**Deliverables**: `src/cddbs/pipeline/twitter_client.py`, updated `orchestrator.py`, updated `config.py`

---

### 5.2 — Batch Analysis Support
**Priority**: P0-critical
**Labels**: backend, frontend
**Estimate**: 5 hours

Allow analysts to submit multiple outlets/accounts for analysis in a single request, producing a batch of linked reports.

**Subtasks**:
- [ ] Design batch request schema: `POST /analysis-runs/batch` accepting `targets[]`
- [ ] Add `Batch` model to `models.py` (id, name, status, created_at, report_ids JSON)
- [ ] Implement batch orchestration: queue each target as a separate pipeline job
- [ ] Add `GET /analysis-runs/batch/{batch_id}` to check batch status
- [ ] Add batch progress tracking (X/N completed)
- [ ] Frontend: BatchAnalysisDialog with multi-outlet input (add/remove rows)
- [ ] Frontend: Batch status card in dashboard showing completion progress

**Acceptance Criteria**:
- [ ] Batch of 3 outlets queued and executed independently
- [ ] Batch status endpoint returns per-target status
- [ ] Frontend displays batch progress
- [ ] Individual reports still accessible via existing endpoints

**Deliverables**: Updated `models.py`, `api/main.py`, new `BatchAnalysisDialog.tsx`

---

### 5.3 — Export Formats (PDF, JSON, CSV)
**Priority**: P1-high
**Labels**: backend, frontend
**Estimate**: 5 hours

Generate downloadable reports in multiple formats for offline sharing and integration with analyst workflows.

**Subtasks**:
- [ ] Add `GET /analysis-runs/{id}/export?format=json` endpoint
- [ ] JSON export: structured briefing JSON + quality scorecard + narrative matches
- [ ] CSV export: flatten key findings, articles, narrative matches into tabular format
- [ ] PDF export: formatted intelligence briefing using reportlab or weasyprint
- [ ] Add `reportlab` (or `weasyprint`) to `requirements.txt`
- [ ] Frontend: Export button dropdown in ReportViewDialog (PDF / JSON / CSV)
- [ ] Frontend: Handle file download via blob URL

**Acceptance Criteria**:
- [ ] JSON export contains complete briefing data
- [ ] CSV export is importable into Excel/Google Sheets
- [ ] PDF export is formatted with CDDBS branding and section headers
- [ ] Export buttons visible in report view

**Deliverables**: New `src/cddbs/export.py`, updated `api/main.py`, updated `ReportViewDialog.tsx`

---

### 5.4 — End-to-End Integration Tests
**Priority**: P0-critical
**Labels**: testing
**Estimate**: 4 hours

Create integration tests that exercise the full pipeline (fetch → Gemini → parse → score → match) with real API responses validated against expected structure.

**Subtasks**:
- [ ] Create `tests/test_integration.py` with pytest markers (`@pytest.mark.integration`)
- [ ] Test: full pipeline with mocked SerpAPI + real Gemini → validate output schema
- [ ] Test: quality scorer produces valid scores on live Gemini output
- [ ] Test: narrative matcher runs on live output without errors
- [ ] Test: API endpoint returns complete response with quality + narrative data
- [ ] Add `INTEGRATION_TEST_KEYS` env var check (skip if no API keys)
- [ ] Document how to run integration tests in QUICK_START.md

**Acceptance Criteria**:
- [ ] Integration tests pass with valid API keys
- [ ] Tests skip gracefully without API keys (CI stays green)
- [ ] At least 5 integration test cases covering happy path + edge cases
- [ ] Output validated against briefing_v1.json schema

**Deliverables**: `tests/test_integration.py`, updated CI config

---

### 5.5 — Analysis Monitoring & Alerting
**Priority**: P1-high
**Labels**: backend, operations
**Estimate**: 3 hours

Track analysis success/failure rates and provide alerting when failure rates exceed thresholds.

**Subtasks**:
- [ ] Add `GET /metrics` endpoint returning: total_runs, success_rate, avg_quality, avg_duration, failure_reasons
- [ ] Track analysis duration (start/end timestamps on Report)
- [ ] Add `AnalysisMetrics` utility class that computes rolling stats from DB
- [ ] Add health check enhancement: warn if success rate < 80% in last 24h
- [ ] Frontend: Metrics panel in dashboard (success rate trend, avg quality trend)
- [ ] Research: webhook alerting design (Slack/email on failure spike)

**Acceptance Criteria**:
- [ ] Metrics endpoint returns accurate stats
- [ ] Analysis duration tracked on report records
- [ ] Health check surfaces degraded state
- [ ] Webhook design documented (implementation deferred to Sprint 6)

**Deliverables**: New `src/cddbs/metrics.py`, updated `api/main.py`, `research/monitoring_design.md`

---

### 5.6 — Network Graph Visualization
**Priority**: P2-medium
**Labels**: frontend
**Estimate**: 4 hours

Render network graph data from briefings as an interactive force-directed graph in the report viewer.

**Subtasks**:
- [ ] Research: evaluate D3.js force layout vs react-force-graph vs vis-network
- [ ] Implement `NetworkGraph.tsx` component rendering nodes + edges
- [ ] Color-code nodes by platform (Twitter=blue, Telegram=purple, News=green)
- [ ] Show edge weights (amplification strength)
- [ ] Render communities as convex hulls or colored clusters
- [ ] Add to ReportViewDialog as a collapsible panel
- [ ] Handle empty graph gracefully (no network data available)

**Acceptance Criteria**:
- [ ] Graph renders for cross-platform briefing fixture
- [ ] Nodes and edges interactive (hover for details)
- [ ] Graceful fallback when no graph data present
- [ ] Minimal dependency footprint (prefer D3 if already bundled)

**Deliverables**: New `frontend/src/components/NetworkGraph.tsx`, updated `ReportViewDialog.tsx`

---

### 5.7 — Backfill Sprint 1 & 2 Retrospectives
**Priority**: P3-low
**Labels**: documentation
**Estimate**: 1 hour

Fill in the template retrospectives for Sprint 1 and Sprint 2 with actual delivery data.

**Subtasks**:
- [ ] Sprint 1: Fill delivery summary, metrics, and lessons learned
- [ ] Sprint 2: Fill delivery summary, quality metrics, and lessons learned
- [ ] Ensure consistency with existing Sprint 3 and 4 retrospective format

**Acceptance Criteria**:
- [ ] Both retrospectives filled with actual data (not template placeholders)
- [ ] Key metrics populated

**Deliverables**: Updated `retrospectives/sprint_1.md`, `retrospectives/sprint_2.md`

---

### 5.8 — CI Pipeline Enhancement
**Priority**: P1-high
**Labels**: operations
**Estimate**: 2 hours

Update CI to cover Sprint 5 additions and run integration tests conditionally.

**Subtasks**:
- [ ] Add integration test job (runs only when `INTEGRATION_TEST_KEYS` secret is set)
- [ ] Add export format validation tests to pytest suite
- [ ] Add sprint_5_backlog.md to file existence check
- [ ] Add batch analysis model tests
- [ ] Ensure all 60+ tests pass

**Deliverables**: Updated `.github/workflows/ci.yml`

---

### 5.9 — Sprint 5 Retrospective & Documentation
**Priority**: P2-medium
**Labels**: documentation
**Estimate**: 1 hour

**Subtasks**:
- [ ] Create Sprint 5 retrospective
- [ ] Update README.md with Sprint 5 deliverables
- [ ] Update execution plan to reflect Sprint 4+5 completion

**Deliverables**: `retrospectives/sprint_5.md`, updated `README.md`, updated `docs/cddbs_execution_plan.md`

---

## Sprint 5 Summary

| Task | Priority | Estimate | Deliverable |
|------|----------|----------|-------------|
| 5.1 Twitter API v2 Integration | P0 | 6h | `twitter_client.py`, updated pipeline |
| 5.2 Batch Analysis Support | P0 | 5h | Batch model + API + frontend dialog |
| 5.3 Export Formats (PDF/JSON/CSV) | P1 | 5h | `export.py`, updated API + frontend |
| 5.4 E2E Integration Tests | P0 | 4h | `test_integration.py` |
| 5.5 Monitoring & Alerting | P1 | 3h | `metrics.py`, health check, design doc |
| 5.6 Network Graph Visualization | P2 | 4h | `NetworkGraph.tsx` |
| 5.7 Backfill Retrospectives | P3 | 1h | Updated sprint_1.md, sprint_2.md |
| 5.8 CI Pipeline Enhancement | P1 | 2h | Updated ci.yml |
| 5.9 Retrospective & Docs | P2 | 1h | retrospective, README, execution plan |
| **Total** | | **31h** | |

---

## Dependencies

```
sprint_5_backlog.md (planning)
    │
    ├─► 5.1 Twitter API v2 Integration
    │       │
    │       └─► 5.2 Batch Analysis (can batch Twitter + news)
    │               │
    │               └─► 5.8 CI Pipeline (test batch + integration)
    │
    ├─► 5.3 Export Formats (independent)
    │
    ├─► 5.4 E2E Integration Tests (depends on 5.1 for Twitter path)
    │
    ├─► 5.5 Monitoring & Alerting (independent)
    │
    ├─► 5.6 Network Graph Visualization (independent — frontend only)
    │
    ├─► 5.7 Backfill Retrospectives (independent — docs only)
    │
    └─► 5.9 Retrospective & Docs (last)
```

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Twitter API v2 access may require paid tier | High | Design adapter to work with Basic tier (limited endpoints); document tier requirements |
| PDF generation adds heavy dependency (weasyprint) | Medium | Evaluate reportlab (lighter) first; make PDF optional, JSON/CSV always available |
| Batch analysis may overload Render free tier | Medium | Limit batch size (max 5 targets); queue with delay between jobs |
| Integration tests with real API are flaky | Medium | Use pytest markers, skip in CI without keys, run manually before release |
| Network graph library adds significant bundle size | Low | Prefer D3.js (tree-shakeable) over full react-force-graph |
