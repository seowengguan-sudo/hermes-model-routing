# Mentor Summary — AI education in business language

Living, compressed log of what we've covered. Newest concept on top.
Daily detail lives in `mentor/daily_notes/YYYY-MM-DD.md`.

## Concept log (newest → oldest)

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
stage: 5            # POC-build: conceptual ladder COMPLETE; execution now scaffolded
last3:
  - Golden-set scaffold DELIVERED (golden_v1.csv + score_eval.py)
  - Golden set / ground-truth curation (leakage, stratify, freeze+version)
  - Precision/Recall & confusion matrix (accuracy lies for rare events)
strongest:
  - Systems / operational framing
  - Tool-use vs agentic distinction
  - Connecting concepts to solar-PM pain
  - Now: shipping the artifact, not just describing it
weakest: EXECUTION — was "csv never built"; scaffold now exists; remaining = replace EXAMPLE-SYNTH labels with human audited sign-off + wire live tool output into score_eval
tests:
  - 2026-08-11 evals/tool/guardrails/precision/golden: pending (cron, no interactive answers)
  - 2026-08-12 operational: run score_eval.py on real tool predictions -> report 2x2 + ship-gate number + missed block case
next_action: replace EXAMPLE-SYNTH labels with audited sign-off; run score_eval.py on live auto_schedule_crew output; bump golden_v2 quarterly
```
