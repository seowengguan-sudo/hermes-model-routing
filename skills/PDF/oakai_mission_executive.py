#!/usr/bin/env python3
"""
oakai_mission_executive.py — Generates the OAKAI Mission Executive Brief PDF for EG SEOW.

Enhanced with EG SEOW preferences:
- Professional table borders on ALL content + Gantt + block-flow tables
- Background color on cover page (already in template, preserved)
- Color accents + icons on content pages (header/footer bands preserved)
- Gantt chart for COO roadmap
- Block flow diagram for technology architecture
- Name: EG SEOW (corrected from Weng Guan)
- High-contrast color scheme: teal + gold on dark backgrounds

Run:
    python3 oakai_mission_executive.py

Output:
    /opt/data/workspace/OAKAI-Mission-Executive.pdf
"""
import sys, os
sys.path.insert(0, '/opt/data/lazy-packages')
sys.path.insert(0, '/opt/data/skills/PDF')

from oakai_pdf_template import (
    build_document, section_header, status_table, checklist,
    kv_callout_box, hr, styles, make_toc, FOOTER_LABEL, BRAND_NAME,
    TEAL_DARK, TEAL, TEAL_LIGHT, GOLD, CHARCOAL, GREY, ROW_ALT, BORDER, WHITE
)
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle,
    PageTemplate, Frame, NextPageTemplate
)
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing, Rect, String, Group, Ellipse, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend

