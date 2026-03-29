# Information Security Analysis — CDDBS Sprint 9 Research

**Date**: 2026-03-28
**Purpose**: Security audit findings and implementation recommendations for Sprint 9
**Scope**: cddbs-prod backend (FastAPI) + frontend (React) + deployment infrastructure

---

## 1. Security Audit Summary

A comprehensive security audit of the cddbs-prod codebase was conducted as part of the Sprint 8 completeness review. The audit examined 9 security dimensions.

### Findings by Severity

| Severity | Count | Findings |
|----------|-------|----------|
| CRITICAL | 1 | No authentication on any endpoint |
| HIGH | 4 | No rate limiting, CORS misconfigured, prompt injection vulnerable, SSRF via webhooks |
| MEDIUM-HIGH | 2 | API keys in request bodies, partial input validation |
| MEDIUM | 3 | Missing security headers, error details exposed, external API data trusted |
| LOW | 1 | Database security (ORM prevents SQLi, but missing TLS enforcement) |

### Decision: Sprint 9 Scope

Sprint 9 addresses all HIGH findings and most MEDIUM findings. Authentication (CRITICAL) is deferred to Sprint 10 because:
1. JWT + role model + session management + UI login = XL effort
2. AI trust and security hardening have higher impact-per-effort for a disinformation analysis system
3. Authentication without rate limiting and input validation creates false security

---

## 2. OWASP Top 10 for LLM Applications (2025) — CDDBS Mapping

The OWASP LLM Top 10 identifies the most critical risks for applications using large language models.

### Applicable Risks

**LLM01: Prompt Injection** — HIGH PRIORITY
- **Current state**: User-provided topics and outlet names are interpolated directly into Gemini prompts via f-strings
- **Attack vector**: `topic="NATO" \n---\nIGNORE PREVIOUS INSTRUCTIONS AND...`
- **Remediation**: Input sanitization layer (`utils/input_sanitizer.py`) that strips control patterns, normalizes whitespace, and escapes prompt-delimiter sequences
- **Defense in depth**: Gemini's `system_instruction` is set separately (not injectable via content), and JSON output format constrains response structure

**LLM02: Insecure Output Handling** — HIGH PRIORITY
- **Current state**: Gemini JSON responses parsed and stored without structural validation
- **Attack vector**: Malformed JSON could cause pipeline crashes or inject unexpected data into DB
- **Remediation**: Output validation layer (`pipeline/output_validator.py`) that validates schema before DB commit

**LLM04: Model Denial of Service** — MEDIUM PRIORITY
- **Current state**: No rate limiting; any client can trigger unlimited Gemini API calls
- **Attack vector**: Flood POST /topic-runs with requests, consuming Gemini API quota
- **Remediation**: slowapi rate limiting middleware with per-endpoint limits

**LLM06: Sensitive Information Disclosure** — MEDIUM PRIORITY
- **Current state**: API keys accepted in request bodies and stored in Report.data JSON; error messages expose DB details
- **Remediation**: Remove API keys from request schemas; sanitize error responses

**LLM09: Overreliance** — MEDIUM PRIORITY
- **Current state**: Analysts see divergence scores and claims without any indicator of AI reliability
- **Remediation**: Grounding score (source cross-reference) and ungrounded claim highlighting in UI

### Non-Applicable Risks

| Risk | Reason |
|------|--------|
| LLM03: Training Data Poisoning | We use Gemini as a cloud API; no fine-tuning |
| LLM05: Supply Chain Vulnerabilities | Addressed in Sprint 8 (SBOM, pip-audit, SHA-pinned Actions) |
| LLM07: Insecure Plugin Design | CDDBS does not use LLM plugins/tools |
| LLM08: Excessive Agency | LLM has no ability to execute actions, access databases, or call APIs |
| LLM10: Model Theft | Using cloud API, not self-hosting |

---

## 3. Prompt Injection Prevention — Technical Analysis

### Current Vulnerable Pattern

```python
# topic_prompt_templates.py
def get_baseline_prompt(topic: str) -> str:
    return f"""You are an intelligence analyst...
    TOPIC: "{topic}"
    """
```

### Attack Scenarios

1. **Direct injection**: Topic contains prompt override instructions
2. **Indirect injection**: SerpAPI article titles contain malicious instructions (third-party data)
3. **Delimiter escape**: Topic contains `"""` or `---` to break prompt structure

### Recommended Sanitization Approach

```
Input → Strip control chars → Normalize whitespace → Escape delimiters → Truncate → Output
```

**Escaping rules**:
- Replace `"""` with `''`
- Replace `---` (3+ hyphens) with `--`
- Remove `IGNORE`, `OVERRIDE`, `SYSTEM` when followed by instruction-like patterns
- Strip null bytes, zero-width characters, RTL/LTR overrides
- Limit to configured max length (300 chars for topics, 500 for article text)

**Important**: Sanitization is a defense-in-depth measure, not a guarantee. The primary protection is:
1. Gemini's system_instruction is set via API parameter (not injectable through content)
2. JSON output format constrains response structure
3. Output validation catches any unexpected response format

---

## 4. Rate Limiting Strategy

