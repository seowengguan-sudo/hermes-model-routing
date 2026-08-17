#!/bin/bash
# Auto-saved by Hermes: this command exceeded the inline command
# parser limit and was blocked from direct execution. Review it,
# then run it via: bash /opt/data/cache/blocked-scripts/blocked-1786899252-949fdddb.sh
cd /opt/data/projects/doc_reader && \
echo "=== Does served UI contain the toggle I added? (count in served vs file) ===" && \
echo "served: $(curl -s http://127.0.0.1:8765/ | grep -c 'style-toggle-card')" && \
echo "file:   $(grep -c 'style-toggle-card' doc_reader_onefile.py)" && \
echo "" && echo "=== Settings overlay open/close: is settingsOverlay element present? ===" && \
curl -s http://127.0.0.1:8765/ | grep -o 'id="settingsOverlay"' | head -1 && \
echo "" && echo "=== Does toggling smart via /settings actually persist & reflect? ===" && \
curl -s -X POST http://127.0.0.1:8765/settings -H "Content-Type: application/json" -d '{"redaction_style":"smart"}' >/dev/null && \
curl -s http://127.0.0.1:8765/settings | python3 -c "import sys,json; print('redaction_style =', json.load(sys.stdin)['settings']['redaction_style'])"
