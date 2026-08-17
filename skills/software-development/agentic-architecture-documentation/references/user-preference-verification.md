# User Preference Verification Pattern

## Trigger
**Use when:** The user provides a specific preference (name, format, style, structure) for a document
and then the deliverable is shown back to them for feedback.

## The problem
Without explicit verification, user name/preference corrections get missed in document fields:
- Cover page "Prepared for" field
- Footer/header text
- Table cell contents
- Callout boxes
- Embedded diagrams
- File metadata

## The fix
After generating ANY document for a user, run this verification:

```python
# For PDFs: use pymupdf to extract ALL text
import pymupdf as fitz

doc = fitz.open(path)
full_text = ""
for page in doc:
    full_text += page.get_text()
doc.close()

# Verify the CORRECT name/preferences are present
assert "EG SEOW" in full_text, "Correct name not found!"

# Verify the WRONG name is absent
assert "Weng Guan" not in full_text, "Old name still present!"

# Log any surprises
for page_num, page in enumerate(doc):
    page_text = page.get_text()
    if "Weng Guan" in page_text:
        print(f"WARNING: old name found on page {page_num + 1}")
```

## When this matters most

1. **Document generators with multiple content sections** — each section may independently
   reference the user's name or preferences
2. **Templates with hardcoded fields** — the `oakai_pdf_template.py` cover template includes
   `prepared_for` as a parameter, but table cells and callout boxes may embed it separately
3. **Multi-pass builds** — TOC estimation, cover regeneration, or rebuild cycles can introduce
   stale values from cached variables

## Session Evidence (Aug 13, 2026)

The OAKAI Mission Executive Brief was initially generated with "Weng Guan" as the
prepared-for name. The user corrected: "My name is EG SEOW, not Weng Guan. For documents
pls do not put wrong name."

The correction required updating:
1. `PREPARED_FOR` constant in the generator script
2. All table cell contents where "Founder" or owner references appeared
3. Footer metadata in the PDF template

This was caught by re-running the full verification suite (name check across all extracted text).

## Rule of thumb

**When a user corrects ANY preference after the first build:**
1. Do NOT just fix the one field the user flagged
2. Re-scan ALL occurrences in the output document (title, body, footer, header)
3. Add the correction pattern to the verification script
4. Re-run full content extraction + assertion
