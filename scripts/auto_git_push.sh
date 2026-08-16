#!/bin/bash
# Daily auto-git-push cron script for OAKAI project
# Commits important changes and pushes to GitHub daily for protection/backups
# Only commits source files, not runtime data or large binaries

set -e
cd /opt/data

# Update .gitignore
git add .gitignore

# Stage important project files only
git add doc_reader_onefile.py 2>/dev/null
git add deploy_doc_reader.sh 2>/dev/null
git add knowledge/data_security_governance_policy.md 2>/dev/null
git add scripts/auto_git_push.sh scripts/cleanup.sh 2>/dev/null
git add workspace/Samples/poc_reader_windows_portable.zip 2>/dev/null
git add workspace/Samples/ARCHITECTURE.md 2>/dev/null

# Check if there are staged changes
if git diff --cached --quiet; then
    echo "[ $(date) ] No important changes to commit"
    exit 0
fi

# Count changes
CHANGED=$(git diff --cached --name-only | wc -l)
echo "[ $(date) ] Committing $CHANGED files"

# Commit
COMMIT_MSG="auto: daily sync for $(date +%Y-%m-%d)"
git commit -m "$COMMIT_MSG" 2>&1 | tail -2

# Push to GitHub
echo "[ $(date) ] Pushing to GitHub..."
git push origin main 2>&1

echo "[ $(date) ] Daily sync complete"