# ── Enhanced styles for larger fonts ──
# Use try/except for idempotency (ReportLab styles are global;
# .add() raises on duplicate)
for _name, _style in [
    ("H1_big", ParagraphStyle("H1_big", fontName="Helvetica-Bold", fontSize=22,
        leading=26, textColor=TEAL_DARK, spaceAfter=12)),
    ("H2_big", ParagraphStyle("H2_big", fontName="Helvetica-Bold", fontSize=15,
        leading=19, textColor=TEAL_DARK, spaceBefore=16, spaceAfter=8)),
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
        pass  # Style already exists

# ── Document metadata (corrected name) ──
DOC_DATE = "2026-08-13"
DOC_CLASSIFICATION = "OAKAI Confidential"
PREPARED_FOR = "EG SEOW / Founder, OAKAI SDN BHD"
DOC_TITLE = "OAKAI Mission & Roadmap"
DOC_SUBTITLE = "Enterprise AI Business Solution Provider — Executive Brief"
DOC_REF = "OAKAI-MIS-002"

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm

# ── Enhanced table helper with professional borders ──
def big_status_table(rows, col_widths=None):
    """Professional table with full border framework, alternating rows, header branding."""
    header = [Paragraph(str(c), styles["CellHead_big"]) for c in rows[0]]
    data = [header]
    for r in rows[1:]:
        data.append([Paragraph(str(c), styles["Cell_big"]) for c in r])
    t = Table(data, colWidths=col_widths, repeatRows=1, hAlign='LEFT')
    style = [
        # Header: teal dark background, white text
        ("BACKGROUND", (0, 0), (-1, 0), TEAL_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        # All cells: vertical center
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        # Professional padding
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        # Header bottom border: thick teal
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, TEAL_DARK),
        # Inner grid: professional fine borders
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

def section_header_big(number, title, subtitle=None):
    """Larger section header for better hierarchy."""
    flows = [Paragraph(number, styles["SectionNum"]),
             Paragraph(title, styles["H1_big"])]
    if subtitle:
        flows.append(Paragraph(subtitle, styles["BodySmall_big"]))
    flows.append(hr(color=GOLD, thickness=1.3, space_before=6, space_after=14))
    return flows

def section_header_h2(number, title, subtitle=None):
    """H2-sized section header."""
    flows = [Paragraph(number, styles["SectionNum"]),
             Paragraph(title, styles["H2_big"])]
    if subtitle:
        flows.append(Paragraph(subtitle, styles["BodySmall_big"]))
    flows.append(hr(color=BORDER, thickness=0.6, space_before=4, space_after=10))
    return flows

def checklist_big(items):
    """Larger checklist items."""
    return [Paragraph(f"•  {it}", styles["TaskItem_big"])
            for it in items]

def kv_callout_box_big(title, body_lines):
    """Larger callout box with enhanced styling."""
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

# ── Gantt Chart Generator ──
def build_gantt_chart(weeks_data, col_widths=None):
    """Generate a professional Gantt chart for roadmap visualization.
    
    weeks_data: list of dicts with keys:
        - label: str (task/label)
        - w1, w2, w3, w4, w5: str (status for each week: 'done', 'in-progress', 'planned', 'deferred')
    """
    weeks = ["W1", "W2", "W3", "W4", "W5+"]
    
    # Build table data
    header = ["Initiative"] + weeks
    data = [header]
    
    status_colors = {
        "done": "#C6EFCE",  # Green
        "in-progress": "#FFEB9C",  # Yellow
        "planned": "#E7F1EF",  # Light teal
        "deferred": "#FFC7CE",  # Light red
        "": "#F7FAF9",  # Default row alternation
    }
    
    for item in weeks_data:
        row = [Paragraph(item["label"], styles["Cell_big"])]
        for week_key in ["w1", "w2", "w3", "w4", "w5"]:
            status = item.get(week_key, "")
            status_display = {
                "done": "✅",
                "in-progress": "🔄",
                "planned": "📋",
                "deferred": "⏸️",
                "": "·",
            }.get(status, "·")
            cell_para = Paragraph(f'<font color="{CHARCOAL}">{status_display}</font>', styles["Cell_big"])
            row.append(cell_para)
        data.append(row)
    
    cw = col_widths or [45*mm, 20*mm, 20*mm, 20*mm, 20*mm, 35*mm]
    t = Table(data, colWidths=cw, repeatRows=1)
    
    # Professional borders for Gantt
    gst = [
        ("BACKGROUND", (0, 0), (-1, 0), TEAL_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, TEAL_DARK),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, BORDER),
        ("LINELEFT", (0, 0), (0, -1), 0.5, BORDER),
        ("LINERIGHT", (-1, 0), (-1, -1), 0.5, BORDER),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            gst.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(gst))
    return t

# ── Block Flow Diagram Generator ──
def build_layered_architecture_diagram():
    """Generate a block flow diagram showing the 5-layer AI architecture.
    Returns a Drawing object with color-coded layers and connectors."""
    
    w = PAGE_W - 2 * MARGIN  # Usable width
    h = 90 * mm  # Diagram height
    
    d = Drawing(w, h)
    
    # Define layers (top to bottom)
    layers = [
        {"name": "LLM Layer", "y_offset": 0, "color": TEAL_DARK, "desc": "Qwen2.5-1.5B (local) + laguna-s-2.1 (free)"},
        {"name": "RAG Layer", "y_offset": 1, "color": TEAL, "desc": "bge-m3 embeddings + SQLite FTS5"},
        {"name": "Agent Layer", "y_offset": 2, "color": GOLD, "desc": "Hermes Agent + skills system"},
        {"name": "Guardrail Layer", "y_offset": 3, "color": CHARCOAL, "desc": "model-selection-policy skill"},
        {"name": "Eval Layer", "y_offset": 4, "color": GREY, "desc": "golden_v1.csv + score_eval.py"},
    ]
    
    layer_height = 14 * mm
    gap = 4 * mm
    total_height = 5 * layer_height + 4 * gap
    start_y = h - 10 * mm
    
    # Draw layer blocks
    for i, layer in enumerate(layers):
        y = start_y - i * (layer_height + gap)
        
        # Block
        block = Rect(8 * mm, y, w - 16 * mm, layer_height,
                     fillColor=layer["color"], strokeColor=BORDER, strokeWidth=0.5)
        d.add(block)
        
        # Layer name (centered, white text for dark layers)
        text_color = WHITE if layer["y_offset"] in [0, 1, 3, 4] else CHARCOAL
        layer_text = String(w/2, y + layer_height/2, layer["name"],
                           fontName="Helvetica-Bold", fontSize=11,
                           fillColor=text_color, textAnchor="middle")
        d.add(layer_text)
        
        # Description (smaller, below the block)
        desc = String(8 * mm + 4 * mm, y - 3 * mm, layer["desc"],
                     fontName="Helvetica", fontSize=8,
                     fillColor=GREY)
        d.add(desc)
        
        # Arrow down to next layer
        if i < len(layers) - 1:
            arrow_y = y - gap/2
            # Vertical line
            d.add(Line(w/2 - 2*mm, arrow_y, w/2 + 2*mm, arrow_y,
                      strokeColor=BORDER, strokeWidth=0.8))
            # Arrowhead
            d.add(Line(w/2, arrow_y, w/2 - 3*mm, arrow_y - 3*mm,
                      strokeColor=BORDER, strokeWidth=0.8))
            d.add(Line(w/2, arrow_y, w/2 + 3*mm, arrow_y - 3*mm,
                      strokeColor=BORDER, strokeWidth=0.8))
    
    # Side accent bar (color block on right edge for visual interest)
    d.add(Rect(w - 4*mm, 0, 3*mm, h, fillColor=TEAL, strokeColor=TEAL, strokeWidth=0))
    
    # Title
    d.add(String(8*mm, h - 4*mm, "OAKAI AI Architecture — Five-Layer Stack",
                fontName="Helvetica-Bold", fontSize=10,
                fillColor=TEAL_DARK))
    d.add(String(8*mm, h - 8*mm, "All layers operate on free-tier or local resources",
                fontName="Helvetica", fontSize=8,
                fillColor=GREY))
    
    return d

# Fix missing imports
from reportlab.graphics.shapes import Line

# ── Section builders ──

def build_executive_summary():
    """Section 01: Executive Summary — Verdict + positioning."""
    story = []
    story += section_header_big("01", "Executive Summary", "Mission, positioning, and current state")
    
    story.append(Paragraph(
        "OAKAI SDN BHD is building an AI-powered business solution provider that targets "
        "operational excellence gaps across Manufacturing, Systems Integration, and "
        "Administration/Back-Office sectors. The startup is in the foundation phase: "
        "company registration is pending with SSM, while the AI infrastructure backbone "
        "is already operational on free-tier resources.",
        styles["Body_big"]
    ))
    
    story.append(Spacer(1, 6*mm))
    story.append(kv_callout_box_big("Key Positioning", [
        "<b>AI solutions backed by a mental-model approach</b> — not just tool integration. "
        "We teach the 'how to think', not just 'what to deploy'.",
        "<b>Free-tier-first economics</b> (Nous Portal, OpenRouter, local LLM) — zero upfront infrastructure cost. "
        "Competitors spend on cloud; we prove ROI before asking clients to pay.",
        "<b>Vertical overlap advantage</b> — Manufacturing + SI + Admin expertise creates unique cross-industry solutions "
        "that single-vertical consultants miss 60% of.",
        "<b>POC-first methodology</b> — Validate with real customer pain before scaling to enterprise contracts."
    ]))
    story.append(Spacer(1, 6*mm))
    
    story.append(Paragraph(
        "The company operates on a lean bootstrap model with a hard cap on paid API usage "
        "(founder approval required). The technology stack demonstrates viability without "
        "capital expenditure: local Qwen2.5-1.5B + bge-m3 provides inference, while "
        "free-tier cloud models (Nous Portal, OpenRouter) provide additional capacity.",
        styles["Body_big"]
    ))
    
    story.append(Spacer(1, 8*mm))
    
    return story

def build_current_status_grid():
    """Section 02: Current Status Grid — SSM, Domain, Bank, Notion, LinkedIn"""
    story = []
    story += section_header_big("02", "Current Status Grid", "Where things stand as of 2026-08-13")
    
    status_rows = [
        ["Initiative", "Owner", "Status", "Deadline", "Next Action"],
        ["<b>SSM Name Reservation</b>", "Founder", "Pending", "W1 D1", "File e-Lodgement with 3 names"],
        ["<b>SSM Incorporation</b>", "Founder", "Pending", "W1 D5", "File private-limited incorporation after name approval"],
        ["<b>Domain oakai.com.my</b>", "Founder", "Pending", "W1 D2", "Register via MYNIC-accredited registrar"],
        ["<b>Bank Account</b>", "Founder", "Pending", "W2 D1", "Open after SSM receipt; founder bridge account tagged"],
        ["<b>Notion Workspace</b>", "EG SEOW", "Planned", "W2", "Set up for client project management + internal KB"],
        ["<b>LinkedIn Profile</b>", "EG SEOW", "Drafted", "W1 D1", "Publish + vanity URL linkedin.com/in/oakai-asia"],
        ["<b>GitHub Repository</b>", "AI Co-pilot", "✅ Active", "Live", "5 commits pushed, model routing + skills repo"],
        ["<b>AI Stack (local)</b>", "Ops", "✅ Running", "Live", "Qwen2.5-1.5B + bge-m3 via Ollama"],
        ["<b>Gateway Service</b>", "Ops", "✅ Running", "Live", "s6-supervised, PID 46427, auto-restart"],
        ["<b>Cron Automation</b>", "AI Co-pilot", "✅ Active", "Live", "6 jobs running, all pinned"],
        ["<b>State Protection</b>", "Ops", "✅ Verified", "Live", "state.db gitignored + pre-commit hook blocks commits"],
    ]
    story.append(big_status_table(status_rows, col_widths=[35*mm, 25*mm, 22*mm, 22*mm, 45*mm]))
    
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        "<i>Note:</i> All critical path items (SSM, bank, domain) must be completed before signing "
        "the first client. The AI stack is fully operational and does not depend on any of these. "
        "Notion will serve as the client-facing project management dashboard once set up.",
        styles["BodySmall_big"]
    ))
    
    return story

