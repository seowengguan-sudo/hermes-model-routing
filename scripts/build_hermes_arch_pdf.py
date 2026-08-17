#!/usr/bin/env python3
"""Hermes Agent Architecture PDF generator.
Live runtime: tencent/hy3:free @ Nous, HERMES_HOME=/opt/data.
Output: /opt/data/workspace/hermes-agent-architecture.pdf"""
import os, sys, math
sys.path.insert(0, '/opt/data/scripts')
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, landscape, portrait
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame,
    NextPageTemplate, PageBreak, Paragraph, Table, TableStyle, Spacer)
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import fitz
from hermes_pdf_data import P1, P1_FOOT, P2, P2_FOOT, P3, P3_FOOT, P4, P4_FOOT, P5, P5_FOOT, P6, P6_FOOT

N='#';OUT='/opt/data/workspace/hermes-agent-architecture.pdf'
TMP='/opt/data/workspace/_master.pdf';PNG='/opt/data/workspace/_master.png'
NAVY=colors.HexColor(N+'1F3864');BLUE=colors.HexColor(N+'2E5C9E');GREEN=colors.HexColor(N+'2E7D32')
AMB=colors.HexColor(N+'B7791F');RED=colors.HexColor(N+'B91C1C');PUR=colors.HexColor(N+'6B2C91')
CAP=colors.HexColor(N+'333333');GRD=colors.HexColor(N+'888888');RW=colors.HexColor(N+'EEF2F8');W=colors.white
ss=getSampleStyleSheet()
C=ParagraphStyle('C',parent=ss['BodyText'],fontSize=8.2,leading=10.5,spaceAfter=0)
CH=ParagraphStyle('CH',parent=ss['BodyText'],fontSize=8.5,leading=10.5,textColor=W,fontName='Helvetica-Bold',spaceAfter=0)
CS=ParagraphStyle('CS',parent=C,fontSize=7.2,leading=8.8)
B=ParagraphStyle('B',parent=ss['BodyText'],fontSize=10,leading=14.5,spaceAfter=7,alignment=TA_LEFT,textColor=CAP)
H1=ParagraphStyle('H1',parent=ss['Heading1'],fontSize=16,leading=19,spaceAfter=7,textColor=NAVY)
H2=ParagraphStyle('H2',parent=ss['Heading2'],fontSize=13,leading=16,spaceAfter=5,textColor=BLUE)

def wc(data, sm=False):
    r = []
    for i, row in enumerate(data):
        stl = CH if i == 0 else (CS if sm else C)
        r.append([Paragraph(str(c), stl) for c in row])
    return r

def ht(data, wd=None, sm=False, hdr=NAVY):
    r = wc(data, sm)
    if wd is None:
        wd = [(176 / len(r[0])) * mm] * len(r[0])
    t = Table(r, colWidths=wd, hAlign='LEFT')
    ts = [('GRID', (0,0), (-1,-1), 0.4, GRD), ('VALIGN', (0,0), (-1,-1), 'TOP'),
          ('LEFTPADDING', (0,0), (-1,-1), 3), ('RIGHTPADDING', (0,0), (-1,-1), 3),
          ('TOPPADDING', (0,0), (-1,-1), 2.5), ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
          ('ROWBACKGROUNDS', (0,1), (-1,-1), [W, RW])]
    if len(r) > 1:
        ts += [('BACKGROUND', (0,0), (-1,0), hdr), ('TEXTCOLOR', (0,0), (-1,0), W)]
    t.setStyle(TableStyle(ts))
    return t

