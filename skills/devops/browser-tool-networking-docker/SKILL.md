---
name: browser-tool-networking-docker
trigger: "When browser_tool or HTTP access to a service inside a Docker container fails."
description: "Fix Docker browser networking. Access container services."
---

# Browser Tool Networking in Docker Environments

## Trigger
Use this skill when:
- Browser tool shows "Connection refused" to localhost:PORT
- Windows browser can't reach a server running inside a Docker container
- SSH tunnel commands fail with image artifacts (XTR1.jpg, XTR2.jpg)

## Root Cause Patterns

### Docker Bridge vs Host Networking
```
Bridge mode:   Container (172.17.0.2) -> Gateway (172.17.0.1) -> WSL2 VM -> Windows
Host mode:     Container shares WSL2 VM's network stack directly
```
In bridge mode, the container has a private IP unreachable from Windows unless ports are published.

## Diagnosis Steps

### 1. Check networking mode
```bash
[ -f /.dockerenv ] && echo "Docker container"
cat /proc/1/cgroup | head -1  # cgroup v2 with 0::/ = host mode
route -n 2>/dev/null || cat /proc/net/route  # bridge gateway = 172.17.0.1
```

### 2. Check server binding
```bash
grep 'HTTPServer' doc_reader_tk.py
# BAD:  HTTPServer(("127.0.0.1", port), ...)
# GOOD: HTTPServer(("0.0.0.0", port), ...)
```

### 3. Verify accessibility
```bash
curl http://localhost:8765/health                    # Inside container
curl http://$(hostname -I | awk '{print $1}'):8765/health  # Container IP
curl http://192.168.65.7:8765/health                 # WSL2 gateway (often fails)
```

## Fix Patterns (Ordered by Reliability)

### Pattern A: Browser Tool (Works Inside Container)
**When:** Using Hermes browser_tool — runs inside the container via Playwright.
**URL:** `http://localhost:8765/` (no tunnel needed)

### Pattern B: SSH Tunnel (Windows → Container)
```powershell
# From Windows PowerShell (requires SSH server in WSL2):
ssh -L 8765:localhost:8765 user@<wsl2-ip>
# Then: http://localhost:8765
```

### Pattern C: Port Proxy (Windows Admin)
```powershell
# Run as Administrator:
netsh interface portproxy add v4tov4 listenport=8765 connectaddress=172.17.0.2 connectport=8765
```

### Pattern D: Run Server in WSL2 Directly
```bash
# Open WSL2 terminal (not container):
/opt/data/.venv-docreader/bin/python3 /opt/data/doc_reader_tk.py --api-server 8765
# WSL2 auto-forwards localhost to Windows
```

## Pitfall: SSH Command Artifacts
When `ssh -L` tunnel commands fail in Windows, they may produce artifacts:
- `XTR1.jpg`, `XTR2.jpg` — screenshots of SSH error pages in `/opt/data/`
- Root cause: SSH commands fail because there's no sshd in the container
- Always clean: `rm -f /opt/data/XTR*.jpg`
- Always verify server health before tunnels: `curl http://localhost:8765/health`

## Pitfalls This Session
- **Pitfall 1**: Background server processes die when terminal session ends.
  Use `browser tool` to interact instead of expecting persistent browser access.
- **Pitfall 2**: Users may paste screenshots expecting the agent to "see" them.
  Files on Windows desktop are NOT in the container filesystem.
  Use `vision_analyze` only on files inside `/opt/data/`.
- **Pitfall 3**: `python -m http.server` is NOT the doc reader server.
  The user mistakenly ran a generic HTTP server instead of `doc_reader_tk.py`.
  Always verify: `curl http://localhost:8765/health` returns `{"status": "ok"}`

## Daytona Sandbox Note
This environment uses a Daytona sandbox with:
- `TERMINAL_DAYTONA_IMAGE=nikolaik/python-nodejs:python3.11-nodejs20`
- Docker bridge network (NOT host mode despite docker-compose config)
- No `docker.host.internal` or SSH server access
- Browser tool is the only way to access the UI directly

### Pattern E: Use Browser Tool (Recommended for Daytona Sandboxes)
**When:** Working in a Daytona sandbox (Docker container without port publishing).
**URL:** `http://localhost:8765/` (browser tool runs inside the container)
**Why:** Daytona sandboxes isolate container networking; ports are NOT published to Windows.
The browser tool (Playwright) runs inside the same container, so localhost is shared.

### Pattern F: Use Runner Script with Mode Selection
```bash
# For WSL2 access (Windows browser):
bash /opt/data/run_doc_reader_browser.sh wsl2

# For Docker container access (browser tool):
bash /opt/data/run_doc_reader_browser.sh docker
```

## File Placement Requirements
When users reference files (e.g., screenshots, documents), verify the file is
inside the Docker mount at `/opt/data/` — NOT on the Windows desktop.

```bash
# Files from Windows DO NOT appear in the container unless shared:
# ❌ /mnt/c/Users/Username/Desktop/file.jpg  (not mounted)
# ✅ /opt/data/file.jpg                    (inside container)

# Always search the container filesystem:
find /opt/data -name "*.jpg" 2>/dev/null | grep -v venv | grep -v site-packages
```