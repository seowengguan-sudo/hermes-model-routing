# Venv pip install workaround for uv-created venvs + spaCy model install

## Problem
When you create a venv with `uv venv`, it does NOT include `pip` by default. If you then try:

```bash
/opt/data/.venv-docreader/bin/python3 -m pip install ...
```

You get `No module named 'pip'`. This affects installing spaCy models, which require pip:

```bash
# This FAILS in a uv-created venv:
/opt/data/.venv-docreader/bin/python3 -m spacy download en_core_web_sm
# → ModuleNotFoundError: No module named 'pip'
```

## Fix (two methods)

### Method A: Install click first, then spacy model via spacy download
```bash
# Step 0: Install click (spacy CLI dependency)
uv pip install --python /path/to/venv/bin/python3 click

# Step 1: Install pip into the uv venv
uv pip install --python /path/to/venv/bin/python3 pip

# Step 2: Now spacy model install works
/path/to/venv/bin/python3 -m spacy download en_core_web_sm
```

### Method B (preferred): Direct wheel install via uv pip
```bash
# Install the model wheel directly — bypasses pip and spacy CLI entirely
uv pip install --python /path/to/venv/bin/python3 \
  https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

## Critical Pitfall: spacy download installs to WRONG venv
Even when using the correct venv's Python, `spacy download en_core_web_sm` may attempt to write to a different venv's site-packages directory (e.g., `/opt/hermes/.venv/lib/python3.13/...` instead of `/opt/data/.venv-docreader/lib/python3.13/...`).

**Symptom:**
```
error: Failed to install: en_core_web_sm-3.8.0-py3-none-any.whl
  Caused by: Failed to create directory `/opt/hermes/.venv/lib/python3.13/site-packages/`
  Caused by: Permission denied
```

**Root cause:** The `spacy` CLI binary may be invoked from a different venv's bin/ directory, causing it to resolve to that venv's site-packages.

**Workaround:** Always use Method B (direct wheel URL with `uv pip install`) to avoid the spacy CLI entirely. If you must use Method A, verify the model is installed in the correct location:

```bash
/path/to/venv/bin/python3 -c "import spacy; print(spacy.load('en_core_web_sm').path)"
```

## Note
This only affects spaCy models and packages that are installed via Python scripts requiring pip. Regular packages work fine with `uv pip install` directly.