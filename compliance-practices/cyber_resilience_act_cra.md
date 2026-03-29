# Cyber Resilience Act (CRA) Compliance Practices

**Last Updated**: 2026-03-18
**Implemented Across**: Sprints 1-6 (hardened in Sprint 6)
**Regulation**: Regulation (EU) 2024/2847 on horizontal cybersecurity requirements for products with digital elements
**Enforcement**: Reporting obligations Sep 2026, core obligations Sep 2026, full conformity Sep 2027

---

## Why This Matters Now

The CRA's first enforcement deadline is **September 2026** — months away. While CDDBS as an open-source project may qualify for exemptions, implementing CRA-aligned practices now:

1. Prepares for potential commercial deployment
2. Establishes reusable engineering patterns
3. Demonstrates security-by-design commitment
4. Creates documentation artifacts useful for any future audit

---

## CRA Requirements Mapped to CDDBS Practices

### 1. Security by Design (Annex I, Part I)

**Requirement**: Products must be designed, developed, and produced to ensure an appropriate level of cybersecurity.

| CRA Expectation | CDDBS Implementation | Evidence |
|-----------------|---------------------|----------|
| Delivered without known exploitable vulnerabilities | Secret scanning CI prevents credential leaks; dependency versions reviewed | `.github/workflows/secret-scan.yml` |
| Secure by default configuration | No default passwords; all secrets via environment variables; collectors fail gracefully | `src/cddbs/config.py` |
| Protection against unauthorized access | HMAC-SHA256 webhook signing; future auth planned for Sprint 8+ | `src/cddbs/webhooks.py` |
| Minimize attack surface | No admin endpoints exposed; API validates all inputs; no debug mode in production | `src/cddbs/api/main.py` |
| Data protection and confidentiality | BYOK architecture; no PII storage; data minimization | See `data_protection_dsgvo.md` |

### 2. Vulnerability Handling (Annex I, Part II)

**Requirement**: Manufacturers must have effective vulnerability handling processes.

| CRA Expectation | CDDBS Implementation | Evidence |
|-----------------|---------------------|----------|
| Documented vulnerability handling process | SECURITY.md with reporting process, scope, response timeline | `SECURITY.md` |
| Timely security updates | Docker-based deployment allows rapid patching; semver-tagged releases | `Dockerfile`, `v0.9.0` tag |
| Public disclosure mechanism | GitHub Security Advisories; SECURITY.md provides contact | `SECURITY.md` |
| SBOM (Software Bill of Materials) | `requirements.txt` with versions; `package.json` with lockfile; ready for CycloneDX generation | `requirements.txt`, `frontend/package.json` |
| Reporting of actively exploited vulnerabilities | Process documented; GitHub issues for tracking | `SECURITY.md` |

### 3. Technical Documentation (Art. 13)

**Requirement**: Manufacturers must draw up technical documentation before placing the product on the market.

| CRA Expectation | CDDBS Implementation | Evidence |
|-----------------|---------------------|----------|
| Product description and intended use | README.md, DEVELOPER.md project overview | `README.md` (line 1-50) |
| Design and development information | DEVELOPER.md architecture section, directory structure | `DEVELOPER.md` (45KB) |
| Cybersecurity risk assessment | Architecture decisions documented in sprint context files; threat model in blog series | `docs/sprint_*_context.md`, `blog-series/01-*.md` |
| Applied harmonized standards | Code style (Ruff), testing framework (pytest), CI pipeline documented | `ruff.toml`, `ci.yml` |
| Security testing results | 132+ automated tests; CI runs on every push | `tests/` directory, CI logs |
| Support and update information | QUICK_START.md, TROUBLESHOOTING.md | Setup and debugging guides |

### 4. Documentation Integrity — The Drift Detection Innovation

**This is CDDBS's most distinctive CRA compliance practice.**

The CRA requires documentation to be "kept up to date" (Art. 13). Most projects address this with process ("remember to update docs"). CDDBS automates it:

```python
# scripts/check_docs_drift.py
# Runs in CI on every push/PR

# 1. Scans src/ for Python modules
# 2. Scans DEVELOPER.md for documented modules
# 3. Fails CI if any module exists without documentation
# 4. Checks API endpoints in code vs docs
# 5. Checks environment variables in code vs docs
```

**Result**: Documentation cannot drift from implementation. If a developer adds a new endpoint without documenting it, CI fails.

**Why this matters for CRA**: Art. 13 requires that documentation "is kept up to date during the expected product lifetime." Automated drift detection is a stronger guarantee than any manual process.

### 5. Update Mechanism (Art. 10(12))

**Requirement**: Ensure security updates can be delivered effectively.

| Mechanism | Implementation |
|-----------|---------------|
| Containerized deployment | Docker + Docker Compose; `docker compose pull && docker compose up` updates all services |
| Version tagging | Semver git tags (`v0.5.0`…`v0.9.0`); CHANGELOG.md tracks all changes |
| Environment-based configuration | All runtime config via environment variables; no code changes needed for config updates |
| Database migrations | SQLAlchemy models with `init_db()` auto-creation; Alembic-ready for schema migrations |

### 6. Branch Policy as Change Control

The CRA requires "documented management procedures" for cybersecurity (Art. 10(6)). CDDBS implements this as automated branch policy:

```
Feature branch → development → main (production)
                     ↑              ↑
              CI validates    CI validates
              (lint, test,    (only from
               docs drift)    development)
```

This is enforced by:
- GitHub Actions workflow (`.github/workflows/branch-policy.yml`)
- CODEOWNERS requiring review for security-sensitive files
- CI pipeline running all compliance checks before merge

---

## SBOM Readiness

While CDDBS doesn't yet generate a formal SBOM (CycloneDX/SPDX), the prerequisites are in place:

### Python Dependencies (`requirements.txt`)

```
fastapi>=0.109.0
uvicorn>=0.27.0
sqlalchemy>=2.0.25
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
requests>=2.31.0
httpx>=0.27.0
google-genai>=1.3.0
feedparser>=6.0.11
scikit-learn>=1.4.0
scipy>=1.13.0
...
```

### Frontend Dependencies (`frontend/package.json`)

Managed via npm with `package-lock.json` for reproducible builds.

### To Generate SBOM (Sprint 8+ or on-demand)

```bash
# Python (CycloneDX)
pip install cyclonedx-bom
cyclonedx-py requirements -i requirements.txt -o sbom-python.json

# Frontend (CycloneDX)
npx @cyclonedx/cyclonedx-npm --output-file sbom-frontend.json

# Combined SPDX
# Use syft or trivy for container-level SBOM
```

---

## Gap Analysis: What's Left for Full CRA Compliance

| Gap | Priority | Target Sprint |
|-----|----------|--------------|
| Formal SBOM generation in CI | Medium | Sprint 8 |
| Automated dependency vulnerability scanning (Dependabot/Snyk) | Medium | Sprint 8 |
| EU vulnerability reporting portal integration | Low | When portal launches |
| Conformity assessment documentation | Low | Before commercial deployment |
| Contact point for vulnerability reports (beyond GitHub) | Low | Sprint 9 |

---

## Reusable Practices for Other Projects

1. **Secret scanning in CI**: <1 second, prevents the most common security failure
2. **Documentation drift detection**: Automate the CRA's "keep documentation up to date" requirement
3. **Branch policy enforcement**: Encode your release process in CI, not just team agreements
4. **SBOM-ready dependency management**: Pin versions now, generate SBOM when needed
5. **SECURITY.md from day one**: CRA requires a vulnerability handling process; write it early
6. **Environment variable configuration**: No secrets in code, ever
