#!/bin/bash
# Auto-saved by Hermes: this command exceeded the inline command
# parser limit and was blocked from direct execution. Review it,
# then run it via: bash /opt/data/cache/blocked-scripts/blocked-1786887969-a5ac4242.sh
cd /opt/data/workspace/Samples/enhanced_doc_reader_v2 && curl -s http://localhost:8800/ -o /tmp/land.html ; echo "bytes:"; wc -c < /tmp/land.html; echo "--- new-UI class counts ---"; for c in app-header stat-card stat-value legend-pill settings-toolbar group-head act-btn; do printf "%-16s %s\n" "$c" "$(grep -o "$c" /tmp/land.html | wc -l)"; done; echo "--- old-UI leftover check (category-group was old) ---"; grep -c "category-group" /tmp/land.html
