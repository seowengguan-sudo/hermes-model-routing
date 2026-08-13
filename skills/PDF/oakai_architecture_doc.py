#!/usr/bin/env python3
"""
OAK_Architecture_13AUG2026.py — Generates comprehensive Hermes workspace
architecture documentation as a professional PDF.

Follows EG SEOW preferences:
- Name: EG SEOW (never Weng Guan)
- Professional table borders (full framework)
- Cover page with TEAL_DARK background (template-native)
- Color accents on content pages (header/footer bands)
- Block flow diagrams for architecture visualization
- Layout optimization (fit_table_to_page for proper column sizing)
- Numbering: 1, 2, 3... main topics; (A), (B), (C)... subsections
"""
import sys, os
sys.path.insert(0, '/opt/data/lazy-packages')
sys.path.insert(0, '/opt/data/skills/PDF')

from oakai_pdf_template import (
    build_document, section_header, status_table, checklist,
    kv_callout_box, hr, styles, make_toc, FOOTER_LABEL, BRAND_NAME,
    TEAL_DARK, TEAL, TEAL_LIGHT, GOLD, CHARCOAL, GREY, ROW_ALT, BORDER, WHITE,
    fit_table_to_page, split_large_table, KeepInFrame, PAGE_W, MARGIN
)
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Group, Ellipse, Line

# ── Enhanced styles for large, readable fonts ──
for _name, _style in [
    ("H1_big", ParagraphStyle("H1_big", fontName="Helvetica-Bold", fontSize=22,
        leading=26, textColor=TEAL_DARK, spaceAfter=12)),
    ("H2_big", ParagraphStyle("H2_big", fontName="Helvetica-Bold", fontSize=15,
        leading=19, textColor=TEAL_DARK, spaceBefore=16, spaceAfter=8)),
    ("H3_big", ParagraphStyle("H3_big", fontName="Helvetica-Bold", fontSize=12,
        leading=16, textColor=TEAL, spaceBefore=10, spaceAfter=6)),
    ("Body_big", ParagraphStyle("Body_big", fontName="Helvetica", fontSize=11.2,
        leading=16.8, textColor=CHARCOAL, alignment=TA_JUSTIFY, spaceAfter=8)),
    ("BodySmall_big", ParagraphStyle("BodySmall_big", fontName="Helvetica", fontSize=9.8,
        leading=14, textColor=GREY, spaceAfter=6)),
    ("CellHead_big", ParagraphStyle("CellHead_big", fontName="Helvetica-Bold", fontSize=10,
        leading=13, textColor=WHITE)),
    ("Cell_big", ParagraphStyle("Cell_big", fontName="Helvetica", fontSize=10,
        leading=14, textColor=CHARCOAL)),
    ("Callout_big", ParagraphStyle("Callout_big", fontName="Helvetica", fontSize=10.5,
        leading=15, textColor=TEAL_DARK, spaceAfter=5)),
    ("TaskItem_big", ParagraphStyle("TaskItem_big", fontName="Helvetica", fontSize=10.5,
        leading=15, textColor=CHARCOAL, spaceAfter=4, leftIndent=2)),
]:
    try:
        styles.add(_style)
    except Exception:
        pass

# ── Document metadata ──
DOC_DATE = "2026-08-13"
DOC_CLASSIFICATION = "OAKAI Confidential"
PREPARED_FOR = "EG SEOW / Founder, OAKAI SDN BHD"
DOC_TITLE = "OAKAI Development Workspace Architecture"
DOC_SUBTITLE = "Hermes Agent Dashboard UI — Holistic Architecture, Flow & Function"
DOC_REF = "OAKAI-ARCH-001"

# Document metadata (imported PAGE_W, MARGIN from template) ──
def big_table(rows, col_widths=None):
    header = [Paragraph(str(c), styles["CellHead_big"]) for c in rows[0]]
    data = [header]
    for r in rows[1:]:
        data.append([Paragraph(str(c), styles["Cell_big"]) for c in r])
    t = Table(data, colWidths=col_widths, repeatRows=1, hAlign='LEFT')
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), TEAL_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, TEAL_DARK),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, BORDER),
        ("LINEABOVE", (0, 1), (-1, 1), 0.5, BORDER),
        ("LINELEFT", (0, 0), (0, -1), 0.5, BORDER),
        ("LINERIGHT", (-1, 0), (-1, -1), 0.5, BORDER),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(style))
    return t

def section_h1(number, title, subtitle=None):
    flows = [Paragraph(number, styles["SectionNum"]),
             Paragraph(title, styles["H1_big"])]
    if subtitle:
        flows.append(Paragraph(subtitle, styles["BodySmall_big"]))
    flows.append(hr(color=GOLD, thickness=1.3, space_before=6, space_after=14))
    return flows

