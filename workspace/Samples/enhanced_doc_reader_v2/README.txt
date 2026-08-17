# OAKAI Document Reader - Enhanced Enterprise Edition

## Overview
Enhanced version of the OAKAI Document Reader with expanded data protection categories and improved user interface.

## New Features

### Expanded Security Categories
The enhanced version includes 6 additional category groups for comprehensive data protection:

1. **HEALTH_INFORMATION**
   - Medical Record Numbers (MRN)
   - Health Plan Beneficiary Numbers
   - Medical Conditions

2. **GOVERNMENT_IDS**
   - Passport Numbers
   - Driver License Numbers
   - Tax Identification Numbers (TIN/EIN)

3. **FINANCIAL** (Expanded)
   - IBAN (International Bank Account Number)
   - SWIFT/BIC Codes
   - Bitcoin Addresses

4. **LOCATION_DATA**
   - Street Addresses
   - GPS Coordinates

5. **CREDENTIALS**
   - Usernames
   - Passwords
   - API Keys

### Enhanced User Interface
- Professional color scheme with improved contrast
- Better visual hierarchy and spacing
- Enhanced hover states and feedback
- Improved settings organization with category grouping
- More intuitive badge styling for different data types

### Improved Processing Logic
- Updated category mapping for accurate redaction labeling
- Enhanced JavaScript handling for new categories
- Better group labeling in settings interface

## Files Included
- `doc_reader_onefile.py` - Main application (all-in-one enhanced version)
- `run.sh` - Linux/macOS/WSL2 launch script
- `run.bat` - Windows launch script (shows console)
- `start_silent.vbs` - Silent Windows launch (no console window)
- `README.txt` - This file
- `test_policy.py` - Verification test for policy structure

## Quick Start
1. Extract all files to a folder (e.g., `C:\oakai_document_reader_enhanced\`)
2. Double-click `start_silent.vbs` (Windows) or run `./run.sh` (Linux/macOS/WSL2)
3. Open your browser to `http://localhost:8765`
4. Drag & drop files or click to select documents for processing

## Features
- ✅ 100% local processing - no external API calls
- ✅ Reversible variable mapping for data reconstruction
- ✅ Support for PDF, Word, Excel, PowerPoint, TXT, CSV, HTML, JSON, MD
- ✅ Live settings updates with instant application
- ✅ Self-contained data storage (no paths outside script directory)
- ✅ Automatic restart for seamless updates
- ✅ Comprehensive audit trails stored locally

## Data Categories
All originally supported categories remain active:
- **PII**: SSN, Email, Phone, Credit Card, Bank Account
- **Business Sensitive**: Company Name, Product Name, Director Name, Quotation ID, Cost Value

Plus all new categories listed above.

## Custom Categories
Users can still add custom regex patterns for specialized data types through the Settings interface.

## License
For internal use and evaluation. Contact OAKAI for commercial licensing.
