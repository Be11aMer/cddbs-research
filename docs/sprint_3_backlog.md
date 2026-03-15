# CDDBS Sprint 3 Backlog

**Sprint**: 3 — Multi-Platform Support
**Duration**: March 3-16, 2026
**Version Target**: v1.3.0
**Predecessor**: Sprint 2 (v1.2.0 — Quality & Reliability)

---

## Sprint Goal

Extend CDDBS beyond Twitter to support Telegram analysis, cross-platform identity correlation, enhanced network analysis, and robust API handling — while keeping all existing tests green.

## Success Criteria

- Schema v1.2.0 supports Telegram-specific fields and cross-platform linking
- Telegram channel/group analysis research documented with platform-specific indicators
- Cross-platform correlation framework defines identity resolution methodology
- Network analysis framework provides graph-based amplification analysis design
- Platform adapter interfaces normalize Twitter and Telegram data into common format
- All existing tests pass (41+) plus new multi-platform tests
- System prompt v1.3 handles both Twitter and Telegram analysis
- API rate limiting design covers Twitter API v2 and Telegram Bot API

---

## Task Breakdown

### 4.1 — Telegram Platform Analysis Research
**Priority**: P0-critical
**Labels**: research
**Estimate**: 5 hours

Research Telegram-specific disinformation patterns, platform architecture, and analysis methodology.

**Subtasks**:
- [ ] Document Telegram platform structure (channels vs groups vs bots)
- [ ] Research Telegram-specific disinformation techniques (forwarding chains, channel networks, bot farms)
- [ ] Identify Telegram-specific behavioral indicators
- [ ] Compare Twitter vs Telegram analysis affordances and limitations
- [ ] Document Telegram API capabilities and data access constraints
- [ ] Review academic literature on Telegram disinformation (DFRLab, Stanford IO)

**Acceptance Criteria**:
- [ ] Research notebook with platform comparison table
- [ ] At least 5 Telegram-specific behavioral indicators identified
- [ ] Data access limitations documented

**Deliverable**: `research/telegram_platform_analysis.ipynb`

---

### 4.2 — Cross-Platform Correlation Framework
**Priority**: P0-critical
**Labels**: research, backend
**Estimate**: 4 hours

Design methodology for linking identities and tracking narratives across platforms.

**Subtasks**:
- [ ] Define identity resolution signals (username matching, bio similarity, content overlap, timing correlation)
- [ ] Create confidence scoring for cross-platform links
- [ ] Document linking evidence types
- [ ] Design cross-platform narrative tracking methodology
- [ ] Address false positive risks and disambiguation

**Acceptance Criteria**:
- [ ] Framework covers at least 4 linking signal types
- [ ] Confidence levels defined for cross-platform identity matches
- [ ] False positive mitigation documented

**Deliverable**: `research/cross_platform_correlation.md`

---

### 4.3 — Network Analysis Enhancement Framework
**Priority**: P1-high
**Labels**: research, backend
**Estimate**: 4 hours

Design graph-based network analysis for amplification pattern detection and community mapping.

**Subtasks**:
- [ ] Define network graph data model (nodes, edges, communities)
- [ ] Design amplification detection algorithms (retweet chains, forwarding paths)
- [ ] Document community detection approaches
- [ ] Define network-level behavioral indicators
- [ ] Design network visualization schema for frontend

**Acceptance Criteria**:
- [ ] Graph model defined with node/edge/community schemas
- [ ] At least 3 network analysis algorithms described
- [ ] Visualization data structure designed

**Deliverable**: `research/network_analysis_framework.md`

---

### 4.4 — Schema Update (v1.2.0)
**Priority**: P0-critical
**Labels**: backend
**Estimate**: 3 hours

Update briefing JSON schema to support multi-platform analysis and enhanced network data.

**Subtasks**:
- [ ] Add `telegram_metadata` optional section (channel_type, subscriber_count, forwarding_metrics)
- [ ] Add `cross_platform_identities` array for identity linking
- [ ] Add `network_graph` structure (nodes, edges, communities)
- [ ] Extend `behavioral_indicators` enum with Telegram-specific types
- [ ] Add `platform_metadata` flexible object for platform-specific fields
- [ ] Ensure all additions are optional (existing fixtures must still validate)

