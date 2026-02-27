# Sprint 4: Research-to-Production Integration Plan

**Sprint**: 4 — Production Integration & UX
**Status**: PLANNING
**Duration**: 2 weeks
**Goal**: Integrate Sprints 1-3 research into the production CDDBS application

---

## Current State Assessment

### Production App (`cddbs-prod` on Codeberg)
- **Stack**: Python (LangGraph + Gemini), Flask/FastAPI on Render
- **Backend**: `cddbs-api.onrender.com` — 5-stage pipeline (Fetch → Analyze → Digest → Translate → Summarize)
- **Frontend**: `cddbs-frontend.onrender.com` — Web dashboard
- **Database**: PostgreSQL (user says migrated to Neon; execution plan originally said Supabase)
  - 3 tables: `outlets`, `articles`, `analyses`
- **Auth**: BYOK (Bring Your Own Key) — API keys in browser localStorage
- **LLM**: Google Gemini (`gemini-2.5-flash`)
- **Data Collection**: SerpAPI (news search) + BeautifulSoup (content extraction)
- **Source Code**: Codeberg (not GitHub) — `cddbs-prod` repo

### Research Draft (Sprints 1-3 completed)
- **Sprint 1**: Briefing format redesign — JSON schema v1.2, 7-section template, system prompts
- **Sprint 2**: Quality & reliability — 7-dimension quality scorer, 18 known narratives, source verification
- **Sprint 3**: Multi-platform — Twitter/Telegram adapters, cross-platform identity resolution, network analysis, CIB detection

### Gap Analysis

| Component | Production (Current) | Research (New) | Integration Work |
|-----------|---------------------|----------------|-----------------|
| **Output Format** | Unstructured markdown text | Structured JSON (schema v1.2) | Replace output pipeline |
| **System Prompt** | Basic "objective briefing" prompt | v1.3 multi-platform with confidence framework | Swap prompt, validate output |
| **Quality Control** | None | 7-dimension, 70-point auto-scorer | Add scoring post-analysis |
| **Narrative Detection** | None | 18 known narratives with keyword matching | Add narrative matching step |
| **Database Schema** | 3 tables (outlets, articles, analyses) | Needs: briefings, narratives, quality_scores, platform_accounts | Schema migration |
| **Platform Support** | News article scraping only | Twitter API v2 + Telegram MTProto | Add social media adapters |
| **Data Adapters** | BeautifulSoup scraper only | TwitterAdapter + TelegramAdapter | Integrate adapters |
| **Analysis Pipeline** | 5 LangGraph nodes (article-focused) | Account-focused briefing generation | Extend pipeline |
| **Frontend** | Basic React dashboard | Needs: briefing viewer, quality badges, network graph viz | Major UX upgrade |
| **Cross-Platform** | None | Identity resolution, content fingerprinting | New feature |
| **Network Analysis** | None | Graph construction, centrality, CIB scoring | New feature |

---

## Integration Strategy

### Approach: Incremental Integration (NOT rewrite)

We will **extend the existing production app** rather than replacing it:
1. Keep the existing article analysis pipeline working
2. Add a new **account analysis** pipeline alongside it
3. Migrate to structured JSON output format
4. Add quality scoring as a post-processing step
5. Expand the database schema
6. Upgrade the frontend incrementally

### Why Not Rewrite?
- Production is live and deployed — minimize disruption
- Article analysis is a valid use case to keep
- Database already has data — migration, not replacement
- Users are using it — backward compatibility matters

---

## Phase Breakdown

### Phase 4A: Backend Integration (Week 1)
**Priority**: P0 — Core pipeline upgrade

#### Task 4A.1: Database Schema Migration
**Effort**: 4 hours

Add new tables to Neon PostgreSQL while keeping existing tables:

