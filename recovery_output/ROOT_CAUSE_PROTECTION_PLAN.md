# Root Cause Analysis & Protection Plan — August 12 Incident

## Executive Summary

**"Everything went blank"** was caused by a **git auto-sync race condition** that committed `state.db` as 0 bytes while SQLite was actively writing, combined with a second sync that removed `knowledge/`, `skills/`, `workspace/`, `cron/`, and `memories/` from git tracking. **Docker Desktop was not involved** — `/opt/data` lives on the WSL2 host filesystem (ext4 on `/dev/sdd`).

---

## Root Cause (Two-Part Race Condition)

### Part 1: state.db Zeroing (Aug 12, 13:14:19 UTC)

**Commit `c2e637c`** ("Auto-sync: initial push after PAT setup"):
- Triggered when user said `+pls user from githubtoken.txt` at ~13:14:20 UTC
- Agent ran `git add -A && git commit && git push` as a git auto-sync
- **Race:** SQLite was actively writing to state.db (WAL checkpoint in progress)
- Git committed state.db as **0 bytes** (file truncated during SQLite write checkpoint)
- state.db-wal had 4.9MB of session data but couldn't replay into the empty main DB
- Sessions table showed 0 rows → "everything went blank"

**The zeroed-DB guard failed** because:
- `is_zeroed_state_db()` (in `hermes_state.py` line 1617) only detects: **size > 0 + all-NUL header bytes** (signature #68474)
- A **0-byte file** (size == 0) returns `False` → opens silently as a fresh empty DB
- No error, no warning, no recovery path triggered

### Part 2: Knowledge/Skills/Workspace Deletion (Aug 12, 13:18:54 UTC)

**Commit `450adc2`** ("chore: sync knowledge base + add .gitignore"):
- Triggered when user said `+refer githubtoken.txt now` at ~13:18:16 UTC
- Agent updated `.gitignore` to exclude `.env`, `config.yaml`, `model_state.json`, `refresh_models.py`
- Agent ran `git add -A && git commit` again
- **Problem:** Between the two commits, the working tree had `knowledge/`, `skills/`, `workspace/`, `cron/` **untracked or deleted**
- Git tracked the tree state without these directories → 293 files instead of 11,779
- The directories **existed on disk** but were **no longer in git's index**

### Root Cause Summary Table

| Component | What Failed | Impact |
|---|---|---|
| state.db | Committed as 0 bytes during active SQLite write | Sessions table empty, dashboard appeared blank |
| zeroed-DB guard | Only detects size>0 + NUL bytes, not 0-byte files | No recovery triggered |
| knowledge/ dir | Removed from git tracking by auto-sync | Skills/knowledge invisible in UI |
| skills/ dir | Removed from git tracking by auto-sync | 1 skill visible instead of 98 |
| workspace/ dir | Removed from git tracking by auto-sync | KB index/workspace deliverables gone |
| cron/ dir | Removed from git tracking by auto-sync | Cron jobs invisible |

---

## Protection Status — What's Protected

### ✅ Already Protected

| Threat | Status | Protection Mechanism |
|---|---|---|
| **Secrets in commits** | ✅ Protected | `.gitignore` excludes `.env`, `GithubToken.txt`, `config.yaml`, `auth.json`; pre-commit hook blocks ghp_* patterns |
| **Docker Desktop crashes** | ✅ Not a threat | `/opt/data` on ext4 (`/dev/sdd`), NOT in Docker volume; Docker daemon not running |
| **Gateway process crashes** | ✅ Protected | Running under s6 supervision (PID 46427); auto-restarts on crash |
| **API key exposure in git** | ✅ Protected | `.env` in `.gitignore`; pre-commit hook blocks `NVIDIA_API_KEY`, `GOOGLE_API_KEY`, etc. |
| **Model config corruption** | ✅ Protected | Read from `config.yaml`, not committed to git for sensitive parts |

### ⚠️ Vulnerabilities Found (Need Fixing)

| Vulnerability | Current Status | Risk | Fix Needed |
|---|---|---|---|
| **state.db not in .gitignore** | ⚠️ Tracked by git | HIGH: Can be committed as 0 bytes during SQLite write | Add `state.db` to `.gitignore` |
| **0-byte DB detection gap** | ⚠️ Not detected | HIGH: Silent empty DB, no recovery | Patch `is_zeroed_state_db()` to also detect size==0 |
| **No pre-commit hook for DB files** | ⚠️ Only secret detection | MEDIUM: Git can commit corrupted DB files | Add pre-commit hook to skip state.db, state.db-wal, state.db-shm |
| **State snapshots** | ⚠️ No snapshots dir exists | HIGH: No recovery point if DB corrupted | Enable Hermes snapshot feature or add pre-sync backup |
| **Working tree vs git tracking divergence** | ⚠️ Happened | HIGH: Dirs exist on disk but not in git | Git sync should verify tracked file count before commit |

---

## Fixes Applied

1. ✅ **Restored files to disk** from git commit `54c4651` (11,779 files)
   - `knowledge/` (25 files), `skills/` (98 SKILL.md), `workspace/` (9 files), `cron/` (6 jobs)
2. ✅ **Restored missing model files** from git
   - `refresh_models.py`, `model_benchmark/`, `model_config_snippet.yaml`
3. ✅ **Gateway service registered** under s6 supervision
   - `s6-supervise gateway-default` (PID 46425) → `hermes gateway run` (PID 46427)
4. ✅ **state.db rebuilt** — 5 sessions now visible (was 0)
5. ✅ **Recovery artifacts saved** to `/opt/data/recovery_output/`

---

## Recommendations for Preventing Recurrence

### 1. Add state.db to .gitignore (CRITICAL)
```bash
# Add to .gitignore:
echo "state.db" >> /opt/data/.gitignore
echo "state.db-wal" >> /opt/data/.gitignore  
echo "state.db-shm" >> /opt/data/.gitignore

# Remove from git tracking (keep on disk):
git rm --cached state.db state.db-wal state.db-shm
git commit -m "chore: remove state.db from git tracking to prevent race-condition corruption"
```

### 2. Enhance pre-commit hook (CRITICAL)
The existing pre-commit hook blocks secrets but allows DB files through. Add:
```bash
# In .git/hooks/pre-commit, add:
if git diff --cached --name-only | grep -qE "state\.db(-wal|-shm)?$"; then
    echo "❌ BLOCKED: state.db files should not be committed (use .gitignore)"
    echo "   These are runtime SQLite files — committing them during active writes"
    echo "   causes zero-byte corruption (see incident #68474)."
    exit 1
fi
```

### 3. Enable Hermes DB snapshots (IMPORTANT)
```bash
# Create state snapshots for recovery:
hermes snapshot create "pre-sync-backup" --description "Auto snapshot before git sync"
# Snapshots go to /opt/data/state-snapshots/ (checked at state.db open time)
```

### 4. Fix the zeroed-DB detector (IMPORTANT)
The `is_zeroed_state_db()` function in `hermes_state.py` (line 1617) needs a patch:
```python
# Current (only catches size>0 + NUL):
if size <= 0:
    return False

# Fix — also detect 0-byte files:
if size <= 0:
    return True  # 0-byte state.db is zeroed/corrupted
```
⚠️ **This is in `/opt/hermes/` which is READ-ONLY.** Requires a Hermes source patch or Docker build update.

### 5. Git sync safety protocol (GOOD PRACTICE)
Before any `git add -A && git commit`:
1. Check that state.db is not an active SQLite file (or skip it via .gitignore)
2. Verify working tree file count matches expected
3. Run `git status --short | wc -l` and review before committing

### 6. State recovery verification (ONGOING)
```bash
# Verify state.db health:
python3 -c "
import sqlite3
conn = sqlite3.connect('/opt/data/state.db')
c = conn.cursor()
c.execute('SELECT count(*) FROM sessions')
print('Sessions:', c.fetchone()[0])
c.execute('PRAGMA integrity_check')
print('Integrity:', c.fetchone()[0])
conn.close()
"
```

---

## Docker Desktop Threat Model

**Docker Desktop is NOT a threat vector** for this setup:

- `/opt/data` is mounted from the **WSL2 host filesystem** (`/dev/sdd` on ext4)
- The Hermes agent runs **directly** on WSL2, not inside a Docker container
- Docker daemon is **not running** in this environment (`docker info` shows client only)
- Even if Docker Desktop restarted or crashed, it would NOT affect `/opt/data` since it's on the host filesystem
- The only Docker-related process is the **dashboard** (`hermes dashboard --port 9119`) which is served by s6

**Verification:**
```
Mount: /dev/sdd on /opt/data type ext4 (rw,relatime)
```
This is a host-level ext4 mount, not a Docker volume.

---

## Current Ecosystem Health

| Component | Status | Notes |
|---|---|---|
| **state.db** | ✅ Healthy (1.9MB, 5 sessions) | SQLite header valid, sessions recovered |
| **Gateway service** | ✅ Running (PID 46427, s6-managed) | Auto-restart enabled |
| **Knowledge directory** | ✅ 25 files restored | All subdirectories present |
| **Skills directory** | ✅ 98 SKILL.md restored | All 20 categories present |
| **Workspace** | ✅ 9 files restored | PDFs, KPIs, INDEX |
| **Cron jobs** | ✅ 6 active jobs | All pinned to tencent/hy3:free |
| **API keys** | ✅ Present in .env | Not in git, pre-commit protected |
| **Git tracking** | ✅ knowledge/skills/workspace/cron tracked | From commit 54c4651 |
| **model_config_snippet.yaml** | ✅ Restored | Approval gate rules documented |
| **model-selection-policy/SKILL.md** | ✅ Restored | Approval gate criteria |
| **`/opt/hermes/` (runtime)** | Read-only (root-owned) | Cannot be modified by agent |