def section_h2(number, title, subtitle=None):
    flows = [Paragraph(number, styles["SectionNum"]),
             Paragraph(title, styles["H2_big"])]
    if subtitle:
        flows.append(Paragraph(subtitle, styles["BodySmall_big"]))
    flows.append(hr(color=BORDER, thickness=0.6, space_before=4, space_after=10))
    return flows

def section_h3(title):
    f = [Paragraph(title, styles["H3_big"]), hr(color=TEAL, thickness=0.4, space_before=4, space_after=6)]
    return f

def callout(title, body_lines):
    content = [Paragraph(title, styles["H2_big"])]
    for line in body_lines:
        content.append(Paragraph(line, styles["Callout_big"]))
    tbl = Table([[content]], colWidths=[PAGE_W - 2 * MARGIN])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E7F1EF")),
        ("BOX", (0, 0), (-1, -1), 0.8, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    return tbl

def checklist_items(items):
    return [Paragraph(f"•  {it}", styles["TaskItem_big"]) for it in items]

# ── Block Flow Diagram: Hermes Workspace Architecture ──
def build_workspace_diagram():
    w = PAGE_W - 2 * MARGIN
    h = 120 * mm
    d = Drawing(w, h)

    # Title
    d.add(String(8*mm, h - 4*mm, "Hermes Agent Workspace — Architecture Flow",
                fontName="Helvetica-Bold", fontSize=12, fillColor=TEAL_DARK))
    d.add(String(8*mm, h - 8*mm, "User ↔ Agent ↔ Tools ↔ Data ↔ Persistence",
                fontName="Helvetica", fontSize=8, fillColor=GREY))

    # Layer 1: User Interface
    box1_y = h - 22*mm
    d.add(Rect(10*mm, box1_y - 10*mm, w - 20*mm, 10*mm,
               fillColor=TEAL_DARK, strokeColor=BORDER, strokeWidth=0.5))
    d.add(String(w/2, box1_y - 5*mm, "User Interface Layer",
                fontName="Helvetica-Bold", fontSize=10, fillColor=WHITE, textAnchor="middle"))
    d.add(String(12*mm, box1_y - 16*mm, "TUI Dashboard + CLI + Web UI",
                fontName="Helvetica", fontSize=8, fillColor=GREY))

    # Arrow
    d.add(Line(w/2, box1_y - 12*mm, w/2, box1_y - 14*mm, strokeColor=BORDER, strokeWidth=1.0))
    d.add(Line(w/2-3*mm, box1_y - 14*mm, w/2+3*mm, box1_y - 14*mm, strokeColor=BORDER, strokeWidth=1.0))

    # Layer 2: Agent Core
    box2_y = box1_y - 22*mm
    d.add(Rect(10*mm, box2_y - 10*mm, w - 20*mm, 10*mm,
               fillColor=TEAL, strokeColor=BORDER, strokeWidth=0.5))
    d.add(String(w/2, box2_y - 5*mm, "Agent Core Layer",
                fontName="Helvetica-Bold", fontSize=10, fillColor=WHITE, textAnchor="middle"))
    d.add(String(12*mm, box2_y - 16*mm, "Hermes Agent + Skills Engine + Model Routing (Free-First)",
                fontName="Helvetica", fontSize=8, fillColor=GREY))

    # Arrow
    d.add(Line(w/2, box2_y - 12*mm, w/2, box2_y - 14*mm, strokeColor=BORDER, strokeWidth=1.0))
    d.add(Line(w/2-3*mm, box2_y - 14*mm, w/2+3*mm, box2_y - 14*mm, strokeColor=BORDER, strokeWidth=1.0))

    # Layer 3: Tools & Gateways
    box3_y = box2_y - 22*mm
    d.add(Rect(10*mm, box3_y - 10*mm, w - 20*mm, 10*mm,
               fillColor=GOLD, strokeColor=BORDER, strokeWidth=0.5))
    d.add(String(w/2, box3_y - 5*mm, "Tools & Gateway Layer",
                fontName="Helvetica-Bold", fontSize=10, fillColor=WHITE, textAnchor="middle"))
    d.add(String(12*mm, box3_y - 16*mm, "Web Search, Browser, Vision, TTS, File Tools + Message Gateway (s6)",
                fontName="Helvetica", fontSize=8, fillColor=GREY))

    # Arrow
    d.add(Line(w/2, box3_y - 12*mm, w/2, box3_y - 14*mm, strokeColor=BORDER, strokeWidth=1.0))
    d.add(Line(w/2-3*mm, box3_y - 14*mm, w/2+3*mm, box3_y - 14*mm, strokeColor=BORDER, strokeWidth=1.0))

    # Layer 4: Data & Knowledge
    box4_y = box3_y - 22*mm
    d.add(Rect(10*mm, box4_y - 10*mm, w - 20*mm, 10*mm,
               fillColor=colors.HexColor("#1F3864"), strokeColor=BORDER, strokeWidth=0.5))
    d.add(String(w/2, box4_y - 5*mm, "Data & Knowledge Layer",
                fontName="Helvetica-Bold", fontSize=10, fillColor=WHITE, textAnchor="middle"))
    d.add(String(12*mm, box4_y - 16*mm, "Knowledge Base, Cron Outputs, State DB, File System",
                fontName="Helvetica", fontSize=8, fillColor=GREY))

    # Arrow
    d.add(Line(w/2, box4_y - 12*mm, w/2, box4_y - 14*mm, strokeColor=BORDER, strokeWidth=1.0))
    d.add(Line(w/2-3*mm, box4_y - 14*mm, w/2+3*mm, box4_y - 14*mm, strokeColor=BORDER, strokeWidth=1.0))

    # Layer 5: Persistence & Control
    box5_y = box4_y - 22*mm
    d.add(Rect(10*mm, box5_y - 10*mm, w - 20*mm, 10*mm,
               fillColor=CHARCOAL, strokeColor=BORDER, strokeWidth=0.5))
    d.add(String(w/2, box5_y - 5*mm, "Persistence & Control Layer",
                fontName="Helvetica-Bold", fontSize=10, fillColor=WHITE, textAnchor="middle"))
    d.add(String(12*mm, box5_y - 16*mm, "Git Version Control, state.db, cron/jobs.json, S6 Supervision",
                fontName="Helvetica", fontSize=8, fillColor=GREY))

    # Side accent bar
    d.add(Rect(w - 4*mm, 0, 3*mm, h, fillColor=TEAL, strokeColor=TEAL, strokeWidth=0))

    return d

# ── Block Flow Diagram: Data Flow ──
def build_data_flow_diagram():
    w = PAGE_W - 2 * MARGIN
    h = 100 * mm
    d = Drawing(w, h)

    d.add(String(8*mm, h - 4*mm, "Data Flow — User Request to Persistence",
                fontName="Helvetica-Bold", fontSize=12, fillColor=TEAL_DARK))

    # Flow stages (left to right)
    stages = [
        (15*mm, 22*mm, 40*mm, "User Input", TEAL_DARK, WHITE),
        (60*mm, 22*mm, 40*mm, "Agent Processing", TEAL, WHITE),
        (105*mm, 22*mm, 40*mm, "Tool Execution", GOLD, WHITE),
        (150*mm, 22*mm, 40*mm, "Data Storage", colors.HexColor("#1F3864"), WHITE),
        (195*mm, 22*mm, 40*mm, "Git + Cron", CHARCOAL, WHITE),
    ]

    for i, (x, y, width, label, fill, txt) in enumerate(stages):
        d.add(Rect(x, y, width, 16*mm, fillColor=fill, strokeColor=BORDER, strokeWidth=0.5))
        d.add(String(x + width/2, y + 8*mm, label,
                    fontName="Helvetica-Bold", fontSize=9, fillColor=txt, textAnchor="middle"))
        if i < len(stages) - 1:
            d.add(Line(x + width + 3*mm, y + 8*mm, x + width + 3*mm + 15*mm, y + 8*mm,
                      strokeColor=BORDER, strokeWidth=1.0))
            d.add(Line(x + width + 15*mm + 12*mm, y + 8*mm, x + width + 15*mm + 15*mm, y + 6*mm,
                      strokeColor=BORDER, strokeWidth=1.0))
            d.add(Line(x + width + 15*mm + 15*mm, y + 8*mm, x + width + 15*mm + 15*mm, y + 10*mm,
                      strokeColor=BORDER, strokeWidth=1.0))

    return d

# ── Section builders ──
def build_executive_summary():
    story = []
    story += section_h1("1", "Executive Summary", "Hermes Agent workspace architecture — high-level view")

    story.append(Paragraph(
        "The OAKAI development workspace runs on Hermes Agent — an autonomous AI agent "
        "operating inside a Docker-on-WSL2 container on the founder's Windows laptop. "
        "The workspace is organized into five architectural layers, each with distinct "
        "responsibilities. The agent is currently in the <b>foundation phase</b>: "
        "SSM registration pending, AI infrastructure fully operational on free-tier resources.",
        styles["Body_big"]
    ))

    story.append(Spacer(1, 6*mm))
    story.append(callout("Key Metrics", [
        "Free-tier priority: Nous Portal ~50RPM, OpenRouter 50/day, NVIDIA NIM (one-time credit)",
        "State protection: state.db gitignored + pre-commit hook blocks commits (prevents Aug 12 race condition)",
        "Gateway service: s6-supervised, PID 46427, auto-restart enabled",
        "Cron automation: 6 jobs, all model-pinned to prevent drift",
    ]))

    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        "This document provides both a holistic overview and in-depth technical details "
        "for each architectural layer, data flow, and operational function.",
        styles["Body_big"]
    ))

    story.append(Spacer(1, 8*mm))
    return story