**Acceptance Criteria**:
- [ ] Schema version updated to 1.2.0
- [ ] All 4 existing fixtures still pass validation
- [ ] New Telegram fixture validates successfully
- [ ] New cross-platform fixture validates successfully

**Deliverable**: `schemas/briefing_v1.json` (updated)

---

### 4.5 — Platform Adapter Interfaces
**Priority**: P1-high
**Labels**: backend
**Estimate**: 3 hours

Build platform-specific data normalization interfaces.

**Subtasks**:
- [ ] Design abstract PlatformAdapter interface
- [ ] Implement TwitterAdapter (normalize tweets → common format)
- [ ] Implement TelegramAdapter (normalize messages → common format)
- [ ] Define common BriefingInput dataclass
- [ ] Handle platform-specific fields (forwarding, threading)

**Acceptance Criteria**:
- [ ] Both adapters normalize to common BriefingInput format
- [ ] Platform-specific metadata preserved
- [ ] Unit tests cover both adapters

**Deliverable**: `tools/platform_adapters.py`

---

### 4.6 — Telegram & Cross-Platform Test Fixtures
**Priority**: P0-critical
**Labels**: backend
**Estimate**: 3 hours

Create test briefing fixtures for Telegram channels and cross-platform entities.

**Subtasks**:
- [ ] Create Telegram channel briefing (RT English Telegram channel)
- [ ] Create cross-platform entity briefing (entity present on both Twitter + Telegram)
- [ ] Ensure both validate against updated schema
- [ ] Include Telegram-specific fields (forwarding data, subscriber metrics)

**Acceptance Criteria**:
- [ ] Telegram fixture passes schema validation
- [ ] Cross-platform fixture includes cross_platform_identities
- [ ] Quality scorer produces reasonable scores for both

**Deliverables**: `tests/fixtures/telegram_channel_briefing.json`, `tests/fixtures/cross_platform_briefing.json`

---

### 4.7 — Quality Scorer Update
**Priority**: P1-high
**Labels**: backend, model-quality
**Estimate**: 3 hours

Update quality scorer to handle Telegram-specific and cross-platform data.

**Subtasks**:
- [ ] Handle Telegram behavioral indicators in scoring
- [ ] Add cross-platform scoring bonus (evidence from multiple platforms strengthens assessment)
- [ ] Score network graph completeness (bonus for having graph data)
- [ ] Ensure backward compatibility (existing scores unchanged for existing fixtures)

**Acceptance Criteria**:
- [ ] All existing quality tests still pass
- [ ] Telegram fixture scores reasonably (>= 40)
- [ ] Cross-platform fixture gets cross-platform bonus

**Deliverable**: `tools/quality_scorer.py` (updated)

---

### 4.8 — Known Narratives Update
**Priority**: P2-medium
**Labels**: research
**Estimate**: 2 hours

Add Telegram-specific propagation patterns and fix metadata discrepancy.

**Subtasks**:
- [ ] Fix metadata.total_narratives (says 18, actual is 16)
- [ ] Add `propagation` field to narratives (how they spread on different platforms)
- [ ] Add Telegram-specific narrative examples where applicable
- [ ] Add 2+ new narrative patterns discovered during Telegram research

**Acceptance Criteria**:
- [ ] Metadata matches actual count
- [ ] At least 2 narratives have Telegram-specific propagation info
- [ ] All existing narrative tests still pass

**Deliverable**: `data/known_narratives.json` (updated)

---

### 4.9 — System Prompt v1.3
**Priority**: P1-high
**Labels**: model-quality
**Estimate**: 4 hours

Create multi-platform-aware system prompt with Telegram-specific guidance.

**Subtasks**:
- [ ] Add platform detection instructions (analyze differently based on platform)
- [ ] Add Telegram-specific behavioral indicators section
- [ ] Add cross-platform correlation instructions
- [ ] Update evidence type guidance for Telegram (FORWARD, CHANNEL_META)
- [ ] Add Telegram-specific self-validation checks
- [ ] Keep backward compatibility with Twitter analysis

