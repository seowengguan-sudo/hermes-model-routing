---
name: svg-diagram-audit
description: "Validate SVG diagrams for geometry and contrast."
version: 0.1.0
author: Hermes Agent
license: MIT
dependencies: []
platforms: [linux, macos]
metadata:
  hermes:
    tags: [svg, diagram, validation, geometry, contrast]
---

# SVG Diagram Audit
When generating architecture diagrams as standalone HTML+inline-SVG, you cannot always open a browser to visually inspect them (sandboxed renderers block file:// and localhost). Programmatic validator catches visual defects - box overlaps, label-anchoring failures, contrast collapses, malformed markup.

## Workflow
1. Generate SVG diagram HTML
2. Run: python3 scripts/svg_audit.py diagram.html
3. Pass/fail per check with pixel coordinates
4. Fix failures before declaring complete

## Checks (7)
1. Box overlap (non-container): sibling rects intersecting >80px^2
2. Canvas utilization: warn if <70% H or <45% V
3. Arrow anchoring: endpoints within 5px of rect edge
4. Text containment: text inside parent rect (except mid-line labels)
5. Color contrast: fills at 0.75 opacity >=3.0:1 vs #020617
6. SVG XML well-formedness: xml.dom.minidom parse
7. HTML tag balance: no unclosed/mismatched tags

## Pitfalls (session evidence)
- Semi-transparent fills (rgba .3-.5) = 1.08-2.22:1 vs #020617 = WCAG FAIL. Fix: hex at opacity 0.75
- Boundary box same layer as children buries content. Fix: inset 15-20px
- Sibling boxes at same y crash (cron daemon x=330 w=320 vs scripts x=530 at y=160). Fix: stack vertically
- browser-use Chromium rejects file:// and localhost. Workaround: programmatic audit
- Dangling text tag from edits breaks SVG parse. Fix: parse-check after every edit

## Layout best practices
- viewBox 0 0 1220 H (380 single, 700 doc)
- Entry row at y=75/80, 20px+ gap
- Arrows right-edge to left-edge
- Inset boundary 15-20px

## Color + typography
- Background #020617; labels #fff 9.5px; sublabels #cbd5e1 8px
- Fills: saturated hex at opacity 0.75, >=3.0:1
- Captions: #9ca3af at 7.9:1

## Linked files
- references/contrast-validation.md
- scripts/svg_audit.py
