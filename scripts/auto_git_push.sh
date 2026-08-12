#!/bin/bash
# auto_git_push.sh
# Auto-commits and pushes changes to GitHub after successful cron execution.
# Called automatically by workspace-cleanup-daily cron job.

set -e

REPO_DIR="/opt/data"
BRANCH="master"
REMOTE="origin"

# Only proceed if there are staged or unstaged changes
cd "$REPO_DIR"
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    exit 0  # Not a git repo — skip silently
fi

# Stage everything
git add -A

# Commit if there are changes
if git diff --cached --quiet; then
    # No changes — nothing to commit
    :
else
    # Write commit message with timestamp
    MSG="Auto-sync: $(date -u +%Y%m%dT%H%M%SZ)"
    git commit -m "$MSG" --allow-empty 2>/dev/null || true
fi

# Attempt push (will fail silently if no credentials/network)
if git push "$REMOTE" "$BRANCH" 2>/dev/null; then
    echo "✅ Pushed to GitHub at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
else
    echo "⚠️ Push skipped (credentials/network/WAF issue)"
fi
