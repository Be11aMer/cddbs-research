# Sprint 3 Execution Context

**Purpose**: Reference file to maintain coherence across Sprint 3 tasks.
**Sprint**: 3 — Multi-Platform Support
**Version Target**: v1.3.0
**Duration**: March 3-16, 2026

---

## What Exists (Sprint 1+2 State)

### Schema (`schemas/briefing_v1.json` — v1.1.0)
- Platform enum already includes: `twitter, telegram, facebook, instagram, youtube, tiktok, vkontakte, other`
- All fixtures use `platform: "twitter"` — no Telegram fixtures yet
- `subject_profile` has: handle, platform, created, followers, following, posts_analyzed, bio, language, verified
- `narrative_analysis.network_context` has: known_associations (string[]), amplification_patterns (string), cross_platform_presence (string[])
- No cross-platform linking structure (no way to link same entity across platforms)
- No Telegram-specific fields (channel vs group, forwarding chains, subscriber count vs follower)

### Quality Scorer (`tools/quality_scorer.py`)
- 7 dimensions, 70 points. All dimension scorers check Twitter-shaped data
- `INDICATOR_TYPES` set includes: posting_frequency, language_patterns, engagement_ratio, coordination_signals, timing_patterns, content_amplification, other
- No Telegram-specific indicators (e.g., forwarding_chain, channel_subscriber_growth, bot_activity)
- No cross-platform scoring dimension

### Known Narratives (`data/known_narratives.json`)
- 7 categories, 16 narratives (metadata says 18 — discrepancy to fix)
- All narrative entries have: id, name, description, keywords, example_claims, source_refs, frequency, first_documented, active
- No platform-specific propagation info (how narratives spread differently on Telegram vs Twitter)

### System Prompt (`templates/system_prompt_v1.2.md`)
- Twitter-centric language throughout
- Evidence types: POST, PATTERN, NETWORK, METADATA, EXTERNAL — all generic enough for multi-platform
- Behavioral indicators reference "posts" not "messages" — need platform-neutral language
- Self-validation checklist is platform-agnostic (good)

### Tests
- 41 tests (22 schema + 19 quality scorer)
- All fixtures are Twitter (@rt_com, @geopolitics_truthseeker, etc.)
- Schema validation tests check `platform` enum already includes "telegram"
- `test_invalid_platform` tests "myspace" → ValidationError

### CI Pipeline (`.github/workflows/ci.yml`)
- Jobs: test, validate, markdown-lint
- Checks: pytest, quality scorer on fixtures, JSON validation, notebook validation, schema structure, narrative dataset, file existence, internal links
- `markdown-lint` checks for: sprint_2_backlog.md — needs update for sprint_3_backlog.md

---

## Sprint 3 Key Decisions

### 1. Schema Evolution Strategy
- **Decision**: Update `schemas/briefing_v1.json` in-place (v1.1.0 → v1.2.0)
- **Rationale**: Still v1 line; no consumers depend on wire compatibility yet
- **Changes needed**:
  - Add `telegram_metadata` optional section (channel/group type, subscriber count, forwarding metrics)
  - Add `cross_platform_references` array to link same entity across platforms
  - Add network graph structure for enhanced network analysis
  - Keep all existing fields as-is (backward compatible)

### 2. Telegram-Specific Indicators
New behavioral indicator types to add:
- `forwarding_chain` — message forwarding analysis
- `channel_growth` — subscriber growth patterns
- `bot_activity` — bot interaction detection
- `message_deletion` — deleted message tracking

### 3. Cross-Platform Identity Resolution
Need a structure like:
```json
"cross_platform_identities": [
  {
    "platform": "telegram",
    "handle": "@rt_english",
    "confidence": "high",
    "linking_evidence": "Bio cross-reference, shared content timing"
  }
]
```

### 4. Network Graph Data Structure
For enhanced network analysis:
```json
"network_graph": {
  "nodes": [{"id": "@rt_com", "platform": "twitter", "role": "source"}],
  "edges": [{"from": "@rt_com", "to": "@SputnikInt", "type": "amplification", "weight": 45}],
  "communities": [{"id": "c1", "label": "Russian state media cluster", "members": ["@rt_com", "@SputnikInt"]}]
}
```

