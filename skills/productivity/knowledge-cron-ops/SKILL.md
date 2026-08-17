---
name: knowledge-cron-ops
description: Operate self-updating knowledge-base cron jobs.
---

# Knowledge-Base Cron Ops

Use when running or authoring an autonomous cron that maintains a compressed, self-improving knowledge base under `/opt/data/knowledge/`. This user runs several of these; they share one operating procedure.

## The operating loop (do in this order)
1. **Read first:** `knowledge/<stream>/SUMMARY.md` — the living compressed log. Produce nothing before reading it.
2. **Read the last 3 notes** in `daily_notes/` (or `logs/`) to see prior tests/gaps.
3. **Find the gap:** current stage, unanswered tests, the missing rung.
4. **Pick ONE unit** that fills a gap, connects to what exists, and has a concrete example.
5. **Teach** in 4–6 operational (not textbook) bullets; **test** with one scenario question.
6. **Write the dated note** (naming rule below).
7. **Update SUMMARY.md:** newest concept on top; refresh the student/profile YAML block; enforce the cap.
8. **Append** one line each to RUN_LOG.md and `/opt/data/workspace/INDEX.md`.
9. **One-line report.**

## Naming rule (avoids clobber — learned the hard way)
Prompt files often say "write `daily_notes/YYYY-MM-DD.md`", but the schedule is frequently **multiple runs/day**. Example: mentor-ai-daily = 07:00 / 15:00 / 22:00 MYT. **Never overwrite an existing same-day note.** Suffix by slot: `YYYY-MM-DD-HHMM.md` (HHMM in MYT). This session hit the clobber risk on 2026-08-13 (a 15:00 note already existed) and resolved it with `2026-08-13-2200.md` — prior note preserved, new lesson captured.

## Hard cap guard
SUMMARY.md must stay **≤ 32768 bytes**. Before writing, `wc -c`. If it would exceed, print `SUMMARY_CAP_HIT` and STOP — do NOT overwrite. To make room, prune oldest foundational concepts (keep newest).

## Append formats
- **RUN_LOG.md:** `YYYY-MM-DD | <concept> | <test-posed> | <predicted-mastery>` — one line, no duplicate of an existing line.
- **/opt/data/workspace/INDEX.md** (ABSOLUTE path, a different tree from `knowledge/`): append a table row `| <Date> | <Stream> | <Entry> | <note-path> |`. Columns: `Date | Stream | Entry | Output`.

## Pitfalls
- **Don't clobber** an existing daily note — suffix by slot (rule above). Cron re-runs are silent and will overwrite without warning.
- **Workspace INDEX is at `/opt/data/workspace/INDEX.md`** — literal absolute path, NOT under `knowledge/`. The prompt's "append to absolute path" wording is exact; resolve it absolutely.
- **read_file can mis-report a valid UTF-8 .md as "binary"** (seen this session on a 4KB note). Verify with `python3 -c "open(p,'rb').read().decode('utf-8','replace')"` before concluding corruption.
- **No-duplication:** check SUMMARY's concept log and RUN_LOG before appending; repeated cron invocations must not pile duplicate entries.
- **Cron target = no interactive answers.** If tests can't be answered, prefer shipping an artifact or advancing the ladder operationally over piling teasers (established adaptive override for this user's crons).

## Verification (after any run)
- `wc -c knowledge/<stream>/SUMMARY.md` < 32768.
- RUN_LOG.md and workspace INDEX.md each gained exactly one new line.
- New note file exists and prior same-day notes are intact (no overwrite).

## References
- `references/kb-cron-formats.md` — concrete format specs + the user's cron schedule discovered this session.
