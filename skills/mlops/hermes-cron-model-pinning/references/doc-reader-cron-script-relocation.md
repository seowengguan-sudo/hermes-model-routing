# Relocating doc_reader cron scripts into `scripts/` (session 2026-08-16)

## Context
After the doc_reader project was restructured, three `no_agent` cron jobs whose `script`
fields referenced scripts that no longer resolve inside `$HERMES_HOME/scripts/` started
failing. This file documents the **exact** state and **verified** fix.

## Live job state (cronjob action=list, 2026-08-16T13:20Z)

| Job | id | script field | last_status | Root cause |
|-----|----|--------------|-------------|------------|
| gateway-watchdog | 46a5f1554285 | `/opt/data/projects/doc_reader/gateway_watchdog.sh` (ABSOLUTE) | **error** | Containment guard rejects absolute path outside `/opt/data/scripts/` |
| daily-git-push | d0ba3a8ed894 | `auto_git_push.sh` (relative basename) | ok (last ok) | resolves to `/opt/data/scripts/auto_git_push.sh` → **MISSING on disk** |
| monthly-cleanup | fa08a598098a | `cleanup.sh` (relative basename) | (unrun yet — scheduled 2026-09-01) | resolves to `/opt/data/scripts/cleanup.sh` → **MISSING on disk** |
| workspace-cleanup-daily | 9dda7d6f3af5 | `cleanup-policy.sh` | ok | exists: `/opt/data/scripts/cleanup-policy.sh` ✅ |

## Where the scripts actually live (not under scripts/)
- `/opt/data/projects/doc_reader/gateway_watchdog.sh`  (executable, 1466 bytes)
- `/opt/data/projects/doc_reader/auto_git_push.sh`      (executable, 1121 bytes)
- `/opt/data/projects/doc_reader/cleanup.sh`            (executable, 7245 bytes)
- `/opt/data/scripts/cleanup-policy.sh`                 (executable, 731 bytes) ← canonical home

## Containment guard — exact block message (verified from cron/output)
Runner text (scheduler.py) rejects the absolute path:
```
Blocked: script path resolves outside the scripts directory (/opt/data/scripts): '/opt/data/projects/doc_reader/gateway_watchdog.sh'
```
This is a **hard block** — the `no_agent` job produces zero output and `last_status: error`
every tick (50+ failed ticks captured in `cron/output/46a5f1554285/`).

## The fix (relocate only — do NOT delete originals)
1. Copy each script INTO `/opt/data/scripts/` keeping the basename (no subpaths).
   - `gateway_watchdog.sh` ← `/opt/data/projects/doc_reader/gateway_watchdog.sh`
   - `auto_git_push.sh`     ← `/opt/data/projects/doc_reader/auto_git_push.sh`
   - `cleanup.sh`           ← `/opt/data/projects/doc_reader/cleanup.sh`
2. Leave the originals in `projects/doc_reader/` alone — `cleanup-policy.sh` (line 14)
   calls `/opt/data/scripts/auto_git_push.sh`, so once relocated that internal ref resolves.
3. Update each cron's `script` field to the **relative basename only**:
   - `gateway-watchdog`    → `script = "gateway_watchdog.sh"`  (via `hermes cron edit`)
   - `daily-git-push`      → `script = "auto_git_push.sh"`    (already correct; just needs the file present)
   - `monthly-cleanup`     → `script = "cleanup.sh"`          (already correct; just needs the file present)
4. Re-chmod `0755` and ensure `.sh` extension (interpreter = extension, shebang ignored; see Pitfall #13).

## Verification
- `python3 skills/mlops/hermes-cron-model-pinning/scripts/verify_cron_script_field.py`
  → expect `PASS: no broken script fields`.
- `cronjob action=run job_id=46a5f1554285` → expect `last_status: ok`, output shows
  `Gateway watchdog: ...` (gatekeeper check), NOT `script failed`.
- `cronjob action=run job_id=d0ba3a8ed894` → expect git push log, no "Script not found".

## Honest residual
Re-enabling `monthly-cleanup` (cleanup.sh) is safe to pre-stage because Sept 1 is weeks out,
but the **gateway-watchdog currently re-errors every 2 minutes** — that's the priority fix.
The containment guard means symlinks won't satisfy the path check reliably (it resolves and
then does `relative_to(scripts_dir)`), so a real file COPY is required, not a symlink.
