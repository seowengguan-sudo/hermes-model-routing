---
name: architecture-diagram
description: "Dark-themed SVG architecture/cloud/infra diagrams as HTML."
version: 1.0.0
author: Cocoon AI (hello@cocoon-ai.com), ported by Hermes Agent
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [architecture, diagrams, SVG, HTML, visualization, infrastructure, cloud]
    related_skills: [concept-diagrams, excalidraw]
---

# Architecture Diagram Skill

Generate professional, dark-themed technical architecture diagrams as standalone HTML files with inline SVG graphics. No external tools, no API keys, no rendering libraries — just write the HTML file and open it in a browser.

## Scope

**Best suited for:**
- Software system architecture (frontend / backend / database layers)
- Cloud infrastructure (VPC, regions, subnets, managed services)
- Microservice / service-mesh topology
- Database + API map, deployment diagrams
- Anything with a tech-infra subject that fits a dark, grid-backed aesthetic

**Look elsewhere first for:**
- Physics, chemistry, math, biology, or other scientific subjects
- Physical objects (vehicles, hardware, anatomy, cross-sections)
- Floor plans, narrative journeys, educational / textbook-style visuals
- Hand-drawn whiteboard sketches (consider `excalidraw`)
- Animated explainers (consider an animation skill)

If a more specialized skill is available for the subject, prefer that. If none fits, this skill can also serve as a general SVG diagram fallback — the output will just carry the dark tech aesthetic described below.

