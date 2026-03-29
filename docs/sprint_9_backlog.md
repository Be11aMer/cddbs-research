# Sprint 9 Backlog — AI Trust, Information Security & Compliance Automation

**Sprint**: 9 (Apr 1 – Apr 14, 2026)
**Target**: v0.9.0
**Status**: Complete (Implementation 2026-03-28)
**Related**: [Sprint 8 Retrospective](../retrospectives/sprint_8.md) | [Execution Plan](cddbs_execution_plan.md) | Security Audit Findings (below)
**Branch Policy**: Production work branches from `development`, not `main`

---

## Sprint Goals

1. **AI Trust Framework** — Validate LLM outputs structurally, detect potential hallucinations, and calibrate confidence scores so analysts can trust what they see
2. **Information Security Hardening** — Close the critical gaps found in the Sprint 8 security audit: CORS, rate limiting, prompt injection, input validation, security headers
3. **Compliance Automation** — Move from manual compliance evidence to CI-generated artifacts that prove regulatory compliance on every build
4. **Recursive Completeness Check** — Final sprint step verifying all tasks implemented, tested, documented, and gap-free

---

## Security Audit Findings (Sprint 8 Audit Context)

The Sprint 8 completeness audit identified these security gaps in cddbs-prod:

| Finding | Severity | Current State |
|---------|----------|---------------|
| No rate limiting on any endpoint | HIGH | Expensive operations (Gemini calls) exposed without throttling |
| CORS wildcard origins + credentials | HIGH | `allow_origins="*"` with `allow_credentials=True` — invalid per spec |
| Prompt injection via f-string interpolation | HIGH | User-provided topic/outlet inserted directly into Gemini prompts |
| Webhook URL accepts any string (SSRF) | HIGH | No URL format validation, no internal IP blocking |
| No authentication on any endpoint | CRITICAL | All endpoints publicly accessible |
| Missing security headers | MEDIUM | No CSP, HSTS, X-Frame-Options, X-Content-Type-Options |
| API keys accepted in request bodies | MEDIUM-HIGH | Keys can be logged/persisted in Report.data JSON |
| Error details exposed in health endpoint | MEDIUM | Database error strings returned to client |

**Sprint 9 addresses all HIGH/CRITICAL items except authentication** (deferred to Sprint 10 — requires JWT, role model, session management, UI changes).

---

## P0 — AI Trust Framework

### 9.1 LLM Output Validation Layer

| # | Task | Effort | Acceptance Criteria |
|---|------|--------|---------------------|
| 9.1.1 | `pipeline/output_validator.py` — structural validation | M | Validates every Gemini JSON response against expected schema before DB commit; catches missing fields, wrong types, out-of-range values (e.g., divergence_score outside 0-100); returns ValidationResult with errors list |
| 9.1.2 | Hallucination heuristic: source cross-reference | L | For Topic Mode: compares outlet claims in Gemini response against article titles/snippets from SerpAPI; flags claims with no source match as "ungrounded"; stores `grounding_score` (0.0-1.0) per outlet result |
| 9.1.3 | Confidence calibration metrics | M | Track historical accuracy: compare Gemini's divergence_score predictions against human feedback (existing feedback system); compute calibration curve data; expose via `GET /metrics/calibration` endpoint |
| 9.1.4 | Output reproducibility check | S | For identical inputs (same topic, same articles), run Gemini twice with temperature=0; store `reproducibility_score` in TopicRun (0.0-1.0 Jaccard similarity of technique lists); log discrepancies |

### 9.2 AI Trust Frontend

| # | Task | Effort | Acceptance Criteria |
|---|------|--------|---------------------|
| 9.2.1 | `TrustIndicator.tsx` component | M | Per-outlet trust badge showing: grounding score (sourced/ungrounded), confidence calibration status, reproducibility; color-coded (green/yellow/red); tooltip with explanation |
| 9.2.2 | Ungrounded claim highlighting | S | In TopicRunDetail, key_claims with no source match rendered with warning icon and "⚠ Ungrounded — no matching source found" annotation |
| 9.2.3 | Wire trust indicators into TopicRunDetail | S | TrustIndicator appears on each outlet card; grounding_score in outlet result API response |

