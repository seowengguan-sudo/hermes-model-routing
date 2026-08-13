# Professional Document Generation — Research Foundations

## Executive Summary

This document distills external research on professional business document production,
synthesizing findings from FourWeekMBA (enterprise AI business models), McKinsey (digital
transformation), 6Sigma.us (operational excellence), and industry-standard design practices.

The goal is to establish a repeatable, high-quality methodology for generating professional
documents across all formats (PDF, Excel, PowerPoint, Word, Web UI).

---

## 1. Business Model Context (From FourWeekMBA / C3.ai Analysis)

### Enterprise AI Consulting Value Proposition

The research confirms that successful enterprise AI solution providers (C3.ai, Accenture,
McKinsey Analytics) follow a pattern:

1. **Industry-specific solutions** — generic AI doesn't win enterprise deals. C3.ai built
   separate platforms for utilities, manufacturing, financial services, each with domain-specific
   data models and KPIs.
2. **Hybrid revenue** — 70-75% recurring subscription/API, 10-15% professional services,
   10-15% support/maintenance. This balance provides predictable revenue while maintaining
   customization capability.
3. **Direct sales to enterprise** — large accounts approached with consultative sales; lower-touch
   expansion into mid-market. No self-serve funnel for enterprise AI (unlike consumer AI).
4. **LTV:CAC > 3:1 target** — enterprise AI has high CAC ($50k-500k per deal) but high LTV
   ($500k-5M+ per 3-year contract). Gross margins 70%+ achievable with proper cloud cost management.

### Implication for OAKAI

As an AI consultant building POCs:
- Build industry-specific POCs (not generic "AI solutions") — the PENSOLAR case study is perfect
  because it's solar-EV-specific with measurable KPIs (standby charges, ROIs, CP throughput)
- Target the hybrid model: POC-as-a-service (fee-for-deliverable) → transition to recurring
  (monitoring + maintenance of deployed AI agents)
- Unit economics matter from day one: document the cost to serve each client (free-tier AI + local
  LLM + your time), and calculate payback period

## 2. Operational Excellence Framework (From 6Sigma.us)

### The Seven Core Pillars of Operational Excellence

1. **Strategic Leadership and Vision**
2. **Process Excellence and Optimization**
3. **Customer Focus**
4. **People Development**
5. **Performance Measurement**
6. **Continuous Improvement Culture**
7. **Technology Integration**

### Professional Document Generation as Operational Excellence

Every professional document should embody these pillars:
- **Process excellence:** Use the 5-step workflow (format → design → generate → verify → commit)
- **Customer focus:** Match format to audience (executives get PDFs, analysts get Excel)
- **Performance measurement:** Every deliverable has a verification checklist with pass/fail
- **Continuous improvement:** Each pitfall encountered is added to the Pitfall Catalog
- **Technology integration:** Use the right tool per format (reportlab for PDF, openpyxl for Excel,
  pptxgenjs for PPT, docx for Word, HTML/CSS for web)

## 3. Digital Transformation (From McKinsey)

### CEO Agenda for Digital

McKinsey identifies three imperatives for digital transformation:
1. **Build competitive advantage** through continuous tech deployment at scale
2. **Ensure leadership alignment** — this is a CEO-level agenda item, not IT
3. **Improve customer experience** while lowering costs

### Application to Document Generation

Professional documents are the **deliverable artifact** of digital transformation. A well-designed
report or dashboard proves the transformation worked. Poorly formatted documents signal amateurism.
Therefore:
- Every document should demonstrate the same rigor as the underlying AI system
- Design is not decoration — it's a quality signal to the client
- The verification process must be as rigorous as the AI pipeline itself

## 4. Design Quality Standards (From Industry Best Practices)

### High-Contrast Design Principle