Based on [Cocoon AI's architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) (MIT).

## Workflow

1. User describes their system architecture (components, connections, technologies)
2. Generate the HTML file following the design system below
3. Save with `write_file` to a `.html` file (e.g. `~/architecture-diagram.html`)
4. User opens in any browser — works offline, no dependencies

### Output Location

Save diagrams to a user-specified path, or default to the current working directory:
```
./[project-name]-architecture.html
```

## Preview

After saving, suggest the user open it:
```bash
# macOS
open ./my-architecture.html
# Linux
xdg-open ./my-architecture.html
```

> **⚠️ Local rendering note:** The browser-use daemon's Chromium sandbox blocks `file://` access (returns `chrome-error://chromewebdata/`). If programmatic screenshot verification is needed, serve over HTTP from a non-localhost address:
> ```bash
> python3 -m http.server 0.0.0.0:8899 --directory .
> # then load via container IP in the browser tool
> ```
> Local `localhost`/`127.0.0.1` URLs are also blocked by the sandbox. If no visual verification path exists, rely on the **Geometry Audit** (contrast + overlap + anchor math) as the substitute verification — it is more rigorous than visual inspection.

### Writing Large Diagrams (byte-cap workaround)

`write_file` truncates content at ~10,000 bytes. Large diagrams (2+ SVGs, multi-panel) must be split:
1. **First `write_file`**: write the `<head>`, CSS `<style>`, `<body>` open, first `<svg>` — stopping at a clean line *before* the 10KB cap. Verify with `read_file`.
2. **Second pass**: use `patch` with `old_string` = the last 1-2 lines of the first SVG, `new_string` = same lines + the appended remainder (second SVG, cards, `</body></html>`).

Never try to fit a multi-SVG diagram in one write call.

## Design System & Visual Language

### Color Palette (Semantic Mapping)

Use specific `fill="HEX"` + `fill-opacity="0.75"` + `stroke="HEX"` (bold stroke) to categorize components. **Validated high-contrast palette** (all ≥3:1 against `#020617` background at 0.75 opacity — verified by luminance math):

| Component Type | Fill (Hex @0.75) | Stroke |
| :--- | :--- | :--- |
| **Frontend** | `#0ea5e9` (sky-600) | `#06dafa` (cyan-400) |
| **Backend** | `#10b981` (emerald-600) | `#34d399` (emerald-400) |
| **Database** | `#a78bfa` (violet-400) | `#a78bfa` |
| **AWS/Cloud** | `#f59e0b` (amber-500) | `#fbbf24` (amber-400) |
| **Security** | `#ef4444` (red-500) | `#fb7185` (rose-400) |
| **Message Bus** | `#0d9488` (teal-600) | `#22d3ee` (cyan-300) |
| **External** | `#475569` (slate-600) | `#94a3b8` (slate-400) |
| **Sandbox** | `#f87171` (red-400) | `#fb7185` |
| **Scripts** | `#ea580c` (orange-600) | `#fbbf24` |

⚠️ **Do NOT** use the old `rgba(R,G,B, 0.3-0.5)` palette — at those opacities the blended result drops below 3:1 against `#020617` for dark colors (purple, deep teal, dark slate). If you must use a dark base color, push opacity to ≥0.80.

### Typography & Background
- **Font:** JetBrains Mono (Monospace), loaded from Google Fonts
- **Sizes:** 12px (Names), 9px (Sublabels), 8px (Annotations), 7px (Tiny labels)
- **Background:** Slate-950 (`#020617`) with a subtle 40px grid pattern

```svg
<!-- Background Grid Pattern -->
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
</pattern>
```

## Technical Implementation Details

### Component Rendering
Components are rounded rectangles (`rx="6"`) with 1.5px strokes. To prevent arrows from showing through semi-transparent fills, use a **double-rect masking technique**:
1. Draw an opaque background rect (`#0f172a`)
2. Draw the semi-transparent styled rect on top

### Connection Rules
- **Z-Order:** Draw arrows *early* in the SVG (after the grid) so they render behind component boxes
- **Arrowheads:** Defined via SVG markers
- **Security Flows:** Use dashed lines in rose color (`#fb7185`)
- **Boundaries:**
  - *Security Groups:* Dashed (`4,4`), rose color
  - *Regions:* Large dashed (`8,4`), amber color, `rx="12"`

### Spacing & Layout Logic
- **Standard Height:** 60px (Services); 80-120px (Large components)
- **Vertical Gap:** Minimum 40px between components
- **Message Buses:** Must be placed *in the gap* between services, not overlapping them
- **Legend Placement:** **CRITICAL.** Must be placed outside all boundary boxes. Calculate the lowest Y-coordinate of all boundaries and place the legend at least 20px below it.

### Geometry Audit (post-write verification)
Before handing off the diagram, run this programmatic check on the generated HTML:
1. **Real overlaps**: Parse all `<rect>` bounding boxes. Two rects "overlap" (defect) if they intersect AND neither fully contains the other (container-within-container is fine). Flag any real overlap >80px².
2. **Canvas utilization**: Compute the bounding box of all real rects vs the SVG viewBox. Horizontal utilization should be ≥85%; flag if <80% (means wasted whitespace = bad flow).
3. **Arrow anchoring**: For every `<line>`, verify at least one endpoint (x1,y1 or x2,y2) lands within 5px of a rect's edge (left/right/top/bottom). Arrow *label* text between boxes is OK — check the line, not the label.
4. **Contrast (WCAG)**: For every `fill="HEX"` + `fill-opacity="N"`, blend the color over `#020617` and compute luminance contrast ratio. Must be ≥3:1 for the fill to count; labels at `#fff` are ≥20:1 (always fine).

Sample checker (Python, run inline):
```python
import re, xml.dom.minidom as md
def blend(fg,bg,a): return tuple(int(a*fg[i]+(1-a)*bg[i]) for i in range(3))
def lum(r,g,b): ... # standard sRGB luminance
def cr(c1,c2): ...  # (max+0.05)/(min+0.05)
bg=(2,6,23)
# For each rect fill+opacity: cr(blend(hex, bg, opacity), bg) >= 3.0
# For each line: endpoint within 5px of a rect edge
# For each viewport: (maxx-minx)/vw >= 0.85
```

## Document Structure

The generated HTML file follows a four-part layout:
1. **Header:** Title with a pulsing dot indicator and subtitle
2. **Main SVG:** The diagram contained within a rounded border card
3. **Summary Cards:** A grid of three cards below the diagram for high-level details
4. **Footer:** Minimal metadata

### Info Card Pattern
```html
<div class="card">
  <div class="card-header">
    <div class="card-dot cyan"></div>
    <h3>Title</h3>
  </div>
  <ul>
    <li>• Item one</li>
    <li>• Item two</li>
  </ul>
</div>
```

## Output Requirements
- **Single File:** One self-contained `.html` file
- **No External Dependencies:** All CSS and SVG must be inline (except Google Fonts)
- **No JavaScript:** Use pure CSS for any animations (like pulsing dots)
- **Compatibility:** Must render correctly in any modern web browser
- **Must pass post-write:** HTML well-formed check, SVG well-formed XML check, Geometry Audit (overlaps/contrast/anchors), and ≥85% canvas utilization.

## Template Reference

Load the full HTML template for the exact structure, CSS, and SVG component examples:

```
skill_view(name="architecture-diagram", file_path="templates/template.html")
```

The template contains working examples of every component type (frontend, backend, database, cloud, security), arrow styles (standard, dashed, curved), security groups, region boundaries, and the legend — use it as your structural reference when generating diagrams.

## PDF Generation (reportlab)

When a printable PDF deliverable is required (e.g. professional architecture document), use reportlab in a dedicated venv:

```bash
cd /opt/data
uv venv hermes-pdf --python python3
source hermes-pdf/bin/activate
uv pip install reportlab pymupdf
```

### Architecture

1. **Master diagram first** (A3 landscape, `canvas.Canvas`): draw the holistic SVG diagram directly on canvas with `roundRect` boxes, `line` arrows, and `drawCentredString` labels — all in PDF-native coordinates (no SVG→PDF conversion needed).
2. **Convert to PNG** via pymupdf (`fitz`): `page.get_pixmap(dpi=170).save(PNG)`.
3. **Cover page** (A3 landscape): `PageTemplate(id='cover', onPage=cover_page)` draws the PNG as full-page background.
4. **Body pages** (A4 portrait): `PageTemplate(id='body', onPage=body_page)` with a `Frame` for text content (paragraphs + tables).

### ⚠️ Critical Pitfall: `st += [ht(...)]` in Python 3.12+

Python 3.12+ bytecode optimization changes how `story_list += [flowable]` compiles. The compiler emits `BUILD_LIST 1` followed by `BUILD_TUPLE 1`, wrapping the single flowable in a tuple-of-list: `([flowable],)`. When `list.__iadd__` receives `([flowable],)`, it iterates and appends the inner `[flowable]` list as-is — the flowable ends up **nested inside a list in the story**, causing `AttributeError: 'list' object has no attribute 'getKeepWithNext'`.

**Fix:** Use `st.append(ht(...))` instead of `st += [ht(...)]`. The `append` method directly adds the flowable object without any `+=`/`__iadd__` wrapping.

This affects ALL `st += [Flowable()]` patterns — not just tables. Use `st.append(...)` everywhere.

### Page-size switching

`BaseDocTemplate` sets one page size for all pages. To have an A3 cover + A4 body:
- `cover_page(cv, doc)` calls `cv.setPageSize(landscape(A3))` in `onPage`
- `body_page(cv, doc)` calls `cv.setPageSize(portrait(A4))` in `onPage`
- Story sequence: `[NextPageTemplate('cover'), NextPageTemplate('body'), PageBreak(), Paragraph(...), ...]`
  - Two `NextPageTemplate` calls: first activates cover template, second pre-activates body template
  - `PageBreak()` triggers cover page rendering (A3 via onPage)
  - Subsequent flowables use body template (A4 via onPage)
