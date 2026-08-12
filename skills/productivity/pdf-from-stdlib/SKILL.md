---
name: pdf-from-stdlib
description: "Generate PDFs in pure Python stdlib with no PDF library."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [pdf, reportlab, fpdf, stdlib, document-generation, fallback]
---

# PDF Generation From Stdlib (No External Deps)

## When to use
- You need to emit a `.pdf` but `reportlab`, `fpdf`, `weasyprint`, `wkhtmltopdf`, and `pandoc` are all absent (common in minimal Docker/WSL images: `pip list` shows none, `which wkhtmltopdf pandoc` empty).
- You want a self-contained script that writes a valid PDF 1.4 with multiple pages, headings, body text, and ASCII diagrams — no pip install required.

## Minimal valid PDF 1.4 writer
A PDF is: header `%PDF-1.4\n`, then objects, then `xref`, `trailer`, `startxref`. Key rules:
1. Objects are numbered sequentially: `N 0 obj\n<data>\nendobj\n`.
2. Page objects reference a shared `/Pages` object and a `/Resources << /Font >>` dict.
3. Text uses PDF text operators inside a content stream: `BT /F1 10 Tf 1 0 0 1 x y Tm (escaped text) Tj ET`.
4. **Escape** parentheses and backslashes in text: `(`→`\(`, `)`→`\)`, `\`→`\\`.
5. The `xref` table must list every object with byte offsets; offset 0 is the free entry `0000000000 65535 f `.
6. `trailer` has `<< /Size N /Root 1 0 R >>` and `startxref <byteOffsetOfXref>\n%%EOF`.

## Layout technique (emulate flow layout)
Maintain a running `y` cursor. Helper methods: `newpage()`, `section(title)` (draws a filled rect + title text, decrements y), `body(lines)` (each line text at current y, decrement), `diagram_block(lines)` (monospace font F2 for ASCII art). When `y < 60`, call `newpage()` and reset `y=800`. Store each page's content operators in a list; on `build()` assemble objects and compute xref offsets by tracking running byte position.

## Pitfalls (all hit and fixed in-session)
- **Tuple arg order bug**: if `body()` takes `(indent, text)` tuples, the call must be `(indent, text)` — NOT `(text, indent)`. A reversed tuple causes `TypeError: unsupported operand for +: 'int' and 'str'` on `42 + ln[1]*10`.
- **xref offset math**: this is the #1 cause of "PDF won't open" in hand-rolled writers. Track each object's byte offset DURING concatenation (record `offsets[onum] = len(out)` right before appending each object's chunk), then build the xref from that dict. Do NOT hardcode or estimate. When a user says "PDF cannot open", suspect the xref table first — verify every offset lands on `N 0 obj` (check in `references/minimal-pdf-writer.md`). **Prefer the verified writer `scripts/pdf_writer.py`** as your starting point instead of rewriting from scratch; it handles offset tracking, content-stream `stream`/`endstream` + `/Length` wrapping, and `xref`/`trailer` correctly. (An earlier skeleton here that used `newpage()` and omitted stream wrapping produced an unopenable file — do not reuse it.)
- **Object numbering**: catalog=1, pages=2, fonts=3,4, then for each page a content-stream obj + page obj. Keep a dict `byid[oid]=bytes` and emit in sorted oid order.
- **Content stream bytes**: the text operators string must be encoded to bytes before concatenation; mixing str and bytes raises `TypeError`.
- Verify output: `header == b'%PDF-1.4'`, `b'%%EOF' in data`, `data.count(b' obj') >= 10`, and page count via `data.count(b'/Type /Page') - data.count(b'/Type /Pages')`.
- **xref validator (run it before declaring the PDF done)** — catches the #1 "won't open" cause:
```python
import re
def validate_pdf(path):
    d=open(path,'rb').read()
    assert d[:8]==b'%PDF-1.4' and b'%%EOF' in d
    xoff=int(re.search(rb'startxref\s+(\d+)',d).group(1))
    xref=d[xoff:].split(b'\n')
    cnt=int([l for l in xref if re.match(rb'0 \d+',l.strip())][0].strip().split()[1])
    cntl=[l for l in xref if re.match(rb'0 \d+',l.strip())][0]
    for j in range(1,cnt):
        e=xref[xref.index(cntl)+1+j].strip().split(); off=int(e[0])
        assert d[off:off+12].decode('latin-1','replace').startswith(f'{j} 0 obj'), f'bad offset obj {j}'
    return True  # all xref offsets land on their objects
```

## Pitfall: delegating the PDF script to an LLM (learned 2026-08-07)
When you ask a model (e.g. Nemotron-120B, Llama-3.1-8B) to *write* the generator script, it often:
- Returns **prose narrating the script** instead of code ("We need to output a Python script that...") — the first line is not `import`.
- Garbles the opening: concatenates your instruction text into the code (`import os" as the very first characters...`).
- **Truncates mid-string** at the default `max_tokens` (3500), leaving an unterminated string literal — bump to 6000 and re-extract from `import os`.
- Produces structurally-correct-looking code with **broken PDF operators** (uses `Td` without `BT`/`ET` wrappers, wrong `re f` fill order) — runs but emits an unopenable 11-byte file.
**Mitigation:** (a) demand "first line must be exactly `import os`, no markdown, no prose"; (b) extract defensively — `re.search(r'import os.*', raw, re.DOTALL)`; (c) `ast.parse()` before running; (d) **prefer writing/validating the generator yourself** (the `scripts/pdf_writer.py` class) — you control correctness, the model does not. The model is fine for *content*, not for *the PDF byte-layer*.

## Reference
- `references/minimal-pdf-writer.md` — verified, openable skeleton (with xref-offset validator).
- `scripts/pdf_writer.py` — ready-to-run `PDF` class; import it and call `.build()` for a valid multi-page PDF with zero dependencies.
