# Hand-rolled PDF via stdlib (deliverable technique)

When no PDF library (reportlab/fpdf) is installed and pip is unavailable
(PEP 668), generate a valid PDF 1.4 by writing bytes directly. The #1 failure
mode that makes the file unopenable is a WRONG xref offset table.

## Correct structure
```
%PDF-1.4\n
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [6 0 R 8 0 R ...] /Count N >> endobj
3 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj   # F1
4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Courier >> endobj     # F2
5 0 obj << /Length L >> stream\n<content ops>\nendstream\nendobj  # page 1 content
6 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents 5 0 R >> endobj
... (one content + one page obj per page, ids 5+2i, 6+2i)
xref
0 M
0000000000 65535 f
<offset> 00000 n   # for obj 1, obj 2, ...
...
trailer
<< /Size M /Root 1 0 R >>
startxref
<byte offset of 'xref'>
%%EOF
```

## Offset computation that works
Write each object to a bytearray, recording `len(out)` as the offset BEFORE writing
each object. Then emit the xref table using those recorded offsets. Verify after
writing: every offset in xref must land on `{objnum} 0 obj`. A mismatch = corrupt file.

## Verified generator
The working script is `/opt/data/architecture/make_pdf.py` (PDF class with text(),
fillrect(), newline(), build(); tracks offsets in build()). Reuse it as the template.

## Pitfall observed
`nemotron-3-super-120b-a12b:free` (OpenRouter) was asked to WRITE such a PDF script
and repeatedly returned PROSE instead of code (e.g. `import os" as the very first
characters...`). If a free model garbles generated code, fall back to a known-good
generator rather than shipping broken output. Lighter models (llama-3.1-8b) may be
more reliable for strict codegen than a 120B that rambles.
