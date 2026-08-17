# KB-Cron Formats & Schedule (discovered 2026-08-13)

Concrete specs for the user's knowledge crons. Keep this as a quick-lookup; the
SKILL.md body holds the procedure.

## Cron schedule (MYT)
- `mentor-ai-daily` — 3x/day: 07:00, 15:00, 22:00 MYT. deliver=local. Teaches ONE
  AI concept + tests the student; writes mentor/SUMMARY + RUN_LOG (no dup).
- `learn-pensolar` — daily 15:00 MYT. Reads SUMMARY → finds gaps → searches only
  gaps → rewrites SUMMARY (no dup).
- `marketing-advisor-daily` — Mon–Sat 06:00 MYT.
- `strategic-coo-guidance` — Sundays 08:00 MYT.
- `workspace-cleanup-daily` — nightly 10:00 MYT; prunes files >14 days.

All: SUMMARY ≤32KB hard cap (halt on breach). deliver=local.

## KB layout
- `/opt/data/knowledge/INDEX.md` — compact map; agent reads full files on demand.
- `mentor/SUMMARY.md` — living concept log + student profile YAML (≤32KB, read-first).
- `mentor/daily_notes/YYYY-MM-DD[-HHMM].md` — per-run lesson + test + readiness.
- `mentor/RUN_LOG.md` — audit trail.
- `raw/` — full fetched articles, dated, NOT auto-loaded (traceability only).
- `by_industry/<vertical>/<client>/` — POC KBs (e.g. solar_energy/pensolar).

## workspace INDEX.md (ABSOLUTE: /opt/data/workspace/INDEX.md)
Markdown table. Header + columns:
```
| Date | Stream | Entry | Output |
|------|--------|-------|--------|
| 2026-08-13 | Mentor | Drift & continuous re-audit: ... | mentor/daily_notes/2026-08-13-2200.md |
```
Stream values seen: Mentor, COO, Marketing, Pensolar, solar ops.

## SUMMARY.md student-profile YAML block (embed at end, ≤1KB)
```yaml
stage: 6            # 1=fundamentals ... 5=POC-build ... 9=scaling
last3:
  - <most recent concept>
  - <prev>
  - <prev>
strongest:
  - ...
weakest: <area>
tests:
  - <date> <topic>: <status>
next_action: <concrete next step>
```

## RUN_LOG.md
Header: `YYYY-MM-DD | concept | test-posed | mastery-prediction`
One line per run; do not duplicate an existing line.

## Worked example (this session)
2026-08-13 22:00 MYT mentor run taught "Production drift & continuous re-audit"
(8th/final scaling rung). Resolved clobber by writing `2026-08-13-2200.md` (a
15:00 note already existed). SUMMARY grew 11361→13907 bytes (cap safe). Appended
one RUN_LOG line + one workspace INDEX row. No artifact shipped (drift_monitor.md
left as next_action) — correct because cron target can't answer tests, so advance
ladder operationally rather than tease.
