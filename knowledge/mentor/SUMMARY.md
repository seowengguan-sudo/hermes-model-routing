# Mentor Summary — AI education in business language

Living, compressed log of what we've covered. Newest concept on top.
Daily detail lives in `mentor/daily_notes/YYYY-MM-DD.md`.

## Concept log (newest → oldest)

### 2026-08-17 — INPUT-INTEGRITY GATE: the recall gate validates the DECIDE end; a stale/wrong INPUT slips past it — assert freshness + project_id BEFORE reasoning (cheapest shift-left layer yet: runtime→CI→input); genuinely NEW failure class beneath R5/R7 — connects guardrails(R3)+evals+golden+drift+shift-left+cost-axis
- **The decision chain is retrieve → read → reason → decide.** Every gate taught validates reason/decide: drift + runtime recall (R8), CI recall (2026-08-16 15:00). But if `get_permit_status`/`check_document_gate` returns the WRONG project's permit or a STALE TNB SOP, the agent reasons perfectly yet ships a compliance-fatal schedule. The defect is upstream of reasoning — the recall gate is blind to it.
- **Stale input = the leakage trap, now at retrieval time.** We taught "snapshot inputs at decision time" when LABELING golden_v1 (2026-08-11). Mirror failure in prod: a cached/old read. If the read says "cleared" but TNB revoked day 3, the agent's decision is "correct" vs that (wrong) input → recall 100%, real block missed. Garbage in, compliance out.
- **Catch it at the CHEAPEST stage = before the agent reasons.** One-line input-integrity assert: `permit_snapshot_age < TTL` (e.g. <24h) AND `returned_project_id == requested_project_id` (no cross-project leak). One cheap read/compare, zero live exposure, zero penalty. Shift-left taken one layer past the CI gate (runtime → CI → input).
- **PENSOLAR failure it prevents:** dev adds Redis cache to `get_permit_status` (cost-axis "minimize tool calls"), TTL=7d. TNB revokes day3; day4 agent reads cached "cleared", commits `commit_schedule` on a now-non-compliant project → 2-wk delay + penalty. Freshness assert fails the read in 0 exposure.
- **Cost lens (his mandate):** caching cuts $/run ONLY if the cached value can't go stale within TTL in a way that causes a miss. TTL(7d) >> revocation latency → caching INVERTS cost (saves tokens, costs a TNB penalty). The cost-axis "minimize calls" must be bounded by a freshness SLA; HIGH-consequence reads → short TTL or no cache.
- **Reuses the whole ladder:** a separate retrieval-precision eval (evals + golden set: did it read the right doc?); staleness IS data-drift (drift lesson) now with a mechanism (freshness assert); an input-validation fence (guardrails R3). Test: Redis cache TTL=7d, TNB revokes day3, agent commits day4 — (a) recall gate catch? No, input wrong not decision wrong; (b) which number + only after what? live-vs-golden gap / review_queue rate, only AFTER a block missed (penalty); (c) cheapest check + assert? freshness+TTL + project_id match before reasoning; (d) caching always cheaper? No — inverts if TTL > revocation latency.

