# PDF Generation — Enhanced Professional Skill

## Two-Tier PDF Strategy

This skill provides **two engines** for PDF generation, each optimized for different needs:

### Tier 1: `/opt/data/skills/PDF/` — OAKAI Professional Design Engine
**Use for:** Professional reports, briefs, packages, any deliverable that needs polished visual quality.
- **Engine:** ReportLab Platypus (full flow layout, automatic text wrapping, table cell wrapping, KeepTogether)
- **Styles:** Centralized color palette, font sizes, paragraph styles — no one-off styling
- **Template:** `oakai_pdf_template.py` — reusable engine with `build_document()`, `section_header()`, `status_table()`, `checklist()`, `kv_callout_box()`
- **Quality features:** Automatic page numbering, headers/footers, two-pass TOC correction, table row preservation across page breaks

### Tier 2: `/opt/data/skills/pdf-from-stdlib/` — Zero-Dependency Fallback
**Use for:** Environments without reportlab, or when you need a valid PDF with zero dependencies.
- **Engine:** Hand-rolled PDF 1.4 writer with correct xref offset tracking
- **Quality:** "Verified openable" by Adobe/Chrome/Preview, but no flow layout, no styling framework
- **Use case:** Fallback only — quality is "readable but not professional"

### `productivity/pdf/` — PDF Utilities (not generation)
Used for: merge, split, fill forms, extract text/tables, watermark, encrypt, OCR.
See that skill for operations on existing PDFs.

---

## When to Use This Skill

Use this skill whenever you need to **generate a PDF document**. The choice between the two tiers depends on:

| Need | Use This Skill | Notes |
|---|---|---|
| Professional report with tables, headers, styled sections | **This skill (PDF/)** | Full ReportLab Platypus engine |
| PDF in a minimal environment (no reportlab installed) | **pdf-from-stdlib** | Hand-rolled writer, no deps |
| Merge/split/fill/encrypt existing PDFs | **productivity/pdf** | Utility operations only |

---

## Tier 1: OAKAI Professional Engine

### File: `oakai_pdf_template.py`

The design engine — import this and use its helpers for every document:

```python
from oakai_pdf_template import (
    build_document, section_header, status_table, checklist,
    kv_callout_box, hr, styles
)
```

### Usage pattern

```python
story = []
story += section_header("01", "Executive Summary", "Verdict TL;DR")
story.append(Paragraph("...content...", styles["Body"]))
story.append(status_table([...rows...], col_widths=[...]))
story += checklist([...items...])
story.append(kv_callout_box("Note", ["..."]))
build_document(story, out_path="/path/out.pdf",
    doc_title="...", doc_subtitle="...", doc_date="...", doc_ref="...",
    prepared_for="...", classification="...", toc_entries=[...])
```

### Key design principles