def build_holistic_view():
    story = []
    story += section_h1("2", "Holistic Architecture Overview", "Five-layer model with cross-cutting concerns")

    story.append(Paragraph(
        "The workspace architecture is organized into five layers, from user-facing "
        "interface down to low-level persistence. Each layer encapsulates specific "
        "responsibilities and communicates with adjacent layers through well-defined "
        "interfaces.",
        styles["Body_big"]
    ))

    story.append(Spacer(1, 6*mm))
    story += section_h2("(A)", "Layer Summary")

    layer_rows = [
        ["Layer", "Component", "Primary Function", "Key Files"],
        ["1. User Interface", "TUI Dashboard, CLI, Web UI", "Human interaction surface",
         "tui-theme-boot.json, config.yaml"],
        ["2. Agent Core", "Hermes Agent, Skills Engine, Model Routing", "AI reasoning + tool orchestration",
         "config.yaml (agent.*), mem/, skills/"],
        ["3. Tools & Gateway", "Web, Browser, Vision, File, Message Gateway", "External API + service integration",
         "gateway_state.json, bin/tirith, .local/"],
        ["4. Data & Knowledge", "Knowledge Base, Cron Outputs, State DB", "Information storage + retrieval",
         "knowledge/, cron/output/, state.db"],
        ["5. Persistence & Control", "Git, Cron Scheduler, S6 Supervision", "Version control + automation",
         "cron/jobs.json, .git/, state.snapshots/"],
    ]
    story.append(big_table(layer_rows, col_widths=[30*mm, 35*mm, 40*mm, 40*mm]))

    story.append(Spacer(1, 8*mm))
    story.append(fit_table_to_page(layer_rows, col_widths=[30*mm, 35*mm, 40*mm, 40*mm]))

    story.append(Spacer(1, 6*mm))
    story += section_h2("(B)", "Block Flow Diagram")
    story.append(build_workspace_diagram())
    story.append(Spacer(1, 6*mm))

    story.append(Spacer(1, 6*mm))
    story += section_h2("(C)", "Data Flow Diagram")
    story.append(build_data_flow_diagram())
    story.append(Spacer(1, 8*mm))

    return story

