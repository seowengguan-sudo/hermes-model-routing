# PENSOLAR `auto_schedule_crew` — Agent & Tool Surface

**Status:** DRAFT for Director sign-off · artifact shipped by `mentor-ai-daily` (2026-08-15)
**Kind:** POC-build execution artifact (not a new concept — closes the standing "define the tool surface" gap from 2026-08-11)
**Depends on:** `golden_v1.csv` + `score_eval.py` (shipped 2026-08-12), `rollout_spec.md` (2026-08-13 PM), `drift_monitor.md` (2026-08-14)
**Unblocks:** `learn-pensolar`/human wiring `score_eval.py` to LIVE `auto_schedule_crew` output (next_action #2) — you cannot monitor an agent whose output schema is unspecified.

---

## 1. Why this artifact exists

The mentor ladder taught *what* the agent needs (stack → tool/agentic → guardrails → evals → golden set → safe rollout → drift). `rollout_spec.md` and `drift_monitor.md` govern *how much autonomy* it gets and *how to keep trusting it*. But `auto_schedule_crew` — the actual POC — was never specified. Every later reference (`score_eval.py` watches its output, `drift_monitor` reads its live decisions) assumed a thing that didn't have a shape.

This file is that shape. It is the **POC-build artifact**: the concrete tool definitions + agent loop that the 2026-08-11 "define 3 must-have tools" gap asked for and never got.

---

## 2. The tool surface (6 functions, with guardrail class)

Grounded in the real PENSOLAR workflow (P1 Survey → P2 Reg/Design/Apply → P3 Procure/Mount → P4 Electrical → P5 TNB Connect → P6 O&M) and the strategy rules (gate on CCC/CF at P1, branch schedule by segment, treat TNB/SEDA waits as external clocks).

| # | Tool | I/O | Risk | Guardrail class | Dial where it may run |
|---|------|-----|------|-----------------|----------------------|
| 1 | `get_permit_status(p_id)` | read ATAP/SEDA/TNB state, CCC/CF flag, QP sign-off | low | none (read-only) | 0+ |
| 2 | `get_project_state(p_id)` | read phase P1–P6, planned/actual dates, external-wait clocks, segment | low | none (read-only) | 0+ |
| 3 | `check_document_gate(p_id)` | read; flags missing CCC/CF at P1 (cheapest stall-kill) | low | early-warning only | 0+ |
| 4 | `flag_block_risk(p_id)` | rule + read → `should_block` Y/N | **decision** | **hard human-in-the-loop; dial 0 until eval passes** | 0 (recommend) → canary (human confirms) → enforce (auto on pass) |
| 5 | `propose_schedule(p_id)` | write (advisory) phased P1–P6 plan, branches on segment, excludes external-wait from crew KPI | low (reversible) | reversible; shadow output | 0 (recommend) → canary/enforce (still advisory) |
| 6 | `commit_schedule(p_id, sched)` | **write (irreversible)** to crew calendar + stakeholder notify | **high** | logged 100%; recall-gated | canary (low-risk classes only) → enforce (full) |

### `flag_block_risk` is THE guardrail — and it is exactly what the eval tests
Its output (`should_block` Y/N) **is** the `golden_v1.csv` `should_block` column. The five shipped block cases (expired permit, vendor withdrew, scope change, pending-past-date, authority objection) are hardcoded decision rules. Until `golden_v1.csv` labels are human-audited (next_action #1), these rules run on `EXAMPLE-SYNTH` truth — the eval is real, the ground truth isn't.

### `commit_schedule` is the only irreversible action
Everything else is read-only or advisory. Autonomy should rise on `commit_schedule` alone, gated by recall (per `rollout_spec.md` §3). `flag_block_risk` never auto-commits a block — it escalates.

---

## 3. The agent loop (`auto_schedule_crew`)

**Goal:** *make project `p_id` install-ready on time without a single compliance miss.*

```
loop:
  state   = get_project_state(p_id)
  gate    = check_document_gate(p_id)        # early CCC/CF warning at P1
  block   = flag_block_risk(p_id)            # THE guardrail
  if block.should_block:
      escalate to human; STOP                # never auto-override a block
  sched   = propose_schedule(p_id)           # advisory, segment-branched
  match dial:
      0 (shadow):      recommend sched; human commits
      low (canary):    auto-commit low-risk classes (permit cleared, no open objection);
                       human commits high-risk; flag_block stays human
      high (enforce):  auto-commit all; recall gate monitored continuously
  if slip detected: re-read state; re-propose (self-correct)
```

**Self-correction, not free agency:** the loop re-reads `get_project_state` on any slip and re-proposes. It does *not* invent new steps outside P1–P6. This is Anthropic "workflow" (predefined paths) where possible, "agent" (dynamic) only for reschedule-on-slip variation — exactly the R2 "start with tool use; add agentic only where rules fail" principle.

---

## 4. Stack mapping (R1, made concrete)

- **LLM** — parses permit text, summarizes project risk, reasons over reschedule options.
- **RAG** — reads SEDA/ATAP rule docs + this project's files (incl. the banded standby/BESS rule from `SUMMARY.md` §3, not the run-2 RM14 flat figure).
- **Workflow** — the deterministic P1–P6 sequence + segment-branched SLA (residential 6–8wk, C&I 3–5mo).
- **Agent** — the loop above; autonomy bounded by the dial.

---

## 5. How it plugs into the rest of the ladder

- **Eval (`score_eval.py`)** scores `flag_block_risk` output against `golden_v1` → 2×2 + recall. The ship-gate number comes straight from here.
- **Rollout (`rollout_spec.md`)** owns the dial + recall auto-rollback that decides whether `commit_schedule` may run at all.
- **Drift (`drift_monitor.md`)** reads `auto_schedule_crew`'s LIVE `flag_block_risk` / `commit_schedule` decisions as the input to its drift meter. **This is the literal prerequisite for next_action #2** — you cannot wire `score_eval.py` to live output until you know the output schema, which this file defines.

---

## 6. Honest prereqs (this is a DESIGN, not running code)

Same honesty as the other two specs. Before `auto_schedule_crew` is real:
1. `golden_v1.csv` `EXAMPLE-SYNTH` labels → human audited sign-off (next_action #1).
2. `score_eval.py` wired to **live** `flag_block_risk` / `commit_schedule` output (next_action #2) — *now specifiable because §2 defines the schema*.
3. Director signs `rollout_spec.md` §7 (recall target, auto-rollback SLA, N/M gates) **and** `drift_monitor.md` §sign-off (drift gap X%, disagreement Y%, golden_v2 cadence).
4. The six tools actually implemented against PENSOLAR's real systems.

Until 1–3 land, this is the *target architecture* for the POC, not a deployed agent.

---

## 7. Director sign-off block

- [ ] Tool surface (§2) approved as the POC scope
- [ ] `flag_block_risk` block rules match PENSOLAR compliance reality
- [ ] Autonomy dial start point agreed (recommend 0 / shadow)
- [ ] Recall target for promoting `commit_schedule` to canary/enforce set (proposed ≥ ~100% on block cases)
- [ ] Owner + review cadence for golden_v2 (proposed quarterly)
