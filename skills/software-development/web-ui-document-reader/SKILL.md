---
name: web-ui-document-reader
description: Build local HTML+JS document redaction UI with settings.
version: 0.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web-ui, document-reader, redaction, pii, settings]
    related_skills: [local-document-reader-agent]
---

# Web UI Document Reader

## When to Use
Build self-contained Python HTTP server with browser-based PII redaction UI, per-client category settings, and Windows deployment.

## Pitfalls

### JS variable scoping (Critical)
Fetch response `const data` defined inside `try` is NOT accessible after `catch` block. All code using `data` must stay inside the try. Element references (`mappingBody`, etc.) must be declared before try to be available in catch.

**From session 2026-08-15:** The mapping fetch code at the BOTTOM of the click handler was outside the try block — when any upload error occurred, `data` was undefined, causing JS exception, breaking ALL buttons (Settings, Refresh, upload, drag-drop) for the entire page. FIX: Move ALL dependent code INSIDE the try block where `data` is in scope.

### Windows silent launch (Updated v2.2)
`start_silent.vbs` must find `pythonw.exe` in PATH or common install locations. Use relative paths with `Left(WScript.ScriptFullName, ...)`.

**Critical pattern** for Windows portables:
```vbs
strScriptDir = Left(WScript.ScriptFullName, Len(WScript.ScriptFullName) - Len(WScript.ScriptName))
pythonwPaths = Array("pythonw.exe", _
    "C:\Users\<USERNAME>\AppData\Local\Programs\Python\Python312\pythonw.exe", ...)
WshShell.Run """" & strPython & """ """ & strScriptPath & """", 0, False
```
The `0` flag = hidden window. `False` = return immediately.

### Live Restart Button (Updated v2.3)
A second button in the UI header enables code hot-swap: edit `doc_reader_onefile.py` on Windows, click the restart button, server auto-restarts.

**Root cause (from hermes-networking-lessons_1.pdf §3.2):** After file edits, the old process must terminate before the new one can bind the port — no process supervisor for portable apps. The restart button automates this via `restart_helper.vbs` (kills old pythonw.exe, relaunches start_silent.vbs).

Server-side (cross-platform — WSL2/Linux + Windows):
```python
elif path == "/restart":
    self._json(200, {"status": "restarting", "message": "Server is restarting..."})
    def _do_restart():
        time.sleep(0.4)
        try:
            if os.name == "nt":
                # Windows: VBS helper kills old pythonw.exe, relaunches start_silent.vbs
                helper = SCRIPT_DIR / "restart_helper.vbs"
                subprocess.Popen(["wscript.exe", str(helper)],
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                    close_fds=True)
            else:
                # Linux / macOS / WSL2: re-exec this script in place so the newly
                # edited doc_reader_onefile.py actually runs. execv lives in the `os`
                # module, NOT `sys` — sys.execv does not exist and raises AttributeError.
                os.execv(sys.executable, [sys.executable, str(SCRIPT_DIR / "doc_reader_onefile.py")])
        except Exception:
            pass
        os._exit(0)
    threading.Thread(target=_do_restart, daemon=True).start()
```

**Two-button distinction (critical):**
- **Refresh**: Calls `loadDocs()` — fetches `/documents`, reloads document list. Does NOT restart.
- **Restart**: Calls `resetServer()` — triggers kill+relaunch cycle. Use ONLY after editing `doc_reader_onefile.py`.

### File input not responding
Check browser console for JS errors. Usually caused by a scoping bug breaking the entire event loop. File input `accept` attribute must be set: `accept=".pdf,.docx,.xlsx,.pptx,.txt,.csv,.html,.htm,.md,.json"`.

ALSO check CSS: a `display: none` on form inputs (e.g. `.switch input { display: none }`) makes them non-interactive while invisible. Use `opacity: 0` with `z-index` instead to keep them clickable. This was the **silent root cause** of the "all buttons stopped working" regression on Windows portable in 2026-08-17 — fixing the toggle click area (removing label `for` attr) left checkboxes unreachable when `display: none` was used. See references/ui_interaction_fixes.md.