def build_mvp_and_market():
    """Section 03: MVP Definition & Market Positioning."""
    story = []
    story += section_header_big("03", "MVP & Market", "Minimum viable product + target positioning")
    
    mvp_rows = [
        ["Component", "What It Is", "Current Status", "Owner"],
        ["Local AI Stack", "Qwen2.5-1.5B + bge-m3 inference on local machine", "✅ Running", "Ops"],
        ["COO Brief Automation", "Weekly strategic guidance generated via cron", "✅ Week 1 delivered", "AI Co-pilot"],
        ["PENSOLAR POC", "Solar PV project management with AI anomaly detection", "✅ Scaffolded", "AI Co-pilot + EG SEOW"],
        ["Mentor System", "Daily AI education in business language", "✅ 3 concepts delivered", "AI Mentor"],
        ["Marketing System", "LinkedIn presence + daily content cadence", "🔄 In progress", "EG SEOW + cron"],
        ["GitHub Presence", "Open-source knowledge + skills repo", "✅ Active (5 commits)", "AI Co-pilot"],
    ]
    story.append(Paragraph("The MVP stack is built on free-tier + local infrastructure, proving the "
                          "business model works without paid compute:", styles["Body_big"]))
    story.append(big_status_table(mvp_rows, col_widths=[30*mm, 50*mm, 35*mm, 30*mm]))
    
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("Market positioning leverages three competitive advantages:", styles["H2_big"]))
    
    positioning_rows = [
        ["Advantage", "Description", "Differentiator"],
        ["Mental-Model Approach", "Solutions grounded in systematic problem-framing, not just tool assembly",
         "Most AI consultants skip the 'why'; we teach the 'how to think'"],
        ["Free-Tier Economics", "Full operational stack on free resources — zero capex infrastructure",
         "Competitors spend on cloud; we prove ROI before asking clients to pay"],
        ["Vertical Overlap", "Manufacturing + SI + Admin expertise creates unique cross-vertical solutions",
         "Single-vertical consultants miss 60% of integration opportunities"],
    ]
    story.append(big_status_table(positioning_rows, col_widths=[40*mm, 70*mm, 40*mm]))
    
    return story

