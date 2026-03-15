# Event Intelligence Pipeline Architecture

**Author**: CDDBS Research
**Date**: March 2026
**Status**: Approved for Sprint 6-7 implementation
**Related**: [Sprint 6 Backlog](../docs/sprint_6_backlog.md)

---

## 1. Overview

CDDBS currently uses SerpAPI for per-outlet/per-topic news discovery and a simple GDELT proxy for the monitoring feed. This document designs an **Event Intelligence Pipeline** that transforms the monitoring dashboard from a passive report viewer into an active OSINT event detection system.

The pipeline ingests multiple news sources, deduplicates articles, clusters them into events, detects narrative bursts, and scores coordinated information operation risk.

### Design Principles

1. **Free/low-cost data sources** — RSS feeds (no cost) + GDELT (free) as primary; Currents API (1000 req/day free) as future addition
2. **Lightweight ML** — TF-IDF + cosine similarity instead of neural embeddings (avoids 2GB PyTorch dependency)
3. **Incremental delivery** — Data ingestion first (Sprint 6), intelligence layer second (Sprint 7)
4. **Complement, don't replace** — Event Monitor runs alongside existing outlet/topic analysis

---

## 2. High-Level Architecture

```
Data Sources
   │
   ├── RSS Feeds (wire services, OSINT sources)
   ├── GDELT v2 (structured events, 15-min updates)
   └── [Future: Currents API, social media]
   │
   ▼
Ingestion Layer (async collectors, 3-5 min cycle)
   │
   ▼
Processing Layer
   ├── URL deduplication (SHA-256 hash)
   ├── Content deduplication (TF-IDF cosine similarity)
   ├── Entity extraction (keyword-based)
   └── TF-IDF vectorization
   │
   ▼
Intelligence Layer
   ├── Event clustering (agglomerative clustering on TF-IDF)
   ├── Burst detection (z-score on keyword frequency)
   ├── Narrative risk scoring (multi-signal composite)
   └── Known narrative matching (existing narratives.json)
   │
   ▼
Storage
   ├── PostgreSQL (raw_articles, event_clusters, narrative_bursts)
   └── [Future: vector DB for embedding search]
   │
   ▼
Dashboard (React + MUI)
   ├── Event map (cluster markers on globe)
   ├── Burst timeline (keyword frequency chart)
   ├── Event cluster panel (ranked by risk)
   └── Multi-source intel feed
```

---

## 3. Data Sources

### 3.1 RSS Feeds (Primary — Sprint 6)

RSS is the fastest, most reliable, and cheapest news source for OSINT. Wire services publish via RSS minutes before aggregation APIs.

**Feed categories:**

| Category | Sources | Update Frequency |
|----------|---------|-----------------|
| Wire services | Reuters, AP, AFP | Minutes |
| Global news | BBC World, Al Jazeera, The Guardian | 10-30 min |
| OSINT/Security | Bellingcat, Crisis Group, ReliefWeb | Hours |
| Conflict monitoring | ACLED, The War Zone, Cipher Brief | Hours-Daily |
| Cyber intelligence | Krebs on Security, The Record | Hours |

**Implementation**: `feedparser` library, configurable feed list in `rss_feeds.json`, async collection every 3 minutes.

### 3.2 GDELT Project (Primary — Sprint 6)

Currently proxied as a simple article feed. Enhanced integration adds:

- **GDELT Doc API** — Full-text article search with tone/sentiment analysis
- **GDELT Events** — Structured event records (actor1, action, actor2, location)
- **GDELT GKG** — Global Knowledge Graph with entity extraction

Update frequency: every 15 minutes.

**Key advantages over news APIs:**
- 65,000+ sources in 100+ languages
- Structured event coding (CAMEO taxonomy)
- Tone/sentiment pre-computed
- Completely free, no API key required

### 3.3 Currents API (Future — Sprint 7+)

- 43,000 sources, 90,000 articles/day
- Free tier: 1,000 requests/day
- Good endpoints: `/latest-news`, `/search?q=keyword`, `/category/politics`
- Adds redundancy and broader coverage beyond English-language wire services

