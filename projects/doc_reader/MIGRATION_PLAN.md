=== MIGRATION PLAN: Phase 5 - Final Switchover ===
Date: 2026-08-16

## Current Status
- ✅ New self-contained structure: /opt/data/projects/doc_reader/ created
- ✅ All files copied and verified (identical checksums)
- ✅ Data synchronized (80 files in both locations)
- ✅ System health verified (server running, uploads working)
- ⏳ Switchover PENDING

## Switchover Steps (to be done in next phase)

### Step 1: Update cron jobs to point to new paths
- auto_git_push.sh: Update from /opt/data/doc_reader_onefile.py → /opt/data/projects/doc_reader/
- cleanup.sh: Update path references
- gateway_watchdog.sh: No changes needed

### Step 2: Update deploy_doc_reader.sh
- Update DATA_DIR references
- Update venv path detection

### Step 3: Test new location
- Run doc_reader_onefile.py from projects/doc_reader/
- Upload test document
- Verify settings API
- Check redaction maps created in correct location

### Step 4: Update running server
- Stop current server (PID from /opt/data/gateway.pid)
- Start from new location: python3 /opt/data/projects/doc_reader/doc_reader_onefile.py
- Verify server responds on port 8765

### Step 5: Decommission old files
- Remove: /opt/data/doc_reader_onefile.py (kept for rollback)
- Remove: /opt/data/deploy_doc_reader.sh (duplicate)
- Keep: /opt/data/data/ (as backup until stable)
- Remove: workspace/Samples/Files/ (all content now in projects/)

## Rollback Plan
If anything breaks:
1. Start server from original location: python3 /opt/data/doc_reader_onefile.py
2. Revert cron job paths to /opt/data/
3. Restore data/ directory if needed

## Notes
- The server is currently running from /opt/data/doc_reader_onefile.py
- All runtime data is in /opt/data/data/
- The new location has synced copies but the server isn't using them yet
- Cron jobs still point to old paths
