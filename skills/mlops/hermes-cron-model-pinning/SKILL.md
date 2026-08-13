---
name: hermes-cron-model-pinning
description: Repair broken Hermes cron jobs — pin drifted model/provider, fix provider/model-id 404s, and clear a broken `script` field emitting a phantom 'Script Error' every tick.
trigger: Cron breaks after model.default changed ("global inference config drifted ... unpinned"), vision/VLM 404s, or a per-tick "Script not found" / "Script Error" caused by a literal-string `script` field.
behavior: Pin via `hermes cron edit` CLI; clear a bad `script` via CLI or direct edit of $HERMES_HOME/cron/jobs.json
---

# Hermes cron job model pinning and drift-guard repair

## When it fires
A cron job that worked before now errors:
"global inference config drifted since this job was created ... This job is unpinned."

Cause: `model.default` changed (e.g. hy3 → laguna-s). Hermes blocks unpinned jobs
to prevent unintended token spend on the new default.

## Fast path
1. Pin via the hermes CLI (NOT the cronjob tool — see Pitfall #1):
   `hermes cron edit <job_id> --model <provider/model> --provider <provider>`
   e.g. `hermes cron edit 2b39ab1514d2 --model tencent/hy3:free --provider nous`
2. Verify: `hermes cron status <job_id>` → expect `ok` / `execution_success: true`.
3. Re-run if needed: `cronjob action=run job_id=<id>`.

## Pitfall #1 — cronjob tool rejects model/provider
The `cronjob` action=update wrapper does NOT accept model/provider fields, even
though its runtime error suggests `cronjob action=update job_id=… model=…`.
Use `hermes cron edit <id> --model … --provider …` from the terminal instead.

## Pitfall #2 — provider id / model id mismatch (vision 404)
- OpenRouter spells NVIDIA VL: `nvidia/nemotron-nano-12b-v2-vl:free` → returns 404.
- NVIDIA NIM spelling: `nvidia/nemotron-nano-12b-v2-vl` (no `:free`) → works.
If a model 404s ("couldn't find that"), check BOTH provider and exact id spelling.

## Repair a broken `script` field (phantom "Script Error" every tick)

Two modes — **Mode A**: `script` holds a literal STUB (no real script) → clear to `""`. **Mode B**: `script` holds a full COMMAND but a real script exists → relocate it into `scripts/` (see Mode B below, before Pitfall #3). Misdiagnosing B as A and clearing the field DESTROYS the job's intended work.
Symptom: every cron tick delivers "## Script Error / The data-collection script failed"
even though the agent still appears to run. Root cause: the job's `script` field holds a
literal string (e.g. `echo "…stub…"`) instead of a real script path. The runner resolves it
under `$HERMES_HOME/scripts/` → file not found → "Script not found: <path>".

Gate (scheduler.py, `_build_job_prompt`): `script_path = job.get("script"); if script_path:`
→ any non-empty string triggers execution. A *failed* script injects the error block but the
agent STILL runs when `no_agent=False`. With `no_agent=True`, a failed script means no
delivery at all (the script IS the job).

Fix — prefer the CLI, fall back to direct edit:
1. CLI: `hermes cron edit <job_id> --script ""` (empty string clears it; `--script ""` is the
   documented clear value). Re-verify with `hermes cron status <job_id>`.
2. Direct-edit fallback (when `hermes` is not on PATH, e.g. inside a WSL cron context):
   edit `$HERMES_HOME/cron/jobs.json` directly — `json.load`, set the job's `script` to `""`,
   `json.dump(…, indent=2)`, save. Agent-prompt crons (`mentor-ai-daily`) and `no_agent`
   watchdogs (`learn-pensolar`) can share this exact defect — clear `script` on BOTH.
3. Verify with `scripts/verify_cron_script_field.py` (replicates the gate, flags any job whose
   `script` is truthy but not a real file under scripts/). Schema detail in `references/cron-jobs-json-schema.md`.

### Mode B — `script` holds a FULL COMMAND but the job has a real script (RELOCATE, don't clear)
Seen 2026-08-13: `workspace-cleanup-daily` had `script: bash /opt/data/workspace/cleanup-policy.conf`.
The runner does NOT shell-parse the field — it treats the whole string as a filename and joins a
relative one under `$HERMES_HOME/scripts/`, so it looks for
`/opt/data/scripts/bash /opt/data/workspace/cleanup-policy.conf` (a path with an embedded space)
→ `Script not found`. Fix = make the field a real relative script name resolving to a file inside `scripts/`:
1. Copy the script INTO `$HERMES_HOME/scripts/` (the containment guard BLOCKS absolute paths
   outside this dir — Pitfall #12). e.g. `/opt/data/workspace/cleanup-policy.conf` →
   `/opt/data/scripts/cleanup-policy.sh`.
2. Give it a `.sh`/`.bash` extension so the runner picks `bash` (NOT `.conf`/extension-less — Pitfall #13).
   The shebang is ignored; interpreter is extension-only.
3. Set `script` to the relative basename `cleanup-policy.sh` (NOT the absolute path, NOT the old `bash …` string).
4. Verify with `scripts/verify_cron_script_field.py` →
   `[workspace-cleanup-daily] script='cleanup-policy.sh' -> OK (runs before agent)` and
   `PASS: no broken script fields.` (Known-good template: `scripts/cleanup-daily.sh`;
   verified session artifact: `/opt/data/scripts/cleanup-policy.sh`.)

### Runner mechanics (scheduler.py::_run_job_script — confirms Modes A & B)
```
scripts_dir = HERMES_HOME / 'scripts'
raw = Path(script_path).expanduser()
path = raw if raw.is_absolute() else (scripts_dir / raw).resolve()  # relative joins under scripts/
path.relative_to(scripts_dir_resolved)   # RAISES -> Blocked: ... outside the scripts directory if it escapes
if not path.exists(): return False, 'Script not found: {path}'
suffix = path.suffix.lower()
argv = ['bash', str(path)] if suffix in {'.sh','.bash'} else [python_exe, str(path)]
```
So: (a) the field is a PATH, never a shell command; (b) it must resolve INSIDE `scripts/`;
(c) extension decides bash vs python. `bash /x.conf` and `/abs/x.sh` (outside scripts/) both fail;
`x.sh` inside `scripts/` works. Reproduce/verify recipe in `references/cron-script-runner-mechanics.md`.

Pitfall #12 — containment guard: scripts MUST live in HERMES_HOME/scripts/
Absolute `script` paths OUTSIDE `scripts/` are rejected with `Blocked: script path resolves outside
the scripts directory`. You cannot point `script` at `/opt/data/workspace/x.sh` — copy the file
into `scripts/` first. (Relative names are always joined under `scripts/`.)

Pitfall #13 — interpreter chosen by extension, shebang ignored
Only `.sh`/`.bash` run with `bash`. A `cleanup-policy.conf` or extension-less file is executed with
`python` → syntax/exec error. Rename to `.sh` even when content is bash.

Pitfall #14 — `script` is a path, not a command
`bash /opt/data/workspace/x.conf` is read as the literal filename `bash /opt/data/workspace/x.conf`
joined under `scripts/` → not found. Never embed `bash `, args, or flags in the field.

Pitfall #3 — a non-path string in `script`
Do NOT put an `echo`/note stub in `script`. Only real script files (or empty string) belong
there. A stub produces a permanent per-tick error and pollutes the agent prompt.

Pitfall #4 — editing jobs.json in place
Round-trip through `json.load`/`json.dump` (don't hand-edit the escaped `prompt` field — it
holds `\n`/`\u` escapes). Keep `updated_at` current. The scheduler reloads jobs.json per tick;
if it caches in memory, one restart applies the change immediately.

## Verification
After pinning, `cronjob action=run job_id=<id>` must return `last_status: ok`,
`execution_success: true`, and produce the expected output files.

## 🧠 System Interlock: Global model.default changes affect ALL crons

Whenever you change the **global default model** (`hermes config set model.default X`),
**every cron job becomes "unpinned"** because its stored model snapshot no longer matches
the new global default. Even if each job has its own `--model`/`--provider` pin, the
drift guard treats them as drifted until re-pinned.

**Workflow after ANY model.switch in the main loop:**

1. Switch global: `hermes config set model.default poolside/laguna-s-2.1:free`
2. Immediately re-pin EACH cron:
   ```
   hermes cron edit 3dfaf435889a --model tencent/hy3:free --provider nous   # mentor
   hermes cron edit 2b39ab1514d2 --model tencent/hy3:free --provider nous   # learn-pensolar
   ```
3. Verify:
   ```
   python3 -c "import json;d=json.load(open('cron/jobs.json'));print([j['name'] for j in d['jobs'] if j.get('model')])"
   ```
   Every job should show its correct pinned model — **not the new global default**.

**Why this matters**: The drift guard is a spending-protection mechanism, not an
inconvenience. Leaving even one cron unpinned means that job silently inherits whatever
global default is active — which could be laguna-s instead of hy3, breaking the
read-first/gap-search contract your mentor cron depends on.

## Pitfall #5 — silent failure when cronjob tool wraps model/provider
The `cronjob` action=update wrapper does not expose model/provider fields, but it may
return HTTP 200 with body `{"success": true, "message": "No updates provided."}` —
appearing to succeed while **leaving model/provider unchanged** (still inheriting the
drifted global default). Always verify the *persisted* value directly:
`python3 -c "import json;d=json.load(open('cron/jobs.json'));print([j for j in d['jobs'] if j.get('id')==<id>][0].get('model'))"`
If it shows the *old* model, re-pin via `hermes cron edit <id> --model <m> --provider <p>`
and confirm the CLI output shows `Schedule: …` + `Skills: none` (full re-read of the job).

## Pitfall #6 — do not write — then clear a stub script
Do not set `script` to an `echo`/`note` stub "temporarily" and clear it later. The stale
stub emits a phantom "Script Error" on every tick between writing and clearing. If the job
had no real script, set `--script ""` **in the same edit** as pinning, or skip `script`
entirely. For agent-prompt jobs (`mentor-ai-daily`, `learn-pensolar`), the correct final
state is `script=""` exactly.

## Startup enforcement: restart recovery workflow

On every Hermes restart (cron context, Docker container restart, WSL boot), two scripts run in **strict order**:

1. **`enforce_pins.py`** — Batch-re-pins ALL cron jobs to `tencent/hy3:free` / `nous` via `hermes cron edit`. Skips jobs already correctly pinned. Backs up `jobs.json` → `jobs.json.bak` before mutating. This is the automated equivalent of the manual pinning in the Fast Path above — run this FIRST so catchup.py operates on the current job state.

2. **`catchup.py`** — Detects restart via `/proc/stat` `btime` compared against `/opt/data/.boot_time`. If the boot-time file is missing or older than the actual kernel boot time, it scans all jobs for missed runs, fires them via `hermes cron run <job_id>`, and records the boot time.

**Pitfall #7 — ordering matters**
Always run `enforce_pins.py` before `catchup.py`. enforce_pins rewrites `jobs.json` in place; catchup.py reads that same file. If run out of order, catchup may read stale schedule data. This is typically invoked by a sentinel cron job (`startup-catchup-enforcement`) or via direct terminal invocation on container/WSL boot.

**Pitfall #8 — catchup.py has a limited cron-expression parser**
`calculate_missed()` only handles hardcoded patterns (`0 7 * * *`, `0 7,11,15,19 * * *`, `0 6 * * 1-6`, `0 0 * * 0`, etc.). Jobs with non-standard schedules (e.g. `1 1 1 1 1` — the sentinel itself) are skipped. If a job's schedule doesn't match a known pattern, catchup won't detect missed runs for it. Verify the schedule expression is in the supported set.

**Output routing**
The startup enforcement workflow should write results to `/opt/data/knowledge/cron_runlog.md` **only** — do not deliver via send_message or print to terminal for delivery. catchup.py's `fire_job()` writes its own entries to the runlog internally (only when it actually fires a job); the stdout from both scripts must also be captured and appended to the runlog.

**Pitfall #9 — catchup.py stdout is NOT auto-written to runlog**
catchup.py only writes to `cron_runlog.md` inside `fire_job()` (the per-job entry). The top-level `[catchup] …` status messages go to stdout only. If you run the scripts and only check the runlog, you'll miss the summary line. Always capture both script stdout AND the runlog file to get the full picture.

## Pitfall #11 — approval gate for autonomous file creation (OAKAI rule)

By default, mentor crons may auto-generate supporting files (e.g. `golden_v1.csv`, `score_eval.py`). Per OAKAI founder's directive: **any cron that creates NEW files outside pre-approved paths** (`mentor/daily_notes/`, `pensolar/logs/`, `marketing/daily-brief-*`, `workspace/INDEX.md`) must embed a `/approve` prompt in its output and **halt before writing**. Approved paths are defined in the cron's `enabled_toolsets` as file-safe zones. If a file would land in an unapproved path (e.g. `/opt/data/docs/` or root `/opt/data/`), the cron instead writes the proposed content into its own daily note under `<pending>/filename` and prompts the user to approve.

## OAKAI Autonomous Stack — 4-stream cron pattern (verified 2026-08-12)

A founder building an AI consultancy → enterprise solution provider runs **4 autonomous streams** in parallel, each with a distinct model and purpose:

1. **`mentor-ai-daily`** (4x/day) — 07:00 / 11:00 / 15:00 / 19:00 MYT  
   Keeps the founder technically sharp. Adaptive: if tests unanswered, ships artifacts + test harness instead of looping teasers.
   Schedule: `0 7,11,15,19 * * *` (UTC+8)

2. **`learn-pensolar`** (daily) — 15:00 MYT  
   Compresses solar-energy domain intel into structured summaries.
   Schedule: `0 7 * * *` (UTC+8)

3. **`strategic-coo-guidance`** (weekly) — Sundays 08:00 MYT  
   Directs company-building: budget allocation, risk register, go-to-market priorities.
   Schedule: `0 0 * * 0` (UTC+8)

4. **`marketing-advisor-daily`** (Mon-Sat) — 06:00 MYT  
   Drives visibility: 1 LinkedIn post/day + group engagement + lead-magnet ideation.
   Schedule: `0 22 * * 1-6` (UTC+8)

All streams write to a master INDEX.md. SUMMARY.md ≤32KB cap (hard halt if exceeded). Each cron pulls only GAPS (not generic content) — hy3 for synthesis, laguna-s only for raw passthrough.

**Key lesson**: crons can be the founder's "COO + CTO + CMO" stack — but each must have a DISTINCT model and purpose. Do NOT let them blur into generic content farms.

The `mentor-ai-daily` cron moved from 2x → 3x → **4x/day** (`0 7,15,22 * * *` → `0 7,11,15,19 * * *`)\\nto accelerate learning for the OAKAI founder. Three new risks surface:

- **Pitfall #10a — catchup.py pattern mismatch**: `calculate_missed()` must include\n  `0 7,11,15,19 * * *` in its hardcoded list, or downtime at 11:00 / 19:00 MYT silently\n  misses lessons. Fix: add the pattern (done 2026-08-12).\n- **Pitfall #10b — schedule immutability still holds**: to reschedule from 3x → 4x,\n  you DELETE (`cronjob action=remove`) + RECREATE the job. Don't rely on `cronjob update`.\n- **Pitfall #10c — verify output, not just schedule**: after changing schedule,\n  run `cronjob action=run` and inspect BOTH `cron_runlog.md` + the output dir.\n  A successful schedule change is NOT proof of execution.\n
**OAKAI context**: All **6 crons** now pinned to `tencent/hy3:free` via Nous. The 4x mentor\nschedule is live and verified:
- Execution confirmed at 02:50 UTC (10:50 MYT slot — the "Eve" run)\n
**Verification checklist for 4x schedule changes**:\n
1. After edit: `hermes cron edit <id> --schedule "0 7,11,15,19 * * *"`\n
2. Run immediately: `cronjob action=run job_id=<id>`\n
3. Check: `knowledge/mentor/daily_notes/YYYY-MM-DD.md` was rewritten\n
4. Check: `workspace/INDEX.md` got new append line for this run\n
5. Check: `cron_runlog.md` shows `[catchup] Done. N jobs backfilled` or `0 missed`
\n## Related
`hermes cron edit --help` (all editable fields), `cronjob` tool (list/run/remove),
`model-selection-policy` (covers model *selection*; this skill covers *pinning* + restart recovery). See `references/startup-enforcement-scripts.md` for script internals. `references/cron-script-runner-mechanics.md` documents the `script` field resolver + containment guard + extension→interpreter rule (covers Mode B / "Script not found" from a full-command `script`).