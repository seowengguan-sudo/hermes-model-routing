# Drift Monitor Spec — continuous re-audit for `auto_schedule_crew` (the permanent safe-rollout gate)

**Status:** DRAFT for Director sign-off · artifact shipped by `mentor-ai-daily` (2026-08-14)
**Purpose:** Operationalize the *Production drift & continuous re-audit* concept into a reviewable, enforceable procedure for PENSOLAR. This is the **permanent** version of the safe-rollout recall gate (`rollout_spec.md` §3): that gate protects autonomy *today*; this one protects *trust over time*.
**Pairs with:** `rollout_spec.md` (shadow → canary → enforce, recall-gated auto-rollback).
**Depends on (not yet real, same as rollout_spec §8):** `golden_v1.csv` is still `EXAMPLE-SYNTH` (must be human-audited) and `score_eval.py` runs on sample predictions only (must be wired to LIVE tool output).

---

## 1. The premise — your golden set and recall gate go stale
A frozen, audited golden set (R7) + scorer (R5) + recall-gated dial (rollout_spec) is the trust machine. The trap: treat it as *done*. Three flavors of drift, in PENSOLAR terms:
- **Data drift** — inputs change shape. TNB/authority SOP changes: a status that was "cleared" now needs a second sign-off. `golden_v1.csv` frozen at decision-time 2026-03-04 doesn't know.
- **Concept drift** — the rule moves. Vendor panel churns; a new EPC appears with a failure mode no historical project had. The `should_block` logic no longer covers reality.
- **Model/provider drift** — the LLM behind `auto_schedule_crew` gets a silent provider update; permit text parsed differently. Recall slips with **zero code change**.

`score_eval.py` vs `golden_v1` can read 100% recall while the tool misses real blocks *live* — because the golden set can't see a world that changed after 2026-03-04. Past correctness ≠ future correctness.

## 2. The drift meter — monitor LIVE, not just golden
- **Nightly `golden_v1` recall** = the *floor* (still useful; detect regressions in how you score).
- **Live / rolling-sample recall** = the *truth*. Hold a rolling sample of **new** real decisions (labeled as they close) and score against it nightly.
- **`drift_gap` = golden_recall − live_recall.** Your headline drift number.
- **`review_queue` disagreement rate** = early warning. A *rising* rate fires BEFORE any block is missed. Fed by the rollout_spec §5 quarantine protocol.
- **Block-case freshness** = days since the last *real* block case was labeled. If it grows unbounded, your set is silently shrinking coverage of live failure modes.

## 3. Alarm thresholds + auto-rollback (same gate as safe rollout)
| Signal | Proposed threshold | Action |
|--------|--------------------|--------|
| `drift_gap` | live recall < golden recall by > **X%** (proposed X = 2 pts) | declare drift → auto-rollback dial to 0 + alert Director (T min, reuse rollout_spec §3 SLA) |
| `review_queue` disagreement rate | > **Y%** (proposed Y = 15%) | same auto-rollback + alert |
| block-case freshness | > **Z days** (proposed Z = 90) with no new block label | force a re-audit (don't wait for quarter) |

Auto-rollback is the safe default and needs **no human approval** — identical to rollout_spec §3. Rolling back is the move that prevents the 2am call.

## 4. Drift response runbook (the loop, not a one-off)
1. On any alarm: auto-rollback dial to 0 + alert PM/Director (reuse rollout_spec §3 channel + SLA).
2. Quarantine the mismatched decisions to `review_queue` (don't delete — rollout_spec §5).
3. Human reviews: agent right → candidate for `golden_v2`; golden right → re-tune agent on **dev set only** (never on the golden set).
4. Re-label a **fresh decision-time sample** → promote `golden_v2` (frozen, versioned, never tuned-on). Keep ≥25% block cases so recall stays measurable.
5. Resume canary → enforce per rollout_spec §2 gates on the new set.

## 5. `golden_v2` cadence
- **Quarterly mandatory** re-audit (Run 7 discipline): replace `EXAMPLE-SYNTH` labels with human sign-off; refresh block-case mix.
- **Triggered early** on any confirmed drift alarm (§3) — don't wait for the quarter.
- Promote, don't patch: bump `golden_v2`, freeze it, never retune on it.

## 6. Integration with `rollout_spec.md`
- The drift alarm (§3) is the **same signal** as the safe-rollout recall gate (rollout_spec §3) — both auto-rollback to 0 + alert. Drift monitoring is the *standing* form; safe rollout is the *launch* form.
- The visibility board (rollout_spec §4) already logs `outcome(TP/FP/FN/TN)` per decision → that log is the **input** to the drift meter. No extra plumbing; you're already capturing it.
- `review_queue` (rollout_spec §5) is the **shared** quarantine that feeds both the launch gate and the golden_v2 promotion.

## 7. Prerequisites (honest — this spec is a design until these land)
1. **Wire `score_eval.py` to LIVE `auto_schedule_crew` output** — currently runs on `sample_predictions.csv` only. *Owner: PENSOLAR build.* Without live output, `drift_gap` and `review_queue` rate are uncomputable.
2. **Audit `golden_v1.csv`** — replace `EXAMPLE-SYNTH` with human sign-off. *Owner: learn-pensolar / human.* Without audited ground truth, the recall numbers measure agreement, not correctness.
3. Both specs (rollout_spec §7, this §sign-off) require Director sign-off before either is enforceable.

## 8. Director sign-off block
- [ ] Drift-gap threshold X = \_\_\_\_ % (recall points)
- [ ] Disagreement-rate threshold Y = \_\_\_\_ %
- [ ] Block-case freshness cap Z = \_\_\_\_ days
- [ ] golden_v2 cadence confirmed: quarterly + on-drift
- [ ] Alert channel + SLA reused from rollout_spec §3 (T = \_\_\_\_ min)
