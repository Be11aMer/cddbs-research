# Sprint 4: Research-to-Production Integration Plan (Revised)

**Sprint**: 4 — Production Integration & UX
**Status**: READY FOR IMPLEMENTATION
**Duration**: 2 weeks
**Goal**: Integrate Sprints 1-3 research into the live production CDDBS app

---

## Current Production Architecture (Confirmed)

### Backend (`src/cddbs/`)
- **Framework**: FastAPI (uvicorn, Docker)
- **Database**: Neon PostgreSQL via SQLAlchemy (3 tables: `outlets`, `articles`, `reports`)
- **LLM**: Google Gemini `gemini-2.5-flash` via `google-genai` SDK
- **Pipeline**: Single consolidated prompt in `orchestrator.py` (Fetch → Gemini → JSON parse → Store)
- **API Endpoints**: `POST /analysis-runs`, `GET /analysis-runs`, `GET /analysis-runs/{id}`, `/health`, `/api-status`
- **Deployment**: Render free tier, auto-deploy on push to `main` of `github.com/Be11aMer/cddbs-prod`

### Frontend (`frontend/`)
- **Framework**: React 18 + TypeScript + Vite + MUI 6
- **State**: Redux Toolkit + TanStack Query
- **Routing**: Nginx reverse proxy (`/api/` → `cddbs-api.onrender.com`)
- **Key Components**: `RunsTable`, `RunDetail`, `ReportViewDialog`, `NewAnalysisDialog`, `SettingsDialog`
- **Report Viewer**: Markdown-based, parses 4 sections (Source, Narrative, Analysis, Credibility)

### Database (Neon PostgreSQL)
```
outlets:  id, name, url
articles: id, outlet_id, report_id, title, link, snippet, date, meta(JSON), full_text, created_at
reports:  id, outlet, country, final_report(Text), raw_response(Text), data(JSON), created_at
```

### Current System Prompt (`prompt_templates.py`)
- Basic inline f-string prompt requesting JSON with `individual_analyses[]` and `final_briefing`
- No confidence framework, no narrative detection, no structured output schema

---

## Gap Analysis (Actual vs Research)

| Component | Production (Actual) | Research (Sprint 1-3) | Delta |
|-----------|--------------------|-----------------------|-------|
| **System Prompt** | 40-line inline f-string | 200+ line v1.3 with confidence framework, narratives, CIB | Replace `prompt_templates.py` |
| **Output Format** | `{individual_analyses[], final_briefing}` | Schema v1.2 with 7 sections, network graph, cross-platform | New response parser |
| **Quality Control** | None | 7-dimension scorer (70 pts) | Add `quality_scorer.py` to pipeline |
| **Narrative Detection** | None (themes in prompt only) | 18 known narratives with keyword matching | Add post-processing step |
| **DB Tables** | 3 (outlets, articles, reports) | Need 5 more (briefings, narrative_matches, quality_scores, platform_accounts, xp_links) | Alembic migration |
| **Platform Support** | SerpAPI news only | Twitter API v2 + Telegram MTProto adapters | Add adapters (graceful if no API keys) |
| **Frontend Report View** | 4 markdown sections via regex parse | 7 structured JSON sections with confidence badges | Rewrite `ReportViewDialog` |
| **Quality Badges** | `FIXME` placeholder in `ReportViewDialog.tsx:234` | Quality scorer with rating bands | Integrate scorer result |

---

## Phase 4A: Backend Integration (Week 1)

### Task 4A.1: Add Research Modules to `src/cddbs/`

Copy files into the production directory structure:

```
cddbs-research-draft/                          →  cddbs-prod/src/cddbs/
├── tools/platform_adapters.py                 →  src/cddbs/adapters.py
├── tools/quality_scorer.py                    →  src/cddbs/quality.py
├── data/known_narratives.json                 →  src/cddbs/data/known_narratives.json
├── schemas/briefing_v1.json                   →  src/cddbs/data/briefing_schema_v1.json
├── templates/system_prompt_v1.3.md            →  src/cddbs/data/system_prompt_v1.3.md
├── tests/fixtures/*.json                      →  tests/fixtures/*.json
├── tests/test_quality_scorer.py               →  tests/test_quality.py
├── tests/test_platform_adapters.py            →  tests/test_adapters.py
└── tests/test_schema_validation.py            →  tests/test_schema.py
```

