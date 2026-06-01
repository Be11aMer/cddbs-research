# Fix C-3 / H-2: Output Validator Wiring + Retry Logic

**Date:** 2026-06-01  
**Branch:** `fix/c3-output-validator-retry`  
**Closes:** C-3 (silent Gemini failures), H-2 (output validator dead code)  

---

## What Was Wrong

### C-3 — Silent Failures
`call_gemini()` in `genai_client.py` had zero retry logic. Any transient error
(rate limit, network timeout, Gemini 5xx) was caught and returned as a string
`"[Gemini error: ...]"` that was then parsed and stored as a valid result.
On free tier (250 req/day, 10 req/min), a 5-outlet topic run consumes 7 calls.
A mid-run rate limit left partial data in the DB with no status flag.

### H-2 — Dead Validator
`output_validator.py` was fully implemented and tested, but never called from
`orchestrator.py` or `topic_pipeline.py`. Every Gemini output was stored without
a quality gate regardless of schema compliance or content validity.

---

## What Was Changed

### `src/cddbs/utils/genai_client.py`
- Added 3-attempt exponential backoff: 2s → 4s → 8s with ≤25% jitter
- Fixed model to read from `settings.GEMINI_MODEL` (was hardcoded `"gemini-2.5-flash"`)
- Total: 4 attempts per call (1 initial + 3 retries)

### `src/cddbs/models.py`
- `Report`: added `analysis_status` column (`completed`/`partial`/`failed`)
- `TopicOutletResult`: added `analysis_status` and `validation_warnings` columns
- `Briefing`: added `validation_warnings` column

### `src/cddbs/database.py`
- Added 4 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` migrations for new columns
- Safe to re-run on every boot (idempotent)

### `src/cddbs/pipeline/orchestrator.py`
- Added `from src.cddbs.pipeline.output_validator import validate_analysis_output`
- Calls `validate_analysis_output(payload)` before `session.add(briefing)`
- Sets `report.analysis_status` = `"completed"` or `"partial"` based on result
- Stores `validation.errors + validation.warnings` in `briefing.validation_warnings`

### `src/cddbs/pipeline/topic_pipeline.py`
- Added `from src.cddbs.pipeline.output_validator import validate_topic_comparative`
- Calls `validate_topic_comparative(comp)` after each Gemini comparative call
- Sets `analysis_status = "failed"` if Gemini returned empty, `"partial"` if schema invalid, `"completed"` otherwise
- Stores warnings in `TopicOutletResult.validation_warnings`

---

## Re-Audit Checklist Status

| Check | Status |
|-------|--------|
| `call_gemini()` has 3-attempt exponential backoff | ✅ |
| `analysis_status` field on `TopicOutletResult` | ✅ |
| `analysis_status` field on `Report` | ✅ |
| `validate_topic_comparative()` called before `session.add(result)` | ✅ |
| `validate_analysis_output()` called before `session.add(briefing)` | ✅ |

---

## Deployment Notes

1. DB migrations run automatically on next Render deploy (in `init_db()`)
2. Existing rows will get `analysis_status = 'completed'` as the DEFAULT
3. No breaking API changes — new fields are additive
4. Monitor Render logs for `"Output validation failed"` entries on first run

---

## Remaining Gaps (Not This PR)

- `analysis_status` is not yet surfaced in the API response schemas (frontend needs update)
- `validation_warnings` stored but not exposed in any API endpoint
- The grounding score (`compute_grounding_score`) is still not called — requires
  extracting claim lists from Gemini output (future work)
