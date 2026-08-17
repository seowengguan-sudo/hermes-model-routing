# Self-Contained Project Migration

## When to Use
Restructuring an application from a flat directory layout into a self-contained project directory (e.g., `/opt/data/projects/<app_name>/`).

## Safe Migration Pattern (4 phases)

### Phase 1: Path Abstraction
- Analyze all hardcoded paths in scripts, Python files, and cron jobs
- Create a central path config file or use dynamic path detection
- Document all hardcoded `/opt/data/...` paths that scripts depend on

### Phase 2: Script Updates
- Update cron job scripts to use new paths
- Test each script independently before relying on cron execution
- Update auto_git_push.sh, cleanup.sh, and other automation scripts

### Phase 3: File Migration
- Copy all files to new structure
- Verify file integrity (checksums)
- Test from new location before stopping old process

### Phase 4: Switchover
- Stop server from old location
- Start server from new location
- Verify all endpoints work (health, upload, settings, documents)
- Update .gitignore for new paths
- Commit and push to GitHub

## Key Techniques

### Dynamic Path Detection (Python)
```python
SCRIPT_DIR = Path(__file__).parent.resolve()
if "projects/doc_reader" in str(SCRIPT_DIR):
    DATA_DIR = SCRIPT_DIR / "data"  # Project-local
elif "opt/data" in str(SCRIPT_DIR):
    DATA_DIR = Path("/opt/data/data")  # Container
else:
    DATA_DIR = SCRIPT_DIR / "data"  # Local portable
```

### Venv Path Resolution
```python
_VENV_CANDIDATES = [
    SCRIPT_DIR.parent / ".venv-docreader" / "lib" / f"python3.{sys.version_info.minor}" / "site-packages",
    SCRIPT_DIR / ".venv-docreader" / "lib" / f"python3.{sys.version_info.minor}" / "site-packages",
]
VENV_SITE_PACKAGES = str(next((p for p in _VENV_CANDIDATES if p.exists()), ""))
```

## Pitfalls
- Don't break running server during migration
- Update ALL path references in scripts
- Verify data file counts match between old and new locations
- Test all API endpoints after switchover
- The `opt/data` string check catches nested paths — add explicit project check first