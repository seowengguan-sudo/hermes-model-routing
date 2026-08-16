OAKAI Document Reader - System Architecture Overview
=====================================================

This document describes the complete file/directory structure of the OAKAI
Document Reader system, what each file does, and which files are needed
vs. legacy/debug artifacts that can be removed.

## ARCHITECTURE OVERVIEW (ASCII)

```
┌─────────────────────────────────────────────────────────────┐
│                    OAKAI DOCUMENT READER                     │
│                    v2.3 - POC Edition                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           USER INTERFACE (Browser)                  │    │
│  │         http://localhost:8765                       │    │
│  │                                                     │    │
│  │  Header:                                           │    │
│  │    OAKAI Logo + Title                              │    │
│  │    [🔄 Refresh] [🔁 Restart] [⚙️ Settings]    │    │
│  │                                                     │    │
│  │  Document List  →  Uploads Section → Results      │    │
│  │  (GET /documents)   (POST /upload)    (fetch)      │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          │ HTTP (JSON + File uploads)          │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           SERVER CORE (doc_reader_onefile.py)       │    │
│  │                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │    │
│  │  │   Route      │  │  File        │  │ Settings  │ │    │
│  │  │  Handler     │  │  Extractors   │  │ Manager   │ │    │
│  │  │              │  │              │  │           │ │    │
│  │  │ /upload      │  │ - extract_   │  │ load/save │ │    │
│  │  │ /documents   │  │   text()     │  │ settings  │ │    │
│  │  │ /settings    │  │ - PDF: pypdf │  │ to JSON   │ │    │
│  │  │ /restart     │  │ - DOCX: docx │  │           │ │    │
│  │  │ /health      │  │ - XLSX: xlrd │  │ Default   │ │    │
│  │  └──────────────┘  │ - fallback   │  │ policy    │ │    │
│  │                     │   raw decode  │  │ from      │ │    │
│  │  ┌──────────────┐  └──────────────┘  │ SECURITY_ │ │    │
│  │  │  Redaction   │                      │ POLICY    │ │    │
│  │  │   Engine     │                      └───────────┘ │    │
│  │  │              │                                      │
│  │  │ - Priority   │  ┌───────────────────────────────┐  │
│  │  │   ordered    │  │     RUNTIME DATA DIRECTORY    │  │
│  │  │   patterns  │  │     (DATA_DIR = /data/)       │  │
│  │  │ - PII first  │  │                               │  │
│  │  │ - Business   │  │  uploads/        (input)     │  │
│  │  │   next       │  │  documents_safe/  (output)   │  │
│  │  │ - Reversible │  │  redaction_maps/ (mapping)   │  │
│  │  │   mapping    │  │  redaction_settings.json     │  │
│  │  └──────────────┘  └───────────────────────────────┘  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        LAUNCHER & RESTART MECHANISM                │    │
│  │                                                     │    │
│  │  start_silent.vbs → pythonw.exe → doc_reader_onefile│    │
│  │              │                                      │    │
│  │              │ [Restart button clicked in browser]  │    │
│  │              ▼                                      │    │
│  │  /restart endpoint → restart_helper.vbs             │    │
│  │              │                                      │    │
│  │              │ (kills old pythonw.exe, launches new)│    │
│  │              └───────────────────────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## FILE-BY-FILE BREAKDOWN

### Core Application Files (ACTIVE - in /opt/data/)

| File | Path | Size | Purpose |
|------|------|------|---------|
| `doc_reader_onefile.py` | `/opt/data/doc_reader_onefile.py` | 60.8 KB | **Main application** — all-in-one server with HTML UI, redaction engine, file extractors, settings manager, and restart endpoint. This is the single source of truth. |
| `deploy_doc_reader.sh` | `/opt/data/deploy_doc_reader.sh` | 7.2 KB | Deployment script — sets up the app, creates symlinks, configures access |

### Runtime Data Directory (AUTO-CREATED at `data/` next to script)

| Subdirectory/File | Path | Purpose |
|-------------------|------|---------|
| `data/uploads/` | `/opt/data/data/uploads/` | Uploaded files (input documents) |
| `data/documents_safe/` | `/opt/data/data/documents_safe/` | Redacted output documents (JSON with safe text) |
| `data/redaction_maps/` | `/opt/data/data/redaction_maps/` | Variable↔Original mapping files (stored locally, never exposed via API) |
| `data/redaction_settings.json` | `/opt/data/data/redaction_settings.json` | User settings (which categories to redact, custom regex patterns) |

### Python Virtual Environment

| Directory | Path | Purpose |
|-----------|------|---------|
| `.venv-docreader/` | `/opt/data/.venv-docreader/` | Python venv with pypdf, python-docx, openpyxl, python-pptx, Pillow for file extraction |

### Portable Package Files (in workspace/Samples/)

| File | Path | Purpose |
|------|------|---------|
| `poc_reader_windows_portable.zip` | `/opt/data/workspace/Samples/poc_reader_windows_portable.zip` | **Production portable package** (6 files, flat structure) |
| `doc_reader_onefile.py` | `/opt/data/workspace/Samples/Files/doc_reader_onefile.py` | Backup copy used in ZIP (same as main) |
| `run.bat` | `/opt/data/workspace/Samples/Files/run.bat` | Windows console launcher |
| `run.sh` | `/opt/data/workspace/Samples/Files/run.sh` | Linux/macOS launcher |
| `start_silent.vbs` | `/opt/data/workspace/Samples/Files/start_silent.vbs` | Silent Windows launcher (pythonw.exe) |
| `restart_helper.vbs` | (embedded in ZIP) | Restart helper — kills + relaunches server |

### System Scripts (in /opt/data/scripts/)

| File | Purpose |
|------|---------|
| `auto_git_push.sh` | Daily cron job — commits + pushes source files to GitHub |
| `cleanup.sh` | Monthly cleanup — removes old venvs, caches, temp files |
| `gateway_watchdog.sh` | Every-2-min check — restarts gateway if s6 down |
| `cleanup-policy.sh` | Defines what gets cleaned (disk usage thresholds) |

### Knowledge Base

| File/Directory | Purpose |
|----------------|---------|
| `knowledge/data_security_governance_policy.md` | Data Security Policy — defines redaction categories |
| `knowledge/INDEX.md` | Knowledge base index |
| `knowledge/by_industry/` | Industry-specific knowledge (solar energy, mentor, strategy) |
| `knowledge/templates/` | Templates for knowledge generation |

### Configuration Files

| File | Purpose |
|------|---------|
| `config.yaml` | Hermes gateway configuration (auth, ports, models) |
| `.env` | Environment variables (gitignored) |
| `requirements.txt` | Python dependencies |

## LEGACY/DEBUG ARTIFACTS (CAN BE REMOVED)

### Root /opt/data/ - Old Monolithic Approach

These files were the original monolithic doc_reader development structure. All functionality is now consolidated into `doc_reader_onefile.py`:

| File | Size | Why Remove |
|------|------|------------|
| `doc_reader_agent.py` | 23 KB | Superseded by `doc_reader_onefile.py` |
| `doc_reader_desktop.py` | 22 KB | Superseded by `doc_reader_onefile.py` |
| `redaction_engine.py` | 14 KB | Engine logic merged into `doc_reader_onefile.py` |
| `safe_format.py` | 9 KB | Formatting logic merged into `doc_reader_onefile.py` |

### workspace/Samples/ - Test/Scratch Files

| File | Size | Why Remove |
|------|------|------------|
| `doc_reader_agent.py` | 24 KB | Duplicate of root, superseded |
| `doc_reader_desktop.py` | 22 KB | Duplicate of root, superseded |
| `doc_reader_tk.py` | 17 KB | Old tkinter UI experiment, replaced by web UI |
| `redaction_engine.py` | 14 KB | Duplicate of root, superseded |
| `safe_format.py` | 9 KB | Duplicate of root, superseded |
| `doc_reader_agent.zip` | 29 KB | Old agent archive |
| `doc_reader_agent_full.zip` | 409 MB | **Massive** old agent archive (largest single file) |
| `test18.png` | 368 KB | Test screenshot |
| `test23.png` | 412 KB | Test screenshot |
| `current_ui.html` | 12 KB | Stale UI snapshot |
| `cmd.png` (in Files/) | 80 KB | Screenshot used for debugging |
| `deploy_doc_reader.sh` | 7 KB | Duplicate of root |
| `redaction_engine.py` | 14 KB | Duplicate |
| `requirements.txt` | 455 B | Minimal requirements (can keep for reference) |

### Orphaned Runtime Data

| Directory | Size | Why Remove |
|-----------|------|------------|
| `/opt/data/documents_safe/` | 188 KB (39 files) | Old runtime location — current path is `/opt/data/data/documents_safe/` |
| `/opt/data/redaction_maps/` | 340 KB (84 files) | Old runtime location — current path is `/opt/data/data/redaction_maps/` |
| `workspace/Samples/RESULT/` | 184 KB | Debug/test output directory |
| `workspace/Samples/Files/README.txt` | 1.4 KB | Old README (superseded by ZIP's README) |

### Backup/Redundant

| File | Size | Why Remove |
|------|------|------------|
| `doc_reader_windows_portable.zip` | 17 KB | Previous version, replaced by `poc_reader_windows_portable.zip` |
| `Files/doc_reader_portable_with_reset.zip` | 20 KB | Intermediate version, merged into final ZIP |

## DIRECTORY TREE (after cleanup)

```
/opt/data/
├── doc_reader_onefile.py          ← MAIN APP (60.8KB, 1520 lines)
├── deploy_doc_reader.sh           ← Deployment script
├── data/                          ← Runtime data (auto-created)
│   ├── uploads/                   ← Input files
│   ├── documents_safe/            ← Redacted output
│   ├── redaction_maps/            ← Reversible mappings
│   └── redaction_settings.json    ← Settings config
├── .venv-docreader/               ← Python venv (pypdf, openpyxl, etc.)
├── scripts/
│   ├── auto_git_push.sh           ← Daily git push
│   ├── cleanup.sh                 ← Monthly cleanup
│   ├── gateway_watchdog.sh        ← Gateway health check
│   └── cleanup-policy.sh          ← Cleanup rules
├── knowledge/                     ← Knowledge base
│   ├── data_security_governance_policy.md  ← Redaction categories
│   └── by_industry/...
├── workspace/Samples/
│   ├── poc_reader_windows_portable.zip  ← PRODUCTION PORTABLE PACKAGE
│   └── Files/
│       ├── doc_reader_onefile.py  ← Source for ZIP
│       ├── run.bat
│       ├── run.sh
│       ├── start_silent.vbs
│       └── restart_helper.vbs
├── config.yaml, .env, requirements.txt
└── backups/ (gitignored)
```
