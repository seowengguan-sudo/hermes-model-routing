# openpyxl / xlsx handling — fix + environment setup

## The corruption bug (hit this session, cost real time)
Writing an `.xlsx` via `write_file` plain text, heredoc `echo`, or TSV **corrupts the
ZIP container** — Excel/Pymupdf reject it ("no such file" / not a zip). The file must be
a real OOXML zip. ALWAYS use openpyxl:

```python
import openpyxl
wb = openpyxl.load_workbook('file.xlsx')   # or Workbook() for new
ws = wb['SheetName']                         # or wb.create_sheet('Name')
ws.append([a,b,c])                           # add rows
# edit cells: ws.cell(r,c).value = ...
wb.save('file.xlsx')
```

## Environment (this host: WSL2, Python 3.13.5, no pip, PEP668)
- `pip` is absent; `python3 -m pip` fails. Use **uv**.
- Create venv + install once:
  ```bash
  uv venv hermes-venv
  source hermes-venv/bin/activate
  uv pip install openpyxl pymupdf reportlab
  ```
- These three cover: xlsx edit (openpyxl), PDF render/verify (pymupdf), PDF build
  (reportlab). Reuse the same venv across sessions.

## Verification after edit (prove, don't assert)
```python
import openpyxl, pymupdf
wb = openpyxl.load_workbook('file.xlsx')     # raises if corrupt
print(wb.sheetnames, wb['Sheet'].max_row)
d = pymupdf.open('file.pdf'); print(d.page_count, not d.is_closed)
```
Render a page to confirm visuals: `d[i].get_pixmap(dpi=110).save('/tmp/p.png')` then vision_check.

## Sheet/column discipline
- When adding capability, ADD a new sheet/column; never overwrite the model matrix or
  sequence columns the user already validated.
- After edits, confirm original columns still present:
  `sum(1 for x in header if str(x).startswith('SEQ_'))`.