### 5. Platform Adapter Design
- Abstract interface: `PlatformAdapter.normalize(raw_data) → BriefingInput`
- Twitter adapter: maps tweets → posts, followers → followers
- Telegram adapter: maps messages → posts, subscribers → followers, forwarded_from → amplification chain
- This lives in `tools/platform_adapters.py`

---

## Dependency Map

```
sprint_3_backlog.md (planning)
    │
    ├─► research/telegram_platform_analysis.ipynb (research first)
    │       │
    │       ├─► schemas/briefing_v1.json (v1.2.0 — informed by Telegram research)
    │       │       │
    │       │       ├─► tests/fixtures/telegram_channel_briefing.json
    │       │       ├─► tests/fixtures/cross_platform_briefing.json
    │       │       └─► tests/test_schema_validation.py (updated)
    │       │
    │       └─► data/known_narratives.json (add Telegram propagation)
    │
    ├─► research/cross_platform_correlation.md (independent research)
    │       │
    │       └─► tools/platform_adapters.py
    │               │
    │               └─► tests/test_platform_adapters.py
    │
    ├─► research/network_analysis_framework.md (independent research)
    │
    ├─► research/api_rate_limiting.md (independent research)
    │
    ├─► templates/system_prompt_v1.3.md (depends on schema + narratives + research)
    │
    ├─► tools/quality_scorer.py (update — depends on schema changes)
    │       │
    │       └─► tests/test_quality_scorer.py (updated)
    │
    ├─► .github/workflows/ci.yml (update — after all tests written)
    │
    └─► retrospectives/sprint_3.md + README.md (last)
```

---

## File Inventory (Sprint 3 New/Modified)

| File | Action | Notes |
|------|--------|-------|
| `docs/sprint_3_backlog.md` | NEW | Sprint 3 task breakdown |
| `docs/sprint_3_context.md` | NEW | This file |
| `research/telegram_platform_analysis.ipynb` | NEW | Telegram-specific research |
| `research/cross_platform_correlation.md` | NEW | Cross-platform identity resolution |
| `research/network_analysis_framework.md` | NEW | Network analysis design |
| `research/api_rate_limiting.md` | NEW | API rate limiting design |
| `schemas/briefing_v1.json` | MODIFY | v1.1.0 → v1.2.0 |
| `data/known_narratives.json` | MODIFY | Add Telegram propagation + fix metadata |
| `tools/quality_scorer.py` | MODIFY | Add multi-platform + network scoring |
| `tools/platform_adapters.py` | NEW | Platform normalization interfaces |
| `templates/system_prompt_v1.3.md` | NEW | Multi-platform system prompt |
| `tests/fixtures/telegram_channel_briefing.json` | NEW | Telegram channel test fixture |
| `tests/fixtures/cross_platform_briefing.json` | NEW | Cross-platform entity fixture |
| `tests/test_schema_validation.py` | MODIFY | Add Telegram + cross-platform tests |
| `tests/test_quality_scorer.py` | MODIFY | Add multi-platform scoring tests |
| `tests/test_platform_adapters.py` | NEW | Platform adapter tests |
| `.github/workflows/ci.yml` | MODIFY | Add sprint_3_backlog.md check, new fixtures |
| `retrospectives/sprint_3.md` | NEW | Sprint 3 retrospective |
| `README.md` | MODIFY | Update structure + deliverables |
| `docs/cddbs_execution_plan.md` | MODIFY | Mark Sprint 1+2 complete |

---

## Risk Register

| Risk | Mitigation |
|------|------------|
| Schema changes break existing tests | Run all 41 tests after schema update — changes must be additive only |
| Quality scorer changes break existing scores | All new indicators are optional; existing scoring paths unchanged |
| Telegram research has limited web sources | Use known academic sources (Stanford IO, DFRLab) + Telegram API docs |
| Cross-platform correlation is complex | Keep to identity resolution design only; actual implementation in prod |
