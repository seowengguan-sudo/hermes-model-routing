#!/usr/bin/env python3
"""
.hermes_run_cache.py
Ensures the Hermes Python runtime caches installed packages persistently.

This prevents the slowdown caused by recreating venvs or reinstalling
reportlab/pypdf on every job invocation.

Usage:
    source <(python3 /opt/data/.hermes_run_cache.py --bash-hook)
    # Or programmatically:
    from hermes_run_cache import get_runtime_python
    py = get_runtime_python()
"""
import os, sys, subprocess, json
import venv as venv_module

CACHE_DIR = "/tmp/hermes-runs/pdf-runtime"
VENV_DIR = os.path.join(CACHE_DIR, "venv")
PKG_CACHE = os.path.join(CACHE_DIR, "packages.json")
SKILL_CACHE = os.path.join(CACHE_DIR, "compiled_skills")

REQUIRED_PACKAGES = ["reportlab>=4.2.0", "pypdf>=5.1.0"]
OPTIONAL_PACKAGES = []

def ensure_runtime():
    """Create or reuse a persistent venv with required packages."""
    os.makedirs(CACHE_DIR, exist_ok=True)

    # Reuse venv if it exists
    python_bin = os.path.join(VENV_DIR, "bin", "python")
    if not os.path.exists(python_bin):
        print("[runtime] Creating persistent venv...", file=sys.stderr)
        venv_module.create(VENV_DIR, with_pip=True)

    # Install packages if not cached
    if not os.path.exists(PKG_CACHE):
        _install_packages(python_bin)
    else:
        try:
            installed = json.loads(open(PKG_CACHE).read())
            if set(installed) != set(REQUIRED_PACKAGES):
                _install_packages(python_bin)
        except Exception:
            _install_packages(python_bin)

    return python_bin

def _install_packages(python_bin):
    pip = os.path.join(os.path.dirname(python_bin), "pip")
    subprocess.run([pip, "install"] + REQUIRED_PACKAGES + OPTIONAL_PACKAGES, check=True)
    with open(PKG_CACHE, "w") as f:
        json.dump(REQUIRED_PACKAGES, f)
    print(f"[runtime] Packages cached to {PKG_CACHE}", file=sys.stderr)

def get_runtime_python():
    """Return path to the cached Python interpreter with all dependencies."""
    py = ensure_runtime()
    return py

def bash_hook():
    py = get_runtime_python()
    print(f"export HERMESES_PYTHON={py}")
    print(f"export PATH=$(dirname {py}):$PATH")
    print(f"echo '[runtime] Using persistent venv: {py}'")

if __name__ == "__main__":
    if "--bash-hook" in sys.argv:
        bash_hook()
    else:
        py = get_runtime_python()
        print(py)