```sql
-- New tables (add to existing schema)

CREATE TABLE briefings (
    id SERIAL PRIMARY KEY,
    briefing_id VARCHAR(100) UNIQUE NOT NULL,
    subject_handle VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    briefing_json JSONB NOT NULL,          -- Full structured briefing
    executive_summary TEXT,                 -- Extracted for quick display
    overall_confidence VARCHAR(20),         -- high/moderate/low
    quality_score INTEGER,                  -- 0-70 from quality scorer
    quality_rating VARCHAR(20),             -- Excellent/Good/Acceptable/Poor
    model_version VARCHAR(50),
    prompt_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE narrative_matches (
    id SERIAL PRIMARY KEY,
    briefing_id INTEGER REFERENCES briefings(id),
    narrative_id VARCHAR(50) NOT NULL,      -- e.g., 'anti_nato_001'
    narrative_name VARCHAR(255),
    category VARCHAR(100),
    matched_keywords TEXT[],
    frequency VARCHAR(20),                  -- dominant/frequent/occasional
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE platform_accounts (
    id SERIAL PRIMARY KEY,
    handle VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    display_name VARCHAR(255),
    followers INTEGER DEFAULT 0,
    bio TEXT,
    last_analyzed TIMESTAMP,
    total_briefings INTEGER DEFAULT 0,
    UNIQUE(handle, platform)
);

CREATE TABLE cross_platform_links (
    id SERIAL PRIMARY KEY,
    account_a_id INTEGER REFERENCES platform_accounts(id),
    account_b_id INTEGER REFERENCES platform_accounts(id),
    confidence VARCHAR(20),                 -- high/moderate/low
    composite_score FLOAT,
    signals JSONB,                          -- Signal breakdown
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE quality_scores (
    id SERIAL PRIMARY KEY,
    briefing_id INTEGER REFERENCES briefings(id),
    total_score INTEGER NOT NULL,
    rating VARCHAR(20) NOT NULL,
    dimensions JSONB NOT NULL,              -- Per-dimension breakdown
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add index for common queries
CREATE INDEX idx_briefings_subject ON briefings(subject_handle, platform);
CREATE INDEX idx_briefings_quality ON briefings(quality_score);
CREATE INDEX idx_narrative_matches_narrative ON narrative_matches(narrative_id);
CREATE INDEX idx_platform_accounts_handle ON platform_accounts(handle, platform);
```

#### Task 4A.2: Copy Research Modules to Production
**Effort**: 2 hours

Copy and adapt these files from `cddbs-research-draft` to `cddbs-prod`:

```
cddbs-research-draft/                  →  cddbs-prod/
├── tools/platform_adapters.py         →  backend/adapters/platform_adapters.py
├── tools/quality_scorer.py            →  backend/scoring/quality_scorer.py
├── schemas/briefing_v1.json           →  backend/schemas/briefing_v1.json
├── data/known_narratives.json         →  backend/data/known_narratives.json
├── templates/system_prompt_v1.3.md    →  backend/prompts/system_prompt_v1.3.md
├── tests/test_platform_adapters.py    →  backend/tests/test_platform_adapters.py
├── tests/test_quality_scorer.py       →  backend/tests/test_quality_scorer.py
├── tests/test_schema_validation.py    →  backend/tests/test_schema_validation.py
└── tests/fixtures/*.json              →  backend/tests/fixtures/*.json
```

Changes needed:
- Update import paths for production directory structure
- Add database connection to quality scorer (store results)
- Add Neon connection string via environment variable
- Ensure all 80 tests pass in production environment

#### Task 4A.3: Extend Analysis Pipeline
**Effort**: 6 hours

Add a new **account analysis** LangGraph pipeline alongside the existing article pipeline:

