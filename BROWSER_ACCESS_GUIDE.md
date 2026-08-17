# Browser Access Guide - Hermes Document Reader

## Problem
The server runs inside a Docker container with isolated networking.
Windows browser cannot directly access container ports.

## Solutions (in order of preference)

### Option 1: Use Browser Tool (Already works)
The browser tool runs inside this container and can access the UI directly:
- URL: http://localhost:8765/
- Full upload form, document list, and safe JSON viewer
- This is the simplest approach - no setup required

### Option 2: WSL2 Mode (For Windows Browser Access)
Run the server from WSL2 directly:
1. Open **WSL2 terminal** (Ubuntu, not Docker container)
2. Run: `/opt/data/.venv-docreader/bin/python3 /opt/data/doc_reader_tk.py --api-server 8765`
3. Open Windows browser: `http://localhost:8765`
4. ✅ WSL2 automatically forwards localhost to Windows

### Option 3: SSH Tunnel (If SSH is available)
From Windows PowerShell:
```powershell
ssh -L 8765:localhost:8765 user@192.168.65.7
```
Then: `http://localhost:8765`

## API Endpoints
- `GET /health` - Health check
- `GET /` - HTML UI
- `GET /documents` - List all processed documents
- `POST /process` - Process a file (`{"file_path": "/path/to/file"}`)
- `GET /documents/<id>/safe` - Get safe (PII-free) JSON
- `POST /upload` - Upload file via browser form

## Runner Scripts
- `bash /opt/data/run_doc_reader_browser.sh wsl2` - For WSL2 access
- `bash /opt/data/run_doc_reader_browser.sh docker` - For container access
