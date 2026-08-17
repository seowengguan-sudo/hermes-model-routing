# Enhancement Patterns for Extensible Document Processing Systems

This document captures patterns and techniques for enhancing document processing systems with extensible security/category policies, based on the OAKAI Document Reader enhancement.

## Pattern 1: Extensible Security Policy Structure

```
SECURITY_POLICY = {
    "CATEGORY_GROUP_NAME": {
        "CATEGORY_KEY": {
            "patterns": [regex_patterns...],
            "description": "Human readable description",
            "dummy_prefix": "PREFIX_FOR_VARIABLES",
            "critical": boolean
        }
    }
}
```

### Best Practices:
- Group related categories under logical group names (PII, FINANCIAL, HEALTH_INFORMATION, etc.)
- Each category should have clear regex patterns for detection
- Use meaningful dummy prefixes for redaction variables (SSN_, EMAIL_, MRN_, etc.)
- Mark critical categories for heightened protection awareness

## Pattern 2: UI Settings Mapping

In the settings UI, map policy groups to user-friendly labels:

```javascript
const groupLabel = groupName === 'PII' ? 'PII / Sensitive' : 
                   groupName === 'BUSINESS_SENSITIVE' ? 'Business Sensitive' :
                   groupName === 'HEALTH_INFORMATION' ? 'Health Information' :
                   groupName === 'GOVERNMENT_IDS' ? 'Government IDs' :
                   groupName === 'FINANCIAL' ? 'Financial Data' :
                   groupName === 'LOCATION_DATA' ? 'Location Data' :
                   groupName === 'CREDENTIALS' ? 'Credentials' : groupName;
```

And map categories to badge types for visual categorization:

```javascript
const categoryGroups = {
    'PII': ['SSN', 'EMAIL', 'PHONE', 'CREDIT_CARD', 'BANK_ACCOUNT'],
    'BUSINESS': ['PRODUCT_NAME', 'COMPANY_NAME', 'DIRECTOR_NAME', 'QUOTATION_ID'],
    'FINANCIAL': ['COST_VALUE', 'IBAN', 'SWIFT', 'BITCOIN_ADDRESS'],
    'HEALTH': ['MEDICAL_RECORD_NUMBER', 'HEALTH_PLAN_BENEFICIARY', 'CONDITION'],
    'GOVERNMENT': ['PASSPORT', 'DRIVER_LICENSE', 'TAX_ID'],
    'LOCATION': ['ADDRESS', 'GPS_COORDINATES'],
    'CREDENTIALS': ['USERNAME', 'PASSWORD', 'API_KEY']
};
```

## Pattern 3: Processing Logic Updates

Ensure JavaScript processing logic accounts for new categories:

1. Update `categoryGroups` definition in processing scripts
2. Update badge assignment logic to match new categories
3. Ensure priority ordering in redaction processing considers new categories if needed
4. Update any category-specific validation or formatting logic

## Pattern 4: Verification and Testing

Create automated tests to validate enhancements:

```python
def test_policy_structure():
    """Verify that enhanced policy contains expected category groups"""
    assert 'HEALTH_INFORMATION' in SECURITY_POLICY
    assert 'GOVERNMENT_IDS' in SECURITY_POLICY
    assert len(SECURITY_POLICY['FINANCIAL']) >= 3  # Expanded from original
    
def test_component_presence():
    """Verify all required components are present in the enhanced system"""
    required = ['SECURITY_POLICY', 'EnhancedRedactionEngine', 'extract_text', 'HTML_UI']
    for component in required:
        assert component in file_content
        
def test_css_enhancements():
    """Verify enhanced CSS variables are present"""
    css_vars = ['--accent-dark:', '--success-light:', '--warning-light:', '--info-light:']
    for var in css_vars:
        assert var in file_content
```

## Pattern 5: Backward Compatibility Maintenance

When extending existing systems:
- Preserve all original category definitions and functionality
- Ensure new additions don't break existing processing flows
- Maintain UI compatibility - new settings should integrate seamlessly
- Keep variable naming conventions consistent
- Preserve all original file format support and processing logic

## Implementation Example: OAKAI Document Reader Enhancement

See `/opt/data/workspace/Samples/enhanced_doc_reader_v2/doc_reader_onefile.py` for a complete implementation showing:
- Expanded SECURITY_POLICY with 6 new category groups
- Enhanced CSS variables for professional UI
- Updated JavaScript categoryGroups and groupLabel mappings
- Preserved all original functionality (100% local processing, reversible mapping, etc.)
- Added verification scripts and documentation

## Key Takeaways

1. **Extensibility by Design**: Structure policies to make adding new categories straightforward
2. **UI Consistency**: Ensure settings and processing logic stay synchronized with policy changes
3. **Verification First**: Implement tests to catch structural issues early
4. **Backward Compatibility**: Never break existing functionality when extending
5. **Documentation Patterns**: Clearly document extension points for future maintainers