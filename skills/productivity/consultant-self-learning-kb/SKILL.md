---
name: consultant-self-learning-kb
description: Compressed, cron-fed learning KB for consulting POCs.
triggers:
  - User is a consultant building POCs and wants the agent to accumulate domain/skill knowledge over time without swelling memory.
  - User wants daily mentoring on a topic (e.g. AI) matched to their level, plus parallel research per active project/vertical.
  - User asks to structure knowledge by industry / work scope / solution area for easy retrieval.
---

# Consultant Self-Learning Knowledge Base

## User context this skill encodes
AI Consultant: quality/efficiency/cost across overlapping industries (mfg,
integration, admin). Mission = build POCs first, then impress clients. Wants the
agent to self-learn continuously and mentor him step-by-step (operationally
strong, AI-architecturally early-stage).

## Core architecture (proven this session)
```
knowledge/
  INDEX.md              <- ONLY thing in active memory (a map, ~compact)
  mentor/daily_notes/   <- AI education, dated, gap + next-step per note
  projects/<client>/    <- brief.md, solution_framework.md, modules/
  by_industry/          <- auto-created per real client (not pre-built)
  raw/                  <- full fetched articles, dated, NEVER auto-loaded
```

## Compression rule (anti-swell — the user's #1 concern)
Every cron pull → extract (pain / solution / benchmark / source / date) →
≤5 bullets into the RIGHT file → `INDEX.md` gets only path + 1-line scope.
Full text → `raw/` only. Never load `raw/` unless asked.

## Cron jobs pattern (create only with approval)
- `mentor-ai-daily` (2×/day): reads last note, detects misunderstanding, teaches
  ONE concept at user's level with a business example; Claude/GPT-style depth,
  ≤400 words; FREE web_search only.
- `learn-<project>` (daily): reads the project brief/framework, finds GAPS,
  pulls intelligence that FILLS those gaps (not generic); ≤500 words; free search.
Key: crons learn what's NEEDED (gap-driven), not wide empty shells.

## Schedule convention (verified this session)
- Cron expressions are entered in **UTC**; user works in **MYT (UTC+8)**.
  Always convert: 15:00 MYT → `0 7 * * *`; 03:00 MYT → `0 19 * * *`.
- Create with `cronjob action=create name=... schedule="<UTC expr> deliver="local"`.
  Schedules are **immutable** after creation — to reschedule, you must DELETE +
  RECREATE the job (updating `schedule` via `cronjob update` does NOT change the
  trigger — confirmed). Capture the job_id from `cronjob list` for deletes.
- `deliver="local"`: output is saved and viewable via `cronjob list`, **NOT**
  delivered to chat. Never promise the user live chat results from a local-deliver cron.

## Self-categorization rule (user Q4)
Do NOT pre-build industry shells. When a real client appears, create
`by_industry/<vertical>/` and segment by sub-function (accounting, purchasing,
ERP...) as the work demands. Let the conversation drive structure.

## Working-style protocol (EMBED in every build for this user)
- DESIGN DIGEST + open questions FIRST; wait for explicit 'go' before coding.
- Close with HONEST RESIDUAL (design ≠ running system unless built + tested).
- Acknowledge validity of his thinking before counterpoints.
- MATCH SCOPE TO PROBLEM: a one-line config fix does not warrant a library.
- Mentor aggressively but patiently; tell him WHY in business terms.

## Retrieval
On a project/vertical/mentor task, read `INDEX.md` first, then the specific file.
Never load `raw/` unless explicitly asked.

## Schedule immutability (verified this session)
Cron schedules are **immutable** after creation — updating `schedule` via
`cronjob action=update` does NOT change the trigger. To reschedule: DELETE the
job (`cronjob action=remove job_id=<id>`) and RECREATE it. Capture job_id from
`cronjob list`. (This tripped me: I tried to edit a schedule and it silently kept
the old one.)

## Sibling-agent + scheduler-lock behavior (verified 2026-08-11)
Two distinct behaviors to recognize:
- **Same-session sibling write**: `write_file` warns "modified by sibling subagent" —
  your write still lands; verify the final bytes are yours.
- **Scheduler lock rejection**: `cronjob action=run` returns
  `"execution_skipped": "Job is already being fired by the scheduler; not run again."`
  This is NOT an error. Do NOT retry immediately — it stacks. Wait for the in-flight
  run; if stuck, toggle the job off/on to clear the lock.

