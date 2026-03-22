# Sprint 7 Retrospective

**Sprint**: 7 — Intelligence Layer & Compliance Hardening
**Duration**: March 14–18, 2026 (accelerated — completed ahead of planned Apr 1-14 window)
**Version**: v1.7.0
**Status**: Complete

---

## Sprint Goal

Build the intelligence layer on top of Sprint 6's raw article ingestion: TF-IDF event clustering, z-score burst detection, narrative risk scoring, a full `/events` API, and frontend visualization components. Complete and document all DSGVO/CRA/EU AI Act compliance practices. Verify the full sprint 1-7 delivery with a recursive completeness audit.

---

## Delivery Summary

### Intelligence Pipeline (Backend)

| Task | Status | Notes |
|------|--------|-------|
| 7.1 TF-IDF event clustering pipeline | Done | `pipeline/event_clustering.py` — agglomerative clustering (distance_threshold=0.6), 6 event type classifiers |
| 7.2 Cluster metadata extraction | Done | Representative title, top-5 keywords, country list, event_type via keyword heuristics |
| 7.3 Z-score burst detection | Done | `pipeline/burst_detection.py` — 24h baseline, 1h window, z-score threshold 3.0, writes NarrativeBurst rows |
| 7.4 Narrative risk scoring | Done | `pipeline/narrative_risk.py` — 4-signal composite (source_concentration, burst_magnitude, timing_sync, narrative_match) |
| 7.5 Background scheduler integration | Done | Runs automatically after each collector cycle via CollectorManager |
| 7.6 known_narratives.json integration | Done | narrative_match signal wired into existing narrative matcher |

### Events API Endpoints

| Task | Status | Notes |
|------|--------|-------|
| 7.7 `GET /events` | Done | Filters: type, country, status, min_risk, limit, offset |
| 7.8 `GET /events/{id}` | Done | Full detail with article list, keyword breakdown, source diversity, timeline |
| 7.9 `GET /events/map` | Done | Country-grouped events with risk scores for map visualization |
| 7.10 `GET /events/bursts` | Done | Active NarrativeBurst records with linked cluster info, min_zscore filter |

### Frontend Intelligence Components

| Task | Status | Notes |
|------|--------|-------|
| 7.11 `EventClusterPanel.tsx` | Done | Ranked clusters by narrative_risk_score with title, type chip, countries, article count, risk bar |
| 7.12 `BurstTimeline.tsx` | Done | Keyword frequency spikes ranked by z-score, threshold indicator, frequency bars |
| 7.13 `EventDetailDialog.tsx` | Done | Full event detail with articles, source breakdown, publication timeline, 4-signal risk breakdown |
| 7.14 Enhanced `GlobalMap.tsx` | Done | Countries with active events get highlighted borders, tooltips with event count and risk score |
| 7.15 Updated `MonitoringDashboard.tsx` | Done | 4-panel bottom row: Event Clusters, Burst Timeline, Active Narratives, Country Risk Index |
| 7.16 `NarrativeTrendPanel.tsx` burst integration | Done | Connected to burst detection data |

### Testing

| Test File | Tests | Coverage |
|-----------|-------|---------|
| `test_event_clustering.py` | 12 | Classification, cluster creation, edge cases, metadata extraction |
| `test_burst_detection.py` | 14 | Z-score, hourly frequencies, spike detection, threshold boundary, edge cases |
| `test_narrative_risk.py` | 23 | All 4 risk signals independently, composite score, edge cases (single source, zero articles) |
| `test_events_api.py` | 13 | List with filters, detail, map grouping, bursts list, pagination, empty states |

**Sprint 7 new tests**: 62
**Total passing**: 204

### Documentation & Compliance

| Task | Status | Notes |
|------|--------|-------|
| 7.22 DEVELOPER.md update | Done | New sections for event clustering, burst detection, risk scoring, /events endpoints |
| 7.23 CHANGELOG.md | Done | v2026.03.1 release notes |
| 7.24 Sprint 7 integration log | Done | Covered in CHANGELOG.md |
| 7.25 Compliance practices documentation | Done | 7 documents in `compliance-practices/` |
| 7.26 Execution plan update | Done | Sprint 6 marked complete, Sprint 7 current |
| 7.29 Recursive completeness audit | Done | **PASSED** 2026-03-18 |

### Deferred Items

| Task | Notes |
|------|-------|
| 7.27 NetworkGraph.tsx production implementation | Carried Sprint 5→6→7→8; will be Sprint 8 task |
| 7.28 Currents API collector | Low priority; RSS + GDELT coverage sufficient |
| Sprint 7 retrospective | This document — deferred to sprint close |

