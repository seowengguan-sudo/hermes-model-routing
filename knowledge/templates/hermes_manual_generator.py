#!/usr/bin/env python3
"""
hermes_manual_generator.py
Builds the official 'Hermes Agent Operations Manual' using the canonical OAKAI skill template.
Usage: python3 hermes_manual_generator.py
"""
import sys
sys.path.insert(0, '/opt/data/skills/PDF')

from oakai_pdf_template import (
    build_document, section_header, status_table, checklist,
    kv_callout_box, hr, styles, TEAL_DARK, TEAL, GOLD, CHARCOAL
)
from reportlab.platypus import Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.units import mm

# ── Constants ──
DOC_DATE = "2026-08-12"
DOC_CLASSIFICATION = "OAKAI Confidential"
PREPARED_FOR = "Weng Guan / Founder, OAKAI SDN BHD"

OUTPUT_PATH = "/opt/data/workspace/HERMES-Agent-Operations-Manual.pdf"

DOC_TITLE = "Hermes Agent Operations Manual"
DOC_SUBTITLE = "A Complete Guide to Operating the OAKAI Autonomous AI Platform"
DOC_REF = "HERMES-MANUAL-V1-0812"

content_story = []

# ─── Section 01: Executive Brief ───
content_story += section_header("01", "Executive Brief", "Purpose & Scope")
content_story.append(Paragraph(
    "This manual provides step-by-step instructions for operating the Hermes Agent "
    "platform — an autonomous AI agent orchestrator used to run scheduled tasks, "
    "generate reports, manage knowledge bases, and coordinate machine learning "
    "workflows across hybrid cloud and local environments.",
    styles["Body"]
))

content_story.append(kv_callout_box("Key Capabilities", [
    "Autonomous task scheduling via cron jobs<br/>",
    "Multi-model routing (free-tier first: Nous Portal, OpenRouter, NVIDIA NIM)<br/>",
    "Skill-based modular execution framework<br/>",
    "Persistent memory + indexed knowledge bases<br/>",
    "Approval-gated high-cost operations<br/>",
    "Local stack fallback when cloud egress is blocked"
]))

content_story.append(Paragraph(
    "Designed for solo operators, startup teams, and enterprise automation engineers "
    "who want reliable AI agents without vendor lock-in or runaway costs.",
    styles["Body"]
))

# ─── Section 02: System Overview ───
content_story += section_header("02", "System Overview", "Architecture & Components")
content_story.append(PageBreak())

content_story.append(Paragraph("The Hermes Agent platform consists of four core layers:", styles["H2"]))
content_story += checklist([
    "<b>Terminal Layer</b> — Direct shell access for debugging, file ops, and ad-hoc commands",
    "<b>TUI Dashboard</b> — Interactive session management with live status monitoring",
    "<b>Cron Engine</b> — Scheduled autonomous jobs with model pinning and drift guard",
    "<b>Skill Framework</b> — Modular plugins for PDF generation, knowledge indexing, etc."
])

content_story.append(Paragraph("Current stack as of 2026-08-12:", styles["H3"]))
overview_rows = [
    ["Component", "Provider", "Model/Version"],
    ["Interactive Model", "Nous Portal", "poolside/laguna-s-2.1:free"],
    ["Cron Jobs", "Nous Portal", "tencent/hy3:free (drift-pinned)"],
    ["Vision", "NVIDIA", "nemotron-nano-12b-v2-vl"],
    ["PDF Engine", "ReportLab", "5.0.0 (via venv)"],
    ["Knowledge Store", "Markdown + PyPDF", "Local /opt/data/knowledge/"]
]
content_story.append(KeepTogether([
    status_table(overview_rows, col_widths=[50*mm, 45*mm, 55*mm]),
]))

# ─── Section 03: Interface Tour ───
content_story += section_header("03", "Interface Tour", "Navigating the Dashboard")
content_story.append(Paragraph("Hermes exposes three primary interfaces:", styles["H2"]))

content_story += section_header("03A", "Terminal Commands", "CLI control layer")
content_story += checklist([
    "`hermes cron list` — View all scheduled jobs",
    "`hermes cron run [id]` — Execute a job immediately",
    "`hermes cron edit [id] --model X` — Repin a drifted cron job",
    "`hermes status` — Full environment health check",
    "`hermes tools list` — See enabled/disabled tool integrations"
])

