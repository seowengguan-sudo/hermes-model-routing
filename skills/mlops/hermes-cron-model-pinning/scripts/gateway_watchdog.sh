#!/bin/bash
# Gateway watchdog - checks if the Hermes messaging gateway is running
# under s6 supervision and restarts it if not.
#
# Use case: combined dashboard+gateway Docker container where
# container_boot.py skips gateway service-slot registration because
# PID 1 is `hermes dashboard`. This watchdog ensures the gateway
# auto-recovers within 2 minutes of any crash/container restart.
#
# Runs every 2 minutes via cron with no_agent=true (no LLM tokens).

set -e

# Check if gateway service slot exists and is up
STATUS=$(/command/s6-svstat /run/service/gateway-default 2>&1) || true

if echo "$STATUS" | grep -q "up"; then
    # Gateway is running fine
    exit 0
fi

# Gateway is down - check if service slot exists
if [ ! -d /run/service/gateway-default ]; then
    # Service slot missing - recreate it
    /opt/hermes/.venv/bin/python3 -c "
import sys; sys.path.insert(0, '/opt/hermes')
from hermes_cli.service_manager import S6ServiceManager
mgr = S6ServiceManager()
mgr.register_profile_gateway('default')
" 2>&1 || true
fi

# Ensure desired_state is set in gateway_state.json
/opt/hermes/.venv/bin/python3 -c "
import json, os
state_file = '/opt/data/gateway_state.json'
if os.path.exists(state_file):
    state = json.load(open(state_file))
    if state.get('gateway_state') == 'running' and 'desired_state' not in state:
        state['desired_state'] = 'running'
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
" 2>&1 || true

# Trigger s6-svscan to pick up the service
/command/s6-svscanctl -a /run/service 2>&1 || true
sleep 2

# Start the service
/command/s6-svc -u /run/service/gateway-default 2>&1 || true
sleep 3

# Verify
STATUS=$(/command/s6-svstat /run/service/gateway-default 2>&1) || true
echo "Gateway watchdog: $STATUS"
