# Sprint 5 Execution Context

**Purpose**: Reference file to maintain coherence across Sprint 5 tasks.
**Sprint**: 5 — Operational Maturity & Data Ingestion
**Version Target**: v1.5.0
**Duration**: March 3-16, 2026

---

## What Exists (Sprint 4 State — Production)

### Backend (`cddbs-prod/src/cddbs/`)

**Pipeline** (`pipeline/orchestrator.py`):
- Single entry point: `run_pipeline(outlet, country, report_id, num_articles, url, serpapi_key, google_api_key, date_filter)`
- Flow: `fetch_articles()` → format articles → `get_consolidated_prompt()` → `call_gemini()` → JSON parse → persist Report + Articles → `score_briefing()` → `match_narratives_from_report()` → commit
- All data sources flow through SerpAPI Google News — no direct platform API integration yet

**Models** (`models.py` — 6 tables):
- `Outlet`: id, name (unique), url
- `Article`: id, outlet_id, report_id, title, link, snippet, date, meta (JSON), full_text, created_at
- `Report`: id, outlet, country, final_report (Text), raw_response (Text), data (JSON), created_at
- `Briefing`: id, report_id (unique FK), briefing_json, quality_score (int/70), quality_rating, quality_details (JSON), prompt_version, created_at
- `NarrativeMatch`: id, report_id (FK), narrative_id, narrative_name, category, confidence, matched_keywords (JSON), match_count, created_at
- `Feedback`: id, tester_name, tester_role, overall_rating, accuracy_rating, usability_rating, bugs_encountered, + optional fields, created_at

**API Endpoints** (`api/main.py`):
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service identity |
| GET | `/health` | DB connectivity |
| GET | `/api-status` | API key config status |
| POST | `/analysis-runs` | Create analysis (queues background task) |
| GET | `/analysis-runs` | List all runs with status/quality/narratives |
| GET | `/analysis-runs/{id}` | Full report with articles |
| GET | `/analysis-runs/{id}/quality` | Quality scorecard |
| GET | `/analysis-runs/{id}/narratives` | Narrative matches |
| GET | `/narratives` | Known narratives DB |
| POST | `/feedback` | Submit feedback |
| GET | `/feedback` | List feedback |

**Quality Scorer** (`quality.py`):
- 7 dimensions × 10 points = 70 max
- Ratings: Excellent (≥60), Good (≥50), Acceptable (≥40), Poor (≥30), Failing (<30)
- Structural, non-LLM scoring (deterministic)

**Platform Adapters** (`adapters.py`):
- `TwitterAdapter` + `TelegramAdapter` exist with normalize methods
- `BriefingInput` dataclass for common format
- **NOT wired into pipeline** — this is the Sprint 5 gap

**Narrative Matcher** (`narratives.py`):
- Keyword-based matching against `data/known_narratives.json` (18 narratives, 8 categories)
- Confidence: high (≥5 hits), moderate (3-4), low (2)

**Config** (`config.py`):
- `SERPAPI_KEY`, `GOOGLE_API_KEY`, `GEMINI_MODEL`, `ARTICLE_LIMIT`, `DATABASE_URL`, `ALLOWED_ORIGINS`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`
- No `TWITTER_BEARER_TOKEN` yet

### Frontend (`cddbs-prod/frontend/`)

**Stack**: React 18 + TypeScript + Vite 6 + MUI 6 + Redux Toolkit + TanStack Query v5

**Key Components**:
- `App.tsx`: Layout with AppBar, sidebar, dashboard metrics (Total Analyses, Avg Quality, Narratives, Success Rate)
- `RunsTable.tsx`: Sortable/filterable table with quality column + narrative count
- `RunDetail.tsx`: Sidebar detail with QualityBadge + NarrativeTags
- `ReportViewDialog.tsx`: Full report with markdown rendering, quality radar, narrative panel
- `NewAnalysisDialog.tsx`: Form with outlet/url/country/articles/date_filter
- `QualityBadge.tsx`, `QualityRadarChart.tsx`, `NarrativeTags.tsx`: Quality/narrative display
- `FeedbackDialog.tsx`, `TestGuideDialog.tsx`: Beta testing infrastructure
- `ColdStartNotice.tsx`, `Skeletons.tsx`, `StatusIndicator.tsx`: UX polish

**Missing from frontend**:
- No batch analysis UI
- No export buttons
- No network graph visualization
- No Twitter-specific analysis form fields

### Tests (56 passing in production)

| File | Count | Scope |
|------|-------|-------|
| `test_quality.py` | 23 | Quality scorer across all fixture types |
| `test_adapters.py` | 22 | Twitter + Telegram adapters |
| `test_narratives.py` | 11 | Keyword matching, confidence, dedup |
| `test_api.py` | — | Endpoint tests with TestClient |
| `test_pipeline.py` | — | Pipeline module mocks |
| `test_models.py` | — | ORM model CRUD |
| `test_database.py` | — | DB connection/session/transaction |
| `test_orchestrator.py` | — | Integration with mocked Gemini |
| `test_schema.py` | — | Schema validation (conditional on jsonschema) |

---

## Sprint 5 Key Decisions

### 1. Twitter API v2 Integration Approach

**Decision**: Add `twitter_client.py` as a new fetch module alongside `fetch.py`
**Rationale**: Keep SerpAPI path untouched; add Twitter path as alternative data source

Pipeline routing:
```
POST /analysis-runs {platform: "news"}   → fetch_articles() via SerpAPI (existing)
POST /analysis-runs {platform: "twitter"} → fetch_tweets() via Twitter API v2 (new)
```

Twitter API v2 endpoints needed:
- `GET /2/users/by/username/:username` — resolve handle to user ID
- `GET /2/users/:id/tweets` — get recent tweets (max 100 per request)
- `GET /2/users/:id` — get profile data (followers, bio, etc.)

Bearer token: stored in `TWITTER_BEARER_TOKEN` env var. Basic tier gives 10K tweets/month read.

### 2. Batch Analysis Architecture

**Decision**: Lightweight batch model linking to existing Report records
**Rationale**: Minimal schema change; each target still creates an independent Report

```python
class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True)
    name = Column(String)  # optional batch name
    status = Column(String, default="queued")  # queued/running/completed/failed
    target_count = Column(Integer)
    completed_count = Column(Integer, default=0)
    report_ids = Column(JSON)  # [1, 2, 3] — links to Report.id
    created_at = Column(DateTime, default=...)