content_story += section_header("03B", "TUI Dashboard", "Interactive session view")
content_story.append(Paragraph("Access via `hermes` (no subcommand). Shows:", styles["Body"]))
content_story += checklist([
    "Active cron job queue (next runs, last execution)",
    "Gateway connection status (web tools, image gen, TTS/STT)",
    "Model/provider availability and rate limits",
    "Session-level memory usage and index health"
])

content_story += section_header("03C", "File System Layout", "Where everything lives")
fs_rows = [
    ["Path", "Purpose"],
    ["/opt/data/knowledge/", "Living knowledge base + logs"],
    ["/opt/data/workspace/", "Generated deliverables + INDEX.md"],
    ["/opt/data/skills/PDF/", "Canonical PDF design system"],
    ["/opt/data/cron/jobs.json", "Cron job configurations"],
    ["/opt/data/memories/", "Persistent memory + USER profile"]
]
content_story.append(KeepTogether([
    status_table(fs_rows, col_widths=[60*mm, 90*mm]),
]))

# ─── Section 04: Daily Operations ───
content_story += section_header("04", "Daily Operations", "Routine Management Tasks")
content_story.append(PageBreak())

content_story += section_header("04A", "Running Crons", "Scheduling & Monitoring")
content_story += checklist([
    "Check next scheduled runs via `hermes cron list`",
    "Verify model pins: all crons must show 'tencent/hy3:free'",
    "Inspect output files in knowledge/[stream]/[date].md",
    "Confirm INDEX.md auto-appends new entries daily",
    "Review RUN_LOG.md for error traces or skipped steps"
])

content_story += section_header("04B", "Updating INDEX.md", "Keeping the map fresh")
content_story.append(Paragraph(
    "The workspace INDEX.md is the single source of truth for all deliverables. "
    "It auto-appends entries from each cron run. Manual review recommended weekly.",
    styles["Body"]
))

content_story += section_header("04C", "Regenerating PDFs", "Using canonical templates")
content_story += checklist([
    "Always use oakai_report_generator.py (not ad-hoc scripts)",
    "Output goes to /opt/data/workspace/[name].pdf",
    "Footer: 'OAKAI Confidential | Page N | Internal Use Only'",
    "TOC must match actual page numbers after first build",
    "Tables wrapped in KeepTogether to prevent orphaned headers"
])

# ─── Section 05: Safety Protocols ───
content_story += section_header("05", "Safety Protocols", "Approval Gates & Cost Control")

content_story += section_header("05A", "Approval Gate", "Preventing unauthorized actions")
content_story.append(Paragraph(
    "All crons operate in <b>read-only + local-write</b> mode. Any action requiring:",
    styles["Body"]
))
content_story += checklist([
    "External API calls beyond free-tier quotas",
    "Financial transactions or budget changes",
    "File modifications outside /opt/data/",
    "Spawning new subagents recursively",
])

content_story.append(Paragraph(
    "Must trigger interactive approval via `/approve` flag in chat session.",
    styles["Body"]
))

content_story += section_header("05B", "Budget Guardrails", "Free-tier enforcement")
budget_rows = [
    ["Action", "Max Daily Budget", "Approval Required"],
    ["Cloud LLM calls", "50/day (OpenRouter)", "Yes (above free tier)"],
    ["Local LLM inference", "Unlimited", "No"],
    ["Image generation (FAL)", "10/day", "No (free tier)"],
    ["Browser automation", "30/day", "No (free tier)"],
    ["New cron job creation", "$0", "Yes (manual review)"]
]
content_story.append(KeepTogether([
    status_table(budget_rows, col_widths=[55*mm, 35*mm, 45*mm]),
]))

# ─── Section 06: Troubleshooting ───
content_story += section_header("06", "Troubleshooting", "Common Errors + Fixes")

content_story += section_header("06A", "Model Drift / Cron Failure")
content_story.append(Paragraph(
    "<b>Symptom:</b> Cron shows 'Script Error' or runs without output<br/>"
    "<b>Cause:</b> Model/provider drift — global config changed but cron wasn't repinned<br/>"
    "<b>Fix:</b> Run `hermes cron edit [id] --model tencent/hy3:free --provider nous`",
    styles["Body"]
))

content_story += section_header("06B", "Egress Blocked")
content_story.append(Paragraph(
    "<b>Symptom:</b> Web search or API call fails silently<br/>"
    "<b>Cause:</b> Cloudflare WAF or DNS blocking on target domain<br/>"
    "<b>Fix:</b> Use local LLM (Qwen2.5-1.5B + bge-m3) as fallback; switch providers<br/>"
    "<b>Workaround:</b> Route through Nous Portal gateway which handles WAF bypass",
    styles["Body"]
))

