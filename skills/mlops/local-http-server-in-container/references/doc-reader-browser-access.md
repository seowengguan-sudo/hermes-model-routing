# Document Reader Browser Access — Reference

## Problem
Users want to access `http://localhost:8765` (OAKAI Document Reader) from their
Windows browser, but the server runs inside an isolated Docker container.

## Why Simple Fixes Don't Work Here

### 1. SSH Tunnel
```powershell
ssh -L 8765:localhost:8765 user@172.17.0.2
```
**Fails:** No `sshd` installed in this container (`sshd not found`), and no
permissions to install it (`dpkg` locked, not root).

### 2. Run from WSL2 directly
```powershell
wsl -e /opt/data/.venv-docreader/bin/python3 /opt/data/doc_reader_tk.py --api-server 8765
```
**Fails:** `/opt/data` exists only inside the Docker container filesystem, not in
WSL2. The container has an isolated ext4 mount (`sdd` device at `/opt/data`).

### 3. Direct Docker port access
```
http://172.17.0.2:8765  # container IP
http://192.168.65.7:8765 # WSL2 gateway
```
**Fails:** Docker bridge network isolation. Container can ping the WSL2 gateway
(`192.168.65.7`) but cannot bind to its IP — `Cannot assign requested address`.

## What Actually Works

### Browser Tool (Inside Container)
```python
browser_navigate("http://localhost:8765/")
```
**✅ This is the most reliable method.** The browser tool runs Playwright
inside the container, sharing the same network namespace. It can access
`localhost:8765` directly and provide full visual UI interaction.

### API Commands (Inside Container)
```bash
curl -s http://localhost:8765/health
curl -X POST http://localhost:8765/process -H "Content-Type: application/json" \
    -d '{"file_path": "/opt/data/sample_invoice.pdf"}'
curl http://localhost:8765/documents/<id>/safe
```
**✅ Works from any terminal inside the container.**

## One-File Server Pattern (Recommended)

When filesystem isolation prevents running the server from WSL2 (since `/opt/data`
is container-only ext4 mount), create a **standalone Python file** with NO external
dependencies:

```bash
python3 /opt/data/doc_reader_onefile.py --api-server 8765
# Accessible at: http://localhost:8765
```

This single file (`/opt/data/doc_reader_onefile.py`, ~28KB) contains:
- `RedactionEngine` class (regex patterns for SSN, CREDIT_CARD, EMAIL, PHONE, API_KEY, BANK_ACCOUNT)
- `extract_text()` function (PDF/DOCX/XLSX/PPTX/TXT with graceful fallbacks to ZIP XML parsing using pypdf/docx/openpyxl if available in venv)
- `HTML_UI` string (Professional OAKAI-branded CSS UI with high contrast design, file type filtering via `accept` attribute)
- API server (`HTTPServer` on `0.0.0.0`) with endpoints: `/health`, `/`, `/documents`, `/upload`, `/process`

**Key improvements from session learnings:**
- UI branded as **OAKAI** (not Hermes) with professional dark-blue color scheme
- File input includes `accept=".pdf,.docx,.xlsx,.pptx,.txt,.csv,.html,.htm,.md,.json"` filter
- Documents list shows actual content instead of stuck "Loading..." (returns proper JSON from `/documents` endpoint)
- Redaction results show category badges with colored highlights
- File upload path returned in response for transparency

**Packaging for Windows users:**
```python
# Create ZIP containing doc_reader_onefile.py, run.bat, run.sh, README.txt
# User extracts ZIP → double-clicks run.bat → browser opens at http://localhost:8765
# ZIP location: /opt/data/workspace/Samples/doc_reader_windows_portable.zip
```

### Enhanced Redaction Engine Details

The `doc_reader_onefile.py` includes an `EnhancedRedactionEngine` with:
- **Priority-ordered, position-sorted redaction** (avoids `text.replace()` offset bugs)
- **Separate `/documents/<id>/map` API endpoint** for redaction mapping (kept OUT of safe document output)
- **Business-sensitive data detection** (COMPANY_NAME, DIRECTOR_NAME, PRODUCT_NAME, QUOTATION_ID, COST_VALUE)

#### Common Redaction Pitfalls (from testing):
- Phone patterns must NOT use `\b` boundaries on leading `+?` digit prefix (catches `+1-555-123-4567` correctly)
- Product name patterns too greedy across newlines — anchor with `[ \t]` not `\s+`
- Bank account `Account:` prefix must allow `:` via `\s*[:]?\s*`
- Cost patterns must not include trailing `\b` for `$` amounts followed by commas
- Always process PII categories BEFORE business-sensitive to avoid business patterns consuming PII tokens
- **Critical:** Keep redaction_map out of the safe document JSON — store separately, serve via dedicated endpoint

## Vision Analysis of Error Screenshots (XTR*.jpg)

### Handling Large Screenshots (test18.png, test15.png, etc.)

When users share screenshots showing PowerShell errors:

1. **Locate the screenshot:** `find /opt/data -name "XTR*.jpg" -o -name "test*.png"`
2. **If vision_analyze returns 500 error:** The image is likely too large or in RGBA mode. Use PIL to preprocess:
   ```python
   from PIL import Image
   
   # For very large PNGs (test18.png is 2573x2431)
   img = Image.open('/opt/data/workspace/Samples/test18.png')
   print(f'Original: {img.size[0]}x{img.size[1]}, mode={img.mode}')
   
   # Convert RGBA to RGB and resize for vision analysis
   img = img.convert('RGB')
   img = img.resize((1280, 720), Image.LANCZOS)
   img.save('/opt/data/workspace/Samples/test18_small.jpg', 'JPEG', quality=85)
   
   # Then call: vision_analyze(image_url='/opt/data/workspace/Samples/test18_small.jpg')
   ```
   **Key insight:** `test18.png` was originally a 2573x2431px RGBA PNG at 372KB. Vision analysis consistently returns HTTP 500 ("EngineCore encountered an issue" / "Inference connection error") on the original. After PIL preprocessing (convert to RGB, resize to 1280x720, JPEG quality 85), vision analysis succeeds.