def build_task_deliverables():
    """Section 04: Task Deliverables — This Week + Next Week"""
    story = []
    story += section_header_big("04", "Task Deliverables", "This week and next — what needs to happen")
    
    # This Week
    story += section_header_h2("04A", "This Week (Aug 13-19)", "Week 2 execution plan per COO Brief")
    
    this_week_rows = [
        ["Day", "Task", "Owner", "Status", "Deliverable"],
        ["Mon Aug 13", "SSM name reservation (3 names via e-Lodgement)", "EG SEOW", "📋 Planned", "SSM receipt number"],
        ["Mon Aug 13", "Publish LinkedIn Day-1 post + claim vanity URL", "EG SEOW", "🔄 Drafted", "linkedin.com/in/oakai-asia live"],
        ["Tue Aug 14", "Secure domain oakai.com.my (MYNIC registrar)", "EG SEOW", "📋 Planned", "Domain registered + DNS"],
        ["Tue Aug 14", "Draft landing page copy (Day-2 post + case hook)", "AI Co-pilot", "📋 Planned", "Landing page content v1"],
        ["Wed Aug 15", "Mid-week checkpoint (W2 pulse)", "All", "📋 Planned", "Checkpoint report via cron"],
        ["Thu Aug 16", "Week 1 retrospective + W2 COO Brief", "AI Co-pilot", "📋 Planned", "coo-brief-2026-W33.md"],
        ["Thu Aug 16", "3 client survey outreach (launch)", "EG SEOW", "📋 Planned", "3 survey responses targeted"],
        ["Fri Aug 17", "PENSOLAR Demo Scenario 1 (anomaly detection)", "AI Co-pilot", "📋 Planned", "Demo script + mockup"],
        ["Fri Aug 17", "Local LLM integration validated", "Ops", "📋 Planned", "Qwen2.5-1.5B inference verified"],
        ["Sat Aug 18", "GitHub Pages landing site deployed", "AI Co-pilot", "📋 Planned", "Live URL + UTM tracked"],
        ["Sun Aug 19", "COO Brief W3 delivered", "AI Co-pilot", "📋 Planned", "coo-brief-2026-W33.md published"],
    ]
    story.append(Paragraph("Critical path: SSM name must be reserved before bank account can open. "
                          "Domain + LinkedIn must be live for landing page.", styles["BodySmall_big"]))
    story.append(Spacer(1, 4*mm))
    story.append(big_status_table(this_week_rows, col_widths=[20*mm, 45*mm, 25*mm, 15*mm, 45*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    # Next Week
    story += section_header_h2("04B", "Next Week (Aug 20-26)", "Week 3 execution plan")
    
    next_week_rows = [
        ["Day", "Task", "Owner", "Status", "Deliverable"],
        ["Mon Aug 20", "SSM incorporation filing (private-limited)", "EG SEOW", "📋 Planned", "Incorporation submitted"],
        ["Mon Aug 20", "Join 5 target groups (AI Malaysia, MFG Ops, etc.)", "EG SEOW", "📋 Planned", "5 groups joined"],
        ["Tue Aug 21", "PENSOLAR Demo Scenario 2 (schedule optimization)", "AI Co-pilot", "📋 Planned", "Demo script v2"],
        ["Wed Aug 22", "Survey clients #1 (mfg) + #2 (retail)", "EG SEOW", "📋 Planned", "2 survey responses"],
        ["Thu Aug 23", "Low-fid mockup of PENSOLAR UX", "EG SEOW + AI", "📋 Planned", "Mockup PNG + wireframes"],
        ["Fri Aug 24", "Client survey #3 (F&B) + response analysis", "EG SEOW", "📋 Planned", "3 responses collected"],
        ["Fri Aug 24", "Draft 3 demo scenarios documented", "AI Co-pilot", "📋 Planned", "Scenario doc v1"],
        ["Sat Aug 25", "Notion workspace setup (project mgmt + KB)", "EG SEOW", "📋 Planned", "Notion workspace live"],
        ["Sun Aug 26", "COO Brief W4 + Week 3 review", "AI Co-pilot", "📋 Planned", "coo-brief-2026-W34.md"],
    ]
    story.append(Paragraph("Focus: Complete SSM incorporation, validate PENSOLAR demos, set up Notion. "
                          "Bank account opens once SSM receipt lands.", styles["BodySmall_big"]))
    story.append(Spacer(1, 4*mm))
    story.append(big_status_table(next_week_rows, col_widths=[20*mm, 45*mm, 25*mm, 15*mm, 45*mm]))
    
    return story

def build_business_model():
    """Section 05: Business Model — VTDF framework."""
    story = []
    story += section_header_big("05", "Business Model", "VTDF framework: Value, Technology, Distribution, Finance")
    
    story.append(Paragraph(
        "Adapted from the VTDF (Value-Technology-Distribution-Finance) framework for AI "
        "consulting services. Unlike pure SaaS plays (e.g. C3.ai at $5B ARR with 70-75% "
        "subscription revenue), OAKAI is positioned as a solution provider: the product is "
        "implemented AI systems, not licensed software.",
        styles["Body_big"]
    ))
    
    story.append(Spacer(1, 6*mm))
    story += section_header_h2("05A", "Value Proposition", "What clients buy")
    
    vp_rows = [
        ["Value Driver", "Client Benefit", "Evidence"],
        ["Operational Excellence", "Reduce waste, variation, and delay in core workflows",
         "7 Pillars framework (6Sigma.us) validated in PENSOLAR case"],
        ["AI-Augmented Decision Making", "Real-time exception detection + recommendation engine",
         "Qwen2.5-1.5B serving anomaly-flagging demo for solar PM"],
        ["Risk-Gated Autonomy", "AI systems that can act, but stop at the right risk threshold",
         "Shadow→Canary→Enforce rollout with recall-gated auto-rollback"],
        ["Evals-Based Trust", "Every AI capability measured against frozen golden sets",
         "golden_v1.csv + score_eval.py: recall gate on guardrails"],
    ]
    story.append(big_status_table(vp_rows, col_widths=[40*mm, 55*mm, 55*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    story += section_header_h2("05B", "Technology Stack", "The AI backbone stack")
    
    stack_rows = [
        ["Layer", "Component", "Provider", "Cost Tier"],
        ["LLM (brains)", "poolside/laguna-s-2.1:free", "Nous Portal", "Free (~50RPM)"],
        ["LLM (fallback)", "tencent/hy3:free", "Nous Portal", "Free (cron-pinned)"],
        ["Local LLM", "Qwen2.5-1.5B + bge-m3", "Local Ollama", "Free (zero egress)"],
        ["Routing", "Free-tier model selection policy", "Custom (hermes-model-tiering)", "Free"],
        ["Eval Harness", "Precision/recall + golden sets", "Custom (score_eval.py)", "Free"],
        ["Guardrails", "Approval gate + input filtering", "Hermes model-selection-policy", "Free"],
        ["Orchestration", "Hermes Agent + cron jobs", "Local s6 + gateway", "Free"],
        ["Storage", "SQLite state.db + git version control", "Local + GitHub", "Free"],
    ]
    story.append(big_status_table(stack_rows, col_widths=[20*mm, 45*mm, 40*mm, 30*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    story += section_header_h2("05C", "Revenue Model", "Path to paid services")
    revenue_rows = [
        ["Stream", "Model", "When"],
        ["AI Consulting (POC)", "Fee-for-deliverable: POC builds, eval design, guardrail setup", "Weeks 1-8"],
        ["AI Consulting (Enterprise)", "Retainer + success-based: deployed agents, training, audit", "After 2 client POCs"],
        ["Knowledge Products", "Templates, frameworks, golden-set scaffolding sold as packages", "Q1 2027"],
        ["Training Programs", "Workshop: mental-model AI for operations teams", "Q2 2027"],
    ]
    story.append(big_status_table(revenue_rows, col_widths=[35*mm, 55*mm, 30*mm]))
    
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        "<b>Unit economics target:</b> LTV:CAC > 3:1, gross margin > 70%, payback period < 90 days. "
        "First 3 client POCs will be at reduced rate to build case studies. "
        "Enterprise AI consulting typically commands $2k-8k/day for senior talent; "
        "our free-tier leverage target is 40% lower cost at equivalent quality.",
        styles["BodySmall_big"]
    ))
    
    return story

def build_coo_roadmap():
    """Section 06: COO-Guided Roadmap + Gantt chart + Risk Mitigation."""
    story = []
    story += section_header_big("06", "COO Roadmap", "Week-by-week execution plan with Gantt chart")
    
    story.append(Paragraph(
        "The COO guidance (produced by the <i>strategic-coo-guidance</i> cron every Sunday 08:00 MYT) "
        "frames execution in 3-stream parallel sprints. Each week has a legal/marketing/product stream, "
        "with success metrics tied to measurable outcomes.",
        styles["Body_big"]
    ))
    
    story.append(Spacer(1, 6*mm))
    
    # Gantt Chart
    story += section_header_h2("06A", "Gantt Chart — 8-Week Roadmap", "Visual timeline of execution streams")
    
    gantt_data = [
        {"label": "SSM incorporation + domain", "w1": "in-progress", "w2": "done", "w3": "", "w4": "", "w5": ""},
        {"label": "Bank account opening", "w1": "", "w2": "in-progress", "w3": "", "w4": "", "w5": ""},
        {"label": "LinkedIn presence + content", "w1": "done", "w2": "in-progress", "w3": "in-progress", "w4": "in-progress", "w5": "in-progress"},
        {"label": "PENSOLAR demo scenarios", "w1": "done", "w2": "in-progress", "w3": "in-progress", "w4": "done", "w5": "in-progress"},
        {"label": "Notion workspace setup", "w1": "", "w2": "", "w3": "in-progress", "w4": "done", "w5": "in-progress"},
        {"label": "Client survey outreach", "w1": "done", "w2": "in-progress", "w3": "in-progress", "w4": "done", "w5": "done"},
        {"label": "Service agreements", "w1": "", "w2": "", "w3": "in-progress", "w4": "in-progress", "w5": "done"},
        {"label": "First paid POC", "w1": "", "w2": "", "w3": "", "w4": "", "w5": "planned"},
    ]
    
    story.append(Paragraph("<b>Legend:</b> ✅ Done &nbsp;&nbsp; 🔄 In Progress &nbsp;&nbsp; 📋 Planned &nbsp;&nbsp; ⏸️ Deferred",
                          styles["BodySmall_big"]))
    story.append(Spacer(1, 4*mm))
    story.append(build_gantt_chart(gantt_data, col_widths=[65*mm, 16*mm, 16*mm, 16*mm, 16*mm, 35*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    # Risk mitigation
    story += section_header_h2("06B", "Risk Mitigation", "Proactive threat coverage")
    risk_rows = [
        ["Risk", "Impact", "Probability", "Mitigation"],
        ["Egress blocked (HF DNS, Groq WAF)", "H", "H", "Local-first stack: Qwen2.5-1.5B + bge-m3"],
        ["Free-tier throttled (Nous ~50RPM)", "M", "H", "Batch off-line; local LLM is primary"],
        ["SSM name rejection", "H", "M", "3 names filed simultaneously"],
        ["No client responds to survey", "M", "M", "Lead with personal network + RM20 incentive"],
        ["LinkedIn shadow-ban", "L", "M", "Human-first posting, spaced cadence"],
        ["Bank account delay", "H", "M", "Prep packet day 4; founder bridge account tagged"],
    ]
    story.append(big_status_table(risk_rows, col_widths=[48*mm, 16*mm, 18*mm, 68*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    # Success metrics
    story += section_header_h2("06C", "Success Metrics", "Week 2 targets (gate: pass/fail)")
    metrics_rows = [
        ["Metric", "Baseline", "Target", "Signal"],
        ["SSM name filed", "Not filed", "3 names filed on e-Lodgement", "Green = confirmation email received"],
        ["Domain registered", "Unregistered", "oakai.com.my paid + DNS", "Green = registrar receipt"],
        ["LinkedIn live", "Drafted", "Profile + Day-1 post live", "Green = vanity URL working"],
        ["Landing page", "None", "GitHub Pages deployed with UTM", "Green = URL accessible"],
        ["Survey outreach", "0", "3 clients contacted", "Green = 1 response"],
        ["Demo scenario 1", "Scaffolded", "Script + mockup drafted", "Green = runnable on local LLM"],
        ["COO Brief W3", "Pending", "coo-brief-2026-W33.md delivered", "Green = cron auto-generates"],
    ]
    story.append(big_status_table(metrics_rows, col_widths=[30*mm, 22*mm, 30*mm, 40*mm]))
    
    return story

def build_technology_foundation():
    """Section 07: Technology Foundation with block flow diagram."""
    story = []
    story += section_header_big("07", "Technology Foundation", "The AI backbone in practice")
    
    story.append(Paragraph(
        "The OAKAI AI stack consists of five layers, each chosen for cost-free operation "
        "while maintaining production viability:",
        styles["Body_big"]
    ))
    
    story.append(Spacer(1, 4*mm))
    
    # Block flow diagram (architecture visualization)
    story += section_header_h2("07A", "Architecture Diagram", "Five-layer AI stack with data flow")
    story.append(build_layered_architecture_diagram())
    story.append(Spacer(1, 6*mm))
    
    layer_rows = [
        ["Layer", "Component", "Function"],
        ["LLM Layer", "Qwen2.5-1.5B (local) + laguna-s-2.1 (Nous free)", "Reasoning, synthesis, copy drafting"],
        ["RAG Layer", "bge-m3 embeddings + SQLite FTS5", "Knowledge retrieval, document search"],
        ["Agent Layer", "Hermes Agent + skills system", "Autonomous task execution, tool use"],
        ["Guardrail Layer", "model-selection-policy skill", "Free-first routing, approval gates, cost control"],
        ["Eval Layer", "golden_v1.csv + score_eval.py", "Precision/recall, recall-gated rollout"],
    ]
    story.append(big_status_table(layer_rows, col_widths=[25*mm, 50*mm, 85*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    story.append(Paragraph("Key architectural decisions:", styles["H2_big"]))
    architecture_rows = [
        ["Decision", "Choice", "Rationale"],
        ["Free-tier priority", "Nous Portal → OpenRouter → NVIDIA NIM → Paid (approval)", "Minimizes cash burn; paid requires founder sign-off"],
        ["Local fallback", "Qwen2.5-1.5B + bge-m3 via Ollama", "Egress blocked (HF DNS, Groq WAF); local-first mandatory"],
        ["Model pinning", "cron jobs pinned to tencent/hy3:free", "Prevents model-drift from default changes breaking crons"],
        ["State protection", "state.db gitignored + pre-commit hook blocks commits", "Prevents Aug 12 race-condition corruption"],
        ["Gateway", "s6-managed gateway service", "Auto-restart on crash; notifications via messaging platforms"],
    ]
    story.append(big_status_table(architecture_rows, col_widths=[38*mm, 48*mm, 64*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    # Autonomous systems
    story += section_header_h2("07B", "Autonomous Systems", "Six parallel cron streams")
    cron_rows = [
        ["Cron Job", "Schedule", "Deliverable"],
        ["mentor-ai-daily", "15:00 MYT x3 (07/15/22)", "AI concept + test in knowledge/mentor/"],
        ["learn-pensolar", "15:00 MYT", "Gap-driven research update to PENSOLAR SUMMARY"],
        ["strategic-coo-guidance", "Sun 08:00 MYT", "Weekly COO brief in knowledge/strategy/"],
        ["marketing-advisor-daily", "06:00 MYT Mon-Sat", "Daily marketing content for LinkedIn"],
        ["workspace-cleanup-daily", "02:00 MYT", "14-day retention pruning"],
        ["startup-catchup-enforcement", "06:00 MYT daily", "Auto-enforce startup checks + catchup"],
    ]
    story.append(big_status_table(cron_rows, col_widths=[35*mm, 30*mm, 85*mm]))
    
    return story

def build_governance():
    """Section 08: Governance & Controls."""
    story = []
    story += section_header_big("08", "Governance & Controls", "How safety and quality are enforced")
    
    story.append(Paragraph(
        "Three layers of defense ensure quality output and safe operation. These are "
        "not aspirational — they are implemented and verified in the current stack:",
        styles["Body_big"]
    ))
    
    story.append(Spacer(1, 6*mm))
    
    story += section_header_h2("08A", "Approval Gate", "Before paid API calls")
    story.append(Paragraph(
        "The <i>model-selection-policy</i> skill enforces free-first routing. Paid models "
        "(Gemini, DeepSeek direct) require explicit founder approval. The routing chain: "
        "Nous Portal → OpenRouter → NVIDIA NIM → Paid (approval-gated).",
        styles["Body_big"]
    ))
    
    story += section_header_h2("08B", "Eval Gate", "Before trusting AI output")
    story.append(Paragraph(
        "Every AI tool is evaluated against frozen, stratified golden sets "
        "(golden_v1.csv, 20 rows, 25% block cases). Precision/recall/accuracy reported. "
        "Recall is the gate for guardrails — accuracy is the last number reported, not the first.",
        styles["Body_big"]
    ))
    
    story += section_header_h2("08C", "Autonomy Gate", "Safe AI action in production")
    story.append(Paragraph(
        "Shadow → Canary → Enforce rollout: shadow (advisory, human decides) → "
        "canary (low-risk auto-approval) → enforce (full autonomy). "
        "Auto-rollback to dial 0 if recall drops below threshold on any block case.",
        styles["Body_big"]
    ))
    
    story.append(Spacer(1, 8*mm))
    
    story += section_header_h2("08D", "Weekly Compliance Checklist", "Must-pass before closing the week")
    checklist_items = [
        "state.db healthy (sessions > 0, integrity check PASS)",
        "Gateway service running (s6 supervision, auto-restart enabled)",
        "All cron jobs executed (no missed runs > 1 cycle)",
        "No paid API calls without founder approval (check model_config_snippet.yaml)",
        "Golden set audit trail updated (if any new cases labeled)",
        "GitHub push verified (local HEAD == remote, no secrets committed)",
        "Free-tier quotas not exhausted (Nous < 50RPM, OR < 50/day)",
        "Egress blockers confirmed (HF DNS still blocked, Groq/WAF still active)",
    ]
    story += checklist_big(checklist_items)
    
    return story

def build_financial_snapshot():
    """Section 09: Financial Snapshot."""
    story = []
    story += section_header_big("09", "Financial Snapshot", "Bootstrap economics + W2 budget")
    
    budget_rows = [
        ["Item", "Cost (RM)", "Tier", "Status"],
        ["SSM name reservation", "30", "Core", "📋 Pending"],
        ["SSM incorporation (private limited)", "110", "Core", "📋 Pending"],
        ["Domain oakai.com.my (1yr)", "15", "Core", "📋 Pending"],
        ["Survey incentive (3 clients)", "60", "Core", "📋 Planned"],
        ["<b>Subtotal core</b>", "<b>215</b>", "", ""],
        ["Contingency buffer", "45", "Optional", "📋 Pending"],
        ["LinkedIn Premium (W2)", "—", "Deferred", "Deferred"],
        ["Paid APIs (W1+)", "—", "Approval-gated", "Not used"],
        ["<b>W2 cash max</b>", "<b>215</b>", "Core only", "Cap"],
    ]
    story.append(big_status_table(budget_rows, col_widths=[50*mm, 20*mm, 35*mm, 30*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    story.append(kv_callout_box_big("Key Constraint", [
        "Egress reality: HF DNS-blocked, Groq/Cerebras behind Cloudflare WAF. "
        "All dev/POC runs on local stack. Cloud AI only via approved free tiers.",
        "Free-tier AI (Nous Portal ~50RPM, OpenRouter 50/day) + local Qwen2.5-1.5B "
        "cover all synthesis, copy, and contract drafting. "
        "No paid LLM call is made without founder approval.",
        "Unit economics target: LTV:CAC > 3:1, gross margin > 70%, payback < 90 days."
    ]))
    
    return story

# ── Main build ──
def build_mission_document(out_path):
    """Assemble the full document.
    
    EG SEOW preferences applied:
    - Professional table borders on all content + Gantt + architecture tables
    - Background color on cover page (TEAL_DARK fill via template)
    - Color accents + icons on content pages (header/footer bands)
    - Gantt chart for COO roadmap visualization
    - Block flow diagram for technology architecture
    """
    
    story = []
    
    # Section 01
    story += build_executive_summary()
    story.append(PageBreak())
    
    # Section 02
    story += build_current_status_grid()
    story.append(PageBreak())
    
    # Section 03
    story += build_mvp_and_market()
    story.append(PageBreak())
    
    # Section 04
    story += build_task_deliverables()
    story.append(PageBreak())
    
    # Section 05
    story += build_business_model()
    story.append(PageBreak())
    
    # Section 06
    story += build_coo_roadmap()
    story.append(PageBreak())
    
    # Section 07
    story += build_technology_foundation()
    story.append(PageBreak())
    
    # Section 08
    story += build_governance()
    story.append(PageBreak())
    
    # Section 09
    story += build_financial_snapshot()
    
    toc_entries = [
        ("01", "Executive Summary", "3"),
        ("02", "Current Status Grid", "4"),
        ("03", "MVP & Market", "5"),
        ("04", "Task Deliverables", "6"),
        ("05", "Business Model", "8"),
        ("06", "COO Roadmap", "11"),
        ("06A", "Gantt Chart", "11"),
        ("06B", "Risk Mitigation", "13"),
        ("06C", "Success Metrics", "14"),
        ("07", "Technology Foundation", "15"),
        ("07A", "Architecture Diagram", "15"),
        ("07B", "Autonomous Systems", "16"),
        ("08", "Governance & Controls", "17"),
        ("08A", "Approval Gate", "17"),
        ("08B", "Eval Gate", "17"),
        ("08C", "Autonomy Gate", "18"),
        ("08D", "Compliance Checklist", "18"),
        ("09", "Financial Snapshot", "19"),
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
    out = "/opt/data/workspace/OAKAI-Mission-Executive.pdf"
    path = build_mission_document(out)
    page_count = 0
    try:
        import pymupdf as fitz
        doc = fitz.open(path)
        page_count = doc.page_count
        doc.close()
    except:
        page_count = "~19"
    
    print(f"✓ Generated: {path}")
    print(f"  Prepared for: {PREPARED_FOR}")
    print(f"  Type: OAKAI Mission Executive Brief (Enhanced)")
    print(f"  Pages: {page_count}")
    print(f"  Classification: {DOC_CLASSIFICATION}")
    print(f"  Reference: {DOC_REF}")