# Incremental vs. Repetitive Automation (user preference)

A daily job that does the SAME search and overwrites the same SUMMARY is
not "learning" — it is busywork that repeats itself. The user spotted this
explicitly: "else what is the point running it daily — the gist is the same."

## The correction
- Each run must be **gap-aware / incremental**: read prior notes, compare,
  emit only what is genuinely NEW relative to (a) the user's known gaps and
  (b) prior learning in the knowledge index.
- If nothing new → **skip** (no-op write, log "nothing fresh").
- If fresh → **append** dated evidence, **rewrite SUMMARY** from the full set.

## How to implement (for any research cron)
1. READ `knowledge/SUMMARY.md` and `knowledge/missing/` (user's gap list) at run start.
2. Search with a "what's new since <yesterday>" framing, not a vanilla repeat.
3. Diff results against prior SUMMARY; keep only novel signal (≤5 bullets).
4. Append to dated log; rewrite SUMMARY; write missing gaps discovered.
5. Report: sources, novel-bullets, skipped-or-not.

Violating this = waste the user pays (token + time) for. Honor it in every
knowledge-pull design. See also `test-driven-development` (incremental green
beats horizontal re-run) and `plan` (tasks must be genuinely incremental).
