---
name: local-http-server-in-container
trigger: "When you need to run an HTTP server inside a Docker/WSL2 container and access its UI."
description: "HTTP servers in containers need 0.0.0.0 not localhost."
---

# Local HTTP Server in Docker/WSL2 Containers

## Problem
Running an HTTP server inside a Docker container on WSL2 — the UI is not reachable from Windows host browser or external curl.

## Root Causes
1. **`127.0.0.1` binding** — Python HTTPServer binds to loopback only; Windows host can't reach container loopback
2. **Docker bridge networking** — container has its own IP (e.g., `172.17.0.2`), separate from WSL2 VM
3. **No port publishing** — no `-p 8765:8765` mapping

## Fix

### Bind to 0.0.0.0
```python
HTTPServer(("0.0.0.0", port), Handler)  # NOT ("127.0.0.1", port)
```

### Access Options
| Method | Works | Notes |
|--------|-------|-------|
| Browser tool (same container) | Yes | `browser_navigate("http://localhost:PORT")` |
| curl localhost:PORT (in container) | Yes | Same network namespace |
| curl 172.17.0.2:PORT (container IP) | Yes | Container bridge IP |
| Windows browser localhost:PORT | No | Different network namespace |
| Windows browser 172.17.0.2:PORT | No | Docker bridge isolation |

### SSH Tunnel from Windows
```powershell
ssh -L 8765:localhost:8765 $USER@$(hostname -I)
# Then open http://localhost:8765 in Windows browser
```

> ⚠️ **SSH tunnel workaround:** Some containers have no sshd installed (check with `which sshd`). If SSH is unavailable, use the alternatives below instead.

### Alternative: Run server in WSL2 directly (bypasses Docker networking entirely)
```bash
# From WSL2 terminal (NOT inside the Docker container):
python3 /opt/data/doc_reader_tk.py --api-server 8765
# WSL2 auto-forwards localhost ports to Windows — no tunnel needed
# Then open: http://localhost:8765 in Windows browser
```

### Alternative: Browser tool (if you only need to verify the UI)
```python
browser_navigate("http://localhost:8765/")
# The browser tool runs inside the container, so localhost works
```

### Docker Compose caveat
The `docker-compose.yml` may specify `network_mode: host` but the actual runtime might use bridge networking (container IP `172.17.0.x`). Always verify with `cat /proc/net/route` and `hostname -I`. When `network_mode: host` is NOT actually in effect, you MUST publish ports with `-p` or use SSH tunneling.

## Key Insight
**Browser tools run inside the container.** Use `browser_navigate("http://localhost:PORT")` for UI verification — works even when Windows browser cannot reach the same URL.

> **Session notes:** See `references/session-notes.md` for detailed troubleshooting of Docker/WSL2 networking, browser tool access patterns, and common user-facing issues. For document reader-specific browser access patterns and troubleshooting, see `references/doc-reader-browser-access.md`. For Windows packaging patterns, silent launch via VBS, and portability checklist, see `references/windows-deployment-patterns.md`.

### One-File Server Pattern

When filesystem isolation prevents running the server from WSL2 (since `/opt/data` is container-only ext4 mount), create a **standalone Python file** with NO external dependencies:

#### Enhanced One-File Server Features (OAKAI Document Reader)
The `doc_reader_onefile.py` includes a full enterprise data anonymization pipeline:
- `EnhancedRedactionEngine` with priority-ordered, position-sorted redaction (avoids `text.replace()` offset bugs)
- 10 security policy categories: SSN, EMAIL, PHONE, CREDIT_CARD, BANK_ACCOUNT, COMPANY_NAME, DIRECTOR_NAME, PRODUCT_NAME, QUOTATION_ID, COST_VALUE
- Reversible variable mapping stored in `data/redaction_maps/<id>_redaction_map.json`
- Safe JSON output in `data/documents_safe/<id>_safe.json` with zero PII leakage
- Professional dark-themed UI with OAKAI branding, drag-drop, file browsing, variable highlighting
- Separate `/documents/<id>/map` API endpoint for redaction map (kept out of safe output)

**Critical: Keep safe output free of original values.** The safe document must NOT include the redaction_map — store it separately and serve via a dedicated endpoint. Verify zero leakage by checking safe text for all original sensitive values.