def build_user_interface_layer():
    story = []
    story += section_h1("3", "User Interface Layer", "How humans interact with the agent")

    story += section_h2("(A)", "TUI Dashboard")
    story.append(Paragraph(
        "The Terminal UI (TUI) is the primary human-facing interface. It renders the "
        "agent's conversation, tool calls, and status in a rich color scheme defined "
        "by <b>tui-theme-boot.json</b>.",
        styles["Body_big"]
    ))

    theme_rows = [
        ["Property", "Value", "Purpose"],
        ["Background", "#1e1e1e (dark)", "Eye comfort in low-light"],
        ["Primary color", "#FFD700 (gold)", "Tool status / highlights"],
        ["Accent color", "#FFBF00 (amber)", "Active selections / prompts"],
        ["Border", "#CD7F32 (bronze)", "Panel boundaries"],
        ["Text", "#FFF8DC (cream)", "High-contrast readable text"],
        ["Status good", "#8FBC8F (green)", "Healthy / success state"],
        ["Status bad", "#FF6B6B (red)", "Error / critical state"],
    ]
    story.append(fit_table_to_page(theme_rows, col_widths=[35*mm, 30*mm, 80*mm]))

    story.append(Spacer(1, 6*mm))
    story += section_h2("(B)", "CLI & Web UI")
    story.append(Paragraph(
        "CLI commands: <b>/help</b>, <b>/new</b>, <b>/stop</b>, <b>/status</b>. "
        "Web UI is provided via the browser-use cloud provider when GUI interaction "
        "is needed (e.g., form submissions, visual verification).",
        styles["Body_big"]
    ))
    story.append(Spacer(1, 8*mm))
    return story