content_story += section_header("06C", "Missing venv / Python Modules")
content_story.append(Paragraph(
    "<b>Symptom:</b> ImportError: No module named 'reportlab' or similar<br/>"
    "<b>Cause:</b> Virtual environment not activated or reportlab not installed<br/>"
    "<b>Fix:</b> Use `/tmp/reportlab-venv/bin/python` explicitly for PDF generation<br/>"
    "<b>Permanent:</b> Add to PATH or use system-wide install path",
    styles["Body"]
))

# ─── Section 07: Appendices ───
content_story += section_header("07", "Appendices", "Reference Materials")

content_story += section_header("07A", "Appendix A — Cron Job Inventory")
cron_rows = [
    ["Job ID", "Name", "Schedule", "Output Path"],
    ["2b39ab1514d2", "learn-pensolar", "15:00 + 22:00 MYT", "pensolar/logs/"],
    ["3dfaf435889a", "mentor-ai-daily", "07:00 / 11:00 / 15:00 / 19:00", "mentor/daily_notes/"],
    ["75e36f8dd14d", "marketing-advisor-daily", "Mon–Sat 06:00 MYT", "marketing/"],
    ["9dda7d6f3af5", "workspace-cleanup-daily", "10:00 MYT", "Auto: cleanup-policy.conf"],
    ["0ee860f4fb74", "startup-catchup-enforcement", "06:00 daily", "Auto: re-pin + backfill"]
]
content_story.append(KeepTogether([
    status_table(cron_rows, col_widths=[30*mm, 40*mm, 40*mm, 40*mm]),
]))

content_story += section_header("07B", "Appendix B — File Path Map")
content_story.append(Paragraph("All deliverables organized as follows:", styles["Body"]))
path_rows = [
    ["/opt/data/knowledge/mentor/", "AI concept lessons + student progress"],
    ["/opt/data/knowledge/by_industry/solar_energy/pensolar/", "PENSOLAR solar case study"],
    ["/opt/data/knowledge/marketing/", "Daily marketing briefs + LinkedIn guidance"],
    ["/opt/data/knowledge/strategy/", "Sunday COO strategy briefs"],
    ["/opt/data/knowledge/templates/", "Python generators for reports"],
    ["/opt/data/workspace/", "Generated PDFs + INDEX.md manifest"]
]
content_story.append(KeepTogether([
    status_table(path_rows, col_widths=[60*mm, 90*mm]),
]))

# ─── TOC Entries ───
toc_entries = [
    ("01", "Executive Brief", "3"),
    ("02", "System Overview", "4"),
    ("02A", "Terminal Commands", "5"),
    ("02B", "TUI Dashboard", "6"),
    ("02C", "File System Layout", "6"),
    ("03", "Interface Tour", "7"),
    ("03A", "Terminal Commands", "8"),
    ("03B", "TUI Dashboard", "9"),
    ("03C", "File System Layout", "9"),
    ("04", "Daily Operations", "10"),
    ("04A", "Running Crons", "11"),
    ("04B", "INDEX.md Updates", "12"),
    ("04C", "Regenerating PDFs", "12"),
    ("05", "Safety Protocols", "13"),
    ("05A", "Approval Gate", "14"),
    ("05B", "Budget Guardrails", "14"),
    ("06", "Troubleshooting", "15"),
    ("06A", "Model Drift", "16"),
    ("06B", "Egress Blocked", "16"),
    ("06C", "Missing venv", "17"),
    ("07", "Appendices", "18"),
    ("07A", "Cron Job Inventory", "19"),
    ("07B", "File Path Map", "19"),
]

# Build document using canonical skill
build_document(
    content_story=content_story,
    out_path=OUTPUT_PATH,
    doc_title=DOC_TITLE,
    doc_subtitle=DOC_SUBTITLE,
    doc_date=str(DOC_DATE),
    doc_ref=DOC_REF,
    prepared_for="Weng Guan / Founder, OAKAI SDN BHD",
    classification=DOC_CLASSIFICATION,
    toc_entries=toc_entries
)

print(f"✓ Manual generated: {OUTPUT_PATH}")
print(f"  Type: Operations Manual")
print(f"  Pages: ~22")
print(f"  Classification: {DOC_CLASSIFICATION}")
