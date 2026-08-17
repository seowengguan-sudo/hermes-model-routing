# Selective Auto-Git Push: Safe Daily Backup Pattern

## Context
The user needs daily pushes to GitHub for protection/backups, but a blanket `git add -A` can
trigger the state.db race condition (Pitfall #15 in this skill). The pattern below selectively
stages only source files, excluding runtime files.

## Pattern: Selective staging via explicit file list

Instead of `git add -A`, stage only project source files that should be backed up:

```bash
#!/bin/bash
# /opt/data/scripts/auto_git_push.sh
cd /opt/data

# Stage specific source files only (NOT data/, .venv/, caches)
git add \
  doc_reader_onefile.py \
  redaction_engine.py \
  safe_format.py \
  doc_reader_tk.py \
  doc_reader_desktop.py \
  deploy_doc_reader.sh \
  knowledge/data_security_governance_policy.md \
  scripts/auto_git_push.sh \
  .gitignore

# Verify no runtime files snuck in
STAGED_DB=$(git diff --cached --name-only | grep -E '\.db$|state\.db' 2>/dev/null)
if [ -n "$STAGED_DB" ]; then
    echo "ABORT: runtime files staged: $STAGED_DB"
    git reset HEAD -- .
    exit 1
fi

# Commit + push
git commit -m "auto: daily sync for $(date +%Y-%m-%d)"
git push origin main
```

## Cron Job Configuration
```yaml
# Schedule: daily at 6:00 UTC
sched: "0 6 * * *"
no_agent: true
script: auto_git_push.sh
deliver: local
```

## Why This Is Safe
1. **No `git add -A`** — only explicitly named files are staged
2. **Runtime file check** — aborts if any `.db` or `state.db` files appear in staging
3. **`.gitignore` covers runtime files** — state.db, executions.db, kanban.db, etc.
4. **Small commit** — 10-15 source files, not 9000+ runtime/cache files
5. **Push timeout avoided** — commit is <50KB, push completes in seconds

## Verified Example
- Commit: `81b5404 feat: OAKAI enterprise data anonymization engine` (10 files)
- Push: successful, completed in ~2 seconds
- No state.db corruption (selective staging avoided race condition)