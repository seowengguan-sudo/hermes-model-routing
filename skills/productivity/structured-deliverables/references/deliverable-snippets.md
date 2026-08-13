# Structured Deliverables — Copy-Ready Snippets

## 1. openpyxl: extend an xlsx (add capacity + per-row derived columns)
```python
import openpyxl
wb = openpyxl.load_workbook('/opt/data/architecture/Provider-Model_FINAL_0.xlsx')
ws = wb['Master Model Matrix']
header = [c.value for c in ws[1]]
# locate where old derived block starts; append after it
base = header[:next(i for i,h in enumerate(header) if h and str(h).startswith('USE_AS_'))]
cap_cols = ['Context Window','Max Output Tokens','Est $/M In','Est $/M Out']
new_header = base + cap_cols + [f'SEQ_{c}' for c in CATS]
for i,name in enumerate(new_header,1): ws.cell(1,i,name)
CAP = { ('NVIDIA NIM','meta/llama-3.1-8b-instruct'): (128000,4096,0,0), ... }  # (ctx,out,in$,out$)
SEQ = { 'vision': ('— (no Nous vision)','nvidia/nemotron-nano-12b-v2-vl:free','— (none)','gemini-2.5-flash'), ... }
for r in range(2, ws.max_row+1):
    prov=ws.cell(r,1).value; model=ws.cell(r,2).value
    if not prov or not model: continue
    ctx,out,ci,co = CAP.get((prov,model),(None,None,None,None))
    col=len(base)+1
    ws.cell(r,col,ctx); ws.cell(r,col+1,out); ws.cell(r,col+2,ci); ws.cell(r,col+3,co)
    for j,c in enumerate(CATS): ws.cell(r,col+4+j, '['+' -> '.join(SEQ[c])+']')
wb.save('/opt/data/architecture/Provider-Model_FINAL_0_v2.xlsx')
```

## 2. openpyxl: verify the write landed
```python
import openpyxl
wb=openpyxl.load_workbook('/opt/data/architecture/Provider-Model_FINAL_0_v2.xlsx')
ws=wb['Master Model Matrix']; h=[c.value for c in ws[1]]
i=h.index('Context Window')+1
print('row2 ctx=', ws.cell(2,i).value, '| SEQ_vision=', ws.cell(2,h.index('SEQ_vision')+1).value)
```

## 3. reportlab: wrap EVERY cell in Paragraph (fixes overlap)
```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib import colors
ss=getSampleStyleSheet()
CELL=ParagraphStyle('CELL',parent=ss['BodyText'],fontSize=7.6,leading=9.6)
CELLH=ParagraphStyle('CELLH',parent=ss['BodyText'],fontSize=7.8,leading=9.8,textColor=colors.white,fontName='Helvetica-Bold')
def wrap(rows):
    out=[]
    for ri,row in enumerate(rows):
        st=CELLH if ri==0 else CELL
        out.append([Paragraph(str(c),st) for c in row])
    return out
def table(data,widths):
    t=Table(wrap(data),colWidths=widths,repeatRows=1)
    t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#BFBFBF')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#305496')),
        ('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),
        ('TOPPADDING',(0,0),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(-1,-1),2.5),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F4F7FC')])]))
    return t
# A4 + 12mm margins => 186mm usable. Sum widths to 186.
doc=SimpleDocTemplate('out.pdf',pagesize=A4,topMargin=12*mm,bottomMargin=11*mm,leftMargin=12*mm,rightMargin=12*mm)
doc.build([table([['H1','H2'],['a long cell that must wrap inside its column and not overflow','b']],[93*mm,93*mm])])
```

## 4. pymupdf: render to PNG + vision-check for overlap
```python
import pymupdf
d=pymupdf.open('out.pdf')
for i in range(d.page_count):
    d[i].get_pixmap(dpi=110).save(f'/tmp/p{i+1}.png')
# then vision_analyze each /tmp/pN.png: "any text overlap, overflow, collision?"
```