### "Updated but the screen looks the same" — verify the deploy, not just the edit (session 2026-08-16)
1. **Cosmetic-only change.** Swapping a few hex values in `:root` while leaving the layout/HTML structure identical produces a near-identical screen. If the ask is "professional + colorful + more usable", rebuild the layout (header/cards/groups/legend), not just the palette.
2. **Wrong deploy location.** The live server is NOT the file you edited. WSL2/container projects run from a *different* dir than where you dropped your work (e.g. live = `/opt/data/projects/doc_reader/`, your edit landed in `Samples/enhanced_X/`). Confirm the running process: `ps aux | grep -i <script>.py`. Copy the finished file into the **live** dir (preserve its `data/` folder + settings file). Never assume the edit sandbox == runtime dir.
3. **Stale process / browser cache.** A long-running server holds old code in memory; ♻️ Restart must actually re-exec (see cross-platform fix above). After redeploy, hard-refresh the browser (Ctrl+Shift+R) — old HTML is cached and masks the new UI even when the server is correct.

**Verify, don't claim:** after every UI/engine change, start the server (or `/restart`) and curl the live port: `grep -c "<new-class>" <fetched.html>` must change (old class → 0, new class → N). For engine changes, POST a sample doc and assert `category_counts` contains the new keys. A change that "looks done" but fails these greps is not done.

### Hard-coded category list silently drops new categories (session 2026-08-16)
`Engine.redact()` built its `priority_order` from a **hard-coded** list of the original ~10 categories. New categories added to `SECURITY_POLICY` + settings become toggleable in the UI but are **never applied** — the engine only iterates that fixed list. Symptom: `/settings` returns all groups, but an upload's `category_counts` is missing the new ones.
**Fix:** derive `priority_order` dynamically by iterating `SECURITY_POLICY` group order and keeping only categories present in `self.categories` (the engine's already-built set). PII/business stay first automatically. Append any custom categories not in the static policy.

### Don't ship verification scripts / extra files into the running deliverable
The user's running dir is `/opt/data/projects/doc_reader/`. When promoting an enhanced build, copy **only** `doc_reader_onefile.py` (and keep the dir's existing `restart_helper.vbs`, launchers, `data/`). Do NOT drop dev artifacts (`test_policy.py`, `verify_enhancement.py`, `_new_ui.html`, README variants) into the live dir — keep those in the side folder. Extra files in the running dir confuse the user about "which file is the key one."

### Portability checklist (from hermes-networking-lessons_1.pdf §2.1-§2.2)
- No hardcoded absolute paths in code logic
- All `mkdir()` calls use `parents=True, exist_ok=True`
- venv paths resolved dynamically using `sys.version_info.minor` (NOT hardcoded `3.13`)
- Cosmetic strings referencing internal paths must be generic

### ZIP packaging — always package from working source files (Updated v2.4)
Never create "improved" versions in a separate location and zip those. Zip **exactly** the files from the source directory the user confirmed working.

**In-place fix workflow (2026-08-16 lesson):** When user's "working" files are older and lack fixes:
1. Identify user's confirmed-working file set (e.g., `Files/` directory)
2. Apply fixes directly to those files
3. Sync fixed file to `/opt/data/doc_reader_onefile.py` (verify with md5sum)
4. Zip exactly those fixed files — no substitutions
5. Verify zip contents match (md5sum comparison)

- 5 files: `doc_reader_onefile.py`, `run.bat`, `run.sh`, `start_silent.vbs`, `README.txt`
- Live Restart adds 6th file: `restart_helper.vbs`
- Run portability self-check on final ZIP contents
- Respect user's ZIP naming conventions (update .gitignore exceptions accordingly)
- Verify ZIP: list contents, check sizes, confirm features present in ZIP's doc_reader_onefile.py

