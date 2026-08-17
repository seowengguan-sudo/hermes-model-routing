# Gateway Auto-Restart Failure Diagnosis (Aug 2026 session)

## Symptom
Gateway shows `Gateway Status: Off` in dashboard. `hermes gateway start` fails with:
```
✗ no such gateway 'default': register it with `hermes profile create default` first
```
CLI `hermes gateway status` shows: `⚠ Stale gateway_state.json: recorded state 'running' but the recorded process is gone`.

## Root Cause
Two-layer failure:

1. **Stale `gateway_state.json` lacking `desired_state`**: After an ungraceful shutdown (SIGTERM from container lifecycle), `gateway_state.json` was left with `gateway_state: "running"` but **no `desired_state` field**. On container boot, `container_boot.py` calls `_read_desired_state()` which prefers `desired_state`, falls back to `gateway_state` — but the s6 service slot was still never registered.

2. **s6 service slot wiped on tmpfs**: s6 service directories live on tmpfs (`/run/service/`). `container_boot.py` (via `cont-init.d/02-reconcile-profiles`) is supposed to recreate `gateway-default` on every boot by calling `S6ServiceManager.register_profile_gateway('default')`. When `gateway_state.json` is stale or missing, the default profile slot is not auto-started — and since no slot exists, `hermes gateway start` has nothing to target.

## Fix (applied session-of-Aug-13-2026)
1. Ensure `gateway_state.json` has `desired_state: "running"`:
   ```python
   import json
   state = json.load(open('/opt/data/gateway_state.json'))
   state.setdefault('desired_state', state.get('gateway_state', 'running'))
   json.dump(state, open('/opt/data/gateway_state.json', 'w'), indent=2)
   ```
2. Register the s6 service slot via `S6ServiceManager`:
   ```python
   from hermes_cli.service_manager import S6ServiceManager
   mgr = S6ServiceManager()
   mgr.register_profile_gateway('default')
   ```
3. Let s6-svscan pick up the new service:
   ```bash
   /command/s6-svscanctl -a /run/service
   /command/s6-svc -u /run/service/gateway-default
   ```

## Verification
```bash
/command/s6-svstat /run/service/gateway-default
# Output: up (pid <N> pgid <N>) <seconds>
```

## Watchdog (cron, every 5 min)
A `no_agent` cron job (`gateway-watchdog`) checks s6 status every 5 minutes and recreates the service slot + restarts if down. Script checks:
- `s6-svstat /run/service/gateway-default` → if `up`, exit 0
- If down or slot missing → register via `S6ServiceManager`, ensure `desired_state`, rescan s6, start service

## Key paths
- `hermes_cli/container_boot.py` — boot-time reconciliation (cont-init.d/02-reconcile-profiles)
- `hermes_cli/service_manager.py` — `S6ServiceManager.register_profile_gateway()` / `_render_run_script()`
- `/run/service/gateway-default/` — s6 service slot (tmpfs, wiped on restart)
- `/opt/data/gateway_state.json` — gateway lifecycle state (persistent; has `desired_state` + `gateway_state`)
- `/command/s6-svstat`, `/command/s6-svscanctl`, `/command/s6-svc` — s6 binaries (not on PATH; use `/command/`)

## CLI quirk
`hermes gateway status` prints "Running manually, not as a system service" even when s6-supervise IS managing it. This is cosmetic — the CLI checks for systemd/launchd unit paths, not the s6 service slot. Verify via `s6-svstat` instead.