def draw_master():
    c = canvas.Canvas(TMP, pagesize=landscape(A3))
    PW, PH = landscape(A3); M = 15*mm; X0 = M; Y0 = M
    VW = PW - 2*M; VH = PH - 2*M

    def box(x, y, wd, h, txt, fill, fs=8.5):
        c.setFillColor(fill)
        c.setStrokeColor(colors.HexColor(N+'0f172a'))
        c.setLineWidth(1.3)
        c.roundRect(X0+x, Y0+y, wd, h, 4, fill=1, stroke=1)
        c.setFillColor(W)
        c.setFont('Helvetica-Bold', fs)
        lines = txt.split('\n')
        th = len(lines) * (fs + 1.8)
        ty = Y0 + y + (h - th) / 2 + fs / 2
        for ln in lines:
            c.drawCentredString(X0 + x + wd/2, ty, ln[:28])
            ty -= fs + 1.8

    def arrow(x1, y1, x2, y2, col=GREEN, w=1.1):
        c.setStrokeColor(col); c.setLineWidth(w)
        c.line(X0+x1, Y0+y1, X0+x2, Y0+y2)
        ang = math.atan2(y2-y1, x2-x1); L = 6
        c.line(X0+x2, Y0+y2, X0+(x2-L*math.cos(ang-0.35)), Y0+(y2-L*math.sin(ang-0.35)))
        c.line(X0+x2, Y0+y2, X0+(x2-L*math.cos(ang+0.35)), Y0+(y2-L*math.sin(ang+0.35)))

    def ln(x, y, txt, fs=5.5, col=CAP):
        c.setFillColor(col); c.setFont('Helvetica-Oblique', fs)
        c.drawCentredString(X0+x, Y0+y, txt)

    # grid
    c.setStrokeColor(colors.HexColor(N+'1e293b')); c.setLineWidth(0.3)
    for gx in range(24, int(VW), 24):
        c.line(X0+gx, Y0, X0+gx, Y0+VH)
    for gy in range(24, int(VH), 24):
        c.line(X0, Y0+gy, X0+VW, Y0+gy)

    # header
    box(0, VH-9, VW, 10, 'HERMES AGENT ARCHITECTURE', NAVY, 11)
    ln(VW/2, VH-3, 'tencent/hy3:free @ Nous  HERMES_HOME=/opt/data  container-sandboxed', 5, W)

    UY = VH - 20
    box(12, UY-15, 42, 12, 'USER\nTUI/CLI/Dashboard', BLUE, 9)
    box(62, UY-15, 52, 12, 'ACTIVE LLM\ntencent/hy3:free', GREEN, 9)
    arrow(54, UY-8, 62, UY-8, GREEN, 1.3)
    ln(58, UY+2, 'prompt\ntext only', 4, GREEN)

    # runtime core boundary
    RY = UY - 34; RH = 26; RX = 10; RW = VW - 20
    c.setFillColor(colors.transparent)
    c.setStrokeColor(AMB); c.setLineWidth(1.4); c.setDash(1.5)
    c.roundRect(X0+RX, Y0+RY, RW, RH, 6, fill=0, stroke=1)
    c.setDash()
    c.setFillColor(AMB); c.setFont('Helvetica-Bold', 7.5)
    c.drawString(X0+RX+6, Y0+(RY+RH)-3, 'RUNTIME CORE  /opt/hermes  LINUX CONTAINER')
    box(RX+3, RY+RH-7, RW-6, 5, 'CONTEXT\n(sys+M+idx+hist+msg)', PUR, 5)

    # runtime boxes (evenly spaced)
    by = RY + 2; bh = 14; bw = (RW - 24) / 4
    bl = [['MEMORY\n/opt/data\nstate.db', BLUE], ['SKILLS\n71+85 dirs', GREEN],
          ['TOOLSETS\nterm/web/exec', AMB], ['SANDBOX\nfs only', RED]]
    for i, (t, f) in enumerate(bl):
        box(RX+4+i*bw, by, bw-2, bh, t, f, 6)
    arrow(56, UY-14, 58, RY+RH-3, GREEN, 1)
    ln(57, RY+RH-6, '1 response', 4, GREEN)

    # delivery layer (sibling boxes, no overlap)
    DL = RY - 8; DH = 16
    box(10, DL-16, 38, DH, 'GATEWAY\ns6 pid 154', RED, 6)
    box(52, DL-16, 42, DH, 'WATCHDOG\ncron 2min', AMB, 6)
    arrow(48, DL+1, 52, DL+1, AMB, 1)
    ln(50, DL+4, 'invokes', 4, AMB)
    box(104, DL-16, 40, DH, 'SCRIPTS\n/opt/data/s/', GREEN, 6)
    box(152, DL-16, 46, DH, 'CRON\n9 jobs', PUR, 6)
    box(210, DL-16, 34, DH, 'MCP\n(optional)', BLUE, 6)
    ln(VW/2+10, DL-19, 'Messaging / Bridge / Cron', 4, CAP)
    ln(VW/2+10, DL-13, 'Telegram / Discord / Email / CLI', 4, CAP)

    ln(VW/2, 4, 'Hermes Agent Architecture  2026-08-16  verified from live runtime', 4, W)
    c.showPage()
    c.save()
    return c

