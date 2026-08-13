# KNOWLEDGE INDEX

Compact map. Agent reads full files on demand; this stays in active memory.

## By Industry (self-categorized per engagement)
- `by_industry/solar_energy/pensolar/` — Solar PV integrator (Penang). Director wants total visibility; POC PM system.
  Files:
    - brief.md (objective+pain), solution_framework.md (6-layer AI backbone)
    - SUMMARY.md (living compressed distillation, ≤32KB — read-first), _GAPS.md (priority research gaps), RUN_LOG.md (audit trail, no dup), logs/YYYY-MM-DD.log (per-run full), modules/ (POC data model)

## Mentor (your AI education — adaptive)
- `mentor/daily_notes/YYYY-MM-DD.md` — concept + test + readiness
- `mentor/SUMMARY.md` (living concept log + student profile, ≤32KB — read-first), RUN_LOG.md (audit trail)

## Raw
- `raw/` — full fetched articles, dated, NOT auto-loaded. Traceability only.

## Cron jobs (adaptive)
- `mentor-ai-daily` — 07:00 + 19:00 UTC (15:00 + 03:00 MYT), hy3, teaches ONE concept + tests student; writes SUMMARY+RUN_LOG (no dup)
- `learn-pensolar` — 07:00 UTC (15:00 MYT), hy3, reads SUMMARY→find gaps→searches only gaps→rewrites SUMMARY (no dup)
- Both: SUMMARY ≤32KB (hard cap; halt on breach), deliver=local