---

## P0 — Information Security Hardening

### 9.3 CORS Hardening

| # | Task | Effort | Acceptance Criteria |
|---|------|--------|---------------------|
| 9.3.1 | Fix CORS configuration | S | `ALLOWED_ORIGINS` defaults to specific domains (Render URL, Cloudflare URL, localhost:5173); remove wildcard; `allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]`; `allow_headers` restricted to `Content-Type, Authorization` |

### 9.4 Rate Limiting

| # | Task | Effort | Acceptance Criteria |
|---|------|--------|---------------------|
| 9.4.1 | Add slowapi rate limiting middleware | M | Install `slowapi`; configure global rate limit (60 requests/minute per IP); stricter limits on expensive endpoints: POST /analysis-runs (5/min), POST /topic-runs (3/min), POST /social-media/analyze (5/min); returns 429 with Retry-After header |
| 9.4.2 | Rate limit response handler | S | Custom 429 response with JSON body `{"detail": "Rate limit exceeded", "retry_after": N}`; logged for monitoring |

### 9.5 Prompt Injection Prevention

| # | Task | Effort | Acceptance Criteria |
|---|------|--------|---------------------|
| 9.5.1 | `utils/input_sanitizer.py` | M | `sanitize_prompt_input(text: str) -> str` — strips control characters, normalizes whitespace, escapes prompt-delimiter patterns (triple quotes, markdown separators, "IGNORE PREVIOUS INSTRUCTIONS"); truncates to max length; logs sanitization actions |
| 9.5.2 | Wire sanitizer into all prompt templates | S | Every f-string interpolation in `topic_prompt_templates.py` and `prompt_templates.py` passes through `sanitize_prompt_input()` before insertion; integration test verifies injection attempt is neutralized |
| 9.5.3 | External data sanitization | S | SerpAPI article titles/snippets and GDELT data sanitized before prompt insertion; strips HTML entities, limits field length to 500 chars |

### 9.6 Input Validation Hardening

| # | Task | Effort | Acceptance Criteria |
|---|------|--------|---------------------|
| 9.6.1 | Enum validation for constrained fields | S | `date_filter: Literal["h", "d", "w", "m", "y"]`; `platform: Literal["twitter", "telegram"]`; Pydantic validates automatically |
| 9.6.2 | Webhook URL validation + SSRF prevention | M | Validate URL format (httpx.URL or urllib.parse); block private IP ranges (10.x, 172.16-31.x, 192.168.x, 127.x, 169.254.x, ::1); block non-HTTP(S) schemes; max URL length 2048 |
| 9.6.3 | Outlet name validation | S | Regex pattern for outlet: domain-like alphanumeric string with hyphens/dots; max 253 chars; reject obvious injection patterns |

### 9.7 Security Headers