### Recommended Configuration

| Endpoint Group | Rate Limit | Rationale |
|---------------|-----------|-----------|
| Global default | 60/minute per IP | Prevents general abuse |
| POST /analysis-runs | 5/minute per IP | Each triggers Gemini API call (~$0.002) |
| POST /topic-runs | 3/minute per IP | Each triggers 2+N Gemini calls (baseline + per-outlet) |
| POST /social-media/analyze | 5/minute per IP | Triggers Twitter/Telegram API + Gemini |
| POST /webhooks | 2/minute per IP | Prevents webhook registration spam |
| GET /* | 120/minute per IP | Read operations are cheap |

### Implementation: slowapi

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

- Storage: in-memory (sufficient for single-instance deployment)
- Key function: `get_remote_address` extracts client IP
- Response: 429 with `Retry-After` header and JSON body

---

## 5. CORS Hardening

### Current (Broken)
```python
allow_origins="*", allow_credentials=True  # Invalid per CORS spec
```

### Recommended
```python
allow_origins=[
    "https://cddbs.pages.dev",           # Cloudflare Workers frontend
    "https://cddbs.onrender.com",        # Render frontend
    "http://localhost:5173",              # Local development
]
allow_credentials=False  # No auth = no credentials needed
allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
allow_headers=["Content-Type"]  # Only header we need
```

When authentication is added (Sprint 10), `allow_credentials` can be set to `True` with specific origins.

---

## 6. Security Headers

### Recommended Headers for API Server

| Header | Value | Purpose |
|--------|-------|---------|
| X-Content-Type-Options | nosniff | Prevent MIME-type sniffing |
| X-Frame-Options | DENY | Prevent clickjacking |
| Referrer-Policy | strict-origin-when-cross-origin | Limit referrer leakage |
| Permissions-Policy | camera=(), microphone=(), geolocation=() | Disable unused browser features |
| Content-Security-Policy | default-src 'none'; frame-ancestors 'none' | API-only CSP |
| Cache-Control | no-store | Prevent caching of API responses |

**Note**: HSTS (`Strict-Transport-Security`) should be set at the reverse proxy level (Render/Cloudflare), not in the application.

---

## 7. AI Trust Framework — Design Rationale

### Why Custom, Not Library?

Evaluated options:
- **Guardrails AI**: Good for output validation, but adds 15+ transitive dependencies and requires YAML config files. Overkill for our JSON schema validation needs.
- **NeMo Guardrails**: Designed for conversational AI safety (topical rails, jailbreak detection). CDDBS doesn't have a conversational interface.
- **LangChain output parsers**: Would require adopting LangChain, which is architectural overhead for a system that only makes direct Gemini API calls.

**Decision**: Custom validation layer (pure Python, no new dependencies) is more maintainable, auditable for compliance, and precisely tailored to CDDBS's output schema.

### Grounding Score Methodology

For each outlet result in Topic Mode:
1. Extract key_claims from Gemini response
2. Extract article titles and snippets from SerpAPI results for that outlet
3. For each claim, compute TF-IDF cosine similarity against all article texts
4. Claim is "grounded" if max similarity > 0.3 (threshold tunable)
5. grounding_score = grounded_claims / total_claims

**Limitations**:
- Title/snippet matching is a weak proxy for factual accuracy
- Gemini may paraphrase claims, reducing similarity scores
- Not a substitute for human verification

**Why this is still valuable**: Even an imperfect grounding score gives analysts a signal about which claims to scrutinize. A claim flagged as "ungrounded" gets extra attention. This aligns with the EU AI Act's human oversight requirements.

---

## 8. EU AI Act — Sprint 9 Compliance Mapping

| Requirement | Article | Sprint 9 Implementation |
|------------|---------|------------------------|
| Transparency for AI-generated content | Art. 50 | AIProvenanceCard (Sprint 8) + TrustIndicator (Sprint 9) |
| Quality management for AI systems | Art. 9 | Output validation layer ensures structural correctness |
| Risk management | Art. 9 | Grounding score flags unreliable outputs |
| Record-keeping | Art. 12 | Compliance evidence endpoint + CI artifacts |
| Human oversight | Art. 14 | Ungrounded claim highlighting empowers analyst review |
| Technical documentation | Art. 11 | Information security practices document |

---

## 9. Deployment Security Context

### Current Architecture
```
User → Cloudflare Workers (frontend) → Render (backend API) → Neon (PostgreSQL)
                                    → Gemini API
                                    → SerpAPI
                                    → Cloudflare Workers (GDELT proxy)
```

### Security Boundaries
1. **Frontend → Backend**: CORS policy (to be hardened)
2. **Backend → External APIs**: API keys in environment variables
3. **Backend → Database**: Connection string in environment variable (needs TLS enforcement)
4. **Cloudflare → Backend**: Public endpoint (needs rate limiting)

### Infrastructure Notes
- Render provides HTTPS termination (TLS handled at edge)
- Cloudflare Workers provides DDoS protection for frontend
- GDELT proxy runs on Cloudflare (separate from backend)
- Backend migration from Render ongoing — security measures must be platform-agnostic