3. **Use vision_analyze** on the preprocessed file
4. **If vision still fails:** Use Playwright to take screenshots of the UI directly (more reliable than user-provided screenshots) and analyze those instead
5. **Alternative analysis:** Use `image_generate` tool or manual inspection with Playwright's `page.content()` and `page.text_content()` methods to extract visible text without vision

### Common XTR Screenshot Error Patterns

| Screenshot | Error Shown | Root Cause | Fix |
|-----------|-------------|------------|-----|
| XTR1.jpg, XTR2.jpg | SSH connection refused | `ssh -L 8765:localhost:8765` failed (no sshd in container) | Use browser tool instead |
| test18.png | "Failed to load resource: 404" + "Loading..." stuck | Old UI bug: `/documents` endpoint returned empty, file input had no `accept` filter | Fixed in doc_reader_onefile.py — `/documents` returns proper JSON, file input has `accept` attribute |
| test15.png | Browser shows raw JSON instead of HTML | Missing `/health` before `/` route check in handler | Fixed in doc_reader_onefile.py: `/health` route checked first |

## User Error Patterns from XTR Screenshots

| Error Pattern | Root Cause | Fix |
|--------------|------------|-----|
| `python -m http.server` | Wrong command, generic server | Use `doc_reader_onefile.py` |
| `wsl -e /opt/data/...` | `/opt/data` not in WSL2 FS | Explain filesystem isolation |
| `ssh -L 8765:...` | No sshd in container | Explain sshd absence, offer browser tool |
| `localhost:8765` Windows | Docker bridge isolation | Use browser tool or API commands |
| `python: Can't open file` | Path doesn't exist in WSL2 | Paths are container-only |
| Vision 500 error on PNG | Image too large/RGBA mode | Preprocess with PIL (resize, convert to RGB JPEG) |

## Key Environment Parameters

| Parameter | Value |
|-----------|-------|
| Container OS | Linux (hermes image) |
| Image | `nikolaik/python-nodejs:python3.11-nodejs20` |
| Container IP | `172.17.0.2` |
| WSL2 Gateway | `192.168.65.7` (from `/etc/resolv.conf`) |
| `/opt/data` mount | `ext4` (`sdd` device), NOT accessible from WSL2 |
| `/opt/hermes` | Container's own filesystem (read-only) |
| sshd available | ❌ No |
| Docker port publishing | ❌ Default `-p` not used |

## Files Created for Access

| File | Purpose |
|------|---------|
| `/opt/data/doc_reader_onefile.py` | Standalone server (28KB, stdlib-only) with OAKAI UI |
| `/opt/data/doc_reader_tk.py` | tkinter/CLI/API variant (lighter weight) |
| `/opt/data/doc_reader_wsl2.py` | Lightweight standalone server for real WSL2 |
| `/opt/data/setup_doc_reader_wsl2.sh` | One-command setup for WSL2 |
| `/opt/data/start_doc_reader.sh` | Quick restart script |
| `/opt/data/workspace/Samples/doc_reader_windows_portable.zip` | Portable ZIP for Windows download |

## Directory Structure

```
/opt/data/
├── doc_reader_onefile.py          # Standalone server
├── doc_reader_tk.py               # Lightweight variant
├── uploads/                       # Uploaded files stored here
│   └── upload_YYYYMMDD_HHMMSS_filename
├── documents_safe/                # Safe JSON outputs ({VARIABLE} format)
│   └── doc_YYYYMMDD_HHMMSS_safe.json
├── redaction_maps/                # Variable-to-original mapping (local only)
│   └── doc_YYYYMMDD_HHMMSS_redaction_map.json
└── workspace/Samples/
    └── doc_reader_windows_portable.zip  # For Windows download
```

## For Future Sessions

When a user asks "why can't I open the browser UI?":

1. **Check for XTR*.jpg/test*.png screenshots** at `/opt/data/workspace/Samples/` — these capture user PowerShell errors and show exact commands/failures. Use `vision_analyze` (with PIL resize workaround for 500 errors on large images) to read them.
2. **Resize screenshots before vision analysis** if they exceed 1280px in width — use PIL `.resize((1280, 720))` with `quality=75-85` to get under vision model limits. If vision returns "Internal Server Error", downscale and retry.
3. **Verify server is running**: `pgrep -f doc_reader_onefile` or `pgrep -f doc_reader_tk`
4. **Use browser tool** for UI verification: `browser_navigate("http://localhost:8765/")`
5. **If user insists on Windows browser access**: explain filesystem isolation (`/opt/data` is container-only, not in WSL2). Point to portable ZIP at `/opt/data/workspace/Samples/doc_reader_windows_portable.zip` that they can download and run locally.
6. **Route to API commands** or browser tool interaction instead — direct Windows browser access impossible without restructuring

## Quick Start for Document Reader

- Run server: `python3 /opt/data/doc_reader_onefile.py` (standalone, no deps)
  - Or: `/opt/data/.venv-docreader/bin/python3 /opt/data/doc_reader_tk.py --api-server 8765`
- Verify via browser tool: `browser_navigate("http://localhost:8765/")`
- API endpoints: `GET /health`, `GET /documents`, `POST /upload`, `POST /process`, `GET /documents/<id>/safe`
- Directory structure: uploads → documents_safe → redaction_maps (all under `/opt/data/`)