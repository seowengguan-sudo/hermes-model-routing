---
name: architecture-doc-pdf
category: productivity
description: Overlap-free reportlab architecture PDFs with diagrams.
---

# Architecture / Design PDF (reportlab Platypus)

Generate professional, print-ready architecture specification PDFs: multi-section documents, dense tables, and embedded flow-chart diagrams. Use this (NOT hand-rolled stdlib PDF) whenever reportlab is available. This is the verified workflow used to produce the Hermes Meta-Intelligence architecture spec (7-page PDF + standalone loop diagram).

## When to use
- User asks for a professional architecture / design / system-spec document as a PDF.
- Deliverable needs tables AND diagrams AND clean multi-page layout.
- Pair with an Excel/CSV data source (e.g. a model-selection matrix).

## Environment setup
```bash
uv venv hermes-venv && source hermes-venv/bin/activate && uv pip install reportlab pymupdf openpyxl
```
(Project used /opt/data/architecture with a hermes-venv; PEP 668 / no pip → use uv.)

## Workflow
1. Build content as a list of `flowables` (Paragraph, Table, Spacer, PageBreak, custom Flowable).
2. **Wrap every table cell in a Paragraph** (see references/reportlab_table_wrapping.md) — NEVER pass raw strings to Table cells.
3. For flow charts, subclass `Flowable` and draw with reportlab.graphics primitives (see references/flowchart_diagram.md).
4. `doc.build(story)`.
5. **VERIFY visually** (scripts/verify_pdf.py): render pages to PNG and run vision_analyze for overlap / overflow / column collision.

## Critical pitfall #1 — the #1 cause of "overlapping text"
Raw strings in reportlab `Table` cells do NOT wrap. Long cells overflow horizontally into the next column and look like clashing/overlapping text. The fix is to wrap every cell in a `Paragraph` with a small font (7–9pt) for dense tables. This single change resolves the most common complaint about ugly/overlapping PDF tables. A user WILL flag overlap if you skip it.

## Critical pitfall #2 — LOW CONTRAST / washed-out formatting (legibility)
A sharp, non-overlapping PDF is NOT enough. Users WILL reject light-tint palettes as "not sharp / not friendly for reading." Use a HIGH-CONTRAST scheme (verified in the Hermes v3.5 architecture docs after a user rejection):
- **Saturated fills, not pastels**: deep navy `#1F3864`, blue `#2E5C9E`, green `#2E7D32`, amber `#B7791F`, red `#B91C1C`, purple `#6B2C91`. NEVER pale tints like `#D9E1F2`/`#E2EFDA`/`#FCE4D6` for box fills.
- **White BOLD text** on every colored box/header → maximum legibility.
- **Dark stroke outlines** (1.3–1.4pt, NOT thin grey `#BFBFBF`) on every diagram box so edges stay crisp.
- **Dark caption/legend/footnote text** (`#333`, NOT `#555`/`#7F7F7F`) — faint grey reads as "soft."
- **Table grid lines** at least `#888` (not `#BFBFBF`); zebra stripe `#EEF2F8` (subtle, not pale-blue wash).
- **Box-label font ≥ 8pt** (not 7.6) so small boxes stay readable.
- Colour palette + reusable helpers live in references/high_contrast_palette.md — import those constants instead of inventing hex values.
VISUAL-VERIFY with vision_analyze on a rendered PNG; explicitly ask "is contrast good / any low-contrast or washed-out areas?" Do not declare done on a tinted palette.

## Critical pitfall #3 — MIXING THE REAL AGENT WITH SPECULATIVE DESIGN (explanation framing)
When the user asks "how does Hermes work / how does a request flow," they mean the **actual default agent that is running now**, not a future architecture you designed. A user WILL push back ("set the design aside, explain how you currently work") if you answer from speculative specs.
- **Explain the real default agent**: one active model per session (chosen by runtime config/profile, NOT per-task routing); context = system prompt + auto-injected MEMORY.md/USER.md + skills index + this-session history + new message; skills are on-demand context injected via `skill_view` (not auto-run code); `delegate_task` spawns isolated leaf subagents with their own context/terminal; memory is a disk file auto-injected every turn; model switching is config/approval-level, not an in-loop router.
- **Keep designed/future architectures in a SEPARATE, clearly-labeled doc** (e.g. "v3.6 proposed spec"). Never present a design as the running system. State the residual honestly: "this is the verified contract; the runtime is not built."
- If the user explicitly says "set the design aside / explain the real agent," drop all speculative material for that answer.