### Directory cleanup (from session 2026-08-16)
After delivering the ZIP, clean up redundant artifacts:
- Remove old monolithic modules: `doc_reader_agent.py`, `doc_reader_desktop.py`, `redaction_engine.py`, `safe_format.py`
- Remove test screenshots: `test*.png`, `cmd.png`, `oaui_*.png`
- Remove superseded ZIP archives
- Remove orphaned runtime data (duplicate dirs at `/opt/data/` root)
- Remove debug output directories (`RESULT/`)
- Update `cleanup.sh` to reference correct obsolete file names

### Self-Contained Project Structure (Updated 2026-08-16)
The project has been migrated to a self-contained structure:
```
/opt/data/projects/doc_reader/
├── doc_reader_onefile.py       ← Main app (ALL logic in one file)
├── deploy_doc_reader.sh        ← Deployment script
├── data_security_governance_policy.md ← Security reference
├── auto_git_push.sh            ← Daily sync (references new paths)
├── cleanup.sh                  ← Monthly cleanup (updated paths)
├── gateway_watchdog.sh         ← Gateway health check
├── MIGRATION_PLAN.md           ← Migration documentation
├── data/                       ← Runtime data (auto-created)
└── workspace/                  ← Windows distribution files
```

**Key path changes:**
- Main app: `/opt/data/projects/doc_reader/doc_reader_onefile.py` (was `/opt/data/doc_reader_onefile.py`)
- Runtime data: `/opt/data/projects/doc_reader/data/` (was `/opt/data/data/`)
- Scripts: `/opt/data/projects/doc_reader/{cleanup.sh,auto_git_push.sh}` (was in `/opt/data/scripts/`)
- Portable ZIP: `/opt/data/workspace/Samples/poc_reader_windows_portable.zip` (updated with self-contained logic)
- See `references/self-contained-project-migration.md` for safe migration pattern

### Browser sandbox blocks `file://` rendering (session 2026-08-16)
Chromium under the browser-use harness rejects `file://` URLs with
`chrome-error://chromewebdata/`. When visual rendering is unavailable, fall
back to **programmatic validation** rather than asserting completion. Run:
```
bash references/validate-self-contained-html.sh /path/to/file.html
```
This checks HTML tag balance, SVG XML well-formedness, arrow-endpoint anchoring
(within 4px of a `<rect>` edge), and color contrast (≥3:1 blended vs `#020617`).
Lesson: the Cocoon architecture-diagram palette's `rgba(..., 0.3-0.4)` fills fail
contrast on slate-950 — use `fill-opacity="0.75"` on hex base colors instead, plus
a 2px dark stroke for crisp outlines.

## References
- `references/hermes-networking-lessons-summary.md` — Postmortem lessons from networking/deploy incidents
- `references/self-contained-project-migration.md` — Safe pattern for restructuring apps into self-contained project directories
- `references/redeploy-and-verify.md` — Find live server, promote build, restart, and curl-based UI/engine verification recipe
- `references/validate-self-contained-html.sh` — One-shot validation gate for self-contained HTML/SVG deliverables

## Template
Server pattern: single Python file with embedded HTML.

**API endpoints:**
- `GET /health` — Health check
- `GET /` — HTML UI
- `POST /upload` — Upload & process
- `POST /settings` — Save settings
- `GET /settings` — Get settings + policy
- `GET /settings/categories` — List categories
- `GET /documents` — List documents
- `GET /documents/<id>/safe` — Redacted output (NO original values)
- `GET /documents/<id>/map` — Reversible mapping (separate)
- `POST /restart` — Restart server (Windows only)

**Settings:** Stored in `data/redaction_settings.json`

**ZIP must contain:** `doc_reader_onefile.py`, `run.bat`, `run.sh`, `start_silent.vbs`, `README.txt`, + `restart_helper.vbs` (if Live Restart included)