def build_agent_core_layer():
    story = []
    story += section_h1("4", "Agent Core Layer", "AI reasoning engine")

    story += section_h2("(A)", "Hermes Agent")
    story.append(Paragraph(
        "The core agent runs with <b>max_turns: 150</b> per session. It loads skills "
        "from <b>/opt/data/skills/</b> and uses the model routing stack to select "
        "free-tier models first.",
        styles["Body_big"]
    ))

    story += section_h2("(B)", "Model Routing (Free-First Priority)")
    routing_rows = [
        ["Priority", "Provider", "Model", "Quota", "Notes"],
        ["1st choice", "Nous Portal", "tencent/hy3:free", "~50RPM", "Default + cron-pinned"],
        ["2nd choice", "OpenRouter", "poolside/laguna-s-2.1:free", "50/day", "Vision fallback"],
        ["3rd choice", "NVIDIA NIM", "nvidia/nemotron-nano-12b-v2-vl", "One-time credit", "Vision only (-vl)"],
        ["Paid (approval)", "Direct", "gemini-2.5-flash, deepseek-v4", "Requires approval", "Last resort"],
    ]
    story.append(fit_table_to_page(routing_rows, col_widths=[20*mm, 35*mm, 45*mm, 22*mm, 35*mm]))

    story.append(Spacer(1, 6*mm))
    story += section_h2("(C)", "Skills Engine")
    story.append(Paragraph(
        "Skills are Python scripts under <b>/opt/data/skills/</b>, organized by category: "
        "PDF generation, productivity (xlsx, powerpoint, docx), creative (design, diagrams), "
        "mlops (model routing, eval), research (web, arxiv), software development, "
        "and hermes-specific tooling.",
        styles["Body_big"]
    ))
    story.append(Spacer(1, 6*mm))

    skill_rows = [
        ["Skill Category", "Key Skills", "Use Case"],
        ["PDF", "OAKAI Professional Engine, mission executive", "Professional reports"],
        ["Productivity", "xlsx, powerpoint, docx, notion, obsidian", "Daily deliverables"],
        ["MLOps", "free-tier-model-routing, hermes-cron-model-pinning", "Cost control + automation"],
        ["Creative", "architecture-diagram, claude-design", "Visual content"],
        ["Research", "web-research-knowledgebase, arxiv, blogwatcher", "Market intelligence"],
    ]
    story.append(fit_table_to_page(skill_rows, col_widths=[30*mm, 55*mm, 60*mm]))

    story.append(Spacer(1, 8*mm))
    return story

def build_tools_layer():
    story = []
    story += section_h1("5", "Tools & Gateway Layer", "External integration and messaging")

    story += section_h2("(A)", "Message Gateway (s6-supervised)")
    gw_rows = [
        ["Property", "Value", "Function"],
        ["Process", "hermes gateway run --replace", "Main gateway loop"],
        ["Supervisor", "s6", "Auto-restart on crash"],
        ["Gateway PID", "46427", "Currently running"],
        ["Supervisor PID", "46425", "Health watchdog"],
        ["Log PID", "46428", "Output capture"],
        ["State", "running", "Active agents: 0 (standby)"],
        ["Platforms", "{} (empty)", "No external platform connected yet"],
    ]
    story.append(fit_table_to_page(gw_rows, col_widths=[35*mm, 35*mm, 85*mm]))

    story.append(Spacer(1, 6*mm))
    story += section_h2("(B)", "External Tools")
    tools_rows = [
        ["Tool", "Provider", "Provider Tier", "Status"],
        ["Web Search", "Firecrawl", "Nous subscription", "Active via gateway"],
        ["Browser Automation", "Browser-Use", "Nous subscription", "Cloud provider"],
        ["Image Generation", "FAL (FLUX.2)", "Nous subscription", "Active"],
        ["TTS", "OpenAI (edge/openai)", "Nous subscription", "Active via gateway"],
        ["STT", "OpenAI Whisper", "Nous subscription", "Active"],
        ["Vision", "NVIDIA Nemotron", "NVIDIA (free)", "Active (nemotron-nano-12b-v2-vl)"],
        ["Local LLM", "Qwen2.5-1.5B + bge-m3", "Local Ollama", "Running (egress fallback)"],
    ]
    story.append(fit_table_to_page(tools_rows, col_widths=[30*mm, 30*mm, 35*mm, 30*mm]))

    story.append(Spacer(1, 6*mm))
    story += section_h2("(C)", "Tirith Threat Intelligence")
    story.append(Paragraph(
        "The <b>tirith</b> binary (22MB) at <b>bin/tirith</b> provides threat "
        "intelligence. Its database lives at <b>.local/share/tirith/tirith-threatdb.dat</b>. "
        "It is referenced in config via <b>tirith_enabled</b> flag.",
        styles["Body_big"]
    ))
    story.append(Spacer(1, 8*mm))
    return story

