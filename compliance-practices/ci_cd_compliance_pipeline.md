# CI/CD Compliance Pipeline

**Last Updated**: 2026-03-18
**Implemented In**: Sprint 6 (cddbs-prod)
**Relevant Regulations**: CRA (documentation integrity, vulnerability handling), DSGVO (security measures)

---

## Overview

The CDDBS CI/CD pipeline enforces compliance automatically on every push and pull request. This document describes each compliance-relevant workflow, why it exists, and how to replicate it in other projects.

---

## 1. Secret Detection (`secret-scan.yml`)

### What It Does

Scans all committed code for hardcoded secrets: API keys, tokens, passwords, connection strings.

### Implementation

```yaml
# .github/workflows/secret-scan.yml
name: Secret Scan
on:
  push:
    branches: [main, master, development]
  pull_request:
    branches: [main, master, development]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python scripts/detect_secrets.py
```

### Detection Script (`scripts/detect_secrets.py`)

Custom Python script that scans for:
- API key patterns (e.g., `AIza...`, `sk-...`, `ghp_...`)
- Generic secret patterns (`password=`, `secret=`, `token=` with values)
- Connection strings with embedded credentials
- Base64-encoded tokens of suspicious length

**Why custom over tools like `truffleHog` or `detect-secrets`?**
- Zero dependencies (runs with stdlib only)
- No false positives from configuration (the patterns are tuned to CDDBS)
- Easy to audit and extend
- Runs in <1 second

### Regulatory Mapping

| Regulation | Requirement | How Secret Scanning Addresses It |
|------------|-------------|----------------------------------|
| CRA Art. 10(4) | No known exploitable vulnerabilities shipped | Prevents credential leaks before they reach production |
| DSGVO Art. 32 | Appropriate security measures | Automated enforcement of secret hygiene |

### Reusable Practice

**For any project**: Add a secret scanning step to CI that runs on every PR. The cost is <1 second of CI time. The alternative — a leaked API key in a public repo — can cost thousands of euros and hours of incident response.

---

## 2. Documentation Drift Detection (`ci.yml` → docs-drift job)

### What It Does

Verifies that documentation stays in sync with code changes. When code structure changes but docs don't update, the CI fails.

### Implementation

```yaml
# Part of .github/workflows/ci.yml
docs-drift:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.11"
    - run: python scripts/check_docs_drift.py
```

### Detection Script (`scripts/check_docs_drift.py`)

Checks for:
- **Structural drift**: Source files exist that aren't mentioned in DEVELOPER.md
- **Endpoint drift**: API endpoints in code not documented in API reference
- **Configuration drift**: Environment variables used in code not in deployment docs
- **Test drift**: Test files exist without corresponding documentation in test guide

### Regulatory Mapping

| Regulation | Requirement | How Drift Detection Addresses It |
|------------|-------------|----------------------------------|
| CRA Art. 13 | Technical documentation must be accurate | Automated verification that docs match implementation |
| CRA Art. 13(15) | Documentation must be kept up to date | CI failure on drift forces immediate documentation update |

### Reusable Practice

**For any project**: Define a "documentation contract" — a set of assertions about what must be documented. Encode these as a script that runs in CI. This prevents the common failure mode where documentation becomes stale months after code changes.

---

## 3. Branch Policy Enforcement (`branch-policy.yml`)

### What It Does

Enforces that:
1. Only the `development` branch can merge into `main`/`master`
2. Feature branches targeting `development` must be based on `development`

### Implementation

```yaml
# .github/workflows/branch-policy.yml
name: Branch Policy
on:
  pull_request:
    branches: [main, master, development]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Enforce branch rules
        run: |
          TARGET="${{ github.base_ref }}"
          SOURCE="${{ github.head_ref }}"
          if [[ "$TARGET" == "main" || "$TARGET" == "master" ]]; then
            if [[ "$SOURCE" != "development" ]]; then
              echo "ERROR: Only 'development' can merge into '$TARGET'"
              exit 1
            fi
          fi
```

### Why This Matters

- **Prevents accidental production deployments** from feature branches
- **Enforces code review flow**: feature → development → main
- **Creates audit trail**: every production change goes through a single integration point
- **Supports rollback**: development branch can be reset without affecting main

### Regulatory Mapping

| Regulation | Requirement | How Branch Policy Addresses It |
|------------|-------------|-------------------------------|
| CRA Art. 10(6) | Effective and documented management procedures | Enforced git workflow with CI verification |
| CRA Annex I, Part II | Vulnerability handling through controlled release | Changes go through development before production |

### Reusable Practice

**For any project**: Implement branch protection rules both in GitHub settings AND in CI (defense in depth). The CI check catches cases where GitHub branch protection is misconfigured or bypassed.

---

## 4. Code Quality (Lint + Test)

### Linting (`ci.yml` → lint job)

```yaml
lint:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.11"
    - run: pip install ruff
    - run: ruff check src/ tests/
```

Uses **Ruff** — a fast Python linter that enforces consistent code style, catches common bugs, and prevents security anti-patterns.

### Testing (`ci.yml` → test job)

```yaml
test:
  runs-on: ubuntu-latest
  services:
    postgres:
      image: postgres:15
      env:
        POSTGRES_PASSWORD: test
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
    - run: pip install -r requirements.txt
    - run: pytest tests/ -v --tb=long
```

**132+ tests** across 12 test files covering:
- API endpoints and response formats
- Pipeline processing logic
- Quality scoring accuracy
- Narrative matching
- Database operations
- Webhook delivery and signing
- Data collection and deduplication

### Frontend Type-Check (`ci.yml` → frontend-build job)

```yaml
frontend-build:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: 20
    - run: cd frontend && npm ci && npm run build
```

TypeScript compilation catches type errors before they reach production.

---

## 5. Code Ownership (`CODEOWNERS`)

### What It Does

Requires specific reviewers for changes to security-sensitive files.

```
# Default: all PRs need review
* @Be11aMer

# Security-sensitive files need extra scrutiny
.github/ @Be11aMer
scripts/ @Be11aMer
Dockerfile @Be11aMer
docker-compose.yml @Be11aMer
src/cddbs/config.py @Be11aMer
src/cddbs/database.py @Be11aMer
```

### Regulatory Mapping

| Regulation | Requirement | How CODEOWNERS Addresses It |
|------------|-------------|----------------------------|
| CRA Art. 10(6) | Documented management procedures | Explicit ownership of security-critical code |
| DSGVO Art. 32 | Organizational security measures | Access control on sensitive configuration |

---

## Summary: The Compliance CI Pipeline

```
Every Push / PR
    │
    ├── Secret Scan ──────── Prevents credential leaks (CRA, DSGVO)
    ├── Lint ─────────────── Code quality and security patterns
    ├── Test ─────────────── Functional correctness (132+ tests)
    ├── Docs Drift ──────── Documentation accuracy (CRA)
    ├── Frontend Build ──── Type safety
    ├── Branch Policy ───── Release control (CRA)
    └── CODEOWNERS ──────── Review requirements (CRA, DSGVO)
```

**Total CI time**: ~3-5 minutes
**Value**: Prevents credential leaks, documentation rot, unauthorized production changes, and regression bugs — automatically, on every change.
