---
name: professional-doc-deliverables
description: Build Excel/PDF/diagram deliverables via reportlab+openpyxl.
---

# Professional Document Deliverables (Excel + PDF + Diagram)

Generate professional, versioned architecture/design deliverables — Excel model
matrices, PDF design specs, and flow-chart diagrams — using Python
(reportlab + openpyxl in a venv). Built for iterative client/architecture work
where the **artifact** (not the runtime system) is the deliverable.

## When to use
- User asks to produce, update, or "rescreen" an architecture/design document
  (Excel matrix, PDF spec, diagram).
- Multi-version iteration on the same deliverable (v1 → v2 → … → vN).
- User wants "professional format", "neat layout", "maximize space for information",
  or "diagram / flow chart for better illustration".

## Setup (one-time per workspace)
```
uv venv hermes-venv && source hermes-venv/bin/activate
uv pip install openpyxl pymupdf reportlab
```
(PEP 668 env: no pip module — use `uv`. Memory already notes: **edit xlsx via
openpyxl only** — writing plain text/CSV to a `.xlsx` corrupts the binary.)

## Workflow
1. Inspect current artifact: openpyxl (xlsx) or pymupdf (pdf).
2. Change via openpyxl (xlsx) / reportlab build (pdf). Never hand-edit binary xlsx
   as text, and never re-save xlsx by writing a TSV/plain-text blob.
3. **VERIFY before claiming done:**
   - xlsx: reopen with openpyxl; assert sheets/cols/rows; spot-check key cells
     (e.g. a known SEQ_* value, a capacity int).
   - pdf: pymupdf open → assert page count + `not doc.is_closed`; render the
     *densest* pages to PNG; **vision_analyze the PNG** to confirm no text
     overlap / cutoff / column collision.
4. Clean up temp builder scripts after each build.

## Critical pitfall — reportlab table overlap (the #1 bug here)
Passing a **plain string** into a reportlab `Table` cell does NOT wrap. Long text
overflows into the next column → the "overlapping wording" users complain about.
**FIX:** wrap EVERY cell in a `Paragraph` (small fontSize style). Use a `table()`
helper that maps all rows through `Paragraph(...)`. See `scripts/overlap_safe_pdf.py`.

## Diagram over table for flow illustration
When the user says a flow/process needs "better illustration", build a real
flow-chart, not just a steps table. With no cairosvg/rsvg, draw with reportlab
graphics primitives inside a `Flowable` subclass: `roundRect` (boxes),
`polygon` (diamonds), `line` + arrowheads (arrows), `drawCentredString` (labels).
See `scripts/overlap_safe_pdf.py` `FlowChart` class. Always verify the rendered PNG.

### FlowChart / diagram gotchas (recur every time — see references/reportlab_flowable_pitfalls.md)
- `Flowable.__init__` wants **positional** `(w,h)`, not `width=`/`height=` kwargs.
- A `box()` helper that wraps fill/stroke with `colors.HexColor(...)` again will throw
  `TypeError: unsupported operand '>>'` if you already passed a `Color`. Guard with
  `f = fill if isinstance(fill, colors.Color) else colors.HexColor(fill)` (same for stroke).
- Never default `stroke=tuple(BLUE)` — `BLUE` is a `Color`; pass it directly.
- For multi-line labels, split on `\n` BEFORE words and treat `\n` as a forced break, else
  the newline becomes a literal token that overflows the box.
- Closed-loop return arc: derive its y-centers from the SAME `top`/`rowh`/index math as the
  boxes, or the arc lands off the boxes.

### Architecture-spec diagram checklist (this user's pattern)
When the spec is an agentic architecture (Master-Specialist, model routing, learning loop),
produce a SET of clean diagrams, not one giant table:
1. System Topology (layered stack, color-coded: grey=you/remote, blue=core, green=local/cost).
2. Provider / tier fallback chain (priority waterfall + "on exhaustion" action).
3. Local-first gate (offline pipeline → ~0-cost branch vs LLM branch).
4. The control loop (two columns + closed-loop arc; color by category with a legend).
5. Feedback / self-improvement loop (circular: execute → log → regression → re-rank).
6. (If relevant) Interruption flow (running agent + new prompt → poller → P0/P1/P2 split).
Each diagram on its own page; verify each PNG for overlap/cutoff. The Hermes v3.5 build used
exactly this 6-diagram set across two PDFs (spec + diagrams companion).

## Quality guardrails (avoid over-claiming)
- Do NOT label outputs "flawless" / "hallucination-free" / "totally aware" until the
  mechanism exists. If you describe a verify step, it must actually check what you
  claim (e.g. "factual grounding" must trace claims → sources, not just coherence).
- Distinguish **artifact vs runtime**: this user often wants the DESIGN DOC / MATRIX
  updated, NOT the agent system built. Confirm scope before coding the system.

## Verification loop (reuse)
render → PNG → vision_analyze → fix → re-render. Never skip the vision check;
overlap bugs are invisible in text extraction but visible in the image.

## Support files
- `scripts/overlap_safe_pdf.py` — reusable reportlab helpers: `safe_table()`
  (Paragraph-wrapped cells → no overlap) + `FlowChart` Flowable
  (boxes/diamonds/arrows/closed-loop arc). Copy and extend.
- `references/architecture-matrix-v3.3.md` — finalized model-selection sequences,
  capacity table, provider limits, and verification rules for the Hermes multi-agent
  architecture (swap for other projects).
- `references/reportlab_flowable_pitfalls.md` — the recurring Flowable/diagram bugs
  (`tuple(Color)` TypeError, double `HexColor(Color)`, positional `Flowable.__init__`,
  `\\n` label wrapping, closed-loop arc math) + the non-negotiable render→PNG→vision check.
- `references/oakai-template-engine.md` — for **branded OAKAI reports** (cover page,
  TOC, footer rules, brand palette), use the custom template engine at
  `skills/PDF/oakai_pdf_template.py` instead of the generic helpers here. This is a
  user-owned skill — read it for the API and style rules, but do not edit it.
