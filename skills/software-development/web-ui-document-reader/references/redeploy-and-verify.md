# Redeploy & Verify Recipe — local doc-reader onefile server

## Find the live server
```bash
ps aux | grep -i doc_reader_onefile.py | grep -v grep
# live process shows the REAL runtime dir, e.g. /opt/data/projects/doc_reader/
```

## Promote an enhanced build to the live dir
```bash
# Edit artifacts stay in the side folder; copy ONLY the app into the live dir
cp /path/to/enhanced/doc_reader_onefile.py /opt/data/projects/doc_reader/doc_reader_onefile.py
python3 -c "import ast; ast.parse(open('/opt/data/projects/doc_reader/doc_reader_onefile.py').read()); print('syntax OK')"
```

## Restart the live server cleanly
If a working process already holds the port:
```bash
curl -s -X POST http://localhost:8765/restart   # works on WSL2/Linux via os.execv now
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/health   # expect 200
```
If restart leaves the port dead, relaunch in the live dir:
```bash
cd /opt/data/projects/doc_reader && (python3 doc_reader_onefile.py >/tmp/live.log 2>&1 &)
```

## Verify the UI changed (not just claiming it)
```bash
curl -s -o /tmp/live.html http://localhost:8765/
grep -c "stat-card"      /tmp/live.html   # new class  -> N
grep -c "category-group" /tmp/live.html   # old class  -> 0
curl -s http://localhost:8765/settings | python3 -c "import sys,json;d=json.load(sys.stdin);print(sorted(d['settings']['categories'].keys()))"
```

## Verify the engine applied new categories
```bash
printf 'SSN 123-45-6789. Passport A1234567. IBAN DE89370400440532013000.\n' > /tmp/s.txt
curl -s -F "file=@/tmp/s.txt" http://localhost:8765/upload | python3 -c "import sys,json;d=json.load(sys.stdin);print('total',d['total_redactions']);print(d['category_counts'])"
# New keys (PASSPORT, IBAN, ...) must appear — if missing, redact() priority_order bug.
```

## Browser cache gotcha
After redeploy, the user must hard-refresh (Ctrl+Shift+R). Old HTML is cached and masks the new UI even when the server is correct.

## Don't pollute the live dir
Keep dev artifacts (test_*.py, verify_*.py, _new_ui.html, README variants) in the side folder. The live dir should hold only doc_reader_onefile.py + launchers + restart_helper.vbs + data/.