```python
# New pipeline: Account Analysis (social media briefing generation)
#
# Input: platform handle (e.g., @rt_com, @rt_english)
# Output: Structured briefing JSON (schema v1.2)

account_analysis_graph = StateGraph(AccountAnalysisState)

# Node 1: Collect — Fetch data via platform adapter
account_analysis_graph.add_node("collect", collect_social_data)

# Node 2: Normalize — Run through TwitterAdapter/TelegramAdapter
account_analysis_graph.add_node("normalize", normalize_platform_data)

# Node 3: Analyze — Send to Gemini with system_prompt_v1.3
account_analysis_graph.add_node("analyze", generate_briefing)

# Node 4: Validate — Schema validation + quality scoring
account_analysis_graph.add_node("validate", validate_and_score)

# Node 5: Detect Narratives — Match against known_narratives.json
account_analysis_graph.add_node("detect_narratives", match_narratives)

# Node 6: Store — Save to Neon database
account_analysis_graph.add_node("store", persist_briefing)
```

#### Task 4A.4: Update System Prompt Integration
**Effort**: 3 hours

Replace the current basic prompt with `system_prompt_v1.3.md`:
- Load prompt from file (not hardcoded)
- Inject known narratives context dynamically
- Ensure Gemini output matches JSON schema v1.2
- Add output parsing/validation step (JSON parse + schema validate)
- Add retry logic for malformed LLM output (max 2 retries)

#### Task 4A.5: Add API Endpoints
**Effort**: 4 hours

New REST endpoints for the production API:

```
POST /api/v2/analyze/account
  Body: { "handle": "@rt_com", "platform": "twitter" }
  Response: { "briefing_id": "...", "status": "processing" }

GET /api/v2/briefings/{briefing_id}
  Response: Full structured briefing JSON

GET /api/v2/briefings
  Query: ?platform=twitter&min_quality=50&limit=20
  Response: Paginated briefing list

GET /api/v2/briefings/{briefing_id}/quality
  Response: Quality scorecard with dimension breakdown

GET /api/v2/narratives
  Response: All known narratives from database

GET /api/v2/narratives/{narrative_id}/matches
  Response: All briefings that match this narrative

POST /api/v2/compare
  Body: { "handle_a": "@rt_com", "handle_b": "@rt_english", "platform_a": "twitter", "platform_b": "telegram" }
  Response: Cross-platform identity resolution result

# Keep existing v1 endpoints working
GET /api/v1/analyze  (existing article pipeline — unchanged)
```

---

### Phase 4B: Frontend UX Upgrade (Week 2)
**Priority**: P1 — User experience

#### Task 4B.1: Briefing Viewer Component
**Effort**: 6 hours

New React component that renders structured briefings:
- **Executive summary** banner with confidence badge (high=green, moderate=yellow, low=red)
- **Key findings** cards with per-finding confidence indicators
- **Subject profile** sidebar with platform icon, follower count, bio
- **Narrative alignment** section with matched narrative tags
- **Quality score** badge in header (e.g., "62/70 — Excellent")
- **Evidence references** collapsible section
- **Limitations** section with expandable alternative interpretations

#### Task 4B.2: Dashboard Redesign
**Effort**: 4 hours

Upgrade the main dashboard:
- **Search bar**: Enter handle + select platform → trigger analysis
- **Recent briefings** list with quality score, confidence, platform icon
- **Narrative heatmap**: Which narratives are most active across all analyzed accounts
- **Platform filter**: Toggle Twitter/Telegram/All
- **Quality filter**: Slider to filter by minimum quality score

#### Task 4B.3: Quality Score Visualization
**Effort**: 3 hours

- Radar chart (7 dimensions) using Chart.js or Recharts
- Score breakdown bar with color-coded dimensions
- Compare mode: overlay two briefings' quality profiles
- Historical trend: how an account's briefing quality changes over time

#### Task 4B.4: Network Graph Visualization
**Effort**: 4 hours

Interactive network graph viewer (using D3.js, vis.js, or Cytoscape.js):
- Nodes colored by platform (Twitter=blue, Telegram=teal)
- Node size by PageRank influence
- Edge thickness by interaction weight
- Click node → view account profile / trigger analysis
- Community clustering with labels
- Zoom/pan/filter controls

#### Task 4B.5: Cross-Platform Identity Panel
**Effort**: 3 hours

