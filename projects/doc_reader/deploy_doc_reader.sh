#!/bin/bash
# ============================================================
# Hermes Local Document Reader Agent - Laptop Deployment Script
# ============================================================
# This script copies all necessary files to run the document reader
# agent on your laptop (any Linux/macOS/Windows+Python environment).
#
# Usage:
#   1. Copy this script to your laptop
#   2. Run: bash deploy_doc_reader.sh
#   3. Launch: python3 doc_reader_desktop.py
#
# Total size: ~1.1 GB (PySide6 UI is the largest component)
# Alternative: see doc_reader_tk.py for a lightweight tkinter version (~200MB)
# ============================================================

set -e

# Configuration
SOURCE_DIR="/opt/data"
VENV_SOURCE="/opt/data/.venv-docreader"
DEST_DIR="${1:-./doc_reader_agent}"

echo "=== Hermes Local Document Reader - Deployment ==="
echo "Destination: $DEST_DIR"
echo ""

# Create destination directory
mkdir -p "$DEST_DIR"

# ── Step 1: Copy core scripts ──────────────────────────────────────────────
echo "--- Step 1: Copying core scripts ---"
cp "$SOURCE_DIR/redaction_engine.py" "$DEST_DIR/"
cp "$SOURCE_DIR/safe_format.py" "$DEST_DIR/"
cp "$SOURCE_DIR/doc_reader_desktop.py" "$DEST_DIR/"
cp "$SOURCE_DIR/doc_reader_agent.py" "$DEST_DIR/"
cp "$SOURCE_DIR/doc_reader_tk.py" "$DEST_DIR/"  # Lightweight tkinter alternative
cp "$SOURCE_DIR/hermes-security-policy.md" "$DEST_DIR/" 2>/dev/null || true
echo "  ✓ Core scripts copied"

# ── Step 2: Copy Python virtual environment ───────────────────────────────
echo "--- Step 2: Copying Python virtual environment ---"
echo "  (This is ~1.1 GB - mostly PySide6 Qt libraries)"
cp -r "$VENV_SOURCE" "$DEST_DIR/.venv-docreader"
echo "  ✓ Virtual environment copied"

# ── Step 3: Create launcher scripts ───────────────────────────────────────
echo "--- Step 3: Creating launcher scripts ---"

# launcher.sh
cat > "$DEST_DIR/run.sh" << 'EOF'
#!/bin/bash
# Launcher for the Desktop UI version (PySide6)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR:.venv-docreader/lib/python3.13/site-packages:$PYTHONPATH"
./.venv-docreader/bin/python3 doc_reader_desktop.py "$@"
EOF

# launcher_tk.sh (lightweight tkinter version)
cat > "$DEST_DIR/run_tk.sh" << 'EOF'
#!/bin/bash
# Launcher for the lightweight tkinter version (~200MB venv)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR:.venv-docreader/lib/python3.13/site-packages:$PYTHONPATH"
./.venv-docreader/bin/python3 doc_reader_tk.py "$@"
EOF

chmod +x "$DEST_DIR/run.sh" "$DEST_DIR/run_tk.sh"
echo "  ✓ Launcher scripts created"

# ── Step 4: Create requirements.txt ────────────────────────────────────────
echo "--- Step 4: Creating requirements.txt ---"
cat > "$DEST_DIR/requirements.txt" << 'EOF'
# Core document reading
pypdf>=4.0
pymupdf>=1.24
pdfplumber>=0.10
openpyxl>=3.1
xlrd>=2.0
python-docx>=1.1
python-pptx>=0.6
striprtf>=0.10

# Redaction (NER for name/location detection)
spacy>=3.7
en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl

# Image rendering (if installed)
Pillow>=10.0

# PDF generation (for test files only)
reportlab>=4.0

# Desktop UI (choose one):
PySide6>=6.6        # Heavy (~640MB) but modern native look
# OR for lightweight:
# tkinter (built into Python, no install needed)

# CLI dependencies
uv>=0.5  # Optional: for easy package management
EOF
echo "  ✓ requirements.txt created"

# ── Step 5: Create README ───────────────────────────────────────────────────
echo "--- Step 5: Creating README ---"
cat > "$DEST_DIR/README.md" << 'EOF'
# Hermes Local Document Reader Agent

A self-contained desktop application for reading PDF, CSV, Excel, Word, PowerPoint,
RTF, and image files **locally** with automatic PII/PHI/financial data redaction.

## Quick Start (Desktop UI)
```bash
./run.sh              # Uses PySide6 (modern native UI)
# or for lightweight version:
./run_tk.sh           # Uses tkinter (built into Python, lighter)
```

## CLI Mode (Process Single File)
```bash
./.venv-docreader/bin/python3 doc_reader_desktop.py --process /path/to/file.pdf
# Output: Safe JSON with template variables + redaction map
```

## HTTP API Mode (For Live Agents)
```bash
./.venv-docreader/bin/python3 doc_reader_desktop.py --api-server 8765
# Then access:
#   GET  /health                  - health check
#   GET  /documents               - list safe documents
#   GET  /documents/<id>/safe     - fetch safe JSON
#   POST /process {"file_path":...}  - process a file
```

## Files
| File | Purpose |
|------|---------|
| `redaction_engine.py` | PII/PHI redaction core (regex + NER + custom abbrevs) |
| `safe_format.py` | Safe output generation + redaction map persistence |
| `doc_reader_agent.py` | Low-level document extraction (PDF, XLSX, DOCX, PPTX, CSV, RTF, images) |
| `doc_reader_desktop.py` | PySide6 desktop UI + CLI + HTTP API |
| `doc_reader_tk.py` | Lightweight tkinter UI (no PySide6 needed) |
| `doc_reader_security_policy.md` | Data security governance policy (10 exclusion categories) |
| `.venv-docreader/` | Python virtualenv with all dependencies |

## Redaction Categories
1. PII (names, SSN, addresses, phones, emails, biometrics)
2. PHI (medical records, insurance, MRNs)
3. Financial (credit cards, bank accounts, loans)
4. Credentials (passwords, API keys, certs, tokens)
5. Corporate (trade secrets, IP, M&A plans)
6. National Security (classified, ITAR, EAR)
7. Industry Data (student records, legal privileged)
8. Infrastructure (IPs, network diagrams, firewall configs)
9. Behavioral (GPS, browsing history, preferences)
10. Composite (user IDs, quasi-identifiers)

## Custom Abbreviations
Edit `DEFAULT_ABBREVIATIONS` in `redaction_engine.py` to define your own:
```python
DEFAULT_ABBREVIATIONS = {
    "A": "Client Name",
    "B": "Project Name",
    "C": "Internal System",
    ...
}
```
Matches patterns like: "Client A: value" -> "Client {A}={CUSTOM_A_1}"
EOF
echo "  ✓ README.md created"

# ── Done ────────────────────────────────────────────────────────────────────
echo ""
echo "=== Deployment Complete ==="
echo ""
echo "To run on your laptop:"
echo "  1. cd $DEST_DIR"
echo "  2. ./run.sh          (PySide6 UI - full feature, ~1.1GB)"
echo "     ./run_tk.sh       (tkinter UI - lighter, ~200MB if you reinstall)"  
echo ""
echo "Output directories:"
echo "  /documents_safe/     - Safe JSON files for live agents"
echo "  /redaction_maps/     - Redaction mapping files (LOCAL ONLY)"
echo ""
echo "Total size: ~$(du -sh .venv-docreader | cut -f1)"
