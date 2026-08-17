#!/usr/bin/env python3
"""Check generated HTML for JS errors"""
import urllib.request
import re

try:
    req = urllib.request.Request('http://localhost:8765/')
    resp = urllib.request.urlopen(req)
    html = resp.read().decode('utf-8')
    
    # Find ALL onclick attributes in HTML to check for issues
    onclick_matches = re.findall(r'onclick="[^"]*"', html)
    print(f"Found {len(onclick_matches)} onclick attributes in HTML")
    
    # Check each for syntax issues
    for onclick in onclick_matches[:5]:
        print(f"\n  onclick: {onclick[:100]}")
        # Check for unescaped quotes
        # Count single quotes
        sq_count = onclick.count("'")
        if sq_count > 0 and sq_count % 2 != 0:
            print(f"    ⚠️ Odd number of single quotes: {sq_count}")
    
    # Extract the inline script
    script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
    if script_match:
        js = script_match.group(1)
        
        # Check for the openSettings function
        if 'function openSettings()' in js:
            print("\n✅ openSettings function found")
        
        # Check for syntax errors by looking at string delimiters
        # Look for the cat-row HTML generation
        if "label>" in js and "label for=" not in js:
            print("✅ Label has no 'for' attribute")
        
        # Check chevron
        if "chev" in js:
            idx = js.find("chev")
            print(f"\nChevron context: ...{js[idx-30:idx+100]}...")
        
        # Check for balanced braces in openSettings
        start = js.find('function openSettings()')
        if start >= 0:
            # Find the end of the function
            depth = 0
            func_start = js.find('{', start)
            for i in range(func_start, min(func_start + 5000, len(js))):
                if js[i] == '{': depth += 1
                elif js[i] == '}': depth -= 1
                if depth == 0:
                    func_body = js[start:i+1]
                    print(f"\nopenSettings function length: {len(func_body)} chars")
                    # Check brace balance
                    opens = func_body.count('{')
                    closes = func_body.count('}')
                    print(f"Brace balance: {opens} open, {closes} close")
                    
                    # Check for any unclosed strings
                    # Count single quotes (not preceded by backslash)
                    sq = len(re.findall(r"(?<!\\)'", func_body))
                    dq = len(re.findall(r'(?<!\\)"', func_body))
                    print(f"Quote balance: {sq} single quotes, {dq} double quotes")
                    
                    if sq % 2 != 0:
                        print("⚠️ Unbalanced single quotes in function!")
                    if dq % 2 != 0:
                        print("⚠️ Unbalanced double quotes in function!")
                    break
        
    print("\n✅ HTML check complete")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
