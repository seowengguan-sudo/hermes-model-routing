# Adaptive gap-driven research loop (SUMMARY + _GAPS + RUN_LOG)

A research cron that re-searches the same broad topic every run produces redundant pulls and a
bloating SUMMARY. The fix is a **three-file self-steering loop** where each run consumes the
previous run's open questions and emits new ones. Verified on `learn-pensolar` (2026-08-11, run 2).

## The file triad

```
<kb>/by_industry/<vertical>/<client>/SUMMARY.md   # living distillation, byte-capped (32768)
<kb>/by_industry/<vertical>/<client>/_GAPS.md     # 3-5 prioritized open questions -> next run's search plan
<kb>/by_industry/<vertical>/<client>/RUN_LOG.md   # append-only audit: date | topics | sources | gaps added
```

Optional but useful: `.prompt-learn.txt` alongside them holding the cron's own prompt, so a run
can read the spec it is executing.

## Execution order (do not reorder)

1. READ all three. SUMMARY = what's known. `_GAPS` = the search plan. RUN_LOG = the do-not-repeat list.
2. Derive 3-5 **specific** search targets from `_GAPS`, filtered against RUN_LOG topics.
3. Search + extract ONLY those. Never re-broaden to the original topic.
4. REWRITE SUMMARY: keep valid content, append newly confirmed items, correct anything falsified.
5. REPLACE `_GAPS.md` with the NEW gaps that emerged this run (highest priority first).
6. APPEND one RUN_LOG line. Never rewrite history there.

## Technique: tie every finding to a KPI

Anchor the brief to the client's operating KPIs (e.g. timeline adherence, cost per unit, callback
rate, procurement lead time). A finding that maps to no KPI is trivia — drop it. This is what keeps
compression honest instead of arbitrary.

## Technique: CLOSE gaps as unanswerable

Some gaps have no public answer (e.g. "Malaysian PV after-sales callback-rate benchmark" — no
published data exists). If left in `_GAPS`, every future run burns queries rediscovering the void.

Mark these explicitly and move them out of the search plan:

```
- CLOSED AS UNANSWERABLE: <gap> — no public data exists.
  Converted to a build requirement (instrument in-house from ticket 1). Do not re-search.
```

Converting a dead research gap into a **build requirement** is often the more valuable outcome:
it tells the client to instrument what nobody else has measured.

## Technique: actively CORRECT prior runs

Treat inherited SUMMARY content as falsifiable, not settled. Two high-value correction classes:

- **Wrong figures.** Run 1 recorded a standby charge at "~RM12/kWp/mo above 1MWp"; sources showed
  RM14/kWp/mo above **72kWp** — a threshold ~14x lower, material to every C&I quote.
- **Conflated segments.** A single "3-5 month" timeline actually blended residential (4-8wk) with
  commercial (3-5mo). Blended KPIs hide problems in the faster segment.

Flag corrections inline (`CORRECTED:` / `(was wrongly ...)`) so the audit trail survives, and say
so plainly in the report — a silently fixed number is indistinguishable from a new error.

## Report shape for the no-user-present run

Lead with the one-line metric ("N sources; G gaps filled; N2 new gaps; SUMMARY now X KB"), then
only the findings that change a decision. Close with an honest source-quality caveat — e.g. vendor
marketing pages give best-case timelines, so label them as vendor-stated, not audited, and leave
the official regulator PDF in `_GAPS` for verification.
