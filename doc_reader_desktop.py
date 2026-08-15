#!/usr/bin/env python3
"""
Hermes Local Document Reader
=============================
A desktop application for reading documents locally with automatic PII/PHI
redaction. No external APIs — everything runs on your machine.

Features:
  - File browser (browse or drag-and-drop)
  - Supports PDF, Excel, CSV, Word, PowerPoint, RTF, images, text
  - Automatic redaction of 10 categories of sensitive data
  - Template variable substitution ({SSN_1}, {PERSON_NAME_1}, etc.)
  - Local redaction map (never leaves your machine)
  - Tabbed output: Text / Tables / Metadata / JSON
  - Export to safe JSON format
  - Local HTTP API for live agents (localhost only)

Usage:
    python3 doc_reader_desktop.py
    python3 doc_reader_desktop.py --api-server 8765  # also start HTTP API
"""

from __future__ import annotations

import json
import os
import sys
import threading
import traceback
from pathlib import Path
from datetime import datetime

# Ensure docreader venv packages are importable
_VENV_SITE = "/opt/data/.venv-docreader/lib/python3.13/site-packages"
if _VENV_SITE not in sys.path:
    sys.path.insert(0, _VENV_SITE)

# Import our modules
sys.path.insert(0, "/opt/data")
sys.path.insert(0, "/opt/hermes")

from safe_format import process_document_to_safe_format, save_safe_document, generate_template_view
from redaction_engine import DEFAULT_ABBREVIATIONS

# ── HTTP API Server (optional, for live agents) ─────────────────────────────

def start_api_server(port: int = 8765, doc_root: Path = None) -> threading.Thread:
    """Start a local HTTP API server for live agents to fetch safe documents."""
    if doc_root is None:
        doc_root = Path("/opt/data/documents_safe")
    
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse
    
    class APIHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress logging
        
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
                return
            
            if self.path == "/" or self.path == "/documents":
                # List available safe documents
                docs = []
                if doc_root.exists():
                    for f in sorted(doc_root.glob("*_safe.json"), reverse=True):
                        docs.append({
                            "id": f.stem.replace("_safe", ""),
                            "filename": f.stem,
                            "url": f"/documents/{f.stem.replace('_safe', '')}/safe",
                            "size": f.stat().st_size,
                        })
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"documents": docs}).encode())
                return
            
            # /documents/<id>/safe
            match = re.match(r"/documents/([^/]+)/safe", self.path)
            if match:
                doc_id = match.group(1)
                safe_file = doc_root / f"{doc_id}_safe.json"
                if safe_file.exists():
                    content = safe_file.read_text(encoding="utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(content.encode())
                else:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Document not found"}).encode())
                return
            
            self.send_response(404)
            self.end_headers()
        
        def do_POST(self):
            if self.path == "/process":
                # Process a file and return safe format
                try:
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)
                    data = json.loads(body) if body else {}
                    file_path = data.get("file_path", "")
                    
                    if not file_path or not Path(file_path).exists():
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "File not found"}).encode())
                        return
                    
                    safe_doc, redaction_map = process_document_to_safe_format(file_path)
                    safe_path = save_safe_document(safe_doc)
                    
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    response = {
                        "document_id": safe_doc.document_id,
                        "safe_document_url": f"/documents/{safe_doc.document_id}/safe",
                        "total_redactions": safe_doc.total_redactions,
                        "category_counts": safe_doc.category_counts,
                    }
                    self.wfile.write(json.dumps(response).encode())
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
                return
            
            self.send_response(404)
            self.end_headers()
    
    import re  # noqa: E402
    server = HTTPServer(("127.0.0.1", port), APIHandler)
    print(f"API server running on http://localhost:{port}")
    server.serve_forever()


# ── PySide6 Desktop UI ──────────────────────────────────────────────────────

