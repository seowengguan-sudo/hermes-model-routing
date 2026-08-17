#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermes Agent Architecture PDF generator.
Live runtime: tencent/hy3:free @ Nous, HERMES_HOME=/opt/data.
Output: /opt/data/workspace/hermes-agent-architecture.pdf
Venv:   /opt/data/hermes-pdf (reportlab 5.0 + pymupdf/fitz)"""
import os,math
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,A3,landscape,portrait
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import (BaseDocTemplate,PageTemplate,Frame,NextPageTemplate,
    PageBreak,Paragraph,Table,TableStyle,Spacer)
from reportlab.lib.enums import TA_LEFT,TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import fitz

N='#'
NAVY=colors.HexColor(N+'1F3864');BLUE=colors.HexColor(N+'2E5C9E');GREEN=colors.HexColor(N+'2E7D32')
AMB=colors.HexColor(N+'B7791F');RED=colors.HexColor(N+'B91C1C');PUR=colors.HexColor(N+'6B2C91')
CAP=colors.HexColor(N+'333333');GRD=colors.HexColor(N+'888888');RW=colors.HexColor(N+'EEF2F8');W=colors.white
OUT='/opt/data/workspace/hermes-agent-architecture.pdf'
TMP='/opt/data/workspace/_master.pdf';PNG='/opt/data/workspace/_master.png'
ss=getSampleStyleSheet()
C=ParagraphStyle('C',parent=ss['BodyText'],fontSize=8.2,leading=10.5,spaceAfter=0)
CH=ParagraphStyle('CH',parent=ss['BodyText'],fontSize=8.5,leading=10.5,textColor=W,fontName='Helvetica-Bold',spaceAfter=0)
CS=ParagraphStyle('CS',parent=C,fontSize=7.2,leading=8.8)
B=ParagraphStyle('B',parent=ss['BodyText'],fontSize=10,leading=14.5,spaceAfter=7,alignment=TA_LEFT,textColor=CAP)
H1=ParagraphStyle('H1',parent=ss['Heading1'],fontSize=16,leading=19,spaceAfter=7,textColor=NAVY)
H2=ParagraphStyle('H2',parent=ss['Heading2'],fontSize=13,leading=16,spaceAfter=5,textColor=BLUE)
T=ParagraphStyle('T',parent=ss['Title'],fontSize=22,leading=26,spaceAfter=5,alignment=TA_CENTER,textColor=NAVY)
S=ParagraphStyle('S',parent=ss['BodyText'],fontSize=11,leading=15,spaceAfter=8,alignment=TA_CENTER,textColor=CAP)
def wc(data,sm=False):
    r=[]
    for i,row in enumerate(data):
        st=CH if i==0 else(CS if sm else C)
        r.append([Paragraph(str(c),st) for c in row])
    return r
def ht(data,wd=None,sm=False,hdr=NAVY):
    r=wc(data,sm)
    if wd is None:wd=[(176/len(r[0]))*mm]*len(r[0])
    t=Table(r,colWidths=wd,hAlign='LEFT')
    st=[('GRID',(0,0),(-1,-1),0.4,GRD),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),
        ('TOPPADDING',(0,0),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(-1,-1),2.5),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[W,RW])]
    if len(r)>1:st+=[('BACKGROUND',(0,0),(-1,0),hdr),('TEXTCOLOR',(0,0),(-1,0),W)]
    t.setStyle(TableStyle(st));return t

# ── master diagram (A3 landscape, direct canvas) ─────────────────────────
def draw_master():
    c=canvas.Canvas(TMP,pagesize=landscape(A3));PW,PH=landscape(A3);c.setPageSize((PW,PH))
    M=15*mm;X0,Y0=M,M;VW=PW-2*M;VH=PH-2*M
    def b(x,y,wd,h,txt,fill,fs=8.5):
        c.setFillColor(fill);c.setStrokeColor(colors.HexColor(N+'0f172a'));c.setLineWidth(1.3)
        c.roundRect(X0+x*mm,Y0+y*mm,wd*mm,h*mm,4,fill=1,stroke=1)
        c.setFillColor(W);c.setFont('Helvetica-Bold',fs);lines=txt.split('\n')
        th=len(lines)*(fs+1.8);ty=Y0+y*mm+(h*mm-th)/2+fs/2
        for ln in lines:c.drawCentredString(X0+x*mm+wd*mm/2,ty,ln[:24]);ty-=fs+1.8
    def a(x1,y1,x2,y2,col=GREEN,w=1.1):
        c.setStrokeColor(col);c.setLineWidth(w);c.line(X0+x1*mm,Y0+y1*mm,X0+x2*mm,Y0+y2*mm)
        ang=math.atan2(y2-y1,x2-x1);L=2.5
        c.line(X0+x2*mm,Y0+y2*mm,X0+(x2-L*math.cos(ang-.35))*mm,Y0+(y2-L*math.sin(ang-.35))*mm)
        c.line(X0+x2*mm,Y0+y2*mm,X0+(x2-L*math.cos(ang+.35))*mm,Y0+(y2-L*math.sin(ang+.35))*mm)
    def l(x,y,txt,fs=5.5,col=CAP):
        c.setFillColor(col);c.setFont('Helvetica-Oblique',fs);c.drawCentredString(X0+x*mm,Y0+y*mm,txt)
    c.setStrokeColor(colors.HexColor(N+'1e293b'));c.setLineWidth(0.3)
    for gx in range(24,int(VW),24):c.line(X0+gx,Y0,X0+gx,Y0+VH)
    for gy in range(24,int(VH),24):c.line(X0,Y0+gy,X0+VW,Y0+gy)
    b(0,VH-6,VW,8,"HERMES AGENT ARCHITECTURE",NAVY,11)
    l(VW/2,VH-2,"tencent/hy3:free @ Nous • HERMES_HOME=/opt/data • container-sandboxed",5,W)
    UY=VH-16
    b(12,UY-14,42,12,"USER",BLUE,9);l(33,UY-17,"TUI/CLI/Dashboard",4.2)
    b(62,UY-14,52,12,"ACTIVE LLM",GREEN,9);l(88,UY-17,"one session model",4.2)
    a(54,UY-8,62,UY-8,GREEN,1.3);l(58,UY+2,"prompt\ntext only",4,GREEN)
    RY=UY-32;RH=24;RX=10;RW=VW-20
    c.setFillColor(colors.transparent);c.setStrokeColor(AMB);c.setLineWidth(1.4);c.setDash(1.5)
    c.roundRect(X0+RX,Y0+RY,RW, RH, 6, fill=0, stroke=1);c.setDash()
    c.setFillColor(AMB);c.setFont('Helvetica-Bold',7.5)
    c.drawString(X0+RX*mm+4,Y0+(RY+RH)*mm-2,"RUNTIME CORE /opt/hermes LINUX CONTAINER")
    b(RX+2,RY+RH-6, RW-4, 5, "CONTEXT\n(sys+M+idx+hist+msg)",PUR,5)
    by=RY+3;bh=14;bw=(RW-22)/4
    bl=[("MEMORY\n/opt/data\nstate.db",BLUE),("SKILLS\n71+85 dirs",GREEN),("TOOLSETS\nterm/web/exec",AMB),("SANDBOX\nfs only",RED)]
    for i,(t,fill) in enumerate(bl):b(RX+4+i*bw,by,bw-2,bh,t,fill,6)
    a(56,UY-14,58,RY+RH-3,GREEN,1);l(57,RY+RH-6,"1 response",4,GREEN)
    DL=RY-8;DH=16
    b(10,DL-16,38,DH,"GATEWAY\ns6 pid154",RED,6);l(29,DL-19,"uptime 89255s",4,W)
    b(52,DL-16,42,DH,"WATCHDOG\n2min cron",AMB,6);l(73,DL-19,"reboot guard",4,W)
    a(48,DL+1,52,DL+1,AMB,1);l(50,DL+4,"invokes",4,AMB)
    b(104,DL-16,40,DH,"SCRIPTS\n/opt/data/s/",GREEN,6)
    b(152,DL-16,46,DH,"CRON\n9 jobs",PUR,6);l(175,DL-19,"no_agent+agent",4,W)
    b(210,DL-16,34,DH,"MCP\n(optional)",BLUE,6)
    l(VW/2+8,DL-19,"DELIVERY LAYER — messaging/bridge/cron",4,CAP)
    l(VW/2,-2,"Hermes Agent Architecture • 2026-08-16 • verified from live runtime",4,W)
    c.showPage();c.save()

def cover_page(cv,doc):
    cv.setPageSize(landscape(A3));PW,PH=landscape(A3);M=12*mm
    try:
        img=ImageReader(PNG);iw,ih=img.getSize()
        TW=PW-2*M;TH=PH-2*M;sc=min(TW/iw,TH/ih)
        cv.drawImage(img,M+(TW-iw*sc)/2,M+(TH-ih*sc)/2,iw*sc,ih*sc)
    except Exception as e:
        cv.setFont('Helvetica',18);cv.drawCentredString(PW/2,PH/2,f"[render: {e}]")
    cv.setFillColor(NAVY);cv.rect(0,PH-18, PW,18, fill=1, stroke=0)
    cv.setFillColor(W);cv.setFont('Helvetica-Bold',9)
    cv.drawCentredString(PW/2,PH-6,"Hermes Agent — TUI + Dashboard Architecture (Live Runtime)")

# ── build the full document ───────────────────────────────────────────────
def build():
    draw_master()
    d=fitz.open(TMP);p=d[0];px=p.get_pixmap(dpi=170);px.save(PNG);d.close()
    doc=BaseDocTemplate(OUT,page_size=portrait(A4),leftMargin=15*mm,
                        rightMargin=15*mm,topMargin=15*mm,bottomMargin=15*mm)
    cov=PageTemplate(id='cover',frames=[],onPage=cover_page)
    bod=PageTemplate(id='body',frames=[Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height)])
    doc.addPageTemplates([cov,bod])
    st=[NextPageTemplate('cover'),PageBreak(),NextPageTemplate('body')]

    # P1: Context Pipeline
    st+=[Paragraph("Context Pipeline",H1)]
    st+=[Paragraph("The active context is rebuilt every turn and sent as ONE request to the single pinned model:",B)]
    st+=[ht([["Step","Source","Type","Persists"],["1","System prompt (bundled)","static","no"],
        ["2","MEMORY.md + USER.md","auto-injected","yes — disk file"],["3","Skills INDEX (names only)","flat list","no"],
        ["4","Conversation history (this session)","compactable","no"],["5","New user message","input","no"]])],
    st.append(Spacer(1,4))
    st+=[Paragraph("History compaction: oldest verbatim turns are summarized+dropped when context grows; gist retained. Across sessions, history resets — only MEMORY.md/USER.md and state.db persist (via session_search).",B)]
    st.append(PageBreak())

    # P2: Model + Skills
    st+=[Paragraph("Model Selection & Skills",H1)]
    st+=[Paragraph("Two frequent misreadings: (1) there is NO free-tier model router in the default agent, (2) the 81 skill count reconciles 71 bundled + 85 profile (not a leak).",B)]
    st+=[Paragraph("2.1 Model selection",H2)]
    st+=[ht([["Aspect","Reality","Misconception"],["Routing","Profile/config — ONE active model per session","Per-task router"],
        ["Model","tencent/hy3:free (pinned)","Multi-model auto-switch"],["Free-tier","NOT in default agent (was a design spec)","Auto-routed across providers"],
        ["Paid","Explicit UI approval only","Autonomous escalation"]],sm=True)]
    st.append(Spacer(1,4))
    st+=[Paragraph("2.2 Skills: two directories",H2)]
    st+=[ht([["Directory","Location","Count","Role"],["Bundled","/opt/hermes/skills/","71","shipped core set"],
        ["Profile","/opt/data/skills/","85","edits/learns (incl .hub/)"],["Hub cache","/opt/data/skills/.hub/","LobeHub","browsable, not auto-loaded"],
        ["UI total","deduped union − disabled","81","71+85→81"]],sm=True)]
    st.append(PageBreak())

    # P3: Tool Execution
    st+=[Paragraph("Tool Execution & Sandboxing",H1)]
    st+=[Paragraph("All tool execution happens inside the Linux container. Nous (the model provider) only sees the text of tool calls and their results — it cannot see the filesystem.",B)]
    st+=[ht([["Toolset","How it runs","Boundary"],["terminal","Shell in container; python3 interpreter","Container fs only"],
        ["execute_code","Script in session venv python","Same container, persistent venv"],
        ["file (read/write/patch)","Direct OS ops via runtime","Path resolution + lock + staleness"],
        ["web/image/skills","Tool backends (FAL, search APIs)","Same text channel"]])]
    st.append(Spacer(1,4))
    st+=[Paragraph("Limits",H2)]
    st+=[ht([["Limit","Default"],["Timeout (execute_code)","300s"],["Tool calls/turn","50"],["stdout","50 KB"],["stderr","10 KB"],
        ["write_file syntax gate","Fail-closed pre-write lint (new errors only)"]],sm=True)]
    st.append(Spacer(1,4))
    st+=[Paragraph("write_file lint gate (fail-closed): .py→py_compile, .js→node --check, .json/.yaml/.toml→in-process parse, .ts/.go/.rs→shell linter. Returns verified:true = on-disk hash confirmed.",B)]
    st.append(PageBreak())

    # P4: Cron + Delivery
    st+=[Paragraph("Cron Daemon & Delivery Layer",H1)]
    st+=[Paragraph("The Cron Daemon (9 jobs) runs via s6 supervision under the Messaging Gateway.",B)]
    st+=[Paragraph("Job split",H2)]
    st+=[ht([["Type","Jobs","Execution","Output"],["no_agent","watchdog, git-push, cleanup, catchup","Script only — stdout verbatim","Silent = success"],
        ["agent","mentor, pensolar, coo, marketing","LLM reasoning on prompt","Reasoned briefing"]])]
    st.append(Spacer(1,4))
    st+=[Paragraph("Path safety: scripts for no_agent crons must reside under /opt/data/scripts/ (sandbox blocks outside). repeat=-1 = infinite. startup-catchup-enforcement is armed + repeat forever.",B)]
    st.append(PageBreak())

    # P5: Memory
    st+=[Paragraph("Memory, State & Persistence",H1)]
    st+=[Paragraph("Three distinct persistence mechanisms — do not conflate them:",B)]
    st+=[ht([["Mechanism","What it is","Scope","How accessed"],["MEMORY.md / USER.md","Durable fact files","Across ALL sessions","Auto-injected every turn"],
        ["state.db (SQLite)","Session store + facts DB","Across ALL sessions","session_search"],
        ["Conversation history","This session's messages","Current session only","In-context; compacted when long"]])]
    st.append(Spacer(1,4))
    st+=[Paragraph("What the model sees: the single model receives system prompt + MEMORY.md + USER.md + skills INDEX + conversational history + the new message. It sees neither the filesystem nor internal state — only this flattened text.",B)]
    st.append(PageBreak())

    # P6: Security
    st+=[Paragraph("Security Model & Data Flow",H1)]
    st+=[Paragraph("The container is a hard boundary. Nous is outside and sees only text.",B)]
    st+=[ht([["Trust zone","Inside","Outside"],["Container (/opt/data, /opt/hermes)","Tools, files, venvs, state.db","—"],
        ["Nous provider channel","Flattened context text (call+result only)","Filesystem/disk"],
        ["Browser (Windows host)","Reads localhost:8765 for doc-reader","Cannot reach internals"],
        ["Browser-use daemon","Headless Chromium (sanitized)","Sandboxed — no file:// or localhost"]])]
    st.append(Spacer(1,4))
    st+=[Paragraph("Data never crosses the boundary in binary form — all tool results are serialized to text before reaching the model.",B)]

    doc.build(st)
    print(f"✅ PDF: {OUT} ({os.path.getsize(OUT)/(1024*1024):.1f} MB)")

if __name__=='__main__':
    build()
