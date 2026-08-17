# Windows Deployment & Silent Launch Patterns

## Problem
Users need to run the OAKAI Document Reader on Windows without a console window, and without the terminal closing killing the process.

## Solutions

### 1. start_silent.vbs — Silent Background Launcher with Restart Support

Critical for Windows users who want the server to stay running after closing the terminal or rebooting.

**Pattern:**
```vbs
Set WshShell = CreateObject("WScript.Shell")
strScriptDir = Left(WScript.ScriptFullName, Len(WScript.ScriptFullName) - Len(WScript.ScriptName))
strScriptPath = strScriptDir & "doc_reader_onefile.py"

' Try pythonw.exe (windowless) first, fall back to python.exe in PATH
pythonwPaths = Array( _
    "pythonw.exe", _
    "C:\Users\" & strUser & "\AppData\Local\Programs\Python\Python312\pythonw.exe", _
    "C:\Users\" & strUser & "\AppData\Local\Programs\Python\Python311\pythonw.exe", _
    "C:\Users\" & strUser & "\AppData\Local\Programs\Python\Python310\pythonw.exe" _
)
```

**Key learnings:**
- `pythonw.exe` = Python without console window. Use `WshShell.Run strCmd, 0, False`
- `0` = hidden window flag; `False` = don't wait for process
- Use relative paths: `Left(WScript.ScriptFullName, ...)` to get script directory
- Check PATH first, then common install locations
- Windows Startup folder (`shell:startup`) for auto-launch (no admin needed)

### 2. run.bat — Console Launcher (for debugging)
```bat
@echo off
cd /d "%~dp0"
python.exe doc_reader_onefile.py
pause
```

### 3. run.sh — Linux/macOS Launcher
```bash
#!/bin/bash
cd "$(dirname "$0")"
python3 doc_reader_onefile.py
```

### 4. Restart Feature (Reset Button) — Safe Server Self-Restart

When users need to update the running server after replacing `doc_reader_onefile.py`:

**Problem:** You cannot replace `doc_reader_onefile.py` while the process has it open (file lock on Windows). Closing the PowerShell and restarting is error-prone.

**Solution (implemented in `doc_reader_portable_with_reset.zip`):**
- Add a dedicated 🔄 Restart button in the UI header (separate from Refresh)
- When clicked, it calls `POST /restart` endpoint
- Server sends JSON response, then spawns `restart_helper.vbs` as a detached process
- `restart_helper.vbs` uses WMI to find and kill `pythonw.exe` processes with `doc_reader_onefile.py` in the command line
- Waits 1.5s for port release
- Relaunches server via `start_silent.vbs`
- Browser auto-reloads when health check passes

**Critical safety: The /restart endpoint must:**
1. Send the HTTP response BEFORE exiting (let client handle connection drop gracefully)
2. Spawn the helper as a **detached process** (`wscript.exe`, not `python.exe`)
3. The helper must NOT inherit the server's process tree
4. Use `os._exit(0)` (not `sys.exit()`) to ensure immediate process termination

**restart_helper.vbs pattern:**
```vbs
' Uses WMI to find and terminate the old process, then relaunches
For Each objProcess in colProcesses
    If InStr(objProcess.CommandLine, "doc_reader_onefile.py") > 0 Then
        objProcess.Terminate()
    End If
Next
WScript.Sleep 1500  ' Give OS time to release the port
WshShell.Run "wscript.exe \"start_silent.vbs\"", 0, False
```

**Never implement process restart from a browser button that:**
- Runs shell commands directly (command injection risk)
- Doesn't handle the file-lock issue on Windows
- Uses `subprocess.run()` (blocks the HTTP thread — use `Popen` + `os._exit()`)

## ZIP Packaging Checklist

The portable ZIP must contain exactly 5 files:

| File | Purpose |
|------|---------|
| doc_reader_onefile.py | Main engine (1500+ lines, self-contained) |
| run.bat | Windows console launcher |
| run.sh | Linux/macOS launcher |
| start_silent.vbs | Silent Windows launcher (pythonw.exe) |
| README.txt | Documentation |

**Pre-shipping verification (per networking-lessons PDF §2.2):**
```bash
# Check for hardcoded absolute paths
grep -n "site-packages" doc_reader_onefile.py | grep -v "VENV_SITE_PACKAGES"

# Check mkdir calls have parents=True
grep -n "mkdir(" doc_reader_onefile.py | grep -v "parents=True"
```

### Portability Checklist for Windows Deployment (from hermes-networking-lessons_1.pdf)

**Critical: A portable ZIP must work when dropped into any empty folder on a fresh Windows machine.**

1. **No hardcoded absolute paths** (`/opt/`, `/home/`, `/usr/`) in executable code
   - Use `Path(__file__).parent` for all file-relative paths
   - Venv site-packages must be resolved dynamically (check relative paths, fall back gracefully)
   - Never embed `SCRIPT_DIR == Path("/opt/data")` checks in shipped code

2. **All `mkdir()` calls must use `parents=True, exist_ok=True`**
   - Without `parents=True`, nested dir creation fails if parent doesn't exist
   - This is the #1 cause of silent startup failures on fresh Windows

3. **Venv path resolution pattern:**
   ```python
   _VENV_CANDIDATES = [
       SCRIPT_DIR.parent / ".venv-docreader" / "lib" / f"python3.{sys.version_info.minor}" / "site-packages",
       SCRIPT_DIR / ".venv-docreader" / "lib" / f"python3.{sys.version_info.minor}" / "site-packages",
   ]
   VENV_SITE_PACKAGES = str(next((p for p in _VENV_CANDIDATES if p.exists()), ""))
   ```

4. **Optional dependency import pattern:**
   ```python
   if VENV_SITE_PACKAGES:
       sys.path.insert(0, VENV_SITE_PACKAGES)
       from pypdf import PdfReader
   else:
       # Fallback to native ZIP/XML parsing — works without any venv
       pass
   ```

5. **UI text must not leak internal paths** — even cosmetic strings like "stored at /opt/data/..." confuse users when running on Windows

## Two ZIP Variants

| ZIP | Files | Has Restart? | Use Case |
|-----|-------|--------------|----------|
| `doc_reader_windows_portable.zip` | 5 files, flat | No | Standard deployment |
| `doc_reader_portable_with_reset.zip` | 6 files + folder | Yes | When users need live-update restart button |

The with-reset variant includes `restart_helper.vbs` and a modified `doc_reader_onefile.py` with the `/restart` endpoint and restart button UI. The standard ZIP is for users who don't need the restart feature.