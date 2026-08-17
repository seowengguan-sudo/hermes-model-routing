#!/usr/bin/env python3
"""Fix #1: Label for attribute"""
filepath = '/opt/data/projects/doc_reader/doc_reader_onefile.py'
with open(filepath, 'r') as f:
    content = f.read()

old = 'label for="cb_' 
new = 'label>'
# Replace in the HTML generation context
content = content.replace("label for=\"cb_' + catKey + '\\\">", "label>", 1)
with open(filepath, 'w') as f:
    f.write(content)
print("Done")
