# Pitfalls confirmed — cron setup session 2026-08-11

## 1. Drift guard silently kills unpinned crons
When the main `model.default` changes mid-session (e.g. hy3 → laguna-s), any cron job
that does NOT have `model`/`provider` explicitly pinned is **blocked** with:
```
RuntimeError: Skipped to prevent unintended spend: global inference config drifted
since this job was created (model 'tencent/hy3:free' -> 'poolside/laguna-s-2.1:free'),
and this job is unpinned. No inference call was made.
See #44585.
```
**Fix:** Pin every cron job explicitly via CLI (the `cronjob` create/edit tool wrapper
does NOT expose model/provider — it silently snapshots the global default at creation):
```
hermes cron edit <job_id> --model tencent/hy3:free --provider nous
```
Then verify: `cronjob action=list` must show `model: tencent/hy3:free` non-null.
A job that shows `model: null` will FAIL every run.

## 2. Path resolution in prompts vs agent cwd
The agent's cwd inside a cron run is `/opt/hermes` (the Docker container root), NOT
`/opt/data`. Relative prompt paths like `knowledge/.../../workspace/INDEX.md` resolve
relative to /opt/hermes and produce STRAY directories (observed: a file written to
`/opt/hermes/knowledge/workspace/` — silently off-target).

**Fix:** Use ABSOLUTE paths everywhere in cron prompts:
```
/opt/data/workspace/INDEX.md
/opt/data/knowledge/mentor/SUMMARY.md
```
This is a silent data-loss trap — the cron reports "ok" but writes to a garbage path.

## 3. Model pinning via `cronjob` tool doesn't work
The `cronjob` create/edit tool ignores `--model`/`--provider` kwargs silently (returned
"No updates provided"). The ONLY reliable pinning is the CLI:
`hermes cron edit <id> --model <model> --provider <provider>`

## 4. `cronjob run` vs `cronjob action='run'`
- `cronjob action='run'` (the tool): returns JSON with `execution_success` — clean.
- `cronjob run` (the CLI): returns a human-style output, harder to parse programmatically.
Both work but use the TOOL form for verifiability.

## 5. Workspace cleanup glob must match daily file naming
The cleanup cron targets `daily-*.md` in `/opt/data/workspace/`. If daily digests are
named `daily-learning-*.md`, the glob MISSES them. Verify the cleanup script path+pattern
matches the file naming scheme exactly.
