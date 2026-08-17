#!/bin/bash
# Auto-saved by Hermes: this command exceeded the inline command
# parser limit and was blocked from direct execution. Review it,
# then run it via: bash /opt/data/cache/blocked-scripts/blocked-1786846580-c1b4ee37.sh
# Verify the latest doc_reader_onefile.py is syntactically valid and has the settings feature
python3 -c "
import ast
with open('/opt/data/doc_reader_onefile.py', 'r') as f:
    source = f.read()
try:
    ast.parse(source)
    print('✅ Syntax OK')
except SyntaxError as e:
    print(f'❌ Syntax error: {e}')
    exit(1)
"

echo ""
echo "=== Feature Check ==="
echo "Settings page: $(grep -c 'openSettings\|settings-modal\|saveSettings' /opt/data/doc_reader_onefile.py) references"
echo "Settings API: $(grep -c '/settings' /opt/data/doc_reader_onefile.py) endpoints"
echo "Lines: $(wc -l < /opt/data/doc_reader_onefile.py)"
echo ""
echo "=== Server Health ==="
curl -s http://localhost:8765/health
