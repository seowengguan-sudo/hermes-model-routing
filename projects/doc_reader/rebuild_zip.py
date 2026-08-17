#!/usr/bin/env python3
"""Rebuild portable ZIP"""
import zipfile
from pathlib import Path

source_dir = Path("/opt/data/workspace/Samples/Files")
zip_path = Path("/opt/data/workspace/Samples/poc_reader_windows_portable.zip")

source_files = [
    "doc_reader_onefile.py",
    "run.bat",
    "run.sh",
    "start_silent.vbs",
    "restart_helper.vbs",
    "README.txt"
]

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    # Add main server file from project
    zf.write(Path("/opt/data/projects/doc_reader/doc_reader_onefile.py"), "doc_reader_onefile.py")
    
    # Add launcher files
    for fname in ["run.bat", "run.sh", "start_silent.vbs", "restart_helper.vbs", "README.txt"]:
        src = source_dir / fname
        if src.exists():
            zf.write(src, fname)
        else:
            print(f"WARNING: {fname} not found")

# Verify
with zipfile.ZipFile(zip_path, 'r') as z:
    print(f"ZIP rebuilt with {len(z.infolist())} files:")
    for info in z.infolist():
        print(f"  {info.filename:30s} {info.file_size:>8,}")
