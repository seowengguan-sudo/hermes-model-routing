# Gateway watchdog: recovering a dead messaging gateway in a combined dashboard+gateway container

## Symptom
`hermes gateway status` reports:
```
✗ no such gateway 'default': register it with `hermes profile create default` first
Gateway is not running
Stale gateway_state.json: recorded state 'running' but the recorded process is gone
```

The gateway process was killed (SIGTERM from container lifecycle, OOM, crash) but:
- The s6 service slot (`/run/service/gateway-default/`) is gone (tmpfs, wiped on restart)
- `container_boot.py` did NOT recreate it because the container runs `hermes dashboard` as PID 1
- `container_boot.py` detects "dashboard container" and skips gateway service registration entirely
  (by design: to avoid log-lock contention in multi-container setups with shared HERMES_HOME)
- The cron watchdog gap means up to N minutes of unrecoverable gateway downtime

## Root cause
In a **single-container** setup (dashboard + gateway in one container), `container_boot.py`'s
`main()` skips all gateway registration when it detects `_is_dashboard_container()` returns True.
This is correct for **multi-container** deployments (separate gateway container + separate dashboard
container sharing a volume), but **wrong** for **single-container** deployments where the same
container must run both.

The detection: PID 1 argv contains `dashboard` → `container_boot.py` prints "reconcile: skipping
(dashboard container — does not need per-profile gateways)" and returns 0 without registering
any gateway service slots.

## Fix: `gateway_state.json` must have `desired_state`
Even if `container_boot.py` DID run, it reads `_read_desired_state()` which prefers the
`desired_state` field. If `gateway_state.json` only has `gateway_state` (old format),
the fallback logic normalizes `draining`/`degraded` → `running` but may miss other states.

**Always ensure `gateway_state.json` has `desired_state: "running"`** for a gateway that
should auto-start.

## Fix: watchdog cron job (the recovery mechanism)
Since `container_boot.py` source is root-owned and can't be patched at runtime, create a
recurring cron job (every 2 minutes, `no_agent=true`) that:

1. Checks `s6-svstat /run/service/gateway-default` → if `up`, exit 0
2. If service slot missing: calls `S6ServiceManager.register_profile_gateway('default')`
3. Ensures `gateway_state.json` has `desired_state: "running"`
4. Runs `s6-svscanctl -a /run/service` (scan for new service dirs)
5. Runs `s6-svc -u /run/service/gateway-default` (start the service)
6. Verifies with `s6-svstat`

## Key paths and constants
- **s6 binaries**: `/command/s6-svstat`, `/command/s6-svc`, `/command/s6-svscanctl` (NOT in PATH)
- **Service slot**: `/run/service/gateway-default/` (tmpfs, wiped on container restart)
- **Service manager**: `hermes_cli.service_manager.S6ServiceManager` (in `/opt/hermes/.venv`)
- **Gateway state**: `/opt/data/gateway_state.json` (persistent, on HERMES_HOME volume)
- **s6 scandir**: `/run/service` (set via `S6_PROFILE_GATEWAY_SCANDIR` env var)

## Verification recipe
1. `ps aux | grep "hermes gateway run"` → process running
2. `/command/s6-svstat /run/service/gateway-default` → `up (pid NNNN)`
3. `hermes gateway status` → shows running
4. `python3 -c "import json; print(json.load(open('/opt/data/gateway_state.json')).get('desired_state'))"` → `running`

## Pitfall — false "started" message
The CLI (`hermes gateway status`) prints "Running manually, not as a system service"
even when the gateway IS under s6 supervision. This is because the CLI checks for
the systemd/launchd unit path, not the s6 service. Don't trust the CLI message;
verify with `s6-svstat` directly.

## Pitfall — `container_boot.py` skip is silent
When `container_boot.py` skips dashboard containers, it prints a message to stdout
but does NOT write to `container-boot.log`. The absence of that log file confirms
reconciliation was skipped.
