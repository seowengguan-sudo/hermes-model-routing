# OAKAI PDF Template Engine — Branded Professional Report Generator

## Overview

There is a **custom, user-owned PDF template engine** at:
- **Engine:** `/opt/data/skills/PDF/oakai_pdf_template.py`
- **Style guide:** `/opt/data/skills/PDF/PDF_SKILL.md`
- **Report generator:** `/opt/data/skills/PDF/oakai_report_generator.py`

This is a **user-owned skill** (curator-managed agent cannot edit it). It exists alongside the bundled `productivity/pdf` and `productivity/professional-doc-deliverables` skills. When the user wants **OAKAI-branded professional reports** (executive summaries, COO briefs, board updates), this template engine is the preferred tool.

## When to use the OAKAI template engine

Use the OAKAI template engine instead of the generic `overlap_safe_pdf.py` when:
- The document is a **formal report, brief, or package** (COO briefs, marketing briefs, execution packages, board updates)
- The user wants **consistent branding** (deep teal `#0B3D3D` / `#0F5C56`, warm gold `#C69B4B`, charcoal `#2B2B2B`)
- The document needs a **cover page**, **table of contents with page numbers**, **section headers**, and **footers** with "OAKAI Confidential" + running page number
- The user explicitly says "use the OAKAI template" or "make it look like the previous report"

## When to use the generic professional-doc-deliverables engine

Use the generic engine (`overlap_safe_pdf.py`) when:
- The document is a **one-off, ad-hoc report** without branding requirements
- The user needs **diagrams/flow-charts** (the OAKAI template doesn't handle diagrams)
- The user wants **quick iteration** without cover pages or TOCs
- You need `KeepTogether` for table+caption combos but not branded footers

## OAKAI Template Engine API

```python
from oakai_pdf_template import *

# Build content story
story = []
story += section_header("01", "Executive Summary")
story.append(Paragraph("...", styles["Body"]))
story.append(status_table([["Metric", "Value"], ["Sessions", "5"]]))
story += checklist(["Item 1", "Item 2"])
story.append(kv_callout_box("Note", ["line 1", "line 2"]))

# Build document (cover + TOC + content)
build_document(
    content_story=story,
    out_path="/mnt/user-data/outputs/report.pdf",
    doc_title="Q3 Architecture Review",
    doc_subtitle="Internal — OAKAI Confidential",
    doc_date="2026-08-13",
    doc_ref="OAKAI-ARC-2026-Q3",
    prepared_for="OAKAI Leadership",
    classification="Confidential",
    toc_entries=[("01", "Executive Summary", "3"),
                 ("02", "Technical Findings", "7"),
                 ("03", "Recommendations", "12")],
)
```

## Key Differences from Generic Template

| Feature | OAKAI Template (`skills/PDF/`) | Generic (`professional-doc-deliverables`) |
|---|---|---|
| Cover page | ✅ Branded teal-gold | ❌ None |
| Footer on every page | ✅ "OAKAI Confidential" + page number | ❌ Manual |
| Table of Contents | ✅ Auto-generated with page numbers | ❌ Manual |
| Color palette | ✅ Brand-defined (teal/gold/charcoal) | ❌ None (monochrome) |
| Fonts | ✅ Helvetica/Helvetica-Bold | ✅ Helvetica |
| Helper functions | ✅ All content via helpers | ✅ `safe_table()` for table overlap |
| Diagram support | ❌ None (no Flowable subclass) | ✅ `FlowChart` Flowable subclass |
| `[VERIFY]` source discipline | ✅ Enforced | ❌ None |
| Build checklist | ✅ Documented | ❌ None |

## Usage Pattern

```python
from oakai_pdf_template import *

story = []
story += section_header("01", "Executive Summary")
story.append(Paragraph("...", styles["Body"]))
story.append(status_table([["Metric", "Value"], ["Sessions", "5"]]))
story += checklist(["Item 1", "Item 2"])
story.append(kv_callout_box("Note", ["line 1", "line 2"]))

build_document(story,
    doc_title="Report Title",
    doc_subtitle="Subtitle",
    doc_date="2026-08-13",
    doc_ref="REF-001",
    prepared_for="Client",
    classification="Confidential",
    toc_entries=[("01", "Section Title", "3")])
```

## Build Checklist (Before Presenting)

- [ ] Cover page renders with full-bleed teal background + gold accent
- [ ] TOC page numbers match actual rendered pages (verify after build)
- [ ] No table header appears alone at bottom of a page (use KeepTogether)
- [ ] Every checklist uses `checklist()` helper (not raw Paragraph with •)
- [ ] Footer shows "OAKAI Confidential" + running page number
- [ ] Any fee, date, or legal claim has a source or flagged `[VERIFY]`