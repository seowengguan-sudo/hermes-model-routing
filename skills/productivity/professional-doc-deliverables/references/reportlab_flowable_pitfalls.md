# reportlab Flowable / Diagram Pitfalls (from a long iterative architecture-PDF build)

When hand-drawing control-loop / flow diagrams by subclassing `Flowable` and using
reportlab.graphics primitives (`roundRect`, `polygon`, `line`, `drawCentredString`),
these bugs recur and are **invisible until you render the page to PNG and vision-check it**.
They do NOT show up in `pymupdf` text extraction.

## 1. `tuple(color)` TypeError
```python
def box(self, ..., stroke=tuple(BLUE), ...):   # BLUE is a Color, not iterable
```
Fix: default `stroke=BLUE` (pass the `Color` object directly). Never wrap a `Color` in `tuple(...)`.

## 2. Double `colors.HexColor(fill)` -> `TypeError: unsupported operand '>>'`
If you pre-wrap (`colors.HexColor(fill)`) and pass it into a helper that ALSO does
`colors.HexColor(fill)`, you call `HexColor(Color)` and it blows up.
Fix: make the box helper accept both forms:
```python
f = fill if isinstance(fill, colors.Color) else colors.HexColor(fill)
s = stroke if isinstance(stroke, colors.Color) else colors.HexColor(stroke)
c.setFillColor(f); c.setStrokeColor(s)
```
Use this guard in every diagram-building script. It ends the whole class of error.

## 3. `Flowable.__init__(width=..., height=...)` kwargs
`reportlab.platypus.Flowable.__init__` takes **positional** `(width, height)`, not kwargs.
`FlowChart(width=W, height=H)` -> `TypeError: unexpected keyword argument 'width'`.
Fix: call positionally `FlowChart(W, H)`, or override `def __init__(self,w,h): self.width=w; self.height=h; Flowable.__init__(self)`.

## 4. `\n` line breaks inside labels
A naive `text.split(' ')` turns an embedded `\n` into a literal token that overflows the
box and breaks wrapping. Fix: split on `\n` first, then words; treat `\n` as a forced
line break (flush current line, start empty):
```python
raw = text.split('\n'); words=[]
for seg in raw: words += seg.split(' '); words.append('\n')
if words and words[-1]=='\n': words.pop()
lines=[]; cur=''
for wd in words:
    if wd=='\n':
        if cur: lines.append(cur)
        lines.append(''); cur=''; continue
    if len(cur)+len(wd)+1 <= wrapw: cur=(cur+' '+wd).strip()
    else: lines.append(cur); cur=wd
if cur: lines.append(cur)
lines = lines[:4]   # cap to avoid overflow
```

## 5. Stray half-edited syntax
e.g. `words = text.split(' '; ) if False else text.split(' ')`. SyntaxError wastes a turn.
Lint catches it but you lose the call. Write clean expressions.

## 6. Closed-loop return arc math
When drawing a return arrow from the last step back to step 1, compute its y-centers from
the SAME `top`/`rowh`/index math used for the boxes, or the arc lands off the boxes.
Pattern: `yN = (top - offset - (N-1)*rowh) + bh/2`.

## Verification (non-negotiable)
Always: build -> pymupdf render densest page to PNG (dpi 110) -> vision_analyze for
overlap / cutoff / arrow collision / margin overflow. Fix -> re-render. Overlap bugs are
image-only; text extraction will report "valid PDF" while the user sees clashing text.
