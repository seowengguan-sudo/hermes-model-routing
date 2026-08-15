#!/bin/bash
# OAKAI Document Reader Clean Up Script
# Removes unnecessary files/caches safely without breaking functionality
# Safe to run: only removes old/duplicate/temp/backup files

cd /opt/data
echo "=== OAKAI System Cleanup ==="
echo "Starting cleanup: $(date)"
echo ""

# ─── 1. Remove old venv copies (not in use) ────────────────────────────────
OLD_VENV="/opt/data/workspace/Samples/.venv-docreader"
if [ -d "$OLD_VENV" ]; then
    SIZE=$(du -sh "$OLD_VENV" | cut -f1)
    echo "Removing old venv copy: $OLD_VENV ($SIZE)"
    rm -rf "$OLD_VENV"
    echo "  ✅ Done (freed $SIZE)"
else
    echo "Skipping: old venv not found"
fi
echo ""

# ─── 2. Remove old backup ZIPs ──────────────────────────────────────────────
for zip in /opt/data/workspace/Samples/doc_reader_windows_portable_backup*.zip; do
    if [ -f "$zip" ]; then
        SIZE=$(du -h "$zip" | cut -f1)
        echo "Removing backup ZIP: $(basename $zip) ($SIZE)"
        rm -f "$zip"
        echo "  ✅ Done (freed $SIZE)"
    fi
done
echo ""

# ─── 3. Remove old XTR screenshot images ────────────────────────────────────
echo "Removing old XTR screenshot images:"
for img in /opt/data/workspace/Samples/XTR*.jpg /opt/data/workspace/Samples/XTR*.png; do
    if [ -f "$img" ]; then
        SIZE=$(du -h "$img" | cut -f1)
        echo "  Removing: $(basename $img) ($SIZE)"
        rm -f "$img"
    fi
done
echo "  ✅ Done"
echo ""

# ─── 4. Remove old screenshot variants ──────────────────────────────────────
echo "Removing old screenshot variants:"
for img in /opt/data/workspace/Samples/test18_*.jpg /opt/data/workspace/Samples/test18_*.png /opt/data/workspace/Samples/oaui_*.png /opt/data/workspace/Samples/oaui_*.jpg; do
    if [ -f "$img" ]; then
        SIZE=$(du -h "$img" | cut -f1)
        echo "  Removing: $(basename $img) ($SIZE)"
        rm -f "$img"
    fi
done
echo "  ✅ Done"
echo ""

# ─── 5. Remove backup .bak files ────────────────────────────────────────────
echo "Removing backup files:"
for bak in /opt/data/config.yaml.bak* /opt/data/.env.bak* /opt/data/memories/USER.md.bak.* /opt/data/cron/jobs.json.bak*; do
    if [ -f "$bak" ]; then
        SIZE=$(du -h "$bak" | cut -f1)
        echo "  Removing: $(basename $bak) ($SIZE)"
        rm -f "$bak"
    fi
done
echo "  ✅ Done"
echo ""

# ─── 6. Remove old doc_reader files no longer used ──────────────────────────
echo "Removing old/unused doc_reader files:"
for old_file in /opt/data/doc_reader_wsl2.py /opt/data/doc_reader_agent_runner.py; do
    if [ -f "$old_file" ]; then
        SIZE=$(du -h "$old_file" | cut -f1)
        echo "  Removing: $(basename $old_file) ($SIZE) - superseded by doc_reader_onefile.py"
        rm -f "$old_file"
    fi
done
echo "  ✅ Done"
echo ""

# ─── 7. Clean __pycache__ directories (non-venv) ────────────────────────────
echo "Removing __pycache__ directories (non-venv):"
find /opt/data -name "__pycache__" -type d -not -path "*/.venv*" -not -path "*/.git/*" 2>/dev/null | while read d; do
    SIZE=$(du -sh "$d" | cut -f1)
    rm -rf "$d"
    echo "  Removed: $d ($SIZE)"
done
echo "  ✅ Done"
echo ""

