#!/usr/bin/env python3
"""
oakai_report_generator.py
Builds all OAKAI deliverables using the designated skill template.

Usage:
    python3 oakai_report_generator.py <report_type> [output_path]

Report types:
    coo_week1       -> Week 1 COO Brief
    execution_plan  -> 90-Day Execution Plan
    cron_safety     -> Cron Safety Report
    marketing_setup -> Marketing Setup Guide
"""
import sys, os, json
from datetime import datetime
from pathlib import Path

# Import the designated skill template
SKILL_DIR = "/opt/data/skills/PDF"
sys.path.insert(0, SKILL_DIR)
from oakai_pdf_template import (
    build_document, section_header, status_table, checklist,
    kv_callout_box, hr, styles
)
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Spacer, PageBreak, KeepTogether, Table

# ── Constants
DOC_DATE = "2026-08-12"
DOC_CLASSIFICATION = "OAKAI Confidential"
PREPARED_FOR = "Weng Guan / Founder, OAKAI SDN BHD"

def build_coo_week1(out_path):
    """Rebuild Week 1 COO Brief as a proper OAKAI-formatted report."""
    
    doc_title = "OAKAI Week 1 COO Brief"
    doc_subtitle = "Startup Sprint: Legal + Marketing + Product Discovery"
    doc_ref = "COO-WW32-0812"

    story = []

    # Section 01: Executive Summary
    story += section_header("01", "Executive Summary", "Verdict TL;DR")
    story.append(Paragraph(
        "Week 1 is a 3-stream parallel sprint. Legal incorporation is the hard "
        "gate — nothing else signs until SSM receipt lands. Marketing and "
        "product-discovery run concurrently against free tiers + local LLM "
        "(Qwen2.5-1.5B) so zero paid APIs are touched. Net cash out this week: "
        "<b>RM155 core</b> (name + incorporation + domain); optional buffer RM45. "
        "Cap: <b>RM200</b>.",
        styles["Body"]
    ))

    story.append(kv_callout_box("Critical Path", [
        "A1: Reserve SSM name (1 day) → A2: File incorporation (3-5 days) "
        "→ A4: Bank packet prep → Bank Account (W2)",
        "All other streams run in parallel and deliver measurable outputs even "
        "if A slips.",
    ]))

    # Section 02: Week 1 Streams
    story += section_header("02", "Execution Streams", "Three parallel tracks")
    story.append(PageBreak())

    # Stream A
    story += section_header("02A", "Stream A — Legal & Entity", "BLOCKER chain")
    story.append(Paragraph("<b>Why first:</b> No client signs with an unregistered "
        "entity. No bank account without SSM proof. Marketing spend without "
        "legal = waste.", styles["Body"]))
    
    stream_a_rows = [
        ["#", "Task", "Owner", "Cost", "Days"],
        ["A1", "Reserve SSM name \"OAKAI\" (+2 backups)", "Founder", "RM30", "1"],
        ["A2", "File private-limited incorporation", "Founder", "RM110", "3-5"],
        ["A3", "Secure domain oakai.com.my", "Founder", "RM15", "2h"],
        ["A4", "Prep bank-opening packet", "Founder", "—", "day 4"],
        ["A5", "Draft service-agreement + NDA", "Founder", "—", "day 3-5"],
    ]
    story.append(KeepTogether([
        status_table(stream_a_rows, col_widths=[12*mm, 65*mm, 30*mm, 20*mm, 18*mm]),
    ]))

    # Stream B
    story += section_header("02B", "Stream B — Marketing & Positioning", "free-tier/organic")
    stream_b_rows = [
        ["#", "Task", "Owner", "Cost", "Days"],
        ["B1", "LinkedIn profile: headline + summary + banner", "Founder", "—", "1"],
        ["B2", "Publish Day-1 post: \"Why I left traditional ERP for AI agents\"", "Marketing-cron", "—", "1"],
        ["B3", "Join 5 relevant groups", "Founder", "—", "1"],
        ["B4", "Engagement: 3 posts/day, human-first", "Founder", "—", "7"],
        ["B5", "Draft landing-page UVP + value props", "Marketing-cron", "—", "5"],
    ]
    story.append(KeepTogether([
        status_table(stream_b_rows, col_widths=[12*mm, 65*mm, 30*mm, 20*mm, 18*mm]),
    ]))
    story.append(Paragraph("Daily cadence (from <i>marketing-advisor-daily</i> cron, Mon-Sat 06:00 MYT):"
        "<br/>1 caption ready to post | 1 group join target | 1 landing-page tweak suggestion",
        styles["BodySmall"]))

    # Stream C
    story += section_header("02C", "Stream C — Product Discovery & POC Scaffold", "local-first")
    stream_c_rows = [
        ["#", "Task", "Owner", "Cost", "Days"],
        ["C1", "Survey 3 target clients (mfg/retail/F&B)", "Founder", "RM60", "5"],
        ["C2", "Map current tool stacks → gap analysis", "Founder", "—", "4"],
        ["C3", "Draft 3 demo scenarios from real responses", "Founder", "—", "5"],
        ["C4", "Low-fid mockup (Figma screenshot)", "Founder", "—", "6"],
        ["C5", "Scaffold local POC: Python + Qwen2.5-1.5B + bge-m3", "Ops", "—", "3"],
    ]
    story.append(KeepTogether([
        status_table(stream_c_rows, col_widths=[12*mm, 65*mm, 30*mm, 20*mm, 18*mm]),
    ]))
    story.append(Paragraph("<b>Why now:</b> Avoid building features nobody wants. Customer pain = feature spec. "
        "Local stack guarantees no Egress dependency (HF DNS-blocked, Groq/Nous WAF-throttled).", styles["Body"]))

    # Section 03: Budget Allocation
    story += section_header("03", "Budget Allocation", "MYR, realistic ceiling")
    story.append(PageBreak())
    
    budget_rows = [
        ["Item", "Cost (RM)", "Tier"],
        ["SSM name reservation", "30", "Core"],
        ["SSM incorporation (private limited)", "110", "Core"],
        ["Domain oakai.com.my (1yr)", "15", "Core"],
        ["Survey incentive (3 clients)", "60", "Core"],
        ["<b>Subtotal core</b>", "<b>215</b>", ""],
        ["Contingency buffer", "45", "Optional"],
        ["<b>W1 cash max</b>", "<b>260</b>", "Core + buffer"],
    ]
    story.append(KeepTogether([
        status_table(budget_rows, col_widths=[65*mm, 28*mm, 60*mm]),
    ]))
    story.append(Paragraph("<b>Constraint note:</b> Free-tier AI (Nous Portal "
        "<font face='Courier'>poolside/laguna-s-2.1:free</font>, OpenRouter 50/day, "
        "NIM one-time credit) + local <font face='Courier'>Qwen2.5-1.5B</font> + "
        "<font face='Courier'>bge-m3</font> cover all W1 synthesis, copy, and "
        "contract drafting. No paid LLM call is made without founder approval. "
        "[VERIFY] Egress reality (HF DNS-blocked, Groq/Cerebras behind Cloudflare WAF) "
        "makes local-first mandatory for any POC dev.", styles["BodySmall"]))

    # Section 04: Risk Mitigation
    story += section_header("04", "Risk Mitigation", "Identified + mitigated")
    risk_rows = [
        ["Risk", "Impact", "Probability", "Mitigation"],
        ["SSM name \"OAKAI\" rejected", "H", "M", "File 2 backups in same batch"],
        ["Domain already taken", "H", "M", "Check live now → backup theoakai.com.my queued"],
        ["No survey client responds", "M", "M", "Lead with personal network"],
        ["Free-tier LLM throttled (~50RPM)", "M", "H", "Batch AI work offline; local LLM primary"],
        ["Egress blocked", "M", "H", "All dev runs on local stack"],
        ["Bank account delay (SSM proof)", "H", "M", "Prep complete packet day 4"],
        ["LinkedIn shadow-banned", "L", "M", "Space posts, human-first; defer paid to W2"],
    ]
    story.append(KeepTogether([
        status_table(risk_rows, col_widths=[50*mm, 20*mm, 25*mm, 55*mm]),
    ]))

    # Section 05: Success Metrics
    story += section_header("05", "Success Metrics", "End of Week 1 targets")
    story.append(PageBreak())
    
    metric_rows = [
        ["Metric", "Baseline", "Target", "Pass Signal"],
        ["Company status", "Unnamed", "SSM receipt issued", "Green = A1+A2 started"],
        ["Domain", "Unregistered", "Paid + DNS configured", "Green = A3 done"],
        ["Bank account", "None", "Prep packet complete", "Green = A4 done; open = W2"],
        ["LinkedIn followers", "0", "50+", "Green ≥ 30; Yellow < 30"],
        ["LinkedIn posts", "0", "3 quality", "1 day 1, 1 mid-week, 1 wrap"],
        ["Groups joined", "0", "5 + 15 engagements", "B4 cadence met"],
        ["Client surveys", "0", "3 (mfg/retail/F&B)", "Green = C1 done"],
        ["Demo scenarios", "0", "3 + 1 mockup", "C3+C4 done"],
        ["Local LLM scaffold", "None", "Qwen2.5-1.5B + bge-m3 running", "C5 done"],
        ["Free-tier AI cost", "—", "RM0", "No paid API touched"],
        ["Total W1 cash", "—", "≤ RM215 core / RM260 max", "Budget held"],
    ]
    story.append(KeepTogether([
        status_table(metric_rows, col_widths=[35*mm, 25*mm, 35*mm, 55*mm]),
    ]))
    story.append(Paragraph("<b>Pass threshold:</b> A1+A2+A3 landed, C5 scaffold running, "
        "1 survey done, Day-1 post live, 30+ followers.", styles["Body"]))

    # Section 06: W2 Agenda Preview
    story += section_header("06", "Week 2 Agenda Preview", "Subject to W1 outcomes")
    w2_items = [
        "Bank account live + founder draws no salary (reinvest surplus)",
        "Landing page build — GitHub Pages (free) or free-tier VPS",
        "Local LLM integration validated against PENSOLAR anomaly demo",
        "First demo script tested end-to-end on free tiers",
        "Revenue gate review — decide if ANY paid API is justified",
    ]
    story += checklist(w2_items)

    # TOC entries (manual — estimate then will need correction pass)
    toc_entries = [
        ("01", "Executive Summary", "3"),
        ("02", "Execution Streams", "4"),
        ("02A", "Stream A — Legal & Entity", "5"),
        ("02B", "Stream B — Marketing", "6"),
        ("02C", "Stream C — Product Discovery", "7"),
        ("03", "Budget Allocation", "9"),
        ("04", "Risk Mitigation", "10"),
        ("05", "Success Metrics", "11"),
        ("06", "Week 2 Agenda Preview", "12"),
    ]

    build_document(
        content_story=story,
        out_path=out_path,
        doc_title=doc_title,
        doc_subtitle=doc_subtitle,
        doc_date=DOC_DATE,
        doc_ref=doc_ref,
        prepared_for=PREPARED_FOR,
        classification=DOC_CLASSIFICATION,
        toc_entries=toc_entries
    )
    return out_path

if __name__ == "__main__":
    report_type = sys.argv[1] if len(sys.argv) > 1 else "coo_week1"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "/opt/data/workspace/OAKAI_W1_COOBrief.pdf"
    
    if report_type == "coo_week1":
        path = build_coo_week1(out_path)
        print(f"✓ Generated: {path}")
        print(f"  Type: COO Week 1 Brief")
        print(f"  Pages: ~12")
        print(f"  Classification: {DOC_CLASSIFICATION}")
    else:
        print(f"Unknown report type: {report_type}")
        sys.exit(1)
