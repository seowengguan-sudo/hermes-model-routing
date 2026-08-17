---
name: documentation-generation
category: productivity
description: Generates valid multi-page PDFs using Python stdlib.
---

# Documentation Generation with Standard Python Library

This skill outlines the process for generating complex, multi-page PDF documents using only Python's standard library. It emphasizes the precision required for PDF syntax and robust content management.

## 1. Core PDF Generation Class (`PDF`)

The `PDF` class encapsulates the low-level PDF object generation, ensuring a valid PDF 1.4 structure with correct xref tables, byte offsets, and content streams.

**Key Features:**
- **Object Management:** Handles creation of PDF objects (Catalog, Pages, Page, Font, Content Stream).
- **Coordinate System:** Uses standard PDF coordinates (0,0 bottom-left).
- **Text Rendering:** Supports `Helvetica` (F1) and `Courier` (F2) fonts.
- **Graphic Primitives:** Basic methods for lines, rectangles, and filled rectangles.
- **Pagination:** Automatic page breaking and page numbering in the footer.
- **Xref Table Accuracy:** Crucial for PDF validity, meticulously tracks all object byte offsets.

## 2. Content Structure and Layout

Content is built by calling `section()`, `body()`, and `diagram()` functions, which manage vertical positioning (`y`) and page breaks.

- **`section(title)`:** Renders a bold, grey-bar section header and manages page breaks.
- **`body(lines, ...)`:** Renders bulleted or indented text lines, handles wrapping and pagination.
- **`diagram(lines)`:** Renders ASCII art diagrams, typically with a monospaced font (`Courier`).

## 3. Robust Content Update Workflow

For complex content updates (e.g., ASCII diagrams with special characters, multi-line text blocks), directly modifying the file in memory and then writing it back is more reliable than using `patch`.

**Workflow:**
1.  `read_file(path)`: Read the entire content of the Python script.
2.  **In-memory modification:** Use Python string manipulation (`.find()`, `.replace()`, regular expressions) to locate and update specific content blocks.
3.  `write_file(path, modified_content)`: Write the complete modified content back to the file.

This approach bypasses `patch`'s string matching sensitivities for large, multi-line, or special-character-laden text.

## 4. LLM Code Generation Pitfalls for PDF

When attempting to have an LLM generate the PDF script itself, several challenges arise:

-   **Prose Injection:** LLMs may include explanatory text or markdown fences despite strict "code-only" instructions.
-   **Syntax Errors:** Common issues include unterminated string literals, incorrect escape sequences, or misformatted PDF operators.
-   **Truncation:** Response `max_tokens` limits can cut off code mid-function, leading to invalid syntax or incomplete logic.
-   **Incorrect PDF Operators:** LLMs may misunderstand low-level PDF operators (e.g., `Tm` vs `Td` for text positioning, incorrect order of graphic operators), resulting in malformed PDFs.

**Recommendation:** For high-precision, low-level code like PDF generation, use a manually verified template and focus LLM assistance on *content generation* (e.g., drafting section text) rather than *code generation* of the PDF writer itself.

## 5. PDF Validation

Always validate the generated PDF:
- Check header: `%PDF-1.4`
- Check EOF marker: `%%EOF`
- Validate xref table: Ensure all object offsets correctly point to `N 0 obj` markers. This is critical for PDF readers.

## 6. Canonical Skill Path Workflow (Mandatory)

Regardless of whether ReportLab, pypdf, or stdlib is used — the agent MUST follow this sequence:

1. **`/skill-view pdf:design-system`** → load canonical template paths
2. **`/read /opt/data/skills/PDF/oakai_pdf_template.py`** → pull branded style definitions
3. **Generate through `/opt/data/skills/PDF/oakai_report_generator.py`** → never ad-hoc scripts
4. **Fallback ONLY if skill engine missing:** use `documentation-generation` stdlib method described above

This guarantees consistency in footers, fonts, and brand compliance across all deliverables.

## 7. Runtime Caching Best Practice

Repeated venv recreation (e.g. per-cron PDF generation) causes unacceptable latency. Implement a persistent runtime cache:

```bash
CACHE_DIR=/tmp/hermes-runs/pdf-runtime
if [ ! -d "$CACHE_DIR/venv" ]; then
  python -m venv "$CACHE_DIR/venv"
  pip install reportlab pypdf openpyxl
fi
```

This eliminates 3–5 second startup delays per invocation.

## 8. Automated PDF Script

A reusable shell script handles canonical PDF generation with caching:

See `scripts/generate_pdf.sh`

```bash
cd /opt/data
./skills/productivity/documentation-generation/scripts/generate_pdf.sh \
  coo_week1 /opt/data/workspace/OAKAI_W1_COOBrief.pdf
```



## 9. Working with Extensible Document Processing Systems\n\nWhen documenting or generating output for systems with extensible security/category policies (like the enhanced OAKAI Document Reader), consider these patterns:\n\n- **Policy Documentation**: Clearly document the structure of security policy dictionaries, including category groups, patterns, dummy prefixes, and criticality flags.\n- **UI Mapping Logic**: Document how category groups map to UI elements (settings panels, badge colors, processing priorities) for maintainability.\n- **Verification Patterns**: Include automated tests that validate policy structure, component presence, and UI variable updates as part of documentation validation.\n- **Backward Compatibility**: Note how enhancements preserve existing functionality while adding new capabilities.\n- **Extension Points**: Clearly identify where users or developers can add custom categories or modify processing logic.\n\nSee the enhanced OAKAI Document Reader example in `/opt/data/workspace/Samples/enhanced_doc_reader_v2/` for practical implementation of these patterns.\n\nSee also `references/enhancement_oakai_document_reader.md` for detailed enhancement patterns.\n\n## Pitfalls\n\n---\n**References:**\n- `templates/make_pdf.py`: The complete Python script for generating the Hermes Meta-Intelligence Architecture PDF.\n- `references/enhancement_oakai_document_reader.md`: Patterns for enhancing document processing systems with extensible security policies.
