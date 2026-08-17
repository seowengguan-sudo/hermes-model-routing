# Two-Tier PDF Strategy

## Problem
Two PDF skill systems exist in the agent's skill library:
1. `skills/PDF/` (uppercase) — OAKAI template engine using ReportLab Platypus
2. `productivity/pdf-from-stdlib/` (lowercase) — pure stdlib PDF writer (no deps)

Confusion arises about which to use for professional document generation.

## Decision Framework

### Use the OAKAI Template Engine (`skills/PDF/`) when:
- ✅ ReportLab is available in the environment
- ✅ Document needs professional layout (tables, multi-section, headers/footers)
- ✅ High-contrast branding is important
- ✅ Multi-page documents with automatic flow
- **Default choice for professional deliverables**

### Use the Stdlib Writer (`productivity/pdf-from-stdlib/`) when:
- ✅ ReportLab is **not available** (PEP 668 / no pip / restricted env)
- ✅ Simple text-only output acceptable
- ✅ Zero-dependency guaranteed output needed
- **Emergency fallback only**

## OAKAI Template Engine Architecture

### Design Principles
1. **Single style dict** reused across all helpers (no inline styling drift)
2. **All table cells wrapped in Paragraph** — prevents overflow/overlap (see pitfall #1)
3. **KeepTogether discipline** — prevents orphaned headers/rows across page breaks
4. **Two-pass TOC** — first pass estimates, second pass corrects page numbers
5. **Holistic overview first** — master diagram embedded as cover (see pitfall #4)

### Key Components
- `build_document()` — assembles story + handles cover + content pages
- `section_header(num, title, subtitle)` — consistent section openers
- `status_table(rows, col_widths)` — zebra-striped tables with cell wrapping
- `checklist(items)` — bullet-style checkbox list
- `kv_callout_box(title, bullets)` — highlighted key-value information
- `hr()` — horizontal rule with spacing
- `styles` dict — centralized ParagraphStyle instances
- `TEAL_DARK`, `GOLD`, `CHARCOAL`, `ROW_ALT` — color constants

### High-Contrast Palette (Verified)
```python
# From oakai_pdf_template.py — imported, not invented
TEAL_DARK = HexColor("#0B3D3D")
GOLD      = HexColor("#C69B4B")
CHARCOAL  = HexColor("#2B2B2B")
ROW_ALT   = HexColor("#F7FAF9")

# Enhanced palette from oakai_advanced_template.py
GREEN     = HexColor("#2E7D32")
AMBER     = HexColor("#B7791F")
BLUE      = HexColor("#2E5C9E")
NAVY      = HexColor("#1F3864")
RED       = HexColor("#B91C1C")
PURPLE    = HexColor("#6B2C91")
GREY_FILL = HexColor("#595959")
TABLE_GRID = HexColor("#888888")
```

## Stdlib Writer Architecture

### When ReportLab is unavailable, use this path:
```python
# From productivity/pdf-from-stdlib/scripts/pdf_writer.py
# Pure Python stdlib: zlib, struct, time
# No external dependencies
# Produces valid PDF 1.4 files
```

### Critical limitations:
- No table support (manual column positioning)
- No cell wrapping
- No automatic page flow
- No header/footer template
- Manual y-cursor tracking required

## Decision Flowchart

```
User asks for professional PDF
        ↓
Is ReportLab available?
        ├─ YES → Use oakai_pdf_template.py (OAKAI template engine)
        │          → Apply high-contrast palette
        │          → Use KeepTogether for tables
        │          → Verify with PyMuPDF
        │
        └─ NO  → Use pdf-from-stdlib/scripts/pdf_writer.py
                   → Accept lower layout quality
                   → Manual positioning only
```

## Verification Pattern (Adopted)
Used in this session to validate oakai_mission_executive.py:

1. **Syntax check**: `ast.parse()` on the .py file
2. **Import check**: verify all module-level code loads
3. **End-to-end**: run the generator, assert output file exists + size > threshold
4. **PDF header**: assert `header.startswith(b"%PDF-1.")`
5. **Content validation**: PyMuPDF opens → extract full text → assert required sections present
6. **Semantic checks**: assert key concepts (VTDF, LTV:CAC, Shadow→Canary→Enforce) in text
7. **Cleanup**: delete temp PDF after verification

This pattern works for ANY PDF generator and should be the standard pre-commit verification.
