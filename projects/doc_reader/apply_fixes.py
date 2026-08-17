#!/usr/bin/env python3
"""Fix settings UI issues in doc_reader_onefile.py"""
import re

filepath = '/opt/data/projects/doc_reader/doc_reader_onefile.py'

with open(filepath, 'r') as f:
    content = f.read()

original = content

# ─── FIX #1: Remove 'for' attribute from label so label doesn't intercept checkbox clicks ───
old_label = '\'<label for="cb_\' + catKey + \'">\''
new_label = '\'<label>\''

if old_label in content:
    content = content.replace(old_label, new_label, 1)
    print("✅ Fix #1: Removed 'for' attribute from label")
else:
    print("❌ Label pattern not found")

# ─── FIX #2: Move group-header onclick to chevron only ───
# Remove onclick from group-head
old_pattern = r'<div class="group-head" onclick="this\.parentElement\.classList\.toggle\(\\'"collapsed\\'\)"'
new_str = '<div class="group-head">'

if re.search(old_pattern, content):
    content = re.sub(old_pattern, new_str, content, count=1)
    print("✅ Fix #2a: Removed onclick from group-head")
else:
    print("❌ group-head onclick pattern not found, trying simpler pattern")
    # Try simpler pattern
    simpler = "onclick=\"this.parentElement.classList.toggle('collapsed')\"
    if simpler in content:
        content = content.replace(simpler, '', 1)
        print("✅ Fix #2a: Removed onclick from group-head (simpler pattern)")
    else:
        print("❌ Simpler pattern also not found")

# Add onclick to chevron
old_chev = '<span class="chev">▼</span>'
# The onclick needs to reference the group div (parent of group-head)
new_chev = '<span class="chev" onclick="event.stopPropagation();this.parentElement.parentElement.classList.toggle(\\'collapsed\\')">▼</span>'

chev_count = content.count(old_chev)
print(f"   Found {chev_count} chevron(s)")

if old_chev in content:
    content = content.replace(old_chev, new_chev, 1)  # First one is the group chevron
    print("✅ Fix #2b: Added onclick to chevron for expand/collapse")
else:
    print("❌ Chevron pattern not found")

# ─── FIX #3: Improve All/None button visibility ───
# We'll add CSS to make min-btn buttons more prominent
# Find the mini-btn CSS and enhance it
old_mini_css = '.mini-btn { padding: 9px 14px; border-radius: 10px; border: 1px solid var(--border-2); background: var(--surface-2); font-size: 13px; font-weight: 600; cursor: pointer; color: var(--primary); }'
new_mini_css = '.mini-btn { padding: 10px 14px; border-radius: 10px; border: 1px solid var(--border-2); background: var(--surface-2); font-size: 13px; font-weight: 600; cursor: pointer; color: var(--primary); min-width: 48px; text-align: center; }'
# Also add a hover state for better visibility

if old_mini_css in content:
    content = content.replace(old_mini_css, new_mini_css, 1)
    print("✅ Fix #3: Enhanced mini-btn CSS for better visibility")
else:
    print("❌ mini-btn CSS pattern not found")

# ─── FIX #4: Multi-file upload support ───
# Frontend changes
# 1. Change selectedFile to selectedFiles array
old_file_var = 'let selectedFile = null;'
new_file_var = 'let selectedFiles = [];'

if old_file_var in content:
    content = content.replace(old_file_var, new_file_var, 1)
    print("✅ Fix #4a: Changed selectedFile to selectedFiles array")
else:
    print("❌ File variable pattern not found")

