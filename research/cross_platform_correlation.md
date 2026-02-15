# Cross-Platform Correlation Framework

**Sprint**: 3 — Multi-Platform Support
**Version**: 1.0
**Status**: Complete
**Purpose**: Methodology for linking identities and tracking narratives across platforms

---

## 1. Overview

Cross-platform correlation is the process of identifying when the same actor operates accounts on multiple platforms (e.g., Twitter + Telegram) and tracking how narratives propagate across platform boundaries. This is critical for CDDBS because disinformation operations rarely confine themselves to a single platform.

### Why Cross-Platform Analysis Matters

- **Attribution strengthening**: Linking accounts across platforms provides additional evidence dimensions
- **Narrative tracing**: Narratives often originate on one platform and spread to others
- **Network completeness**: Single-platform analysis misses coordination happening elsewhere
- **Evasion detection**: Actors may move to different platforms to evade detection

---

## 2. Identity Resolution Signals

### 2.1 Signal Taxonomy

| Signal Type | Description | Confidence Contribution | False Positive Risk |
|------------|-------------|------------------------|-------------------|
| **Username match** | Identical or near-identical handles | Medium | High (common names) |
| **Bio cross-reference** | Bio explicitly links to other platform | High | Low |
| **Content overlap** | Same content posted within time window | High | Medium (shared sources) |
| **Timing correlation** | Posting times correlated across platforms | Medium | Medium |
| **Visual identity** | Same profile photo/banner | Medium-High | Low (if verified) |
| **URL cross-reference** | Shared links in bios or posts | High | Low |
| **Network overlap** | Same accounts in interaction network | Medium | Medium |
| **Writing style** | Consistent linguistic patterns | Medium | High (stylistic overlap) |

### 2.2 Signal Scoring

Each signal contributes to a composite confidence score:

```
Cross-Platform Link Confidence = weighted_sum(signals) / max_possible

Weights:
  bio_cross_reference:    0.25  (highest — explicit self-declaration)
  url_cross_reference:    0.20  (strong — deliberate linking)
  content_overlap:        0.20  (strong — same content, timed)
  visual_identity:        0.15  (good — but can be stolen)
  username_match:         0.10  (weak alone — many false positives)
  timing_correlation:     0.05  (supporting evidence only)
  network_overlap:        0.05  (supporting evidence only)
```

### 2.3 Confidence Thresholds

| Confidence Level | Composite Score | Minimum Signals | Description |
|-----------------|----------------|-----------------|-------------|
| **High** | >= 0.70 | 3+ signals, at least 1 bio/URL | Strong evidence of same entity |
| **Moderate** | 0.40 - 0.69 | 2+ signals | Probable same entity, some ambiguity |
| **Low** | 0.20 - 0.39 | 1-2 weak signals | Possible link, needs investigation |
| **Unlinked** | < 0.20 | 0-1 weak signals | Insufficient evidence |

---

## 3. Identity Resolution Procedures

### 3.1 Automated Matching

**Step 1: Username normalization**
```
normalize(handle):
  - Strip platform prefixes (@, t.me/, etc.)
  - Lowercase
  - Remove underscores, dots, hyphens
  - Strip trailing numbers (may be disambiguation)

Example: "@RT_com" → "rtcom"
         "t.me/rt_english" → "rtenglish"
```

**Step 2: Candidate generation**
- Exact normalized match across platforms
- Levenshtein distance <= 2 on normalized names
- Bio text contains other platform handle
- Shared URLs in profile

**Step 3: Candidate scoring**
- For each candidate pair, compute signal scores per Section 2.2
- Rank by composite confidence
- Flag pairs above "Low" threshold for review

### 3.2 Manual Verification Checklist

For candidates above "Low" confidence:

- [ ] Profile photos visually compared (reverse image search if needed)
- [ ] Bio text cross-references verified (not just similar — actually links)
- [ ] Content overlap verified as original (not both quoting same source)
- [ ] Timing correlation checked (are they posting the same thing at similar times, or just following the same news cycle?)
- [ ] Network overlap assessed (do they interact with the same accounts, or just the same public figures?)

### 3.3 False Positive Mitigation

