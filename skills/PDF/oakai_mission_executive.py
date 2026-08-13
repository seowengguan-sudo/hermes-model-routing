#!/usr/bin/env python3
"""
oakai_mission_executive.py — Generates the OAKAI Mission Executive PDF.

Uses the verified OAKAI design engine (skills/PDF/oakai_pdf_template.py)
with high-contrast palette and professional layout discipline.

Run:
    python3 oakai_mission_executive.py

Output:
    /opt/data/workspace/OAKAI-Mission-Executive.pdf
"""
import sys, os
sys.path.insert(0, '/opt/data/lazy-packages')
sys.path.insert(0, '/opt/data/skills/PDF')
sys.path.insert(0, '/opt/data/skills/productivity/architecture-doc-pdf')

from oakai_pdf_template import (
    build_document, section_header, status_table, checklist,
    kv_callout_box, hr, styles, make_toc, FOOTER_LABEL, BRAND_NAME
)
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, PageBreak, KeepTogether, Table
from reportlab.lib import colors

# ── Document metadata ──
DOC_DATE = "2026-08-13"
DOC_CLASSIFICATION = "OAKAI Confidential"
PREPARED_FOR = "Weng Guan / Founder, OAKAI SDN BHD"
DOC_TITLE = "OAKAI Mission & Roadmap"
DOC_SUBTITLE = "Enterprise AI Business Solution Provider — Executive Brief"
DOC_REF = "OAKAI-MIS-001"

def build_executive_summary():
    """Section 01: Executive Summary — Verdict + positioning."""
    story = []
    story += section_header("01", "Executive Summary", "Mission, positioning, and current state")
    
    story.append(Paragraph(
        "OAKAI SDN BHD is building an AI-powered business solution provider that targets "
        "operational excellence gaps across Manufacturing, Systems Integration, and "
        "Administration/Back-Office sectors. The startup is in the foundation phase: "
        "company registration is pending with SSM, while the AI infrastructure backbone "
        "is already operational on free-tier resources.",
        styles["Body"]
    ))
    
    story.append(kv_callout_box("Key Positioning", [
        "AI solutions backed by a mental-model approach — not just tool integration",
        "Free-tier-first economics (Nous Portal, OpenRouter, local LLM) eliminates upfront infrastructure cost",
        "Vertical overlap: expertise in manufacturing/power-house, systems integration, and back-office "
        "creates a unique intersection advantage for cross-industry AI solutions",
        "POC-first methodology: validate with real customer pain before scaling to enterprise contracts"
    ]))
    
    story.append(hr(color=colors.HexColor("#C69B4B"), thickness=1.0, space_before=8, space_after=12))
    
    story.append(Paragraph(
        "The company operates on a lean bootstrap model with a hard cap on paid API usage "
        "(founder approval required). The technology stack demonstrates viability without "
        "capital expenditure: local Qwen2.5-1.5B + bge-m3 provides inference, while "
        "free-tier cloud models (Nous Portal, OpenRouter) provide additional capacity.",
        styles["Body"]
    ))
    
    story.append(Spacer(1, 6*mm))
    
    return story

