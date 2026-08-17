#!/usr/bin/env python3
"""Fix remaining group-head onclick"""
import re

filepath = '/opt/data/projects/doc_reader/doc_reader_onefile.py'

with open(filepath, 'r') as f:
    content = f.read()

# The pattern in the file uses complex escaping
pattern = r'group-head\\" onclick=\\"this\.parentElement\.classList\.toggle\(\\\\'collapsed\\\\\)\"\">'

if re.search(pattern, content):
    content = re.sub(pattern, r'group-head\\"', content, count=1)
    print("Fixed via regex pattern 1")
else:
    print(f"Pattern 1 not found")
    # Try alternate pattern
    content = re.sub(r'group-head\\" onclick=[^>]*>', 'group-head\\"', content, count=1)
    if 'onclick' not in content[content.find('group-head\\"'):content.find('group-head\\"')+50]:
        print("Fixed via regex pattern 2")
    else:
        print("Pattern 2 also failed")
        # Manual replacement
        idx = content.find('group-head\\" onclick')
        if idx >= 0:
            end = content.find('>', idx)
            old_section = content[idx:end+1]
            new_section = 'group-head\\"'
            content = content.replace(old_section, new_section, 1)
            print(f"Manual replace: '{old_section[:50]}...' -> '{new_section}'")

with open(filepath, 'w') as f:
    f.write(content)

# Verify
with open(filepath, 'r') as f:
    content = f.read()

remaining = re.findall(r'group-head\\" onclick', content)
print(f"Remaining group-head onclick instances: {len(remaining)}")
