# WSL2/Docker Container HTTP Server — Session Notes

## Session Context
- Date: 2026-08-14
- Environment: Docker container (Hermes agent) inside WSL2/Docker Desktop
- Image: `nikolaik/python-nodejs:python3.11-nodejs20`
- Container IP: `172.17.0.2` (Docker bridge network)
- WSL2 gateway: `192.168.65.7` (from `/etc/resolv.conf`)

## Timeline of Issues

### Issue 1: Server not accessible from browser
**Symptom:** `http://localhost:8765` in Windows browser shows "Cannot connect"
**Root cause:** Server was binding to `127.0.0.1` (loopback only), inside Docker container
**Fix:** Changed `HTTPServer(("127.0.0.1", port), ...)` to `HTTPServer(("0.0.0.0", port), ...)`

### Issue 2: Container IP also not accessible from Windows
**Symptom:** `http://172.17.0.2:8765` in Windows browser fails
**Root cause:** Docker bridge network isolation — no port publishing (`-p`)
**Fix:** Use browser tool (`browser_navigate`) which runs inside the container, OR SSH tunnel from Windows

### Issue 3: Background process termination
**Symptom:** Server dies after terminal command timeout
**Root cause:** Background process tied to terminal session lifecycle
**Fix:** Use `terminal(background=true, notify_on_complete=true)` with explicit PID tracking

### Issue 4: `network_mode: host` vs actual networking
**Symptom:** docker-compose.yml specifies `network_mode: host` but container runs in bridge mode
**Root cause:** Docker compose file not used for container launch; actual runtime uses bridge networking
**Fix:** Don't rely on docker-compose.yml for networking assumptions; always check `/proc/net/route` and `hostname -I`. When `network_mode: host` is NOT actually in effect, you MUST publish ports with `-p` or use SSH tunneling.

## Key Learnings

1. **'localhost' is context-dependent**
   - Inside container: `localhost` = container's loopback
   - Windows host: `localhost` = Windows loopback (different network namespace)
   - Browser tool: runs inside container, so `localhost` = container's loopback ✅

2. **`/proc/net/tcp` for binding verification**
   ```
   00000000:239F = 0.0.0.0:8765 (all interfaces) ✅
   0100007F:239F = 127.0.0.1:8765 (localhost only) ❌
   ```

3. **Browser tools run INSIDE the container**
   This is the most reliable way to verify UI — the Playwright browser shares the network namespace

4. **Docker networking in this environment**
   - `network_mode: host` in docker-compose.yml but actual runtime uses bridge (172.17.0.x)
   - Container cannot reach WSL2 gateway (192.168.65.7) directly
   - No Docker CLI or port publishing available inside container

5. **SSH tunnel solution is NOT applicable in this environment**
   - The skill's recommended SSH tunnel approach (`ssh -L 8765:localhost:8765`) requires sshd on the server side
   - This container has **no sshd installed** (`sshd not found`, `service ssh not available`)
   - No `apt-get install` permissions (not root, dpkg lock denied)
   - **Alternative**: Run server from WSL2 directly (bypasses Docker networking entirely)
   - Or use the browser tool (runs inside container, can access `localhost:PORT`)

## Browser Access from Windows — What Actually Works

In the Daytona/Hermes sandbox environment where this Docker container runs:

1. **Windows browser CANNOT directly reach container ports**
   - `localhost:8765` → Windows loopback (different namespace)
   - `172.17.0.2:8765` → Container IP (Docker bridge isolation)
   - `192.168.65.7:8765` → WSL2 gateway (unreachable from container)

2. **Browser tool ALWAYS works for verification**
   - Use `browser_navigate("http://localhost:8765/")` to verify UI
   - Runs inside container, shares network namespace
   - Confirmed working in session: HTML UI, drag-drop, file processing all functional

3. **User access — the ONLY working approach**
   - Stop trying SSH tunnels (no sshd available)
   - Don't try to reach container IP from Windows browser (bridge isolation)
   - **Run server from WSL2 directly** (bypasses Docker networking):
     ```bash
     # In WSL2 terminal (NOT Docker container):
     /opt/data/.venv-docreader/bin/python3 /opt/data/doc_reader_tk.py --api-server 8765
     # WSL2 auto-forwards localhost to Windows
     # Then open: http://localhost:8765 in Windows browser
     ```

4. **Wrong commands to avoid**
   - `python -m http.server 8765` → starts generic Python HTTP, not the doc reader
   - `ssh -L 8765:localhost:8765` → fails (no sshd in container)
   - `http://localhost:8765` from Windows PowerShell → connection refused

## User Experience Notes
- When user shares JPG/PNG screenshots of PowerShell errors, these are NOT accessible from inside the Docker container
- The container has zero visibility into the user's Windows filesystem
- User confusion ("why can't I open the UI?") stems from misunderstanding the network boundary
- Clear instructions: "run from WSL2 directly" is the single reliable path to Windows browser access

