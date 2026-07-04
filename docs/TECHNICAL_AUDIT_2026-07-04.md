# CDDBS Technical Re-Audit & Pilot-Readiness Evaluation

**Date:** 2026-07-04
**Auditor:** Claude Code
**Repositories:** `be11amer/cddbs-research` · `be11amer/cddbs-prod`
**Audience:** Developer (Bellamer) + Cyber Intelligence Institute (CII) pilot / federal-ministry budget review
**Predecessor:** `docs/TECHNICAL_AUDIT_2026-06-01.md`

---

## Executive Summary

Since the June audit, CDDBS has closed most of its findings with real, verifiable code — not just checklist ticks. Eight of the eleven Critical/High/Medium findings are genuinely fixed: deterministic sampling (`temperature=0.0`), app-wide API-key authentication with Argon2id hashing, retry/backoff on the LLM client, output-validator wiring, model-version logging, baseline caching, structured logging, and a DISARM-grounded propaganda taxonomy that stores both raw and normalised tags. For a solo-built research prototype this is an unusually strong engineering baseline, and the self-documenting rubric/protocol files show good methodological hygiene.

However, **the project is not yet ready to be presented as a CII/federal pilot**, for two independent reasons.

**First, a security regression undoes the headline fix.** The Sprint 10 authentication is correctly implemented on the server — but the single shared API key that gates the *entire* backend is baked into the public JavaScript bundle served to every visitor of the public frontend. Anyone who opens the site can read the key from the static asset. The server-side control is sound; in production it protects nothing against a motivated external actor. On top of this, changes merged *after* the June audit introduced new attack surface that was never reviewed: a webhook Server-Side Request Forgery (SSRF) primitive and an automated, unauthenticated prompt-injection path via the June auto-analysis feature.

**Second, the single most important methodology item is still open.** The June audit called measuring the divergence score's run-to-run variance "the single highest-priority pre-CII action." The consistency-testing harness and protocol were built — but **the test has never been run**, so the reproducibility of the system's headline metric remains literally unknown. No security threat model exists either. These are days of work, not months — but until the numbers and the documents exist, a federal reviewer would (correctly) withhold sign-off.

**Bottom line for the pilot question:** solid and impressive as an R&D prototype; **not yet a citable, deployable research instrument.** The remaining gap is now measured in days-to-weeks of focused work plus a redeployment, not another engineering quarter.

---

## Part 1 — Re-Audit of Prior Findings

Verdicts verified against source (file:line) and, where possible, the live deployment. The live API (`cddbs-api.onrender.com`) was **not reachable from the audit environment** (network policy blocks the host at the proxy layer), so production-runtime state of auth is inferred from repo config and noted as such.