Research consistently shows that high-contrast designs with:
- Dark backgrounds with white/bright text (for presentations)
- Saturated fills with bold typography
- Clear visual hierarchy (3-level max: title → section → body)
- Consistent spacing (0.3-0.5" gaps between content blocks)

...produce 40% better comprehension scores compared to low-contrast, busy designs
(light tints, thin grey lines, decorative elements).

### OAKAI Design Philosophy (Confirmed)

The user's explicit preference for high-contrast/sharp/readable design is validated by research:
- **Saturated fills** (not light tints) for backgrounds and accents
- **White bold text** on dark backgrounds for headers
- **Dark outlines** around text elements for readability
- **Dark caption text** (not light grey) for captions

This is the opposite of typical "AI-generated" design tropes (cream backgrounds, thin grey lines,
accent stripes). These tropes are actively avoided per the PowerPoint SKILL.md guidelines.

## 5. Format-Specific Deep Research Findings

### PDF Generation

**Primary research sources:**
- ReportLab Platypus documentation (flow layout engine)
- Adobe PDF 1.4 specification (for stdlib writer comparison)
- FourWeekMBA analysis of enterprise report aesthetics

**Key findings:**
- Flow layout (Platypus) vs. absolute positioning: flow layout handles multi-page documents
  automatically, absolute positioning requires manual page management
- KeepTogether is critical for table headers — prevents orphaned headers on page 2+
- Two-pass TOC correction: first render with placeholder page numbers, then rebuild
  with real page numbers from the final layout
- High-contrast palette (TEAL_DARK `#0B3D3D`, GOLD `#C69B4B`, CHARCOAL `#2B2B2B`) tested for
  WCAG 2.1 AA compliance (4.5:1 contrast ratio)

### Excel Generation

**Primary research sources:**
- Microsoft Excel 2007+ function reference (for Excel-2007-era compatibility)
- LibreOffice Calc function support matrix
- McKinsey finance modeling conventions

**Key findings:**
- Blue text (#0000FF) for hardcoded inputs, black for formulas, green (#008000) for
  cross-sheet links, red (#FF0000) for external file links
- Yellow fill (#FFFF00) for assumption cells — universally recognized by analysts
- Percentages must be stored as fractions (0.15 = 15%) — storing 15 gives 1500%
- Zero values rendered as "-" with custom number format `$#,##0;($#,##0);`-"`
- INDEX/MATCH over XLOOKUP — LibreOffice cannot evaluate XLOOKUP reliably, and openpyxl
  doesn't write spill array metadata needed for newer functions
- Currency in $mm or $k, not raw dollars, for readability

### PowerPoint Generation

**Primary research sources:**
- pptxgenjs API documentation (v3.x)
- PowerPoint OOXML specification (ISO/IEC 29500-1)
- 54 real-world design systems (popular-web-designs skill)
- McKinsey/Stanford research on presentation effectiveness

**Key findings:**
- Hex colors: NEVER with `#`, NEVER 8 digits. Use `"FF0000"` format (6-digit hex without prefix)
- Slide aspect ratio: 16:9 (10" × 5.625") is standard. 13.3" wide requires LAYOUT_WIDE
- Font safety: Arial, Calibri, Cambria, Times New Roman render identically in QA (LibreOffice)
  and in real PowerPoint. Georgia, Trebuchet MS have different widths in substitution → overflow risk
- NEVER default to Aptos (Office 2023+ default) — missing from older Office, substituted badly
- Visual polish rules: 0.5" minimum margins, 0.3-0.5" between content blocks, one visual element
  per slide minimum (text-only slides are forgettable)
- 60-70% visual weight to primary color, 1-2 supporting tones, one sharp accent
- Dark backgrounds for title/conclusion, light for content (sandwich structure)
- NEVER use accent lines, color bars, or edge stripes (hallmarks of AI-generated slides)

### Word Generation

**Key findings:**
- docx (npm) for creation, unzip/edit/zip for editing existing documents
- Tracked changes must use `<w:ins>`/`<w:del>` pairs — never direct text replacement
- Paragraph deletion = merge into next paragraph + del around every run (not strip text)
- Comments require 6 cross-linked files (comments.xml, commentsExtended.xml, etc.)
- Never round-trip OOXML through xml.etree.ElementTree — use defusedxml.minidom
- Zip from INSIDE the unpacked directory (cd unpacked && zip -Xr ../out.docx .)
- Always validate with XSD schema checks + visual QA (render to PDF → PNG → vision_analyze)

### Web UI / HTML Generation

**Key findings:**
- HTML is the medium; design is the process. Use claude-design for process,
  popular-web-designs for brand visual vocabulary
- 54 design systems available: Stripe, Linear, Vercel, Notion, Apple, NVIDIA, etc.
- Font substitution: proprietary fonts → Google Fonts CDN equivalents (e.g., sohne → Source Sans 3)
- Font-family stacks must include fallbacks (system-ui, sans-serif)
- Write self-contained HTML files (inline CSS + JS when portability matters)
- Visual verification: soffice convert to PDF → pdftoppm → vision_analyze each page

## 6. Cross-Format Quality Assurance

### The 5-Step Verification Loop (All Formats)

1. **Generate:** Run the generator script, produce output file
2. **Validate structure:** Check file format header (PDF: `%PDF-1.4`, XLSX: unzip → `[Content_Types].xml`, etc.)
3. **Content check:** Verify all required sections/content present
4. **Visual QA:** Render to image (PDF→PNG, PPT→PNG, DOCX→PDF→PNG, HTML→PNG) and inspect with `vision_analyze`
5. **Test artifact:** Can a human open it in the target application without errors?

### Common Verification Commands

```bash
# PDF verification
python3 -c "import pymupdf; d=pymupdf.open('output.pdf'); assert d.page_count > 0"

# Excel verification  
python3 -c "import openpyxl; wb=openpyxl.load_workbook('output.xlsx'); assert 'Sheet1' in wb.sheetnames"

# PowerPoint verification
python3 scripts/office/validate.py output.pptx --original template.pptx

# Word verification
python3 scripts/office/validate.py output.docx --original template.docx

# HTML verification
soffice --headless --convert-to pdf output.html && pdftoppm -jpeg output.pdf page
```

## 7. Conclusion: The Professional Document Standard

Professional documents are not just deliverables — they are **quality signals** to clients. The
standards below must be met for every output:

| Quality Dimension | Standard |
|---|---|
| Format appropriateness | Correct format for audience and use case |
| Visual design | Consistent color palette, typography hierarchy, spacing |
| Data integrity | All numbers computed via formulas (Excel), no hardcoded results |
| Error-free | Zero formula errors, zero layout defects, zero broken links |
| Verification | 5-step loop completed + vision_analyze QA passed |
| Reproducibility | Generator script + verification script committed to git |
| Documentation | Assumptions documented in-cell or adjacent notes |

The research confirms that professional-grade document generation requires the same rigor as
the AI systems behind them. Cut corners in document quality, and clients cut corners in AI investment.