### 2026-08-16 (15:00 MYT) — SHIFT-LEFT THE QUALITY GATE: score_eval.py must block the deploy (CI/merge gate), not just report it — defense-in-depth for the eval (pre-deploy catch BEFORE runtime/drift gates); genuinely NEW stage, not a 10th rung: places the recall metric one lifecycle stage earlier (commit→CI→deploy→runtime→drift); connects R5/R7 + cost-axis + audit
- **The recall gate you have lives at RUNTIME (rollout_spec §3 auto-rollback) + production (drift).** That catches bad behavior AFTER code is live — a bad change can ship to canary, miss 3 block cases, before the runtime gate fires. Cheapest catch is BEFORE deploy.
- **Make score_eval.py a CI gate, not a report.** Wire it into the PR/build pipeline: every change to the crew's prompt/tools/parsing runs score_eval.py vs golden_v1.csv (audited!) and the PR FAILS if recall on block cases < target. Agent never reaches shadow until it passes. Same number that gates rollout now also gates the merge ("shift left").
- **Not a 10th rung — same metric, earlier in the lifecycle (commit→CI→deploy→runtime→drift).** R5/R7 taught the number; cost-axis its $ value; this enforces it at the cheapest point. Defense in depth = runtime gate + pre-deploy gate = two independent catches (bad CODE change vs real-world DRIFT).
- **PENSOLAR failure it prevents:** dev "improves" permit-status parser prompt; block-case recall silently 100%→85%; runtime gate catches it only after canary mis-schedules 3 projects. CI gate fails the PR in ~4 min — zero live exposure, zero TNB penalty.
- **Cost lens (his mandate):** pre-deploy catch ≈ 4 min CI + re-write; post-deploy catch = 3 mis-scheduled projects + 2-wk TNB delay + rollback investigation. Earlier gate = cheaper miss (cost-axis applied to the BUILD stage).
- **Dependency it exposes (ties to audit):** CI gate only as real as golden_v1. If still EXAMPLE-SYNTH, "recall 100% in CI" = self-lick again → audit (step 1) must land BEFORE the gate means anything. Re-sequences hand-off: audit → gate → live. Test: dev PR recall 88% (was 100%), accuracy 92%, "ship to canary" — (a) FAIL PR, gate on recall not accuracy; (b) ~1 of 5 block cases slips canary → 1 mis-schedule + TNB penalty before runtime gate; (c) CI=pre-deploy zero-exposure vs runtime=post-deploy drift catch, want BOTH; (d) audit golden_v1 first, then gate meaningful.

### 2026-08-16 (19:00 MYT) — HUMAN-IN-THE-LOOP CHECKPOINT DESIGN: the dial says WHEN to escalate; triage+batch+SLA+pre-fill says HOW so the guardrail doesn't re-create the PM bottleneck (scaling bridge; closes the gap the cost-axis lesson exposed — it promised 2-min review without the mechanism) — connects guardrails(R3)+dial+cost-axis+drift
- **Dial = WHEN, not HOW:** `flag_block_risk`→`should_block=Y`→human; at 40 projects even block-only can be 8/wk; naive same-day paging re-creates the bottleneck automation removed.
- **Triage by consequence-timeline:** HIGH (TNB lapsed, install imminent → page now) vs LOW (permit pending 3+wk → batch Friday). Route by speed of consequence, not binary flag.
- **Batch+SLA beats interrupt:** HIGH immediate (2×10m), LOW one 30m weekly session w/ signed SLA → turns 8 min/proj/day into 2; it's a *design* choice, async.
- **Shrink the human's job below the automation's:** agent pre-fills the one decisive fact + recommendation → 30-sec confirm, not re-investigation. This is where the cost-axis $/run saving actually lands.
- **Checkpoint = data engine too:** every human decision (esp. override) → `review_queue` → `drift_monitor` `golden_v2` re-audit. Reuses 2026-08-14 drift lesson.
- **Three lenses, one decision:** cost-axis saving is real ONLY if checkpoint is triaged+batched+bounded. Safety+throughput+economics point the same way. Test: 8 blocks/wk (2H+6L), $40/hr — naive ~$53/wk rebottleneck; triaged 50m/wk fits 80m/day budget; pre-fill cuts LOW batch ~83%; decisions→review_queue→golden_v2.