| False Positive Source | Mitigation |
|----------------------|------------|
| Common usernames (e.g., "news_daily") | Require 2+ signals beyond username match |
| Shared content from same source | Check if content is identical (copy-paste) vs. similar (same topic) |
| Fan accounts mimicking official | Look for platform verification, account age, follower asymmetry |
| Name squatting / impersonation | Check account creation dates, content consistency over time |
| Parody accounts | Look for parody indicators in bio, content tone |

---

## 4. Cross-Platform Narrative Tracking

### 4.1 Narrative Propagation Patterns

**Pattern A: Broadcast → Amplification**
```
Kremlin announcement → RT.com article → @rt_com (Twitter) → Telegram channels → Facebook groups
                                      ↳ RT Telegram channel ↗
```

**Pattern B: Telegram-First**
```
Anonymous Telegram channel → screenshot shared on Twitter → blog posts → mainstream coverage
```

**Pattern C: Platform Arbitrage**
```
Content banned on Twitter → reposted on Telegram → screenshot circulated on Twitter as "censored truth"
```

### 4.2 Temporal Analysis

- **Time-to-spread**: How quickly does content appear on other platforms after initial posting?
- **Coordination window**: If content appears within 5 minutes on multiple platforms, likely coordinated (same operator or coordinated campaign)
- **News cycle vs. coordination**: Content appearing 2-24 hours apart may be organic spread; <5 minutes suggests coordination

### 4.3 Content Fingerprinting

For tracking the same narrative across platforms:

1. **Exact text match**: Same text posted verbatim (strongest signal)
2. **URL sharing**: Same URLs shared across platforms
3. **Image/media match**: Same images (perceptual hashing for near-duplicates)
4. **Semantic similarity**: Same talking points in different words (requires NLP)
5. **Translation patterns**: Same content in different languages across platforms

---

## 5. CDDBS Schema Integration

### 5.1 Cross-Platform Identity in Briefing

```json
"cross_platform_identities": [
  {
    "platform": "telegram",
    "handle": "@rt_english",
    "confidence": "high",
    "linking_evidence": "Bio explicitly states 'Follow us on Telegram: t.me/rt_english'; content overlap >95% within 10-minute windows; same visual branding",
    "briefing_id": "d4e5f6a7-8b9c-0d1e-2f3a-4b5c6d7e8f9a"
  },
  {
    "platform": "youtube",
    "handle": "RT",
    "confidence": "high",
    "linking_evidence": "Verified YouTube channel linked from RT.com; same organizational branding; content from same editorial pipeline"
  }
]
```

### 5.2 Cross-Platform Network Edges

```json
"network_graph": {
  "edges": [
    {
      "from": "@rt_com",
      "to": "@rt_english_tg",
      "type": "amplification",
      "weight": 450,
      "cross_platform": true
    }
  ]
}
```

---

## 6. Limitations

- **API access asymmetry**: Twitter API provides richer metadata than Telegram Bot API
- **Temporal gaps**: Not all platforms provide precise timestamps for historical data
- **Privacy constraints**: Some platforms don't expose follower/subscriber lists
- **Scale**: Cross-platform matching is O(n*m) where n,m are account counts per platform
- **Evasion**: Sophisticated actors may deliberately avoid cross-platform linking signals
- **Language barriers**: Multi-language content complicates semantic matching

---

## 7. Implementation Roadmap

| Phase | Scope | Sprint |
|-------|-------|--------|
| **Design** (current) | Framework, methodology, schema | Sprint 3 |
| **Manual** | Analyst-driven cross-platform linking | Sprint 4 |
| **Semi-automated** | Candidate generation + manual review | Sprint 5 |
| **Automated** | Full pipeline with confidence scoring | Sprint 7+ |

---

## References

- Graphika: "Secondary Infektion" report (2020) — cross-platform tracking methodology
- Stanford Internet Observatory: EIP cross-platform analysis framework
- DFRLab: "Pillars of Russia's Disinformation" ecosystem mapping
- Bellingcat: Open-source cross-platform investigation techniques
- Meta Threat Intelligence: CIB takedown reports with cross-platform analysis