def build_data_layer():
    story = []
    story += section_h1("6", "Data & Knowledge Layer", "How information is organized")

    story += section_h2("(A)", "Knowledge Base Structure")
    story.append(Paragraph(
        "The knowledge base at <b>/opt/data/knowledge/</b> is indexed by <b>INDEX.md</b>. "
        "It follows a 4-bucket structure:",
        styles["Body_big"]
    ))

    kb_rows = [
        ["Bucket", "Path", "Purpose", "Constraints"],
        ["By Industry", "knowledge/by_industry/", "Client-specific POCs + domain research", "≤32KB SUMMARY (hard cap)"],
        ["Mentor", "knowledge/mentor/", "Daily AI education for founder", "≤32KB SUMMARY (hard cap)"],
        ["Raw", "knowledge/raw/", "Full fetched articles (traceability)", "Not auto-loaded"],
        ["Strategy", "knowledge/strategy/", "COO strategic guidance", "Weekly generation"],
    ]
    story.append(fit_table_to_page(kb_rows, col_widths=[25*mm, 35*mm, 45*mm, 50*mm]))

    story.append(Spacer(1, 6*mm))
    story += section_h2("(B)", "Cron Output Storage")
    story.append(Paragraph(
        "Cron job outputs are stored at <b>/opt/data/cron/output/<job_id>/</b> as "
        "timestamped markdown files. Six active jobs:",
        styles["Body_big"]
    ))

    cron_rows = [
        ["Job ID", "Schedule (UTC)", "Schedule (MYT)", "Deliverable"],
        ["mentor-ai-daily", "07:00, 11:00, 15:00, 19:00", "15:00, 19:00, 23:00, 03:00", "AI concept + test"],
        ["learn-pensolar", "07:00", "15:00", "PENSOLAR research update"],
        ["workspace-cleanup-daily", "02:00", "10:00", "14-day retention pruning"],
        ["strategic-coo-guidance", "Sun 00:00", "Sun 08:00", "Weekly COO brief"],
        ["marketing-advisor-daily", "06:00 (Mon-Sat)", "14:00 (Mon-Sat)", "Marketing content"],
        ["startup-catchup-enforcement", "06:00", "14:00", "Startup checks + catchup"],
    ]
    story.append(fit_table_to_page(cron_rows, col_widths=[25*mm, 25*mm, 25*mm, 70*mm]))

    story.append(Spacer(1, 6*mm))
    story += section_h2("(C)", "State Management")
    state_rows = [
        ["File", "Size", "Purpose", "Protection"],
        ["state.db", "~3.1MB", "Session state, context", "gitignored + pre-commit hook"],
        ["kanban.db", "14KB", "Task tracking", "gitignored"],
        ["projects.db", "4KB", "Project registry", "gitignored"],
        ["verification_evidence.db", "32KB", "Test results log", "gitignored"],
        ["context_length_cache.yaml", "227B", "Token budget tracking", "gitignored"],
        [".hermes_history", "~varies", "Chat session history", "gitignored"],
    ]
    story.append(fit_table_to_page(state_rows, col_widths=[30*mm, 20*mm, 45*mm, 60*mm]))
    story.append(Spacer(1, 8*mm))
    return story

def build_persistence_layer():
    story = []
    story += section_h1("7", "Persistence & Control Layer", "Durability and automation")

    story += section_h2("(A)", "Git Version Control")
    story.append(Paragraph(
        "Repository: <b>https://github.com/seowengguan-sudo/hermes-model-routing.git</b>. "
        "All changes are pushed ad-hoc (multiple commits). No daily sync cron job exists — "
        "pushes are performed manually after each significant change.",
        styles["Body_big"]
    ))
    story.append(Spacer(1, 4*mm))
    checklist_git = [
        "Commit eb8adf2 — gitignore + pre-commit hardening",
        "Commit 2511c44 — PDF enhance with task deliverables",
        "Commit 5c299b5 — Mission executive PDF generator",
        "Commit 0fb524e — Deep research methodology skill",
        "Commit 3ff19f2 — Unified professional-doc-generation skill",
        "Commit b625a30 — Revised mission PDF with larger fonts",
        "Commit f75fa5a — Idempotent style registration fix",
        "Commit 1516e3f6 — INDEX.md cross-references update",
        "Commit 2e63059 — EG SEOW preferences + Gantt + architecture diagram",
        "Commit ae19735 — Aug 2026 calendar date/day correlation fix",
        "Commit 8b13142 — SKILL.md documentation update",
        "Commit d490ef2 — Layout optimization helpers + page-fit improvements",
    ]
    story += checklist(checklist_git)
    story.append(Spacer(1, 6*mm))

    story += section_h2("(B)", "State Protection (Post-Aug 12 Incident)")
    story.append(callout("August 12 Incident", [
        "Git auto-sync race condition zeroed state.db during concurrent read/write",
        "Recovery: restored from commit 54c4651 (pre-race snapshot)",
        "Fix: state.db added to .gitignore + pre-commit hook blocks commits",
        "state.db is now untracked — protected from git operations",
    ]))
    story.append(Spacer(1, 6*mm))

    story += section_h2("(C)", "S6 Process Supervision")
    story.append(Paragraph(
        "The gateway service runs under <b>s6</b> supervision with auto-restart. "
        "If the gateway crashes, s6 restarts it within 5 seconds. The supervisor "
        "and log processes ensure no silent failures.",
        styles["Body_big"]
    ))
    story.append(Spacer(1, 4*mm))
    s6_rows = [
        ["Process", "PID", "Role"],
        ["hermes gateway", "46427", "Main gateway loop (message delivery)"],
        ["s6-supervisor", "46425", "Health watchdog + auto-restart"],
        ["s6-log", "46428", "Output capture + logging"],
    ]
    story.append(fit_table_to_page(s6_rows, col_widths=[50*mm, 25*mm, 80*mm]))
    story.append(Spacer(1, 8*mm))
    return story

