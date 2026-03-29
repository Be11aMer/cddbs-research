# EU Regulatory Landscape for Software Projects

**Last Updated**: 2026-03-18

---

## Overview

Three major EU regulations affect software projects like CDDBS. This document maps how each regulation applies and what practical engineering measures address them.

---

## 1. DSGVO (General Data Protection Regulation / GDPR)

**In force since**: May 25, 2018
**Applies to**: Any system processing personal data of EU residents

### Relevance to CDDBS

CDDBS analyzes publicly available news articles and social media accounts. While the primary data is public, the system touches personal data in several ways:

- **Analyst accounts**: Users of the system (future: authentication in Sprint 8+)
- **Social media handles**: Twitter/Telegram accounts analyzed may belong to identifiable persons
- **Article authors**: News articles may reference or be authored by identifiable persons
- **API keys**: User-provided credentials (SerpAPI, Gemini, Telegram Bot Token)

### Key Principles Applied

| DSGVO Principle | CDDBS Implementation |
|-----------------|---------------------|
| **Data minimization** (Art. 5(1)(c)) | Only store analysis results, not raw personal data; article content stored as metadata, not full text |
| **Purpose limitation** (Art. 5(1)(b)) | Data used exclusively for disinformation analysis; no secondary use |
| **Storage limitation** (Art. 5(1)(e)) | Analysis runs can be deleted; no indefinite retention policy |
| **Security** (Art. 32) | BYOK architecture (keys never stored server-side), HMAC-SHA256 webhooks, environment variable secrets |
| **Privacy by design** (Art. 25) | Architecture designed to minimize PII exposure from Sprint 1 |

---

## 2. EU Cyber Resilience Act (CRA)

**Timeline**:
- Reporting obligations for actively exploited vulnerabilities: **September 2026**
- Core obligations (security requirements, vulnerability handling): **September 2026**
- Full conformity assessment requirements: **September 2027**

### Relevance to CDDBS

The CRA applies to "products with digital elements" placed on the EU market. As an open-source project:

- **If CDDBS is used commercially**: CRA obligations apply to the commercial deployer
- **As open-source**: The CRA exempts non-commercial open-source software, BUT provides obligations for "open-source software stewards" (foundations, maintainers who support commercial use)
- **Practical stance**: We implement CRA-aligned practices regardless of exemption status, because they are good engineering

### Key Requirements & CDDBS Response

| CRA Requirement | CDDBS Implementation |
|-----------------|---------------------|
| **Security by design** (Annex I, Part I) | Input validation on all API endpoints, HMAC webhook signing, environment-variable secrets |
| **Vulnerability handling** (Annex I, Part II) | SECURITY.md with CVE reporting process, 48h acknowledgement SLA |
| **Documentation** (Art. 13) | DEVELOPER.md (45KB), QUICK_START.md, DATABASE_CONNECTION.md, inline code docs |
| **SBOM readiness** (Art. 13(15)) | `requirements.txt` with pinned versions, `package.json` with lockfile; ready for CycloneDX/SPDX generation |
| **Update mechanism** (Art. 10(12)) | Docker-based deployment, semver-tagged releases (v0.5.0–v0.9.0), CHANGELOG.md |
| **No known exploitable vulnerabilities** (Art. 10(4)) | Secret scanning CI, dependency versions reviewed, no hardcoded credentials |
| **Documentation integrity** (Art. 13) | CI documentation drift detection (`scripts/check_docs_drift.py`) ensures docs match code |

---

## 3. EU AI Act

**Timeline**:
- Prohibited AI practices: **February 2, 2025**
- GPAI model obligations: **August 2, 2025**
- High-risk AI system obligations: **August 2, 2026**
- Full application: **August 2, 2027**

### Risk Classification for CDDBS

CDDBS is an **AI-assisted analysis tool** that uses Google Gemini (a GPAI model) to generate intelligence briefings. Risk classification:

| Factor | Assessment |
|--------|-----------|
| **System type** | AI-assisted decision support tool (not autonomous decision-maker) |
| **Domain** | Media analysis / OSINT (not listed as high-risk in Annex III) |
| **Human oversight** | Analyst always reviews AI output; no automated action taken |
| **Risk level** | **Limited risk** — transparency obligations apply, not high-risk requirements |

### Applicable Obligations (Limited Risk)

| EU AI Act Requirement | CDDBS Implementation |
|----------------------|---------------------|
| **Transparency** (Art. 50) | Briefings explicitly state "AI-generated analysis"; confidence scores on every claim; quality scoring rubric transparent |
| **Human oversight** | Analyst reviews all output; feedback system (Sprint 4) allows correction; no automated downstream action |
| **Record keeping** | All analysis runs persisted with timestamps, input parameters, model used, quality scores |
| **GPAI model documentation** | Using Google Gemini (commercial GPAI); Google provides model cards and technical documentation |

### What CDDBS Does NOT Do (Prohibited Practices)

- No social scoring
- No real-time biometric identification
- No manipulation of human behavior
- No exploitation of vulnerabilities of specific groups
- No emotion recognition in workplace/education

---

## Practical Takeaway

The intersection of these three regulations creates a clear engineering mandate:

1. **Minimize personal data** (DSGVO) → BYOK, no PII storage, purpose limitation
2. **Secure the software lifecycle** (CRA) → CI/CD compliance pipeline, vulnerability handling, documentation integrity
3. **Be transparent about AI** (EU AI Act) → Confidence scores, quality rubric, human-in-the-loop design

These are not conflicting requirements — they reinforce each other and produce better software.