## Critical pitfall #4.5 — KeepTogether misuse causes content to disappear or overlap

When wrapping table-heavy sections that span pages, wrapping in a `KeepTogether([])`
list can cause ReportLab to overflow frames silently if the content is too large for
the remaining space. This was observed when building the MVP table in the OAKAI
Mission Executive PDF.

**Fix:** For tables that are long but not critical to keep together, wrap the *table*
in KeepTogether but let section headers break naturally. For short tables (< 8 rows),
always wrap in KeepTogether. For longer content, use `NextPageTemplate` + `PageBreak`
before the table instead of relying on KeepTogether.

```python
# ❌ DON'T: large table in KeepTogether (overflow risk)
story.append(KeepTogether([section_header(...), status_table(big_rows, ...)]))

# ✅ DO: separate section header from long table
story += section_header("03", "Business Model", "...")
story.append(PageBreak())  # ensure table starts clean
story.append(KeepTogether([status_table(medium_rows, ...)]))  # 4-8 rows = safe
```

## Critical pitfall #4 — NO HOLISTIC OVERVIEW; TOO MANY GRANULAR DIAGRAMS
Users find a pile of narrow diagrams (topology, chain, gate, 20-step loop, feedback…) HARDER to grasp than ONE coherent whole-system view. When documenting a whole architecture:
- **Lead with ONE master/holistic diagram** that shows the entire system at a glance (user → intake → core → state → specialists/models → feedback loops), then drill into granular diagrams/tables afterward.
- **Embed the master diagram as the opening view** of the consolidated PDF (landscape cover page) so the reader gets the big picture first.
- Technique + verified build approach: references/holistic_overview.md.

## Layout tips
- Margins 12mm ⇒ 186mm usable width on A4.
- Row striping (alternating fill) improves scanability.
- Put a flow-chart BEFORE its equivalent reference table so readers get the visual first.
- Colour-code by category (e.g. green=local/learning, amber=guard/verify/gate, blue=routing/budget) with a legend.

## Verification checklist
- `pymupdf` open → assert page count; extract text to confirm content present.
- Render to PNG (dpi 110) and vision_analyze each dense page for overlap / overflow / column collision AND contrast ("is contrast good / any low-contrast or washed-out areas?") BEFORE declaring done. Tinted pastel palettes fail this check.
- Reuse templates/architecture_pdf_skeleton.py as the starting scaffold.

## References
- references/reportlab_table_wrapping.md — the cell-wrapping fix + reusable high-contrast table() helper.
- references/flowchart_diagram.md — FlowChart Flowable for control-loop / process diagrams.
- references/high_contrast_palette.md — saturated fills, dark strokes, dark caption text; the palette to use (replaces pastel tints a user rejected).
- references/holistic_overview.md — master/whole-system diagram: A3 direct-canvas build + embed as cover.
- references/two_tier_pdf_strategy.md — decision framework for choosing OAKAI template engine vs stdlib writer.
- references/verification_pitfalls.md — critical pitfalls: KeepTogether overflow, ReportLab version diffs, PDF header assertion bugs, lazy-packages path, ad-hoc verification pattern.

## Overlap note for the curator
This class of work also touches `pdf` (reportlab create), `documentation-generation` (stdlib PDF), and `architecture-diagram` (SVG/HTML, protected). Those are either protected (bundled) or method-mismatched (stdlib). This skill captures the verified reportlab+Platypus+diagram path. Consider consolidating the reportlab-creation guidance here vs `pdf`.