def build_governance():
    story = []
    story += section_h1("8", "Governance & Controls", "Safety layers that prevent errors")

    story += section_h2("(A)", "Three-Layer Approval Framework")
    gov_rows = [
        ["Gate", "When", "Mechanism", "Status"],
        ["Approval Gate", "Before paid API calls", "model-selection-policy skill", "✅ Active"],
        ["Eval Gate", "Before trusting AI output", "golden_v1.csv + score_eval.py", "✅ Active"],
        ["Autonomy Gate", "Before AI acts autonomously", "Shadow→Canary→Enforce rollout", "✅ Active"],
    ]
    story.append(fit_table_to_page(gov_rows, col_widths=[30*mm, 35*mm, 55*mm, 30*mm]))

    story.append(Spacer(1, 6*mm))
    story += section_h2("(B)", "Pre-commit Hook")
    story.append(Paragraph(
        "Located at <b>/opt/data/.git/hooks/pre-commit</b>. Blocks commits of:",
        styles["Body_big"]
    ))
    story += checklist([
        "state.db and all SQLite database files (*.db)",
        "All credential/token files (.env, auth.json, *.txt secrets)",
        "Runtime cache files (context_length_cache.yaml)",
    ])

    story.append(Spacer(1, 6*mm))
    story += section_h2("(C)", "Pre-commit Verification Results")
    precommit_rows = [
        ["Check Category", "Checks", "Status"],
        ["State DB protection", "Blocks state.db*, kanban.db*, projects.db*", "✅ 19/19 passed"],
        ["Secret scanning", "Blocks .env, auth.json, GithubToken.txt", "✅ Clean"],
        ["Credential detection", "Blocks API keys, tokens, passwords", "✅ Clean"],
    ]
    story.append(fit_table_to_page(precommit_rows, col_widths=[50*mm, 50*mm, 40*mm]))

    story.append(Spacer(1, 6*mm))
    story += section_h2("(D)", ".gitignore Coverage")
    gi_rows = [
        ["Protected Pattern", "Examples"],
        ["Runtime databases", "state.db*, kanban.db*, projects.db*, cron/executions.db*"],
        ["Logs", "logs/*, *.log"],
        ["Credentials", ".env, GithubToken.txt, auth.json, *.credentials"],
        ["Caches", "context_length_cache.yaml, .hermes_history"],
        ["Session state", "desktop/interrupted_turns.json, skills/.usage.json"],
    ]
    story.append(fit_table_to_page(gi_rows, col_widths=[50*mm, 90*mm]))
    story.append(Spacer(1, 8*mm))
    return story

def build_deployment():
    story = []
    story += section_h1("9", "Deployment & Infrastructure", "Runtime environment details")

    story += section_h2("(A)", "Environment")
    env_rows = [
        ["Property", "Value"],
        ["Host", "Windows (WSL2)"],
        ["Container", "Docker (daemon currently down — irrelevant)"],
        ["Python", "3.13.5 (no pip module, PEP 668)"],
        ["Package Manager", "uv (installed)"],
        ["Working Dir", "/opt/data"],
        ["Git Remote", "github.com/seowengguan-sudo/hermes-model-routing"],
        ["Profile", "default (local)"],
    ]
    story.append(fit_table_to_page(env_rows, col_widths=[40*mm, 90*mm]))

    story.append(Spacer(1, 6*mm))
    story += section_h2("(B)", "Directory Structure")
    dir_rows = [
        ["Directory", "Purpose", "~Size"],
        [".venv (architecture/hermes-venv)", "Python env with reportlab, openpyxl, pymupdf", "86MB"],
        ["lazy-packages/", "Isolated package dir (pymupdf, reportlab, pyyaml)", "1.1MB"],
        ["knowledge/", "Knowledge base (INDEX.md + 4 buckets)", "varies"],
        ["skills/", "Agent capabilities (categorías, hermes, productivity...)", "100+ skills"],
        ["cron/", "Scheduled automation (jobs.json + output/)", "1KB + outputs"],
        ["workspace/", "Generated deliverables (PDFs, data)", "varies"],
        ["state-snapshots/", "Periodic recovery snapshots", "post-Aug12 recovery"],
    ]
    story.append(fit_table_to_page(dir_rows, col_widths=[35*mm, 55*mm, 30*mm]))

    story.append(Spacer(1, 6*mm))
    story += section_h2("(C)", "Egress Constraints")
    story.append(callout("Network Reality", [
        "Egress IP: 161.142.137.99 (TTNET, Penang MY)",
        "Cloudflare WAF blocks Groq/Cerebras (HTTP 403/1010)",
        "HuggingFace DNS-blocked (NXDOMAIN for *.huggingface.co)",
        "Nous API rate-limited (but still accessible — primary provider)",
        "Free-tier priority: Nous → OpenRouter → NVIDIA NIM → Paid (approval-gated)",
        "Mitigation: local-first stack (Qwen2.5-1.5B + bge-m3 via Ollama)",
    ]))
    story.append(Spacer(1, 8*mm))
    return story