# 2. Update file input change handler
old_change_handler = """fileInput.addEventListener('change', () => {
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

new_change_handler = """fileInput.addEventListener('change', () => {
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

if old_change_handler in content:
    content = content.replace(old_change_handler, new_change_handler, 1)
    print("✅ Fix #4b: Updated file input change handler for multiple files")
else:
    print("❌ File input change handler pattern not found")

# 3. Update resetFileUI
old_reset = "processBtn.disabled = true; processBtn.textContent = 'Upload & Process'; selectedFile = null;"
new_reset = "processBtn.disabled = true; processBtn.textContent = 'Upload & Process'; selectedFiles = [];"

if old_reset in content:
    content = content.replace(old_reset, new_reset, 1)
    print("✅ Fix #4c: Updated resetFileUI to clear array")
else:
    print("❌ resetFileUI pattern not found")

# 4. Update the process button click handler
old_process_check = "if (!selectedFile) return;"
new_process_check = "if (selectedFiles.length === 0) return;"

if old_process_check in content:
    content = content.replace(old_process_check, new_process_check, 1)
    print("✅ Fix #4d: Updated process check to use array")
else:
    print("❌ Process check pattern not found")

# 5. Update formData.append to loop through all files
old_append = "formData.append('file', selectedFile);"
new_append = """for (let i = 0; i < selectedFiles.length; i++) {
      formData.append('file', selectedFiles[i]);
    }"""

if old_append in content:
    content = content.replace(old_append, new_append, 1)
    print("✅ Fix #4e: Updated formData to append all files")
else:
    print("❌ formData.append pattern not found")

# 6. Update drag-and-drop handler for multiple files
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
else:
    print("❌ Drag-drop handler pattern not found")

# ─── FIX #5: Update backend to process multiple files ───
# Change _handle_upload to process all files instead of returning after first
old_upload_return = """                            self._json(200, {
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

new_upload_return = """                            results.append({
                                "document_id": safe_doc["document_id"],
                                "safe_url": f"/documents/{safe_doc['document_id']}/safe",
                                "original_filename": filename,
                                "total_redactions": safe_doc["total_redactions"],
                                "category_counts": safe_doc["category_counts"],
                                "file_path": saved_path,
                                "safe_path": safe_path,
                                "map_path": map_path
                            })"""

# First, we need to add `results = []` before the for loop
old_for_loop = """                for part in parts:
                    if b"filename=" in part:"""
new_for_loop = """                results = []
                for part in parts:
                    if b"filename=" in part:"""

if old_for_loop in content:
    content = content.replace(old_for_loop, new_for_loop, 1)
    print("✅ Fix #5a: Added results list initialization")

if old_upload_return in content:
    content = content.replace(old_upload_return, new_upload_return, 1)
    print("✅ Fix #5b: Changed single return to append to results array")
else:
    print("❌ Upload return pattern not found")

# Add the return for multiple files after the for loop
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
else:
    print("❌ No file uploaded pattern not found")

# ─── FIX #6: Update frontend to handle multi-file response ───
old_json_handler = """    if (data.error) {
      resultTitle.textContent = 'Processing Error';
      resultStatus.className = 'status-badge status-error';
      resultStatus.textContent = '✗ Failed';
      resultContent.innerHTML = '<div class=\"banner-err\">Error: ' + escapeHtml(data.error) + '</div>';
      resultsSection.style.display = 'block';
    } else {
      resultTitle.textContent = data.original_filename || 'Document Processed';
      resultStatus.className = 'status-badge status-success';
      resultStatus.textContent = '✓ Complete';"""

new_json_handler = """    if (data.error) {
      resultTitle.textContent = 'Processing Error';
      resultStatus.className = 'status-badge status-error';
      resultStatus.textContent = '✗ Failed';
      resultContent.innerHTML = '<div class=\"banner-err\">Error: ' + escapeHtml(data.error) + '</div>';
      resultsSection.style.display = 'block';
    } else if (data.documents) {
      // Multi-file response
      const docs = data.documents;
      resultTitle.textContent = docs.length === 1 ? docs[0].original_filename : (docs.length + ' Documents Processed');
      resultStatus.className = 'status-badge status-success';
      resultStatus.textContent = '✓ Complete (' + docs.length + ')';
      let html = '<div style="display:flex;flex-direction:column;gap:12px;">';
      docs.forEach((doc, i) => {
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

# This is the old pattern
old_single_handler = """    } else {
      resultTitle.textContent = data.original_filename || 'Document Processed';
      resultStatus.className = 'status-badge status-success';
      resultStatus.textContent = '✓ Complete';"""

if old_single_handler in content:
    content = content.replace(old_single_handler, new_json_handler, 1)
    print("✅ Fix #6: Updated frontend to handle multi-file response")
else:
    print("❌ Frontend handler pattern not found")

# ─── FIX #7: Update the success display section ───
old_success = """      resultStatus.className = 'status-success';
      resultStatus.textContent = '✓ Complete';
      processBtn.disabled = false; processBtn.textContent = 'Upload & Process';
      if (data.redaction_map || data.total_redactions > 0) {
        resultContent.innerHTML = '<div style=\"display:flex;gap:16px;align-items:center;\"><div><strong>' + data.total_redactions + '</strong> redactions</div><div><span style=\"background:rgba(22,163,74,0.1);padding:4px 12px;border-radius:6px;font-size:12px;font-weight:600;color:#16a34a;\">' + (data.redaction_style || 'token') + ' mode</span></div></div>';
        resultContent.innerHTML += '<div style="margin-top:12px;"><a href="' + data.safe_url + '" class="btn btn-ghost" style="font-size:13px;">🔍 View Redacted Document</a></div>';
      } else {
        resultContent.innerHTML = '<div style=\"color:var(--muted);padding:12px;\">No sensitive data detected. Document is safe to share.</div>';
      }
      docCountSpan.textContent = data.total_redactions || 0;"""

new_success = """      resultStatus.textContent = data.total_redactions + ' redactions';
      processBtn.disabled = false; processBtn.textContent = 'Upload & Process';
      resultContent.innerHTML = '<div style="display:flex;gap:16px;align-items:center;"><div><strong>' + data.total_redactions + '</strong> redactions detected</div></div>';
      resultContent.innerHTML += '<div style="margin-top:12px;"><a href="' + data.safe_url + '" class="btn btn-ghost" style="font-size:13px;">🔍 View Redacted Document</a></div>';
      docCountSpan.textContent = data.total_redactions || 0;
      resetFileUI();"""

if old_success in content:
    content = content.replace(old_success, new_success, 1)
    print("✅ Fix #7: Updated success display for current flow")
else:
    print("❌ Success handler pattern not found")

# ─── FIX #8: Add resetFileUI() call after successful processing ───
# Check if resetFileUI is already called
if 'resetFileUI();' in content and 'resultsSection.style.display = 'block'' in content:
    # It seems the new_success already includes resetFileUI()
    print("✅ Fix #8: resetFileUI already included in success handler")
else:
    # Find where we should add it
    old_after_success = """docCountSpan.textContent = data.total_redactions || 0;
    resetFileUI();"""
    if old_after_success in content:
        print("✅ Fix #8: resetFileUI already present")
    else:
        # Add it
        old_doccount = "docCountSpan.textContent = data.total_redactions || 0;"
        new_doccount = "docCountSpan.textContent = data.total_redactions || 0;\n      resetFileUI();"
        if old_doccount in content:
            content = content.replace(old_doccount, new_doccount, 1)
            print("✅ Fix #8: Added resetFileUI() call after processing")

# Save if changes were made
if content != original:
    with open(filepath, 'w') as f:
        f.write(content)
    print("\n✅ All fixes applied and saved to file")
else:
    print("\n❌ No changes were made")
