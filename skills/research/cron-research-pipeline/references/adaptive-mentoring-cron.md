# Adaptive-mentoring cron variant (`mentor-ai-daily`)

Same cron skeleton as a research pull, but the "knowledge" being grown is the **student's
capability**, not market facts. Derived from the `mentor-ai-daily` runs on
`/opt/data/knowledge/mentor/`.

## Layout
```
/opt/data/knowledge/mentor/SUMMARY.md              # concept log newest-on-top + ## Student Profile YAML, cap 32768
/opt/data/knowledge/mentor/daily_notes/YYYY-MM-DD.md   # full lesson + test question + readiness observation
/opt/data/knowledge/mentor/RUN_LOG.md              # date | concept | test-posed | mastery-prediction
/opt/data/workspace/INDEX.md                       # one line: <YY-MM-DD> | concept | project focus | gaps added/resolved
```
Read order each run: SUMMARY → last 3 daily notes → then choose the concept. Never pick a
concept already in the log unless you are deepening it with a genuinely new angle.

## Multiple runs on the SAME calendar day
The job can tick more than once per day (e.g. 15:00 + 03:00 MYT both landing on one date).
Do NOT create a second file or overwrite — **append a `## Run N (<time-of-day>) — <concept>`
section** to the existing `daily_notes/<date>.md`, and prepend the concept block to
SUMMARY's log. `date +%F` first; if a note for that date already exists, you're in run N+1.

## PITFALL: appending via patch splits sentences
Trying to insert a placeholder *before* an existing paragraph (patch on the first clause of a
sentence) leaves the remainder of that sentence orphaned after your inserted block — cost two
extra repair patches this session.

**Correct shape:** anchor `old_string` on the **final sentence of the file**, and set
`new_string` = that same sentence + `\n\n---\n\n` + the new run section. One patch, nothing
split. (Same rule for SUMMARY: anchor on the heading of the currently-newest concept block and
re-emit it after your new block to prepend.)

## Adaptive targeting rules (the part that makes it mentoring, not lecturing)
1. Pick a concept that (a) fills an identified gap, (b) connects to something already taught,
   (c) has a concrete example in the student's live POC. All three, or don't teach it.
2. Always close with ONE scenario-based test question — not "explain X" but "here's a broken
   setup, name the defect and the fix."
3. Track `tests:` in the Student Profile YAML with pending/passed/failed.
4. **ESCALATION RULE (important):** if N tests in a row come back unanswered (the student is
   consuming lessons but not producing artifacts), the diagnosis is an EXECUTION gap, not a
   comprehension gap. Stop stacking new concepts. Either (a) hand over the concrete artifact
   shape/schema outright instead of teasing it, then (b) next run, co-build the artifact with
   them. Record this as `next_action:` in the profile YAML so the following run honours it.
   Teaching a 6th concept over 5 unanswered tests is the failure mode to avoid.
5. State the unanswered-test count honestly in the delivered report. Never imply mastery that
   hasn't been demonstrated.

## Student Profile YAML block (keep ≤1KB, at end of SUMMARY.md)
```yaml
stage: 1-9          # 1=fundamentals 5=POC-build 9=scaling; add a comment on WHY
last3: [...]        # newest first
strongest: [...]
weakest: ...        # name it sharply, incl. "EXECUTION — <artifact> still unbuilt after N teasers"
tests: [...]        # date + concept + pending/passed/failed
next_action: ...    # binding instruction for the next run
```

## Report shape
User wants bottom-line first. Deliver the lesson bullets + the test question in the body, then
one final status line: `Taught: … | Test: … | Stage: … | SUMMARY now X KB`.
