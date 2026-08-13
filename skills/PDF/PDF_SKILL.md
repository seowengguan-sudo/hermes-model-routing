# PDF Report Skill — OAKAI Document Standard

## When to use this
Any time a deliverable is a PDF report, brief, or package (COO briefs, marketing
briefs, execution packages, board updates). Do NOT hand-roll a new layout each
time — always start from `oakai_pdf_template.py` in this skill folder and fill
in content. Consistency across documents is the point.

## Non-negotiable structure
1. **Cover page** — full-bleed brand-color background, title, subtitle, a small
   metadata table (Prepared for / Reference / Date / Classification), and a
   footer with "OAKAI Confidential" + "Page 1". No page margins/header rule on
   the cover — it's a different template from the content pages.
2. **Table of Contents** — numbered sections with real page numbers. Update
   these numbers AFTER the first build by counting actual pages, don't guess.
3. **Content pages** — every one gets:
   - A thin top rule with "OAKAI" (left) and doc subtitle (right)
   - A thin bottom rule with "OAKAI Confidential" (left, bold), doc reference
     code (center), "Page N" (right) — N counts from the cover as page 1
4. **Section headers** — two-digit number in accent color, then an H1 title,
   then a colored horizontal rule before body content starts.
5. **Never let a table header split across a page break.** Wrap
   table+caption combos in `KeepTogether([...])`. If a block doesn't fit,
   let it flow whole to the next page — do not leave a half-empty page with
   an orphaned table header floating alone (this is the #1 visible defect
   in unpolished agent-generated PDFs).

## Visual language (fixed — do not reinvent per document)
- Palette: deep teal (`#0B3D3D` / `#0F5C56`) as primary, warm gold (`#C69B4B`)
  as the single accent (used ONLY for rules and the tiny section number —
  never for large fill areas), charcoal body text (`#2B2B2B`), light grey
  table zebra-striping (`#F7FAF9`).
- Fonts: Helvetica / Helvetica-Bold only (built into every PDF reader, zero
  embedding risk). Title 28–30pt, H1 18pt, H2 12–13pt, body 9.5–10pt,
  footer/caption 7.5–8pt.
- Every checklist item, table, and callout box goes through the SAME helper
  function every time (see template file) — never write one-off Paragraph
  styling inline. If a new content shape is needed, add a new helper
  function to the template file and reuse it — don't improvise.

## Content-to-source discipline
- Every fact that has a real-world cost, deadline, or legal requirement
  (registration fees, statutory deadlines, compliance obligations) MUST be
  checked against a live source before being printed in a document — not
  recalled from the model's training data. Malaysian SSM/company-law figures
  in particular change and are commonly confused between business types
  (sole prop vs Sdn Bhd have different fee schedules). If a cost or deadline
  cannot be verified this run, mark it inline as `[VERIFY]` rather than
  printing a confident-looking wrong number.
- If two of your own knowledge-base documents disagree (e.g. one file says
  mentor cadence is 3x/day, another says 4x/day), do not silently pick one —
  surface the conflict to the user and ask which file is canonical.

## Build checklist before presenting the file
- [ ] Cover page renders with no text touching the side accent bar
- [ ] TOC page numbers match actual rendered pages (re-check after build)
- [ ] No table header appears alone at the bottom of a page
- [ ] Every checklist uses the bullet helper (not a raw Paragraph with •)
- [ ] Footer shows "OAKAI Confidential" + running page number on every
      content page, cover included
- [ ] Any fee, date, or legal claim has a source or is flagged `[VERIFY]`
