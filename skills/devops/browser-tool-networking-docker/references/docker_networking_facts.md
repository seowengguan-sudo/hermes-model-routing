# Runtime Facts: Docker/WSL2 Networking for Browser Access

## Environment (this session, Aug 14, 2026)
- Container: Docker bridge mode (network_mode: host declared in docker-compose.yml but actually bridge at runtime)
- Container IP: 172.17.0.2
- Bridge gateway: 172.17.0.1
- WSL2 gateway: 192.168.65.7 (unreachable from container)
- Server binding: HTTPServer(("0.0.0.0", 8765)) in doc_reader_tk.py
- User: hermes (not root)

## Accessibility Matrix
| URL | From Container | From Windows |
|-----|---------------|-------------|
| localhost:8765 | Works | Not forwarded |
| 172.17.0.2:8765 | Works | Bridge isolated |

## Browser Tool Behavior
- Hermes browser_tool runs Playwright INSIDE the container
- localhost:8765 IS accessible from browser tool
- Confirmed working multiple times in this session

## SSH Tunnel Issues
- No sshd in Docker container
- Failed SSH commands produced XTR1.jpg/XTR2.jpg artifacts in /opt/data/
- Cleanup: rm -f /opt/data/XTR*.jpg

## Key Commands
```bash
[ -f /.dockerenv ] && echo "In Docker"
cat /proc/net/tcp | grep "239F"
curl http://localhost:8765/health
```