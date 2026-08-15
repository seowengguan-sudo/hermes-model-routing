#!/usr/bin/env python3
"""
Hermes Local Document Reader Agent
===================================
A self-contained Python script that reads PDF, CSV, Excel, Word, PPT, RTF,
images, and text files entirely locally — no external LLM/API required.

This version is designed to be invoked from Hermes' `execute_code` tool.
It auto-detects the file type and uses the appropriate local library to
extract text, tables, metadata, and rendered page images.

Usage from Hermes execute_code:
    from hermes_tools import read_file, terminal
    # Or just call this script directly:
    result = terminal("python3 /opt/data/doc_reader_agent_runner.py /path/to/file.pdf --json")

Supported formats:
  PDF        → pypdf (text) + pymupdf (tables/rendering) + pdfplumber (tables)
  Excel      → openpyxl (.xlsx/.xlsm) + xlrd (.xls)
  CSV        → built-in csv module
  Word       → python-docx (.docx) + striprtf (.doc)
  PowerPoint → python-pptx (.pptx/.ppt)
  RTF        → striprtf
  Images     → Pillow (metadata) + local Vision model via vision_analyze
  Text       → built-in read_file (any text-based format)

All libraries installed in /opt/data/.venv-docreader/
"""

import json
import os
import sys

# Ensure the docreader venv packages are importable
VENV_SITE = "/opt/data/.venv-docreader/lib/python3.13/site-packages"
if VENV_SITE not in sys.path:
    sys.path.insert(0, VENV_SITE)

# Import and run the main agent
exec(open("/opt/data/doc_reader_agent.py").read().replace(
    'PROJECT_ROOT = "/opt/hermes"',
    'PROJECT_ROOT = "/opt/hermes"'
))

if __name__ == "__main__":
    sys.exit(main())