---

## Key Metrics

- **New API endpoints**: 4 (`/events`, `/events/{id}`, `/events/map`, `/events/bursts`)
- **New pipeline modules**: 3 (`event_clustering.py`, `burst_detection.py`, `narrative_risk.py`)
- **New frontend components**: 3 (`EventClusterPanel.tsx`, `BurstTimeline.tsx`, `EventDetailDialog.tsx`)
- **Frontend components enhanced**: 2 (`GlobalMap.tsx`, `MonitoringDashboard.tsx`)
- **New tests**: 62 across 4 files
- **Total test suite**: 204 tests passing
- **Compliance documents produced**: 7 (`compliance-practices/` folder)
- **New dependencies**: 0 — scikit-learn and scipy already added in Sprint 6
- **Audit status**: PASSED (all 6 audit categories clear)

---

## What Went Well

1. **Zero new dependencies** — All Sprint 7 ML capabilities (TF-IDF clustering, z-score, cosine similarity) used scikit-learn and scipy added in Sprint 6. Docker image size unchanged, no new attack surface.
2. **Thorough risk scoring decomposition** — 4-signal composite (source_concentration, burst_magnitude, timing_sync, narrative_match) is independently interpretable. Analysts can see which signals drove a risk score, not just the final number.
3. **Recursive completeness audit as a discipline** — Task 7.29 made it operationally impossible to close the sprint with undocumented work. The audit caught the retrospective gap and deferred it explicitly rather than silently skipping it.
4. **Test depth on narrative risk** — 23 tests for narrative_risk.py covering every signal independently, composite score, and edge cases (zero articles, single source). This is the most analytically critical module and got the most coverage.
5. **Compliance documentation now reusable** — The 7 compliance practice documents in `compliance-practices/` are not sprint-specific; they document the architecture decisions that can be referenced in a formal assessment (CRA enforcement summer 2026).

---

## What Could Be Improved

- [ ] **NetworkGraph.tsx** — Carried for three consecutive sprints (5→6→7→8). Needs a dedicated, unambiguous Sprint 8 slot or a decision to drop it permanently.
- [ ] **EventClusterPanel and BurstTimeline not end-to-end tested with real cluster data** — Unit tests use mock DB state. Integration testing requires collectors to have run 24-48h to populate meaningful clusters. This should be validated in a staging environment before v1.7.0 is considered production-ready.
- [ ] **Z-score threshold discrepancy** — Backlog specified default 2.5, implementation used 3.0. Configurable via environment variable, but the discrepancy between spec and implementation should be documented.
- [ ] **Sprint patches not tracked as formal artifacts** — `patches/sprint7_production_changes.patch` was planned but not confirmed. Patch export should be automated in CI rather than a manual post-sprint step.

---

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Clustering algorithm | Agglomerative (distance_threshold=0.6) | No need to pre-specify cluster count; threshold approach handles variable article volumes |
| Burst detection window | 24h baseline / 1h current | Long baseline smooths weekend/timezone effects; 1h window catches emerging spikes early |
| Risk score design | 0-1 composite, 4 additive signals | Interpretable components; no black-box score |
| Pipeline trigger | After each collector cycle | Avoids a separate scheduler; uses existing CollectorManager lifecycle |
| Event type classification | Keyword heuristics (6 types) | Lightweight, inspectable, no additional model call; suitable for MVP intelligence layer |

---

## Vision Alignment

Sprint 7 completes the transition from **reactive** (analyst-initiated analysis) to **proactive** (automated event detection):

- Sprints 1-5: Analyst submits a URL → system produces a briefing
- Sprint 6: System ingests articles continuously from 15+ feeds
- Sprint 7: System clusters articles into events, detects narrative bursts, scores risk — without analyst input

This evolution is on-mission. The core purpose — "analyzing media outlets and social media accounts for potential disinformation activity" — is served by surfacing emerging narrative clusters before an analyst knows to ask about them.

**No feature creep detected.** All Sprint 7 components serve intelligence analysis for disinformation detection.

---

## Action Items for Sprint 8

| Action | Priority |
|--------|----------|
| Implement Topic Mode (topic-centric multi-outlet comparative analysis) | Critical |
| Implement NetworkGraph.tsx production visualization | High |
| Generate SBOM in CI (CycloneDX format) | High |
| Automated dependency vulnerability scanning (pip-audit in CI) | High |
| User-facing AI disclosure panel in frontend | Medium |
| Validate event clustering and burst detection with 48h of live collector data | Medium |
| Currents API collector | Low |
