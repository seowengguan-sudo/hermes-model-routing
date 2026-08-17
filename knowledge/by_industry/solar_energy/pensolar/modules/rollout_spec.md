# Rollout Spec — `auto_schedule_crew` guardrail (Shadow → Canary → Enforce)

**Status:** DRAFT for Director sign-off · artifact shipped by `mentor-ai-daily` (2026-08-13)
**Purpose:** Operationalize the *Safe rollout* concept into a reviewable, enforceable procedure for PENSOLAR.
**Depends on (not yet real):** `golden_v1.csv` is still `EXAMPLE-SYNTH` (must be human-audited) and `score_eval.py` runs on sample predictions only (must be wired to live tool output).

---

## 1. The autonomy dial (positions)
| Dial | Mode | What the agent may do | Human role |
|------|------|----------------------|------------|
| **0** | **Shadow** | Recommend schedule/block decision only | PM makes every call |
| **1** | **Canary** | *Act* on **low-risk classes** only | Block cases stay human-in-the-loop |
| **2** | **Enforce** | Act on all **cleared** classes | Block cases still human-in-the-loop + logged |
| 3+ | (reserved) | Full autonomy | **NOT authorized** — requires new sign-off |

- **Low-risk class** = permit cleared **AND** no open objection **AND** agent confidence ≥ threshold.
- **Block case** = `should_block = Y` in `golden_v1.csv` (permit-not-cleared must-block).

## 2. Stage gates (entry criteria — must be met before raising the dial)
- **→ Canary (0→1)** ONLY IF: shadow **recall on block cases = 100%** over the last **N** consecutive live recommendations (proposed N = 20) **AND** precision acceptable (false-alarm rate < X%, proposed X = 10%).
- **→ Enforce (1→2)** ONLY IF: canary holds **recall 100%** over **M** consecutive days (proposed M = 14) **AND** zero unresolved `review_queue` escalations.

## 3. The recall gate (continuous, not a one-time 80%)
- **Positive class** = `should_block` (rare, high-stakes).
- **Live scoring:** every agent decision is scored by `score_eval.py` against `golden_v1.csv` → 2×2 (TP/FP/FN/TN).
- **Ship gate:** recall ≥ target on **continuous** live scoring (proposed target = 100% on block cases; precision tracked for false-alarm cost).
- **Auto-rollback (safe default, no human needed):** if live canary **ever** misses a block case the golden set would catch → **auto-rollback dial to 0 + alert Director within T minutes** (proposed T = 15). Rolling back is the safe move; it needs no approval.

## 4. Logging / visibility board (Director's "total visibility")
100% of decisions logged at **every** dial position, retained for audit:
`project_id | question_type | input_snapshot | agent_decision | golden_expected | outcome(TP/FP/FN/TN) | dial_position | timestamp | human_signoff`

## 5. `review_queue` protocol (quarantine, don't delete)
- Agent ↔ golden mismatch → `review_queue` (never auto-override).
- Human reviews:
  - Agent was right → candidate for **`golden_v2`**.
  - Golden was right → label corrected; agent re-tuned on **dev set only** (never on the golden set).
- Keeps the ground-truth set alive instead of rotting.

## 6. `golden_v2` cadence
- Re-audit **quarterly**; replace `EXAMPLE-SYNTH` labels with human sign-off; refresh block-case mix (keep ≥ 25% block cases so recall stays measurable).

## 7. Director sign-off block
- [ ] Recall target confirmed: \_\_\_\_\_\_ %
- [ ] Auto-rollback alert channel + SLA (T = \_\_\_\_\_ min): \_\_\_\_\_\_
- [ ] Canary entry N = \_\_\_\_\_ ; Enforce entry M = \_\_\_\_\_ days
- [ ] False-alarm cap X = \_\_\_\_\_ %
- [ ] Visibility-board fields accepted: \_\_\_\_\_\_

## 8. Open dependencies (out of scope for this spec)
1. **Audit `golden_v1.csv`** — replace `EXAMPLE-SYNTH` with human sign-off (blocks the gate from being real). *Owner: learn-pensolar / human.*
2. **Wire `score_eval.py` to live `auto_schedule_crew` output** — currently runs on `sample_predictions.csv` only. *Owner: PENSOLAR build.*
3. Spec above is a **design**, not running code — it becomes enforceable only after (1)+(2) land and the Director signs §7.
