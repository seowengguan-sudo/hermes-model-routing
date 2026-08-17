#!/bin/bash
# Verification script for HTTP servers in containers
# Run after making changes to doc_reader_tk.py or similar server code
# Usage: bash /opt/data/skills/mlops/local-http-server-in-container/scripts/verify_container_http_server.sh

PASS=0; FAIL=0
check() { if [ "$1" = "0" ]; then echo "  ✓ $2"; PASS=$((PASS+1)); else echo "  ✗ $2"; FAIL=$((FAIL+1)); fi; }

PY="${PYTHON:-python3}"
SCRIPT_PATH="${1:-/opt/data/doc_reader_tk.py}"
PORT="${2:-8765}"

echo "=== Container HTTP Server Verification ==="
echo "Script: $SCRIPT_PATH"
echo "Port:   $PORT"
echo ""

# 1: Compiles
$PY -m py_compile "$SCRIPT_PATH" 2>&1
check $? "Script compiles"

# 2: Binds to 0.0.0.0
grep -q 'HTTPServer(("0.0.0.0"' "$SCRIPT_PATH" 2>/dev/null
check $? "Binds to 0.0.0.0 (not 127.0.0.1)"

# 3: Not bound to localhost only
grep -q 'HTTPServer(("127.0.0.1"' "$SCRIPT_PATH" 2>/dev/null && { echo "  ✗ Still binds to 127.0.0.1"; FAIL=$((FAIL+1)); } || check 0 "No localhost-only binding"

# 4: Server process running
pgrep -f "${SCRIPT_PATH}.*api-server" > /dev/null 2>&1
check $? "Server is running"

# 5: Health endpoint
curl -s --connect-timeout 2 "http://127.0.0.1:${PORT}/health" | $PY -c "import json,sys; d=json.load(sys.stdin); assert d['status']=='ok'" 2>/dev/null
check $? "GET /health responds with status ok"

# 6: HTML UI at root
curl -s --connect-timeout 2 "http://127.0.0.1:${PORT}/" | grep -q "DOCTYPE html\|<!DOCTYPE" 2>/dev/null
check $? "GET / serves HTML UI (not raw JSON)"

# 7: Document list endpoint
curl -s --connect-timeout 2 "http://127.0.0.1:${PORT}/documents" | $PY -c "import json,sys; d=json.load(sys.stdin); assert 'documents' in d" 2>/dev/null
check $? "GET /documents returns JSON list"

# 8: Container IP accessible
CIP=$(hostname -I 2>/dev/null | awk '{print $1}')
[ -n "$CIP" ] && curl -s --connect-timeout 2 "http://${CIP}:${PORT}/health" | $PY -c "import json,sys; assert json.load(sys.stdin)['status']=='ok'" 2>/dev/null
check $? "Accessible via container IP ($CIP)"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ $FAIL -eq 0 ] && echo "✅ All checks passed" || echo "❌ Some checks failed"
exit $FAIL