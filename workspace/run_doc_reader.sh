#!/bin/bash
# Run this script from WSL2 terminal (NOT inside Docker container)
# It will start the document reader server accessible from Windows browser

echo "Starting Hermes Document Reader..."
echo "Access from Windows browser at: http://localhost:8765"
echo "To stop: Ctrl+C"
echo ""

exec /opt/data/.venv-docreader/bin/python3 /opt/data/doc_reader_tk.py --api-server 8765