### 3.4 Future Social Media Sources

| Source | Signal Value | Difficulty |
|--------|-------------|-----------|
| Reddit API | Early narrative incubation | Medium (API limits) |
| Google Trends | Search interest spikes | Easy (pytrends) |
| Wikipedia edit streams | Event edit spikes | Medium (SSE stream) |
| Telegram channels | Conflict/propaganda | Hard (MTProto) |

---

## 4. Database Schema

### 4.1 raw_articles

Normalized storage for all ingested articles regardless of source.

```sql
CREATE TABLE raw_articles (
    id SERIAL PRIMARY KEY,
    url_hash VARCHAR(64) UNIQUE NOT NULL,  -- SHA-256 of URL
    title VARCHAR NOT NULL,
    url VARCHAR NOT NULL,
    content TEXT,
    source_name VARCHAR,
    source_domain VARCHAR,
    source_type VARCHAR,  -- 'rss', 'gdelt', 'news_api'
    published_at TIMESTAMP,
    language VARCHAR(10),
    country VARCHAR(100),
    raw_meta JSONB,
    cluster_id INTEGER REFERENCES event_clusters(id),
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of INTEGER REFERENCES raw_articles(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_raw_articles_domain ON raw_articles(source_domain);
CREATE INDEX idx_raw_articles_published ON raw_articles(published_at);
CREATE INDEX idx_raw_articles_cluster ON raw_articles(cluster_id);
```

### 4.2 event_clusters

Detected events (groups of related articles).

