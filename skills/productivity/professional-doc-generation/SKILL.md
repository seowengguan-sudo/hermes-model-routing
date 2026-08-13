# Professional Document Generation — Unified Skill

## Trigger
**Use when:** The user needs a high-quality professional document in any format — PDF report, Excel matrix, PowerPoint deck, Word document, or web UI. This skill coordinates the existing format-specific skills into a unified professional output pipeline.

## Overview

Professional document generation is a cross-format skill. When the user asks for a deliverable, you must choose the right format for the right purpose, apply the correct design system, and run format-specific verification. This skill provides the decision matrix and unified workflow.

## Format Selection Matrix

Match the deliverable purpose to the format:

| Purpose | Best Format | Why | Key Skill |
|---|---|---|---|
| Executive summary, board presentation, formal report | **PDF** (OAKAI template) | Fixed layout, brand consistency, non-editable | `skills/PDF/SKILL.md` or `skills/PDF/oakai_pdf_template.py` |
| Data analysis, financial modeling, matrices | **Excel (.xlsx)** | Editable numbers, formulas, sorting/filtering | `skills/productivity/xlsx/SKILL.md` |
| Client presentation, pitch deck, meeting deck | **PowerPoint (.pptx)** | Visual-first, slide-by-slide narrative | `skills/productivity/powerpoint/SKILL.md` |
| Contract, formal letter, memo, template | **Word (.docx)** | Editable prose, tracked changes, comments | `skills/productivity/docx/SKILL.md` |
| Interactive prototype, live dashboard, landing page | **HTML/CSS** | Browser-native, interactive, shareable | `skills/creative/claude-design` + `popular-web-designs` |
| Architecture diagram, flow chart, system visual | **SVG/PDF** | Vector precision, scales cleanly | `skills/creative/architecture-diagram` or `professional-doc-deliverables` |

## Unified Professional Document Workflow

### Step 1: Format Selection (before any tool call)
1. **What is the primary use case?** (analysis / presentation / reference / editing)
2. **Who is the audience?** (executives / engineers / clients / public)
3. **How will it be consumed?** (printed / projected / shared / edited)
4. **Does it need interactivity?** (yes → HTML; no → choose from PDF/xlsx/pptx/docx)

### Step 2: Design System Selection
- **OAKAI-branded documents** → use `skills/PDF/oakai_pdf_template.py` (high-contrast teal-gold palette, cover page, footer rules)
- **Standard professional documents** → use `skills/productivity/professional-doc-deliverables` (generic reportlab + openpyxl templates)
- **Web/UI deliverables** → use `skills/creative/popular-web-designs` (54 design systems: Stripe, Linear, Vercel, etc.)
- **Architecture diagrams** → use `skills/productivity/professional-doc-deliverables` references for 6-diagram sets (topology, fallback chain, local-first gate, control loop, feedback loop, interruption flow)

### Step 3: Generator Script Creation
Always create a Python generator script, never inline code. Template:
```python
#!/usr/bin/env python3
"""Generate <deliverable_name>.<ext>"""
import sys, os
sys.path.insert(0, '/opt/data/lazy-packages')
# Add format-specific paths as needed

def build():
    # Use the chosen skill's template/generator
    ...
    return output_path

if __name__ == "__main__":
    build()
```

### Step 4: Ad-Hoc Verification (Format-Specific)
Run the verification script immediately after generation — never skip this step.

| Format | Verification Steps |
|---|---|
| **PDF** | 1. Syntax valid (ast.parse) 2. Module imports work 3. PDF generated (>100 bytes) 4. Valid header (`%PDF-1.`) 5. PyMuPDF reads pages 6. Content sections present 7. Temp file cleaned up |
| **Excel** | 1. Sheet names correct 2. Column count matches spec 3. Key formula cells produce expected values 4. No `#NAME?` or `#VALUE?` errors 5. Number format correct 6. Temp file cleaned up |
| **PowerPoint** | 1. `pptxgenjs` syntax valid 2. Deck opens in PyMuPDF (render check) 3. Slide count matches 4. No placeholder text (`[TODO]`, `lorem`, `???`) 5. `validate.py --original template.pptx` passes 6. Visual QA via `soffice → pdftoppm → vision_analyze` |
| **Word** | 1. Pandoc/markitdown extracts clean text 2. No leftover placeholders 3. Tracked changes properly wrapped 4. Tables render correctly 5. `validate.py --original` passes |
| **HTML** | 1. `write_file` creates valid HTML 2. `soffice --convert-to pdf` succeeds 3. Render → PNG → `vision_analyze` checks layout 4. No text overflow or element overlap |

### Step 5: Commit & Push
- Commit generator script + output to the appropriate skill directory
- Update MEMORY.md and INDEX.md with cross-references
- Push to GitHub with descriptive commit message

## Cross-Format Consistency Rules

### Color Palette (Always Use)
- **OAKAI palette:** TEAL_DARK `#0B3D3D`, GOLD `#C69B4B`, CHARCOAL `#2B2B2B`, ROW_ALT `#F7FAF9`
- **Professional palette:** Navy `#1F3864`, Teal `#028090`, Amber `#B7791F`, Green `#2E7D32`
- **Presentation palette:** Match the `popular-web-designs` system for the chosen brand (e.g., Stripe = `#635BFF` primary)