Import path changes needed:
- No external dependencies to add (all stdlib + existing packages)
- `quality_scorer.py` and `platform_adapters.py` are self-contained
- `known_narratives.json` loaded via `Path(__file__).parent / "data"`

### Task 4A.2: Database Schema Migration (Alembic)

Add new SQLAlchemy models to `src/cddbs/models.py` (keep existing 3 models untouched):

```python
# New models to add to models.py

class Briefing(Base):
    __tablename__ = "briefings"
    id = Column(Integer, primary_key=True, index=True)
    briefing_id = Column(String, unique=True, nullable=False, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=True)  # Link to existing report
    subject_handle = Column(String, nullable=False)
    platform = Column(String, nullable=False, default="news")
    briefing_json = Column(JSON, nullable=False)           # Full structured briefing
    executive_summary = Column(Text)
    overall_confidence = Column(String)                     # high/moderate/low
    quality_score = Column(Integer)                         # 0-70
    quality_rating = Column(String)                         # Excellent/Good/Acceptable/Poor
    quality_dimensions = Column(JSON)                       # Per-dimension breakdown
    model_version = Column(String, default="gemini-2.5-flash")
    prompt_version = Column(String, default="v1.3")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    report = relationship("Report", backref="briefing")
    narrative_matches = relationship("NarrativeMatch", back_populates="briefing")

class NarrativeMatch(Base):
    __tablename__ = "narrative_matches"
    id = Column(Integer, primary_key=True, index=True)
    briefing_db_id = Column(Integer, ForeignKey("briefings.id"))
    narrative_id = Column(String, nullable=False, index=True)   # e.g. 'anti_nato_001'
    narrative_name = Column(String)
    category = Column(String)
    matched_keywords = Column(JSON)                              # list of strings
    frequency = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    briefing = relationship("Briefing", back_populates="narrative_matches")
```

Since `init_db()` calls `Base.metadata.create_all()`, new tables are auto-created on startup. No manual migration needed for Neon — just deploy and the tables appear.

### Task 4A.3: Upgrade System Prompt + Output Parser

**Replace** `src/cddbs/pipeline/prompt_templates.py`:

```python
# Load v1.3 prompt from file instead of inline f-string
def get_consolidated_prompt(outlet, country, articles_data):
    prompt_path = Path(__file__).parent.parent / "data" / "system_prompt_v1.3.md"
    base_prompt = prompt_path.read_text()

    # For article analysis, wrap the v1.3 prompt with article-specific context
    return f"""
{base_prompt}

---
ANALYSIS TARGET:
Outlet: {outlet}
Country: {country}

SOURCE ARTICLES:
{articles_data}

Generate a structured JSON briefing following the schema specified above.
Use "news" as the platform. The subject_handle should be the outlet name.
"""
```

**Add output parser** to `orchestrator.py` after Gemini call:
- Parse JSON response
- Validate against briefing schema v1.2
- Run quality scorer on the structured briefing
- Match narratives against `known_narratives.json`
- Store `Briefing` + `NarrativeMatch` records
- Fallback: if Gemini returns old format, wrap it in new schema

### Task 4A.4: Add Quality Scoring to Pipeline

In `orchestrator.py`, after getting the briefing JSON:

```python
from src.cddbs.quality import score_briefing
from src.cddbs.narratives import match_narratives  # new module

# After parsing Gemini response into briefing_json:
scorecard = score_briefing(briefing_json)
narrative_hits = match_narratives(briefing_json, narratives_db)

# Store enriched briefing
briefing = Briefing(
    briefing_id=f"CDDBS-{report.id:05d}",
    report_id=report.id,
    subject_handle=outlet,
    platform="news",
    briefing_json=briefing_json,
    executive_summary=briefing_json.get("executive_summary", ""),
    overall_confidence=briefing_json.get("metadata", {}).get("overall_confidence", ""),
    quality_score=scorecard["total_score"],
    quality_rating=scorecard["rating"],
    quality_dimensions=scorecard["dimensions"],
)
session.add(briefing)

for hit in narrative_hits:
    session.add(NarrativeMatch(
        briefing_db_id=briefing.id,
        narrative_id=hit["narrative_id"],
        narrative_name=hit["narrative_name"],
        category=hit["category"],
        matched_keywords=hit["matched_keywords"],
    ))
```

### Task 4A.5: Add New API Endpoints

Add to `src/cddbs/api/main.py`:

```python
# --- New v2 endpoints (alongside existing) ---

@app.get("/briefings/{briefing_id}")
def get_briefing(briefing_id: str, db: Session = Depends(get_db)):
    """Get a structured briefing by its CDDBS ID."""
    ...

@app.get("/analysis-runs/{report_id}/briefing")
def get_report_briefing(report_id: int, db: Session = Depends(get_db)):
    """Get the structured briefing for an analysis run (if available)."""
    ...

@app.get("/analysis-runs/{report_id}/quality")
def get_report_quality(report_id: int, db: Session = Depends(get_db)):
    """Get the quality scorecard for an analysis run."""
    ...

@app.get("/narratives")
def list_narratives():
    """List all known narratives from the database."""
    ...

@app.get("/narratives/{narrative_id}/matches")
def get_narrative_matches(narrative_id: str, db: Session = Depends(get_db)):
    """Get all briefings matching a specific narrative."""
    ...
```

### Task 4A.6: Update Dockerfile

Add data files to Docker build:

```dockerfile
# In Dockerfile, after COPY src:
COPY src /app/src
# No changes needed - data/ is inside src/cddbs/data/
```

---

## Phase 4B: Frontend UX Upgrade (Week 2)

### Task 4B.1: Add Quality Badge to Report Viewer

In `ReportViewDialog.tsx`, replace the `FIXME` placeholder (line 234):

```tsx
// Replace hardcoded "High Confidence" / "Limited Data" with actual quality score
<Chip
    label={briefing?.quality_rating
        ? `${briefing.quality_score}/70 — ${briefing.quality_rating}`
        : data.articles.length >= 3 ? "High Confidence" : "Limited Data"
    }
    size="small"
    color={
        briefing?.quality_score >= 60 ? "success" :
        briefing?.quality_score >= 40 ? "info" :
        briefing?.quality_score >= 30 ? "warning" : "error"
    }
/>
```

### Task 4B.2: Upgrade Report Viewer Sections

Replace the 4-section markdown parsing (`parseSections`) with structured JSON rendering:

Current sections: Source, Narrative, Analysis, Credibility
New sections (from schema v1.2):
1. **Executive Summary** — with confidence badge
2. **Subject Profile** — handle, platform, followers, bio
3. **Key Findings** — cards with individual confidence levels
4. **Narrative Analysis** — matched narratives with tags
5. **Evidence Base** — collapsible evidence items with source types
6. **Quality Score** — radar chart of 7 dimensions
7. **Limitations** — alternative interpretations

Fetch structured data from new endpoint:
```tsx
// In api.ts, add:
export async function fetchBriefing(reportId: number) {
    const { data } = await api.get<BriefingResponse>(`/analysis-runs/${reportId}/briefing`);
    return data;
}

export async function fetchQuality(reportId: number) {
    const { data } = await api.get<QualityResponse>(`/analysis-runs/${reportId}/quality`);
    return data;
}
```

### Task 4B.3: Add Narrative Tags to RunsTable

In `RunsTable.tsx`, add a column showing matched narratives as color-coded chips:

```tsx
<Chip label="Anti-NATO" size="small" color="error" />
<Chip label="Ukraine" size="small" color="warning" />
```

### Task 4B.4: Quality Radar Chart Component

