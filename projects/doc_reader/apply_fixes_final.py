#!/usr/bin/env python3
"""Apply UI fixes to doc_reader_onefile.py - safe mode"""
import re

filepath = '/opt/data/projects/doc_reader/doc_reader_onefile.py'

with open(filepath, 'r') as f:
    content = f.read()

original = content
fixes = []

# ─── FIX #1 & #2: Label for attribute and group-head onclick ───
# These are embedded in HTML strings within JavaScript
# Pattern 1: Remove for attribute from label
content = content.replace("label for=\"cb_' + catKey + '\">", "label>", 1)
fixes.append("Fix #1: Removed 'for' from label")

# Pattern 2: Remove onclick from group-head
# The escaped form in the file
gh_pattern = r'group-head\\" onclick=\\"this\.parentElement\.classList\.toggle\(\\'"collapsed\\'\\)\\"'
content = re.sub(gh_pattern, 'group-head"', content, count=1)
fixes.append("Fix #2: Removed onclick from group-head")

# Pattern 3: Fix chevron backtick escaping
content = content.replace(
    "classList.toggle(`collapsed`)",
    "classList.toggle('collapsed')",
    1
)
fixes.append("Fix #2b: Fixed chevron backtick escaping")

# ─── FIX #3: mini-btn CSS enhancement ───
old_css = '.mini-btn { padding: 10px 16px; border-radius: 10px; border: 1px solid var(--border-2); background: var(--surface-2); font-size: 14px; font-weight: 600; cursor: pointer; color: var(--primary); min-width: 52px; text-align: center; transition: all .2s; } .mini-btn:hover { background: var(--accent); color: #fff; }'
# Check what's currently there
minibtns = re.findall(r'\.mini-btn\s*\{[^}]*\}', content)
for css in minibtns:
    print(f"Current mini-btn CSS: {css[:80]}...")

# ─── FIX #4: Multi-file upload ───
# 4a: selectedFile → selectedFiles
content = content.replace("let selectedFile = null;", "let selectedFiles = [];", 1)
fixes.append("Fix #4a: selectedFiles array")

# 4b-d: Update all references to selectedFile in JS
content = content.replace("selectedFile = files[0];", "selectedFiles = Array.from(files);", 1)
fixes.append("Fix #4b: File selection handler")

# 4c: Filename display
content = content.replace(
    "? selectedFile.name + ' (' + Math.round(selectedFile.size/1024) + ' KB)'\n      : files.length + ' files selected';",
    "? selectedFiles[0].name + ' (' + Math.round(selectedFiles[0].size/1024) + ' KB)'\n      : files.length + ' files selected (' + Math.round(Array.from(files).reduce(function(a,f){return a+f.size},0)/1024) + ' KB total)';",
    1
)
fixes.append("Fix #4c: Multi-file filename display")

content = content.replace(
    "processBtn.disabled = true; processBtn.textContent = 'Upload & Process'; selectedFile = null;",
    "processBtn.disabled = true; processBtn.textContent = 'Upload & Process'; selectedFiles = [];",
    1
)
fixes.append("Fix #4d: resetFileUI update")

content = content.replace("if (!selectedFile) return;", "if (selectedFiles.length === 0) return;", 1)
fixes.append("Fix #4e: Process check")

content = content.replace("formData.append('file', selectedFile);", 
    "for (let i = 0; i < selectedFiles.length; i++) {\n      formData.append('file', selectedFiles[i]);\n    }", 1)
fixes.append("Fix #4f: formData loop")

# 4g-i: Drag-drop handler
content = content.replace("selectedFile = e.dataTransfer.files[0];", "selectedFiles = Array.from(e.dataTransfer.files);", 1)
fixes.append("Fix #4g: Drop handler")

old_drop_fn = "fileNameDiv.textContent = selectedFile.name + ' (' + Math.round(selectedFile.size/1024) + ' KB)';"
new_drop_fn = """fileNameDiv.textContent = selectedFiles.length === 1
      ? selectedFiles[0].name + ' (' + Math.round(selectedFiles[0].size/1024) + ' KB)'
      : selectedFiles.length + ' files selected (' + Math.round(selectedFiles.reduce(function(a,f){return a+f.size},0)/1024) + ' KB total)';"""