def cover_page(cv, doc):
    cv.setPageSize(landscape(A3))
    PW, PH = landscape(A3)
    M = 12*mm
    try:
        img = ImageReader(PNG)
        iw, ih = img.getSize()
        TW = PW - 2*M; TH = PH - 2*M
        sc = min(TW/iw, TH/ih)
        cv.drawImage(img, M+(TW-iw*sc)/2, M+(TH-ih*sc)/2, iw*sc, ih*sc)
    except Exception:
        cv.setFont('Helvetica', 18)
        cv.drawCentredString(PW/2, PH/2, '[master diagram]')
    cv.setFillColor(NAVY)
    cv.rect(0, PH-18, PW, 18, fill=1, stroke=0)
    cv.setFillColor(W)
    cv.setFont('Helvetica-Bold', 9)
    cv.drawCentredString(PW/2, PH-6, 'Hermes Agent Architecture  Live Runtime  2026-08-16')

def build():
    draw_master()
    d = fitz.open(TMP)
    p = d[0]
    px = p.get_pixmap(dpi=170)
    px.save(PNG)
    d.close()
    doc = BaseDocTemplate(OUT, page_size=portrait(A4), leftMargin=15*mm,
                          rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    def body_page(cv, doc):
        cv.setPageSize(portrait(A4))
    cov = PageTemplate(id='cover', frames=[Frame(0, 0, 1, 1)], onPage=cover_page)
    bod = PageTemplate(id='body', frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height)], onPage=body_page)
    doc.addPageTemplates([cov, bod])
    # Page 1: cover (A3, drawn by cover_page onPage)
    # Page 2+: body (A4)
    st = [NextPageTemplate('cover'), NextPageTemplate('body'), PageBreak()]

    st.append(Paragraph('Context Pipeline', H1))
    st.append(Paragraph('The active context is rebuilt every turn and sent as ONE request to the single pinned model:', B))
    st.append(ht(P1, sm=True))
    st.append(Spacer(1, 4))
    st.append(Paragraph(P1_FOOT[0], B))
    st.append(PageBreak())

    st.append(Paragraph('Model Selection & Skills', H1))
    st.append(Paragraph('Two misreadings: (1) NO free-tier model router in default agent, (2) 81 skills = 71+85 deduped.', B))
    st.append(ht(P2, sm=True))
    st.append(Spacer(1, 4))
    st.append(Paragraph(P2_FOOT[0], B))
    st.append(PageBreak())

    st.append(Paragraph('Tool Execution & Sandboxing', H1))
    st.append(Paragraph('All tool execution inside the Linux container. Nous sees only text of calls+results.', B))
    st.append(ht(P3, sm=True))
    st.append(Spacer(1, 4))
    st.append(Paragraph(P3_FOOT[0], B))
    st.append(PageBreak())

    st.append(Paragraph('Cron Daemon & Delivery Layer', H1))
    st.append(Paragraph('Cron Daemon (9 jobs) runs via s6 supervision under the Messaging Gateway.', B))
    st.append(ht(P4, sm=True))
    st.append(Spacer(1, 4))
    st.append(Paragraph(P4_FOOT[0], B))
    st.append(PageBreak())

    st.append(Paragraph('Memory, State & Persistence', H1))
    st.append(Paragraph('Three distinct persistence mechanisms — do not conflate them:', B))
    st.append(ht(P5, sm=True))
    st.append(Spacer(1, 4))
    st.append(Paragraph(P5_FOOT[0], B))
    st.append(PageBreak())

    st.append(Paragraph('Security Model & Data Flow', H1))
    st.append(Paragraph('The container is a hard boundary. Nous is outside and sees only text.', B))
    st.append(ht(P6, sm=True))
    st.append(Spacer(1, 4))
    st.append(Paragraph(P6_FOOT[0], B))

    doc.build(st)
    sz = os.path.getsize(OUT) / (1024*1024)
    print(f'PDF: {OUT} ({sz:.1f} MB)')

if __name__ == '__main__':
    build()
