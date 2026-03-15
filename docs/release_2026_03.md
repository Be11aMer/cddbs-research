# Release 2026.03 — First Production Release

**Date:** 2026-03-11
**Branch:** `claude/dashboard-news-api-plan-2DBHl`

## What shipped

This release consolidates all features from research sprints 1-6 into a
deployable, documented production platform.

### New in this release

1. **GitHub Actions CI** — Ruff lint, pytest with PostgreSQL service, and
   frontend build/type-check on every push/PR to `main`.

2. **JSON export endpoint** — `GET /analysis-runs/{id}/export` returns a
   complete structured JSON archive containing briefing, quality scorecard,
   narrative matches, and article analyses. Frontend "Export JSON" button
   added to the Report View dialog.

3. **Operational metrics** — `GET /metrics` returns success rate, average
   quality score, average analysis duration, top countries, and top
   narratives.

4. **Quality trends** — `GET /stats/quality-trends` returns per-outlet
   quality score time-series data with aggregate averages.

5. **Comprehensive developer documentation** — `DEVELOPER.md` covers
   architecture, all 31 API endpoints, 11 data models, 3 pipeline flows,
   30 frontend components, configuration, deployment, testing, and
   contributor guide.

6. **CHANGELOG.md** — Formal release notes.

### Previously implemented (documented for completeness)

- 7-section structured intelligence briefing (Gemini v1.3 prompt)
- 70-point, 7-dimension quality scoring rubric
- Known disinformation narrative matching (50+ narratives)
- Twitter and Telegram social media analysis
- Topic mode discovery pipeline
- Event intelligence with RSS/GDELT collectors (runs every 3 min)
- Event clustering, deduplication, burst detection, narrative risk scoring
- Full monitoring dashboard with 10+ visualization components
- 132 test functions across 12 files
- Docker Compose deployment

## Key files changed

| File | Change |
|------|--------|
| `.github/workflows/ci.yml` | New — CI pipeline |
| `src/cddbs/api/main.py` | +286 lines — export, metrics, quality trends endpoints |
| `frontend/src/api.ts` | +72 lines — export, metrics, quality trends API functions |
| `frontend/src/components/ReportViewDialog.tsx` | Export JSON button |
| `CHANGELOG.md` | New — release notes |
| `DEVELOPER.md` | New — comprehensive developer documentation |

## API endpoints added (total now 31)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/analysis-runs/{id}/export` | JSON export download |
| `GET` | `/metrics` | Operational metrics |
| `GET` | `/stats/quality-trends` | Quality score time-series |

## Known gaps (for future sprints)

- PDF/CSV export formats
- Batch analysis UI
- Social media analysis frontend form
- Prometheus-format metrics
- Alembic migration configuration