# ── Main document assembly ──
def build_architecture_document(out_path):
    story = []

    # Section 1
    story += build_executive_summary()
    story.append(PageBreak())

    # Section 2
    story += build_holistic_view()
    story.append(PageBreak())

    # Section 3
    story += build_user_interface_layer()
    story.append(PageBreak())

    # Section 4
    story += build_agent_core_layer()
    story.append(PageBreak())

    # Section 5
    story += build_tools_layer()
    story.append(PageBreak())

    # Section 6
    story += build_data_layer()
    story.append(PageBreak())

    # Section 7
    story += build_persistence_layer()
    story.append(PageBreak())

    # Section 8
    story += build_governance()
    story.append(PageBreak())

    # Section 9
    story += build_deployment()

    # TOC entries with corrected page numbers (1-indexed, no cover/TOC prefix adjustment)
    toc_entries = [
        ("1", "Executive Summary", "3"),
        ("2", "Holistic Architecture Overview", "4"),
        ("2A", "Layer Summary", "4"),
        ("2B", "Block Flow Diagram", "5"),
        ("2C", "Data Flow Diagram", "6"),
        ("3", "User Interface Layer", "7"),
        ("3A", "TUI Dashboard", "7"),
        ("3B", "CLI & Web UI", "8"),
        ("4", "Agent Core Layer", "9"),
        ("4A", "Hermes Agent", "9"),
        ("4B", "Model Routing", "10"),
        ("4C", "Skills Engine", "11"),
        ("5", "Tools & Gateway Layer", "12"),
        ("5A", "Message Gateway", "12"),
        ("5B", "External Tools", "13"),
        ("5C", "Tirith Threat Intel", "14"),
        ("6", "Data & Knowledge Layer", "15"),
        ("6A", "Knowledge Base Structure", "15"),
        ("6B", "Cron Output Storage", "16"),
        ("6C", "State Management", "17"),
        ("7", "Persistence & Control", "18"),
        ("7A", "Git Version Control", "18"),
        ("7B", "State Protection", "20"),
        ("7C", "S6 Process Supervision", "21"),
        ("8", "Governance & Controls", "22"),
        ("8A", "Three-Layer Approval", "22"),
        ("8B", "Pre-commit Hook", "23"),
        ("8C", "Pre-commit Verification", "24"),
        ("8D", ".gitignore Coverage", "25"),
        ("9", "Deployment & Infrastructure", "26"),
        ("9A", "Environment", "26"),
        ("9B", "Directory Structure", "27"),
        ("9C", "Egress Constraints", "28"),
    ]

    result_path = build_document(
        content_story=story,
        out_path=out_path,
        doc_title=DOC_TITLE,
        doc_subtitle=DOC_SUBTITLE,
        doc_date=DOC_DATE,
        doc_ref=DOC_REF,
        prepared_for=PREPARED_FOR,
        classification=DOC_CLASSIFICATION,
        toc_entries=toc_entries
    )

    return result_path

if __name__ == "__main__":
    out = "/opt/data/workspace/OAK_Architecture_13AUG2026.pdf"
    path = build_architecture_document(out)
    page_count = 0
    try:
        import pymupdf as fitz
        doc = fitz.open(path)
        page_count = doc.page_count
        doc.close()
    except:
        page_count = "~29"
    print(f"✓ Generated: {path}")
    print(f"  Prepared for: {PREPARED_FOR}")
    print(f"  Type: OAKAI Workspace Architecture Documentation")
    print(f"  Pages: {page_count}")
    print(f"  Classification: {DOC_CLASSIFICATION}")
    print(f"  Reference: {DOC_REF}")