# ─── 8. Clean terminal output cache (keep last 10) ───────────────────────────
echo "Cleaning terminal output cache:"
CACHE_DIR="/opt/data/cache/terminal-output"
if [ -d "$CACHE_DIR" ]; then
    COUNT=$(ls "$CACHE_DIR"/*.log 2>/dev/null | wc -l)
    SIZE=$(du -sh "$CACHE_DIR" | cut -f1)
    if [ "$COUNT" -gt 10 ]; then
        ls -t "$CACHE_DIR"/*.log 2>/dev/null | tail -n +11 | xargs rm -f
        echo "  Cleaned: removed $((COUNT - 10)) old log files (kept latest 10, freed from $SIZE)"
    else
        echo "  Skipped: only $COUNT log files (under threshold)"
    fi
fi
echo ""

# ─── 9. Clean old cron output files (keep last 30) ──────────────────────────
echo "Cleaning cron output:"
CRON_OUT="/opt/data/cron/output"
if [ -d "$CRON_OUT" ]; then
    COUNT=$(find "$CRON_OUT" -name "*.md" 2>/dev/null | wc -l)
    if [ "$COUNT" -gt 30 ]; then
        find "$CRON_OUT" -name "*.md" -mtime +7 2>/dev/null | head -$((COUNT - 30)) | xargs rm -f 2>/dev/null
        echo "  Cleaned: old cron outputs (had $COUNT files)"
    else
        echo "  Skipped: $COUNT cron output files (under threshold)"
    fi
fi
echo ""

# ─── 10. Clean old state snapshots (keep latest 3) ──────────────────────────
echo "Cleaning state snapshots:"
SNAP_DIR="/opt/data/state-snapshots"
if [ -d "$SNAP_DIR" ]; then
    COUNT=$(ls -d "$SNAP_DIR"/*/ 2>/dev/null | wc -l)
    if [ "$COUNT" -gt 3 ]; then
        ls -td "$SNAP_DIR"/*/ 2>/dev/null | tail -n +4 | xargs rm -rf 2>/dev/null
        echo "  Cleaned: removed old snapshots (had $COUNT, kept 3)"
    else
        echo "  Skipped: only $COUNT snapshots (under threshold)"
    fi
fi
echo ""

# ─── 11. Clean package manager caches (UV + pip) ─────────────────────────────────
# These caches speed up package reinstallation but are NOT needed for running
# already-installed packages. Safe to clean.
echo "Cleaning package manager caches:"
for cache_dir in /opt/data/home/.cache/uv/archive-v0 /opt/data/home/.cache/pip/http-v2; do
    if [ -d "$cache_dir" ]; then
        SIZE=$(du -sh "$cache_dir" | cut -f1)
        rm -rf "$cache_dir"/*
        echo "  Cleaned: $cache_dir (freed $SIZE)"
    fi
done
echo ""

# ─── 12. Clean architecture/hermes-venv if not used ────────────────────────────
if [ -d "$ARCH_VENV" ]; then
    # Check if anything references it
    REFS=$(grep -r "architecture/hermes-venv" /opt/data/*.py /opt/data/*.sh /opt/data/scripts/*.sh 2>/dev/null | wc -l)
    if [ "$REFS" -eq 0 ]; then
        SIZE=$(du -sh "$ARCH_VENV" | cut -f1)
        echo "Removing unused architecture venv: $ARCH_VENV ($SIZE)"
        rm -rf "$ARCH_VENV"
        echo "  ✅ Done (freed $SIZE)"
    else
        echo "Skipping architecture venv: referenced by $REFS scripts"
    fi
fi
echo ""

# ─── Summary ─────────────────────────────────────────────────────────────────
echo "=== Cleanup Summary ==="
echo "Completed at: $(date)"
echo ""
echo "Disk usage after cleanup:"
du -sh /opt/data 2>/dev/null
echo ""
echo "Top directories:"
du -sh /opt/data/* 2>/dev/null | sort -rh | head -10
echo ""
echo "✅ Cleanup complete!"
