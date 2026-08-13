#!/usr/bin/env python3
"""Reusable helpers for professional PDF deliverables (reportlab) that DO NOT overlap.

Key lesson: passing a plain *string* into a reportlab Table cell does NOT wrap;
long text overflows into the next column. Fix = wrap every cell in a Paragraph.

Provide your own `story` list (reportlab flowables) and call build_pdf().
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                ListFlowable, ListItem, HRFlowable, PageBreak, Flowable)
import math

NAVY=colors.HexColor('#1F3864'); BLUE=colors.HexColor('#305496')
GREY=colors.HexColor('#F2F2F2'); AMBER=colors.HexColor('#BF8F00'); GREEN=colors.HexColor('#548235')

ss=getSampleStyleSheet()
H1=ParagraphStyle('H1',parent=ss['Heading1'],textColor=NAVY,fontSize=15,spaceAfter=5,spaceBefore=9,leading=18)
H2=ParagraphStyle('H2',parent=ss['Heading2'],textColor=BLUE,fontSize=11.5,spaceAfter=3,spaceBefore=8,leading=14)
BODY=ParagraphStyle('BODY',parent=ss['BodyText'],fontSize=9,leading=12.5,alignment=TA_LEFT,spaceAfter=3)
SMALL=ParagraphStyle('SMALL',parent=ss['BodyText'],fontSize=7.6,leading=9.8,textColor=colors.HexColor('#555555'))
SUB=ParagraphStyle('SUB',parent=ss['Normal'],fontSize=10,textColor=BLUE,spaceAfter=2,leading=13)
TITLE=ParagraphStyle('TITLE',parent=ss['Title'],textColor=NAVY,fontSize=19,spaceAfter=2,leading=22)
CELL=ParagraphStyle('CELL',parent=ss['BodyText'],fontSize=7.6,leading=9.6,alignment=TA_LEFT,spaceAfter=0)
CELLH=ParagraphStyle('CELLH',parent=ss['BodyText'],fontSize=7.8,leading=9.8,textColor=colors.white,fontName='Helvetica-Bold',alignment=TA_LEFT,spaceAfter=0)
CELLS=ParagraphStyle('CELLS',parent=CELL,fontSize=7.0,leading=8.8)

def P(t,s=BODY): return Paragraph(t,s)

def wrap(rows, small=False):
    """Wrap every cell in a Paragraph so reportlab columns wrap (NO overlap)."""
    out=[]
    for ri,row in enumerate(rows):
        st = CELLH if ri==0 else (CELLS if small else CELL)
        out.append([Paragraph(str(c), st) for c in row])
    return out

def safe_table(data, widths, header=True, small=False, hdr=BLUE):
    t=Table(wrap(data,small), colWidths=widths, repeatRows=1 if header else 0)
    st=[('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#BFBFBF')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),
        ('TOPPADDING',(0,0),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(-1,-1),2.5),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F4F7FC')])]
    if header: st+=[('BACKGROUND',(0,0),(-1,0),hdr)]
    t.setStyle(TableStyle(st)); return t

def blist(items, style=BODY):
    return ListFlowable([ListItem(Paragraph(x,style),leftIndent=11,value='•') for x in items],
                        bulletType='bullet', start='•')

def build_pdf(story, out_path, title='Document', author='Hermes Agent', margins=12*mm):
    doc=SimpleDocTemplate(out_path, pagesize=A4, topMargin=margins, bottomMargin=margins*0.9,
                          leftMargin=margins, rightMargin=margins, title=title, author=author)
    doc.build(story)
    return out_path


# ---------------- FlowChart: draw with reportlab graphics (no cairosvg/rsvg) ----------------
class FlowChart(Flowable):
    """Self-contained 2-column closed-loop flow chart using reportlab primitives."""
    def __init__(self, width=186*mm, height=238*mm): self.width=width; self.height=height
    def wrap(self,*a): return (self.width, self.height)
    def draw(self):
        c=self.canv; W=self.width; H=self.height
        c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
        def box(x,y,w,h,text,fill,stroke,fs=8.2):
            c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(0.8); c.roundRect(x,y,w,h,4,fill=1,stroke=1)
            c.setFillColor(colors.white); c.setFont('Helvetica-Bold',fs)
            words=text.split(' '); lines=[]; cur=''
            for wd in words:
                if len(cur)+len(wd)+1<=34: cur=(cur+' '+wd).strip()
                else: lines.append(cur); cur=wd
            if cur: lines.append(cur)
            lines=lines[:3]; th=fs+2; ty=y+h/2+(len(lines)-1)*th/2
            for ln in lines: c.drawCentredString(x+w/2,ty,ln); ty-=th
        def arrow(x1,y1,x2,y2,col=colors.HexColor('#7F7F7F')):
            c.setStrokeColor(col); c.setLineWidth(1.1); c.line(x1,y1,x2,y2)
            ang=math.atan2(y2-y1,x2-x1); L=6
            c.line(x2,y2,x2-L*math.cos(ang-0.4),y2-L*math.sin(ang-0.4))
            c.line(x2,y2,x2-L*math.cos(ang+0.4),y2-L*math.sin(ang+0.4))
        def label(x,y,t,fs=7,col=colors.HexColor('#555555')):
            c.setFillColor(col); c.setFont('Helvetica',fs); c.drawCentredString(x,y,t)
        bw=70*mm; bh=9*mm
        c.setFillColor(NAVY); c.rect(0,H-14*mm,W,14*mm,fill=1,stroke=0)
        c.setFillColor(colors.white); c.setFont('Helvetica-Bold',12); c.drawCentredString(W/2,H-9*mm,self.__class__.__name__)
        top=H-18*mm
        steps=[('1 Example','#E2EFDA',GREEN),('2 Example','#DDEBF7',BLUE),('3 Example','#FCE4D6',AMBER)]
        colx=[W*0.30, W*0.72]; rowh=12.6*mm
        for i,(t,fill,stroke) in enumerate(steps):
            col=0 if i<2 else 1; ridx=i if i<2 else i-2
            bx=colx[col]-bw/2; by=top-4*mm-ridx*rowh
            box(bx,by,bw,bh,t,colors.HexColor(fill),stroke)
            if ridx>0: arrow(bx+bw/2,by+bh+1,bx+bw/2,by+rowh-1)
        ly=14*mm
        c.setFillColor(colors.HexColor('#E2EFDA')); c.roundRect(8*mm,ly,bh,bh,2,fill=1,stroke=1)
        c.setFillColor(colors.HexColor('#FCE4D6')); c.roundRect(60*mm,ly,bh,bh,2,fill=1,stroke=1)
        c.setFillColor(colors.HexColor('#DDEBF7')); c.roundRect(112*mm,ly,bh,bh,2,fill=1,stroke=1)
        c.setFillColor(colors.black); c.setFont('Helvetica',7.5)
        c.drawString(8*mm+bh+2,ly+bh-6,'Green = Local/Learning'); c.drawString(60*mm+bh+2,ly+bh-6,'Amber = Guard/Verify'); c.drawString(112*mm+bh+2,ly+bh-6,'Blue = Routing/Budget')
        c.setFillColor(colors.HexColor('#555555')); c.setFont('Helvetica-Oblique',7)
        c.drawCentredString(W/2,6*mm,'Replace the steps[] list with your own; keep box()/arrow() helpers.')

# USAGE:
#   from overlap_safe_pdf import safe_table, blist, P, H1, build_pdf, FlowChart
#   story=[H1('Title'), safe_table(mydata, [w1,w2,...]), FlowChart(...)]
#   build_pdf(story, 'out.pdf', title='...')
