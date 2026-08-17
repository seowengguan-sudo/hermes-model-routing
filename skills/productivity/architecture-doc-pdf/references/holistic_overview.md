# Holistic / Master Architecture Overview Diagram

Verified technique for the ONE whole-system diagram that leads an architecture doc.

## Goal
A single coherent view: user -> intake (inbound/poller) -> agentic core (gate/cost/master/loop/metacog)
-> state model -> router/specialists/model pool, plus the live feedback loops (interrupt, cost/learning,
screening). Embed it as the opening landscape page of the consolidated PDF.

## Build approach that worked (reportlab, A3 landscape)
- Use a DIRECT canvas (`reportlab.pdfgen.canvas.Canvas`, `pagesize=landscape(A3)`), NOT a
  SimpleDocTemplate Flowable. Reason: a big custom Flowable overflowed the A4 portrait frame and
  silently spilled to page 2. Direct canvas with `X(m)=m*mm` helper gives full control and one page.
- A3 landscape = 420 x 297 mm. Keep all boxes within ~x:[8, 404] mm, y:[8, 262] mm.
- Reuse the HIGH-CONTRAST palette (see high_contrast_palette.md): saturated fills, white bold text,
  dark 1.3pt strokes, #333 captions.
- Draw order: zones (dashed rounded rects) first, then boxes, then arrows/curves, then labels, then legend.
- Central "engine": a rounded rect labelled "26-STEP AGENTIC CONTROL LOOP" with an inner dashed circle
  + 6 clockwise labels (Observe/Orient/Decide/Act/Verify/Learn) + an "engine" core label.
- Feedback arcs as bezier curves with a small italic label; dashed purple for async/interrupt.

## Verification (before declaring done)
- pymupdf open -> assert 1 page, size 1191x842 (A3L).
- Render to PNG; scan outer 10px border for non-white pixels -> must be 0 (no clip/overflow).
- vision_analyze (if model supports vision) OR structural text check: all labelled blocks present,
  right-edge box fully on-page (x+width <= 404mm).
- If vision_analyze returns 404 (active model has no vision endpoint - real limitation with tencent/hy3),
  fall back to the border-scan + text-presence check; do NOT claim visual verification you couldn't do.

## Embedding into the consolidated PDF (mixed page sizes)
SimpleDocTemplate cannot easily mix A3 landscape + A4 portrait in one flow. Use BaseDocTemplate with
two PageTemplates: 'cover' (landscape frame) and 'body' (portrait frame), switch via NextPageTemplate.
Cover page draws the title + the master PNG (rendered at dpi~170) scaled to fit; body holds the spec.

## Verification Pattern (from session: oakai_mission_executive.py)

When generating any PDF via the OAKAI template engine, verify with this pattern:

1. **Syntax check**: `ast.parse()` on the .py generator file
2. **Import check**: verify the module loads without errors
3. **End-to-end**: run `build_document()` → assert output file exists + size > 100 bytes
4. **PDF header**: assert `open(path, "rb").read(8).startswith(b"%PDF-1.")`  (note: use startswith, not slice compare)
5. **Content validation**: PyMuPDF opens → extract full text → assert all required sections present
6. **Semantic checks**: assert key concepts appear in text (e.g. "VTDF", "LTV:CAC > 3:1")
7. **Cleanup**: delete temp PDF after verification

```python
# Quick inline verification snippet:
header = open(result, "rb").read(8)
assert header.startswith(b"%PDF-1."), f"Bad header: {header}"
```

Full reference: see `references/two_tier_pdf_strategy.md` (Verification Pattern section)