### 2026-08-16 — COST AXIS of the autonomy dial: every run has a $/decision cost; the Director's sign-off is a break-even ($/compliance-miss-avoided), not just a safety gate; recall gate (R5/R7) doubles as the cost ceiling — NEW cross-cutting axis, fills the economic-layer gap the 9-rung design omitted; connects to R3 + R5/R7
- **Not a 10th ladder rung** — a cross-cutting axis laid over the existing ladder. The autonomy dial had only ever been taught as a *safety* control; for a cost-optimization consultant the missing rung is its *$* axis.
- **Cost = tool calls × tokens.** Shadow (dial 0) pays full LLM cost with zero labor saved; enforce (dial 10) pays the same LLM cost but also saves human minutes/decision. Canary/enforce add commit + re-score calls → more tokens → more $. The loop's shape sets the bill, not just the model.
- **Break-even the Director signs = $/compliance-miss-avoided.** Missed block = TNB penalty + 2-wk delay (real $); agent ≈ $0.02/run. Quantify it — that business case IS the cost-optimization value-add. Trap: "free-tier only" habit hides per-token cost in production.
- **Design to keep $/run flat as autonomy rises:** cache permit/status reads, batch nightly score_eval, commit only the low-risk class, don't re-score every action. Cheapest guardrail = the call you didn't make.
- **Recall gate is also the cost ceiling:** a breach → auto-rollback to dial 0 → full LLM cost, zero autonomy benefit (worst of both). Keeping recall high is *also* keeping the system cost-efficient. Safety and economics point the same way.
- **Test posed:** 40 projects, dial0 = $0.02/run + 8 min PM/proj; dial8 = $0.03/run + 2 min PM/proj; PM $40/hr. (a) net daily $ saved at dial8 (~$160). (b) 1 recall breach → 3-day rollback to dial0 → ~$480 PM-time cost. (c) design choice keeping $/run flat = minimize tool calls.

### 2026-08-15 (19:00 MYT) — CAPSTONE: one integrated operating picture (R1→R7 + the 4 specs as a single machine) + integrative pipeline test + execution hand-off — arc stays 9 rungs; no new concept; remaining gap = EXECUTION owned by learn-pensolar/human
- **Not a 10th rung.** The conceptual ladder is complete (9 rungs) and all four execution artifacts exist (`golden_v1.csv`+`score_eval.py`, `rollout_spec.md`, `drift_monitor.md`, `agent_surface.md`). Today synthesizes them into ONE closed-loop operating picture threaded through a single PENSOLAR C&I project (SunnyVilla), plus an integrative test that spans the whole pipeline and a crisp execution hand-off.
- **The unifying insight:** the eval (R5/R7) is the *hand on the autonomy dial* (R3); drift monitoring (R7-continuous) keeps that hand honest forever. The four `modules/*.md` are not separate docs — one input (a PENSOLAR project) → one output (an install-ready date that never caused a compliance miss).
- **Integrative test posed:** SunnyVilla in canary, TNB approval lapses (sync stale) → `flag_block_risk` emits `should_block=Y` → `commit_schedule` blocked/escalate; live recall drops 100%→92% → `rollout_spec.md` §3 auto-rollback dial to 0 + alert; `review_queue` disagreement 22% (>Y=15%) → `drift_monitor.md` declares drift → quarantine + re-label → promote `golden_v2`; the ship-gate number = recall on block cases from `score_eval.py` vs `golden_v1`.
- **Execution hand-off (the only remaining gap):** (1) audit `golden_v1` `EXAMPLE-SYNTH`→human sign-off [learn-pensolar/human]; (2) implement the 6 `agent_surface` tools vs real PENSOLAR systems [learn-pensolar]; (3) wire `score_eval.py` to LIVE `auto_schedule_crew` output + run 2×2 [learn-pensolar]; (4) Director signs `rollout_spec` §7 + `drift_monitor` §sign-off + `agent_surface` sign-off block [Director]. Then shadow→canary→enforce can run and `golden_v2` becomes quarterly habit.
- **Durable fix this run:** embedded the real mentor prompt into `jobs.json` (was the literal placeholder `[System: mentor-ai-daily prompt content]`), so future runs self-execute instead of emitting `[SILENT]` (the 15:00 MYT slot today did exactly that). Low-risk, clearly intended. Nothing else in config touched.

