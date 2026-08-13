---
name: structured-deliverables
description: Edit Excel xlsx and build clean PDFs without corrupting.
category: productivity
---

# Structured Deliverables (Excel .xlsx + PDF)

## When to use
- Editing/extending an existing `.xlsx` (add columns, sheets, rows) — e.g. a model-selection or provider matrix.
- Generating a multi-page, professional PDF from structured data (architecture docs, specs, reports).
- Any "update the Excel / make a neat PDF / it looks messy" request.

## Core technique A — Excel via openpyxl (NEVER text-write)
A `.xlsx` is a ZIP of XML. Writing it with `write_file` (plain text) or a script that prints TSV **destroys it** — the file loses its `PK` ZIP header and won't open ("The excel file cannot open").
- Always: `wb = openpyxl.load_workbook(path)`, mutate cells, `wb.save(path)`.
- Preserve the original: `shutil.copy` a `*_original_backup.xlsx` before overwriting.
- If `openpyxl`/`pymupdf`/`reportlab` missing and pip blocked (PEP 668): `uv venv hermes-venv && source hermes-venv/bin/activate && uv pip install openpyxl pymupdf reportlab`.
- Append capacity/derived columns by locating the header row and writing to `ws.max_column+1` per data row. For per-category lookup sheets, create a dedicated sheet rather than duplicating data across every row.
- Verify: reopen with `openpyxl.load_workbook` and assert new columns/values read back.

## Core technique B — PDF via reportlab (wrap cells in Paragraph)
ReportLab `Table([...])` does **not** wrap raw strings. Long cell text overflows into the next column and **overlaps** — the #1 cause of "the PDF wording looks overlapping / messy". User explicitly requires: neat layout, maximized info density, no overlap.
- Wrap EVERY cell in a `Paragraph(style)` so it flows within the column width.
- Set `colWidths` summing to usable width: A4 with 12 mm margins → **186 mm**.
- Small cell style (~7.6 pt) + `ROWBACKGROUNDS` for density; `TableStyle` with `VALIGN TOP` and ~3 px padding.
- Helper that maps each row's cells through `Paragraph(cell, style)` — including the header row.

## Verify BEFORE claiming done (critical, easy to skip)
- xlsx: reopen with openpyxl; read the new columns back; print a sample row.
- PDF: render each page to PNG with `pymupdf` (`page.get_pixmap(dpi=110)`) and **vision-check** for overlap/overflow/margin violations. A doc that `build()`s without error can still overlap visually.

## Pitfalls
- ❌ Writing xlsx via `write_file` or a TSV print → corrupted, unopenable file. ✅ openpyxl load/save.
- ❌ `Table(data)` with `str` cells → overlap. ✅ `Table([[Paragraph(c,st) for c in row] for row in data])`.
- ❌ Declaring success after `build()` with no visual check. ✅ render + vision verify.
- ❌ English-only embeddings (all-MiniLM-L6-v2) for multilingual clients → mis-ranked retrieval. ✅ BAAI/bge-m3 (100+ languages).
- ❌ Putting a non-capability-matched model in slot 1 (e.g. a text model as "vision", or a general model as "moderation"/'tool-use"). ✅ Match model to category by real capability; use "—" when a tier has no fit and let the router skip.
- ❌ **FALLBACK FLAT-TEXT TRAP** — when the canonical skill template (`oakai_pdf_template.build_document`) fails, errors, or produces empty output, NOT falling back to dumping unstyled paragraphs into `SimpleDocTemplate`—the resulting document is visually flat ("paste text into PDF"), with no headers, footers, section dividers, or brand styling. ✅ Detect template failures via stderr assertion + page-count check; if fallback is unavoidable, wrap ALL content in `Paragraph` objects with proper styles and add a visible error banner at top. NEVER deliver an unbranded, flat-text PDF — it violates the "professional format" requirement.
- ❌ **SKILL IMPORT FALLBACK** — when `/opt/data/skills/PDF/oakai_pdf_template.py` raises `NameError` (e.g., undefined constant like `DOC_DATE`), the generator must surface the error clearly rather than silently producing minimal output. ✅ Always verify skill imports succeed before writing output; log the exact import error to stderr.

## Canonical PDF Skill Integration (Aug 2026 session)
When generating PDFs, ALWAYS use `/opt/data/skills/PDF/oakai_pdf_template.py` via `build_document()`. Do NOT write ad-hoc reportlab layout code. The template provides:
- Deep teal (`#0B3D3D`) headers + gold (`#C69B4B`) accents
- Helvetica fonts (no embedding issues)
- Automatic TOC generation from `toc_entries` list
- Branded footer on every page
- Section headers with numbered badges
- `KeepTogether` wrapping for table row integrity

If the template fails to import or build, STOP and report the error — do not fall back to raw reportlab. See `references/pdf_skill_integration.md` for error-handling patterns observed in production.

## References
- `references/deliverable-snippets.md` — copy-ready openpyxl extend + reportlab wrapping-table + pymupdf render-verify snippets.
- `references/manufacturing_kpi_template.md` — KPI dashboard layout for manufacturing Excel deliverables (Aug 2026 session).
