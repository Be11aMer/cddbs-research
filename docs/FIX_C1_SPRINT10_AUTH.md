# Fix C-1: Sprint 10 API Key Authentication

**Date:** 2026-06-01  
**Branch:** `fix/c1-sprint10-auth`  
**Closes:** C-1 (no authentication on any API endpoint)  

---

## What Was Wrong

Every endpoint in `src/cddbs/api/main.py` was unauthenticated. Any internet client
could trigger Gemini API calls (consuming quota), read all stored intelligence,
write to the database, and modify webhooks. This is explicitly flagged as
blocking for CII engagement.

---

## Design Decision: Static API Key + Argon2id

The auth research in `research/auth_model_research.md` documents the full
Spring 11 path (Ed25519, DPoP, WebAuthn). Sprint 10 is the intentional
"throwaway" first step: one high-entropy static key, Argon2id hash in DB.

**Why not JWT/sessions for Sprint 10?**  
This is a single-user research tool accessed by one operator. The overhead
of session management, refresh tokens, and a login flow adds complexity with
zero benefit at this usage scale. A static high-entropy key + Argon2id provides:
- No replay risk from API key reuse (key is static, not per-session)
- Argon2id prevents offline brute force even if DB is leaked
- Simple to revoke: flip `is_active = false` in DB
- Zero frontend changes required

**Sprint 11 migration path:**  
The `ApiKey` table and `APIKeyMiddleware` will be replaced by WebAuthn/session
tokens in Sprint 11. The middleware interface is already abstracted so the
swap is localized to `auth.py` and the middleware registration in `main.py`.

---

## Implementation

### `src/cddbs/api/auth.py` (new)
- `PasswordHasher` configured: `time_cost=2`, `memory_cost=65536` (64 MiB), `parallelism=2`
- `APIKeyMiddleware(BaseHTTPMiddleware)` checks `X-API-Key` header (primary)
  or `Authorization: Bearer <key>` (secondary) for all non-exempt paths
- Exempt paths: `{"health", "/", "/docs", "/openapi.json", "/redoc"}`
- 5-minute in-memory cache keyed by `sha256(plaintext_key)` to avoid Argon2
  execution on every request
- `bootstrap_api_key()`: on startup, if `CDDBS_BOOTSTRAP_API_KEY` is set
  and no keys exist in DB, hashes and stores the key

### `src/cddbs/models.py`
- New `ApiKey` model:
  - `key_hash`: Argon2id hash (never stores plaintext)
  - `key_prefix`: first 8 chars for log identification
  - `is_active`: revocation flag
  - `last_used_at`: audit trail

### `src/cddbs/api/main.py`
- `APIKeyMiddleware` registered via `app.add_middleware(APIKeyMiddleware)`
- `bootstrap_api_key()` called in lifespan startup
- `X-API-Key` and `Authorization` added to CORS `allow_headers`

---

## Deployment Steps

1. **Generate a key**: `python3 -c "import secrets; print('cddbs_' + secrets.token_urlsafe(32))"`
2. **Set env var** in Render dashboard: `CDDBS_BOOTSTRAP_API_KEY=<your_generated_key>`
3. **Deploy** — on startup, the key is hashed and stored in `api_keys` table
4. **Remove env var** after first deploy (key is now in DB; env var no longer needed)
5. **Test**: `curl -H 'X-API-Key: <your_key>' https://your-render-url/analysis-runs`

> **Security note**: Never log or commit the plaintext key. Only the hash is safe to store.

---

## Re-Audit Checklist Status

| Check | Status |
|-------|--------|
| `GET /health` returns 200 unauthenticated | ✅ (exempt path) |
| All other endpoints return 401 without valid key | ✅ (middleware enforced) |

---

## Connection to Research

This Sprint 10 key is the "proof establishment" layer from
`research/auth_model_research.md` Experiment 1 — the simplest possible
credential: a shared secret known to both parties. The research experiments
build toward Sprint 11's Ed25519 + assertion layer which provides offline
verification for CDDBS-Edge.