| ID | Prior finding | Verdict | Evidence |
|---|---|---|---|
| **C-1** | No auth on any endpoint | **PARTIAL — mechanism fixed, defeated in production** | `api/auth.py:79-109` middleware, Argon2id (`:30-36`), fail-closed (`:61-76`); **but** key baked into public bundle — see [N-1] |
| **C-2** | Divergence score non-deterministic | **FIXED (Option b)** | `temperature=0.0` `genai_client.py:30`; rubric `docs/DIVERGENCE_SCORE_RUBRIC.md`. Deterministic formula (Option a) still future work |
| **C-3** | No retry; silent permanent failures | **PARTIAL** | Retry FIXED (`genai_client.py:10-42`, 2/4/8s+jitter); topic pipeline sets status; **but** `orchestrator.py:115` never sets `failed` — Gemini-error string still stored as `final_report` with status `completed`; status not surfaced in API/UI |
| **H-1** | `ALLOWED_ORIGINS:"*"` in render.yaml | **FIXED** | Override removed; allowlist `config.py:18`; `allow_credentials=False`, `main.py:85-91` |
| **H-2** | Output validator not wired | **FIXED** | `topic_pipeline.py:339`, `orchestrator.py:114`; warnings persisted |
| **H-3** | External article content unsanitised | **PARTIAL** | Two named files fixed w/ UNTRUSTED markers; `sitrep.py`, `social_media_pipeline.py`, `auto_trigger.py` paths still unsanitised — see [N-3] |
| **H-4** | Model version not logged | **FIXED** | `genai_client.py:27` reads `settings.GEMINI_MODEL`; `model_version` columns populated |
| **M-1** | No propaganda taxonomy | **FIXED** | `data/propaganda_techniques_taxonomy.json` (23 techniques, DISARM + SemEval-2020 + EU DisinfoLab); raw+normalised stored `topic_pipeline.py:355` |
| **M-2** | Baseline reconstructed per run | **FIXED** (one flag) | `TopicBaseline` table + `baseline_id` FK; reuse `topic_pipeline.py:197-213`. Flag: a *failed* baseline is cached and reused indefinitely — see [N-5] |
| **M-3** | `print()` as production logging | **PARTIAL** | orchestrator/topic_pipeline clean; residual `print()` in `fetch.py` (5×), `social_media_pipeline.py` (2×) |
| **M-4** | No consistency-testing protocol | **NOT DONE (harness only)** | `scripts/consistency_test.py` + `docs/CONSISTENCY_TEST_PROTOCOL.md` built, but **no results file exists**; rubric doc admits "N=10 pending / blocked on live API" |
| **L-1** | research main unprotected | Not re-verified (GitHub settings) | — |
| **L-2** | Narrative matching = keyword overlap | **PARTIAL** | Still substring match (`narratives.py:47`); UI tooltip says "keyword matches" (`NarrativeTags.tsx:129`) but outputs still use "confidence" language, no explicit "indicator not confirmation" disclaimer |
| **L-3** | Render free tier | **NOT DONE** | `render.yaml:32` still `plan: free` |

**Score:** 8 of 11 C/H/M findings fully closed. C-1, C-3, H-3 are partial; M-4 (the highest-priority one) is effectively open.

---

## Part 2 — New Findings (introduced or discovered since 2026-06-01)

### [N-1] CRITICAL — Backend API key is embedded in the public frontend bundle

**Location:** `frontend/src/api.ts:13-14`; `frontend/Dockerfile:15-19`; `README.md:9-10`
**Description:** The frontend sends `X-API-Key: import.meta.env.VITE_API_KEY`. Vite performs static string substitution at build time, so the literal key is compiled into the JS. The Dockerfile bakes `VITE_API_KEY` into `/app/dist` at `npm run build`. Per `api.ts:10-11` this value equals `CDDBS_BOOTSTRAP_API_KEY` — the single key protecting the whole backend. Both frontends are publicly deployed. Therefore any visitor can extract the key from a static asset and gain full authenticated access.
**Risk:** The Sprint 10 auth (C-1) provides no real protection against an external attacker — only against a casual anonymous `curl`. All "protected" mutation and Gemini-cost endpoints are reachable. Additionally `/compliance/evidence` (`main.py:2597`) advertises `api_key_hygiene: "server_side_only"`, which is factually false — a compliance-integrity problem for a federal submission.
**Recommendation:** A browser-delivered SPA cannot hold a shared secret. Options: (a) per-user auth (login → short-lived token minted server-side, the JWT+RBAC originally planned for Sprint 10); (b) a thin backend-for-frontend / proxy that injects the key server-side so it never reaches the browser; (c) at minimum, a *separate, low-privilege, rate-limited* frontend key distinct from the admin bootstrap key. Correct the `/compliance/evidence` claim regardless.

### [N-2] HIGH — Webhook endpoint is an SSRF primitive

**Location:** `api/main.py:2239-2260` (`POST /webhooks`); `webhooks.py:48-52` (`deliver_webhook`)
**Description:** `POST /webhooks` validates event types but stores an arbitrary `url` with no scheme/host/private-range validation. `deliver_webhook` then performs a server-side `httpx.post(url, ...)` on burst/failure events and on `POST /webhooks/test/{id}`. No allowlist, no block on private/link-local ranges.
**Risk:** Server-side requests to internal services or cloud metadata (`http://169.254.169.254/…`), reachable by anyone holding the (public — see N-1) key. No rate limit on webhook routes compounds this.
**Recommendation:** Validate the URL: require `https`, resolve and reject private/loopback/link-local/metadata ranges (deny `169.254.0.0/16`, RFC1918, `::1`, etc.), enforce an egress allowlist if feasible. Add rate limiting to all webhook routes.

