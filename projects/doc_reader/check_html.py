#!/usr/bin/env python3
"""Check generated HTML for JS errors"""
import urllib.request

try:
    req = urllib.request.Request('http://localhost:8765/')
    resp = urllib.request.urlopen(req)
    content = resp.read().decode('utf-8')
    
    # Find chevron in generated HTML
    idx = content.find('chev')
    if idx >= 0:
        start = max(0, idx - 200)
        end = min(len(content), idx + 300)
        print("=== Chevron context in generated HTML ===")
        print(content[start:end])
        print()
    
    # Find the group-head line
    idx = content.find('group-head')
    if idx >= 0:
        start = max(0, idx - 50)
        end = min(len(content), idx + 200)
        print("\n=== group-head context ===")
        print(content[start:end])
    
    # Find any obvious JS syntax errors
    if "toggle(`collapsed`)" in content:
        print("Toggle uses backtick - breaks JS")
    elif "toggle('collapsed')" in content:
        print("\n✅ toggle('collapsed') is correct")
    elif 'toggle(\'collapsed\')' in content or 'toggle("collapsed")' in content:
        print("\n✅ toggle uses proper quoting")
    
    # Check for unescaped quotes in onclick
    if "onclick=\"event.stopPropagation();this.parentElement.parentElement.classList.toggle(" in content:
        print("\n✅ Chevron onclick found in generated HTML")
    
except Exception as e:
    print(f"Error: {e}")
