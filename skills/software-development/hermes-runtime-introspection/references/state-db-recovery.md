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