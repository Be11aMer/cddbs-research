# Sprint-by-Sprint Compliance Log

**Last Updated**: 2026-03-28
**Purpose**: Track what compliance-relevant measures were implemented in each sprint

---

## Sprint 1: Briefing Format Redesign (Feb 3-16, 2026)

### Compliance Measures Implemented

| Measure | Regulation | Description |
|---------|-----------|-------------|
| BYOK architecture | DSGVO Art. 32 | API keys stored only in environment variables, never persisted |
| Confidence framework | EU AI Act Art. 50 | Three-tier confidence (HIGH/MODERATE/LOW) in AI output |
| AI-generated labeling | EU AI Act Art. 50 | System prompt instructs model to identify output as AI-generated |
| JSON schema validation | CRA Art. 13 | Structured output validated against JSON Schema draft-07 |
| .gitignore for secrets | DSGVO Art. 32 | .env and credential files excluded from version control |
| Data minimization | DSGVO Art. 5(1)(c) | Only structured briefing results stored, not raw API responses |

### Key Decision
Architecture designed privacy-first from day one. BYOK means the server never possesses user credentials.

---

## Sprint 2: Quality & Reliability (Feb 17 - Mar 2, 2026)

### Compliance Measures Implemented

| Measure | Regulation | Description |
|---------|-----------|-------------|
| 70-point quality rubric | EU AI Act Art. 50 | Independent, deterministic quality assessment of AI output |
| 7-dimension scoring | EU AI Act | Structural completeness, attribution, confidence, evidence, rigor, actionability, readability |
| Known narrative dataset | EU AI Act | Reference dataset for detecting disinformation patterns |
| Source verification framework | EU AI Act | 5 evidence types for claim verification |
| 41 automated tests | CRA Annex I | Automated quality assurance on every change |

### Key Decision
Quality scoring is **structural and deterministic** — no AI in the scoring loop. This provides an independent validation layer.

---

## Sprint 3: Multi-Platform Support (Mar 3-16, 2026)

### Compliance Measures Implemented

| Measure | Regulation | Description |
|---------|-----------|-------------|
| Platform adapters | DSGVO Art. 5(1)(c) | Normalize social media data to minimal required fields |
| API rate limiting design | CRA Art. 10(4) | Respect platform rate limits to avoid service disruption |
| Cross-platform correlation | EU AI Act | Framework for verifying claims across multiple platforms |
| 80 tests total | CRA Annex I | Expanded test coverage for new platform adapters |

### Key Decision
Platform adapters normalize data at ingestion — personal data fields are stripped to the minimum needed for analysis.

---

## Sprint 4: Production Integration (Mar 1-3, 2026)

### Compliance Measures Implemented

| Measure | Regulation | Description |
|---------|-----------|-------------|
| Research-to-production integration | CRA Art. 10(6) | Controlled transfer of research modules to production codebase |
| Feedback system | EU AI Act | Analyst feedback loop for correcting AI output |
| Additive-only changes | CRA Art. 10(4) | Zero-risk rollback; no existing functionality modified |
| 56 new production tests | CRA Annex I | Quality, adapter, and narrative matching tests |
| Zero new dependencies | CRA Art. 10(4) | Custom SVG instead of recharts; minimized attack surface |

### Key Decision
All Sprint 1-3 research was transferred to production as **additive-only** changes. No existing tables, endpoints, or data were modified. This supports the CRA's requirement for controlled change management.

---

## Sprint 5: Operational Maturity (Mar 3-16, 2026)

### Compliance Measures Implemented

| Measure | Regulation | Description |
|---------|-----------|-------------|
| Exponential backoff | CRA Art. 10(4) | Twitter client implements production-grade rate limiting from day one |
| Operational metrics endpoint | CRA Art. 13 | `GET /metrics` provides system health visibility |
| Export formats (JSON/CSV/PDF) | EU AI Act | Enable offline review and auditing of AI-generated briefings |
| Developer documentation | CRA Art. 13 | 812-line developer guide covering full architecture |
| 169 tests total | CRA Annex I | Comprehensive automated quality assurance |

### Key Decision
Export functionality (JSON/CSV/PDF) supports the EU AI Act's record-keeping requirements — analysis results can be exported, archived, and audited independently of the running system.

---

## Sprint 6: Scale, Analytics & Event Intelligence (Mar 14-18, 2026)

### Compliance Measures Implemented

| Measure | Regulation | Description |
|---------|-----------|-------------|
| **Secret scanning CI** | DSGVO Art. 32, CRA Art. 10(4) | `secret-scan.yml` + `detect_secrets.py` prevents credential leaks |
| **Documentation drift detection** | CRA Art. 13 | `check_docs_drift.py` ensures docs match code |
| **Branch policy enforcement** | CRA Art. 10(6) | `branch-policy.yml` enforces development→main flow |
| **CODEOWNERS** | CRA Art. 10(6) | Mandatory review for security-sensitive files |
| **SECURITY.md** | CRA Annex I, Part II | Vulnerability reporting process, 48h acknowledgement SLA |
| **CONTRIBUTING.md** | CRA Art. 13 | Contributor guidelines with security requirements |
| **LICENSE (MIT)** | CRA Art. 13 | Clear open-source licensing |
| **HMAC-SHA256 webhooks** | DSGVO Art. 32 | Cryptographic payload signing for webhook delivery |
| **SBOM-ready dependencies** | CRA Art. 13(15) | Pinned versions in requirements.txt ready for CycloneDX |
| **~197 tests total** | CRA Annex I | Expanded coverage including collectors, dedup, webhooks |

