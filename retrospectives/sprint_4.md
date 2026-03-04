# Sprint 4 Retrospective

**Sprint**: 4 — Research-to-Production Integration
**Duration**: March 1-3, 2026 (compressed sprint)
**Version**: v1.4.0

---

## Sprint Goal

Integrate Sprints 1-3 research (quality scoring, narrative detection, multi-platform adapters, system prompt v1.3) into the live production CDDBS app (`cddbs-prod`), and upgrade the frontend UX to surface quality and narrative data.

## Delivery Summary

### Phase 4A: Backend Integration

| Task | Status | Notes |
|------|--------|-------|
| 4A.1 Copy research modules to `src/cddbs/` | Done | quality.py, adapters.py, narratives.py, data files, test fixtures |
| 4A.2 Database schema (Briefing + NarrativeMatch) | Done | Simplified from plan — FK to reports.id, auto-created via init_db() |
| 4A.3 Upgrade system prompt + output parser | Done | v1.3 loaded from file, JSON parse with fallback chain |
| 4A.4 Quality scoring in pipeline | Done | score_briefing() + match_narratives_from_report() in orchestrator |
| 4A.5 New API endpoints | Done | 3 new endpoints + updated runs list (simpler than planned) |
| 4A.6 Dockerfile update | Done | No changes needed — data/ inside src/ already copied |

### Phase 4B: Frontend UX

| Task | Status | Notes |
|------|--------|-------|
| 4B.1 Quality badge in report viewer | Done | QualityBadge component, replaces FIXME placeholder |
| 4B.2 Structured report sections | Done | Markdown rendering + quality radar + narrative panel |
| 4B.3 Narrative tags in RunsTable | Done | NarrativeTags component with confidence color-coding |
| 4B.4 Quality radar chart | Done | Custom SVG (no recharts dependency) |
| 4B.5 Dashboard metric cards | Done | Avg Quality + Narratives Detected replace Running/Completed |

### Unplanned Work (Delivered)

| Feature | Notes |
|---------|-------|
| Feedback system | Feedback model, POST/GET /feedback endpoints, FeedbackDialog component |
| Test guide | TestGuideDialog with 5-step walkthrough + 4 test scenarios |
| Keyboard shortcuts | useKeyboardShortcuts hook, Ctrl+K/N/R, Shift+?, Escape |
| Cold start handling | ColdStartNotice component, wakeUpBackend() on mount |
| Skeleton loading | TableSkeleton, DetailSkeleton, MetricCardSkeleton |
| Status distribution chart | Custom SVG donut chart for run status breakdown |
| Collapsible sidebar | Pinnable drawer with localStorage persistence |
| Error message utilities | HTTP status code → human-readable message mapping |

---

## Plan vs Actual: Key Differences

### Simplified from plan

| Plan | Actual | Rationale |
|------|--------|-----------|
| `Briefing` with `briefing_id`, `subject_handle`, `platform`, etc. | `Briefing` with `report_id` (unique FK), `briefing_json`, `quality_score` | Simpler — one briefing per report, no separate ID system needed |
| `NarrativeMatch` FK to `briefings.id` | FK to `reports.id` + `confidence` + `match_count` fields | Direct report association; added confidence/count for richer data |
| 5 new API endpoints (`/briefings/{id}`, `/narratives/{id}/matches`, etc.) | 3 endpoints (`/quality`, `/narratives`, `/narratives` DB) | Simpler API surface; briefing data accessible via report endpoints |
| `recharts` dependency for radar chart | Custom SVG radar chart (heptagon) | Zero new dependencies; full control over rendering |
| `jsonschema` added to requirements.txt | Skipped — tests conditional on jsonschema install | Avoids new dependency in production |

### Expanded beyond plan

| Addition | Impact |
|----------|--------|
| Feedback system (model + API + UI) | Beta testing infrastructure for analyst feedback collection |
| Keyboard shortcuts framework | Power user productivity; reusable hook pattern |
| Cold start notice + backend wake-up | Handles Render free-tier latency gracefully |
| Skeleton loading states | Professional UX during data fetching |
| Status indicator widget | Real-time API key configuration monitoring |

---

## Key Metrics

- **New database tables**: 3 (briefings, narrative_matches, feedback)
- **New API endpoints**: 5 (quality, narratives, narratives DB, feedback POST, feedback GET)
- **New frontend components**: 11 (QualityBadge, QualityRadarChart, NarrativeTags, FeedbackDialog, TestGuideDialog, KeyboardShortcutsDialog, ColdStartNotice, Skeletons, MetricCard, StatusDistributionChart, StatusIndicator)
- **Modified frontend components**: 5 (ReportViewDialog, RunDetail, RunsTable, App, api.ts)
- **Tests passing**: 56 new (quality: 23, adapters: 22, narratives: 11)
- **New pip dependencies**: 0
- **New npm dependencies**: 0

---

## What Went Well

1. **Additive-only integration** — all changes were additive; existing tables, endpoints, and data untouched; zero-risk rollback via PR revert
2. **Plan-first approach** — the revised Sprint 4 plan (based on actual cddbs-prod architecture exploration) accurately identified all integration points, preventing rework
3. **Dependency discipline** — custom SVG for radar chart and conditional jsonschema import kept the dependency footprint at zero additions
4. **Unplanned UX work adds real value** — feedback system, cold start handling, and keyboard shortcuts address real user pain points discovered during integration
5. **Quality scoring is deterministic** — structural scorer (no LLM calls) means scores are reproducible and fast

## What Could Be Improved

- [ ] Sprint 1 and Sprint 2 retrospectives remain template-only — should be filled in retroactively
- [ ] Plan assumed separate `briefing_id` system; actual implementation simplified to report-linked — plan should have been updated before implementation
- [ ] No integration tests running against real Gemini API — quality scoring only tested with fixtures
- [ ] Feedback system was unplanned scope — should have been a separate ticket
- [ ] Platform adapters (`adapters.py`) copied to production but not wired into the live pipeline — they're only used for testing/research

## Action Items for Sprint 5

| Action | Priority |
|--------|----------|
| Wire platform adapters into live pipeline (Twitter API v2) | High |
| Batch analysis support (multiple outlets in one request) | High |
| Export formats (PDF, JSON, CSV) | Medium |
| End-to-end integration test with real Gemini API | Medium |
| Fill in Sprint 1 and Sprint 2 retrospectives | Low |
| Implement automated monitoring/alerting for analysis failures | Medium |
| Network graph visualization in frontend | Low |

---

## Technical Debt

- Platform adapters exist in production but are orphaned (not called by any pipeline code)
- `Briefing.quality_details` stores the full scorecard JSON — could be normalized into a separate table
- Narrative keyword matching is substring-based (O(n*m)) — may need optimization at scale
- `known_narratives.json` only has `propagation` field on 2 of 18 narratives (Telegram-specific)
- Quality scorer cross-platform bonus is binary — should weight by link confidence score
- Frontend auto-refreshes every 10s when runs are active — should use WebSocket or SSE instead of polling

---

## Sprint 5 Planning Notes

Sprint 5 should focus on operational maturity: making the system usable for real analysts at scale. Key themes:
- **Data ingestion**: Wire Twitter API v2 adapter for direct account analysis (not just SerpAPI news)
- **Batch operations**: Analyze multiple outlets/accounts in a single request
- **Export pipeline**: Generate PDF/JSON/CSV reports for offline sharing
- **Monitoring**: Alert on analysis failures, track quality trends over time
- **Testing**: End-to-end pipeline test with real API keys
