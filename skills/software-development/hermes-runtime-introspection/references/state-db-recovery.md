# State DB Recovery Reference

## When state.db is zeroed but sessions are lost

### Diagnosis
1. Check `/opt/data/state.db` size — valid SQLite header but 0 data pages = zeroed (not deleted).
2. Check `/opt/data/state.db-wal` on disk — may have recent writes.
3. If WAL is consumed/nothing on disk, check git: `git log --oneline --diff-filter=A -- state.db` finds the commit that captured the WAL.
4. Docker daemon NOT running = NOT the cause (confirmed via `docker ps -a` → "daemon not running").

### Recovery from git WAL
```bash
cd /opt/data
# Find the commit with the WAL
git log --oneline --diff-filter=A -- state.db-wal
# Extract WAL from git history
git show <commit>:state.db-wal > /tmp/recovery-wal
# WAL page size = int.from_bytes(wal_data[8:12], 'big') — usually 4096
# Frames start at offset 32, each has 24-byte frame header + page
```

### WAL parsing in Python (minimal)
```python
import struct, re

wal_data = open('/tmp/recovery-wal', 'rb').read()
page_size = int.from_bytes(wal_data[8:12], 'big')

# Walk WAL frames
offset = 32
while offset + 24 + page_size <= len(wal_data):
    page_num = int.from_bytes(wal_data[offset:offset+4], 'big')
    page_data = wal_data[offset+24:offset+24+page_size]
    # Search page for session IDs
    text = page_data.decode('utf-8', errors='replace')
    ids = re.findall(r'(20\d{6}_[0-9]{6}_[a-f0-9]{6})', text)
    # Session records are B-tree leaf cells (page type 0x0D)
    # Model config JSON is inline at payload start: {"model": "xxx", "provider": "yyy"}
    offset += 24 + page_size
```

### Known session pages from Aug 2026 recovery
- Page 4: WAL header (database page count = 8058, but only 468 WAL frames)
- Pages 53, 291, 344: session records for `20260805_`, `20260808_`, `20260810_`
- Page 7891: conversation messages (6 messages from main session)
- Pages 1441, 1466, 1471, 1489, 1513: system prompt + skills catalog + memory + user profile
- Page 1630: provider/model routing metadata
- B-tree pages corrupted (0 cells, garbage num_cells) — use raw text search instead of SQLite cell parsing

### Restoring deleted directories from git
If skills/, knowledge/, workspace/, cron/, docs/ are missing from working tree:
```bash
git checkout 54c4651 -- skills/ knowledge/ workspace/ cron/ docs/
```
Commit 54c4651 ("Initial sync after GitHub repo creation") has the full 11,779-file tree. Commit 450adc2 removed these from tracking.

### Key lesson: .gitignore and state.db
The `.gitignore` in commit 450adc2 added `state.db*` as excluded, but the WAL file was accidentally committed in `c2e637c`. The `.gitignore` change went uncommitted until 450adc2. Always check git for WAL recovery when state.db shows 0 rows.

### Variant: state.db valid but missing ALL TUI (non-cron) sessions
**Seen 2026-08-13:** User reports the chat panel showing only cron automation sessions — no
earlier human-initiated (TUI) chats. The live `state.db` is NOT zeroed (it's the full ~2MB
SQLite file with a valid header) but its `sessions` table contains **only `source='cron'` rows**
plus possibly one current `source='tui'` row for the *just-opened* session.

**Root cause:** the TUI sessions were lost *before* the post-incident snapshot was taken. The
snapshot at `state-snapshots/20260813-040721-post-aug12-recovery/` — named "post-recovery" —
already contains only cron sessions (5 of them). This means the recovery itself did NOT
restore TUI sessions; the TUI history was already gone prior to 04:07. WAL-from-git and
snapshot restore will NOT recover TUI chats in this variant because those sessions never made
it into either the snapshot or the committed WAL.

**Diagnostic (run BEFORE assuming zeroed-DB):**
```bash
python3 -c "
import sqlite3
conn=sqlite3.connect('/opt/data/state.db')
c=conn.cursor()
c.execute('SELECT source, COUNT(*) FROM sessions GROUP BY source')
print(dict(c.fetchall()))
# Expected: {'cron': N, 'tui': M} — if 'tui' is absent or only =1 (current session),
# the earlier human chats are lost from state.db.
conn.close()
"
```

**Recovery in this variant:** No automated DB recovery exists — the TUI session transcripts were
not written to any snapshot or git-committed WAL. Recovery depends on whether:
1. The current `state.db-wal` file on disk still has uncommitted TUI session pages (check
   `ls -la state.db-wal` — if it's 0 bytes or absent, nothing is pending).
2. The user has an external transcript/log of the lost chat (Hermes TUI does not auto-save
   raw transcripts to disk by default).

**Prevention:** set up `hermes backup --quick` on a **shorter** interval (e.g. every 4h via cron,
not just post-incident) so at least one recent snapshot preserves TUI sessions. See
`hermes-cron-model-pinning` Pitfall #15 for the state.db git-race root-cause prevention already in place
(pre-commit hook + `.gitignore`).