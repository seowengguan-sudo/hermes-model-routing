#!/bin/bash
# OAKAI Document Reader - Portable Server (Linux/macOS/WSL2)
# v2.2 - Fixed UI with Settings page

echo "Starting OAKAI Document Reader..."
echo "Access at: http://localhost:8765"
echo ""

cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found in PATH"
    echo "Please install Python 3.10+ from https://python.org"
    exit 1
fi

# Check Pillow (for image handling in UI)
python3 -c "from PIL import Image" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Note: Pillow not installed (optional)"
    echo "Install with: pip install pillow"
    echo "Continuing without image processing support..."
fi

echo "Server starting..."
python3 doc_reader_onefile.py