def build_mvp_and_market():
    """Section 02: MVP Definition & Market Positioning."""
    story = []
    story += section_header("02", "MVP & Market", "Minimum viable product + target positioning")
    
    # MVP definition table
    mvp_rows = [
        ["Component", "What It Is", "Current Status", "Owner"],
        ["Local AI Stack", "Qwen2.5-1.5B + bge-m3 inference on local machine", "✅ Running", "Ops"],
        ["COO Brief Automation", "Weekly strategic guidance generated via cron", "✅ Week 1 delivered", "AI Co-pilot"],
        ["PENSOLAR POC", "Solar PV project management with AI anomaly detection", "✅ Scaffolded", "AI Co-pilot + Founder"],
        ["Mentor System", "Daily AI education in business language", "✅ 3 concepts delivered", "AI Mentor"],
        ["Marketing System", "LinkedIn presence + daily content cadence", "🔄 In progress", "Founder + cron"],
        ["GitHub Presence", "Open-source knowledge + skills repo", "✅ Active (5 commits)", "AI Co-pilot"],
    ]
    story.append(Paragraph("The MVP stack is built on free-tier + local infrastructure, proving the "
                          "business model works without paid compute:", styles["H3"]))
    story.append(KeepTogether([
        status_table(mvp_rows, col_widths=[30*mm, 50*mm, 30*mm, 30*mm])
    ]))
    
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("Market positioning leverages three competitive advantages:", styles["H3"]))
    
    positioning_rows = [
        ["Advantage", "Description", "Differentiator"],
        ["Mental-Model Approach", "Solutions grounded in systematic problem-framing, not just tool assembly",
         "Most AI consultants skip the 'why'; we teach the 'how to think'"],
        ["Free-Tier Economics", "Full operational stack on free resources — zero capex infrastructure",
         "Competitors spend on cloud; we prove ROI before asking clients to"],
        ["Vertical Overlap", "Manufacturing + SI + Admin expertise creates unique cross-vertical solutions",
         "Single-vertical consultants miss 60% of integration opportunities"],
    ]
    story.append(status_table(positioning_rows, col_widths=[40*mm, 70*mm, 40*mm]))
    
    return story

