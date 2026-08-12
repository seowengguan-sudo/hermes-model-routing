# Startup Enforcement Scripts — Internals Reference

## Overview

Two scripts run on every Hermes restart (invoked by the sentinel `startup-catchup-enforcement` job `0ee860f4fb74` or via direct terminal invocation):

### 1. enforce_pins.py

**Location:** `/opt/data/knowledge/enforce_pins.py`

**Purpose:** Ensure every cron job is pinned to `tencent/hy3:free` (Nous provider).

**Logic:**
1. Backups `jobs.json` → `jobs.json.bak` (only if backup doesn't already exist).
2. Loads `/opt/data/cron/jobs.json`.
3. For each job: if `model != "tencent/hy3:free"` or `provider != "nous"`, calls `hermes cron edit <id> --model tencent/hy3:free --provider nous` via subprocess.
4. Updates the in-memory data structure.
5. Writes back to `jobs.json` if any changes were made.

**Key implementation notes:**
- Uses `/opt/hermes/bin/hermes` directly (absolute path, works in WSL cron context).
- The Hermes CLI call output is captured (`capture_output=True`) but not inspected — the script trusts the CLI succeeds.
- Jobs with `model: null` / `provider: null` ARE re-pinned (e.g. `workspace-cleanup-daily`, `startup-catchup-enforcement`).
- Jobs with `provider_snapshot` / `model_snapshot` but null `model`/`provider` are still treated as unpinned — the CLI call updates the active fields.
- **Backup guard:** Only creates `.bak` if it doesn't already exist. On repeated runs, the original backup is preserved (not overwritten). This means the backup reflects the state at first run, not the latest state before the current run.

**What it doesn't do:**
- Does not touch the `script` field (that's a separate concern).
- Does not re-pin jobs that are already correct (no-op).
- Does not verify the CLI succeeded — if `hermes cron edit` fails, the in-memory JSON is still updated to the target values.

### 2. catchup.py

**Location:** `/opt/data/knowledge/catchup.py`

**Purpose:** Detect Hermes restart and backfill any missed cron executions.

**Logic:**
1. Reads boot time from `/proc/stat` (`btime` line). Falls back to "now - 86400s" if unavailable.
2. Reads last recorded boot time from `/opt/data/.boot_time` (mtime of the file, not its content).
3. **Restart detection:** If `last_boot_recorded (mtime) < boot_time (kernel)`, a restart is detected.
4. If restart detected:
   a. Loads all jobs from `jobs.json`.
   b. For each job, calls `calculate_missed(schedule_expr)`.
   c. Queues all missed (job_id, name, missed_at) entries.
   d. Writes queue to `/opt/data/cron/missed_runs.json`.
   e. Fires each missed job via `hermes cron run <job_id>` (subprocess, 120s timeout).
   f. `fire_job()` writes a log entry to `/opt/data/knowledge/cron_runlog.md` for each fired job.
   g. Removes the queue file.
   h. Prints summary to stdout.
5. Records current boot time: writes `str(boot_time)` to `/opt/data/.boot_time`.

**calculate_missed() — supported cron expressions:**
| Pattern | Meaning |
|---------|---------|
| `0 7 * * *` | Daily at 07:00 UTC (15:00 MYT) |
| `0 7,11,15,19 * * *` | 4x daily at 07:00, 11:00, 15:00, 19:00 UTC |
| `0 7,15,22 * * *` | 3x daily at 07:00, 15:00, 22:00 UTC |
| `0 6 * * 1-6` | Daily Mon-Sat at 06:00 UTC |
| `0 0 * * 0` | Sunday only at 00:00 UTC |
| `1 1 1 1 1` | Sentinel job — intentionally **skipped** by catchup (non-standard pattern). Handle via `cronjob action=run job_id=0ee860f4fb74` if needed. |

**Key implementation notes:**
- The `calculate_missed` function does NOT use a full cron library — it uses string matching. Non-matching patterns silently get no missed times.
- `fire_job()` timeout is 120 seconds — long-running jobs may be killed.
- `fire_job()` considers success if `execution_success` is in stdout OR returncode == 0.
- The `.boot_time` file stores the boot timestamp integer as content, but catchup uses **file mtime** for comparison.
- **Bug-ish:** The mtime comparison means if the filesystem mtime is preserved across reboots (unlikely in WSL/Docker), restart detection could fail.

## Verification checklist

After running both scripts:
1. `python3 -c "import json;d=json.load(open('/opt/data/cron/jobs.json'));print([(j['name'],j.get('model'),j.get('provider')) for j in d['jobs']])"` — all jobs should show `tencent/hy3:free` / `nous`.
2. `ls -la /opt/data/.boot_time` — file should exist with boot timestamp content.
3. `ls /opt/data/cron/missed_runs.json` — should NOT exist (removed after processing).
4. `ls /opt/data/cron/jobs.json.bak` — should exist (backup from enforce_pins).
5. `cat /opt/data/knowledge/cron_runlog.md` — should contain entries from this startup cycle.
