---
name: python-venv-setup
description: "uv venv when pip blocked; never write Office as text."
version: 1.0.0
author: Hermes agent (session-derived)
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Python, venv, PEP668, openpyxl, xlsx, docx, pdf, setup]
    category: productivity
    related_skills: [xlsx, docx, pdf, powerpoint]
---

# Python venv setup for document/data libraries

Use this whenever you must edit or generate `.xlsx` / `.docx` / `.pptx` / `.pdf` files but the host Python has no `pip` and is externally managed. Two things will break a naive attempt: (1) you cannot `pip install`, and (2) the text you got from `read_file` is NOT the file's on-disk format, so writing it back corrupts the file.

## When to use
- `python3 -m pip` or `pip3` fails with "externally managed environment" / "command not found".
- You need `import openpyxl` / `python-docx` / `reportlab` / `pandas` and they are absent.
- You are about to edit an Office/binary file whose contents were surfaced by `read_file` as rendered text or a TSV — that rendering is a *view*, not the file.

## Steps
1. Create a venv with `uv` (uv is usually present even when pip is not):
   ```bash
   uv venv hermes-venv && source hermes-venv/bin/activate && uv pip install openpyxl
   ```
   Add whatever library the task needs (openpyxl for xlsx, python-docx for docx, reportlab for pdf; pandas optional).
2. Run your script with the venv's `python3`.
3. Terminal session state does NOT persist across separate tool calls — re-`source hermes-venv/bin/activate` each time you open a new shell, or chain the activate into the same command.

## CRITICAL pitfall — never write binary files back as text
`read_file` on an `.xlsx` (and similar zipped formats) returns an *extracted text rendering* (e.g. a TSV of the first sheet, with `# ── Sheet: ... ──` markers). This is great for reading but is NOT the file format. If you read that text, append rows/columns, and `write_file` it back unchanged, you replace the real ZIP/OOXML container with plain text and the file becomes unopenable in Excel/LibreOffice.

Always edit through the library that owns the format:
```python
import openpyxl
wb = openpyxl.load_workbook(path)   # real binary parse
ws = wb['Master Model Matrix']
ws.cell(row=r, column=c, value="...")
wb.save(path)                       # real binary write
```
Verify immediately by re-loading:
```python
wb2 = openpyxl.load_workbook(path)
print(wb2['Master Model Matrix'].dimensions)   # throws if corrupt
```

## Verification checklist
- `load_workbook(out_path)` (or the format's loader) succeeds with no exception.
- Header row and a sample data cell contain expected values.
- `ls -la` shows a sane size. A text-corrupted xlsx is usually much larger and either starts with the original ZIP bytes mixed with text or is pure text — both are wrong.

## SpaCy model ordering for NER-based redaction
When building a redaction engine that combines regex patterns with spaCy NER:
1. **Run NER FIRST** on the original text — NER needs full sentence context to correctly tag PERSON/ORG/GPE entities
2. **Then run regex patterns** (SSN, credit card, phone, email) — these are precise and should overwrite any NER-detected tokens
3. **Then run custom abbreviation matching** — these are user-defined labels (A, B, C) that should not interfere with NER

Running regex first causes NER to see replaced tokens (e.g. `{EMAIL_1}`) instead of original context, leading to misclassification.

## Common NER false positives to filter
spaCy's `en_core_web_sm` model frequently tags common words as PERSON/ORG/GPE:
- "Email", "Phone", "Address", "Date" as PERSON
- "SSN" as ORGANIZATION
- "Client", "Project" as ORGANIZATION

Filter these with a `NER_SKIP_WORDS` set of ~30 common terms, plus skip single-character entities from PERSON/ORG labels.

## Related
- `xlsx` skill (bundled) — covers openpyxl formulas, recalc, financial conventions.
  NOTE: its Prerequisites still say `pip install openpyxl`, which fails under PEP 668, and it lacks the text-writeback corruption warning. Recommend `hermes curator adopt xlsx` to fold this pitfall in.

## References
- `references/spacy-pip-install-via-uv.md` — Fix for spaCy model install in uv venvs + critical pitfall: spacy download to wrong venv path
- `references/data-security-governance-policy.md` — 10 PII/PHI/financial exclusion categories for document readers
- See also: `mlops/local-document-reader-agent` skill for a full local document reader with PII redaction built on these venv patterns.