```

Batch execution: loop targets, call `run_pipeline()` for each, update `completed_count`. Max batch size: 5 (Render free tier constraint).

### 3. Export Format Strategy

**Decision**: JSON always available (no dependency), CSV via stdlib `csv`, PDF via `reportlab`
**Rationale**: `reportlab` is lighter than weasyprint; JSON/CSV add zero dependencies

Export endpoint: `GET /analysis-runs/{id}/export?format=json|csv|pdf`

### 4. Integration Test Design

**Decision**: Use `@pytest.mark.integration` marker; skip without `INTEGRATION_TEST_KEYS`
**Rationale**: Keep CI green without API keys; developers run integration tests manually

```bash
# Run unit tests only (CI default)
pytest -m "not integration"

# Run all tests including integration (requires API keys)
SERPAPI_KEY=xxx GOOGLE_API_KEY=xxx pytest
```

### 5. Network Graph Library

**Decision**: Evaluate D3.js force-directed layout (via `d3-force` + React SVG)
**Rationale**: D3 is tree-shakeable; only import `d3-force` + `d3-selection` (< 30KB gzipped). Full react-force-graph is 200KB+.

---

## File Inventory (Sprint 5 New/Modified)

### New Files in `cddbs-prod`
| File | Task | Notes |
|------|------|-------|
| `src/cddbs/pipeline/twitter_client.py` | 5.1 | Twitter API v2 client |
| `src/cddbs/export.py` | 5.3 | PDF/JSON/CSV export module |
| `src/cddbs/metrics.py` | 5.5 | Analysis metrics computation |
| `tests/test_integration.py` | 5.4 | E2E integration tests |
| `frontend/src/components/NetworkGraph.tsx` | 5.6 | Force-directed graph viz |
| `frontend/src/components/BatchAnalysisDialog.tsx` | 5.2 | Multi-target analysis form |
| `research/monitoring_design.md` | 5.5 | Alerting/webhook design doc |

### Modified Files in `cddbs-prod`
| File | Task | Changes |
|------|------|---------|
| `src/cddbs/config.py` | 5.1 | Add `TWITTER_BEARER_TOKEN` |
| `src/cddbs/models.py` | 5.2 | Add `Batch` model |
| `src/cddbs/pipeline/orchestrator.py` | 5.1 | Route by platform |
| `src/cddbs/api/main.py` | 5.1-5.5 | Batch, export, metrics endpoints |
| `frontend/src/api.ts` | 5.2-5.3 | Batch + export API functions |
| `frontend/src/components/ReportViewDialog.tsx` | 5.3, 5.6 | Export buttons, network graph |
| `frontend/src/components/App.tsx` | 5.2 | Batch status in dashboard |
| `requirements.txt` | 5.3 | Add `reportlab` |
| `.github/workflows/ci.yml` | 5.8 | Integration test job |

### Modified Files in `cddbs-research-draft`
| File | Task | Changes |
|------|------|---------|
| `retrospectives/sprint_1.md` | 5.7 | Fill in actual data |
| `retrospectives/sprint_2.md` | 5.7 | Fill in actual data |
| `README.md` | 5.9 | Sprint 5 deliverables |
| `docs/cddbs_execution_plan.md` | 5.9 | Sprint 4+5 completion |

---

## Deployment Notes

- **New env var**: `TWITTER_BEARER_TOKEN` (optional — pipeline skips Twitter path if unset)
- **New pip dependency**: `reportlab` (PDF generation — ~2MB installed)
- **No new npm dependencies** if using D3 directly (d3-force is a devDependency of @types/d3)
- **Batch size limit**: 5 targets max (Render free tier has limited CPU/memory)
- **Tables auto-created**: `batches` table via `init_db()` on deploy