def create_ui():
    """Create the PySide6 desktop application."""
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QTextEdit, QFileDialog, QLabel, QProgressBar,
        QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
        QTreeWidget, QTreeWidgetItem, QMessageBox, QSplitter,
        QFrame, QFormLayout, QLineEdit, QSizePolicy,
    )
    from PySide6.QtCore import Qt, QSize, Signal, QThread, QUrl
    from PySide6.QtGui import QFont, QKeySequence, QDesktopServices
    from PySide6.QtGui import QAction
    
    class DocumentProcessor(QThread):
        """Background thread for document processing."""
        finished = Signal(object, object)  # safe_doc, redaction_map
        error = Signal(str)
        progress = Signal(str)
        
        def __init__(self, file_path: str):
            super().__init__()
            self.file_path = file_path
        
        def run(self):
            try:
                self.progress.emit("Reading document...")
                safe_doc, redaction_map = process_document_to_safe_format(self.file_path)
                self.progress.emit(f"Processed {safe_doc.page_count or '?'} pages, {safe_doc.total_redactions} redactions")
                self.finished.emit(safe_doc, redaction_map)
            except Exception as e:
                self.error.emit(f"{e}\n\n{traceback.format_exc()}")
    
    class DocReaderApp(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Hermes Local Document Reader")
            self.resize(1000, 700)
            
            self.current_file = None
            self.safe_doc = None
            self.redaction_map = None
            self.processor = None
            
            self._setup_ui()
            self._setup_menu()
            
            # Create output directories
            Path("/opt/data/documents_safe").mkdir(parents=True, exist_ok=True)
            Path("/opt/data/redaction_maps").mkdir(parents=True, exist_ok=True)
        
        def _setup_menu(self):
            menubar = self.menuBar()
            
            file_menu = menubar.addMenu("File")
            open_action = QAction("Open...", self)
            open_action.setShortcut(QKeySequence("Ctrl+O"))
            open_action.triggered.connect(self.open_file)
            file_menu.addAction(open_action)
            
            export_action = QAction("Export Safe Format", self)
            export_action.setShortcut(QKeySequence("Ctrl+E"))
            export_action.triggered.connect(self.export_safe)
            file_menu.addAction(export_action)
            
            file_menu.addSeparator()
            
            exit_action = QAction("Exit", self)
            exit_action.setShortcut(QKeySequence("Ctrl+Q"))
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            tools_menu = menubar.addMenu("Tools")
            api_action = QAction("Start API Server", self)
            api_action.triggered.connect(self.toggle_api_server)
            tools_menu.addAction(api_action)
    
        def _setup_ui(self):
            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)
            layout.setContentsMargins(10, 10, 10, 10)
            
            # Top: File selection bar
            top_bar = QHBoxLayout()
            layout.addLayout(top_bar)
            
            self.file_label = QLabel("No file selected")
            self.file_label.setStyleSheet("color: #666;")
            top_bar.addWidget(self.file_label, 1)
            
            browse_btn = QPushButton("Browse File")
            browse_btn.clicked.connect(self.open_file)
            top_bar.addWidget(browse_btn)
            
            self.process_btn = QPushButton("Process Document")
            self.process_btn.clicked.connect(self.process_document)
            self.process_btn.setEnabled(False)
            top_bar.addWidget(self.process_btn)
            
            # Progress bar
            self.progress_bar = QProgressBar()
            self.progress_bar.setTextVisible(True)
            self.progress_bar.setText("Ready")
            layout.addWidget(self.progress_bar)
            self.progress_bar.hide()
            
            # Tabbed output
            self.tabs = QTabWidget()
            layout.addWidget(self.tabs, 1)
            
            # Text tab
            self.text_edit = QTextEdit()
            self.text_edit.setReadOnly(True)
            self.text_edit.setFont(QFont("Monospace", 10))
            self.tabs.addTab(self.text_edit, "Text (Redacted)")
            
            # Tables tab
            self.tables_widget = QTableWidget()
            self.tables_widget.setAlternatingRowCountShown(True)
            header = self.tables_widget.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)
            self.tabs.addTab(self.tables_widget, "Tables")
            
            # Metadata tab
            self.metadata_widget = QTreeWidget()
            self.metadata_widget.setHeaderLabels(["Key", "Value"])
            self.metadata_widget.header().setStretchLastSection(True)
            self.tabs.addTab(self.metadata_widget, "Metadata")
            
            # JSON tab
            self.json_edit = QTextEdit()
            self.json_edit.setReadOnly(True)
            self.json_edit.setFont(QFont("Monospace", 9))
            self.tabs.addTab(self.json_edit, "Safe JSON")
            
            # Bottom: Redaction summary
            bottom = QFrame()
            bottom.setFrameShape(QFrame.StyledPanel)
            bottom.setStyleSheet("background-color: #f5f5f5; border-top: 1px solid #ddd;")
            bottom_layout = QVBoxLayout(bottom)
            self.summary_label = QLabel("No document loaded")
            self.summary_label.setStyleSheet("font-weight: bold;")
            bottom_layout.addWidget(self.summary_label)
            self.category_label = QLabel("")
            bottom_layout.addWidget(self.category_label)
            
            # Export buttons
            export_layout = QHBoxLayout()
            self.export_btn = QPushButton("Export Safe JSON")
            self.export_btn.clicked.connect(self.export_safe)
            self.export_btn.setEnabled(False)
            export_layout.addWidget(self.export_btn)
            
            self.template_btn = QPushButton("Save Template View")
            self.template_btn.clicked.connect(self.save_template)
            self.template_btn.setEnabled(False)
            export_layout.addWidget(self.template_btn)
            
            self.map_btn = QPushButton("Show Redaction Map")
            self.map_btn.clicked.connect(self.show_redaction_map)
            self.map_btn.setEnabled(False)
            export_layout.addWidget(self.map_btn)
            
            self.open_folder_btn = QPushButton("Open Output Folder")
            self.open_folder_btn.clicked.connect(self.open_output_folder)
            self.open_folder_btn.setEnabled(False)
            export_layout.addWidget(self.open_folder_btn)
            
            bottom_layout.addLayout(export_layout)
            layout.addWidget(bottom)
            
            self.layout().setStretch(2, 1)  # Tabs expand
        
        def open_file(self):
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Document",
                str(Path.home()),
                "Documents (*.pdf *.docx *.doc *.xlsx *.xls *.pptx *.ppt *.csv *.rtf *.txt *.md *.png *.jpg *.jpeg);;All Files (*)"
            )
            if file_path:
                self.load_file(file_path)
        
        def load_file(self, file_path: str):
            self.current_file = file_path
            self.file_label.setText(f"{Path(file_path).name} ({Path(file_path).stat().st_size:,} bytes)")
            self.file_label.setStyleSheet("color: #333;")
            self.process_btn.setEnabled(True)
            self.summary_label.setText(f"Selected: {Path(file_path).name}")
            self.category_label.setText("Click 'Process Document' to extract and redact")
        
        def process_document(self):
            if not self.current_file:
                return
            
            self.progress_bar.show()
            self.progress_bar.setRange(0, 0)  # Indeterminate
            self.progress_bar.setText("Processing...")
            
            self.tabs.setEnabled(False)
            self.export_btn.setEnabled(False)
            self.template_btn.setEnabled(False)
            self.map_btn.setEnabled(False)
            self.open_folder_btn.setEnabled(False)
            
            self.processor = DocumentProcessor(self.current_file)
            self.processor.progress.connect(self._update_progress)
            self.processor.finished.connect(self._on_processed)
            self.processor.error.connect(self._on_error)
            self.processor.start()
        
        def _update_progress(self, msg: str):
            self.progress_bar.setText(msg)
        
        def _on_processed(self, safe_doc, redaction_map):
            self.safe_doc = safe_doc
            self.redaction_map = redaction_map
            
            self.progress_bar.hide()
            self.tabs.setEnabled(True)
            
            # Update text tab
            self.text_edit.setPlainText(safe_doc.all_text or "(No text extracted)")
            
            # Update tables tab
            if safe_doc.tables:
                self.tables_widget.setRowCount(len(safe_doc.tables[0]))
                self.tables_widget.setColumnCount(len(safe_doc.tables[0][0]))
                for table_idx, table in enumerate(safe_doc.tables):
                    for row_idx, row in enumerate(table):
                        for col_idx, cell in enumerate(row):
                            self.tables_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(cell)))
            self.tabs.update()
            
            # Update metadata tab
            self.metadata_widget.clear()
            for key, value in safe_doc.metadata.items():
                item = QTreeWidgetItem([str(key), str(value)])
                self.metadata_widget.addTopLevelItem(item)
            for key, value in safe_doc.metadata.items():
                if isinstance(value, dict):
                    parent = QTreeWidgetItem([str(key), ""])
                    self.metadata_widget.addTopLevelItem(parent)
                    for k, v in value.items():
                        child = QTreeWidgetItem([str(k), str(v)])
                        parent.addChild(child)
            
            # Update JSON tab
            self.json_edit.setPlainText(json.dumps(safe_doc.to_full_dict(), indent=2, default=str))
            
            # Update summary
            self.summary_label.setText(
                f"✅ Processed: {self.current_file and Path(self.current_file).name}\n"
                f"Redactions: {safe_doc.total_redactions}"
            )
            if safe_doc.category_counts:
                counts_str = ", ".join(f"{k}: {v}" for k, v in sorted(safe_doc.category_counts.items()))
                self.category_label.setText(f"Categories: {counts_str}")
            else:
                self.category_label.setText("No sensitive data detected")
            
            # Enable export buttons
            self.export_btn.setEnabled(True)
            self.template_btn.setEnabled(True)
            self.map_btn.setEnabled(True)
            self.open_folder_btn.setEnabled(True)
        
        def _on_error(self, error_msg: str):
            self.progress_bar.hide()
            self.tabs.setEnabled(True)
            QMessageBox.critical(self, "Error", f"Failed to process document:\n\n{error_msg}")
        
        def export_safe(self):
            if not self.safe_doc:
                return
            safe_path = save_safe_document(self.safe_doc)
            QMessageBox.information(self, "Exported", f"Safe document saved to:\n{safe_path}")
        
        def save_template(self):
            if not self.safe_doc:
                return
            template = generate_template_view(self.safe_doc)
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Template View",
                str(Path.home()),
                "Text Files (*.txt *.md);;All Files (*)"
            )
            if file_path:
                Path(file_path).write_text(template, encoding="utf-8")
                QMessageBox.information(self, "Saved", f"Template saved to:\n{file_path}")
        
        def show_redaction_map(self):
            if not self.redaction_map:
                return
            map_text = json.dumps(self.redaction_map.to_dict(), indent=2, ensure_ascii=False)
            # Show in a new dialog
            dialog = QTextEdit()
            dialog.setWindowTitle("Redaction Map (LOCAL ONLY - Do Not Share)")
            dialog.setPlainText(map_text)
            dialog.setReadOnly(True)
            dialog.resize(600, 400)
            dialog.show()
        
        def open_output_folder(self):
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl.fromLocalFile("/opt/data/documents_safe"))
        
        def toggle_api_server(self):
            # Placeholder for API server toggle
            QMessageBox.information(self, "API Server", 
                "Use --api-server flag when launching:\n\npython3 doc_reader_desktop.py --api-server 8765\n\n"
                "The API runs on http://localhost:8765"
            )
    
    return DocReaderApp


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Hermes Local Document Reader")
    parser.add_argument("--api-server", type=int, default=None,
                       help="Port for local HTTP API server (e.g. 8765)")
    parser.add_argument("--no-ui", action="store_true",
                       help="Only run the HTTP API server, no desktop UI")
    parser.add_argument("--process", type=str, default=None,
                       help="Process a single file and exit")
    args = parser.parse_args()
    
    if args.process:
        # CLI mode: process a single file
        safe_doc, redaction_map = process_document_to_safe_format(args.process)
        safe_path = save_safe_document(safe_doc)
        print(f"✓ Safe document: {safe_path}")
        print(f"  Pages: {safe_doc.page_count}")
        print(f"  Total redactions: {safe_doc.total_redactions}")
        for cat, count in sorted(safe_doc.category_counts.items()):
            print(f"    {cat}: {count}")
        return
    
    if args.no_ui:
        # API-only mode
        if args.api_server:
            print(f"Starting API server on port {args.api_server}...")
            start_api_server(args.api_server)
        return
    
    # Desktop UI mode
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Optionally start API server in background
    if args.api_server:
        api_thread = threading.Thread(
            target=start_api_server,
            args=(args.api_server,),
            daemon=True,
        )
        api_thread.start()
        print(f"API server started on http://localhost:{args.api_server}")
    
    app_window = create_ui()
    app_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()