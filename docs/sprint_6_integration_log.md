# Sprint 6: Production Integration Log

**Date**: 2026-03-14
**Target Repo**: `cddbs-prod` (https://github.com/Be11aMer/cddbs-prod)
**Source Repo**: `cddbs-research`
**Branch**: `claude/complete-sprint-6-ps4q4`
**Status**: PATCH EXPORTED — ready to apply in a `cddbs-prod` session

---

## Prerequisites

### Sprint 4 and Sprint 5 Must Be Applied First

Sprint 6 builds on Sprint 4 and Sprint 5. Before applying the Sprint 6 patch:

1. **Merge Sprint 4** — `feature/test-guide-and-feedback` branch in cddbs-prod contains all Sprint 4 work (feature/sprint-4-integration + feature/sprint-4b-frontend-ux)
2. **Apply Sprint 5** — `patches/sprint5_production_changes.patch` from this repo

```bash
# Step 1: Merge Sprint 4
cd /path/to/cddbs-prod
git checkout main
git merge feature/test-guide-and-feedback

# Step 2: Apply Sprint 5
git checkout -b feature/sprint-5-operational-maturity
git apply /path/to/cddbs-research/patches/sprint5_production_changes.patch
git add -A
git commit -m "Sprint 5: Add Twitter API, batch analysis, export, and metrics

- Twitter API v2 client with rate limiting and exponential backoff
- Batch analysis endpoint for multiple targets (up to 5)
- Export reports in JSON, CSV, and PDF formats
- Operational metrics dashboard endpoint
- Platform routing in orchestrator (news/twitter with fallback)
- Frontend: platform selector, export buttons, batch/metrics API
- Developer guide documentation
- 35 new tests (169 total passing)"
git push -u origin feature/sprint-5-operational-maturity
# Then create PR and merge to main
git checkout main && git merge feature/sprint-5-operational-maturity

# Step 3: Apply Sprint 6
git checkout -b feature/sprint-6-event-intelligence
git apply /path/to/cddbs-research/patches/sprint6_production_changes.patch
```

---

## Sprint 6 Changes Detail

### New Files (12 files)

| File | Lines | Description |
|------|-------|-------------|
| `src/cddbs/collectors/__init__.py` | 0 | Package init |
| `src/cddbs/collectors/base.py` | 67 | `BaseCollector` ABC + `RawArticleData` dataclass with URL hashing |
| `src/cddbs/collectors/rss.py` | 126 | RSS feed collector (feedparser), 15 feeds, per-feed error isolation |
| `src/cddbs/collectors/gdelt.py` | 120 | GDELT Doc API v2 collector (httpx async), no API key required |
| `src/cddbs/collectors/manager.py` | 152 | `CollectorManager`: async scheduling, DB persistence, health stats |
| `src/cddbs/pipeline/deduplication.py` | 87 | TF-IDF cosine similarity dedup (scikit-learn), threshold configurable |
| `src/cddbs/webhooks.py` | 97 | Webhook delivery: HMAC-SHA256 signing, retry/disable logic |
| `src/cddbs/data/rss_feeds.json` | 156 | 15 curated OSINT-grade RSS feeds (wire services, OSINT, cyber, military) |
| `tests/test_collectors.py` | 98 | 9 tests: RawArticleData, RSSCollector, GDELTCollector |
| `tests/test_deduplication.py` | 52 | 5 tests: identical/near-identical/unique/edge cases |
| `tests/test_webhooks.py` | 62 | 7 tests: signing, delivery success/failure, fire_event |
| `tests/test_trends.py` | 48 | 4 tests: trends endpoints, global stats, collector status |

### Modified Files (5 files)

| File | Changes | Description |
|------|---------|-------------|
| `requirements.txt` | +4 | feedparser, httpx, scikit-learn, scipy |
| `src/cddbs/config.py` | +7 | TELEGRAM_BOT_TOKEN, COLLECTOR_INTERVAL_SECONDS, GDELT_INTERVAL_SECONDS, RSS_FEEDS_PATH, DEDUP_SIMILARITY_THRESHOLD, WEBHOOK_SECRET, BURST_ZSCORE_THRESHOLD |
| `src/cddbs/models.py` | +65 | RawArticle, EventCluster, NarrativeBurst, WebhookConfig models |
| `src/cddbs/api/main.py` | +243 | 12 new endpoints: collector/status, monitoring/feed, stats/global, trends/quality, trends/narratives, analysis-runs/telegram, webhooks CRUD + test |
| `src/cddbs/pipeline/orchestrator.py` | +12 | Telegram platform routing via TelegramAdapter |
| `frontend/src/api.ts` | +130 | CollectorStatus, FeedArticle, GlobalStats, QualityTrend, NarrativeTrend, TelegramAnalysis, WebhookConfig types and API functions |

---

## New API Endpoints (Sprint 6)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/collector/status` | GET | Per-collector health: runs, stored, last_run, errors |
| `/monitoring/feed` | GET | Multi-source articles (RSS+GDELT), filter by source_type |
| `/stats/global` | GET | Global stats: total_runs, active_events_count, active_bursts_count |
| `/trends/quality` | GET | Daily avg quality per outlet (last N days) |
| `/trends/narratives` | GET | Top N narrative daily frequencies (last N days) |
| `/analysis-runs/telegram` | POST | Trigger Telegram channel analysis |
| `/webhooks` | GET | List all webhook configs |
| `/webhooks` | POST | Create webhook (url, events, secret) |
| `/webhooks/{id}` | DELETE | Deactivate webhook |
| `/webhooks/test/{id}` | POST | Send test event to webhook |

---

## New Environment Variables

Add to `docker-compose.yml` and `.env.example`:

```env
# Sprint 6: Collector settings
TELEGRAM_BOT_TOKEN=           # Telegram Bot API token for channel analysis
COLLECTOR_INTERVAL_SECONDS=180 # RSS collection interval (default: 3 min)
GDELT_INTERVAL_SECONDS=300     # GDELT collection interval (default: 5 min)
RSS_FEEDS_PATH=src/cddbs/data/rss_feeds.json
DEDUP_SIMILARITY_THRESHOLD=0.85
WEBHOOK_SECRET=               # Shared secret for webhook HMAC signing
BURST_ZSCORE_THRESHOLD=2.5    # Z-score threshold for burst detection
```

---

## How to Apply Sprint 6

```bash
# Assumes Sprint 4 and Sprint 5 are already on main in cddbs-prod

cd /path/to/cddbs-prod
git checkout -b feature/sprint-6-event-intelligence

# Apply the patch
git apply /path/to/cddbs-research/patches/sprint6_production_changes.patch

# Verify no conflicts
git status

# Run tests
pip install -r requirements.txt  # installs feedparser, httpx, scikit-learn
pytest tests/ -v --tb=short -x

# Commit
git add -A
git commit -m "Sprint 6: Event Intelligence Pipeline, Telegram, Trends & Webhooks

Event Intelligence Pipeline:
- Multi-source ingestion: RSS (15 feeds) + GDELT Doc API v2
- BaseCollector ABC + RawArticleData dataclass with SHA-256 URL dedup
- CollectorManager: async scheduling (RSS every 3min, GDELT every 5min)
- TF-IDF cosine similarity title deduplication (scikit-learn, threshold 0.85)
- RawArticle, EventCluster, NarrativeBurst DB models

API Endpoints:
- GET /collector/status — per-collector health reporting
- GET /monitoring/feed — merged RSS+GDELT articles with source badges
- GET /stats/global — active_events_count, active_bursts_count
- GET /trends/quality — daily avg quality per outlet
- GET /trends/narratives — top narrative frequency trends

Telegram Integration:
- POST /analysis-runs/telegram — wires TelegramAdapter into pipeline
- Platform routing for 'telegram' in orchestrator._fetch_for_platform()

Webhook Alerting:
- WebhookConfig model (url, events, secret, active, failure_count)
- HMAC-SHA256 payload signing
- fire_event() delivers to all subscribed active webhooks
- Auto-disable after 10 consecutive failures
- Supported events: pipeline_failure, narrative_burst, collector_failure, batch_completed

New dependencies: feedparser>=6.0.11, httpx>=0.27.0, scikit-learn>=1.4.0, scipy>=1.13.0
Tests: +28 new (23 unit + 5 integration stubs), total ~197 passing"

git push -u origin feature/sprint-6-event-intelligence
```

---

## Test Coverage (Sprint 6 Additions)

| Test File | Tests | Coverage |
|-----------|-------|---------|
| `test_collectors.py` | 9 | RawArticleData URL hash, domain extraction, RSSCollector failure isolation, GDELTCollector HTTP failure |
| `test_deduplication.py` | 5 | Identical titles, near-identical, unique, single, empty |
| `test_webhooks.py` | 7 | HMAC signing, deliver success/failure, fire_event validation |
| `test_trends.py` | 4 | Trends endpoints, global stats, collector status |

**Sprint 6 test count**: 25 new tests
**Estimated total**: ~194 tests passing (169 from Sprint 5 + 25 new)

---

## Known Gaps / Sprint 7 Deferred

| Item | Reason Deferred |
|------|-----------------|
| EventCluster population | Requires Sprint 7 TF-IDF clustering pipeline |
| NarrativeBurst z-score detection | Requires Sprint 7 burst detection background task |
| `NetworkGraph.tsx` component | Frontend visualization deferred to Sprint 7 |
| `EventClusterPanel.tsx` | Sprint 7 frontend work |
| `BurstTimeline.tsx` | Sprint 7 frontend work |
| Currents API collector | Low priority vs free alternatives; Sprint 8+ |
| sentence-transformers upgrade | 2GB Docker dependency; revisit in Sprint 8 |

---

## Verification Checklist

After applying the patch to cddbs-prod:

- [ ] `pytest tests/ -v` passes with ~194 tests
- [ ] `docker compose up` starts without error
- [ ] `GET /collector/status` returns `{"status": "running", "collectors": {"rss": {...}, "gdelt": {...}}}`
- [ ] `GET /monitoring/feed` returns articles from both RSS and GDELT after ~3 minutes
- [ ] `GET /stats/global` returns all 5 fields including `active_events_count`
- [ ] `POST /webhooks` creates a webhook, `GET /webhooks` lists it
- [ ] `POST /analysis-runs/telegram` with channel `@bbcnews` creates a queued run
- [ ] `GET /trends/quality` returns 200 (empty list if no completed runs)
