#!/usr/bin/env python3
"""Fix settings UI issues in doc_reader_onefile.py"""
import re

filepath = '/opt/data/projects/doc_reader/doc_reader_onefile.py'

with open(filepath, 'r') as f:
    content = f.read()

original = content
fixes_applied = 0

# ─── FIX #1: Remove 'for' attribute from label ───
# This prevents the label from intercepting clicks meant for the checkbox
old_label = "'<label for=\"cb_' + catKey + '\">'"
new_label = "'<label>'"

if old_label in content:
    content = content.replace(old_label, new_label, 1)
    print("✅ Fix #1: Removed 'for' attribute from label")
    fixes_applied += 1
else:
    print("❌ Fix #1: Label pattern not found")

# ─── FIX #2: Move group-header onclick to chevron only ───
# Remove onclick from group-head div
old_group_head = "group-head\" onclick=\"this.parentElement.classList.toggle('collapsed')\">"
new_group_head = "group-head\">"

if old_group_head in content:
    content = content.replace(old_group_head, new_group_head, 1)
    print("✅ Fix #2a: Removed onclick from group-head")
    fixes_applied += 1
else:
    print("❌ Fix #2a: group-head onclick not found")

# Add onclick to chevron - use 3 parents to reach .group div
old_chev = '<span class="chev">▼</span>'
new_chev = '<span class="chev" onclick="event.stopPropagation();this.parentElement.parentElement.classList.toggle(\\'collapsed\\')">▼</span>'

chev_count = content.count(old_chev)
if old_chev in content:
    content = content.replace(old_chev, new_chev, 1)  # Replace first chevron only
    print(f"✅ Fix #2b: Added onclick to main group chevron ({chev_count} found)")
    fixes_applied += 1
else:
    print("❌ Fix #2b: Chevron pattern not found")

# ─── FIX #3: Improve mini-btn CSS ───
old_mini = '.mini-btn { padding: 9px 14px; border-radius: 10px; border: 1px solid var(--border-2); background: var(--surface-2); font-size: 13px; font-weight: 600; cursor: pointer; color: var(--primary); }'
new_mini = '.mini-btn { padding: 10px 16px; border-radius: 10px; border: 1px solid var(--border-2); background: var(--surface-2); font-size: 14px; font-weight: 600; cursor: pointer; color: var(--primary); min-width: 52px; text-align: center; transition: all .2s; } .mini-btn:hover { background: var(--accent); color: #fff; }'

if old_mini in content:
    content = content.replace(old_mini, new_mini, 1)
    print("✅ Fix #3: Enhanced mini-btn CSS with hover effects")
    fixes_applied += 1
else:
    print("❌ Fix #3: mini-btn CSS not found")

# ─── FIX #4: Multi-file upload support ───

# 4a: Change selectedFile to selectedFiles array
old_var = "let selectedFile = null;"
new_var = "let selectedFiles = [];"
if old_var in content:
    content = content.replace(old_var, new_var, 1)
    print("✅ Fix #4a: Changed selectedFile to selectedFiles array")
    fixes_applied += 1
else:
    print("❌ Fix #4a: File variable pattern not found")

# 4b: Update file input change handler
old_change = """fileInput.addEventListener('change', () => {
  const files = fileInput.files;
  if (files.length > 0) {
    selectedFile = files[0];
    fileNameDiv.textContent = files.length === 1
      ? selectedFile.name + ' (' + Math.round(selectedFile.size/1024) + ' KB)'
      : files.length + ' files selected';
    processBtn.disabled = false;
    processBtn.textContent = 'Process ' + files.length + ' file(s)';
  } else { resetFileUI(); }
});"""

new_change = """fileInput.addEventListener('change', () => {
  const files = fileInput.files;
  if (files.length > 0) {
    selectedFiles = Array.from(files);
    fileNameDiv.textContent = files.length === 1
      ? selectedFiles[0].name + ' (' + Math.round(selectedFiles[0].size/1024) + ' KB)'
      : files.length + ' files selected (' + Math.round(Array.from(files).reduce((a,f)=>a+f.size,0)/1024) + ' KB total)';
    processBtn.disabled = false;
    processBtn.textContent = 'Process ' + files.length + ' file(s)';
  } else { resetFileUI(); }
});"""

if old_change in content:
    content = content.replace(old_change, new_change, 1)
    print("✅ Fix #4b: Updated file input change handler for multiple files")
    fixes_applied += 1
else:
    print("❌ Fix #4b: File input change handler not found")

# 4c: Update resetFileUI
old_reset = "processBtn.disabled = true; processBtn.textContent = 'Upload & Process'; selectedFile = null;"
new_reset = "processBtn.disabled = true; processBtn.textContent = 'Upload & Process'; selectedFiles = [];"
if old_reset in content:
    content = content.replace(old_reset, new_reset, 1)
    print("✅ Fix #4c: Updated resetFileUI to clear array")
    fixes_applied += 1
