#!/usr/bin/env python3
"""
Hermes Local Document Reader - Lightweight tkinter UI
=====================================================
A lightweight version using tkinter (built into Python) instead of PySide6.
Total runtime: ~400MB instead of ~1.1GB (no PySide6 Qt libraries needed).

All redaction/security features are identical — only the UI toolkit differs.
If tkinter is not available (e.g. python3-tk not installed), falls back to
the PySide6 UI from doc_reader_desktop.py, or runs in CLI/API-only mode.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import traceback
from pathlib import Path
from datetime import datetime

# Ensure venv packages are importable
_VENV_SITE = "/opt/data/.venv-docreader/lib/python3.13/site-packages"
if _VENV_SITE not in sys.path:
    sys.path.insert(0, _VENV_SITE)
sys.path.insert(0, "/opt/data")

# Try to import tkinter — falls back gracefully if python3-tk is missing
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    _HAS_TK = True
except ImportError:
    _HAS_TK = False
    tk = None
    ttk = None
    filedialog = None
    messagebox = None
    scrolledtext = None

# Import our modules (works regardless of UI toolkit)
from safe_format import process_document_to_safe_format, save_safe_document, generate_template_view


# -- HTML UI for Browser Access ----------------------------------------------

HTML_UI = """<!DOCTYPE html>
<html>
<head>
<title>Hermes Local Document Reader</title>
<style>
body{font-family:sans-serif;margin:40px;background:#1a1a2e;color:#eee;max-width:800px}
h1{color:#00d4ff}
.upload-box{border:3px dashed #00d4ff;padding:40px;text-align:center;border-radius:10px;margin:20px 0;cursor:pointer;transition:.3s}
.upload-box:hover{border-color:#0099cc;background:#2a2a4a}
#uploadBtn{background:#00d4ff;color:#000;padding:12px 24px;border:none;border-radius:5px;font-size:16px;cursor:pointer;font-weight:bold}
.progress{height:20px;background:#333;border-radius:10px;margin:20px 0;overflow:hidden}
.progress-bar{height:100%;background:#00d4ff;width:0%;transition:.3s}
.results{background:#2a2a4a;padding:20px;border-radius:10px;margin-top:20px}
.doc-link{color:#00d4ff;text-decoration:none;margin:5px 0;display:block}
.doc-link:hover{text-decoration:underline}
.status{color:#00d4ff;font-weight:bold}
.note{color:#888;font-size:14px}
table{width:100%;border-collapse:collapse;margin:10px 0}
th,td{border:1px solid #444;padding:8px;text-align:left}
th{background:#333}
pre{background:#1a1a2e;color:#0f0;padding:15px;border-radius:5px;overflow:auto;font-size:13px;max-height:400px}
</style>
</head>
<body>
<h1>Hermes Local Document Reader</h1>
<p>Upload a document to view the PII-redacted (safe) version for LLM consumption.</p>
<p class="note">Redacts: SSN, credit cards, emails, phones, names, addresses, bank accounts, credentials, and 10+ PII categories. All processing is local — nothing leaves this machine.</p>

<div class="upload-box" id="dropZone">
  <p>Drag & drop a file here or click to browse</p>
  <input type="file" id="fileInput" accept=".pdf,.csv,.xlsx,.xls,.docx,.pptx,.txt,.rtf,.png,.jpg,.jpeg,.gif,.bmp,.tiff,.webp">
</div>
<button id="uploadBtn" disabled>Upload & Process</button>
<div class="note" id="fileName"></div>
<div class="progress" style="display:none"><div class="progress-bar" id="progressBar"></div></div>
<div id="results"></div>

<h2>Previously Processed Documents</h2>
<div id="docList"><span class="status">Loading...</span></div>

<script>
const fileInput = document.getElementById('fileInput');
const dropZone = document.getElementById('dropZone');
const uploadBtn = document.getElementById('uploadBtn');
const fileNameEl = document.getElementById('fileName');
const progressBar = document.getElementById('progressBar');
const resultsEl = document.getElementById('results');
const docListEl = document.getElementById('docList');
let selectedFile = null;

dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.style.borderColor = '#0099cc'; });
dropZone.addEventListener('dragleave', () => dropZone.style.borderColor = '#00d4ff');
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#00d4ff';
    if (e.dataTransfer.files.length > 0) {
        selectedFile = e.dataTransfer.files[0];
        fileNameEl.textContent = selectedFile.name;
        uploadBtn.disabled = false;
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        fileNameEl.textContent = selectedFile.name;
        uploadBtn.disabled = false;
    }
});

uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    uploadBtn.disabled = true;
    document.querySelector('.progress').style.display = 'block';
    resultsEl.innerHTML = '<span class="status">Processing... (local processing, no network)</span>';

    // Copy file to uploads dir, then process via API
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const uploadResp = await fetch('/upload', {method: 'POST', body: formData});
        const uploadData = await uploadResp.json();
        const serverPath = uploadData.file_path;

        const resp = await fetch('/process', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({file_path: serverPath})
        });
        const data = await resp.json();

        if (data.error) {
            resultsEl.innerHTML = '<span style="color:#ff6666">Error: ' + data.error + '</span>';
        } else {
            const safeResp = await fetch(data.safe_url);
            const safeData = await safeResp.json();
            resultsEl.innerHTML = formatResults(safeData);
            loadDocuments();
        }
    } catch (err) {
        resultsEl.innerHTML = '<span style="color:#ff6666">Error: ' + err.message + '</span>';
    }

    document.querySelector('.progress').style.display = 'none';
    uploadBtn.disabled = false;
});

function formatResults(data) {
    let html = '<div class="results">';
    html += '<h3>Document: ' + data.document_id + '</h3>';
    html += '<p><strong>Redactions:</strong> ' + data.total_redactions + '</p>';
    html += '<p><strong>Categories:</strong> ' + Object.entries(data.category_counts).map(([k,v]) => k + ': ' + v).join(', ') + '</p>';
    html += '<h4>Safe Text (PII redacted to template variables):</h4>';
    html += '<pre>' + escapeHtml(data.all_text) + '</pre>';
    html += '<p class="note">Original values are stored locally in redaction_maps/. They are NOT accessible via this UI.</p>';
    html += '</div>';
    return html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function loadDocuments() {
    try {
        const resp = await fetch('/documents');
        const data = await resp.json();
        if (data.documents.length === 0) {
            docListEl.innerHTML = '<span class="note">No documents processed yet.</span>';
        } else {
            docListEl.innerHTML = data.documents.map(doc =>
                '<a href="/documents/' + doc.id + '/safe" class="doc-link" target="_blank">' +
                doc.filename + ' (' + doc.size + ' bytes, ' + Math.round(doc.size/1024) + ' KB)</a>'
            ).join('');
        }
    } catch (err) {
        docListEl.innerHTML = '<span style="color:#ff6666">Failed to load documents</span>';
    }
}

loadDocuments();
</script>
</body>
</html>"""


# -- Lightweight CLI/API Entry Point (no UI dependencies) --------------------

def cli_process(file_path: str) -> None:
    """Process a single file and print the safe result."""
    safe_doc, rmap = process_document_to_safe_format(file_path)
    path = save_safe_document(safe_doc)
    print(f"Safe document: {path}")
    print(f"  Pages: {safe_doc.page_count}")
    print(f"  Total redactions: {safe_doc.total_redactions}")
    for cat, count in sorted(safe_doc.category_counts.items()):
        print(f"    {cat}: {count}")


def cli_serve_api(port: int = 8765) -> None:
    """Start the local HTTP API server with browser UI for live agents."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse

    doc_root = Path("/opt/data/documents_safe")
    upload_dir = Path("/opt/data/uploads")
    upload_dir.mkdir(exist_ok=True)

    class APIHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            # Health check
            if self.path == "/health":
                self._respond(200, {"status": "ok"})
                return
            # Serve HTML UI at root
            if self.path == "/" or self.path == "/ui" or self.path == "/index.html":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(HTML_UI.encode("utf-8"))
                return
            # Serve uploaded files
            if self.path.startswith("/uploads/"):
                file_path = upload_dir / self.path[9:]
                if file_path.exists():
                    if file_path.suffix == ".json":
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                    else:
                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain; charset=utf-8")
                        self.end_headers()
                    self.wfile.write(file_path.read_bytes())
                else:
                    self._respond(404, {"error": "File not found"})
                return
            # List documents
            if self.path == "/documents" or self.path == "/documents/":
                docs = []
                if doc_root.exists():
                    for f in sorted(doc_root.glob("*_safe.json"), reverse=True):
                        docs.append({
                            "id": f.stem.replace("_safe", ""),
                            "filename": f.name,
                            "url": f"/documents/{f.stem.replace('_safe', '')}/safe",
                            "size": f.stat().st_size,
                        })
                self._respond(200, {"documents": docs})
                return
            # Fetch single safe document
            import re
            match = re.match(r"/documents/([^/]+)/safe", self.path)
            if match:
                doc_id = match.group(1)
                safe_file = doc_root / f"{doc_id}_safe.json"
                if safe_file.exists():
                    data = json.loads(safe_file.read_text())
                    self._respond(200, data)
                else:
                    self._respond(404, {"error": "Document not found"})
                return
            self._respond(404, {"error": "Not found"})

        def do_POST(self):
            if self.path == "/process":
                try:
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length)
                    data = json.loads(body) if body else {}
                    fp = data.get("file_path", "")
                    if not fp or not Path(fp).exists():
                        self._respond(400, {"error": "File not found"})
                        return
                    safe_doc, rmap = process_document_to_safe_format(fp)
                    save_safe_document(safe_doc)
                    self._respond(200, {
                        "document_id": safe_doc.document_id,
                        "safe_url": f"/documents/{safe_doc.document_id}/safe",
                        "total_redactions": safe_doc.total_redactions,
                        "category_counts": safe_doc.category_counts,
                    })
                except Exception as e:
                    self._respond(500, {"error": str(e)})
            elif self.path == "/upload":
                try:
                    content_type = self.headers.get("Content-Type", "")
                    if not content_type.startswith("multipart/form-data"):
                        self._respond(400, {"error": "Expected multipart/form-data"})
                        return
                    # Parse multipart manually
                    boundary = content_type.split("boundary=")[1].encode()
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)
                    parts = body.split(b"--" + boundary)
                    filename = None
                    file_data = None
                    for part in parts:
                        if b"filename=" in part:
                            lines = part.split(b"\r\n")
                            for line in lines:
                                decoded = line.decode("utf-8", errors="replace")
                                if "filename=" in decoded:
                                    start = decoded.find('filename="') + 10
                                    end = decoded.find('"', start)
                                    filename = decoded[start:end]
                            # Find the file data (after double CRLF)
                            data_start = part.find(b"\r\n\r\n") + 4
                            file_data = part[data_start:-2] if part.endswith(b"\r\n") else part[data_start:]
                            break
                    if filename and file_data:
                        server_filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        server_path = upload_dir / server_filename
                        server_path.write_bytes(file_data)
                        self._respond(200, {"file_path": str(server_path), "filename": filename})
                    else:
                        self._respond(400, {"error": "No file uploaded"})
                except Exception as e:
                    self._respond(500, {"error": str(e)})
            else:
                self._respond(404, {"error": "Not found"})

        def _respond(self, code, data):
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())

    server = HTTPServer(("0.0.0.0", port), APIHandler)
    print(f"API server running at http://localhost:{port}")
    print(f"  Browser UI: http://localhost:{port}")
    print(f"  Also accessible via container IP if needed")
    print(f"  Health:      http://localhost:{port}/health")
    print(f"  Documents:   http://localhost:{port}/documents")
    server.serve_forever()


# -- PySide6 Desktop UI (full-featured) ---------------------------------------

def run_pyside6_ui():
    """Run the PySide6 desktop UI."""
    from PySide6.QtWidgets import QApplication
    from doc_reader_desktop import create_ui
    app = QApplication(sys.argv)
    window = create_ui()
    window.show()
    sys.exit(app.exec())


# -- tkinter Desktop UI (lightweight) ----------------------------------------

def run_tkinter_ui():
    """Run the lightweight tkinter desktop UI."""
    if not _HAS_TK:
        print("tkinter not available. Install python3-tk or use PySide6 UI:")
        print("  python3 doc_reader_tk.py --pyside6  # Use PySide6 instead")
        print("  python3 doc_reader_tk.py --api-server 8765  # API only, no UI")
        sys.exit(1)
    from doc_reader_tk_ui import DocReaderApp as TKDocReaderApp
    root = tk.Tk()
    app = TKDocReaderApp(root)
    root.mainloop()


# -- Main CLI ----------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Hermes Local Document Reader (Lightweight tkinter UI)"
    )
    parser.add_argument("--api-server", type=int, default=None,
                       help="Start local HTTP API server with browser UI on given port")
    parser.add_argument("--process", type=str, default=None,
                       help="Process a single file and exit")
    parser.add_argument("--pyside6", action="store_true",
                       help="Use PySide6 UI instead of tkinter (falls back automatically)")
    parser.add_argument("--no-ui", action="store_true",
                       help="Run in API-only mode (no desktop UI)")
    args = parser.parse_args()

    if args.process:
        cli_process(args.process)
        return

    if args.no_ui or args.api_server:
        port = args.api_server if args.api_server else 8765
        cli_serve_api(port)
        return

    # Desktop UI mode
    if _HAS_TK and not args.pyside6:
        run_tkinter_ui()
    else:
        run_pyside6_ui()


if __name__ == "__main__":
    main()
