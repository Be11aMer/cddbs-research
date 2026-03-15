# Network Analysis Enhancement Framework

**Sprint**: 3 — Multi-Platform Support
**Version**: 1.0
**Status**: Complete
**Purpose**: Graph-based amplification analysis, community detection, and network visualization design

---

## 1. Network Model

### 1.1 Graph Data Model

CDDBS models the information environment around a subject as a directed, weighted, multi-type graph.

**Nodes** represent accounts/entities:
```
Node {
  id:        string   // account handle (unique within platform)
  platform:  enum     // twitter, telegram, facebook, ...
  role:      enum     // subject, source, amplifier, target, peer, unknown
  label:     string   // display name
  metadata:  object   // platform-specific fields (follower count, etc.)
}
```

**Edges** represent interactions:
```
Edge {
  from:    string   // source node ID
  to:      string   // target node ID
  type:    enum     // retweet, reply, mention, forward, quote, follow, amplification
  weight:  integer  // interaction count (how many times this interaction occurred)
  period:  object   // {start, end} — time range of observed interactions
}
```

**Communities** represent detected clusters:
```
Community {
  id:       string    // cluster identifier
  label:    string    // descriptive name
  members:  string[]  // node IDs
  cohesion: float     // 0-1 internal edge density
}
```

### 1.2 Edge Types by Platform

| Edge Type | Twitter | Telegram | Description |
|-----------|---------|----------|-------------|
| `retweet` | Retweet/Repost | — | Direct content republishing |
| `reply` | Reply thread | Group message reply | Direct response |
| `mention` | @mention | @mention | Tagging another account |
| `forward` | — | Message forward | Telegram forwarding chain |
| `quote` | Quote tweet | — | Repost with commentary |
| `follow` | Follow relationship | Channel subscription | Persistent connection |
| `amplification` | Aggregated promotion | Aggregated forwarding | Composite metric |

---

## 2. Network Analysis Algorithms

### 2.1 Centrality Measures

**Degree Centrality** — Number of connections
- **Use**: Identify most-connected nodes (hubs)
- **CDDBS application**: Accounts with highest degree are likely key nodes in amplification network
- **Formula**: `C_d(v) = deg(v) / (n - 1)`
- **Threshold**: Nodes with degree > 2 standard deviations above mean flagged as potential hubs

**Betweenness Centrality** — Bridge detection
- **Use**: Identify accounts that bridge different communities
- **CDDBS application**: High betweenness = potential "bridge" between state media and organic audiences
- **Formula**: `C_b(v) = Σ (σ_st(v) / σ_st)` for all s,t pairs
- **Significance**: Proxy accounts often have high betweenness — they connect official sources to organic spread

**PageRank** — Influence measure
- **Use**: Rank nodes by influence (weighted by influence of connected nodes)
- **CDDBS application**: Identifies most influential accounts in the amplification network
- **Note**: Works well for Twitter retweet networks; adapted for Telegram forwarding chains

### 2.2 Community Detection

**Louvain Algorithm** (recommended primary)
- **Method**: Modularity optimization via greedy aggregation
- **Pros**: Fast (O(n log n)), works well on large networks, produces hierarchical communities
- **Cons**: Resolution limit (may miss small communities), non-deterministic
- **CDDBS use**: Primary community detection for identifying coordinated groups

**Label Propagation**
- **Method**: Iterative label spreading based on majority neighbor labels
- **Pros**: Very fast, no parameters to tune
- **Cons**: Non-deterministic, may produce trivial solutions
- **CDDBS use**: Quick preliminary clustering for large networks

**Infomap**
- **Method**: Information-theoretic flow-based community detection
- **Pros**: Detects overlapping communities, flow-based (good for directed networks)
- **Cons**: Slower than Louvain
- **CDDBS use**: When directed relationships (who amplifies whom) matter more than symmetric ties

### 2.3 Coordinated Inauthentic Behavior (CIB) Detection

**Temporal Coordination Score**
```
For each pair of accounts (a, b):
  - Extract posting timestamps for matching content
  - Compute average time delta: Δt = mean(|t_a - t_b|) for shared content
  - If Δt < 5 minutes for >50% of shared content: HIGH coordination signal
  - If Δt < 30 minutes for >30%: MODERATE coordination signal
```

**Content Similarity Matrix**
```
For each pair of accounts (a, b):
  - Compute Jaccard similarity of shared URLs
  - Compute cosine similarity of posting content (TF-IDF vectors)
  - High similarity (>0.7) + temporal correlation = CIB indicator
```

**Behavioral Synchronization**
- Same posting schedule (daily/weekly patterns)
- Simultaneous activity bursts
- Coordinated topic shifts
- Identical response patterns to news events

---

## 3. Telegram-Specific Network Analysis

### 3.1 Forwarding Chain Analysis

Telegram's forwarding metadata is uniquely valuable — every forwarded message retains its source channel:

```
Message {
  forward_from_chat: Channel  // source of the forward
  forward_date: datetime      // when original was posted
  views: integer              // how many saw this message
}
```

**Forwarding chain reconstruction**:
```
Original post (Channel A)
  → Forwarded to Channel B (10 min later, 50K views)
    → Forwarded to Channel C (25 min later, 12K views)
    → Forwarded to Channel D (30 min later, 8K views)
  → Forwarded to Channel E (2 hours later, 100K views)
```

**Metrics**:
- **Forwarding depth**: How many hops from original source
- **Forwarding breadth**: How many channels forward from the same source
- **Time-to-forward**: Average delay from source to first forward
- **Amplification ratio**: Total downstream views / original views

### 3.2 Channel Network Topology

Telegram channel networks exhibit distinctive patterns:

| Pattern | Description | Significance |
|---------|-------------|--------------|
| **Star** | One source, many amplifiers | Central control (state media pattern) |
| **Chain** | Linear forwarding path | Content laundering pipeline |
| **Mesh** | Dense mutual forwarding | Coordinated network |
| **Hub-and-spoke** | Few hubs, many receivers | Typical organic spread |

### 3.3 Bot Detection in Telegram

- **Instant forwarding** (<1 second from source): Likely automated
- **24/7 activity**: No human sleep patterns
- **No original content**: 100% forwarded messages
- **Subscriber growth spikes**: Artificial inflation
- **Generic channel names**: "News_Daily_123" pattern

---

## 4. Cross-Platform Network Mapping

### 4.1 Unified Graph Construction

When an entity operates on multiple platforms, the network graph spans platforms:

```
[Twitter] @rt_com ──retweet──▶ @SputnikInt
     │                              │
     │ (cross-platform link)        │ (cross-platform link)
     ▼                              ▼
[Telegram] @rt_english ──forward──▶ @sputnik_channel
     │
     └──forward──▶ @geopolitics_daily (proxy)
```

**Rules for cross-platform edges**:
1. Cross-platform edges have type `amplification` (aggregated)
2. Weight = estimated content overlap count
3. Confidence inherits from the cross-platform identity link confidence

### 4.2 Multi-Platform Metrics

**Cross-Platform Amplification Score**:
```
XP_Amp(entity) = Σ platforms × Σ downstream_reach_per_platform / total_platforms

Higher XP_Amp = entity successfully amplifies across multiple platforms
```

**Platform Diversification Index**:
```
PDI = 1 - Σ (share_per_platform)²   (Herfindahl-Hirschman inverse)

PDI near 0: concentrated on one platform
PDI near 1: evenly spread across many platforms
```

---

## 5. Visualization Schema

### 5.1 JSON Structure for Frontend

The `network_graph` field in the briefing schema supports frontend rendering:

```json
{
  "network_graph": {
    "nodes": [
      {"id": "@rt_com", "platform": "twitter", "role": "subject", "label": "RT"},
      {"id": "@SputnikInt", "platform": "twitter", "role": "peer", "label": "Sputnik"},
      {"id": "@rt_english", "platform": "telegram", "role": "subject", "label": "RT English"},
      {"id": "@proxy_1", "platform": "telegram", "role": "amplifier", "label": "Geopolitics Daily"}
    ],
    "edges": [
      {"from": "@rt_com", "to": "@SputnikInt", "type": "retweet", "weight": 45},
      {"from": "@rt_english", "to": "@proxy_1", "type": "forward", "weight": 230},
      {"from": "@rt_com", "to": "@rt_english", "type": "amplification", "weight": 450}
    ],
    "communities": [
      {
        "id": "c1",
        "label": "Russian state media cluster",
        "members": ["@rt_com", "@SputnikInt", "@rt_english"]
      },
      {
        "id": "c2",
        "label": "Proxy amplification network",
        "members": ["@proxy_1"]
      }
    ]
  }
}
```

### 5.2 Visualization Recommendations

| Layout | Use Case | Library |
|--------|----------|---------|
| Force-directed | General network overview | D3.js, Cytoscape.js |
| Hierarchical | Forwarding chains, amplification paths | Dagre, ELK |
| Circular | Community comparison | Cytoscape.js |
| Geographic | When location data available | Leaflet + D3 |

**Color encoding**:
- Node color by platform (Twitter=blue, Telegram=blue-gradient, etc.)
- Node size by influence (PageRank or follower count)
- Edge color by type (retweet=green, forward=orange, mention=gray)
- Edge thickness by weight
- Community indicated by background hull/cluster highlight

---

## 6. Implementation Notes

### 6.1 Recommended Libraries (Python)

| Library | Purpose | Notes |
|---------|---------|-------|
| `networkx` | Graph construction, centrality, community detection | Standard, well-documented |
| `python-louvain` | Louvain community detection | Fast, integrates with networkx |
| `cdlib` | Advanced community detection (Infomap, etc.) | Research-grade algorithms |
| `pyvis` | Interactive network visualization | Quick prototyping |

### 6.2 Scale Considerations

| Network Size | Approach | Notes |
|-------------|----------|-------|
| < 100 nodes | networkx in-memory | Fine for single-account analysis |
| 100-10K nodes | networkx with optimization | May need sparse representations |
| > 10K nodes | graph database (Neo4j) | Production-grade for large campaigns |

### 6.3 Data Collection for Network Construction

**Twitter**: Retweet/quote/reply endpoints → edges. Follower/following → edges. User lookup → node metadata.

**Telegram**: `getForwardedFrom` in messages → forwarding edges. Channel mentions in messages → mention edges. No native "follow" edge API; subscription is private.

---

## 7. Quality Scoring Integration

Network analysis contributes to the quality scorer in two ways:

1. **Evidence presentation bonus**: Having network graph data adds richness to evidence (+1-2 points)
2. **Analytical rigor**: Multi-dimensional analysis (content + behavioral + network) is the gold standard for high-confidence assessments

The quality scorer should award bonus points when:
- `network_graph.nodes` has >= 3 nodes
- `network_graph.edges` has >= 3 edges
- `network_graph.communities` has >= 1 community
- Multiple evidence types including `network` are used in findings

---

## References

- Graphika: "Spamouflage" report — network mapping methodology
- Stanford Internet Observatory: "Robust Network Analysis" techniques
- DFRLab: "Botnet Takedowns" — CIB detection through network analysis
- Louvain method: Blondel et al., "Fast unfolding of communities in large networks" (2008)
- Infomap: Rosvall & Bergstrom, "Maps of random walks on complex networks" (2008)
- GEC: "Pillars" report — ecosystem mapping as network analysis
