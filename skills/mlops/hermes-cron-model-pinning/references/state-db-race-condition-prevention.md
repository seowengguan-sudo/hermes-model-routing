# Git Sync & state.db Race-Condition Protection (#68474)

## Incident Timeline (Aug 12, 2026, MYT)

| UTC Time | Commit | Event | Impact |
|---|---|---|---|
| 13:14:19 | `c2e637c` | Auto-sync: "initial push after PAT setup" | Committed state.db as 0 bytes (race condition) |
| 13:18:16 | `450adc2` | "sync knowledge base + add .gitignore" | Committed deletion of knowledge/, skills/, workspace/, cron/, memories/ from git tracking |
| 13:18:54 | `450adc2` | `.gitignore` updated | Added .env, config.yaml, model_state.json exclusions |

## Root Cause: Git Auto-Sync Race Condition

1. User said `+pls user from githubtoken.txt` — triggered agent-initiated git sync
2. Agent ran: `git add -A && git commit && git push`
3. **Race:** Hermes was running (cron jobs executing) → SQLite doing WAL checkpoint on state.db
4. Git's `git add` read state.db at the exact moment file was 0 bytes (between unlink and recreate)
5. Git committed 0-byte file → sessions table empty → dashboard blank

The zeroed-DB guard `is_zeroed_state_db()` only catches `size > 0 + all-NUL`, not 0-byte files.

## Protection Applied (All Verified)

### 1. .gitignore — Untrack all runtime files

The full set of runtime files now ignored (`.gitignore` updated and verified):

**Runtime SQLite databases (race-condition risk):**
```
state.db, state.db-wal, state.db-shm, state.db-journal
cron/executions.db, cron/executions.db-shm, cron/executions.db-wal, cron/executions.db-journal
kanban.db, kanban.db-shm, kanban.db-wal, kanban.db-journal
projects.db, projects.db-shm, projects.db-wal, projects.db-journal
*.db-shm, *.db-wal, *.db-journal
```

**Runtime logs (never commit):**
```
logs/agent.log, logs/dashboard-auth.log, logs/errors.log, logs/gui.log
logs/gateway_start.log, logs/tui_gateway_crash.log, logs/gateway.log
logs/gateway-exit-diag.log, logs/gateway_faulthandler.log
logs/gateways/, logs/*.log
```

**Runtime caches & lock/pid files:**
```
.hermes_history, .boot_time, .tui-theme-boot.json
.lsp/, .lsp.lock, .processes.lock
gateway.lock, gateway.pid, gateway-starts.log, gateway_state.json
context_length_cache.yaml, channel_directory.json
models_dev_cache.json, provider_models_cache.json, ollama_cloud_models_cache.json
skills/.usage.json, skills/.bundled_manifest.lock
sketches.lock, .skills_prompt_snapshot.json
```

### 2. Pre-commit hook — Block runtime file commits

```bash
# ── Block state.db and other runtime SQLite files ──
STAGED_DB_FILES=$(git diff --cached --name-only | grep -E "^.*\\.db$|state\\.db.*|cron/executions|kanban\\.db|projects\\.db" 2>/dev/null)
if [ -n "$STAGED_DB_FILES" ]; then
    echo "❌  BLOCKED: Runtime SQLite files must not be committed (#68474)"
    echo "   These are live SQLite files — committing during active writes"
    echo "   causes 0-byte truncation → blank dashboard."
    echo "   Files blocked: $STAGED_DB_FILES"
    exit 1
fi
```

**Pre-commit hook behavior (verified):**
- Blocks any commit where state.db* files are staged (force-add does not bypass)
- Also catches by glob: any `*.db` file staged for commit
- Allows safe commits (non-runtime files pass through)
- Bash syntax validated with `bash -n`
- Verified: state.db commit → exit 1 (blocked); safe commit → exit 0 (allowed)
- Also blocks secrets: `ghp_*`, `NVIDIA_API_KEY`, `api_key=`, etc.

## Recovery Commands (If It Happens Again)
```bash
git checkout 54c4651 -- skills/ knowledge/ workspace/ cron/ docs/ memories/ model/
git show c2e637c:state.db-wal > /opt/data/state.db-wal
hermes gateway run
```

## Variant: state.db valid but TUI sessions missing
If the user reports the chat panel showing **only cron sessions** and no earlier human chats,
but `state.db` is NOT zeroed (it's the full file with valid SQLite header), this is a DIFFERENT
failure than the git-race zeroing above. In this variant the TUI sessions were lost *before*
the post-incident snapshot was taken. WAL-from-git and snapshot restore will NOT recover them.
See `hermes-runtime-introspection` → `references/state-db-recovery.md` ("Variant: state.db valid
but missing ALL TUI sessions") for the diagnostic (`SELECT source, COUNT(*) FROM sessions GROUP BY source`)
and prevention recommendation (shorter-interval backups).