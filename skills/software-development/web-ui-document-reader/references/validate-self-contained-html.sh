#!/usr/bin/env bash
# validate-self-contained-html.sh — one-shot gate for SVG/HTML deliverables
# Usage: ./references/validate-self-contained-html.sh /path/to/diagram.html
#
# Checks: (1) HTML tag balance, (2) SVG well-formedness, (3) arrow anchoring,
# (4) color contrast vs background (#020617). Fails nonzero if any check fails.
#
# Run from the skill dir: skill_view the script, chmod +x, execute.
# Captures the validation pattern from session 2026-08-16 architecture diagrams.

set -euo pipefail
HTML_FILE="${1:-${1:?usage: $0 /path/to/diagram.html}}"

python3 - "$HTML_FILE" <<'PY'
import re, os, sys
from html.parser import HTMLParser
from xml.dom.minidom import parseString

VOID = {'img','br','hr','input','meta','link','area','base','col','embed','source','track','wbr'}

class TagBalance(HTMLParser):
    def __init__(self):
        super().__init__(); self.stk=[]; self.mismatches=[]
    def handle_starttag(self,t,a):
        if t not in VOID: self.stk.append(t)
    def handle_endtag(self,t):
        if self.stk and self.stk[-1]==t: self.stk.pop()
        elif t in self.stk:
            while self.stk and self.stk[-1]!=t:
                self.mismatches.append(f"close </{t}> mismatched with {self.stk[-1]}"); self.stk.pop()
            if self.stk: self.stk.pop()
        else: self.mismatches.append(f"stray </{t}>")

def hx2rgb(h):
    h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def lum(r,g,b):
    a=[v/255. for v in (r,g,b)]
    a=[v/12.92 if v<=0.03928 else ((v+0.055)/1.055)**2.4 for v in a]
    return .2126*a[0]+.7152*a[1]+.0722*a[2]
def blend(fg,bg,a): return tuple(int(a*fg[i]+(1-a)*bg[i]) for i in range(3))
def contrast(c1,c2):
    l1,l2=max(lum(*c1),lum(*c2)),min(lum(*c1),lum(*c2)); return (l1+.05)/(l2+.05)
BG = hx2rgb('020617')
RECT = re.compile(r'<rect\b[^>]+\bx="(\d+)"[^>]+y="(\d+)"[^>]+width="(\d+)"[^>]+height="(\d+)"')
LINE = re.compile(r'<line\b[^>]+x1="(\d+)"[^>]+y1="(\d+)"[^>]+x2="(\d+)"[^>]+y2="(\d+)"')

h = open(sys.argv[1]).read()
errors = []

# 1. HTML tag balance
p = TagBalance(); p.feed(h)
if p.stk: errors.append(f"HTML unclosed tags: {p.stk[-5:]}")
if p.mismatches: errors.extend(p.mismatches)

# 2. SVG well-formedness
for i,(vb,body) in enumerate(re.findall(r'<svg[^>]*viewBox="([^"]+)"[^>]*>(.*?)</svg>', h, re.S)):
    try:
        parseString(f'<svg viewBox="{vb}">{body}</svg>')
    except Exception as e:
        errors.append(f"SVG#{i} parse error: {e}")

# 3. Arrow anchoring — every endpoint within 4px of a rect edge
rects = [(int(x),int(y),int(w),int(ht)) for x,y,w,ht in RECT.findall(h)]
rects = [(x,y,x+w,y+ht) for x,y,w,ht in rects if x+w<2500]  # filter grid bg
def near(px,py):
    for rx,ry,rX,rY in rects:
        if (abs(px-rx)<=4 or abs(px-rX)<=4) and ry-4<=py<=rY+4: return True
        if (abs(py-ry)<=4 or abs(py-rY)<=4) and rx-4<=px<=rX+4: return True
    return False
for x1,y1,x2,y2 in [(int(a),int(b),int(c),int(d)) for a,b,c,d in LINE.findall(h)]:
    if not (near(x1,y1) or near(x2,y2)):
        errors.append(f"unanchored arrow: ({x1},{y1}->{x2},{y2})")

# 4. Color contrast — every fill-opacity=0.75 hex
for m in re.finditer(r'fill="([#a-f0-9]{7})"\s+fill-opacity="0\.75"', h, re.I):
    c = blend(hx2rgb(m.group(1)), BG, 0.75)
    r = contrast(c, BG)
    if r < 3.0: errors.append(f"low contrast: {m.group(1)} @0.75 = {r:.2f}:1")

print(f"  size={os.path.getsize(sys.argv[1])}B  errors={len(errors)}")
if errors:
    for e in errors[:10]: print(f"  ✗ {e}")
    sys.exit(1)
print("  ✓ all checks passed")
PY