```sql
CREATE TABLE event_clusters (
    id SERIAL PRIMARY KEY,
    title VARCHAR,
    event_type VARCHAR,  -- conflict, protest, diplomacy, disaster, cyber, info_warfare
    countries JSONB,     -- ["Ukraine", "Russia"]
    entities JSONB,      -- {"people": [], "orgs": [], "locations": []}
    keywords JSONB,      -- ["explosion", "port", "Odessa"]
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    article_count INTEGER DEFAULT 0,
    source_count INTEGER DEFAULT 0,
    burst_score FLOAT DEFAULT 0.0,
    narrative_risk_score FLOAT DEFAULT 0.0,
    status VARCHAR DEFAULT 'active',  -- active, declining, resolved
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4.3 narrative_bursts

Detected keyword/topic frequency spikes.

```sql
CREATE TABLE narrative_bursts (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR NOT NULL,
    baseline_frequency FLOAT,  -- articles/hour (rolling 24h average)
    current_frequency FLOAT,   -- articles/hour (last 1h)
    z_score FLOAT,
    cluster_id INTEGER REFERENCES event_clusters(id),
    detected_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

CREATE INDEX idx_bursts_keyword ON narrative_bursts(keyword);
CREATE INDEX idx_bursts_detected ON narrative_bursts(detected_at);
```

---

## 5. Collector Architecture

### 5.1 Base Collector

```python
@dataclass
class RawArticleData:
    title: str
    url: str
    content: str | None
    source_name: str
    source_domain: str
    source_type: str  # "rss", "gdelt", "news_api"
    published_at: datetime | None
    language: str | None
    country: str | None
    raw_meta: dict

class BaseCollector(ABC):
    @abstractmethod
    async def collect(self) -> list[RawArticleData]: ...

    @property
    @abstractmethod
    def name(self) -> str: ...
```

### 5.2 RSS Collector

- Uses `feedparser` to parse configured feeds
- Runs every 3 minutes
- Extracts: title, link, published date, summary
- Maps feed URL to source metadata (name, domain, category)

### 5.3 GDELT Collector

- Queries GDELT Doc API v2 with disinformation-relevant terms
- Queries GDELT Events for structured event data
- Extracts: title, URL, source, tone, entities, event type
- Caches results for 5 minutes (matching current TTL)

### 5.4 Collector Manager

- Runs all collectors on configurable schedule via asyncio
- Stores results in `raw_articles` table
- Handles errors per-collector (one failure doesn't stop others)
- Reports health status per collector

---

## 6. Processing Pipeline

### 6.1 Deduplication

**Layer 1 — URL exact match:**
SHA-256 hash of normalized URL. If hash exists in `raw_articles.url_hash`, skip.

**Layer 2 — Title similarity:**
For articles within a 24h window, compute TF-IDF cosine similarity on titles. If similarity > 0.85, mark as duplicate and link to original via `duplicate_of`.

### 6.2 Event Clustering

**Algorithm:** Agglomerative clustering on TF-IDF vectors

**Pipeline:**
1. Take non-duplicate articles from last 24 hours
2. Compute TF-IDF matrix on `title + content[:500]`
3. Compute pairwise cosine similarity
4. Agglomerative clustering with `distance_threshold=0.6`
5. Each cluster → `EventCluster` record

**Why agglomerative over HDBSCAN:**
- No heavy dependency (scikit-learn only, already used for TF-IDF)
- Works well with cosine distance
- Deterministic results

**Cluster metadata extraction:**
- Title: most representative article title (closest to centroid)
- Keywords: top TF-IDF terms in cluster
- Countries: extracted from article metadata
- Event type: keyword heuristics mapping (e.g., "protest" → protest, "attack" → conflict)

### 6.3 Burst Detection

**Algorithm:** Rolling z-score on keyword frequency

```python
def detect_bursts(keyword_counts: dict[str, list[float]], window=24, threshold=3.0):
    bursts = []
    for keyword, hourly_counts in keyword_counts.items():
        baseline = hourly_counts[-window:-1]  # last 24h excluding current
        current = hourly_counts[-1]           # last hour

        mean = sum(baseline) / len(baseline)
        std = statistics.stdev(baseline) if len(baseline) > 1 else 1.0
        z = (current - mean) / max(std, 0.1)

        if z > threshold:
            bursts.append(NarrativeBurst(keyword=keyword, z_score=z, ...))
    return bursts
```

Keywords are extracted from article titles via TF-IDF top terms.

### 6.4 Narrative Risk Scoring

Composite score per event cluster (0.0 to 1.0):

```python
risk_score = (
    source_concentration   # 0-1: inverse of source diversity
    + burst_magnitude      # 0-1: normalized z-score
    + timing_sync          # 0-1: article time window concentration
    + narrative_match      # 0-1: overlap with known_narratives.json
) / 4.0
```

**source_concentration**: `1 - (unique_sources / article_count)`. High when many articles from few sources.

**burst_magnitude**: `min(z_score / 10.0, 1.0)`. Normalized burst intensity.

**timing_sync**: `1 - (time_spread_hours / 24.0)`. High when articles published in tight window.

**narrative_match**: `max_confidence` from matching cluster keywords against `known_narratives.json`.

---

## 7. API Endpoints

### New endpoints for event intelligence:

```
GET  /events
     Query: type, country, status, min_risk, limit, offset
     Returns: List of EventCluster with article counts and risk scores

GET  /events/{id}
     Returns: EventCluster with full article list, keyword breakdown, timeline

GET  /events/map
     Returns: Events grouped by country for map visualization

GET  /events/bursts
     Query: min_zscore, active_only
     Returns: List of NarrativeBurst records

GET  /monitoring/feed
     Enhanced: Merges GDELT + RSS articles, sorted by time
     Returns: MonitoringFeedResponse (same format, more items, source badges)

GET  /collector/status
     Returns: Per-collector health (last run, article count, errors)
```

### Modified endpoints:

```
GET  /stats/global
     Add: active_events_count, active_bursts_count to response
```

---

## 8. Frontend Components

### 8.1 New Components

**EventClusterPanel.tsx**
- Lists active event clusters ranked by narrative_risk_score
- Shows: title, event_type chip, countries, article_count, risk score bar
- Click to open EventDetailDialog

**BurstTimeline.tsx**
- Line chart showing keyword frequency over time
- Horizontal threshold line at z=3
- Burst events marked with alert icons
- Filter by keyword

**EventDetailDialog.tsx**
- Full event detail: articles list, source breakdown, timeline
- Narrative risk score breakdown (4 sub-scores)
- Link to create Topic Run from event (bridges to existing Topic Mode)

### 8.2 Modified Components

**MonitoringDashboard.tsx**
- Add metric cards: Active Events, Active Bursts
- Add EventClusterPanel and BurstTimeline panels
- Restructured grid layout

**GlobalMap.tsx**
- Overlay event cluster markers (circles sized by article_count, colored by risk)
- Toggle between analysis heatmap and event markers

**IntelFeed.tsx**
- Show source type badges (RSS, GDELT)
- Add source filter chips
- Display more items from merged feed

**NarrativeTrendPanel.tsx**
- Connect to burst detection data
- Show keyword frequency sparklines

---

## 9. Sprint Mapping

### Sprint 6 (Mar 17-30) — Data Ingestion Layer

| Task | Effort | Priority |
|------|--------|----------|
| DB schema: raw_articles, event_clusters, narrative_bursts | S | P0 |
| BaseCollector + RawArticleData dataclass | S | P0 |
| RSS collector + rss_feeds.json config | M | P0 |
| Enhanced GDELT collector (replace inline proxy) | M | P0 |
| CollectorManager with async scheduling | M | P0 |
| URL deduplication | S | P0 |
| Title similarity dedup (TF-IDF cosine) | M | P1 |
| Enhanced /monitoring/feed (multi-source) | S | P1 |
| /collector/status endpoint | S | P2 |
| IntelFeed.tsx source badges | S | P2 |

### Sprint 7 (Apr 1-14) — Intelligence Layer

| Task | Effort | Priority |
|------|--------|----------|
| TF-IDF event clustering pipeline | L | P0 |
| Burst detection (z-score) | M | P0 |
| Narrative risk scoring | M | P0 |
| /events API endpoints | M | P0 |
| EventClusterPanel.tsx | M | P1 |
| BurstTimeline.tsx | M | P1 |
| EventDetailDialog.tsx | M | P1 |
| Enhanced GlobalMap with event markers | M | P1 |
| Updated MonitoringDashboard layout | S | P1 |
| NarrativeTrendPanel burst integration | S | P2 |

S = Small (< 2h), M = Medium (2-4h), L = Large (4-8h)

---

## 10. Dependencies

### Python packages (add to requirements.txt):

```
feedparser>=6.0           # RSS feed parsing
httpx>=0.27               # Async HTTP for GDELT/API calls
scikit-learn>=1.4         # TF-IDF, cosine similarity, agglomerative clustering
```

Note: `httpx` may already be available. `scikit-learn` is the only significant new dependency (~30MB).

### No new frontend dependencies needed
- Charts can use existing MUI components or simple SVG
- Map already uses react-simple-maps

---

## 11. Integration Points

1. **Collectors → raw_articles**: Independent of existing SerpAPI pipeline
2. **Event clusters → Topic Mode**: Analyst can create a Topic Run from a detected event cluster
3. **Narrative risk scoring → known_narratives.json**: Reuses existing narrative database
4. **Enhanced monitoring/feed → IntelFeed.tsx**: Drop-in replacement, same response format
5. **Event map → GlobalMap.tsx**: Additive overlay on existing country risk map

---

## 12. Future Enhancements (Sprint 8+)

1. **Currents API collector** — Add when RSS + GDELT prove insufficient coverage
2. **Neural embeddings** — Switch to sentence-transformers when Docker size is acceptable
3. **Google Trends integration** — Detect search interest spikes as early warning
4. **Reddit collector** — Monitor subreddits for narrative incubation
5. **Propagation graph** — NetworkX graph showing source → amplifier → mainstream flow
6. **Event cascade detection** — Track event chains (sanctions → protests → violence)
7. **LLM-powered event classification** — Use Gemini for precise CAMEO event coding
8. **Webhook alerts** — Slack/email on high-risk narrative bursts
