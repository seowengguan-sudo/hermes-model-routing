# Hermes cron jobs.json — schema & `script` field notes

Location: `$HERMES_HOME/cron/jobs.json` (on this host `/opt/data/cron/jobs.json`).
Companion files in the same dir: `executions.db` (run history), `output/<job_id>/*.md`
(per-run agent output), `.jobs.lock`.

## Top-level shape
```json
{ "jobs": [ { …job… } ], "updated_at": "2026-08-11T10:43:35.421087+00:00" }
```

## Per-job key fields
| field | meaning |
|---|---|
| `id` | 12-char hex job id (used by `hermes cron edit <id>`, `cronjob action=run`) |
| `name` | human label, e.g. `mentor-ai-daily` |
| `prompt` | the agent prompt text (escaped `\n` / `\u` — never hand-edit) |
| `script` | optional pre-run data-collection script; `""` = disabled |
| `no_agent` | `false` = run agent with prompt; `true` = script IS the job |
| `model` / `provider` | pinned inference (see model-pinning section) |
| `schedule` | `{ "kind": "cron", "expr": "0 7,19 * * *" }` |
| `enabled` / `state` | on/off + scheduler state |
| `repeat` | `{ "times": null, "completed": N }` |
| `last_run_at` / `last_status` / `last_error` | run telemetry |

## `script` field semantics (from `/opt/hermes/cron/scheduler.py`)
- Relative paths resolve under `$HERMES_HOME/scripts/`; absolute paths are validated to
  stay inside that dir (path-traversal guard). A path outside it is *blocked*, not run.
- Truthy `script` → runner executes it; **stdout** is injected as `## Script Output`
  context into the agent prompt.
- If the script **fails**, the runner injects `## Script Error` + the error text but the
  agent STILL runs when `no_agent=False`. (`no_agent=True` + failed script ⇒ no delivery.)
- Empty string `""` → `if script_path:` is false → no script runs, agent runs directly.
- CLI clear value: `hermes cron edit <id> --script ""`.

## Direct-edit fallback (no `hermes` CLI on PATH)
```python
import json, datetime
p = "/opt/data/cron/jobs.json"
d = json.load(open(p))
for j in d["jobs"]:
    if j.get("script"): j["script"] = ""
d["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
json.dump(d, open(p, "w"), indent=2, ensure_ascii=True)
```
Round-trip only — never hand-edit the escaped `prompt`. Verify with
`scripts/verify_cron_script_field.py`.
