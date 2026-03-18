# Sprint 6 Retrospective

**Sprint**: 6 — Scale, Analytics & Event Intelligence
**Duration**: March 14–18, 2026
**Version**: v1.6.0
**Status**: Complete

---

## Sprint Goal

Build a multi-source event intelligence pipeline (RSS + GDELT), wire Telegram into the analysis pipeline, add quality/narrative trend endpoints, implement webhook alerting, and harden the project for open-source release with CI compliance checks.

---

## Delivery Summary

### Event Intelligence Pipeline (Backend)

| Task | Status | Notes |
|------|--------|-------|
| 6.1 DB models: RawArticle, EventCluster, NarrativeBurst | Done | Added to `models.py` (+65 lines) |
| 6.2 BaseCollector ABC + RawArticleData dataclass | Done | `collectors/base.py` (67 lines), SHA-256 URL hash |
| 6.3 RSS collector (feedparser) | Done | `collectors/rss.py` (126 lines), 15 feeds, per-feed error isolation |
| 6.4 Curated RSS feeds JSON | Done | `data/rss_feeds.json` (156 lines), 15 OSINT-grade feeds |
| 6.5 GDELT Doc API v2 collector | Done | `collectors/gdelt.py` (120 lines), async via httpx |
| 6.6 CollectorManager async scheduling | Done | `collectors/manager.py` (152 lines), lifespan integration |
| 6.7 URL deduplication (SHA-256) | Done | UNIQUE constraint on `raw_articles.url_hash` |
| 6.8 TF-IDF title deduplication | Done | `pipeline/deduplication.py` (87 lines), cosine similarity threshold 0.85 |
| 6.9 Enhanced /monitoring/feed | Done | Merges GDELT + RSS, filterable by source_type |
| 6.10 /collector/status endpoint | Done | Per-collector health: runs, stored, last_run, errors |
| 6.11 Add feedparser, httpx, scikit-learn | Done | Also added scipy as transitive dependency |

### Telegram & Trend Detection

| Task | Status | Notes |
|------|--------|-------|
| 6.14 Wire TelegramAdapter into pipeline | Done | `POST /analysis-runs/telegram` + orchestrator routing |
| 6.16 Quality score trends | Done | `GET /trends/quality` — daily avg per outlet |
| 6.17 Narrative frequency trends | Done | `GET /trends/narratives` — top N daily frequencies |

### Webhook Alerting

| Task | Status | Notes |
|------|--------|-------|
| 6.18 Webhook configuration model + endpoint | Done | WebhookConfig model, CRUD + test endpoints |
| 6.19 Alert triggers | Done | HMAC-SHA256 signing, auto-disable after 10 failures |

### Frontend (Partial)

| Task | Status | Notes |
|------|--------|-------|
| 6.12 IntelFeed source badges | Done | Source type badges in monitoring feed |
| 6.13 Updated /stats/global | Done | active_events_count, active_bursts_count added |
| Dashboard visualizations | Done | Activity timeline, narrative bar charts, outlet network graph, annotated article cards |

### Open-Source Hardening & CI Compliance

| Task | Status | Notes |
|------|--------|-------|
| CODEOWNERS | Done | PR review ownership, security-sensitive file escalation |
| Secret scanning CI | Done | `scripts/detect_secrets.py` + `.github/workflows/secret-scan.yml` |
| Documentation drift detection | Done | `scripts/check_docs_drift.py` for EU CRA compliance |
| Branch policy enforcement | Done | `.github/workflows/branch-policy.yml` — only development→main |
| LICENSE (MIT) | Done | MIT License added |
| SECURITY.md | Done | Vulnerability reporting process |
| CONTRIBUTING.md | Done | Branching rules, PR requirements, code style |
| TROUBLESHOOTING.md | Done | Common issues and debugging guide |

### Testing

| Test File | Tests | Coverage |
|-----------|-------|---------|
| `test_collectors.py` | 9 | RawArticleData, RSS, GDELT |
| `test_deduplication.py` | 5 | Identical, near-identical, unique, edge cases |
| `test_webhooks.py` | 7 | HMAC signing, delivery, fire_event |
| `test_trends.py` | 4 | Trends endpoints, global stats, collector status |

