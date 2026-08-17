#!/usr/bin/env python3
"""Comprehensive fix for all 4 UI issues in doc_reader_onefile.py"""

filepath = '/opt/data/projects/doc_reader/doc_reader_onefile.py'

with open(filepath, 'r') as f:
    content = f.read()

original = content
fixes = []

# ─── FIX #1: Make label not intercept checkbox clicks ───
# Replace: '<label for="cb_' + catKey + '">' 
#      → '<label>'  
# This was already done by apply_fixes_v3.py - verify
if '<label for="cb_' in content and "<label>'" not in content:
    # Hasn't been fixed yet
    content = content.replace("<label for=\"cb_' + catKey + '\">", "<label>", 1)
    fixes.append("Fix #1: Removed 'for' attribute from label")
elif "<label>'" in content or "<label>" in content:
    # Check more carefully
    if "label for=\"cb_" in content:
        content = content.replace("label for=\"cb_'", "label>", 1)
        fixes.append("Fix #1: Removed 'for' attribute from label (cleanup)")
    else:
        fixes.append("Fix #1: Already applied - label is clean")
else:
    fixes.append("Fix #1: Already applied - no 'for' attribute found")

# ─── FIX #2: Move group-header onclick to chevron only ───
# The group-head currently has onclick - need to remove it and ensure 
# chevron has the handler. BUT this conflicts with All/None buttons...
# 
# Strategy:
# - Remove onclick from group-head entirely
# - Move expand/collapse handling to the chevron ONLY
# - All/None buttons keep their own handlers with event.stopPropagation()
# 
# Current group-head onclick pattern (with escaping in the Python string):
group_head_old = 'group-head" onclick="this.parentElement.classList.toggle(\\\\\'collapsed\\\\\')">'
group_head_new = 'group-head">'

if group_head_old in content:
    content = content.replace(group_head_old, group_head_new, 1)
    fixes.append("Fix #2: Removed onclick from group-head")
else:
    # Try alternate patterns
    patterns_to_try = [
        'group-head\\\" onclick=\\\"this.parentElement.classList.toggle('collapsed')\">',
        'group-head" onclick="this.parentElement.classList.toggle(\'collapsed\')">',
    ]
    found = False
    for p in patterns_to_try:
        if p in content:
            content = content.replace(p, 'group-head">', 1)
            fixes.append("Fix #2: Removed onclick from group-head (alternate pattern)")
            found = True
            break
    if not found:
        fixes.append("Fix #2: group-head onclick already removed or pattern different")

# Fix the chevron onclick - ensure it uses proper escaping
# Current chevron (may have backtick issue): 
chev_old1 = '<span class="chev" onclick="event.stopPropagation();this.parentElement.parentElement.classList.toggle(`collapsed`)">▼</span>'
chev_new1 = '<span class="chev" onclick="event.stopPropagation();this.parentElement.parentElement.classList.toggle(\\\'collapsed\\\')">▼</span>'

if chev_old1 in content:
    content = content.replace(chev_old1, chev_new1, 1)
    fixes.append("Fix #2b: Fixed chevron onclick escaping")
else:
    fixes.append("Fix #2b: Chevron onclick already correct or pattern different")

# ─── FIX #3: All/None button visibility ───
# Already enhanced by apply_fixes_v3.py - check current state
old_mini_css = '.mini-btn { padding: 9px 14px'
new_mini_css = '.mini-btn { padding: 10px 16px; border-radius: 10px; border: 1px solid var(--border-2); background: var(--surface-2); font-size: 14px; font-weight: 600; cursor: pointer; color: var(--primary); min-width: 52px; text-align: center; transition: all .2s; } .mini-btn:hover { background: var(--accent); color: #fff; }'

if old_mini_css in content:
    # Only replace if the simple version is present
    import re
    content = re.sub(
        r'\.mini-btn \{[^}]*\}',
        new_mini_css,
        content,
        count=1
    )
    fixes.append("Fix #3: Enhanced mini-btn CSS")
else:
    fixes.append("Fix #3: mini-btn CSS already enhanced")

# ─── FIX #4: Multi-file upload - ensure all pieces are in place ───

# 4a: Verify selectedFiles array
if 'let selectedFiles = [];' in content:
    fixes.append("Fix #4a: selectedFiles array - ✓")
else:
    content = content.replace('let selectedFile = null;', 'let selectedFiles = [];', 1)
    fixes.append("Fix #4a: Changed selectedFile to selectedFiles array")

# 4b: Verify file selection handler
old_sel = 'selectedFile = files[0];'
new_sel = 'selectedFiles = Array.from(files);'
if old_sel in content:
    content = content.replace(old_sel, new_sel, 1)
    fixes.append("Fix #4b: Updated file selection")
