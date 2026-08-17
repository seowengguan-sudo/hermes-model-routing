# WSL2 + Docker: HTTP Server Binding Fix

## Problem
Docker container running under WSL2 with `network_mode: host`. A Python HTTP server
binding to `127.0.0.1:PORT` is NOT reachable from the Windows host browser.

## Root Cause
`network_mode: host` in Docker Desktop for WSL2 shares the **WSL2 VM network namespace**,
not the Windows host network. Therefore `127.0.0.1` inside the container resolves to
the **WSL2 VM's loopback**, which Windows has no route to by default.

## Environment Detection
```bash
# Check if in Docker
[ -f /.dockerenv ] && echo "Inside Docker container"

# Check if WSL2
grep -qi microsoft /proc/version && echo "Under WSL2"

# Get container IP (reachable from WSL2)
hostname -I → 172.17.0.2

# Get WSL2 gateway (Windows host from container perspective)
cat /etc/resolv.conf | grep nameserver → 192.168.65.7
```

## Solution
Change HTTPServer binding from `127.0.0.1` to `0.0.0.0`:

```python
# BEFORE (not reachable from Windows):
server = HTTPServer(("127.0.0.1", port), Handler)

# AFTER (reachable from any network interface):
server = HTTPServer(("0.0.0.0", port), Handler)
```

## Access Patterns

### From Windows browser:
1. **Find the container IP** (run inside container):
   ```bash
   hostname -I  # e.g., 172.17.0.2
   cat /etc/resolv.conf | grep nameserver  # e.g., 192.168.65.7
   ```

2. **Option A — Direct** (if WSL2 routing allows):
   ```
   http://172.17.0.2:8765
   ```

3. **Option B — SSH tunnel** (most reliable):
   In Windows PowerShell:
   ```powershell
   ssh -L 8765:localhost:8765 <wsl2-gateway-ip>
   # Then: http://localhost:8765
   ```

### From WSL2 terminal:
```bash
curl http://127.0.0.1:8765/health  # localhost
curl http://172.17.0.2:8765/health  # container IP
```

## Files Changed
- `/opt/data/doc_reader_tk.py`: `HTTPServer(("127.0.0.1", port), ...)` → `HTTPServer(("0.0.0.0", port), ...)`

## Verification
```bash
# Server should bind to 0.0.0.0
cat /proc/net/tcp | grep 239F  # 00000000:239F = 0.0.0.0:8765

# Health check from localhost
curl http://127.0.0.1:8765/health

# Health check from container IP
CONTAINER_IP=$(hostname -I | awk '{print $1}')
curl http://${CONTAINER_IP}:8765/health
```

## Related
See `gateway-watchdog-recovery.md` for the gateway auto-restart watchdog pattern,
which also operates in this WSL2 + Docker environment.