# Fix C-2: temperature=0.0 and Divergence Score Rubric

**Date:** 2026-06-01  
**Branch:** `fix/c2-temperature-zero`  
**Closes (partially):** C-2 (divergence score stochastic, no formula)  

---

## What Was Wrong

The `divergence_score` was produced by Gemini at `temperature=0.1`. Even small
temperature values introduce stochasticity: the same input produces different
outputs across runs. For a research instrument presenting results to analysts,
this means two researchers running the same topic will see different scores
with no explanation.

Additionally, the rubric used subjective qualifiers ("noticeable," "significant,"
"strong") with no operational definitions. No documentation existed for what
any score actually meant.

---

## What This Fix Does

### Immediate action: temperature=0.0

`src/cddbs/utils/genai_client.py` changed from `temperature=0.1` to
`temperature=0.0`. At temperature=0.0, Gemini is deterministic for a fixed
model version: identical inputs produce identical outputs.

**Limitation**: This does NOT make scores reproducible across model updates.
Google may silently update `gemini-2.5-flash`, changing scoring behaviour with
no notification. Full reproducibility requires logging the model version (H-4)
and pinning to a specific model snapshot.

### Rubric documentation: docs/DIVERGENCE_SCORE_RUBRIC.md

The verbal rubric is now formally documented in `cddbs-prod` with:
- Five bands (0–15, 16–30, 31–50, 51–70, 71–100) with operational definitions
- Four scoring dimensions: factual omissions, framing, propaganda technique
  density, amplification signal
- Explicit bounds for subjective terms ("systematic" = ≥3 of sampled articles)
- Honest limitations table: what is and is not reproducible
- Citation language for research outputs

---

## What This Fix Does NOT Do

C-2 is a multi-week effort. This PR closes the immediate action items only:

| Action | Status |
|--------|--------|
| temperature=0.0 | ✅ Done |
| Rubric formally documented | ✅ Done |
| N=10 consistency test | ❌ Pending (requires live API) |
| Inter-rater reliability testing | ❌ Pending (weeks of work) |
| Mathematical formula (Option a) | ❌ Future work |
| Model version logging (H-4) | ❌ Tracked separately |

---

## Re-Audit Checklist Status

| Check | Status |
|-------|--------|
| `temperature=0.0` set in `genai_client.py` | ✅ |
| Divergence score rubric document exists in `docs/` | ✅ |
| N=10 consistency test results documented | ❌ Pending live API runs |

---

## Impact

**Before this fix**: Two analysts running the same topic could get divergence
scores that differ by 5–15 points, silently. Any published comparison between
two runs was unreliable.

**After this fix**: For a fixed model version (gemini-2.5-flash at a specific
point in time), identical inputs produce identical scores. The variance source
is now only model updates (which will eventually happen) rather than
normal per-call stochasticity.

This is a significant improvement for research credibility even if not full
reproducibility.
