#!/usr/bin/env python3
"""
oakai_advanced_template.py — Enhanced template examples demonstrating
advanced techniques: diagrams, flow charts, multi-page-size mixing.

Usage:
    python3 oakai_advanced_template.py

This module supplements oakai_pdf_template.py with advanced patterns
demonstrated in real Hermes reports. See SKILL.md for the two-tier
PDF strategy and when to use each.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from reportlab.lib.pagesizes import A4, landscape, A3
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
    TableStyle, NextPageTemplate, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Group, Image
from reportlab.graphics import renderPDF
from reportlab.platypus import Flowable

# ── Reuse the OAKAI palette ──
TEAL_DARK  = colors.HexColor("#0B3D3D")
TEAL       = colors.HexColor("#0F5C56")
TEAL_LIGHT = colors.HexColor("#E7F1EF")
GOLD       = colors.HexColor("#C69B4B")
CHARCOAL   = colors.HexColor("#2B2B2B")
GREY       = colors.HexColor("#6E6E6E")
ROW_ALT    = colors.HexColor("#F7FAF9")
BORDER     = colors.HexColor("#D9E2E0")
WHITE      = colors.white

# High-contrast palette (from architecture-doc-pdf/references/high_contrast_palette.md)
NAVY   = colors.HexColor('#1F3864')
BLUE   = colors.HexColor('#2E5C9E')
GREEN  = colors.HexColor('#2E7D32')
AMBER  = colors.HexColor('#B7791F')
RED    = colors.HexColor('#B91C1C')
PURPLE = colors.HexColor('#6B2C91')
GREY_FILL = colors.HexColor('#595959')
TABLE_GRID = colors.HexColor('#888888')
ARROW = '#333333'

# ── Advanced: Color-coded diagram box Flowable ──
class DiagramBox(Flowable):
    """A colored box with wrapped text and a dark stroke — high-contrast palette.
    
    Category colors:
      green  = local/learning/cache
      amber  = guard/verify/gate
      blue   = routing/budget
      navy   = title bands
      red    = abort/destructive
      purple = interrupt/async
    """
    def __init__(self, text, fill_color=GREEN, width=40*mm, height=22*mm, 
                 font_size=8.5, text_color=WHITE):
        self.text = text
        self.fill = fill_color
        self.w = width
        self.h = height
        self.fs = font_size
        self.tc = text_color
        
    def wrap(self, *args):
        return (self.w, self.h)
    
    def draw(self):
        c = self.canv
        # Fill + stroke (1.3pt dark stroke for crispness)
        stroke_color = self._darken(self.fill, 0.7)
        c.setFillColor(self.fill)
        c.setStrokeColor(stroke_color)
        c.setLineWidth(1.3)
        c.roundRect(0, 0, self.w, self.h, 4, fill=1, stroke=1)
        
        # Wrap text inside box
        c.setFillColor(self.tc)
        c.setFont("Helvetica-Bold", self.fs)
        words = self.text.split()
        lines, cur = [], ''
        for wd in words:
            if len(cur) + len(wd) + 1 <= 28:
                cur = (cur + ' ' + wd).strip()
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        
        th = self.fs + 2
        ty = self.h / 2 + (len(lines) - 1) * th / 2
        for ln in lines[:3]:
            c.drawCentredString(self.w / 2, ty, ln)
            ty -= th
    
    def _darken(self, color, factor):
        """Return a darker version of the fill for the stroke."""
        r = max(0, int(color.red * factor * 255)) / 255
        g = max(0, int(color.green * factor * 255)) / 255
        b = max(0, int(color.blue * factor * 255)) / 255
        return colors.Color(r, g, b)

# ── Advanced: Arrow connector ──
class ArrowConnector(Flowable):
    """Draws an arrow from (x1,y1) to (x2,y2) with arrowhead.
    
    Color-code: arrows follow the category of the element they lead TO.
    """
    def __init__(self, x1, y1, x2, y2, color=ARROW, width=1.1):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.color = color
        self.width = width
        
    def wrap(self, *args):
        return (0, 0)  # doesn't take space in flow
    
    def draw(self):
        import math
        c = self.canv
        c.setStrokeColor(self.color)
        c.setLineWidth(self.width)
        c.line(self.x1, self.y1, self.x2, self.y2)
        
        # Arrowhead
        ang = math.atan2(self.y2 - self.y1, self.x2 - self.x1)
        L = 6
        c.line(self.x2, self.y2,
               self.x2 - L * math.cos(ang - 0.4),
               self.y2 - L * math.sin(ang - 0.4))
        c.line(self.x2, self.y2,
               self.x2 - L * math.cos(ang + 0.4),
               self.y2 - L * math.sin(ang + 0.4))

# ── Advanced: Two-page-size mixed document ──
def build_mixed_size_document(content_story, out_path, doc_title, doc_subtitle,
                               doc_date, doc_ref, prepared_for, classification,
                               cover_drawing, toc_entries):
    """Build a document with an A3-landscape master diagram cover
    followed by A4 portrait body pages.
    
    content_story: list of flowables for A4 body pages
    cover_drawing: a Drawing/Group to embed on the A3 cover
    """
    from reportlab.lib.pagesizes import A4, landscape as lscape, A3
    from reportlab.lib.units import mm
    
    PAGE_W, PAGE_H = A4
    MARGIN = 20 * mm
    
    # Create doc with A4 pages
    doc = BaseDocTemplate(out_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=22*mm, bottomMargin=20*mm, title=doc_title)
    
    # Cover frame (A3 landscape)
    a3w, a3h = A3  # 842 x 595 (landscape = 842 wide, 595 tall)
    cover_frame = Frame(0, 0, a3w, a3h, id="cover",
        leftPadding=MARGIN, rightPadding=MARGIN, topPadding=0, bottomPadding=0)
    
    # Content frame (A4 portrait)
    content_frame = Frame(MARGIN, 20*mm, PAGE_W - 2*MARGIN,
                         PAGE_H - 22*mm - 20*mm, id="content")
    
    def draw_a3_cover(c, doc):
        """Draw the A3 landscape cover with embedded diagram."""
        c.saveState()
        c.setFillColor(TEAL_DARK)
        c.rect(0, 0, a3w, a3h, stroke=0, fill=1)
        
        # Embed the diagram
        if cover_drawing:
            d = cover_drawing
            d.drawOn(c, a3w/2 - d.width/2, a3h/2 - d.height/2)
        
        # Footer
        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(WHITE)
        c.drawString(MARGIN, 12*mm, f"OAKAI Confidential  •  {doc_ref}  •  Page 1")
        
        c.setFont("Helvetica", 14)
        c.setFillColor(TEAL_LIGHT)
        c.drawCentredString(a3w/2, 30*mm, doc_title)
        c.setFont("Helvetica", 10)
        c.drawCentredString(a3w/2, 18*mm, doc_subtitle)
        c.restoreState()
    
    def draw_a4_content(c, doc, subtitle, ref):
        c.saveState()
        c.setStrokeColor(BORDER); c.setLineWidth(0.6)
        c.line(MARGIN, PAGE_H - 15*mm, PAGE_W - MARGIN, PAGE_H - 15*mm)
        c.setFont("Helvetica-Bold", 7.6); c.setFillColor(TEAL)
        c.drawString(MARGIN, PAGE_H - 13*mm, "OAKAI")
        c.setFont("Helvetica", 7.6); c.setFillColor(GREY)
        c.drawRightString(PAGE_W - MARGIN, PAGE_H - 13*mm, subtitle)
        c.line(MARGIN, 14*mm, PAGE_W - MARGIN, 14*mm)
        c.setFont("Helvetica-Bold", 7.8); c.setFillColor(TEAL_DARK)
        c.drawString(MARGIN, 10*mm, "OAKAI Confidential")
        c.setFont("Helvetica", 7.8); c.setFillColor(GREY)
        c.drawCentredString(PAGE_W / 2, 10*mm, ref)
        page_num = c.getPageNumber()
        c.drawRightString(PAGE_W - MARGIN, 10*mm, f"Page {page_num}")
        c.restoreState()
    
    doc.addPageTemplates([
        PageTemplate(id="CoverA3", frames=[cover_frame],
            onPage=lambda c, d: draw_a3_cover(c, d),
            pagesize=(a3w, a3h)),
        PageTemplate(id="Content", frames=[content_frame],
            onPage=lambda c, d: draw_a4_content(c, d, doc_subtitle, doc_ref)),
    ])
    
    story = []
    # Switch to A4 content template after the A3 cover
    story.append(NextPageTemplate("Content"))
    story.append(PageBreak())
    
    # TOC
    from oakai_pdf_template import make_toc, hr, styles
    story.append(Paragraph("Table of Contents", styles["H1"]))
    story.append(hr(color=GOLD, thickness=1.3, space_before=4, space_after=14))
    story.append(make_toc(toc_entries))
    story.append(PageBreak())
    
    # Content
    story += content_story
    doc.build(story)
    return out_path

# ── Example: Architecture decision table with color coding ──
def architecture_table(rows, col_widths, highlight_row=None, highlight_color=AMBER):
    """Build a status_table with optional row highlighting.
    
    rows: [[header...], [row1...], ...]
    highlight_row: index of row (0-based) to highlight
    """
    from oakai_pdf_template import status_table
    # We extend the base status_table by post-processing styles
    t = status_table(rows, col_widths=col_widths)
    if highlight_row:
        style = t.getListStyle()
        style.add(('BACKGROUND', (0, highlight_row), (-1, highlight_row), highlight_color), 'BACKGROUND')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, highlight_row), (-1, highlight_row), highlight_color),
            ('TEXTCOLOR', (0, highlight_row), (-1, highlight_row), WHITE),
        ]))
    return t

# ── Demo ---
if __name__ == "__main__":
    print("This module provides advanced PDF template helpers.")
    print("Usage:")
    print("  from oakai_advanced_template import DiagramBox, ArrowConnector, build_mixed_size_document")
    print("  # See SKILL.md for the complete usage guide.")
    print()
    print("Key enhancements over the base template:")
    print("  1. DiagramBox Flowable — high-contrast category-colored boxes")
    print("  2. ArrowConnector — proper arrows with arrowheads")
    print("  3. build_mixed_size_document — A3 landscape cover + A4 portrait body")
    print("  4. architecture_table — status_table with row highlighting")
    print()
    print("Palette reference:")
    print(f"  GREEN={GREEN}  (local/learning/cache)")
    print(f"  AMBER={AMBER}  (guard/verify/gate)")
    print(f"  BLUE={BLUE}  (routing/budget)")
    print(f"  NAVY={NAVY}    (title bands)")
    print(f"  RED={RED}    (abort/destructive)")
    print(f"  PURPLE={PURPLE} (interrupt/async)")
    print(f"  GREY_FILL={GREY_FILL} (neutral layers)")
    print(f"  TABLE_GRID={TABLE_GRID} (table grid lines)")