content = content.replace(old_drop_fn, new_drop_fn, 1)
fixes.append("Fix #4h: Drop filename display")

content = content.replace(
    "processBtn.disabled = false; processBtn.textContent = 'Process ' + e.dataTransfer.files.length + ' file(s)';\n    if (e.dataTransfer.files.length === 1) setTimeout(() => processBtn.click(), 100);",
    "processBtn.disabled = false; processBtn.textContent = 'Process ' + selectedFiles.length + ' file(s)';\n    if (selectedFiles.length === 1) setTimeout(() => processBtn.click(), 100);",
    1
)
fixes.append("Fix #4i: Drop button text")

# ─── FIX #5: Backend multi-file support ───
# Add results array before the for loop
old_loop = "                for part in parts:\n                    if b\"filename=" in part:"
new_loop = "                results = []\n                for part in parts:\n                    if b\"filename=" in part:"
content = content.replace(old_loop, new_loop, 1)
fixes.append("Fix #5a: Added results array")

# Change return to append
old_ret = '"map_path": map_path\n                            })\n                            return'
new_ret = '"map_path": map_path\n                            })'
content = content.replace(old_ret, new_ret, 1)
fixes.append("Fix #5b: Changed return to append")

# Change self._json(200, to results.append({
old_json = '                            self._json(200, {\n                                "document_id": safe_doc["document_id"],\n                                "safe_url": f"/documents/{safe_doc[\'document_id\']}/safe",\n                                "original_filename": filename,\n                                "total_redactions": safe_doc["total_redactions"],\n                                "category_counts": safe_doc["category_counts"],\n                                "file_path": saved_path,\n                                "safe_path": safe_path,\n                                "map_path": map_path\n                            })'
new_append = '                            results.append({\n                                "document_id": safe_doc["document_id"],\n                                "safe_url": f"/documents/{safe_doc[\'document_id\']}/safe",\n                                "original_filename": filename,\n                                "total_redactions": safe_doc["total_redactions"],\n                                "category_counts": safe_doc["category_counts"],\n                                "file_path": saved_path,\n                                "safe_path": safe_path,\n                                "map_path": map_path\n                            })'
if old_json in content:
    content = content.replace(old_json, new_append, 1)
    fixes.append("Fix #5c: Changed self._json to results.append")

# Add multi-file response handler
old_no_file = "                self._json(400, {\"error\": \"No file uploaded\"})"
new_no_file = """                if results:
                    self._json(200, {
                        "documents": results,
                        "total_documents": len(results)
                    })
                else:
                    self._json(400, {"error": "No file uploaded"})"""
content = content.replace(old_no_file, new_no_file, 1)
fixes.append("Fix #5d: Multi-file response")

# ─── FIX #6: Frontend multi-file handler ───
if "data.documents" not in content:
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
        Object.entries(doc.category_counts || {}).forEach(([cat, count]) => {
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
      resultTitle.textContent = data.original_filename || 'Document Processed';
      resultStatus.className = 'status-badge status-success';
      resultStatus.textContent = '✓ Complete';"""
    
    if old_handler in content:
        content = content.replace(old_handler, new_handler, 1)
        fixes.append("Fix #6: Multi-file frontend response handler")
    else:
        print("Fix #6: Handler pattern not found")

# Add resetFileUI() call after successful single-file processing
if "resetFileUI();" not in content.split("resultsSection.style.display = 'block';")[1][:500] if "resultsSection.style.display = 'block';" in content else "":
    # Find the single-file success block and add resetFileUI
    old_success_block = """processBtn.disabled = false; processBtn.textContent = 'Upload & Process';
      if (data.redaction_map"""
    new_success_block = """processBtn.disabled = false; processBtn.textContent = 'Upload & Process';
      resetFileUI();
      if (data.redaction_map"""
    if old_success_block in content:
        content = content.replace(old_success_block, new_success_block, 1)
        fixes.append("Fix #7: Added resetFileUI after processing")

# Save
if content != original:
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"\n✅ {len(fixes)} fixes applied:")
    for fix in fixes:
        print(f"  {fix}")
else:
    print("\n⚠️ No changes made")

print(f"\nFinal file size: {len(content):,} bytes")