## File Changes Made
- `/opt/data/doc_reader_tk.py` — Changed `127.0.0.1` to `0.0.0.0` on server bind
- `/opt/data/doc_reader_tk.py` — Added `/health` endpoint to do_GET handler
- `/opt/data/doc_reader_tk.py` — Added `/upload` multipart file upload handler
- `/opt/data/doc_reader_tk.py` — Added `HTML_UI` constant (6.2KB browser HTML page)
- `/opt/data/redaction_engine.py` — Extended SSN regex for partial formats (`{2,3}-{5,7}`)
- `/opt/data/redaction_engine.py` — Extended phone regex for short formats (7-digit local)

## Environment Variables
- `TERMINAL_DOCKER_NETWORK=True` — confirms Docker bridge networking
- `TERMINAL_DOCKER_RUN_AS_HOST_USER=False` — not running as host user
- `TERMINAL_DAYTONA_IMAGE=nikolaik/python-nodejs:python3.11-nodejs20` — sandbox image

## Issue 5: Cannot access /opt/data from WSL2 (filesystem isolation)

**Symptom:** User runs `wsl -e /opt/data/.venv-docreader/bin/python3 /opt/data/doc_reader_tk.py` from Windows PowerShell and gets errors. The path `/opt/data` does not exist in WSL2's filesystem.

**Root cause:** `/opt/data` is a mounted ext4 filesystem (`sdd` device) inside the Docker container. It is NOT accessible from WSL2 — the Docker container has an isolated filesystem namespace. `/opt/hermes` is the container's own filesystem (also not accessible from WSL2).

**Key learnings:**
1. **`wsl -e` executes inside the WSL2 VM**, not inside the Docker container. Paths like `/opt/data/doc_reader_tk.py` don't exist in WSL2.
2. **File uploads from Windows** must be routed through the browser tool or API, since the container can't see Windows files.
3. **The browser tool is the ONLY way** to visually interact with the UI from the user's perspective — it runs inside the container and can access `localhost:8765`.

**Solution for users:** Either use the browser tool to interact with the UI, or accept that document processing must be done via API/curl commands within the container (no direct Windows browser access possible without restructuring the deployment).

## Issue 6: User PowerShell error patterns (diagnosed via XTR screenshots)

**Symptom:** User repeatedly tries to access the browser UI from Windows but runs incorrect commands in PowerShell, producing errors.

**Root cause:** The user doesn't understand the Docker/WSL2 networking boundary and tries ad-hoc commands. Error screenshots shared as XTR*.jpg in `/opt/data/workspace/Samples/`.

**Error patterns seen:**
- `python -m http.server 8765` → Wrong command: starts a generic Python HTTP server, not the document reader
- `ssh -L 8765:localhost:8765` → Fails: no sshd in container
- `wsl -e /opt/data/...` → Fails: path doesn't exist in WSL2

**Diagnosing via XTR screenshots:**
These JPGs are accessible from inside the container at `/opt/data/workspace/Samples/XTR*.jpg`. The vision_analyze tool can read them, but may fail with 500 errors on large images (>2573x2431) — in which case, resize first:

```python
from PIL import Image
img = Image.open('/opt/data/workspace/Samples/XTR5.jpg')
img = img.resize((1280, 720))
img.save('/opt/data/workspace/Samples/XTR5_downscaled.jpg', quality=85)
# Then use vision_analyze on the downscaled version
```

## Issue 7: Portable one-file server for cross-environment deployment

When filesystem isolation prevents running the server from WSL2 (since `/opt/data` is Docker-only), create a **standalone Python file** with NO external dependencies:

```bash
python3 /opt/data/doc_reader_onefile.py --api-server 8765
```

This single file contains:
- `RedactionEngine` class (regex patterns for SSN, CC, email, phone, API keys)
- `extract_text()` function (PDF/DOCX/XLSX/PPTX/TXT with graceful fallbacks)
- `HTML_UI` string (6.2KB browser interface)
- API server (`HTTPServer` on `0.0.0.0`)

**Packaging for Windows users who can't access `/opt/data`:**
Create a ZIP with:
- `doc_reader_onefile.py` (standalone server)
- `run.bat` (Windows launcher)
- `run.sh` (Linux/WSL launcher)  
- `README.txt` (instructions)

User extracts ZIP → double-clicks `run.bat` → browser opens at `http://localhost:8766`

**Python TCP relay attempt (experimental, FAILED):**
Tried to create a TCP relay process bridging Docker container network ↔ WSL2 gateway. Cannot bind to WSL2 gateway IP (`192.168.65.7`) from inside the Docker container — different network namespace, and the container's network interface doesn't include the WSL2 gateway address.