#!/bin/bash
# Auto-cleanup policy: delete daily files older than 14 days
# Runs nightly via cronjob (workspace-cleanup-daily). Registered as the
# cron 'script' field with the relative name 'cleanup-policy.sh' so the
# scheduler resolves it under HERMES_HOME/scripts/ and runs it with bash.
#
# Intended original line (kept for reference):
#   0 2 * * * cd /opt/data && bash workspace/cleanup-policy.conf

# Step 1: Cleanup stale daily files (absolute path -> cwd-independent)
find /opt/data/workspace -maxdepth 1 -name "daily-*.md" -mtime +14 -delete

# Step 2: Auto-sync changes to GitHub (if credentials available)
if [ -x /opt/data/scripts/auto_git_push.sh ]; then
    /opt/data/scripts/auto_git_push.sh 2>/dev/null || true
fi
