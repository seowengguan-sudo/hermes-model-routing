#!/bin/bash
# Daily auto-git-push (curated scope) — VForge / Hermes workspace backup.
# Restored 2026-08-20 to match the original "reference current files only" scope,
# with SAFE-GUARD: a file is staged ONLY if it exists on disk as a real file/symlink.
# Missing/deleted paths are skipped (logged) and NEVER staged as deletions, so this
# cron can never push a file OFF GitHub. No `git add -A`. Branch main -> origin/main.
#
# Learning from prior break: the old script `git add doc_reader_onefile.py` after the
# OAKAI->VForge migration deleted those files from the repo. This version refuses to.

set -uo pipefail
cd /opt/data || exit 1

LOG="$HOME/../logs/auto_git_push.log"
LOGDIR="$(dirname "$LOG")"
[ -d "$LOGDIR" ] || mkdir -p "$LOGDIR"
ts() { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "[ $(ts) ] $*" | tee -a "$LOG"; }

GIT="/usr/bin/git"
G=$(git config --global credential.helper >/dev/null 2>&1; echo ok)
# Ensure git resolves the stored credential (helper = store in /opt/data/home/.gitconfig)
export HOME=/opt/data/home

# Curated, explicitly-named file set (NO globs, NO add -A).
# This is the exact source-file scope from the last-good commit (2546748),
# plus this very script so the cron self-maintains.
FILES=(
  ".gitignore"
  "knowledge/data_security_governance_policy.md"
  "workspace/Samples/poc_reader_windows_portable.zip"
  "workspace/Samples/ARCHITECTURE.md"
  "scripts/auto_git_push.sh"
)

log "=== Daily sync start (safe, curated scope) ==="

STAGED_ANY=0
for f in "${FILES[@]}"; do
  # Only stage if it exists on disk as a real file or a symlink with a live target.
  if [ -e "$f" ]; then
    if "$GIT" add -- "$f" 2>>"$LOG"; then
      log "staged: $f"
      STAGED_ANY=1
    else
      log "WARN: git add failed for $f (skipped)"
    fi
  else
    # File is missing from disk (e.g. migrated away). Do NOT stage -> no deletion pushed.
    log "SKIP (not on disk, kept on GitHub): $f"
  fi
done

# Commit only if something was actually staged.
if [ "$STAGED_ANY" -eq 1 ] && ! "$GIT" diff --cached --quiet; then
  CHANGED=$("$GIT" diff --cached --name-only | wc -l)
  log "Committing $CHANGED file(s)"
  "$GIT" commit -m "auto: daily sync for $(date +%Y-%m-%d)" >>"$LOG" 2>&1 || log "WARN: commit failed"
  log "Pushing to origin main..."
  if "$GIT" push origin main >>"$LOG" 2>&1; then
    log "Push OK"
  else
    log "ERROR: push failed (see log above) — no data lost locally"
  fi
else
  log "No changes to commit (clean or only deletions skipped)"
fi

log "=== Daily sync end ==="
echo "DONE"
