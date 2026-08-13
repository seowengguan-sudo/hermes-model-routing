---
name: agentic-architecture-documentation
description: Documents agentic AI architectures into executive PDFs.
author: Hermes Agent
---

# Agentic Architecture Documentation

## When to use this skill

Use this skill when documenting a complex multi-agent AI architecture (e.g., Master-Specialist patterns, dynamic model routing, continuous learning frameworks) into a professional, executive-ready PDF format. Focus on clarity, comprehensiveness, and persuasive communication of the system's value and capabilities.

## Workflow

1.  **Content Review & Enhancement (Deep Research & Comb):** Thoroughly review existing architectural content to identify areas for expansion, clarification, or integration of advanced concepts. Conduct targeted research on advanced agentic architectures, continuous learning, anti-hallucination, dynamic model tiering, resilience, and data security. Synthesize research findings to propose specific content enhancements for each section. Emphasize "executive-ready" style: refined vision statements, key pillars, quantified value propositions, detailed mechanisms, and forward-looking concepts.

2.  **Professional Diagram & Illustration Pointers:** Design diagrams that clearly illustrate data flows, control flows, feedback loops, and key interfaces. Do NOT settle for a single ASCII steps-table when the user asks for "better illustration" — build a real flow-chart. See the diagram checklist in `professional-doc-deliverables` (Topology, provider chain, local gate, control loop, feedback loop, interruption flow). When reportlab is available, draw diagrams by subclassing `Flowable` (roundRect/polygon/line primitives).

3.  **PDF Generation (verified reportlab path — NOT stdlib-only):** The older stdlib-only PDF method is error-prone for dense, multi-table, multi-diagram specs. Use **reportlab Platypus** instead:
    - Build content as a list of flowables (Paragraph, Table, Spacer, PageBreak, custom Flowable).
    - **Wrap every Table cell in a Paragraph** (raw strings do NOT wrap → overlap). Use a `table()` helper.
    - Valid structure, consistent fonts (Helvetica), page numbering, section dividers.
    - **VERIFY visually before declaring done:** render the densest pages to PNG (dpi 110) and `vision_analyze` for overlap / cutoff / column collision. If `vision_analyze` returns a 404 (no vision endpoint on the active model), use the programmatic checks in `references/high_contrast_and_diagram_verification.md` instead.

## Diagram & Formatting Standards (high-contrast, legible)

User feedback (FIRST-CLASS skill signal): light tints + thin grey strokes read as washed-out and are NOT friendly for quick comprehension. Every diagram and table in the deliverable must be high-contrast:

- **Fills:** saturated, not pastel — Navy `#1F3864`, Blue `#2E5C9E`, Green `#2E7D32`, Amber `#B7791F`, Red `#B91C1C`, Purple `#6B2C91`, Teal `#0F766E`. For neutral "remote/local" bands use dark grey `#595959`, NOT light grey.
- **Text on fills:** white, **bold** (Helvetica-Bold), ≥7.5pt.
- **Outlines:** dark strokes 1.2–1.6pt (never thin grey) — the outline is what separates a box from the white page.
- **Captions / legends / footnotes:** dark grey `#333333`, NOT `#555555`.
- **Tables:** navy header fill + white text; grid `#888888`; body text near-black; subtle zebra `#EEF2F8` only (must not reduce contrast).
- **Box-label helper:** split on `\n` FIRST then on spaces (else `\n` becomes a literal overflowing token); guard `isinstance(fill, colors.Color)` before `colors.HexColor()`. See `references/high_contrast_and_diagram_verification.md`.

## Holistic Master Diagram (whole-system view)

When the user says "one diagram that articulates the overall architecture" or "professional clear structured diagram," do NOT deliver only a pile of narrow subsystem diagrams. Produce:
1. ONE **master/holistic overview** on its own page — the whole system at a glance (user → core → specialists → model pool, with feedback loops drawn as arcs). Best on **A3 landscape** via direct `canvas.Canvas` to avoid frame-fit overflow.
2. Then the detailed per-subsystem diagrams (topology, provider chain, local gate, control loop, feedback, interruption, orchestration) as supporting pages.
Embed the master diagram as the **COVER** of the consolidated PDF so the reader gets the big picture first.