### [N-3] HIGH — Automated, unauthenticated prompt-injection surface via auto-analysis

**Location:** `pipeline/auto_trigger.py:50-115` (commit `152502e`, 2026-06-09); `sitrep.py:38-101`; `social_media_pipeline.py:28-61`
**Description:** The June auto-analysis feature runs after the collectors ingest RSS/GDELT articles — no user request, no auth, no rate limit — and feeds untrusted article content into the **unsanitised** SitRep prompt and into `run_topic_pipeline` with an unsanitised `cluster.title` (bypassing the topic sanitisation applied at the manual endpoint, `main.py:973`). Separately, `sitrep.py` interpolates raw article titles/content and `social_media_pipeline.py` interpolates raw bios/posts directly into Gemini prompts. H-3's fix only covered `orchestrator.py` and `topic_pipeline.py`.
**Risk:** An adversary who merely gets an article indexed by the collectors can attempt prompt injection against the analysis LLM with zero authentication and zero rate limiting — a strictly larger surface than the manual endpoints H-3 considered.
**Recommendation:** Apply `sanitize_text()` + `[BEGIN/END UNTRUSTED …]` markers to every external field in `sitrep.py`, `social_media_pipeline.py`, and the `auto_trigger.py` path (topic title). Treat "any text entering a prompt" as the sanitisation boundary, not a per-endpoint list.

### [N-4] MEDIUM — Rate-limiting gaps on expensive/mutation endpoints

**Location:** `main.py:2434` (`/threat-briefings/quarterly`), `:1748` (`/stats/source-credibility/refresh`), `:623` (`/feedback`), all `/webhooks*` routes
**Description:** These lack `@limiter.limit` (unlike analysis/topic/social endpoints). The quarterly and refresh endpoints trigger Gemini calls. Given the public key (N-1) they are effectively open to cost-amplification (LLM DoS) and unbounded row insertion.
**Recommendation:** Add `@limiter.limit` to all mutation and LLM-triggering endpoints.

### [N-5] LOW — Failed baseline cached indefinitely; misc.

**Location:** `topic_pipeline.py:262-270`; `models.py:88-91`
**Description:** If a baseline `call_gemini()` returns the `"[Gemini error: …]"` sentinel, `baseline_raw` is still written to `TopicBaseline` and reused indefinitely (manual invalidation only). Also: `/docs` + `/openapi.json` are unauthenticated (full schema disclosure — minor); retry/backoff and `analysis_status`-setting behaviour are untested despite 277 prod tests.
**Recommendation:** Guard the baseline path with a validity check before caching; consider gating `/docs` in production; add tests for retry and status transitions.

---

## Part 3 — Methodology & Research-Instrument Readiness

The security items above are fixable engineering. The items below are what a **research/federal-methodology reviewer** will actually block on.

| Dimension | State | Pilot-ready? |
|---|---|---|
| Infrastructure (Docker, CI, tests) | Strong; CI green on main; 277 prod + 80 research tests | ✓ |
| Authentication (design) | Argon2id middleware, fail-closed | ✓ (design) |
| Authentication (production) | Shared key public in bundle | ✗ (N-1) |
| Divergence-score reproducibility | `temperature=0.0` + documented rubric | Partial |
| **Consistency measurement (N=10 variance)** | **Harness built, never run — variance unknown** | ✗ (M-4) |
| Propaganda taxonomy | DISARM-grounded, raw+normalised stored | ✓ |
| Output validation | Wired; warnings stored (not surfaced) | Partial |
| Audit trail | Model version + status stored; not exposed via API | Partial |
| Threat model document | **Does not exist** | ✗ |
| Supply chain | SBOM, pip-audit, pinned SHAs, dependency scanner | ✓ |
| Compliance documentation | Substantive but partly stale (README dated 2026-03-18, pre-Sprint 9) | Partial |
| Operational tier | Render Postgres still free (90-day expiry) | ✗ (L-3) |

