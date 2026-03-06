# Sprint 6 Backlog — Scale, Analytics & Event Intelligence

**Sprint**: 6 (Mar 17-30, 2026)
**Target**: v1.6.0
**Status**: Planning
**Related**: [Event Intelligence Pipeline](../research/event_intelligence_pipeline.md)

---

## Sprint Goals

1. **Event Intelligence Pipeline** — Multi-source news ingestion with event clustering and burst detection
2. **Telegram Bot API** — Wire TelegramAdapter into pipeline (carried from original roadmap)
3. **Trend detection** — Quality and narrative trends over time
4. **Webhook alerting** — Slack/email on failure spikes

---

## Event Intelligence Pipeline (NEW — from News API research)

### P0 — Core Data Ingestion

| # | Task | Effort | Owner |
|---|------|--------|-------|
| 6.1 | Add DB models: `RawArticle`, `EventCluster`, `NarrativeBurst` to `models.py` | S | — |
| 6.2 | Create `src/cddbs/collectors/base.py` — `BaseCollector` ABC + `RawArticleData` dataclass | S | — |
| 6.3 | Create `src/cddbs/collectors/rss.py` — RSS feed collector using feedparser | M | — |
| 6.4 | Create `src/cddbs/data/rss_feeds.json` — 15 curated OSINT-grade RSS feeds | S | — |
| 6.5 | Create `src/cddbs/collectors/gdelt.py` — Enhanced GDELT collector (Doc API v2 + Events) | M | — |
| 6.6 | Create `src/cddbs/collectors/manager.py` — CollectorManager with async scheduling | M | — |
| 6.7 | URL deduplication (SHA-256 hash on raw_articles.url_hash) | S | — |

### P1 — Processing & API

| # | Task | Effort | Owner |
|---|------|--------|-------|
| 6.8 | Create `src/cddbs/pipeline/deduplication.py` — Title similarity dedup (TF-IDF cosine) | M | — |
| 6.9 | Enhanced `/monitoring/feed` endpoint — merge GDELT + RSS articles | S | — |
| 6.10 | `/collector/status` endpoint — per-collector health reporting | S | — |
| 6.11 | Add `feedparser`, `httpx`, `scikit-learn` to requirements.txt | S | — |

### P2 — Frontend

| # | Task | Effort | Owner |
|---|------|--------|-------|
| 6.12 | Update `IntelFeed.tsx` — source type badges, source filter chips | S | — |
| 6.13 | Update `/stats/global` — add active_events_count, active_bursts_count | S | — |

---

## Original Sprint 6 Items (from execution plan)

### Telegram Bot API Integration

| # | Task | Effort | Owner |
|---|------|--------|-------|
| 6.14 | Wire TelegramAdapter into analysis pipeline | L | — |
| 6.15 | Telegram channel analysis endpoints | M | — |

### Trend Detection

| # | Task | Effort | Owner |
|---|------|--------|-------|
| 6.16 | Quality score trends over time (per-outlet time series) | M | — |
| 6.17 | Narrative frequency trends (top narratives over time) | M | — |

### Webhook Alerting

| # | Task | Effort | Owner |
|---|------|--------|-------|
| 6.18 | Webhook configuration model and endpoint | M | — |
| 6.19 | Alert triggers (pipeline failure, high-risk narrative burst) | M | — |

---

## Sprint 7 Preview — Intelligence Layer

These tasks build on Sprint 6 data ingestion:

- TF-IDF event clustering pipeline
- Z-score burst detection on keyword frequency
- Narrative risk scoring (4-signal composite)
- `/events` API endpoints (list, detail, map, bursts)
- `EventClusterPanel.tsx`, `BurstTimeline.tsx`, `EventDetailDialog.tsx`
- Enhanced `GlobalMap.tsx` with event cluster markers
- Restructured `MonitoringDashboard.tsx` layout

---

## Acceptance Criteria

### Event Intelligence Pipeline
- [ ] RSS collector fetches articles from 15+ feeds every 3-5 minutes
- [ ] GDELT collector fetches articles with structured event data every 5 minutes
- [ ] URL deduplication prevents duplicate storage (same URL never stored twice)
- [ ] Title dedup catches near-identical articles from different sources (>85% similarity)
- [ ] `/monitoring/feed` returns merged articles from all sources with source badges
- [ ] `/collector/status` reports health of each collector
- [ ] All collectors handle errors gracefully (one failure doesn't stop others)

### Original Items
- [ ] Telegram analysis can be triggered from the frontend
- [ ] Quality trends chart shows score evolution per outlet
- [ ] Webhook fires on pipeline failure

---

## Tech Stack Additions

| Package | Purpose | Size |
|---------|---------|------|
| `feedparser>=6.0` | RSS feed parsing | ~100KB |
| `httpx>=0.27` | Async HTTP client | ~500KB |
| `scikit-learn>=1.4` | TF-IDF, clustering, similarity | ~30MB |

No neural network dependencies (PyTorch/sentence-transformers deferred to future sprint).

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| RSS feeds may change URLs or go offline | Monitor collector health, fallback to remaining feeds |
| GDELT API may rate limit | 5-minute cache TTL, exponential backoff |
| TF-IDF clustering quality insufficient | Can upgrade to sentence-transformers in Sprint 8+ |
| scikit-learn adds Docker image size | ~30MB is acceptable; much less than PyTorch (2GB) |
| Collector scheduling conflicts with pipeline | Collectors run in separate background tasks, no shared state |

---

## Definition of Done

- All P0 tasks completed and tested
- Collectors running in Docker alongside existing services
- No regression in existing outlet/topic analysis functionality
- Monitoring dashboard shows multi-source feed
- Research documentation updated in cddbs-research-draft
