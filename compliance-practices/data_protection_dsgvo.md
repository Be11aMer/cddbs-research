# Data Protection Practices (DSGVO/GDPR)

**Last Updated**: 2026-03-18
**Implemented Across**: Sprints 1-6
**Regulation**: Regulation (EU) 2016/679 (General Data Protection Regulation)

---

## Architectural Approach: Privacy by Design

CDDBS was designed from Sprint 1 with data minimization as a core architectural principle, not retrofitted after development.

---

## 1. BYOK (Bring Your Own Key) Architecture

### What

API keys (SerpAPI, Google Gemini, Telegram Bot Token) are provided by the user via environment variables or browser configuration. The CDDBS server never stores or persists API keys.

### How It Was Implemented

```python
# src/cddbs/config.py
class Settings:
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
```

Keys are:
- Read from environment variables at startup
- Never written to database, logs, or response bodies
- Never included in error messages or stack traces
- Protected by secret scanning CI (prevents accidental commits)

### DSGVO Mapping

| Principle | Implementation |
|-----------|---------------|
| Data minimization (Art. 5(1)(c)) | Server doesn't store credentials it doesn't need to persist |
| Security (Art. 32) | Keys exist only in memory during process lifetime |
| Accountability (Art. 5(2)) | Environment variable approach is auditable and documented |

### Reusable Practice

> **BYOK for any SaaS**: If your application uses third-party API keys on behalf of users, store them in the user's environment — not in your database. This eliminates an entire class of data breach scenarios.

---

## 2. Data Minimization in Analysis Pipeline

### What

CDDBS stores analysis results (structured briefings, quality scores, narrative matches) but minimizes storage of raw personal data.

### How

| Data Type | What We Store | What We Don't Store |
|-----------|--------------|---------------------|
| Articles | Title, URL, source, publish date, summary excerpt | Full article body (only first 500 chars for clustering) |
| Social media | Account handle, analysis results | Direct messages, follower lists, personal posts |
| Briefings | Structured JSON with confidence scores | Raw LLM conversation history |
| Quality | Dimensional scores (7 dimensions, 70 points) | Individual scorer reasoning/logs |

### Pipeline Data Flow

```
External API → fetch_articles() → [title, URL, summary] → analyze() → [briefing JSON]
                                                                        ↓
                                                              score_briefing() → [quality scores]
                                                                        ↓
                                                              match_narratives() → [narrative matches]
                                                                        ↓
                                                              PostgreSQL (structured results only)
```

Raw API responses are processed in memory and discarded. Only structured results are persisted.

### DSGVO Mapping

| Principle | Implementation |
|-----------|---------------|
| Purpose limitation (Art. 5(1)(b)) | Data stored exclusively for disinformation analysis |
| Data minimization (Art. 5(1)(c)) | Only structured results stored, not raw data |
| Storage limitation (Art. 5(1)(e)) | Analysis runs deletable; no indefinite retention |

---

## 3. No User Tracking

### Current State (Pre-Authentication)

CDDBS currently has no user authentication (planned for Sprint 8+). This means:

- No user accounts stored
- No session cookies
- No analytics or tracking pixels
- No third-party tracking scripts
- No fingerprinting

### Future Authentication (Sprint 8+ Planning)

When user authentication is implemented, the following principles must be maintained:

- [ ] Password hashing (bcrypt/argon2, never plaintext)
- [ ] Session tokens with expiry (not indefinite)
- [ ] No tracking beyond authentication necessity
- [ ] Clear data deletion path for user accounts
- [ ] Documented legal basis for processing (legitimate interest for security research tool)

---

## 4. Secret Protection

### Multi-Layer Defense

| Layer | Mechanism | Sprint |
|-------|-----------|--------|
| Development | `.gitignore` excludes `.env`, credentials | Sprint 1 |
| Pre-commit | `scripts/detect_secrets.py` available locally | Sprint 6 |
| CI | `secret-scan.yml` runs on every push/PR | Sprint 6 |
| Runtime | Environment variables only; no config files with secrets | Sprint 1 |
| Documentation | SECURITY.md documents responsible disclosure | Sprint 6 |

### What the Secret Scanner Detects

- Google API keys (`AIza...`)
- Generic API keys (`sk-...`, `ghp_...`)
- Connection strings with passwords
- Hardcoded tokens in test files
- Base64-encoded secrets

---

## 5. Webhook Security (DSGVO Art. 32)

### HMAC-SHA256 Signing

All webhook payloads are signed with HMAC-SHA256 using a shared secret:

```python
# src/cddbs/webhooks.py
def sign_payload(payload: str, secret: str) -> str:
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
```

The signature is sent in the `X-CDDBS-Signature` header. Receivers verify:

```python
expected = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
assert hmac.compare_digest(expected, received_signature)
```

This prevents:
- Payload tampering in transit
- Unauthorized webhook delivery
- Replay attacks (when combined with timestamp validation)

---

## Summary: DSGVO Compliance Measures

| Measure | Article | Sprint Implemented |
|---------|---------|-------------------|
| BYOK architecture | Art. 5(1)(c), Art. 32 | Sprint 1 |
| Data minimization in pipeline | Art. 5(1)(c) | Sprint 1 |
| Purpose limitation | Art. 5(1)(b) | Sprint 1 |
| No user tracking | Art. 5(1)(c) | Sprint 1 |
| Secret protection (.gitignore) | Art. 32 | Sprint 1 |
| Secret scanning CI | Art. 32 | Sprint 6 |
| HMAC webhook signing | Art. 32 | Sprint 6 |
| SECURITY.md disclosure process | Art. 33/34 | Sprint 6 |
| Environment variable configuration | Art. 32 | Sprint 1 |