### Key Decision
Sprint 6 was the **compliance hardening sprint**. The CI pipeline gained three compliance-specific workflows (secret scan, docs drift, branch policy) that run on every push and PR. This is the most significant compliance investment in the project's history.

---

## Sprint 7: Intelligence Layer (Mar 14-18, 2026) — COMPLETE

### Compliance Measures Implemented

| Measure | Regulation | Description |
|---------|-----------|-------------|
| Compliance practices documentation | All | 7 documents in `compliance-practices/` covering DSGVO, CRA, EU AI Act |
| Recursive completeness audit | CRA Art. 13 | Task 7.29 PASSED — all code tested, documented, gap-free |
| Vision alignment check | CRA Art. 10(6) | Sprints 1-7 verified on-mission — no drift detected |
| Updated execution plan | CRA Art. 13 | Sprint 6 marked complete, Sprint 7 current, architecture updated |
| CHANGELOG update | CRA Art. 13 | v2026.03.1 release notes with all Sprint 7 features |
| 62 new tests (204 total) | CRA Annex I | Event clustering, burst detection, risk scoring, events API tests |
| Risk scoring interpretability | EU AI Act Art. 50 | 4-signal decomposition; analysts see which signals drive each risk score |

### Key Decision
Sprint 7 is the first sprint where all compliance measures were **documented before implementation** via this compliance-practices folder. This folder now serves as a reusable reference for any formal regulatory assessment.

---

## Sprint 8: Topic Mode & Supply Chain Security (Mar 22-28, 2026) — COMPLETE

### Compliance Measures Implemented

| Measure | Regulation | Description |
|---------|-----------|-------------|
| **SBOM generation in CI** | CRA Art. 13(15) | CycloneDX `sbom.json` generated on every push to main/development via `sbom.yml`; uploaded as 90-day CI artifact; BSI TR-03183-2 compatible format |
| **Dependency vulnerability scanning** | CRA Art. 10(4) | pip-audit in CI (`ci.yml` vulnerability-scan job); fails on actionable HIGH/CRITICAL CVEs (non-empty fix_versions); unfixable CVEs logged as notices |
| **AI provenance disclosure** | EU AI Act Art. 50 | `AIProvenanceCard.tsx` — tiered disclosure: badge showing model ID + prompt version, expandable provenance detail with quality score and legal text; replaces generic "Experimental" alert |
| **Machine-readable AI metadata** | EU AI Act Art. 50 | `ai_metadata` object in `GET /analysis-runs/{id}` response: model_id, prompt_version, quality_score, requires_human_review, disclosure text |
| **Topic Mode transparency** | EU AI Act Art. 50 | Divergence scores (0-100) are deterministic and inspectable; coordination signal computation documented; methodology in DEVELOPER.md Section 15 |
| **Supply chain hardening** | CRA Art. 10(4) | All GitHub Actions pinned to commit SHAs (mitigates GhostAction-style supply chain attacks on CI); `cyclonedx-bom` and `pip-audit` added to `requirements.txt` |
| **Coordination signal detection** | EU AI Act Art. 50 | Post-analysis computation flags coordinated narrative clusters (outlets sharing ≥2 propaganda techniques at divergence ≥60); score + detail stored and surfaced in UI |
| **10 new tests** | CRA Annex I | `test_sprint8_topic_innovations.py` — coordination logic, key claims/omissions storage, API schema completeness, ai_metadata structure validation |

### Key Decision
Sprint 8 closes three compliance gaps simultaneously: (1) SBOM generation moves from "ready" to "done" (CRA Art. 13(15)), (2) AI disclosure moves from system-prompt-level to user-facing UI (EU AI Act Art. 50), (3) supply chain integrity via SHA-pinned Actions and vulnerability scanning. The coordination signal detection is an innovation beyond the original backlog — it surfaces potential coordinated disinformation campaigns, directly serving the project mission.

---

## Compliance Maturity Timeline

```
Sprint 1 ─── Privacy by Design (BYOK, data minimization, confidence framework)
    │
Sprint 2 ─── Quality Assurance (70-point rubric, automated testing)
    │
Sprint 3 ─── Data Normalization (platform adapters, rate limiting)
    │
Sprint 4 ─── Controlled Integration (research→prod transfer, feedback loop)
    │
Sprint 5 ─── Operational Maturity (metrics, export, documentation)
    │
Sprint 6 ─── CI Compliance Pipeline (secret scan, docs drift, branch policy, SECURITY.md)
    │
Sprint 7 ─── Documentation & Audit (compliance practices, recursive verification) ✓ COMPLETE
    │
Sprint 8 ─── SBOM artifact, vulnerability scanning, AI provenance UI, supply chain hardening ✓ COMPLETE
    │
Sprint 9 ─── AI trust framework, information security, compliance automation  ← CURRENT
```

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Sprints with compliance measures | 8/8 (100%) |
| Automated CI compliance checks | 6 (secret scan, docs drift, branch policy, lint, SBOM, pip-audit) |
| Test count | 214 (Sprint 8 complete: 204 + 10 new) |
| Documentation pages | 10+ production docs, 16+ sprint docs, 5 blog posts, 7 compliance docs |
| Security-specific files | SECURITY.md, CODEOWNERS, detect_secrets.py, secret-scan.yml, sbom.yml |
| DSGVO measures | 6 (BYOK, minimization, purpose limitation, no tracking, secret protection, webhook signing) |
| CRA measures | 10 (secret scan, docs drift, branch policy, SBOM generation, pip-audit, SECURITY.md, documentation, SHA-pinned Actions, version tags, change control) |
| EU AI Act measures | 7 (confidence framework, quality rubric, human oversight, record keeping, AI labeling, AI provenance UI, coordination signal transparency) |
