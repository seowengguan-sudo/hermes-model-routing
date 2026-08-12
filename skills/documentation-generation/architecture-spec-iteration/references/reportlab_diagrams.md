# Reusable high-contrast reportlab diagram pattern

Used inside `build_*.py` to draw flowcharts/loops for spec PDFs. Verified clean across
v3.3→v3.6 of the Hermes architecture docs (rendered + vision-checked, no overlap/cutoff).

## Palette (APPROVED — high contrast, user-mandated)
- NAVY  #1F3864  (headers, metacog steps)
- BLUE  #2E5C9E  (routing/budget/dispatch)
- GREEN #2E7D32  (local/cache/learn)
- AMBER #B7791F  (guard/verify/gate)
- RED   #B91C1C  (abort / P0)
- PURPLE #6B2C91 (interrupt yield points)
- TEAL  #0F766E  (orchestration)
- text inside boxes: WHITE BOLD
- caption/legend text: #333333 (never #555 — too faint)
- grid lines in tables: #888888

## Flowable skeleton
```python
class Diagram(Flowable):
    def __init__(self,w,h): self.width=w; self.height=h
    def wrap(self,*a): return (self.width,self.height)
    def draw(self):
        c=self.canv; W=self.width; H=self.height
        c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
        def box(x,y,w,h,text,fill,stroke,tcol=colors.white,fs=8.0,lw=1.3):
            f = fill if isinstance(fill,colors.Color) else colors.HexColor(fill)
            s = stroke if isinstance(stroke,colors.Color) else colors.HexColor(stroke)
            c.setFillColor(f); c.setStrokeColor(s); c.setLineWidth(lw)
            c.roundRect(x,y,w,h,4,fill=1,stroke=1)
            c.setFillColor(tcol); c.setFont('Helvetica-Bold',fs)
            raw=str(text).split('\n'); words=[]
            for seg in raw: words+=seg.split(' '); words.append('\n')
            if words and words[-1]=='\n': words.pop()
            lines=[]; cur=''
            for wd in words:
                if wd=='\n':
                    if cur: lines.append(cur)
                    lines.append(''); cur=''; continue
                if len(cur)+len(wd)+1<=wrapw: cur=(cur+' '+wd).strip()
                else: lines.append(cur); cur=wd
            if cur: lines.append(cur)
            lines=lines[:4]; th=fs+2; ty=y+h/2+(len(lines)-1)*th/2
            for ln in lines: c.drawCentredString(x+w/2,ty,ln); ty-=th
        def arrow(x1,y1,x2,y2,col=GREY,lw=1.1):
            c.setStrokeColor(col); c.setLineWidth(lw); c.line(x1,y1,x2,y2)
            ang=math.atan2(y2-y1,x2-x1); L=6
            c.line(x2,y2,x2-L*math.cos(ang-0.4),y2-L*math.sin(ang-0.4))
            c.line(x2,y2,x2-L*math.cos(ang+0.4),y2-L*math.sin(ang+0.4))
        # ... lay out steps, call box()/arrow() ...
```

## Critical gotchas (caused real failures this session)
- **Pass colors consistently.** `box()` accepts a `colors.Color` OR a hex string; do NOT
  double-wrap (`colors.HexColor(colors.HexColor(...))`) — raises "unsupported operand for >>".
  If you pre-wrap, pass the Color object directly, not re-wrapped.
- **Flowable subclasses take positional (w,h), NOT kw `width=`.** `Diagram(W,H)` not
  `Diagram(width=W,height=H)` — kwargs raise "unexpected keyword argument 'width'".
- **Don't feed a coordinate where a color is expected.** A float like `16*mm+16*mm` (≈90.7pt)
  passed as the `col` arg of `arrow()` raises "Unknown color". Keep arrow args as
  (x1,y1,x2,y2,col,lw) and use plain numbers for coords.
- **Two-column loop + closed arc:** left col steps 1..N, right col N+1..2N; horizontal
  arrow from top-left(N) to top-right(N+1); green arc from bottom-right(2N) back to top-left(1).
- **Legend:** draw small rounded swatches + bold black labels below the diagram.
```
