#!/usr/bin/env python3
"""Rebuild portable ZIP with self-contained path logic"""
import zipfile, os, shutil
from pathlib import Path

zip_path = "/opt/data/workspace/Samples/poc_reader_windows_portable.zip"

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    # Main app from project (correct path logic)
    zf.write("/opt/data/projects/doc_reader/doc_reader_onefile.py", "doc_reader_onefile.py")
    
    # Portable launcher files
    source_files = [
        "/opt/data/projects/doc_reader/workspace/portable/run.bat",
        "/opt/data/projects/doc_reader/workspace/portable/run.sh",
        "/opt/data/projects/doc_reader/workspace/portable/start_silent.vbs",
    ]
    for f in source_files:
        if os.path.exists(f):
            zf.write(f, Path(f).name)
    
    # README from Samples
    readme_path = "/opt/data/workspace/Samples/README.txt"
    if not os.path.exists(readme_path):
        # Generate README
        readme_content = """OAKAI Document Reader - Windows Portable Edition v2.3
=====================================================

SELF-CONTAINED: No installation required. All files stay together.

Quick Start:
  1. Extract this ZIP to C:\\doc_reader_portable\\
  2. Run start_silent.vbs (double-click it)
  3. Open http://localhost:8765 in your browser

Files:
  doc_reader_onefile.py  - Main application (all-in-one)
  run.bat               - Console launch (for debugging)
  run.sh                - Linux launch
  start_silent.vbs      - Silent Windows launch (pythonw.exe)
  README.txt            - This file

For Windows updates:
  1. Replace doc_reader_onefile.py with new version
  2. Click restart button in UI
  3. Page auto-reloads

Features:
  - 10 redaction categories (PII + Business Sensitive)
  - Live restart button for seamless updates
  - Self-contained data folder (no paths outside script dir)
  - Fully local - zero external calls

"""
        zf.writestr("README.txt", readme_content)
    else:
        zf.write(readme_path, "README.txt")

# Also update Files/ source directory
files_dir = Path("/opt/data/workspace/Samples/Files")
files_dir.mkdir(exist_ok=True)
shutil.copy2("/opt/data/projects/doc_reader/doc_reader_onefile.py", files_dir / "doc_reader_onefile.py")

# Verify
with zipfile.ZipFile(zip_path, 'r') as zf:
    names = sorted(zf.namelist())
    print(f"ZIP rebuilt: {len(names)} files ({os.path.getsize(zip_path):,} bytes)")
    for name in names:
        info = zf.getinfo(name)
        print(f"  {name} ({info.file_size:,} bytes)")

print("✅ Files/doc_reader_onefile.py updated with self-contained logic")
