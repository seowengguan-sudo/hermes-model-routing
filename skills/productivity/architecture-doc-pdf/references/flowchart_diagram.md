# FlowChart Flowable — control-loop / process diagrams in reportlab

Subclass `Flowable` and draw with `reportlab.graphics.shapes` primitives. This produced the
14-step Hermes Agentic Control Loop diagram (standalone PDF + embedded in the arch spec).

## Skeleton
```python
from reportlab.platypus import Flowable
from reportlab.lib.units import mm
from reportlab.lib import colors

class FlowChart(Flowable):
    def __init__(self, width=186*mm, height=240*mm):
        self.width=width; self.height=height
    def wrap(self, *a):
        return (self.width, self.height)
    def draw(self):
        c=self.canv
        W,H=self.width,self.height
        c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
        def box(x,y,w,h,text,fill,stroke=colors.HexColor('#305496'),fs=8.5):
            c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(0.8)
            c.roundRect(x,y,w,h,4,fill=1,stroke=1)
            c.setFillColor(colors.white); c.setFont('Helvetica-Bold',fs)
            words=text.split(' '); lines=[]; cur=''
            for wd in words:
                if len(cur)+len(wd)+1<=34: cur=(cur+' '+wd).strip()
                else: lines.append(cur); cur=wd
            if cur: lines.append(cur)
            lines=lines[:3]; th=fs+2; ty=y+h/2+(len(lines)-1)*th/2
            for ln in lines: c.drawCentredString(x+w/2,ty,ln); ty-=th
        def arrow(x1,y1,x2,y2,col=colors.HexColor('#7F7F7F')):
            import math
            c.setStrokeColor(col); c.setLineWidth(1.1); c.line(x1,y1,x2,y2)
            ang=math.atan2(y2-y1,x2-x1); L=6
            c.line(x2,y2,x2-L*math.cos(ang-0.4),y2-L*math.sin(ang-0.4))
            c.line(x2,y2,x2-L*math.cos(ang+0.4),y2-L*math.sin(ang+0.4))
        # ... place boxes in two columns, vertical connectors, one horizontal
        # bridge between columns, and a returning arc for the closed loop.
```

## Key lessons
- Use a **two-column zig-zag** for long step lists (e.g. 7 steps per column) to fit on one page.
- Draw a **returning green arc** on the right edge to show "closed loop" and label it.
- Color-code boxes (green=local/learning, amber=guard/verify/gate, blue=routing/budget) + legend.
- Word-wrap labels inside `box()` by splitting to ≤3 lines and vertically centering.
- Title band: filled `rect` at top with white bold centered text.

## Verification
Render the page to PNG (dpi 110) and run `vision_analyze` to confirm no overlap / cutoff / arrow
collision before delivering.
