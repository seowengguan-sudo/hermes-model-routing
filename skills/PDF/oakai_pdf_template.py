# -*- coding: utf-8 -*-
"""
OAKAI PDF Design System — reusable engine.

This is the ENGINE only: colors, styles, and helper functions
(section_header, status_table, checklist, kv_callout_box, cover/footer
drawing). It has no document-specific content in it.

Usage pattern for any new report:
    from oakai_pdf_template import *

    story = []
    story += section_header("01", "Executive Summary")
    story.append(Paragraph("...", styles["Body"]))
    story.append(status_table([...]))
    story += checklist([...])
    story.append(kv_callout_box("Note", ["..."]))

    build_document(story, out_path="/mnt/user-data/outputs/report.pdf",
                    doc_title="...", doc_subtitle="...", doc_date="...",
                    doc_ref="...", toc_entries=[("01","Executive Summary","3"), ...])

See oakai_report_example.py for a full worked example.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
    TableStyle, NextPageTemplate, PageBreak, KeepTogether, HRFlowable,
    KeepInFrame
)
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

# ----------------------------------------------------------------------
# BRAND PALETTE — change these 6 lines to re-skin every document at once
# ----------------------------------------------------------------------
TEAL_DARK  = colors.HexColor("#0B3D3D")
TEAL       = colors.HexColor("#0F5C56")
TEAL_LIGHT = colors.HexColor("#E7F1EF")
GOLD       = colors.HexColor("#C69B4B")
CHARCOAL   = colors.HexColor("#2B2B2B")
GREY       = colors.HexColor("#6E6E6E")
ROW_ALT    = colors.HexColor("#F7FAF9")
BORDER     = colors.HexColor("#D9E2E0")
WHITE      = colors.white

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm

FOOTER_LABEL = "OAKAI Confidential"
BRAND_NAME = "OAKAI"

# ----------------------------------------------------------------------
# STYLES
# ----------------------------------------------------------------------
styles = getSampleStyleSheet()
styles.add(ParagraphStyle("CoverTitle", fontName="Helvetica-Bold", fontSize=30,
    leading=34, textColor=WHITE))
styles.add(ParagraphStyle("CoverSubtitle", fontName="Helvetica", fontSize=13,
    leading=18, textColor=TEAL_LIGHT))
styles.add(ParagraphStyle("CoverMeta", fontName="Helvetica", fontSize=9.5,
    leading=14, textColor=colors.HexColor("#BFE0DA")))
styles.add(ParagraphStyle("SectionNum", fontName="Helvetica-Bold", fontSize=9,
    leading=11, textColor=GOLD, spaceAfter=2))
styles.add(ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=18,
    leading=22, textColor=TEAL_DARK, spaceAfter=10))
styles.add(ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=12.5,
    leading=16, textColor=TEAL_DARK, spaceBefore=14, spaceAfter=6))
styles.add(ParagraphStyle("H3", fontName="Helvetica-Bold", fontSize=10.5,
    leading=14, textColor=TEAL, spaceBefore=8, spaceAfter=4))
styles.add(ParagraphStyle("Body", fontName="Helvetica", fontSize=9.7,
    leading=14.5, textColor=CHARCOAL, alignment=TA_JUSTIFY, spaceAfter=6))
styles.add(ParagraphStyle("BodySmall", fontName="Helvetica", fontSize=8.8,
    leading=12.8, textColor=GREY, spaceAfter=4))
styles.add(ParagraphStyle("TaskItem", fontName="Helvetica", fontSize=9.4,
    leading=13.5, textColor=CHARCOAL, spaceAfter=3, leftIndent=2))
styles.add(ParagraphStyle("Callout", fontName="Helvetica", fontSize=9.3,
    leading=13.5, textColor=TEAL_DARK, spaceAfter=4))
styles.add(ParagraphStyle("CellHead", fontName="Helvetica-Bold", fontSize=8.6,
    leading=11, textColor=WHITE))
styles.add(ParagraphStyle("Cell", fontName="Helvetica", fontSize=8.6,
    leading=12, textColor=CHARCOAL))
styles.add(ParagraphStyle("TOCEntry", fontName="Helvetica", fontSize=10.5,
    leading=20, textColor=CHARCOAL))
styles.add(ParagraphStyle("TOCPage", fontName="Helvetica-Bold", fontSize=10.5,
    leading=20, textColor=TEAL))

# ----------------------------------------------------------------------
# HELPERS — reuse these for every document, don't write one-offs
# ----------------------------------------------------------------------

def hr(color=BORDER, thickness=0.6, space_before=4, space_after=8):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                       spaceBefore=space_before, spaceAfter=space_after)


def section_header(number, title, subtitle=None):
    """Returns a LIST of flowables — use story += section_header(...)"""
    flows = [Paragraph(number, styles["SectionNum"]),
             Paragraph(title, styles["H1"])]
    if subtitle:
        flows.append(Paragraph(subtitle, styles["BodySmall"]))
    flows.append(hr(color=GOLD, thickness=1.3, space_before=6, space_after=14))
    return flows


def status_table(rows, col_widths=None):
    """rows[0] is the header row. Returns a single Table flowable —
    wrap in KeepTogether with any caption below it to avoid orphaned
    headers across a page break."""
    header = [Paragraph(str(c), styles["CellHead"]) for c in rows[0]]
    data = [header]
    for r in rows[1:]:
        data.append([Paragraph(str(c), styles["Cell"]) for c in r])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), TEAL_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, TEAL_DARK),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, BORDER),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(style))
    return t


def checklist(items):
    """Returns a LIST of flowables — use story += checklist([...]).
    Uses a bullet glyph, not a checkbox, since checkbox unicode glyphs
    render as black boxes in base-14 PDF fonts."""
    return [Paragraph(f"&#8226;&nbsp;&nbsp;{it}", styles["TaskItem"])
            for it in items]


def kv_callout_box(title, body_lines):
    """Soft teal callout box. body_lines is a list of strings (already
    HTML-entity-safe)."""
    content = [Paragraph(title, styles["H3"])]
    for line in body_lines:
        content.append(Paragraph(line, styles["Callout"]))
    tbl = Table([[content]], colWidths=[PAGE_W - 2 * MARGIN])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TEAL_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.8, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return tbl


def make_toc(entries):
    """entries: list of (number, title, page_str). Returns a Table flowable."""
    data = [[Paragraph(f"<b>{n}</b>", styles["TOCPage"]),
             Paragraph(t, styles["TOCEntry"]),
             Paragraph(p, styles["TOCPage"])] for n, t, p in entries]
    tbl = Table(data, colWidths=[14 * mm, 130 * mm, 15 * mm])
    tbl.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
    ]))
    return tbl


# ----------------------------------------------------------------------
# LAYOUT OPTIMIZATION HELPERS — maximize page fill, minimize waste
# ----------------------------------------------------------------------

def auto_split_paragraph(text, style, max_width):
    """Split long text into paragraphs that fit within max_width.
    Returns a string with <br/> tags at word-wrap boundaries.
    Call this before wrapping text for narrow table cells."""
    # Use reportlab's built-in text wrapping
    from reportlab.lib.utils import simpleSplit
    font_name = style.fontName or "Helvetica"
    font_size = style.fontSize or 10
    # Get the actual font to measure properly
    from reportlab.pdfbase import pdfmetrics
    try:
        font = pdfmetrics.getFont(font_name)
        avg_char_width = font.face.width * font_size / 1000.0
    except Exception:
        avg_char_width = font_size * 0.5
    chars_per_line = int(max_width / avg_char_width) if avg_char_width > 0 else 40
    if chars_per_line < 10:
        chars_per_line = 10
    
    lines = simpleSplit(text, font_name, font_size, max_width * mm if max_width < 100 else max_width, 
                        max_width * 0.6 if max_width < 100 else None)
    # simpleSplit returns lines based on width; if it doesn't work, fallback to manual splitting
    if isinstance(lines, list) and len(lines) > 1:
        return "<br/>".join(lines)
    
    # Fallback: simple character-based splitting
    words = text.split()
    result_lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= chars_per_line:
            current += " " + word if current else word
        else:
            if current:
                result_lines.append(current)
            current = word
    if current:
        result_lines.append(current)
    return "<br/>".join(result_lines)


def fit_table_to_page(rows, col_widths, max_height=None, style_overrides=None):
    """Wraps a Table in KeepInFrame to ensure it fits on page.
    
    If the table is too wide, columns are auto-shrunk proportionally.
    If the table is too tall, it's constrained to max_height.
    
    Usage:
        table = fit_table_to_page(rows, [30*mm, 50*mm, ...], max_height=100*mm)
        story.append(table)
    """
    # Build the table
    header = [Paragraph(str(c), styles["CellHead"]) for c in rows[0]]
    data = [header]
    for r in rows[1:]:
        data.append([Paragraph(str(c), styles["Cell"]) for c in r])
    
    # Adjust column widths if total exceeds page width
    page_content_width = PAGE_W - 2 * MARGIN
    total_requested = sum(col_widths)
    if total_requested > page_content_width:
        # Scale down proportionally
        scale_factor = page_content_width / total_requested
        col_widths = [w * scale_factor for w in col_widths]
    
    t = Table(data, colWidths=col_widths, repeatRows=1, hAlign='LEFT')
    
    # Default table style (full professional borders)
    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), TEAL_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, 0), 1.0, TEAL_DARK),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, BORDER),
        ("LINEABOVE", (0, 1), (-1, 1), 0.5, BORDER),
        ("LINELEFT", (0, 0), (0, -1), 0.5, BORDER),
        ("LINERIGHT", (-1, 0), (-1, -1), 0.5, BORDER),
    ]
    
    # Zebra striping
    for i in range(1, len(data)):
        if i % 2 == 0:
            table_style.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    
    if style_overrides:
        table_style.extend(style_overrides)
    
    t.setStyle(TableStyle(table_style))
    
    if max_height:
        return KeepInFrame(max_height, page_content_width * 0.9, [t], mode='shrink')
    return t


def split_large_table(rows, col_widths, max_rows_per_table=15):
    """Split a large table into chunks that fit well on pages.
    Returns a list of Table flowables.
    
    This prevents tables from spanning 3+ pages uncontrollably.
    Each chunk includes the header row."""
    if len(rows) <= max_rows_per_table:
        return [status_table(rows, col_widths)]
    
    tables = []
    header = rows[0]
    for i in range(1, len(rows), max_rows_per_table - 1):
        chunk = [header] + rows[i:i + max_rows_per_table - 1]
        tables.append(status_table(chunk, col_widths))
    return tables


# ----------------------------------------------------------------------
# PAGE DRAWING — cover and content-page chrome (header/footer rules)
# ----------------------------------------------------------------------

def _draw_content_page(c, doc, subtitle, doc_ref):
    c.saveState()
    page_num = c.getPageNumber()
    c.setStrokeColor(BORDER); c.setLineWidth(0.6)
    c.line(MARGIN, PAGE_H - 15 * mm, PAGE_W - MARGIN, PAGE_H - 15 * mm)
    c.setFont("Helvetica-Bold", 7.6); c.setFillColor(TEAL)
    c.drawString(MARGIN, PAGE_H - 13 * mm, BRAND_NAME)
    c.setFont("Helvetica", 7.6); c.setFillColor(GREY)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 13 * mm, subtitle)
    c.line(MARGIN, 14 * mm, PAGE_W - MARGIN, 14 * mm)
    c.setFont("Helvetica-Bold", 7.8); c.setFillColor(TEAL_DARK)
    c.drawString(MARGIN, 10 * mm, FOOTER_LABEL)
    c.setFont("Helvetica", 7.8); c.setFillColor(GREY)
    c.drawCentredString(PAGE_W / 2, 10 * mm, doc_ref)
    c.drawRightString(PAGE_W - MARGIN, 10 * mm, f"Page {page_num}")
    c.restoreState()


def _draw_cover(c, doc, title_meta):
    c.saveState()
    c.setFillColor(TEAL_DARK); c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(GOLD); c.rect(0, PAGE_H - 8 * mm, PAGE_W, 3, stroke=0, fill=1)
    c.setFillColor(TEAL); c.rect(0, 0, 6 * mm, PAGE_H, stroke=0, fill=1)
    c.setFillColor(GOLD); c.rect(6 * mm, 0, 1.4 * mm, PAGE_H, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 13); c.setFillColor(GOLD)
    c.drawString(MARGIN, PAGE_H - 40 * mm, " ".join(BRAND_NAME))
    c.setStrokeColor(colors.HexColor("#1E6F68")); c.setLineWidth(0.6)
    c.line(MARGIN, 22 * mm, PAGE_W - MARGIN, 22 * mm)
    c.setFont("Helvetica-Bold", 8.5); c.setFillColor(WHITE)
    c.drawString(MARGIN, 16 * mm, FOOTER_LABEL)
    c.setFont("Helvetica", 8.5); c.setFillColor(colors.HexColor("#9FC9C2"))
    c.drawRightString(PAGE_W - MARGIN, 16 * mm, "Page 1")
    c.restoreState()


# ----------------------------------------------------------------------
# TOP-LEVEL BUILD FUNCTION
# ----------------------------------------------------------------------

def build_document(content_story, out_path, doc_title, doc_subtitle,
                    doc_date, doc_ref, prepared_for, classification,
                    toc_entries):
    """
    content_story: list of flowables for sections 01+ (build with
        section_header / status_table / checklist / kv_callout_box).
        Do NOT include the cover or TOC — this function builds those.
    toc_entries: list of (number, title, page_str) tuples. On the FIRST
        build, estimate pages; then open the PDF, check real page numbers,
        and rebuild with corrected toc_entries. Always do this second pass.
    """
    doc = BaseDocTemplate(out_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=22 * mm, bottomMargin=20 * mm,
        title=doc_title)

    cover_frame = Frame(0, 0, PAGE_W, PAGE_H, id="cover",
        leftPadding=MARGIN, rightPadding=MARGIN, topPadding=0, bottomPadding=0)
    content_frame = Frame(MARGIN, 20 * mm, PAGE_W - 2 * MARGIN,
        PAGE_H - 22 * mm - 20 * mm, id="content")

    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame],
            onPage=lambda c, d: _draw_cover(c, d, None)),
        PageTemplate(id="Content", frames=[content_frame],
            onPage=lambda c, d: _draw_content_page(c, d, doc_subtitle, doc_ref)),
    ])

    story = []
    story.append(Spacer(1, 90 * mm))
    story.append(Paragraph(doc_title, styles["CoverTitle"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(doc_subtitle, styles["CoverSubtitle"]))
    story.append(Spacer(1, 14 * mm))
    meta_tbl = Table([
        [Paragraph("PREPARED FOR", styles["CoverMeta"]), Paragraph(prepared_for, styles["CoverMeta"])],
        [Paragraph("REFERENCE", styles["CoverMeta"]), Paragraph(doc_ref, styles["CoverMeta"])],
        [Paragraph("DATE", styles["CoverMeta"]), Paragraph(doc_date, styles["CoverMeta"])],
        [Paragraph("CLASSIFICATION", styles["CoverMeta"]), Paragraph(classification, styles["CoverMeta"])],
    ], colWidths=[45 * mm, 100 * mm])
    meta_tbl.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#1E6F68")),
    ]))
    story.append(meta_tbl)
    story.append(NextPageTemplate("Content"))
    story.append(PageBreak())

    story.append(Paragraph("Table of Contents", styles["H1"]))
    story.append(hr(color=GOLD, thickness=1.3, space_before=4, space_after=14))
    story.append(make_toc(toc_entries))
    story.append(PageBreak())

    story += content_story
    doc.build(story, canvasmaker=canvas.Canvas)
    return out_path
