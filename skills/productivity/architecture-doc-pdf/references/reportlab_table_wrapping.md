# reportlab Table Cell-Wrapping Fix (the overlap killer)

## The problem
```python
from reportlab.platypus import Table
# WRONG — raw strings do NOT wrap; long cells overflow into the next column.
Table([['Short', 'A very long cell that overflows horizontally into the next column and looks like overlapping text']], ...)
```

## The fix — wrap every cell in a Paragraph
```python
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, Paragraph

ss = getSampleStyleSheet()
CELL  = ParagraphStyle('CELL',  parent=ss['BodyText'], fontSize=7.6, leading=9.6, spaceAfter=0)
CELLH = ParagraphStyle('CELLH', parent=ss['BodyText'], fontSize=7.8, leading=9.8,
                       textColor=colors.white, fontName='Helvetica-Bold', spaceAfter=0)
CELLS = ParagraphStyle('CELLS', parent=CELL, fontSize=7.0, leading=8.8)  # dense variant

def wrap(rows, small=False):
    out=[]
    for ri,row in enumerate(rows):
        style = CELLH if ri==0 else (CELLS if small else CELL)
        out.append([Paragraph(str(c), style) for c in row])
    return out

def table(data, widths, header=True, small=False, hdr=colors.HexColor('#1F3864')):
    # HIGH-CONTRAST defaults (verified after a user rejected washed-out tints):
    # header fill = navy, grid = #888, zebra = subtle #EEF2F8. See references/high_contrast_palette.md.
    t = Table(wrap(data, small), colWidths=widths, repeatRows=1 if header else 0)
    st = [('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#888888')),
          ('VALIGN',(0,0),(-1,-1),'TOP'),
          ('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),
          ('TOPPADDING',(0,0),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(-1,-1),2.5),
          ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, colors.HexColor('#EEF2F8')])]
    if header: st += [('BACKGROUND',(0,0),(-1,0),hdr), ('TEXTCOLOR',(0,0),(-1,0),colors.white)]
    t.setStyle(TableStyle(st))
    return t
```

## Why this matters
The user flagged "PDF wording inside looks overlapping" — that was exactly this bug (raw strings).
Wrapping cells in Paragraphs makes text flow within the column width. Dense tables use 7–9pt fonts.
Always pass `colWidths` in mm and size columns so the widest cell fits.

## A4 usable width
Margins 12mm each side → 186mm usable. Keep `sum(widths) ≈ 186mm`.
