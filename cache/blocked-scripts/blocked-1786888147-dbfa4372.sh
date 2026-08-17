#!/bin/bash
# Auto-saved by Hermes: this command exceeded the inline command
# parser limit and was blocked from direct execution. Review it,
# then run it via: bash /opt/data/cache/blocked-scripts/blocked-1786888147-dbfa4372.sh
cd /opt/data/workspace/Samples/enhanced_doc_reader_v2 && python3 -c "import ast; ast.parse(open('doc_reader_onefile.py').read()); print('syntax OK')" && (pkill -f "doc_reader_onefile.py --api-server 8800" 2>/dev/null; sleep 0.5; python3 doc_reader_onefile.py --api-server 8800 >/tmp/dr_test.log 2>&1 &) ; sleep 2.5 ; curl -s http://localhost:8800/ -o /tmp/land.html ; echo "bytes: $(wc -c < /tmp/land.html)" ; echo "app-header: $(grep -c app-header /tmp/land.html)" ; echo "stat-card: $(grep -c stat-card /tmp/land.html)" ; echo "legend-pill: $(grep -c legend-pill /tmp/land.html)" ; echo "old category-group (should be 0): $(grep -c category-group /tmp/land.html)"
