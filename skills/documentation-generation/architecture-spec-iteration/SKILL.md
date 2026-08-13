---
name: architecture-spec-iteration
description: Rescreen architecture specs with their Excel data models.
---

# Architecture Spec Iteration (audit → fix → verify)

Recurring class of work for this user: a design/solution architecture lives as a **PDF spec** plus a **companion data model** (usually an `.xlsx` "source of truth" matrix). The user repeatedly asks to rescreen the architecture for weaknesses, fix them, and keep both artifacts consistent. Treat the two files as one contract — never update one without the other.

## When to use
- "Rescreen / recheck / audit the architecture" · "find weaknesses and fix everything" · "update the documents"
- "Make a clear / professional diagram / flowchart" · "fix the PDF formatting / contrast / overlap"
- Any request naming both a spec doc and a data file and wanting them improved together.

## Workflow
1. **Read the actual artifacts first.** Load the PDF (pymupdf `get_text`) and the xlsx (openpyxl) before claiming anything. Do not reason from memory of prior turns — re-read the current files.
2. **Audit against the explicit bars the user set** (e.g. "continuous self-improvement without hallucination," "cost-efficient agentically," "interruptible"). List concrete gaps as `[ID] problem → fix`, each mapped to the artifact section/sheet it lives in.
3. **Fix in the data model first** (openpyxl), then regenerate the PDF from the data so they cannot drift. Keep the model matrix + any "sequence" columns intact; ADD new sheets/columns rather than overwriting existing data.
4. **Diagrams:** build with reportlab `Flowable` + hand-drawn `box()`/`arrow()` primitives (see references/reportlab_diagrams.md). Two columns + closed-loop arc for control loops; layered stack for topology; top-down split for decision flows.
5. **Verify by rendering, not by assertion.** Render each PDF page with pymupdf `get_pixmap(dpi=110)` and run a vision check for overlap / cutoff / arrow collision / margin overflow / low contrast. Fix and re-render until clean.
6. **State the residual honestly:** these are verified *contracts/specs*, not running code, unless the user explicitly asked to build the runtime.

## Hard rules / pitfalls
- **Never write .xlsx via plain text / echo / TSV** — it corrupts the ZIP container (file will not open). Always `openpyxl.load_workbook` → edit → `save`. (See references/openpyxl_xlsx.md.)
- **High-contrast is mandatory, not optional.** The user explicitly rejected low-contrast pastel tints as "not sharp, not friendly for reading." Use **saturated fills + white bold text + dark stroke outlines (≥1.2pt) + dark caption/legend text (#333, never #555)**. See references/reportlab_diagrams.md for the approved palette.
- **Wrap every table cell and diagram label in a wrapping construct** (reportlab `Paragraph` for tables; manual word-wrap inside `box()` for shapes). Raw strings in table cells do NOT wrap → they overflow into neighbouring columns (the overlap bug).
- **Don't claim a diagram is clean — prove it.** Render + vision-check every diagram page before saying "done."
- **Keep the model matrix + sequence columns untouched** when adding safety sheets; new capability = new sheet/column, not mutation of existing data.
- **One build script per artifact; delete temp scripts after.** Don't leave `verify_*.py` / `build_*.py` littering the workspace.

## Deliverable discipline
- Excel: log sheet count + new rows; confirm SEQ/matrix columns still present after edits.
- PDF: confirm page count + validity (pymupdf page count) + keyword presence.
- Always report what changed in BOTH files.

## References
- `references/reportlab_diagrams.md` — reusable high-contrast Flowable diagram pattern (box/arrow/label helpers, palette, verified loop example).
- `references/openpyxl_xlsx.md` — xlsx corruption fix + venv/uv setup note for this environment.

## Note on overlap
Overlaps with `architecture-diagram` (SVG/HTML, dark-themed) and `pdf` / `pdf-from-stdlib`. Those cover SVG and stdlib-PDF output; this skill covers **reportlab hand-drawn high-contrast flowcharts inside a spec PDF** plus the **dual-artifact (PDF+Excel) audit loop**. Background curator may consolidate.
