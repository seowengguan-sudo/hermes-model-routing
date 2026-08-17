
# Test that the enhanced document reader has all required components
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Test imports that would be needed
try:
    # Test that we can extract the key components
    with open('doc_reader_onefile.py', 'r') as f:
        content = f.read()
    
    # Verify key components exist
    required_components = [
        'SECURITY_POLICY',
        'EnhancedRedactionEngine', 
        'extract_text',
        'HTML_UI',
        'Handler',
        'main'
    ]
    
    missing = []
    for component in required_components:
        if component not in content:
            missing.append(component)
    
    if missing:
        print(f"❌ Missing components: {missing}")
        sys.exit(1)
    else:
        print("✅ All required components present")
        
    # Verify new category groups are in policy
    new_groups = ['HEALTH_INFORMATION', 'GOVERNMENT_IDS', 'FINANCIAL', 'LOCATION_DATA', 'CREDENTIALS']
    missing_groups = []
    for group in new_groups:
        if group not in content:
            missing_groups.append(group)
            
    if missing_groups:
        print(f"❌ Missing category groups: {missing_groups}")
        sys.exit(1)
    else:
        print("✅ All new category groups present")
        
    # Verify enhanced CSS variables
    css_vars = ['--accent-dark:', '--success-light:', '--warning-light:', '--info-light:']
    missing_css = []
    for var in css_vars:
        if var not in content:
            missing_css.append(var)
            
    if missing_css:
        print(f"❌ Missing CSS variables: {missing_css}")
        sys.exit(1)
    else:
        print("✅ Enhanced CSS variables present")
        
    print("\n🎉 All tests passed! The enhanced document reader is ready.")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    sys.exit(1)