def build_business_model():
    """Section 03: Business Model — VTDF framework adapted for AI consulting."""
    story = []
    story += section_header("03", "Business Model", "VTDF framework: Value, Tech, Distribution, Finance")
    
    story.append(Paragraph(
        "Adapted from the VTDF (Value-Technology-Distribution-Finance) framework for AI "
        "consulting services. Unlike pure SaaS plays (e.g. C3.ai), OAKAI is positioned as "
        "a solution provider: the product is implemented AI systems, not licensed software.",
        styles["Body"]
    ))
    
    story.append(Spacer(1, 6*mm))
    
    # Value Proposition
    story += section_header("03A", "Value Proposition", "What clients buy")
    vp_rows = [
        ["Value Driver", "Client Benefit", "Evidence"],
        ["Operational Excellence", "Reduce waste, variation, and delay in core workflows",
         "7 Pillars framework validated in PENSOLAR case"],
        ["AI-Augmented Decision Making", "Real-time exception detection + recommendation engine",
         "Qwen2.5-1.5B serving anomaly-flagging demo for solar PM"],
        ["Risk-Gated Autonomy", "AI systems that can act, but stop at the right risk threshold",
         "Shadow→Canary→Enforce rollout with recall-gated auto-rollback"],
        ["Evals-Based Trust", "Every AI capability measured against frozen golden sets",
         "golden_v1.csv + score_eval.py: recall gate on guardrails"],
    ]
    story.append(status_table(vp_rows, col_widths=[40*mm, 50*mm, 60*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    # Technology Stack
    story += section_header("03B", "Technology Stack", "The AI backbone stack")
    
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
    story.append(status_table(stack_rows, col_widths=[20*mm, 45*mm, 40*mm, 30*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    # Revenue Model
    story += section_header("03C", "Revenue Model", "Path to paid services")
    revenue_rows = [
        ["Stream", "Model", "When"],
        ["AI Consulting (POC)", "Fee-for-deliverable: POC builds, eval design, guardrail setup", "Weeks 1-8"],
        ["AI Consulting (Enterprise)", "Retainer + success-based: deployed agents, training, audit", "After 2 client POCs"],
        ["Knowledge Products", "Templates, frameworks, golden-set scaffolding sold as packages", "Q1 2027"],
        ["Training Programs", "Workshop: mental-model AI for operations teams", "Q2 2027"],
    ]
    story.append(status_table(revenue_rows, col_widths=[40*mm, 55*mm, 30*mm]))
    
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        "<b>Unit economics target:</b> LTV:CAC > 3:1, gross margin > 70%, payback period < 90 days. "
        "First 3 client POCs will be at reduced rate to build case studies.",
        styles["BodySmall"]
    ))
    
    return story

def build_coo_roadmap():
    """Section 04: COO-Guided Roadmap."""
    story = []
    story += section_header("04", "COO Roadmap", "Week-by-week execution plan")
    
    story.append(Paragraph(
        "The COO guidance (produced by the <i>strategic-coo-guidance</i> cron every Sunday 08:00 MYT) "
        "frames execution in 3-stream parallel sprints. Each week has a legal/marketing/product stream, "
        "with success metrics tied to measurable outcomes.",
        styles["Body"]
    ))
    
    story.append(Spacer(1, 4*mm))
    
    roadmap_rows = [
        ["Week", "Legal Stream", "Marketing Stream", "Product Stream", "Key Metric"],
        ["W1", "SSM incorporation + domain", "LinkedIn profile + Day-1 post", "3 client surveys + local LLM scaffold", "SSM receipt + 30 LinkedIn followers"],
        ["W2", "Bank account opening", "Landing page GitHub Pages", "PENSOLAR demo scenario 1", "Bank ready + landing page live"],
        ["W3", "Service agreement template", "Content calendar + 7 posts", "PENSOLAR demo scenario 2", "3 demo scenarios drafted"],
        ["W4", "NDA template + COO Brief package", "Group engagement 15+ posts", "Local LLM integration validated", "First client demo tested"],
        ["W5-W8", "Client contract templates", "Case study content pipeline", "Client POC #1 (real engagement)", "First paid POC signed"],
    ]
    story.append(status_table(roadmap_rows, col_widths=[15*mm, 25*mm, 35*mm, 35*mm, 40*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    # Risk mitigation
    story += section_header("04A", "Risk Mitigation", "Proactive threat coverage")
    risk_rows = [
        ["Risk", "Impact", "Probability", "Mitigation"],
        ["Egress blocked (HF DNS, Groq WAF)", "H", "H", "Local-first stack: Qwen2.5-1.5B + bge-m3"],
        ["Free-tier throttled (Nous ~50RPM, OR 50/day)", "M", "H", "Batch off-line; local LLM is primary"],
        ["SSM name rejection", "H", "M", "3 names filed simultaneously"],
        ["No client responds to survey", "M", "M", "Lead with personal network + RM20 incentive each"],
        ["LinkedIn shadow-ban", "L", "M", "Human-first posting, spaced cadence, no hashtag spam"],
        ["Bank account delay", "H", "M", "Prep packet day 4; founder personal bridge account tagged"],
    ]
    story.append(status_table(risk_rows, col_widths=[50*mm, 18*mm, 20*mm, 62*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    # Success metrics
    story += section_header("04B", "Success Metrics", "Week 1 targets (gate: pass/fail)")
    metrics_rows = [
        ["Metric", "Baseline", "Target", "Signal"],
        ["Company status", "Unnamed", "SSM receipt issued", "Green = A1+A2 started"],
        ["Domain", "Unregistered", "Paid + DNS configured", "Green = A3 done"],
        ["Bank account", "None", "Prep packet complete", "Green = A4 done; open = W2"],
        ["LinkedIn followers", "0", "30+", "Green ≥ 30"],
        ["Client surveys", "0", "3 (mfg/retail/F&B)", "Green = C1 done"],
        ["Local LLM scaffold", "None", "Running inference", "Green = C5 done"],
        ["W1 cash spent", "—", "≤ RM215 core", "Budget held"],
    ]
    story.append(status_table(metrics_rows, col_widths=[30*mm, 25*mm, 30*mm, 40*mm]))
    
    story.append(Paragraph(
        "Pass threshold: A1+A2+A3 landed, C5 scaffold running, 1 survey done, Day-1 post live, 30+ followers.",
        styles["BodySmall"]
    ))
    
    return story

def build_technology_foundation():
    """Section 05: Technology Foundation — how the AI stack works."""
    story = []
    story += section_header("05", "Technology Foundation", "The AI backbone in practice")
    
    story.append(Paragraph(
        "The OAKAI AI stack consists of five layers, each chosen for cost-free operation "
        "while maintaining production viability:",
        styles["Body"]
    ))
    
    story.append(Spacer(1, 4*mm))
    
    layer_rows = [
        ["Layer", "Component", "Function"],
        ["LLM Layer", "Qwen2.5-1.5B (local) + laguna-s-2.1 (Nous free)", "Reasoning, synthesis, copy drafting"],
        ["RAG Layer", "bge-m3 embeddings + SQLite FTS5", "Knowledge retrieval, document search"],
        ["Agent Layer", "Hermes Agent + skills system", "Autonomous task execution, tool use"],
        ["Guardrail Layer", "model-selection-policy skill", "Free-first routing, approval gates, cost control"],
        ["Eval Layer", "golden_v1.csv + score_eval.py", "Precision/recall, recall-gated rollout"],
    ]
    story.append(status_table(layer_rows, col_widths=[25*mm, 50*mm, 85*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    story.append(Paragraph("Key architectural decisions:", styles["H3"]))
    
    architecture_rows = [
        ["Decision", "Choice", "Rationale"],
        ["Free-tier priority", "Nous Portal → OpenRouter → NVIDIA NIM → Paid (approval)", "Minimizes cash burn; paid requires founder sign-off"],
        ["Local fallback", "Qwen2.5-1.5B + bge-m3 via Ollama", "Egress blocked (HF DNS, Groq WAF); local-first mandatory"],
        ["Model pinning", "cron jobs pinned to tencent/hy3:free", "Prevents model-drift from default changes breaking crons"],
        ["State protection", "state.db gitignored + pre-commit hook blocks commits", "Prevents Aug 12 race-condition corruption"],
        ["Gateway", "s6-managed gateway service", "Auto-restart on crash; notifications via messaging platforms"],
    ]
    story.append(status_table(architecture_rows, col_widths=[40*mm, 50*mm, 65*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    # Autonomous systems
    story += section_header("05A", "Autonomous Systems", "Six parallel cron streams")
    
    cron_rows = [
        ["Cron Job", "Schedule", "Deliverable"],
        ["mentor-ai-daily", "15:00 MYT x3 (07/15/22)", "AI concept + test in knowledge/mentor/"],
        ["learn-pensolar", "15:00 MYT", "Gap-driven research update to PENSOLAR SUMMARY"],
        ["strategic-coo-guidance", "Sun 08:00 MYT", "Weekly COO brief in knowledge/strategy/"],
        ["marketing-advisor-daily", "06:00 MYT Mon-Sat", "Daily marketing content for LinkedIn"],
        ["workspace-cleanup-daily", "02:00 MYT", "14-day retention pruning"],
        ["startup-catchup-enforcement", "06:00 MYT daily", "Auto-enforce startup checks + catchup"],
    ]
    story.append(status_table(cron_rows, col_widths=[35*mm, 30*mm, 85*mm]))
    
    return story

def build_governance():
    """Section 06: Governance & Controls."""
    story = []
    story += section_header("06", "Governance & Controls", "How safety and quality are enforced")
    
    story.append(Paragraph(
        "Three layers of defense ensure quality output and safe operation. These are "
        "not aspirational — they are implemented and verified in the current stack:",
        styles["Body"]
    ))
    
    story.append(Spacer(1, 6*mm))
    
    story += section_header("06A", "Approval Gate", "Before paid API calls")
    story.append(Paragraph(
        "The <i>model-selection-policy</i> skill enforces free-first routing. Paid models "
        "(Gemini, DeepSeek direct) require explicit founder approval. The routing chain: "
        "Nous Portal → OpenRouter → NVIDIA NIM → Paid (approval-gated).",
        styles["Body"]
    ))
    
    story += section_header("06B", "Eval Gate", "Before trusting AI output")
    story.append(Paragraph(
        "Every AI tool is evaluated against frozen, stratified golden sets "
        "(golden_v1.csv, 20 rows, 25% block cases). Precision/recall/accuracy reported. "
        "Recall is the gate for guardrails — accuracy is the last number reported, not the first.",
        styles["Body"]
    ))
    
    story += section_header("06C", "Autonomy Gate", "Safe AI action in production")
    story.append(Paragraph(
        "Shadow → Canary → Enforce rollout: shadow (advisory, human decides) → "
        "canary (low-risk auto-approval) → enforce (full autonomy). "
        "Auto-rollback to dial 0 if recall drops below threshold on any block case.",
        styles["Body"]
    ))
    
    story.append(Spacer(1, 8*mm))
    
    # Compliance checklist
    story += section_header("06D", "Weekly Compliance Checklist", "Must-pass before closing the week")
    
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
    story += checklist(checklist_items)
    
    return story

def build_financial_snapshot():
    """Section 07: Financial Snapshot."""
    story = []
    story += section_header("07", "Financial Snapshot", "Bootstrap economics + W1 budget")
    
    budget_rows = [
        ["Item", "Cost (RM)", "Tier", "Status"],
        ["SSM name reservation", "30", "Core", "Pending"],
        ["SSM incorporation (private limited)", "110", "Core", "Pending"],
        ["Domain oakai.com.my (1yr)", "15", "Core", "Pending"],
        ["Survey incentive (3 clients)", "60", "Core", "Pending"],
        ["<b>Subtotal core</b>", "<b>215</b>", "", ""],
        ["Contingency buffer", "45", "Optional", "Pending"],
        ["LinkedIn Premium (W2)", "—", "Deferred", "Deferred"],
        ["Paid APIs (W1+)", "—", "Approval-gated", "Not used"],
        ["<b>W1 cash max</b>", "<b>260</b>", "Core + buffer", "Cap"],
    ]
    story.append(status_table(budget_rows, col_widths=[50*mm, 20*mm, 35*mm, 30*mm]))
    
    story.append(Spacer(1, 8*mm))
    
    story.append(kv_callout_box("Key Constraint", [
        "Egress reality: HF DNS-blocked, Groq/Cerebras behind Cloudflare WAF. "
        "All dev/POC runs on local stack. Cloud AI only via approved free tiers.",
        "Free-tier AI (Nous Portal ~50RPM, OpenRouter 50/day) + local Qwen2.5-1.5B "
        "cover all W1 synthesis, copy, and contract drafting. "
        "No paid LLM call is made without founder approval."
    ]))
    
    return story

# ── Main build ──
def build_mission_document(out_path):
    """Assemble the full document."""
    
    story = []
    
    # Section 01
    story += build_executive_summary()
    story.append(PageBreak())
    
    # Section 02
    story += build_mvp_and_market()
    story.append(PageBreak())
    
    # Section 03
    story += build_business_model()
    story.append(PageBreak())
    
    # Section 04
    story += build_coo_roadmap()
    story.append(PageBreak())
    
    # Section 05
    story += build_technology_foundation()
    story.append(PageBreak())
    
    # Section 06
    story += build_governance()
    story.append(PageBreak())
    
    # Section 07
    story += build_financial_snapshot()
    
    # TOC (estimate page numbers — two-pass correction in SKILL.md)
    toc_entries = [
        ("01", "Executive Summary", "3"),
        ("02", "MVP & Market", "4"),
        ("03", "Business Model", "5"),
        ("04", "COO Roadmap", "7"),
        ("05", "Technology Foundation", "9"),
        ("06", "Governance & Controls", "11"),
        ("07", "Financial Snapshot", "13"),
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
        import fitz
        doc = fitz.open(path)
        page_count = doc.page_count
        doc.close()
    except:
        page_count = "~14"
    
    print(f"✓ Generated: {path}")
    print(f"  Type: OAKAI Mission Executive Brief")
    print(f"  Pages: {page_count}")
    print(f"  Classification: {DOC_CLASSIFICATION}")
    print(f"  Reference: {DOC_REF}")