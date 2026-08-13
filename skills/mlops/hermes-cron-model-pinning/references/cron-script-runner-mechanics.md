# Cron `script` field — runner mechanics (from scheduler.py::_run_job_script)

Verified 2026-08-13 against `/opt/hermes/cron/scheduler.py`. Durable behavior of the
pre-run data-collection `script` field for a Hermes cron job.

## Resolution
```
scripts_dir = HERMES_HOME / 'scripts'          # e.g. /opt/data/scripts
raw = Path(script_path).expanduser()
path = raw if raw.is_absolute() else (scripts_dir / raw).resolve()
```
- Relative `script` (e.g. `cleanup-policy.sh`) → joined under `scripts/`
  → `/opt/data/scripts/cleanup-policy.sh`.
- Absolute `script` → used as-is, BUT still must resolve INSIDE `scripts/` (containment guard).

## Containment guard
```
path.relative_to(scripts_dir_resolved)   # ValueError -> blocked
```
Any path resolving outside `scripts/` (absolute elsewhere, or `..` traversal) is rejected:
`Blocked: script path resolves outside the scripts directory (<scripts_dir>): <script>`.
=> You can NEVER point `script` at `/opt/data/workspace/x.sh`. Copy the file into `scripts/`.

## Existence + type
```
if not path.exists():   return False, 'Script not found: {path}'
if not path.is_file():  return False, 'Script path is not a file: {path}'
```
This is the exact error the failed job emitted:
`Script not found: /opt/data/scripts/bash /opt/data/workspace/cleanup-policy.conf`
(the whole `bash /...` string became one filename with an embedded space).

## Interpreter (extension-only; shebang IGNORED)
```
suffix = path.suffix.lower()
argv = ['bash', str(path)] if suffix in {'.sh', '.bash'} else [python_exe, str(path)]
```
- `.sh` / `.bash` → run with `bash`.
- anything else (`.conf`, `.py`, extension-less) → run with `python` (sys.executable).
=> A bash script named `cleanup-policy.conf` is run with `python` and fails. Always use `.sh`.

## How to verify a fix
1. `python3 scripts/verify_cron_script_field.py` (ships in this skill; replicates the gate).
   Expect per job: `script='<name>' -> OK (runs before agent)` and final
   `PASS: no broken script fields.`
2. Optional real-execution check (confirms exit 0, no stray deletions):
   `bash /opt/data/scripts/cleanup-policy.sh; echo "exit=$?"`
   (only deletes `daily-*.md` older than 14 days under `/opt/data/workspace`.)

## Reproduce the Mode B bug
Set `script` to `bash /opt/data/workspace/cleanup-policy.conf` (a full command) and run the
verifier → it reports the embedded-space path as not a file. The correct value is the relative
basename `cleanup-policy.sh` after copying the script into `scripts/`.