else:
    print("❌ Fix #4c: resetFileUI pattern not found")

# 4d: Update process check
old_check = "if (!selectedFile) return;"
new_check = "if (selectedFiles.length === 0) return;"
if old_check in content:
    content = content.replace(old_check, new_check, 1)
    print("✅ Fix #4d: Updated process check to use array length")
    fixes_applied += 1
else:
    print("❌ Fix #4d: Process check pattern not found")

# 4e: Update formData.append to loop through all files
old_append = "formData.append('file', selectedFile);"
new_append = "for (let i = 0; i < selectedFiles.length; i++) {\n      formData.append('file', selectedFiles[i]);\n    }"
if old_append in content:
    content = content.replace(old_append, new_append, 1)
    print("✅ Fix #4e: Updated formData to append all files in loop")
    fixes_applied += 1
else:
    print("❌ Fix #4e: formData.append pattern not found")

# 4f: Update drag-and-drop handler
old_drop = """dropZone.addEventListener('drop', e => {
  if (e.dataTransfer.files.length) {
    fileInput.files = e.dataTransfer.files;
    selectedFile = e.dataTransfer.files[0];
    fileNameDiv.textContent = selectedFile.name + ' (' + Math.round(selectedFile.size/1024) + ' KB)';
    processBtn.disabled = false; processBtn.textContent = 'Process ' + e.dataTransfer.files.length + ' file(s)';
    if (e.dataTransfer.files.length === 1) setTimeout(() => processBtn.click(), 100);
  }
});"""

new_drop = """dropZone.addEventListener('drop', e => {
  if (e.dataTransfer.files.length) {
    fileInput.files = e.dataTransfer.files;
    selectedFiles = Array.from(e.dataTransfer.files);
    const totalSize = selectedFiles.reduce((a,f) => a+f.size, 0);
    fileNameDiv.textContent = selectedFiles.length === 1
      ? selectedFiles[0].name + ' (' + Math.round(selectedFiles[0].size/1024) + ' KB)'
      : selectedFiles.length + ' files selected (' + Math.round(totalSize/1024) + ' KB total)';
    processBtn.disabled = false; processBtn.textContent = 'Process ' + selectedFiles.length + ' file(s)';
    if (selectedFiles.length === 1) setTimeout(() => processBtn.click(), 100);
  }
});"""

if old_drop in content:
    content = content.replace(old_drop, new_drop, 1)
    print("✅ Fix #4f: Updated drag-drop handler for multiple files")
    fixes_applied += 1
else:
    print("❌ Fix #4f: Drag-drop handler not found")

# ─── FIX #5: Backend multi-file support ───

# 5a: Add results array before file processing loop
old_loop = """                for part in parts:
                    if b"filename=" in part:"""
new_loop = """                results = []
                for part in parts:
                    if b"filename=" in part:"""
if old_loop in content:
    content = content.replace(old_loop, new_loop, 1)
    print("✅ Fix #5a: Added results list initialization")
    fixes_applied += 1
else:
    print("❌ Fix #5a: Upload loop pattern not found")

# 5b: Change single return to results.append
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
    print("✅ Fix #5b: Changed single return to results.append")
    fixes_applied += 1
else:
    print("❌ Fix #5b: Upload return pattern not found")

# 5c: Add multi-file response handler
old_no_file = """                self._json(400, {"error": "No file uploaded"})"""
new_no_file = """                if results:
                    self._json(200, {
                        "documents": results,
                        "total_documents": len(results)
                    })
                else:
                    self._json(400, {"error": "No file uploaded"})"""
if old_no_file in content:
    content = content.replace(old_no_file, new_no_file, 1)
    print("✅ Fix #5c: Added multi-file response handler")
    fixes_applied += 1
else:
    print("❌ Fix #5c: No file uploaded pattern not found")

# ─── FIX #6: Update frontend response handler ───
old_handler = """    } else {
      resultTitle.textContent = data.original_filename || 'Document Processed';
      resultStatus.className = 'status-badge status-success';
      resultStatus.textContent = '✓ Complete';"""

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
    } else {
      resultTitle.textContent = data.original_filename || 'Document Processed';
      resultStatus.className = 'status-badge status-success';
      resultStatus.textContent = '✓ Complete';"""

# Check if single-handler exists first
if old_handler in content:
    content = content.replace(old_handler, new_handler, 1)
    print("✅ Fix #6: Updated frontend to handle multi-file response")
    fixes_applied += 1
else:
    # Check if new_handler already exists (maybe already applied)
    if "} else if (data.documents)" in content:
        print("✅ Fix #6: Multi-file handler already present")
    else:
        print("❌ Fix #6: Frontend handler pattern not found")

# Save if changes were made
if content != original:
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"\n🎉 {fixes_applied} fixes applied and saved!")
else:
    print("\n❌ No changes were made to the file")