When viewing a briefing with cross-platform identities:
- Side-by-side profile comparison panel
- Signal strength indicators (8 signals with scores)
- Content overlap percentage
- Temporal synchronization chart
- "Linked accounts" section in briefing viewer

---

## Production Deployment Plan

### Environment Configuration (Render)

```bash
# Existing env vars (keep)
GOOGLE_API_KEY=...
SERPER_API=...

# New env vars (add)
DATABASE_URL=postgresql://...@ep-xxx.us-east-2.aws.neon.tech/cddbs  # Neon connection string
TWITTER_BEARER_TOKEN=...          # Twitter API v2 (when ready)
TELEGRAM_API_ID=...               # Telegram MTProto (when ready)
TELEGRAM_API_HASH=...             # Telegram MTProto (when ready)
CDDBS_VERSION=1.3.0
SYSTEM_PROMPT_VERSION=v1.3
```

### Deployment Steps

1. **Branch**: Create `feature/sprint-4-integration` in `cddbs-prod`
2. **Database**: Run migration SQL against Neon (new tables only — no breaking changes)
3. **Backend**: Deploy updated backend to Render
4. **Frontend**: Deploy updated frontend to Render
5. **Smoke Test**: Analyze @rt_com → verify structured briefing + quality score
6. **Rollback Plan**: Old v1 endpoints remain untouched; v2 endpoints are additive

### Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Neon DB migration breaks existing data | New tables only; no ALTER on existing tables |
| Gemini output doesn't match schema | JSON parsing with retry + fallback to unstructured |
| Render cold start delays | Add health check endpoint; consider paid tier |
| Twitter/Telegram API not yet configured | Graceful degradation: show "API not configured" in UI |
| Quality scorer disagrees with human judgment | Show scores as "beta" with feedback button |

---

## Implementation Priority Order

```
Week 1 (Backend):
  Day 1-2: 4A.1 (DB migration) + 4A.2 (copy modules)
  Day 3-4: 4A.3 (extend pipeline) + 4A.4 (system prompt)
  Day 5:   4A.5 (API endpoints) + integration testing

Week 2 (Frontend):
  Day 1-2: 4B.1 (briefing viewer) + 4B.2 (dashboard)
  Day 3:   4B.3 (quality visualization)
  Day 4:   4B.4 (network graph) + 4B.5 (cross-platform panel)
  Day 5:   End-to-end testing + deployment
```

---

## Success Criteria

- [ ] All 80 research tests pass in production environment
- [ ] New account analysis endpoint generates valid schema v1.2 briefings
- [ ] Quality scorer runs on every briefing and stores results
- [ ] Narrative matching detects at least 1 narrative for state media accounts
- [ ] Frontend displays structured briefings with quality badges
- [ ] Existing article analysis pipeline still works (backward compatible)
- [ ] Database migration is non-destructive (existing data preserved)
- [ ] Deployment to Render succeeds without downtime

---

## Open Questions for User

1. **Production repo access**: `cddbs-prod` is on Codeberg (confirmed from execution plan). Can you either:
   - Clone it into this environment so we can work on it directly?
   - Or give the Codeberg URL so we can access it?
   - Or create a GitHub mirror we can push to?

2. **Database status**: The execution plan says "migrating to Supabase" but you mentioned Neon. Which is the current provider? Can you provide the DATABASE_URL connection string?

3. **Twitter API access**: Do you have a Twitter API v2 Bearer Token? (Needed for live data collection)

4. **Telegram API access**: Do you have Telegram API credentials (api_id + api_hash)? (Needed for Telegram data)

5. **Frontend setup**: Is the frontend in the same repo as the backend, or separate? What framework (vanilla HTML? React? Vue?)?

6. **Render service config**: What are the exact Render service names and any render.yaml config?

7. **Priority**: Should we focus on backend-only first (API + DB), or do frontend changes simultaneously?

8. **Framework**: Is the backend Flask or FastAPI? (The execution plan says "Flask/FastAPI" — which one is it?)
