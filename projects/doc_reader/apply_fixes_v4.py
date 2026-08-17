#!/usr/bin/env python3
"""Apply UI fixes to doc_reader_onefile.py - targeted line-by-line approach"""

filepath = '/opt/data/projects/doc_reader/doc_reader_onefile.py'

with open(filepath, 'r') as f:
    lines = f.readlines()

changes = []

# ─── FIX #1: Remove 'for' attribute from label (line ~1603) ───
# This makes the label non-interactive, so only the switch itself gets clicks
for i, line in enumerate(lines):
    if "label for=\"cb_" in line and "catRow" not in line:
        # Change '<label for="cb_' + catKey + '">' to '<label>'
        old = "<label for="
        new = "<label>"
        lines[i] = line.replace(old, new)
        changes.append(f"Fix #1: Removed 'for' attribute from label at line {i+1}")
        break

# ─── FIX #2: Move group-header onclick to chevron ───
# Find group-head with onclick and remove it
for i, line in enumerate(lines):
    if "group-head" in line and "onclick" in line and "toggle" in line:
        # Replace the onclick attribute
        lines[i] = line.replace(' onclick="this.parentElement.classList.toggle(\'collapsed\')"', '')
        changes.append(f"Fix #2a: Removed onclick from group-head at line {i+1}")
        break

# Find chevron and add onclick
for i, line in enumerate(lines):
    if 'class="chev">▼</span>' in line:
        # Add onclick to the chevron span
        lines[i] = line.replace(
            '<span class="chev">▼</span>',
            '<span class="chev" onclick="event.stopPropagation();this.parentElement.parentElement.classList.toggle(\'collapsed\')">▼</span>'
        )
        changes.append(f"Fix #2b: Added onclick to chevron at line {i+1}")
        break

# ─── FIX #3: Already applied via apply_fixes_v3.py ───
# (CSS enhancement for mini-btn was already done)

# ─── FIX #4: Multi-file upload - already partially applied by v3 ───
# Need to verify remaining items

# ─── FIX #6: Frontend response handler for multi-file ───
# This needs to be added where success is shown
# Find the `} else {` success handler
found_success_handler = False
for i, line in enumerate(lines):
    if "} else {" in line and i > 1400 and i < 1500:
        context_after = ''.join(lines[i+1:i+10])
        if "resultTitle.textContent" in context_after and "Document Processed" in context_after:
            # This is the success handler we need to enhance
            # For now, just make sure resetFileUI is called
            if "resetFileUI()" not in ''.join(lines[i:i+30]):
                # Add resetFileUI() after the success block
                # Find the end of the else block
                for j in range(i+1, min(i+50, len(lines))):
                    if "processBtn.disabled = false" in lines[j] and "Upload & Process" in lines[j]:
                        lines[j] += "\n      resetFileUI();"
                        changes.append(f"Fix #4-complete: Added resetFileUI() after success at line {j+1}")
                        break
            found_success_handler = True
            break

if not found_success_handler:
    # Search more broadly
    for i, line in enumerate(lines):
        if "resultStatus.textContent = '✓ Complete';" in line:
            # Check if resetFileUI() is called nearby
            nearby = ''.join(lines[max(0,i-5):i+10])
            if "resetFileUI()" not in nearby:
                # Insert resetFileUI() call
                lines.insert(i+1, "      resetFileUI();\n")
                changes.append(f"Fix #4-complete: Added resetFileUI() at line {i+2}")
            break

# Save changes
with open(filepath, 'w') as f:
    f.writelines(lines)

print(f"Applied {len(changes)} fixes:")
for c in changes:
    print(f"  ✅ {c}")
if not changes:
    print("  ⚠️ No changes needed (fixes may already be applied)")
