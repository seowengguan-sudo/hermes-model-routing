# UI interaction fixes for doc_reader_onefile.py Settings modal

Captured from a session where the user reported 4 UI issues in the Settings page.

## Issue ⚠️ CRITICAL: Toggle switch itself not clickable (root cause of ALL buttons failing)

**Symptom:** ALL buttons stopped working on the Windows portable app — upload browse,
settings button, etc. The entire JS UI appeared broken.

**Root cause (found 2026-08-17):** The `.switch input` CSS had `display: none` to hide
the raw checkbox. BUT with this setting, the checkbox is NOT rendered by the browser,
meaning clicks on the slider do NOT toggle the checkbox. Combined with the removed `for`
attribute on the label (Issue 1), there was NO way to toggle any category checkbox.

The fix for Issue 1 (removing `for` from label) was correct to prevent label click area,
but it left the checkbox unreachable when `display: none` was used.

**Fix:** Change the CSS for `.switch input` from:
```css
.switch input { display: none; }
```
to:
```css
.switch input { opacity: 0; width: 100%; height: 100%; cursor: pointer; position: relative; z-index: 2; }
```
- `opacity: 0` makes the checkbox invisible but STILL RENDERED and CLICKABLE
- `width: 100%; height: 100%` makes it cover the entire slider area
- `z-index: 2` ensures it's on top of the slider
- `cursor: pointer` gives visual feedback

This pattern also applies to the smart toggle switch (`.switch.big`) which uses the same
CSS rule.

**Verification:** After this fix, clicking the toggle switch directly toggles the checkbox
and the `onchange="toggleCategory(...)"` handler fires correctly.

## Issue 1: Toggle button click area too broad

**Symptom:** Clicking the category label text toggles the checkbox — the user only
wants the toggle switch itself to trigger enable/disable.

**Root cause:** The `<label>` element had a `for="cb_<key>"` attribute, which
associates it with the checkbox. Combined with `flex: 1` on the label, the entire
row became clickable.

**Fix:**
1. Remove the `for` attribute from the generated `<label>` HTML
2. Add `pointer-events: none` to `.cat-row label` CSS
3. Remove `cursor: pointer` from `.cat-row` (set to `default`) since there's no click
   handler anymore — the cat-row itself does nothing on click
4. The checkbox is now only clickable via the switch area (enabled by the opacity:0 fix above)

```javascript
// Before: '<label for="cb_' + catKey + '">' ...
// After:
'<label>' ...
```

```css
.cat-row label { flex: 1; cursor: default; font-size: 14px; display: flex; align-items: center; gap: 8px; pointer-events: none; }
.cat-row input[type=checkbox] { width: 19px; height: 19px; accent-color: var(--gc, #0ea5e9); cursor: pointer; }
.cat-row { cursor: default; }
```

## Issue 2: Group expand/collapse via entire header row

**Symptom:** Clicking anywhere on the group header toggled expand/collapse,
including on the All/None buttons and group title. The user wants only
the chevron/arrow to control this.

**Root cause:** The `onclick` handler was on the entire `.group-head` div:
`onclick="this.parentElement.classList.toggle('collapsed')"`

**Fix:**
1. Remove `onclick` from `.group-head` div
2. Add `onclick` to ONLY the chevron `<span>`:
```javascript
'<span class="chev" onclick="event.stopPropagation();this.parentElement.parentElement.classList.toggle(\'collapsed\')">▼</span>'
```
- `event.stopPropagation()` prevents the click from bubbling to any parent handler
- `this.parentElement.parentElement` navigates from chevron -> group-tools -> group-head -> group

**IMPORTANT:** The chevron onclick uses SINGLE QUOTES around `'collapsed'` inside a
double-quoted HTML attribute. This is safe because the HTML attribute uses double quotes.
NEVER use backticks around `collapsed` here — they break the JavaScript string evaluation.

CSS adds `cursor: pointer` to `.chev` for visual affordance:
```css
.chev { transition: transform .2s; color: var(--muted); font-size: 13px; cursor: pointer; }
.group-head { ... cursor: default; ... }  /* No longer pointer since no onclick */
```

## Issue 3: All/None button visibility

**Symptom:** The All/None buttons for each group were present but hard to see
and click.

**Fix:** Enhanced the `.mini-btn` CSS:
- Increased padding from `9px 14px` → `10px 16px`
- Added `min-width: 52px` and `text-align: center`
- Added hover effect: `background: var(--accent); color: #fff;`
- Added `transition: all .2s` for smooth hover animation

These buttons already worked correctly — they call `groupAll(groupName, true/false)`
which sets all subcategories in that group. The fix was purely visual.

## Issue 4: Single-file upload only

**Symptom:** Only one file could be uploaded and processed at a time, even though
the file input had `multiple` attribute.

**Root cause:** The frontend stored only `selectedFile` (single) and the backend
returned immediately after processing the first file.

**Fix (frontend):**
1. Changed `let selectedFile = null` -> `let selectedFiles = []`
2. File input change handler: `selectedFiles = Array.from(files)`
3. Filename display: show file count + total size for multi-file
4. Form data: loop through all files `for (let i = 0; i < selectedFiles.length; i++)`
5. Drag-drop handler: same array-based approach
6. Response handler: check `data.documents` (array) vs `data.original_filename` (single)

**Fix (backend):**
1. Added `results = []` before the file processing loop in `_handle_upload`
2. Changed `self._json(200, {...})` + `return` -> `results.append({...})`
3. After loop: return `self._json(200, {"documents": results, "total_documents": len(results)})`
4. Added `resetFileUI()` call after successful processing

**Verification:** 3 files uploaded simultaneously -> all 3 processed independently,
results displayed with per-file redaction counts and links.

## Debugging pitfall: Escaping in Python string-generated HTML/JS

When working with JS inside Python strings that generate HTML:
- The Python string uses double-quoted JS: `"' + onclick + '"`
- HTML attributes use double quotes: `onclick="..."`
- JavaScript strings with literal values use single quotes: `toggle('collapsed')`
- NEVER use backticks inside HTML onclick attributes — they are NOT template literals in this context

**Example pattern that works:**
```python
'<span class="chev" onclick="event.stopPropagation();this.parentElement.parentElement.classList.toggle(\\'collapsed\\')">▼</span>'
```

**Pattern that breaks (backticks):**
```python
# This creates toggle(`collapsed`) which is NOT a valid JS string!
'<span class="chev" onclick="...toggle(`collapsed`)">▼</span>'
```