**Acceptance Criteria**:
- [ ] Prompt handles both Twitter and Telegram analysis
- [ ] Telegram-specific indicators documented
- [ ] Cross-platform correlation guidance included

**Deliverable**: `templates/system_prompt_v1.3.md`

---

### 4.10 — API Rate Limiting Research
**Priority**: P2-medium
**Labels**: research, backend
**Estimate**: 2 hours

Design patterns for handling API rate limits across platform APIs.

**Subtasks**:
- [ ] Document Twitter API v2 rate limits (academic vs basic)
- [ ] Document Telegram Bot API rate limits
- [ ] Design retry/backoff strategy
- [ ] Design request queuing architecture
- [ ] Cost analysis for different API tiers

**Acceptance Criteria**:
- [ ] Rate limit documentation for both platforms
- [ ] Retry strategy designed with exponential backoff
- [ ] Cost estimates for planned analysis volume

**Deliverable**: `research/api_rate_limiting.md`

---

### 4.11 — Test Suite Expansion
**Priority**: P0-critical
**Labels**: backend
**Estimate**: 3 hours

Write tests covering all Sprint 3 additions.

**Subtasks**:
- [ ] Schema validation tests for Telegram fixtures
- [ ] Schema validation tests for cross-platform fixtures
- [ ] Platform adapter unit tests
- [ ] Quality scorer tests for multi-platform briefings
- [ ] Network graph validation tests

**Acceptance Criteria**:
- [ ] All existing 41 tests still pass
- [ ] New tests bring total to >= 60
- [ ] Platform adapter tests cover both Twitter and Telegram

**Deliverables**: Updated `tests/test_schema_validation.py`, `tests/test_quality_scorer.py`, new `tests/test_platform_adapters.py`

---

### 4.12 — CI Pipeline Update
**Priority**: P1-high
**Labels**: backend
**Estimate**: 1 hour

Update CI to validate all Sprint 3 deliverables.

**Subtasks**:
- [ ] Add sprint_3_backlog.md to file existence check
- [ ] Add new fixtures to quality scorer run
- [ ] Ensure platform adapter tests run in pytest

**Deliverable**: `.github/workflows/ci.yml` (updated)

---

### 4.13 — Sprint 3 Retrospective & Documentation
**Priority**: P2-medium
**Labels**: documentation
**Estimate**: 2 hours

**Subtasks**:
- [ ] Create Sprint 3 retrospective template
- [ ] Update README.md with new directory structure and deliverables
- [ ] Update execution plan to reflect Sprint 1+2 completion

**Deliverables**: `retrospectives/sprint_3.md`, `README.md`, `docs/cddbs_execution_plan.md` (all updated)

---

## Sprint 3 Summary

| Task | Priority | Estimate | Deliverable |
|------|----------|----------|-------------|
| 4.1 Telegram Platform Analysis | P0 | 5h | `research/telegram_platform_analysis.ipynb` |
| 4.2 Cross-Platform Correlation | P0 | 4h | `research/cross_platform_correlation.md` |
| 4.3 Network Analysis Framework | P1 | 4h | `research/network_analysis_framework.md` |
| 4.4 Schema Update (v1.2.0) | P0 | 3h | `schemas/briefing_v1.json` |
| 4.5 Platform Adapter Interfaces | P1 | 3h | `tools/platform_adapters.py` |
| 4.6 Test Fixtures (Telegram + XP) | P0 | 3h | `tests/fixtures/` |
| 4.7 Quality Scorer Update | P1 | 3h | `tools/quality_scorer.py` |
| 4.8 Known Narratives Update | P2 | 2h | `data/known_narratives.json` |
| 4.9 System Prompt v1.3 | P1 | 4h | `templates/system_prompt_v1.3.md` |
| 4.10 API Rate Limiting Research | P2 | 2h | `research/api_rate_limiting.md` |
| 4.11 Test Suite Expansion | P0 | 3h | `tests/` |
| 4.12 CI Pipeline Update | P1 | 1h | `.github/workflows/ci.yml` |
| 4.13 Retrospective & Docs | P2 | 2h | retrospective, README, execution plan |
| **Total** | | **39h** | |
