#!/usr/bin/env python3
"""
consolidated_summary.py — delegates to canonical OAKAI skill template.

IMPORTANT: Uses /opt/data/skills/PDF/oakai_report_generator.py ONLY.
Never writes ad-hoc PDF layout code. Always inherits brand styling.
"""
import sys
sys.path.insert(0, '/opt/data/skills/PDF')

from oakai_report_generator import build_document, section_header, status_table, checklist, kv_callout_box, hr, styles, DOC_CLASSIFICATION, DOC_DATE, PREPARED_FOR
from reportlab.platypus import Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.units import mm

OUTPUT_PATH = "/opt/data/workspace/Consolidated_Knowledge_Summary_2026-08-12.pdf"

# ── Content: All sections from your knowledge base (Aug 1–12, 2026) ──
content_story = []

# Executive Overview
content_story += section_header("01", "Executive Overview", "Phase 1 complete — autonomous agent system live")
content_story.append(Paragraph(
    "Mission: Build enterprise-grade AI consultancy delivering operational "
    "efficiency via autonomous agents. Target clients: manufacturing, retail, "
    "and F&B operations with legacy ERP pain points.",
    styles["Body"]
))

content_story += checklist([
    "Mission: Build enterprise-grade AI consultancy delivering operational efficiency via autonomous agents.",
    "Target Clients: Manufacturing, retail, F&B operations with legacy ERP pain points.",
    "Budget Posture: Free-tier first (Nous Portal, OpenRouter, local LLMs); paid APIs require explicit approval.",
    "Technical Stack: Python 3.13 + ReportLab (PDF), pypdf (extraction), uv venv management.",
])

# Mentor Program
content_story += section_header("02", "Mentor Program", "5 concepts mastered / 9 total")
content_story += checklist([
    "Started 3x/day cadence (07:00/15:00/22:00 MYT)",
    "Completed: LLM fundamentals, agent workflows, guardrails, tool-use vs agentic",
    "Current Focus: Evals, confusion matrices, golden sets",
    "Mastery Level: 6/9 concepts mastered",
])

content_story.append(kv_callout_box("Mentor Key Insight", [
    "Auto-switch to operational mode: mentor shipped golden_v1.csv scaffold "
    "instead of teasing next concept after detecting execution gap."
]))

# PENSOLAR Case Study
content_story += section_header("03", "PENSOLAR Case Study", "Solar project management automation")
content_story.append(Paragraph(
    "<b>Domain:</b> Solar energy project management in Malaysia<br/>"
    "<b>Pain Points:</b> Manual permit tracking, crew scheduling conflicts<br/>"
    "<b>Solution:</b> AI-driven anomaly flagging in existing ERP workflows<br/>"
    "<b>Key Insight:</b> Start tool-use + routing before full autonomy",
    styles["Body"]
))

# Marketing Engine
content_story += section_header("04", "Marketing Engine", "Daily cadence active")
content_story += checklist([
    "Daily briefs Mon-Sat via marketing-advisor-daily cron",
    "Target Personas: Manufacturing Ops, Retail Store Managers, F&B Kitchen Leads",
    "Channels: LinkedIn organic, landing page UVP, lead magnets",
    "Content Cadence: 3 posts/week case-driven storytelling",
])

# COO Strategy
content_story += section_header("05", "COO Strategy", "Week 1 executed, W2 preview ready")
content_story += checklist([
    "Week 1 Objectives: Legal entity setup, domain registration, bank account prep",
    "Budget: RM200 core (SSM + domain + survey), optional buffer RM45",
    "Risks: SSM name rejection, domain taken, free-tier throttling mitigated",
    "Success Metrics: 50+ LinkedIn followers, 3 quality posts, C5 scaffold running",
])

# System Architecture
content_story += section_header("06", "System Architecture", "5 crons pinned + autonomous recovery")
content_story += checklist([
    "5 active crons all pinned to tencent/hy3:free (nous)",
    "Skills auto-load via /opt/data/skills/PDF/ path injection",
    "Workspace cleanup auto-deletes files older than 14 days",
    "INDEX.md tracks all outputs with direct links",
    "Auto-backfill + pin enforcement on every restart",
])

# Progress Tracking
content_story += section_header("07", "Progress Tracking", "Mastery + milestones")
progress_rows = [
    ["Concept", "Status", "Score"],
    ["LLM Fundamentals", "Mastered", "N/A"],
    ["Agent Workflows", "Mastered", "N/A"],
    ["Guardrails/RBAC", "Mastered", "N/A"],
    ["Tool vs Agentic", "Mastered", "N/A"],
    ["Confusion Matrix", "Mastered", "3/3"],
    ["Golden Set Eval", "Scaffold built", "Pending audit"],
]
content_story.append(KeepTogether([
    status_table(progress_rows, col_widths=[50*mm, 30*mm, 25*mm]),
]))

content_story.append(PageBreak())

# TOC entries (manual estimate — rebuild after first pass to correct numbers)
toc_entries = [
    ("01", "Executive Overview", "3"),
    ("02", "Mentor Program", "4"),
    ("03", "PENSOLAR Case Study", "5"),
    ("04", "Marketing Engine", "6"),
    ("05", "COO Strategy", "7"),
    ("06", "System Architecture", "8"),
    ("07", "Progress Tracking", "9"),
]

# Call canonical builder
build_document(
    content_story=content_story,
    out_path=OUTPUT_PATH,
    doc_title="Consolidated Knowledge Summary",
    doc_subtitle="OAKAI AI Solutions Provider Journey — Aug 2026",
    doc_date=DOC_DATE,
    doc_ref="KNOWLEDGE-SUM-0812-V1",
    prepared_for=PREPARED_FOR,
    classification=DOC_CLASSIFICATION,
    toc_entries=toc_entries
)

print(f"✓ Generated: {OUTPUT_PATH}")
print(f"  Pages: 9 estimated (TOC may need correction pass)")
print(f"  Classification: {DOC_CLASSIFICATION}")
