#!/usr/bin/env python3
"""Diagnose JS syntax error in generated HTML"""
import urllib.request
import re

try:
    req = urllib.request.Request('http://localhost:8765/')
    resp = urllib.request.urlopen(req)
    html = resp.read().decode('utf-8')

    # Extract the script
    script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
    if script_match:
        js = script_match.group(1)
        print(f"Script length: {len(js)} chars")
        
        # Check for obvious syntax errors
        lines = js.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Check for unbalanced quotes
            if "'" in stripped:
                sq_count = stripped.count("'")
                if sq_count % 2 != 0:
                    # Check if it's a string context issue
                    if 'onclick' in stripped or 'toggle(' in stripped or 'function' in stripped:
                        print(f"\n⚠️ Potential quote imbalance on line {i+1}:")
                        print(f"  {stripped[:120]}")
            
            # Check for broken function definitions
            if 'function ' in stripped and not stripped.strip().endswith('{') and '{' not in stripped:
                if i < len(lines) - 1:
                    print(f"\n⚠️ Suspicious function definition on line {i+1}:")
                    print(f"  {stripped[:120]}")
        
        # Check for specific patterns that break JS
        if "toggle('collapsed')" in js:
            # Check if it's inside an onclick HTML attribute (which would break JS)
            # The issue would be if this appears in a JS string that gets put into HTML onclick
            idx = js.find("toggle('collapsed')")
            context = js[max(0,idx-100):idx+50]
            print(f"\nChevron toggle context: {context}")
        
        # Check for the cat-row HTML generation
        idx = js.find('cat-row')
        while idx >= 0:
            before = js[max(0, idx-20):idx]
            if 'rows +=' in before:
                print(f"\n=== cat-row generation around position {idx} ===")
                print(js[idx-50:idx+200])
                break
            idx = js.find('cat-row', idx+1)
        
        # Check for missing semicolons or broken strings in key areas
        # Look for the openSettings function
        idx = js.find('function openSettings()')
        if idx >= 0:
            end = js.find('\n}', idx + 100)
            if end > 0:
                func = js[idx:end]
                # Check for any obvious issues
                if 'rows +=' in func:
                    # Find the rows += line
                    ridx = func.find('rows +=')
                    if ridx >= 0:
                        print(f"\n=== cat-row generation ===")
                        print(func[ridx:ridx+300])
                        
        print("\n✅ JS analysis complete")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