New component `QualityRadar.tsx` using recharts (already in MUI ecosystem):

Add to `package.json`: `"recharts": "^2.12.0"`

7-axis radar chart showing:
- Structural Completeness
- Attribution Quality
- Confidence Signaling
- Evidence Presentation
- Analytical Rigor
- Actionability
- Readability

### Task 4B.5: Dashboard Metric Cards Update

Update the 4 metric cards in `App.tsx` to include:
- **Total Analyses** (keep)
- **Avg Quality Score** (new — replace "Running")
- **Active Narratives** (new — replace "Completed")
- **Success Rate** (keep)

---

## Deployment Plan

### Step 1: Create branch
```bash
cd cddbs-prod
git checkout -b feature/sprint-4-integration
```

### Step 2: Copy research files + make changes

### Step 3: Test locally
```bash
docker-compose up --build
# Run existing tests
pytest tests/
# Run new research tests
pytest tests/test_quality.py tests/test_adapters.py tests/test_schema.py
```

### Step 4: Push to branch → create PR
```bash
git push origin feature/sprint-4-integration
# Create PR → review → merge to main
# Render auto-deploys on merge to main
```

### Step 5: Verify deployment
- `GET /health` returns OK
- `POST /analysis-runs` with RT → check response includes `quality_score`
- `GET /analysis-runs/{id}/briefing` returns structured JSON
- Frontend shows quality badge instead of `FIXME`

### Rollback
- All changes are additive (new tables, new endpoints, new files)
- Existing endpoints (`/analysis-runs`) remain backward compatible
- If merge breaks, revert the PR on GitHub → Render auto-reverts

---

## File-Level Change Summary

### New Files in `cddbs-prod`
```
src/cddbs/adapters.py              (from tools/platform_adapters.py)
src/cddbs/quality.py               (from tools/quality_scorer.py)
src/cddbs/narratives.py            (new — narrative matching module)
src/cddbs/data/known_narratives.json
src/cddbs/data/briefing_schema_v1.json
src/cddbs/data/system_prompt_v1.3.md
tests/fixtures/                     (6 fixture files)
tests/test_quality.py
tests/test_adapters.py
tests/test_schema.py
frontend/src/components/QualityRadar.tsx
frontend/src/components/NarrativeTags.tsx
frontend/src/components/BriefingView.tsx
```

### Modified Files in `cddbs-prod`
```
src/cddbs/models.py                (add Briefing + NarrativeMatch models)
src/cddbs/pipeline/prompt_templates.py  (load v1.3 prompt from file)
src/cddbs/pipeline/orchestrator.py      (add quality scoring + narrative matching)
src/cddbs/api/main.py                   (add new endpoints)
src/cddbs/utils/genai_client.py         (update system prompt source)
frontend/package.json                    (add recharts)
frontend/src/api.ts                      (add briefing/quality fetch functions)
frontend/src/components/ReportViewDialog.tsx  (structured view + quality badge)
frontend/src/components/RunsTable.tsx         (narrative tags column)
frontend/src/App.tsx                          (updated metric cards)
requirements.txt                              (add jsonschema for validation)
Dockerfile                                    (no changes needed - data inside src/)
```

### Unchanged Files (backward compatible)
```
render.yaml
docker-compose.yml
frontend/Dockerfile
frontend/nginx.conf
All existing test files
```

---

## Success Criteria

- [ ] `docker-compose up --build` succeeds
- [ ] All existing tests pass (`pytest tests/`)
- [ ] All new tests pass (`pytest tests/test_quality.py tests/test_adapters.py tests/test_schema.py`)
- [ ] `POST /analysis-runs` returns reports with `quality_score` field
- [ ] `GET /analysis-runs/{id}/briefing` returns structured JSON
- [ ] Frontend `ReportViewDialog` shows quality badge (not FIXME)
- [ ] New tables (`briefings`, `narrative_matches`) created in Neon on deploy
- [ ] Existing data in `outlets`, `articles`, `reports` tables untouched
- [ ] Render deployment succeeds without manual intervention