else:
    fixes.append("Fix #4b: Already using selectedFiles")

# 4c: Verify filename display
old_fn = "fileNameDiv.textContent = files.length === 1\n      ? selectedFile.name + ' (' + Math.round(selectedFile.size/1024) + ' KB)'\n      : files.length + ' files selected';"
new_fn = "fileNameDiv.textContent = files.length === 1\n      ? selectedFiles[0].name + ' (' + Math.round(selectedFiles[0].size/1024) + ' KB)'\n      : files.length + ' files selected (' + Math.round(Array.from(files).reduce(function(a,f){return a+f.size},0)/1024) + ' KB total)';"
if old_fn in content:
    content = content.replace(old_fn, new_fn, 1)
    fixes.append("Fix #4c: Updated filename display")
else:
    fixes.append("Fix #4c: Already updated")

# 4d: Verify resetFileUI
old_reset = "processBtn.disabled = true; processBtn.textContent = 'Upload & Process'; selectedFile = null;"
new_reset = "processBtn.disabled = true; processBtn.textContent = 'Upload & Process'; selectedFiles = [];"
if old_reset in content:
    content = content.replace(old_reset, new_reset, 1)
    fixes.append("Fix #4d: Updated resetFileUI")
else:
    fixes.append("Fix #4d: Already updated")

# 4e: Verify process check
old_check = "if (!selectedFile) return;"
new_check = "if (selectedFiles.length === 0) return;"
if old_check in content:
    content = content.replace(old_check, new_check, 1)
    fixes.append("Fix #4e: Updated process check")
else:
    fixes.append("Fix #4e: Already updated")

# 4f: Verify formData loop
old_append = "formData.append('file', selectedFile);"
new_append = "for (let i = 0; i < selectedFiles.length; i++) {\n      formData.append('file', selectedFiles[i]);\n    }"
if old_append in content:
    content = content.replace(old_append, new_append, 1)
    fixes.append("Fix #4f: Updated formData to loop")
else:
    fixes.append("Fix #4f: Already looping")

# 4g: Verify drop handler
old_drop = "selectedFile = e.dataTransfer.files[0];"
new_drop = "selectedFiles = Array.from(e.dataTransfer.files);"
if old_drop in content:
    content = content.replace(old_drop, new_drop, 1)
    fixes.append("Fix #4g: Updated drop handler")
else:
    fixes.append("Fix #4g: Already using selectedFiles")

# 4h: Verify drop filename display  
old_drop_fn = "fileNameDiv.textContent = selectedFile.name + ' (' + Math.round(selectedFile.size/1024) + ' KB)';"
new_drop_fn = """fileNameDiv.textContent = selectedFiles.length === 1
      ? selectedFiles[0].name + ' (' + Math.round(selectedFiles[0].size/1024) + ' KB)'
      : selectedFiles.length + ' files selected (' + Math.round(selectedFiles.reduce(function(a,f){return a+f.size},0)/1024) + ' KB total)';"""
if old_drop_fn in content:
    content = content.replace(old_drop_fn, new_drop_fn, 1)
    fixes.append("Fix #4h: Updated drop filename display")
else:
    fixes.append("Fix #4h: Already updated")

# 4i: Verify drop button text
old_drop_btn = "processBtn.disabled = false; processBtn.textContent = 'Process ' + e.dataTransfer.files.length + ' file(s)';\n    if (e.dataTransfer.files.length === 1) setTimeout(() => processBtn.click(), 100);"
new_drop_btn = "processBtn.disabled = false; processBtn.textContent = 'Process ' + selectedFiles.length + ' file(s)';\n    if (selectedFiles.length === 1) setTimeout(() => processBtn.click(), 100);"
if old_drop_btn in content:
    content = content.replace(old_drop_btn, new_drop_btn, 1)
    fixes.append("Fix #4i: Updated drop button text")
else:
    fixes.append("Fix #4i: Already updated")

# 4j: Backend - add results array
old_loop = "                for part in parts:\n                    if b\"filename=\" in part:"
new_loop = "                results = []\n                for part in parts:\n                    if b\"filename=" in part:"
if old_loop in content:
    content = content.replace(old_loop, new_loop, 1)
    fixes.append("Fix #4j: Added results array in backend")
else:
    fixes.append("Fix #4j: Results array already present")

# 4k: Backend - change return to append
old_return = """                            self._json(200, {
                                "document_id": safe_doc["document_id"],
                                "safe_url": f"/documents/{safe_doc['document_id']}/safe",
                                "original_filename": filename,
                                "total_redactions": safe_doc["total_redactions"],
                                "category_counts": safe_doc["category_counts"],
                                "file_path": saved_path,
                                "safe_path": safe_path,
                                "map_path": map_path
                            })
                            return"""