## Mentor-cron adaptive override — ship the artifact, don't loop (verified 2026-08-12)
`mentor-ai-daily` (and any mentor-type cron) teaches ONE concept + poses a test each run.
But a cron has NO interactive student — the "test" never comes back. If the SUMMARY's
`next_action` says "stop new concepts if tests unanswered" and the SAME execution gap has
recurred across runs, DO NOT teach a 5th teaser. Instead DELIVER the artifact:
- Build the concrete scaffold the student kept failing to produce (correct schema, worked
  example rows), plus a runnable script that exercises it.
- Mark synthetic/placeholder rows clearly (e.g. `labeled_by=EXAMPLE-SYNTH`) so they are
  NOT mistaken for audited ground truth — the lesson is "no sign-off = no ground truth."
- Verify the script actually runs (see next section) BEFORE reporting the artifact done.
This converted a 4-run teaser loop into a delivered, validated `golden_v1.csv` + `score_eval.py`.
Reusable golden-set eval scaffold (schema + known-good scorer) → `references/golden-set-eval-scaffold.md`.

## Verify delivered code by running it (2026-08-12 revision)

Any cron that writes a script/CSV must EXECUTE it and show real output before declaring success —
("Finishing the job" = verified artifact, not description).

**Approval-gated file creation rule (new):**
- Pre-approved write zones ONLY: `mentor/daily_notes/`, `pensolar/logs/`, `marketing/daily-brief-*`, `workspace/INDEX.md`
- Any NEW file outside these zones (e.g. `golden_v1.csv`, `score_eval.py`) → cron writes proposal into its own daily note under `<pending>/<filename>` and prompts `/approve` in chat before writing.
- This prevents unrequested file sprawl across the user's system.

**Execution requirement:**
The safe-root enforcement (`HERMES_WRITE_SAFE_ROOT=/opt/data`) blocks writes outside `/opt/data`. Within that boundary, a cron must still prove its artifact works:
- Scripts: run them inline (e.g. `python3 script.py input.csv predictions.csv`) and assert expected output (TP=4, Recall=80%, etc.).
- CSVs: validate schema + example rows load + parse.
- Never claim "verified" until both compile + runtime-output checks pass.

## Model choice affects cron OUTPUT QUALITY (verified 2026-08-11)
For a research-compression cron, **hy3 (`tencent/hy3:free`) > laguna-s** for synthesis:
- **hy3**: compresses 5 extract pages into a director-ready structured brief
  (workflow phases + admin/acctg + pinch per phase), 8 well-chosen sources.
- **laguna-s**: dumped raw FAQ pages verbatim, no synthesis; also hung >180s.
For KNOWLEDGE-ACCUMULATING crons, **pin hy3**. Laguna-s is fine for raw passthrough only.

## Evolving to enterprise AI solution provider (verified 2026-08-12)

The core pattern now drives an AI consultancy → enterprise solution provider via
**four** parallel autonomous streams, all feeding a master INDEX.md:

1. **`mentor-ai-daily`** (4x/day) — 07:00 / 11:00 / 15:00 / 19:00 MYT
   Keeps the founder technically sharp. Adaptive: if tests unanswered, ships artifacts + test harness instead of looping teasers (golden-set example).
   Schedule: `0 7,11,15,19 * * *` (UTC+8 → `0 23,3,7,11 * * *` UTC).

2. **`learn-pensolar`** (daily) — 15:00 MYT
   Compresses solar-energy domain intel into structured summaries.
   Schedule: `0 7 * * *` (UTC+8).

3. **`strategic-coo-guidance`** (weekly) — Sundays 08:00 MYT
   Directs company-building: budget allocation, risk register, go-to-market priorities.
   Output: `strategy/coo-brief-WWYY.md` with Gantt + success metrics table.
   Schedule: `0 0 * * 0` (UTC+8).

4. **`marketing-advisor-daily`** (Mon-Sat) — 06:00 MYT
   Drives visibility: 1 LinkedIn post/day + group engagement + lead-magnet ideation.
   Output: `marketing/daily-brief-YYYY-MM-DD.md` with copy-and-paste caption.
   Schedule: `0 22 * * 1-6` (UTC+8).

All streams write to a master INDEX.md. SUMMARY.md ≤32KB cap (hard halt if exceeded). Each cron pulls only GAPS (not generic content) — hy3 for synthesis, laguna-s only for raw passthrough.

Key lesson: crons can be the founder's "COO + CTO + CMO" stack — but each must have a DISTINCT model and purpose. Today's verified setup:
- mentor-ai-daily → hy3 (synthesis + teaching)
- learn-pensolar → hy3 (domain intel compression)
- strategic-coo-guidance → hy3 (strategic reasoning)
- marketing-advisor-daily → hy3 (tactical marketing)
Do NOT let them blur into generic content farms — pin per-stream purpose.

