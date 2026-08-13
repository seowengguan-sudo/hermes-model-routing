# Safe xlsx editing (do not corrupt the workbook)

The `Provider-Model_FINAL*.xlsx` files are REAL binary (.xlsx = ZIP of XML), not TSV/CSV.

## WRONG (corrupts the file — happened once)
Reading it as text, splitting on `\t`, appending columns, writing back as text. The result is
unopenable in Excel despite a `PK..` magic header, because the internal XML/ZIP structure is broken.

## RIGHT (openpyxl)
```bash
cd /opt/data/architecture
uv venv hermes-venv && source hermes-venv/bin/activate
uv pip install openpyxl
```
```python
import openpyxl
wb = openpyxl.load_workbook('Provider-Model_FINAL_0.xlsx')
ws = wb['Master Model Matrix']
start_col = ws.max_column + 1
for i, name in enumerate(new_cols):
    ws.cell(row=1, column=start_col+i, value=name)
    for r in range(2, ws.max_row+1):
        ws.cell(row=r, column=start_col+i, value=seq[name])
wb.save('Provider-Model_FINAL_0.xlsx')
```
Verify after save: `openpyxl.load_workbook(...)` succeeds and `ws.dimensions` grew.

## Tips
- If pandas is needed: it is not on the system interpreter; install into a venv (uv venv) — the
  system Python is externally-managed (PEP 668). `pip`/`pip3` are absent; use `uv pip install`.
- Keep a pristine backup before overwriting: `cp src.xlsx src_original_backup.xlsx`.

## The `read_file` TSV DECOY (why the corruption happens)
`read_file` on a `.xlsx` returns what *looks* like tab-separated text. That is the extractor's
decoded view — **not** the on-disk format. The bytes are a ZIP (`PK\x03\x04` magic). If you take
that TSV, mutate it, and write it back (even with `errors='ignore'`), you emit a non-ZIP file Excel
cannot open. This is exactly how the 2026-08-08 corruption occurred. **Never** treat the `read_file`
output as the file format. Edit only through `load_workbook`/`save`. To inspect, use `openpyxl` or
`fitz`/`pymupdf`, not `read_file`.

## Multi-sheet build recipe (append cols to every row + add sheets + style)
```python
header = [c.value for c in ws[1]]
old_start = next((i for i,h in enumerate(header) if h and str(h).startswith('USE_AS_')), None)
base = header[:old_start] if old_start is not None else header
new_header = base + ['Context Window','Max Output Tokens','Est $/M In','Est $/M Out'] + [f'SEQ_{c}' for c in CATS]
for i,name in enumerate(new_header, start=1):
    ws.cell(row=1, column=i, value=name)
for r in range(2, ws.max_row+1):
    if not ws.cell(r,1).value: continue
    # write capacity + 4-slot SEQ columns at len(base)+1 .. 
wb.create_sheet('Category_Sequence')   # clean per-category lookup (1 row per USE_AS)
wb.create_sheet('Provider_Budget')     # live quota ledger the token-gate loop reads
for sheet in [ws, ws_seq, ws_bud]:
    for c in sheet[1]:
        c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='305496')
    sheet.freeze_panes = 'A2'
    for col in sheet.columns:
        w = max((len(str(c.value)) for c in col if c.value is not None), default=10)
        sheet.column_dimensions[col[0].column_letter].width = min(max(w+2,12),60)
wb.save(OUT)
```
Verify: `openpyxl.load_workbook(OUT)` succeeds, `ws.max_column` equals expected, spot-check 1–2 new cells.

## Building the companion PDF with reportlab (platypus)
`uv pip install reportlab` in the venv. Wrap long table-cell text in `Paragraph()`, not raw strings
(raw strings truncate in tables). **Numbered lists:** DO NOT pass `value='1.'` to `ListItem` —
`ListFlowable([ListItem(Paragraph(s,BODY), leftIndent=12, value=str(i+1)+'.') ...], bulletType='1', start='1')`
raises `ValueError: invalid literal for int() with base 10: '1.'`. Use `ListItem(Paragraph(s,BODY), leftIndent=12)`
with `bulletType='1', start=1` and let reportlab number automatically. Verify with `fitz.open(OUT).page_count`.