```bash
python3 /opt/data/doc_reader_onefile.py --api-server 8765
# Accessible at: http://localhost:8765
```

This single file contains:
- `RedactionEngine` class (regex patterns for SSN, CREDIT_CARD, EMAIL, PHONE, API_KEY)
- `extract_text()` function (PDF/DOCX/XLSX/PPTX/TXT with graceful fallbacks to ZIP XML parsing)
- `HTML_UI` string (Professional CSS UI with OAKAI branding, high contrast design, file type filtering)
- API server (`HTTPServer` on `0.0.0.0`) with endpoints: `/health`, `/`, `/documents`, `/upload`, `/process`, `/documents/<id>/safe`, `/documents/<id>/map`, `/settings`, `GET /settings`, `GET /settings/categories`

**Packaging for Windows users** who can't access `/opt/data`:
Create a ZIP containing exactly **5 files**: `doc_reader_onefile.py`, `run.bat`, `run.sh`, `start_silent.vbs`, and `README.txt`. User extracts ZIP → double-clicks `start_silent.vbs` (silent/background) OR `run.bat` (console) → browser opens at `http://localhost:8765`.

**Key portability requirements for Windows deployment:**
- No hardcoded `/opt/` or `/home/` paths in code logic (use `PATH(__file__).parent`)
- All `mkdir()` calls use `parents=True, exist_ok=True`
- venv dependency paths resolved dynamically or with graceful fallback
- `start_silent.vbs` looks for `pythonw.exe` in PATH then common install locations (Python310-312)
- If `pythonw.exe` not found, fall back to `run.bat` for console debugging

### Diagnosing User PowerShell Errors via XTR Screenshots

When a user shares a JPG showing their PowerShell error (found at `/opt/data/workspace/Samples/XTR*.jpg`):

1. **Locate the screenshot**: `find /opt/data -name "XTR*.jpg"`
2. **Convert if needed**: Use PIL to resize/convert if vision analysis fails with 500 errors:
   ```python
   from PIL import Image
   img = Image.open('XTR5.jpg')
   img = img.resize((1280, 720))
   img.save('XTR5_downscaled.jpg', quality=85)
   ```
3. **Analyze**: Use `vision_analyze` to read the terminal text
4. **Identify error pattern**:
   - `python -m http.server` → wrong command (generic server, not doc reader)
   - `wsl -e /opt/data/...` → path doesn't exist in WSL2 (filesystem isolation)
   - `ssh -L 8765:...` → no sshd installed in container
   - `localhost:8765` from Windows → Docker bridge isolation
5. **Provide targeted fix** based on the specific error shown

## Quick Start for Document Reader
- Run server: `/opt/data/.venv-docreader/bin/python3 /opt/data/doc_reader_tk.py --api-server 8765`
- Verify via browser tool: `browser_navigate("http://localhost:8765/")`
- Access from Windows: Run the above command from **WSL2 directly** (not Docker container); WSL2 auto-forwards to Windows
- API endpoints: `GET /health`, `GET /documents`, `POST /process`, `GET /documents/<id>/safe`

## Diagnostics
```bash
cat /proc/net/tcp | grep "239F"  # 8765 in hex = 0x239F
hostname -I  # container IP (e.g. 172.17.0.2)
cat /etc/resolv.conf | grep nameserver  # WSL2 gateway (e.g. 192.168.65.7)
ls /.dockerenv  # confirms Docker container
```

## Checklist
1. Server binds to `0.0.0.0`, not `127.0.0.1`
2. `/health` responds via curl `localhost:PORT`
3. HTML UI served at root (`GET /` returns HTML)
4. Browser tool can reach `http://localhost:PORT`
5. Container IP works for external access
6. Check `/proc/net/tcp` for binding confirmation (`00000000:` prefix = 0.0.0.0)
7. Verify network mode: `cat /proc/net/route` shows bridge vs host
8. Confirm Docker networking: `hostname -I` for container IP, `cat /etc/resolv.conf` for WSL2 gateway
9. Check sshd availability: `which sshd` — if missing, SSH tunnel won't work; use browser tool or WSL2-direct alternatives