### Typography Hierarchy (Consistent Across Formats)
| Element | PDF (pt) | PPT (pt) | Word (pt) | Web (px) |
|---|---|---|---|---|
| Document Title | 24-30 | 40-44 | 20-24 | 36-48 |
| Section Header | 14-16 | 20-24 | 14-18 | 20-24 |
| Body Text | 9-10 | 14-16 | 11-12 | 14-16 |
| Caption | 7-8 | 10-12 | 9-10 | 10-12 |

### Table Cell Wrapping Rule (Critical)
**PDF (reportlab):** Always wrap cells in `Paragraph(...)` — plain strings don't wrap and overflow silently.
**Excel:** Excel handles wrapping natively, but ensure column widths accommodate text.
**PowerPoint:** Tables auto-size, but check for overflow at QA step.
**Word:** Tables auto-size, verify rendering after conversion.

## Pitfall Catalog (Cross-Format)

1. **Git race conditions** — Never commit SQLite DBs (`*.db`, `*.db-wal`, `*.db-shm`) during active writes.
2. **Egress awareness** — HF DNS-blocked, Groq/Cerebras WAF-throttled. Use local-first alternatives.
3. **ReportLab table overlap** — Plain strings in cells don't wrap → overflow. Always use `Paragraph`.
4. **PowerPoint file corruption** — Hex colors with `#` or 8 digits corrupt. Use `"FF0000"` format.
5. **Excel formula portability** — LibreOffice can't evaluate `XLOOKUP`, `SORT`, `FILTER`, `UNIQUE`. Use `INDEX`/`MATCH`.
6. **Word XML namespace corruption** — Don't round-trip OOXML through `xml.etree.ElementTree`; use `defusedxml.minidom`.
7. **Python path issues** — `sys.path.insert(0, '/opt/data/lazy-packages')` needed for reportlab/openpyxl.
8. **ReportLab version differences** — API surface changes between versions. Verify against installed version.
9. **Font rendering differences** — QA fonts via LibreOffice may substitute incorrectly. Use safe fonts: Arial, Calibri, Cambria, Times New Roman.
10. **Template slot vs source items** — If template shows 4 items and you have 3, delete the 4th's entire group (image + text boxes), not just text.

## Available Tools Matrix

| Tool | PDF | Excel | PPT | Word | Web | Diagram |
|---|---|---|---|---|---|---|
| `reportlab` | ✅ Primary | — | — | — | — | ✅ (Flowable) |
| `openpyxl` | — | ✅ Primary | — | — | — | — |
| `pptxgenjs` | — | — | ✅ Primary | — | — | — |
| `docx (npm)` | — | — | — | ✅ Primary | — | — |
| `pymupdf/fitz` | ✅ QA/verify | — | ✅ QA render | ✅ QA render | — | ✅ QA render |
| `markitdown` | ✅ Read/extract | ✅ Read/extract | ✅ Content check | ✅ Read/extract | — | — |
| `libreoffice` | ✅ Recalc/verify | ✅ Formula recalc | ✅ Render/validate | ✅ Render/verify | — | — |
| `pypdf/pypdf2` | ✅ Merge/split | — | — | — | — | — |
| `fitz (PyMuPDF)` | ✅ Verify pages | — | ✅ Render slides | ✅ Render pages | — | ✅ Verify |
| `vision_analyze` | ✅ Visual QA | — | ✅ Slide QA | — | ✅ Layout QA | ✅ Diagram QA |
| `soffice` | ✅ Convert | ✅ Recalc | ✅ Render | ✅ Convert | — | ✅ Render |

## References

- **OAKAI PDF Template:** `skills/PDF/oakai_pdf_template.py` — high-contrast palette, cover page, footer rules, `build_document()` API
- **ReportLab Pitfalls:** `skills/productivity/professional-doc-deliverables/references/reportlab_flowable_pitfalls.md`
- **Architecture Diagrams:** `skills/productivity/professional-doc-deliverables/references/architecture-matrix-v3.3.md`
- **Excel Finance Conventions:** `skills/productivity/xlsx/SKILL.md` (Section "Financial models")
- **PowerPoint Design:** `skills/creative/popular-web-designs/SKILL.md` (54 design systems)
- **Deep Research Methodology:** `skills/productivity/deep-research-methodology/SKILL.md`
- **Ad-hoc Verification Pattern:** Embedded in each format's verification step above

## Related Skills

- `pdf` — Generic PDF operations (merge, split, fill forms)
- `PDF` (uppercase) — OAKAI-branded professional PDF reports
- `xlsx` — Excel creation/editing with finance conventions
- `powerpoint` — PowerPoint creation with design QA
- `docx` — Word documents with tracked changes/comments
- `popular-web-designs` — 54 brand design systems for HTML/UI
- `claude-design` — Design process and taste for one-off artifacts
- `architecture-diagram` — SVG architecture diagrams
- `professional-doc-deliverables` — Excel/PDF/diagram deliverables
- `deep-research-methodology` — 5-layer research-to-code framework
