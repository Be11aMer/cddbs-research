# Sprint 6 Context File

**Sprint**: 6 — Scale, Analytics & Event Intelligence
**Date**: 2026-03-14
**Status**: Implementation complete — patch exported

---

## Session Summary

This session (March 14, 2026) completed the following:

### Backfilled Missing Work
1. **Sprint 1 retrospective** — Filled in from template stub (beta feedback, metrics, delivery summary)
2. **Sprint 2 retrospective** — Filled in from template stub (quality scorer scores, test metrics, narrative dataset)
3. **Sprint 5 retrospective** — Created from scratch (was entirely missing from the repo)

### Sprint 6 Implementation
4. **Sprint 6 production patch** — `patches/sprint6_production_changes.patch` (1,828 lines, 17 files)
5. **Sprint 6 integration log** — `docs/sprint_6_integration_log.md`
6. **Sprint 6 research notebook** — `notebooks/experiments/sprint_6_event_intelligence.ipynb`

---

## Production State Going Into Sprint 6

### cddbs-prod main branch (as of March 14)
- Sprint 1-3: Merged to main (research modules, quality scorer, adapters)
- Sprint 4: ON REMOTE BRANCHES (not merged to main)
  - `feature/sprint-4-integration`
  - `feature/sprint-4b-frontend-ux`
  - `feature/test-guide-and-feedback` ← contains all Sprint 4 work
- Sprint 5: Patch ready but not applied (`patches/sprint5_production_changes.patch`)
- Sprint 6: Patch ready (`patches/sprint6_production_changes.patch`)

### Required Merge Order
```
main ← feature/test-guide-and-feedback   (Sprint 4 — all of it)
     ← sprint5_production_changes.patch   (Sprint 5)
     ← sprint6_production_changes.patch   (Sprint 6)
```

---

## Sprint 6 Architecture Decisions

### Decision 1: Async collectors in FastAPI lifespan
**Choice**: Start CollectorManager in the FastAPI `@asynccontextmanager lifespan` handler
**Why**: Allows graceful startup/shutdown without a separate worker process; compatible with Render free tier (single process)
**Trade-off**: If the FastAPI process crashes, collection stops until restart

### Decision 2: feedparser over httpx for RSS
**Choice**: feedparser for RSS parsing (synchronous)
**Why**: feedparser handles the full range of RSS/Atom malformations gracefully; battle-tested for 20 years
**Trade-off**: Synchronous — wrapped with `asyncio.create_task` at the collector level; collector runs in event loop but feedparser itself blocks briefly (~100ms per feed)

### Decision 3: GDELT over NewsAPI/Currents
**Choice**: GDELT Doc API v2 as the second collector (no API key, completely free)
**Why**: 65,000+ sources, pre-computed tone/sentiment, structured event coding; no daily request limits
**Trade-off**: No full article text; only metadata + URL

### Decision 4: TF-IDF over sentence-transformers
**Choice**: TF-IDF cosine similarity (scikit-learn) at threshold=0.85
**Why**: ~30MB dependency vs 2GB for PyTorch/sentence-transformers; sufficient for headline-level dedup
**Trade-off**: Misses semantic similarity ("Russia attacks Ukraine" ≈ "Moscow strikes Kyiv"); acceptable for Sprint 6; revisit in Sprint 8+

### Decision 5: SHA-256 URL hash as primary dedup
**Choice**: Primary dedup is SHA-256 hash of URL stored in `raw_articles.url_hash` (UNIQUE constraint)
**Why**: Zero-cost, database-level enforcement, prevents duplicate storage at insert time
**Complement**: TF-IDF is secondary — catches cross-source reprints of the same story

### Decision 6: Webhook HMAC-SHA256 (not JWT)
**Choice**: HMAC-SHA256 signature in `X-CDDBS-Signature` header
**Why**: Industry standard (GitHub webhooks use same approach); receiver can verify without a key exchange protocol
**Trade-off**: Shared secret must be configured out-of-band; no expiry mechanism (not needed for server-to-server)

---

## Dependency Additions (Sprint 6)

| Package | Version | Reason | Docker size impact |
|---------|---------|---------|-------------------|
| feedparser | ≥6.0.11 | RSS parsing | ~100KB |
| httpx | ≥0.27.0 | Async HTTP for GDELT | ~500KB |
| scikit-learn | ≥1.4.0 | TF-IDF deduplication | ~30MB |
| scipy | ≥1.13.0 | scikit-learn dependency | ~15MB |

Total Docker image size increase: ~46MB (acceptable; much less than PyTorch at 2GB)

---

## Sprint 7 Dependencies (Requires Sprint 6 Data)

Sprint 7 (April 1-14, 2026) is the Intelligence Layer. It requires Sprint 6's data ingestion to be running and populated before Sprint 7 can produce meaningful results.

| Sprint 7 Task | Requires |
|---------------|---------|
| TF-IDF event clustering | `raw_articles` table with 500+ articles |
| Z-score burst detection | 24h+ of rolling article frequency data |
| `EventCluster` population | Clustering pipeline to run and write results |
| `NarrativeBurst` population | Burst detection to run and write results |
| `/events` API endpoints | `event_clusters` table populated |
| `EventClusterPanel.tsx` | `/events` API working |

**Minimum data ramp time**: 24-48 hours of collectors running before Sprint 7 intelligence tasks are meaningful.

---

## File Inventory Added This Session

```
retrospectives/sprint_1.md          — FILLED IN (was template stub)
retrospectives/sprint_2.md          — FILLED IN (was template stub)
retrospectives/sprint_5.md          — CREATED (was missing entirely)
patches/sprint6_production_changes.patch — CREATED (1828 lines, 17 files)
docs/sprint_6_integration_log.md    — CREATED
docs/sprint_6_context.md            — CREATED (this file)
notebooks/experiments/sprint_6_event_intelligence.ipynb — CREATED
```
