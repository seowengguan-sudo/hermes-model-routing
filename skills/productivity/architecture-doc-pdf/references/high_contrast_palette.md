# High-Contrast Palette (verified after user rejected washed-out tints)

Use these constants in BOTH diagrams (Flowable boxes) and tables. Do NOT invent pastel hex
values — they read as "soft / not sharp" and users reject them.

## Fills (saturated, white bold text on top)
NAVY   = '#1F3864'   # title bands, topology "you/model-pool" grey-ish layers use #595959 text
BLUE   = '#2E5C9E'   # routing / budget / cost-aware tier
GREEN  = '#2E7D32'   # local / cache / learn / ~0-cost
AMBER  = '#B7791F'   # guard / verify / gate / paid-escalation
RED    = '#B91C1C'   # P0 abort / destructive
PURPLE = '#6B2C91'   # interrupt yield points
GREY_FILL = '#595959' # neutral layers (you / model pool) — pair with #1A1A1A text

## Strokes / lines
BOX_STROKE = dark version of the fill (e.g. GREEN fill → GREEN stroke), width 1.3–1.4pt
TABLE_GRID = '#888888'  (never '#BFBFBF')
ARROW      = '#333333'

## Text
WHITE_BOLD = colors.white, Helvetica-Bold  (on saturated fills)
DARK_TEXT  = '#1A1A1A' (on grey fills like LGREY)
CAPTION    = '#333333' (captions/legends/footers — never '#555' or '#7F7F7F')

## Zebra striping (tables)
ROW_ALT = '#EEF2F8'  (subtle, not pale-blue wash)

## Diagram box recipe (Flowable._box)
- fill = saturated color; stroke = same hue darker; lineWidth 1.3
- text: Helvetica-Bold, white, fontSize >= 8 (7.8 ok for 22-step loops)
- support explicit '\n' line breaks in labels (split on '\n' then words)
- legend swatches: use the SATURATED fill (not a tint)

## Verified result
Applied to Hermes_Architecture_Diagrams_v35.pdf and the Solidified spec PDF; vision_analyzed
each dense page with the prompt "is contrast good / any low-contrast or washed-out areas?"
→ all clean. This is the bar to meet before declaring a diagram/PDF done.