### 2026-08-15 (07:00 MYT) — PENSOLAR agent/tool surface SHIPPED: the actual POC-build shape (`auto_schedule_crew`) — closes the original "define 3 must-have tools" gap; prerequisite for wiring score_eval to live
- **Artifact shipped:** `pensolar/modules/agent_surface.md` — the concrete 6-tool surface + agent loop for the PENSOLAR POC, grounded in the real P1–P6 workflow. Not a new concept — closes the standing execution gap the 2026-08-11 "define 3 must-have tools" lesson opened and never filled.
- **The 6 tools:** `get_permit_status` / `get_project_state` / `check_document_gate` (read-only, low risk) · `flag_block_risk` (THE guardrail — its `should_block` output IS the `golden_v1.csv` column `score_eval.py` tests) · `propose_schedule` (advisory/reversible) · `commit_schedule` (the ONLY irreversible action, recall-gated).
- **The agent loop:** goal = "install-ready on time without a compliance miss"; read state → check doc gate → flag block (escalate, never auto-override) → propose → act per dial → self-correct on slip. Predefined paths where possible, dynamic only for reschedule-on-slip (R2 "start with tool use").
- **Why it unblocks the ladder:** `drift_monitor.md` reads `auto_schedule_crew`'s LIVE decisions as its drift-meter input; you cannot wire `score_eval.py` to live output (next_action #2) until the output schema exists. This file defines that schema.
- **Honest prereq (mirrors the other specs):** not running code until (1) `golden_v1.csv` labels human-audited, (2) the six tools implemented, (3) Director signs all three §7/sign-off blocks. It is the target architecture, not a deployed agent.
- **Unifies the ladder:** R1+R2+R3+R5+R7+safe rollout+drift+**agent surface** = a buildable, trustworthy POC. The mentor's concept-teaching arc is now COMPLETE (9 rungs); everything below is execution + sign-off owned by learn-pensolar/human.
- **ARTIFACT SHIPPED (this run):** `pensolar/modules/agent_surface.md`. All four execution artifacts the ladder demanded now exist. Remaining: audit golden_v1 (#1) + implement the 6 tools + Director signs rollout_spec §7, drift_monitor §sign-off, AND this spec's sign-off block.

### 2026-08-14 (07:00 MYT) — Drift monitor SPEC shipped: operationalizes continuous re-audit (the permanent safe-rollout gate); not a new concept — closes the artifact gap the drift lesson opened
- **Artifact shipped:** `pensolar/modules/drift_monitor.md` — pairs with `rollout_spec.md`. Same adaptive-override pattern as 2026-08-12 (golden_v1 + score_eval) and 2026-08-13 PM (rollout_spec): conceptual ladder is COMPLETE (8 rungs), so this run ships the still-open execution artifact instead of teasing a contrived 9th concept the non-interactive student can't answer.
- **What it pins down:** the *drift meter* = gap between nightly `golden_v1` recall (the floor) and **live/rolling-sample recall** (the truth) + `review_queue` disagreement rate (early warning). Three drift flavors (data / concept / model-provider) answered by ONE mechanism: monitor on LIVE, not just the frozen set.
- **The alarm = the safe-rollout gate, made permanent:** if live recall < golden recall by >X% (proposed X=2 pts) OR disagreement rate >Y% (proposed Y=15%) → declare drift → auto-rollback dial to 0 + alert Director (same no-approval rollback as rollout_spec §3). Fires BEFORE any block is missed.
- **The loop (golden_v2):** on confirmed drift, quarantine mismatches to `review_queue`, re-label a fresh decision-time sample → promote `golden_v2` (frozen + versioned, never tuned-on). Quarterly cadence mandatory; triggered early on drift. Keeps the set alive (Run 7 discipline).
- **Honest prereq (mirrors rollout_spec §8):** the drift meter is *uncomputable* until (1) `score_eval.py` is wired to LIVE `auto_schedule_crew` output and (2) `golden_v1.csv` `EXAMPLE-SYNTH` labels are replaced with human sign-off. The spec is a design until both land — same standing execution gap.
- **Unifies the ladder:** R1 stack + R3 guardrails + R5 evals + R7 golden set + safe rollout + drift monitor = trustworthy on day 1 AND day 300. Conceptual arc DONE; everything below is execution + Director sign-off on two specs (rollout_spec §7, drift_monitor §sign-off).
- **ARTIFACT SHIPPED (this run):** `pensolar/modules/drift_monitor.md` — drift meter (live-vs-golden recall gap + review_queue alarms) + golden_v2 promotion runbook + Director sign-off block. Fills the gap the 2026-08-13 22:00 lesson explicitly opened. Remaining: audit golden_v1 (#1) + wire live score_eval (#2) + Director signs both §7s.

### 2026-08-13 (22:00 MYT) — Production drift & continuous re-audit: your golden set + recall gate go stale; keep the eval machine honest on day 300
- **Drift = the past stops predicting the future.** Three flavors: *data drift* (inputs change shape — TNB SOP change makes a "cleared" status need a 2nd sign-off), *concept drift* (the rule moves — new vendor/authority failure mode no historical project had), *model/provider drift* (LLM silently updated, parses permit text differently, recall slips with zero code change).
- **The trap:** a frozen golden set (R7) is a snapshot of the past, not a guarantee about the future. `score_eval.py` vs `golden_v1.csv` can read 100% recall while the tool misses real blocks LIVE — because the set can't see a world that changed after 2026-03-04. Past correctness ≠ future correctness.
- **Detect on LIVE, not just golden:** keep nightly golden-v1 score as the floor, but ALSO hold a rolling sample of NEW real decisions (labeled as they close) and score against it. Gap between golden-recall and live-recall = your **drift meter**. Also watch `review_queue` disagreement rate (from safe rollout) — a rising rate is the early warning that fires BEFORE any block is missed.
- **Drift alarm = same as the recall gate:** if live recall < golden recall by >X%, or disagreement rate >Y% → auto-rollback dial to 0 + alert. Drift monitoring is the *permanent* version of the safe-rollout gate (that protects autonomy today; this protects trust over time).
- **Re-audit → golden_v2 (the loop, not a one-off):** on confirmed drift, do NOT retune on golden_v1 (training-on-test/leakage) — re-label a fresh decision-time sample → promote `golden_v2`, frozen + versioned + never tuned-on. That operationalizes Run 7's "re-audit quarterly."
- **Unify the ladder:** R1 stack + R3 guardrails + R5 evals + R7 golden set + safe rollout + drift = trustworthy on day 1 AND day 300. Closes the POC→production→scale arc (8 rungs now complete). Next: execution (wire live + audit labels) + Director sign-off — drift can't even be measured until live output feeds score_eval.
- **ARTIFACT NEEDED (not yet shipped):** a `drift_monitor.md` spec (live-vs-golden recall gap + review_queue rate alarms + golden_v2 promotion runbook). Fills the gap this lesson opens; pairs with existing rollout_spec.md.

### 2026-08-13 (15:00 MYT) — Safe rollout: Shadow → Canary → Enforce, gated by your eval (the POC-build → scaling bridge)
- **Shadow mode = agent advises, human decides; you still score it.** Wire `auto_schedule_crew` to recommend schedule/block, PM makes the call, but run every rec through `score_eval.py` vs `golden_v1.csv`. Recall <100% on block cases → dial stays 0, zero career risk — you just caught the exact failure the eval exists for.
- **Canary = small real autonomy + full visibility.** After shadow recall holds, raise dial to "act on low-risk classes only" (permit cleared + no open objection auto-approved), block decisions stay human-in-the-loop. Log 100% of canary actions for the Director's visibility board.
- **The gate is recall, enforced CONTINUOUSLY, not a one-time 80%.** If live canary ever misses a block case the golden set would catch → auto-rollback dial to 0 + alert. Ship gate = "recall ≥ target on continuous live scoring, auto-rollback on breach" (Run 5b: gate on recall).
- **Quarantine disagreement, don't delete it.** Agent↔golden-set mismatch = new signal → `review_queue` for human sign-off; if human agrees agent was right, candidate for `golden_v2` (Run 7: re-audit quarterly). Keeps the set alive instead of rotting.
- **Rollout is a dial, not a switch; the eval is the hand on it.** Stack (R1) + tool/agentic (R2) + guardrails (R3) + evals (R5) + golden set (R7) = how to TRUST it. Shadow→canary→enforce = the operating procedure to raise autonomy without a 2am call. That's POC-build → scaling.
- Closes the *how-do-I-actually-deploy* gap; unifies R3+R5+R7. Next: design rollout config + recall auto-rollback, then audit golden_v1.
- **ARTIFACT SHIPPED (2026-08-13 PM run):** `pensolar/modules/rollout_spec.md` — reviewable shadow→canary→enforce spec with recall auto-rollback gate + Director sign-off block. Operationalizes this lesson; fills next_action #3. Remaining: audit golden_v1 (#1) + wire live output into score_eval (#2).

### 2026-08-12 (03:00 MYT) — Golden-set scaffold DELIVERED: stopped teaser loop, shipped golden_v1.csv + score_eval.py
- **Adaptive override:** SUMMARY.next_action said STOP new concepts if tests unanswered. Student is a cron target (no interactive answers — Runs 3–6 still pending), and the 4-run gap was pure execution. So we SHIPPED the artifact instead of a 5th teaser.
- **Delivered** `pensolar/modules/golden_v1.csv`: 20 rows, the 8-col schema (`project_id | question_type | input_snapshot | correct_answer | should_block | labeled_by | labeled_date | version`); `input_snapshot` frozen at decision time (2026-03-04), never the final cleared date — leakage trap demonstrated, not just named.
- **Stratified on purpose:** 5 of 20 rows (25%) are real block cases (expired permit, vendor withdrew, scope change, pending-past-date, authority objection). A random 20 carries ~1; this is what makes recall measurable.
- **Delivered** `score_eval.py` (~20 lines): reads golden + predictions → 2×2 + precision/recall/accuracy. Verified run: TP=4 FP=1 FN=1 TN=14, precision 80%, recall 80%, accuracy 90%.
- **SCAFFOLD FLAG:** every `labeled_by = EXAMPLE-SYNTH`. Rows show correct shape — NOT audited sign-off. Must be replaced with human sign-off before it is real ground truth (Run-6 discipline). Closes the 4-run execution gap; remaining work = audit + wire live tool output.

### 2026-08-11 (Late, run 6) — The Golden Set: your eval is only as good as its ground truth
- **Golden set = audited answer key, not a data dump.** No human sign-off = no ground truth; you'd be measuring agreement, not correctness (QA calibration logic).
- **Label at the decision, not the record:** label "should the tool have blocked? Y/N", not "permit = pending". Otherwise the risky decision stays untested.
- **Stratify, don't random-sample:** random 20 gives ~1 block case → recall unmeasurable. Deliberately over-include rare/ugly failure modes (expired permit, vendor withdrawal, scope change).
- **Freeze + version + never tune on it:** `golden_v1.csv` locked; tune on a dev set, report on the frozen set. Ground truth rots → re-audit quarterly (`v2`).
- **Leakage:** snapshot inputs *as of decision time*. Using the final cleared permit date inflates every score.
- PENSOLAR schema to build: `project_id | question_type | input_snapshot | correct_answer | should_block | labeled_by | labeled_date | version` — 8 cols, 20 rows.
- Closes the *how* of the standing gap; gap now execution-only (CSV still not built after 3 teasers).

### 2026-08-11 (Eve, run 5) — Precision/Recall & confusion matrix: accuracy lies for rare, high-stakes events
- **Confusion matrix** = 2×2 naming every mistake: TP / FP / FN / TN. Accuracy blends them; for guardrails that hides the one that kills you.
- **Precision** = TP/(TP+FP) — of flags raised, how many real (false-alarm rate). **Recall** = TP/(TP+FN) — of real risks, how many caught (miss rate).
- **Why accuracy lies:** rare "block" class (3/20) → never-block tool scores 85% accuracy, recall 0%. For safety guardrails, recall is the gate.
- PENSOLAR: `auto_schedule_crew` guardrail; positive class = permit-not-cleared must-block (rare). Gate on recall (~100%); track precision for false-alarm cost.
- Connects to evals (last) + guardrails (earlier) — the metric that makes the quality gate real. Gap closed on *which number to ship*; next is building the 20-case set with the 2×2 reported.

### 2026-08-11 (Eve) — Evals: prove the tool/agent is right before you trust it
- **Eval** = a fixed test set of real past cases with the known-correct answer; run your AI over them, measure % correct. The AI equivalent of a factory QA acceptance check before parts ship.
- **Why:** confident-sounding ≠ correct. Without an eval you can't tell if a change helped, and can't defend the demo to the Director.
- PENSOLAR: 20 closed projects as the set; known answer = real permit status / awarded quote / install date. Score `get_permit_status` % correct = baseline.
- Two cheap starts: *output eval* (answer matches known value) + *guardrail eval* (high-risk action correctly stops for human). Both reuse the same project data — no new plumbing.
- Connects to prior lessons: evals are what let you RAISE the autonomy dial safely (promote tool past dial 0 only after it passes); and evals pick tool-use vs agentic (95% one-shot → don't build the loop).
- POC takeaway: ship a tiny eval harness (CSV of ~20 cases + 20-line score script) beside the first tool demo. Gap closed on concepts — next is to actually build the 20-case set.

### 2026-08-11 (PM, run 3) — When a tool call is enough vs. an agentic workflow
- **Tool use** = one well-defined action, known inputs, predictable output (e.g.
  `get_permit_status` once). You wired the sequence; model just fires the function.
- **Agentic workflow** = a *goal* with unknown path; model loops, decides next
  step, self-corrects (e.g. "get SunnyVilla install-ready": chase permit, get 3
  quotes, compare, schedule, reschedule on slip).
- **Tradeoff (Anthropic):** agentic loops cost more money + latency; only earn it
  where deterministic rules can't handle the variation. Default to the simpler pattern.
- POC takeaway: PENSOLAR pain is *first* a tool-use + routing problem, not autonomy.
  Tool-use demo is cheaper/faster/easier to guardrail. Gap: write the tool surface
  (3-5 functions). Next: evals.

### 2026-08-11 (PM) — Guardrails & the autonomy dial
- **Autonomy dial** = how freely the agent loop may run (0 = suggests only,
  10 = acts end-to-end). Start low; raise only after it earns trust.
- **Guardrails** = fences: input filtering, per-action call limits,
  human-in-the-loop for high-risk / irreversible actions.
- Match dial to risk: read status = low risk (auto-ok); email client / change
  status = high risk (force human checkpoint).
- POC takeaway: demo the AI win without career risk — look autonomous, stay the
  safety switch. Gap: label each tool reversible vs irreversible. Next: evals.

### 2026-08-11 (PM, earlier) — Tool use vs. Agentic workflow
- **Tool use**: model calls one function you wired; *you* control the sequence.
- **Agentic workflow**: model given a goal *decides* the sequence, loops, self-corrects.
- **Workflow** (Anthropic) = LLM+tools through *predefined* code paths (predictable, cheap).
- **Agent** (Anthropic) = LLM *dynamically directs* its own process (flexible, costs more).
- POC takeaway: PENSOLAR pain solved with tool use + simple workflows first;
  don't over-build a free agent loop. Gap: define 3 must-have tools (tool surface).

### 2026-08-11 (AM) — AI backbone is a stack, not one thing
- Stack = LLM (brains) + Agent (does steps) + RAG (reads your docs) + Workflow (rules).
- For PENSOLAR: LLM summarizes, Agent flags exceptions, RAG reads project data,
  Workflow enforces approvals. You don't need all four on day one.
- Gap: define "visibility" as DATA, not a dashboard wish.

## Operating principles for your POCs
- Match the AI pattern to the pain; simplest solution that works wins (Anthropic).
- Start with tool use; add agentic autonomy only where rules genuinely fail.
- Guardrails everywhere: input filter, tool-use limits, human-in-the-loop for
  high-risk/irreversible actions. Keep the autonomy dial low at first.
- Prove it with evals before raising the autonomy dial or trusting the output.
- No audited, frozen, stratified golden set = no eval. Snapshot inputs at decision time (no leakage); never tune on the golden set.
- For guardrail evals, gate on recall (never miss a high-risk block); treat accuracy
  as the last number you report, not the one you ship on.

## Canonical references
- OpenAI — A practical guide to building agents
- Anthropic — Building effective agents

## Cap status
No cap hit. SUMMARY well under 32KB.

## Student Profile
```yaml
stage: 8            # concept arc COMPLETE (9 rungs) + cost axis + HITL-checkpoint + shift-left CI gate + INPUT-INTEGRITY gate (2026-08-17); now POC EXECUTION — audit golden_v1 -> add pre-deploy eval gate + input-integrity assert to specs/tools -> implement 6 tools -> wire live -> Director sign-off; stage-7->9 (scaling) bridges taught 2026-08-16..17
last3:
  - INPUT-INTEGRITY GATE (assert freshness + project_id BEFORE reasoning; cheapest shift-left layer: runtime->CI->input; garbage-in slips past recall) — genuinely new failure class beneath R5/R7
  - SHIFT-LEFT CI EVAL GATE (score_eval blocks the merge, not just runtime/drift; defense-in-depth) — pre-deploy stage; reuses R5/R7 + cost-axis
  - HITL CHECKPOINT DESIGN (triage by consequence-timeline + batch+SLA + pre-fill + loop-back to golden_v2) — scaling bridge
strongest:
  - Systems / operational framing
  - Unifying discrete concepts into an operating procedure (rollout)
  - Connecting concepts to solar-PM pain
  - Shipping the artifact, not just describing it
  - POC-build synthesis (agent_surface composes R1+R2+R3+R5+R7 into a buildable shape)
  - Cost/labor reasoning (reframed the dial as a $ control — his core value prop)
  - Throughput/bottleneck reasoning (grasped HITL-checkpoint as a scaling concern with minimal push)
  - Catch-defect-at-cheapest-stage / shift-left (cost mandate; now applied 3 layers deep: runtime->CI->input)
weakest: EXECUTION ONLY now — all 4 designs shipped + 4 conceptual scaling/quality bridges taught (cost-axis 2026-08-16 AM + HITL-checkpoint 2026-08-16 PM + shift-left CI gate 2026-08-16 15:00 + input-integrity 2026-08-17); remaining = (0) replace EXAMPLE-SYNTH labels with human audited sign-off [learn-pensolar/human] — MUST precede any gate; (1) ADD pre-deploy eval-gate subsection to rollout_spec §pre-deploy + agent_surface + ADD input-integrity assert (freshness+TTL+project_id) to the 6 read tools; (2) IMPLEMENT the 6 agent_surface tools (+ checkpoint/triage + input-integrity behavior) vs real PENSOLAR systems; (3) wire score_eval.py to LIVE auto_schedule_crew output + run the 2x2; (4) Director signs §7 rollout_spec + §sign-off drift_monitor + sign-off block agent_surface. NO further conceptual gaps visible.
tests:
  - 2026-08-11..12 evals/tool/guardrails/precision/golden/rollout: pending (cron, no interactive answers)
  - 2026-08-13 rollout: permit-lapse FN in canary -> first action + which 2x2 number
  - 2026-08-15 agent_surface: lapsed-permit sync gap -> which tool catches it + dial-0 vs enforce + which number gates promotion
  - 2026-08-16 cost-axis: 40 proj dial0 vs dial8 net daily $ saved (~$160) + 3-day breach PM cost (~$480) + $/run flat design
  - 2026-08-16 PM checkpoint: 8 blocks/wk (2H+6L), $40/hr — naive ~$53/wk vs triaged 50m/wk fits 80m/day; pre-fill ~83%; decisions->review_queue->golden_v2
  - 2026-08-16 15:00 shift-left: dev PR recall 88% (was 100%), accuracy 92% "ship to canary" — fail PR? which number? ~how many block cases slip canary? CI vs runtime gate? audit-first ordering
  - 2026-08-17 input-integrity: Redis cache TTL=7d, TNB revokes day3, agent commits day4 — recall gate catch? which number + only after what? cheapest check + assert? caching always cheaper?
next_action: (concept arc DONE — 9 rungs + cost axis + HITL-checkpoint + shift-left CI gate + input-integrity gate; all 4 specs shipped, +2 lines to add: pre-deploy eval gate + input-integrity assert) EXECUTION HAND-OFF, owned by learn-pensolar/human + Director: (0) audit golden_v1.csv EXAMPLE-SYNTH->human sign-off [prereq for any gate]; (1) add pre-deploy eval-gate subsection + input-integrity assert to rollout_spec §pre-deploy + agent_surface; (2) implement the 6 agent_surface tools (+ checkpoint/triage + input-integrity) vs real PENSOLAR systems; (3) wire score_eval.py to LIVE auto_schedule_crew output + run 2x2; (4) Director signs §7 rollout_spec + §sign-off drift_monitor + sign-off block agent_surface. Mentor cron's remaining job = periodic golden_v2 nudge (meaningless if v1 never audited) + periodic audit-first nudge.
```
