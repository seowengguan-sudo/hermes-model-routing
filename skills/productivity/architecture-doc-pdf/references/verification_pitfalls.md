# Pitfalls: KeepTogether + ReportLab Version + Mixed Page Sizes

## Pitfall: KeepTogether causes silent overflow for long tables

**When:** `Story(KeepTogether([section_header(...), status_table(big_rows, ...)]))`

**Symptom:** Large table (8+ rows) wrapped in `KeepTogether` gets silently truncated
or overflows the frame when it doesn't fit on the remaining page space. Content
disappears or overlaps with the next section.

**Fix:** For tables that may span pages:
- Separate the section header from the table (don't put both in KeepTogether)
- Use `PageBreak()` before long tables to ensure they start on a clean page
- For short tables (< 8 rows), `KeepTogether` is safe
- For medium tables (4-8 rows), wrap in `KeepTogether` but allow section headers to break

```python
# ❌ DON'T: large table in KeepTogether (overflow risk)
story.append(KeepTogether([section_header(...), status_table(big_rows, ...)]))

# ✅ DO: separate section header from long table
story += section_header("03", "Business Model", "...")
story.append(PageBreak())  # ensure table starts clean
story.append(KeepTogether([status_table(medium_rows, ...)]))  # 4-8 rows = safe
```

## Pitfall: ReportLab version differences

**When:** `reportlab` is installed at version 5.0.0 (installed via `uv pip install --target lazy-packages reportlab`)

**Symptom:** API differences between reportlab 3.x and 5.x can cause `HexColor`,
`Paragraph`, `Table`, and `Flowable` behaviors to differ. Always verify against
the installed version.

**Fix:** Always check version after import:
```python
import reportlab
print(reportlab.Version)  # e.g. "5.0.0"
```

**Environment note:** In this WASM-based environment, `reportlab` is NOT pre-installed.
Install it to lazy-packages:
```bash
uv pip install --target /opt/data/lazy-packages reportlab
```
Then in Python scripts:
```python
import sys
sys.path.insert(0, '/opt/data/lazy-packages')
```

## Pitfall: Mixed page sizes (A3 landscape + A4 portrait)

**When:** Embedding a landscape cover page with a master diagram into a portrait PDF

**Symptom:** `SimpleDocTemplate` cannot mix page sizes. Content spills or clips.

**Fix:** Use `BaseDocTemplate` with two `PageTemplate`s:
- `'cover'` template: landscape frame (A3 or A4 landscape)
- `'body'` template: portrait frame (A4)

Switch between them with `NextPageTemplate` + `PageBreak`.

## Pitfall: PDF header comparison in test scripts

**When:** Ad-hoc verification of generated PDFs

**Symptom:** `header[:5] == b"%PDF-1"` fails because `b"%PDF-1"` is 6 bytes, not 5.

**Fix:** Always use `.startswith()`:
```python
# ✅ Correct
with open(result, 'rb') as f:
    header = f.read(8)
assert header.startswith(b"%PDF-1."), f"Bad header: {header}"
```

## Pitfall: Module not found in verification scripts

**When:** Running ad-hoc verification with `python3 -c "import reportlab"` or inline scripts

**Symptom:** `ModuleNotFoundError: No module named 'reportlab'` even after install

**Fix:** The module is in `lazy-packages/`, not the default Python path. Always
add it to `sys.path` before importing:
```python
import sys
sys.path.insert(0, '/opt/data/lazy-packages')
import reportlab  # now works
```

For longer verification scripts, create them under `/opt/data/` (not `/tmp/` —
the write sandbox restricts `/tmp/` writes).

## Pitfall: Deep research without verification = wasted iteration

**When:** Generating professional documents (PDFs, reports, POCs) based on external research

**Symptom:** Producing output that looks right but has structural issues (missing sections,
wrong business model framework, omitted constraints).

**Fix:** Always run ad-hoc verification BEFORE declaring a deliverable complete:
1. Syntax check (ast.parse)
2. Import check (all modules load)
3. End-to-end generation (file exists + non-trivial size)
4. PDF header validation (starts with `%PDF-1.`)
5. Content validation (PyMuPDF opens + text extraction for required sections)
6. Semantic checks (key concepts like "VTDF" or "LTV:CAC" present in text)
7. Cleanup (delete temp file)

This pattern is now captured as skill: `productivity/deep-research-methodology`