| # | Task | Effort | Acceptance Criteria |
|---|------|--------|---------------------|
| 9.7.1 | Security headers middleware | S | Custom FastAPI middleware adding: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=()`, `Content-Security-Policy: default-src 'self'` (API-only CSP) |

### 9.8 Error Handling Hardening

| # | Task | Effort | Acceptance Criteria |
|---|------|--------|---------------------|
| 9.8.1 | Sanitize error responses | S | Health endpoint returns generic `{"status": "unhealthy"}` on DB error (no exception details); analysis run errors stored as generic categories ("api_error", "pipeline_error", "validation_error") not raw exception strings; API key values never appear in error messages |

### 9.9 API Key Hygiene

| # | Task | Effort | Acceptance Criteria |
|---|------|--------|---------------------|
| 9.9.1 | Remove API keys from request bodies | M | Remove `google_api_key` and `serpapi_key` from POST request schemas; use environment variables exclusively; remove keys from Report.data JSON storage; migration script to clean existing stored keys |
| 9.9.2 | Add API key presence validation at startup | S | App refuses to start if required API keys (GOOGLE_API_KEY, SERPAPI_KEY) not set; clear error message pointing to DEVELOPER.md |

---

## P1 — Compliance Automation

### 9.10 Automated Compliance Evidence

| # | Task | Effort | Acceptance Criteria |
|---|------|--------|---------------------|
| 9.10.1 | `compliance-report.yml` CI workflow | L | Runs on every push to main/development; generates JSON report with: test count, lint status, SBOM present, vulnerability scan results, security headers verified, docs drift status, secrets scan status; uploads as CI artifact |
| 9.10.2 | Compliance evidence endpoint | M | `GET /compliance/evidence` returns machine-readable JSON: app version, deployment date, SBOM generation timestamp, last vulnerability scan, test count, AI disclosure status, data retention policy; authenticated (basic API key) |
| 9.10.3 | Data retention policy enforcement | S | Automated cleanup: analysis runs older than configurable retention period (default 90 days) are flagged; `GET /compliance/retention` shows retention status; actual deletion requires manual trigger (safety) |

### 9.11 Regulatory Documentation Update

| # | Task | Effort | Acceptance Criteria |
|---|------|--------|---------------------|
| 9.11.1 | Update EU AI Act compliance doc | M | Document all Sprint 9 AI trust measures in `compliance-practices/eu_ai_act.md`; map grounding score to Art. 50 transparency; document output validation as quality management (Art. 9) |
| 9.11.2 | Update CRA compliance doc | S | Document security hardening measures in `compliance-practices/cyber_resilience_act_cra.md`; rate limiting, CORS, input validation, security headers mapped to CRA articles |
| 9.11.3 | Information security practices document | M | New document `compliance-practices/information_security.md` covering: OWASP Top 10 for LLM Applications mapping, prompt injection prevention, SSRF prevention, rate limiting rationale, security headers explanation |

---

## P1 — Testing

| # | Task | Effort | Acceptance Criteria |
|---|------|--------|---------------------|
| 9.12 | Output validator tests | M | ≥8 tests: valid JSON passes, missing fields caught, out-of-range values caught, hallucination heuristic flags ungrounded claims, grounding score calculation |
| 9.13 | Input sanitizer tests | M | ≥8 tests: injection patterns neutralized ("IGNORE PREVIOUS", triple quotes, markdown separators), control characters stripped, HTML entities escaped, max length enforced |
| 9.14 | Security hardening tests | M | ≥10 tests: CORS rejects unauthorized origin, rate limit returns 429, webhook URL rejects private IPs, enum validation rejects invalid values, security headers present on all responses, error responses don't leak details |
| 9.15 | Compliance endpoint tests | S | ≥4 tests: evidence endpoint returns valid JSON, retention endpoint works, compliance report covers all required fields |
| 9.16 | Frontend type-check | S | `npm run build` passes with all new components |

---

## P1 — Documentation

| # | Task | Effort | Acceptance Criteria |
|---|------|--------|---------------------|
| 9.17 | Update DEVELOPER.md with Sprint 9 features | M | New sections: AI trust framework, security hardening, compliance automation, input sanitizer usage |
| 9.18 | Update CHANGELOG.md | S | v1.9.0 release notes with all Sprint 9 features |
| 9.19 | Update execution plan | S | Mark Sprint 8 complete, Sprint 9 current; update architecture section |
| 9.20 | Update compliance log | S | Sprint 9 compliance measures documented with evidence |

---

## P2 — Deferred Items

| # | Task | Effort | Notes |
|---|------|--------|-------|
| 9.21 | User authentication (JWT + role model) | XL | Deferred to Sprint 10 — foundational but large; requires session management, password hashing, UI login flow |
| 9.22 | Shared analysis workspaces | XL | Depends on auth; Sprint 11 |
| 9.23 | Analyst annotations on briefings | L | Depends on auth; Sprint 11 |
| 9.24 | CDDBS-Edge Phase 0 | L | Deferred to Sprint 10 — focus on trust/security first |
| 9.25 | Backend migration from Render | — | User researching alternatives in parallel; keep-alive workflow interim solution |

---

## FINAL STEP — Recursive Completeness Check (Task 9.26)

**This task must be executed last, after all other Sprint 9 tasks are marked done.**

### 9.26 Sprint 9 Recursive Completeness Audit

#### 9.26.1 Implementation Completeness
- [ ] Every P0 task (9.1–9.9) has corresponding code committed
- [ ] Every P1 task (9.10–9.20) has corresponding code/docs committed
- [ ] No TODO/FIXME/HACK comments left in Sprint 9 code
- [ ] All new files imported/registered where needed

#### 9.26.2 Test Coverage
- [ ] `pytest tests/ -v` passes — ≥244 total tests (≥30 new Sprint 9 tests)
- [ ] `npm run build` succeeds (frontend type-check)
- [ ] All new API endpoints return expected responses
- [ ] Security tests verify: CORS rejection, rate limiting, prompt injection blocked, SSRF blocked

#### 9.26.3 Documentation Completeness
- [ ] DEVELOPER.md updated with all Sprint 9 features
- [ ] CHANGELOG.md has v1.9.0 entry
- [ ] New `information_security.md` compliance document created
- [ ] Sprint 9 retrospective — deferred to sprint close
- [ ] Compliance log updated

#### 9.26.4 CI/Compliance Verification
- [ ] Lint passes (ruff check clean)
- [ ] pip-audit passes (no actionable CVEs)
- [ ] SBOM workflow runs and uploads artifact
- [ ] compliance-report.yml generates valid evidence artifact
- [ ] No secrets in committed code
- [ ] Branch policy: PR targets development branch

#### 9.26.5 Vision Alignment Check (Sprints 1-9)
- [ ] AI trust framework serves core mission: ensuring analyst confidence in AI-generated analysis
- [ ] Security hardening protects the platform and its users
- [ ] Compliance automation reduces manual regulatory burden
- [ ] No feature creep away from counter-disinformation mission
- [ ] Auth deferral to Sprint 10 is deliberate — trust/security before access control

#### 9.26.6 Gap Identification
- [ ] Document any gaps found
- [ ] Confirm Sprint 10 candidates: user auth, CDDBS-Edge Phase 0, shared workspaces
- [ ] Assess backend migration status (Render alternatives)

---

## Acceptance Criteria (Sprint-Level)

### AI Trust
- [ ] Every Gemini response validated structurally before DB commit
- [ ] Ungrounded claims flagged with warning in UI
- [ ] Grounding score visible per outlet in TopicRunDetail
- [ ] Output validation errors logged and retrievable

### Information Security
- [ ] CORS rejects requests from unauthorized origins
- [ ] Rate limiting active on all endpoints (429 returned on excess)
- [ ] Prompt injection attempts neutralized (test with known injection patterns)
- [ ] Webhook URLs validated and private IPs blocked
- [ ] Security headers present on all responses
- [ ] API keys never appear in request bodies or error messages

### Compliance
- [ ] Compliance evidence artifact generated on every CI run
- [ ] Machine-readable compliance endpoint accessible
- [ ] Information security compliance document created
- [ ] All Sprint 9 measures mapped to regulations

### Quality
- [ ] ≥30 new tests (≥244 total passing)
- [ ] All CI workflows green
- [ ] No documentation drift

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Rate limiting too aggressive for legitimate use | Start with generous limits (60/min global, 5/min analysis); tune based on real usage patterns; document override via env var |
| Input sanitizer breaks legitimate topics | Whitelist-based approach: allow alphanumeric + common punctuation; sanitizer returns cleaned text, never rejects; log all sanitizations for review |
| Output validator rejects valid Gemini responses | Lenient validation: required fields + type checks only; optional fields allowed to be null; validation errors logged but don't block pipeline |
| Grounding score gives false confidence | Clearly label as "heuristic — not definitive"; source cross-reference is title/snippet matching, not semantic; document limitations |
| Security headers break frontend | API-only CSP (`default-src 'self'`); frontend served separately via Cloudflare Workers with its own CSP |
| Compliance endpoint exposes sensitive info | Endpoint returns operational metadata only (no PII, no analysis content, no API keys); basic auth protection |

---

## Tech Stack (New Dependencies)

| Package | Purpose | Tier |
|---------|---------|------|
| `slowapi` | Rate limiting middleware for FastAPI | Runtime |

No other new runtime dependencies. AI trust framework uses existing `google-genai` SDK + custom validation logic. Input sanitizer is pure Python (re module). Security headers middleware is custom FastAPI middleware.

---

## Architecture Decisions

### Why AI Trust Before Auth?

Authentication (Sprint 10) controls **who** can use the system. AI trust (Sprint 9) controls **what the system tells people**. For a disinformation detection system, output integrity is more critical than access control — a trusted analyst using unreliable AI output is worse than an unauthorized user seeing reliable output.

### Why Not Use a Dedicated AI Safety Library?

Libraries like Guardrails AI and NeMo Guardrails add complexity and dependencies. CDDBS's trust needs are specific: validate JSON structure, cross-reference claims against source material, track confidence calibration. Custom implementation is more maintainable and auditable for compliance purposes.

### Prompt Injection: Sanitize vs. Separate

Two approaches to prompt injection:
1. **Sanitize inputs** — strip dangerous patterns before insertion (chosen)
2. **Separate user data** — use system/user message separation

We use approach 1 because Gemini's `genai.generate_content()` doesn't support the OpenAI-style system/user message separation in the same way. The system_instruction parameter is set once; article data and topics go into the content. Sanitization is the pragmatic choice.

### OWASP Top 10 for LLM Applications — Sprint 9 Coverage

| OWASP LLM Risk | Sprint 9 Task | Coverage |
|-----------------|---------------|----------|
| LLM01: Prompt Injection | 9.5.1-9.5.3 | Input sanitization + external data sanitization |
| LLM02: Insecure Output Handling | 9.1.1 | Structural validation before DB commit |
| LLM03: Training Data Poisoning | N/A | We don't fine-tune; using Gemini as-is |
| LLM04: Model Denial of Service | 9.4.1 | Rate limiting on endpoints that trigger Gemini calls |
| LLM05: Supply Chain Vulnerabilities | Sprint 8 | SBOM + pip-audit + SHA-pinned Actions (done) |
| LLM06: Sensitive Information Disclosure | 9.8.1, 9.9.1 | Error sanitization + API key removal from requests |
| LLM07: Insecure Plugin Design | N/A | No plugins/tools |
| LLM08: Excessive Agency | N/A | LLM has no ability to execute actions |
| LLM09: Overreliance | 9.1.2, 9.2.1-9.2.2 | Grounding score + ungrounded claim highlighting |
| LLM10: Model Theft | N/A | Using cloud API, not hosting model |

---

## Definition of Done

- All P0 and P1 tasks completed and tested
- Recursive completeness check (9.26) executed and all items checked
- CI green on all workflows (ci.yml, branch-policy.yml, secret-scan.yml, sbom.yml, compliance-report.yml)
- DEVELOPER.md and CHANGELOG.md updated
- Sprint 9 retrospective written
- Compliance log updated
- No regression in Sprint 1-8 functionality
- Security audit findings (HIGH/CRITICAL) resolved
- Production patch exported to `patches/sprint9_production_changes.patch`