**Reproducibility verdict:** still **NO** — the headline metric's stability has not been measured.
**Greatest research-credibility risk:** unchanged from June — the divergence score has no mathematical derivation *and* its empirical variance is undocumented.
**Greatest security risk:** the production auth is defeated by the public frontend key (N-1).

---

## Part 4 — Prioritised Immediate Next Steps

Ordered for a pilot decision. The first three are the true blockers.

| # | Priority | Action | Location | Effort |
|---|---|---|---|---|
| 1 | **CRITICAL** | Stop shipping the backend key to the browser: introduce per-user login or a server-side proxy/BFF, or at minimum a separate low-privilege rate-limited frontend key. Fix the false `server_side_only` compliance claim. | `frontend/`, `api/auth.py`, `main.py:2597` | 2–4 days |
| 2 | **CRITICAL** | **Run the N=10 consistency test** on the canonical topic; commit `docs/CONSISTENCY_TEST_RESULTS.md` with mean/stdev/range. If variance >10 pts, act on it. This is the #1 pre-CII item. | `scripts/consistency_test.py` | 1–2 days (API-billed) |
| 3 | **HIGH** | Add SSRF validation to the webhook URL path; add rate limits to webhook + quarterly + refresh + feedback endpoints. | `webhooks.py`, `main.py` | 1 day |
| 4 | **HIGH** | Sanitise all remaining prompt-entry points (SitRep, social media, auto-analysis topic). | `sitrep.py`, `social_media_pipeline.py`, `auto_trigger.py` | 0.5 day |
| 5 | **HIGH** | Fix orchestrator error handling: detect the Gemini-error sentinel, set `analysis_status="failed"`, never store the error string as a briefing. | `orchestrator.py:92-123` | 0.5 day |
| 6 | **MEDIUM** | Surface `analysis_status`, `validation_warnings`, `model_version` in API responses + frontend (the human-oversight signal). | `main.py` response models, `frontend/` | 1 day |
| 7 | **MEDIUM** | Write a real security threat model (STRIDE / trust boundaries / attack surface) — required for BSI-ANSSI / CII framing. | `docs/` | 2–3 days |
| 8 | **MEDIUM** | Guard the baseline cache against caching failed baselines. | `topic_pipeline.py` | 0.5 day |
| 9 | **LOW** | Refresh compliance README to Sprint 9/10; upgrade Render Postgres off free tier; add the L-2 "keyword-based indicator" disclaimer to outputs. | research repo, `render.yaml`, outputs | 1 day |

**Honest timeline to a defensible pilot demo:** roughly **1–2 weeks** of focused work (items 1–5) plus a redeployment — down from the June estimate of "3 months," reflecting how much has genuinely shipped. The methodology *foundation* is ready; what's missing is the measurement (item 2) and closing the security regression (item 1).

---

## Re-Audit Checklist (for the next pass)

- [ ] N-1: backend key no longer present in any public JS asset; `/compliance/evidence` claim corrected
- [ ] N-2: webhook URL validated (private/metadata ranges rejected); webhook routes rate-limited
- [ ] N-3: `sanitize_text()` + UNTRUSTED markers in `sitrep.py`, `social_media_pipeline.py`, `auto_trigger.py`
- [ ] N-4: rate limits on quarterly / refresh / feedback / webhook endpoints
- [ ] C-3: `orchestrator.py` sets `failed` on Gemini error; error string never stored as `final_report`; status in API + UI
- [ ] M-4: `docs/CONSISTENCY_TEST_RESULTS.md` exists with N=10 variance numbers
- [ ] Threat model document present in `docs/`
- [ ] N-5: failed baselines not cached; retry/status tests added
- [ ] L-3: Render Postgres off free tier

---

*Live-deployment note: the production API host was unreachable from the audit environment (blocked by network policy at the proxy). All runtime claims about deployed auth are inferred from repository configuration and should be confirmed against the live instance — in particular, whether `CDDBS_BOOTSTRAP_API_KEY` and `VITE_API_KEY` are set in the Render dashboard, which determines whether auth is active at all and whether N-1 is live.*