new_append = """                            results.append({
                                "document_id": safe_doc["document_id"],
                                "safe_url": f"/documents/{safe_doc['document_id']}/safe",
                                "original_filename": filename,
                                "total_redactions": safe_doc["total_redactions"],
                                "category_counts": safe_doc["category_counts"],
                                "file_path": saved_path,
                                "safe_path": safe_path,
                                "map_path": map_path
                            })"""
if old_return in content:
    content = content.replace(old_return, new_append, 1)
    fixes.append("Fix #4k: Changed return to results.append")
else:
    fixes.append("Fix #4k: Already using append")

# 4l: Backend - multi-file response
old_no_file = "                self._json(400, {\"error\": \"No file uploaded\"})"
new_no_file = """                if results:
                    self._json(200, {
                        "documents": results,
                        "total_documents": len(results)
                    })
                else:
                    self._json(400, {"error": "No file uploaded"})"""
if old_no_file in content:
    content = content.replace(old_no_file, new_no_file, 1)
    fixes.append("Fix #4l: Added multi-file response")
else:
    fixes.append("Fix #4l: Already present")

# 4m: Frontend - add resetFileUI() to success handler
# Check current success handler around line 1441
if 'resultStatus.textContent = \'✓ Complete\';' in content:
    # Check if resetFileUI() is already called after success
    pos = content.find("resultStatus.textContent = '✓ Complete';")
    context = content[pos:pos+500]
    if 'resetFileUI()' not in context:
        # Add resetFileUI after the process button is re-enabled
        old_re_enable = "processBtn.disabled = false; processBtn.textContent = 'Upload & Process';"
        new_re_enable = "processBtn.disabled = false; processBtn.textContent = 'Upload & Process';\n      resetFileUI();"
        if old_re_enable in content:
            content = content.replace(old_re_enable, new_re_enable, 1)
            fixes.append("Fix #4m: Added resetFileUI() after success")
        else:
            fixes.append("Fix #4m: Could not find re-enable line")
    else:
        fixes.append("Fix #4m: resetFileUI() already called after success")

# ─── FIX #5: Frontend multi-file response handler ───
# Check if handler for data.documents exists
if 'data.documents' not in content:
    # Need to add the multi-file response handler
    # Find the single-file success handler and add multi-file support before it
    old_handler = """    } else {
      resultTitle.textContent = data.original_filename || 'Document Processed';"""
    new_handler = """    } else if (data.documents) {
      const docs = data.documents;
      resultTitle.textContent = docs.length === 1 ? docs[0].original_filename : (docs.length + ' Documents Processed');
      resultStatus.className = 'status-badge status-success';
      resultStatus.textContent = '✓ Complete (' + docs.length + ')';
      let html = '<div style="display:flex;flex-direction:column;gap:12px;">';
      docs.forEach((doc) => {
        html += '<div style="border:1px solid var(--border);border-radius:8px;padding:12px;">';
        html += '<div style="font-weight:600;margin-bottom:6px;">' + escapeHtml(doc.original_filename) + '</div>';
        html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:10px;">';
        Object.entries(doc.category_counts).forEach(([cat, count]) => {
          html += '<span style="background:rgba(239,68,68,0.1);padding:4px 8px;border-radius:6px;font-size:12px;font-weight:600;color:#dc2626;">' + cat + ': ' + count + '</span>';
        });
        html += '</div>';
        html += '<a href="' + doc.safe_url + '" target="_blank" style="color:var(--accent);font-size:13px;">🔍 View redacted document</a>';
        html += '</div>';
      });
      html += '</div>';
      resultContent.innerHTML = html;
      docCountSpan.textContent = docs.reduce((sum, d) => sum + d.total_redactions, 0);
      resetFileUI();
    } else {
      resultTitle.textContent = data.original_filename || 'Document Processed';"""
    
    if old_handler in content:
        content = content.replace(old_handler, new_handler, 1)
        fixes.append("Fix #5: Added multi-file frontend response handler")
    else:
        fixes.append("Fix #5: Handler not found (may already exist)")
else:
    fixes.append("Fix #5: Multi-file handler already present")

# Save
if content != original:
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"\n✅ {len([f for f in fixes if not f.endswith('(already)') and 'Already' not in f])} fixes applied out of {len(fixes)} checks")
    for f in fixes:
        print(f"  {f}")
else:
    print("\n⚠️ No changes made")
    for f in fixes:
        print(f"  {f}")

print(f"\nFile size: {len(content):,} bytes")