**Sprint 6 new tests**: 25
**Estimated total**: ~197 tests passing (132 prod baseline + 25 Sprint 6 + 40 from prior sprint accumulation)

---

## Key Metrics

- **New API endpoints**: 10 (collector/status, monitoring/feed, stats/global, trends/quality, trends/narratives, telegram analysis, webhooks CRUD×3, webhooks test)
- **New DB models**: 4 (RawArticle, EventCluster, NarrativeBurst, WebhookConfig)
- **New pip dependencies**: 4 (feedparser, httpx, scikit-learn, scipy)
- **Docker image size increase**: ~46MB (acceptable)
- **CI workflows**: 3 (ci.yml, branch-policy.yml, secret-scan.yml)
- **Documentation files added/updated**: 7 (CONTRIBUTING, SECURITY, TROUBLESHOOTING, LICENSE, CODEOWNERS, DEVELOPER.md update, CHANGELOG)

---

## What Went Well

1. **Free data sources strategy** — GDELT + RSS eliminates API cost and key management; zero-cost, always-available data ingestion
2. **Lightweight ML choice** — TF-IDF (30MB) instead of sentence-transformers (2GB) keeps Docker lean while providing adequate dedup quality
3. **HMAC-SHA256 webhooks** — Industry-standard approach (matching GitHub's webhook model) that's simple to implement and verify
4. **CI compliance pipeline** — Documentation drift detection + secret scanning + branch policy enforcement create a compliance-ready CI before it's legally required (CRA enforcement summer 2026)
5. **Backfilled retrospectives** — Sprint 1, 2, and 5 retrospectives were filled in, closing documentation debt

---

## What Could Be Improved

- [ ] **Telegram adapter not end-to-end tested** — Endpoint exists and orchestrator routes to it, but no integration test with real Telegram Bot API
- [ ] **EventCluster and NarrativeBurst tables are empty** — Models exist but population requires Sprint 7's clustering/burst detection pipelines
- [ ] **Sprint patches not yet applied to main** — Sprint 4, 5, 6 code exists on branches/patches but the main branch merge sequence hasn't been completed
- [ ] **Frontend components for events deferred** — EventClusterPanel, BurstTimeline, EventDetailDialog pushed to Sprint 7
- [ ] **NetworkGraph.tsx** — Carried from Sprint 5, still not implemented in production

---

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Async collectors | FastAPI lifespan handler | Single process compatible with Render free tier; graceful startup/shutdown |
| RSS parsing | feedparser (sync, wrapped) | 20-year battle-tested library; handles RSS/Atom malformations |
| News API | GDELT Doc API v2 (free) | 65,000+ sources, no API key, structured event coding |
| Deduplication | TF-IDF cosine @ 0.85 | 30MB vs 2GB; sufficient for headline-level dedup |
| URL dedup | SHA-256 hash + UNIQUE constraint | Zero-cost DB-level enforcement |
| Webhook signing | HMAC-SHA256 | Industry standard; simple shared-secret verification |

---

## Sprint 7 Dependencies

Sprint 7 (Intelligence Layer) requires Sprint 6's data ingestion to be running and populated:

| Sprint 7 Task | Sprint 6 Prerequisite |
|---------------|----------------------|
| TF-IDF event clustering | `raw_articles` table with 500+ articles |
| Z-score burst detection | 24h+ of rolling article frequency data |
| EventCluster population | Clustering pipeline reads from raw_articles |
| NarrativeBurst population | Burst detection reads from raw_articles |
| /events API endpoints | event_clusters table populated |

**Minimum data ramp time**: 24-48 hours of collectors running.

---

## Action Items for Sprint 7

| Action | Priority |
|--------|----------|
| Implement TF-IDF event clustering pipeline | Critical |
| Implement z-score burst detection | Critical |
| Implement narrative risk scoring (4-signal composite) | High |
| Build /events API endpoints (list, detail, map, bursts) | High |
| Build EventClusterPanel, BurstTimeline, EventDetailDialog frontend | Medium |
| Enhance GlobalMap with event cluster markers | Medium |
| Update MonitoringDashboard layout | Medium |
| Connect NarrativeTrendPanel to burst data | Low |
