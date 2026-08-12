#!/bin/bash
# Auto-cleanup policy: delete daily files older than 14 days
# Runs nightly via cronjob: 0 2 * * *
# Schedule: `0 2 * * *` (UTC) = 10:00 MYT nightly
# Script path in cron job's `script` field, NOT prompt.
# This is a no_agent=True watchdog pattern: script IS the job.
find /opt/data/workspace -maxdepth 1 -name "daily-*.md" -mtime +14 -delete
# Keep INDEX.md + cleanup-policy.conf always (they don't match daily-*.md glob)
echo "cleanup complete at $(date)"
