# Hermes Networking Lessons — Summary for OAKAI Document Reader

## Source: hermes-networking-lessons_1.pdf (session 2026-08-16)

### Incident 1 — Dashboard (port 9119) Went Unreachable
Key diagnostic sequence (apply in order):
1. Is the container running? `docker ps -a`
2. Is the port published? `docker inspect <c> --format '{{.NetworkSettings.Ports}}'`
3. Does it respond on loopback from inside container? (Python socket test against 127.0.0.1:PORT)
4. Compare internal vs external curl
5. Only then consider WSL2/Windows networking

**Fail-closed pattern**: TCP connects but resets on every request = missing auth provider on non-loopback bind (HERMES_DASHBOARD_BASIC_AUTH_USERNAME + _PASSWORD + _SECRET).

### Incident 2 — Portable Script Failed on Windows
Hardcoded `/opt/data/.venv-docreader/...` paths caused `FileNotFoundError` on Windows.

**Rule**: Before shipping any ZIP:
- grep for `/opt/|/root/|/home/|/mnt/` in code — any hits = investigate
- All mkdir() must use parents=True, exist_ok=True
- Trace code as if running on bare target machine with empty destination folder

### Incident 3 — Stale State Crashed App
`JSONDecodeError: line 1 column 1 (char 0)` = file empty/absent, not malformed JSON.
- Read path must check file exists and is non-empty before json.loads()
- Only record item as complete AFTER output write succeeds

### Incident 3.2 — "It runs" ≠ "it stays running"
- run.bat launches in foreground → closing terminal kills process
- Solution: pythonw.exe + start_silent.vbs + Startup folder (no admin rights needed)
- Restart button (v2.3) provides in-app server restart for code changes

## Live Restart Pattern (v2.3)
### Server endpoint:
```python
elif path == "/restart":
    self._json(200, {"status": "restarting"})
    def _do_restart():
        time.sleep(0.4)
        helper = SCRIPT_DIR / "restart_helper.vbs"
        subprocess.Popen(["wscript.exe", str(helper)],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            close_fds=True)
        os._exit(0)
    threading.Thread(target=_do_restart, daemon=True).start()
```

### restart_helper.vbs (WMI-based process kill + relaunch):
```vbs
Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")
Set colProcesses = objWMIService.ExecQuery( _
    "Select * from Win32_Process Where (Name = 'python.exe' or Name = 'pythonw.exe')")
For Each objProcess in colProcesses
    If InStr(objProcess.CommandLine, "doc_reader_onefile.py") > 0 Then
        objProcess.Terminate()
    End If
Next
WScript.Sleep 1500
WshShell.Run """" & scriptFolder & "\start_silent.vbs""", 0, False
```

### Frontend polling (browser):
```javascript
// After POST /restart, poll /health every 500ms, reload when OK
// Max 20 attempts (10 seconds)
```

### Two-button distinction:
- **Refresh** = `loadDocs()` → fetches `/documents` only (no restart)
- **Restart** = `resetServer()` → kills + relaunches server process (use after code changes)