1. **Never hand-roll a new layout** — always start from `oakai_pdf_template.py`
2. **Every table cell uses a Paragraph** (never raw strings — prevents overlap/overflow)
3. **KeepTogether for table+caption** — prevents orphaned headers across page breaks (the #1 visible defect)
4. **Two-pass TOC** — estimate page numbers, build, then correct with actual counts
5. **Consistent palette** — TEAL_DARK `#0B3D3D`, GOLD `#C69B4B`, CHARCOAL `#2B2B2B`, WHITE, ROW_ALT `#F7FAF9`

### Style reference

| Style Name | Font | Size | Color | Use Case |
|---|---|---|---|---|
| CoverTitle | Helvetica-Bold | 30pt | WHITE | Document title on cover |
| CoverSubtitle | Helvetica | 13pt | TEAL_LIGHT | Subtitle on cover |
| CoverMeta | Helvetica | 9.5pt | `#BFE0DA` | Metadata table on cover |
| SectionNum | Helvetica-Bold | 9pt | GOLD | Section number badge |
| H1 | Helvetica-Bold | 18pt | TEAL_DARK | Section titles |
| H2 | Helvetica-Bold | 12.5pt | TEAL_DARK | Sub-sections |
| Body | Helvetica | 9.7pt | CHARCOAL | Main content |
| BodySmall | Helvetica | 8.8pt | GREY | Captions, notes |
| CellHead | Helvetica-Bold | 8.6pt | WHITE | Table header |
| Cell | Helvetica | 8.6pt | CHARCOAL | Table cells |

### High-contrast requirements (from architecture-doc-pdf)

For **charts, diagrams, and colored boxes** embedded in OAKAI reports, apply these verified rules:

- **Saturated fills, not pastels** — deep navy `#1F3864`, blue `#2E5C9E`, green `#2E7D32`, amber `#B7791F`, red `#B91C1C`, purple `#6B2C91`
- **White BOLD text** on every colored box → maximum legibility
- **Dark stroke outlines** (1.3–1.4pt, NOT thin grey `#BFBFBF`) on every diagram box
- **Dark caption/legend/footnote text** (`#333`, NOT `#555`/`#7F7F7F`)
- **Table grid lines** at least `#888` (not `#BFBFBF`); zebra stripe `#EEF2F8`
- **Box-label font ≥ 8pt** (not 7.6) so small boxes stay readable

### Diagram integration

For flowcharts and architecture diagrams in PDFs:
1. Use `reportlab.graphics.shapes` directly on canvas (not Platypus Flowable) for landscape A3 master views
2. Two-column zig-zag layout for long step lists (≤7 steps per column)
3. Returning arcs for closed loops
4. Color-code: green=local/learning, amber=guard/verify/gate, blue=routing/budget
5. **Verification:** render to PNG (dpi 110) and vision_analyze — check for overlap, low contrast, overflow

### Multi-page size mixing

For documents that need A3 landscape cover + A4 portrait body:
1. Use `BaseDocTemplate` with two `PageTemplate`s
2. Cover template: landscape frame with embedded PNG of master diagram
3. Body template: portrait frame with all content

---

## Tier 2: Zero-Dependency Stdlib Writer

### File: `scripts/pdf_writer.py`

Use ONLY when reportlab is not available:

```python
from pdf_writer import PDF
p = PDF()
p.fillrect(0, 760, 595, 82, 0.12)
p.text(40, 815, "Title", 20, 'F2')
p.text(40, 790, "Subtitle", 11, 'F1')
p.newline()  # start new page
data = p.build()
open('out.pdf', 'wb').write(data)
```

### Constraints of the stdlib writer
- **No flow layout** — every element is manually positioned (x, y)
- **No text wrapping** — long text must be manually split
- **No tables** — no built-in table support, must draw rectangles and text manually
- **No styling framework** — font/color per-element
- **Layout helpers:** `newline()` (flush current page), `fillrect()` (filled rect), `text()` (positioned text)

### Verification (stdlib writer only)
Run this before declaring the PDF done:
```python
import re
d = open('out.pdf','rb').read()
assert d[:8] == b'%PDF-1.4' and b'%%EOF' in d
m = re.search(rb'startxref\s+(\d+)', d); xoff = int(m.group(1))
# xref offset verification — catches the #1 "won't open" cause
```

---

## Build Checklist (Tier 1 — OAKAI Engine)

Before presenting any PDF:
- [ ] Cover page renders with no text touching the side accent bar
- [ ] TOC page numbers match actual rendered pages (re-check after build — two-pass)
- [ ] No table header appears alone at bottom of a page (use `KeepTogether` or let it flow to next page)
- [ ] No table cell overflow (every cell wrapped in `Paragraph`, column widths sized for widest content)
- [ ] Every checklist uses the bullet helper (not raw `•` characters in `Paragraph` — renders as black boxes)
- [ ] Footer shows "OAKAI Confidential" + running page number on every page
- [ ] Color palette is high-contrast (saturated fills, white bold text, dark strokes) — no pastel tints
- [ ] Diagrams verified via PNG render + vision_analyze (or border-scan fallback if no vision)
- [ ] Any fee, date, or legal claim has a source or is flagged `[VERIFY]`
- [ ] If two KB documents disagree, surface the conflict to the user before picking

---

## Integration with Other Skills

| Task | Use This Skill | Related Skill |
|---|---|---|
| Generate styled PDF report | **This (PDF/)** | architecture-doc-pdf (for diagrams) |
| Merge/split existing PDFs | productivity/pdf | This skill (for generation) |
| Edit text in existing PDF | productivity/nano-pdf | This skill (for new PDFs) |
| PDF from HTML/Markdown | (use reportlab.platypus) | documentation-generation (for stdlib fallback) |
| Extract text/tables from PDF | productivity/pdf | This skill (for generation side) |