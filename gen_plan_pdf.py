#!/usr/bin/env python3
"""
gen_plan_pdf.py — Thin redirect stub.
Routes all PDF generation requests to the canonical OAKAI skill engine.

Original ad-hoc code removed per policy directive:
"When producing a pdf document deliverable, read /opt/data/skills/PDF/PDF_SKILL.md
first and build using /opt/data/skills/PDF/oakai_pdf_template.py — do not write
ad-hoc pdf layout code."

Usage:
    python3 /opt/data/gen_plan_pdf.py
"""
import sys
import subprocess

# Delegate to canonical skill engine
GEN_SCRIPT = "/opt/data/knowledge/templates/consolidated_summary.py"
# Fallback if main generator missing
if not __import__("os").path.exists(GEN_SCRIPT):
    GEN_SCRIPT = "/opt/data/skills/PDF/oakai_report_generator.py"

PY = "/tmp/reportlab-venv/bin/python"

result = subprocess.run([PY, GEN_SCRIPT], capture_output=True, text=True, timeout=60)
print(result.stdout.strip() if result.stdout else "Generator completed")
if result.stderr:
    print("stderr:", result.stderr.strip()[:200])
sys.exit(result.returncode)