## Rescreen → Incremental Versioning Workflow

The user repeatedly asks "rescreen the architecture for <weakness>." Recurring pattern:
1. Re-read the ACTUAL current artifacts (Excel sheets, PDF text) — do not rely on memory of what you "wrote."
2. Identify concrete gaps as enumerated IDs (e.g. A1..An, F1..Fn, H1..Hn).
3. Implement as a versioned increment (v3.4 → v3.5 → v3.6…) touching BOTH Excel (new sheet / extended loop) AND the PDF (new section + diagram).
4. Keep the model matrix and 4-slot SEQ columns intact; only ADD.
5. State the honest residual: design/spec ≠ running system unless the runtime was actually built.

## Verification Without Vision (fallback)

The active free-tier model may have NO vision endpoint — `vision_analyze` then returns `404 - No endpoints found that support image input`. Do NOT rely on it as the only check. Verify programmatically (pymupdf text + PIL border-pixel scan; see `references/high_contrast_and_diagram_verification.md`): zero non-white pixels in the outer ~10px border ⇒ nothing clipped/overflowing. If a single diagram must be eyeballed and vision is unavailable, only then fall back to `browser_vision` if a browser session exists.

## Pitfalls & Lessons Learned

- **LLM Code Generation for Complex PDF:** Free-tier LLMs may struggle to produce complex, standard-library-only PDF generation scripts reliably. Prefer: (1) LLM generates *content*; (2) a pre-validated, hand-authored script assembles the PDF.
- **Network Egress Blocks:** Direct API calls to some LLM providers (Groq, Cerebras, HF, Nous Portal direct) may be blocked from sandbox environments due to ASN reputation (Cloudflare 1010), DNS allowlisting, or rate limits. Route through Hermes's native gateway/OAuth path where available. See `references/network-egress-llm-blocks.md`.
- **Architecture ↔ Model Routing Alignment:** When reviewing an agentic architecture spec against an existing model routing matrix (Excel), verify these integration points:
  - **Terminology unification**: Architecture's "recipe" (cheapest-correct model per sub-task) = Model Selection's `SEQ_*` per USE_AS category. Pick one term and use everywhere.
  - **Slot 0 (Local) missing**: Architecture Section 12 assumes "Local: Qwen2.5-1.5B + bge-m3" as the first escalation tier, but model routing matrices often start at Slot 1 (Nous). Add local tier before Nous in `Category_Sequence`.
  - **Vision single-point-of-failure**: Free tier has ONLY `nvidia/nemotron-nano-12b-v2-vl:free` (OpenRouter) for vision. If it fails/rate-limits, gap → paid (Gemini) → approval. Architecture should flag this.
  - **NIM lifetime limit**: NVIDIA NIM free tier is ONE-TIME lifetime credit. Router MUST treat exhaustion as irreversible — no retry, skip straight to paid. Hard-code this in exhaustion handling.
  - **Nous Portal = Gateway-verified only**: Nous models (tencent/hy3:free, hy3.1:free, deepseek-v3.2:free, etc.) work via Hermes gateway OAuth, NOT direct API. Label them "Gateway-verified" in matrices; direct calls 403 on token expiry.
  - **Probe→Router wire**: Architecture's Model Gateway pre-call stage must consume LIVE probe data (15-min TTL), not just static `Category_Sequence`. Build this wire in Phase 3.
  - **Genuinely open items**: Architecture Section 33 names two items that cannot be resolved by architects: (1) Right-to-erasure vs immutable Audit Log — design Audit Log with cryptographic erasure (tenant key destruction) as default mechanism, parameterize policy; (2) True cross-region catastrophic failover — document as v2 infrastructure decision, build v1 single-region with solid in-region DR.

## Linked references
- `references/high_contrast_and_diagram_verification.md` — high-contrast palette, fixed reportlab box() helper, A3 landscape master-diagram recipe, combined landscape-cover + portrait-body PDF, and programmatic verification when vision is unavailable.
- `references/network-egress-llm-blocks.md` — detailed breakdown of observed egress blocks.
