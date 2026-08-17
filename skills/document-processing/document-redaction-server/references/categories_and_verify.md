# doc_reader — Category Groups & Verification Reference

## Storage layout (when run from /opt/data/projects/doc_reader/)
- DATA_DIR        = /opt/data/projects/doc_reader/data/
- DOCS_DIR        = DATA_DIR/documents_safe/      →  <id>_safe.json  (redacted output, NO raw values)
- MAPS_DIR        = DATA_DIR/redaction_maps/      →  <id>_redaction_map.json  (variable→original, never via API)
- SETTINGS_FILE   = DATA_DIR/redaction_settings.json
- Uploads         = DATA_DIR/uploads/

Safe doc JSON keys: document_id, original_filename, total_redactions, category_counts,
all_text (the redacted text with {TOKEN_n}), redaction_summary.
Map JSON keys: map {token: original}, full_map {token: {original,category,group,...}},
category_counts, created_at.

## SECURITY_POLICY groups (7) and their categories
1. PII                 — EMAIL, PHONE, SSN, NAME, IP_ADDRESS, DOB, NATIONAL_ID
2. BUSINESS_SENSITIVE  — QUOTATION_ID, COST_VALUE, DIRECTOR_NAME, CONTRACT_ID,
                         PROJECT_CODE, INTERNAL_NOTE
3. HEALTH_INFORMATION  — MEDICAL_RECORD_NUMBER, DIAGNOSIS, PRESCRIPTION, PATIENT_ID
4. GOVERNMENT_IDS      — PASSPORT, DRIVER_LICENSE, TAX_ID, VISA_NUMBER
5. FINANCIAL           — CREDIT_CARD, IBAN, SWIFT, BANK_ACCOUNT, BITCOIN_ADDRESS
6. LOCATION_DATA       — ADDRESS, GPS_COORDINATES, ZIP_CODE
7. CREDENTIALS         — USERNAME, PASSWORD, API_KEY

Original 2 groups (PII, BUSINESS_SENSITIVE) are preserved; the 5 new groups extend the
data-protection taxonomy for broader filtering in Settings.

## How redaction is applied (data-driven — DO NOT hard-code)
redact() iterates categories in SECURITY_POLICY group order (PII/BUSINESS first),
building the match order dynamically. A hard-coded `priority_order` list was the bug
that made new categories toggleable but never applied. Keep iteration derived from the
policy dict.

## Verification recipe (paste-ready)
```bash
printf 'Contact a@b.com call +1-555-123-4567 SSN 123-45-6789 Passport A1234567 IBAN DE89370400440532013000 123 Main St MRN 987654 BTC 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa Quote QTN-2024-0847 $12,500 CEO Mr approved\n' > /tmp/s.txt
ID=$(curl -s -F "file=@/tmp/s.txt" http://localhost:8765/upload | python3 -c "import sys,json;print(json.load(sys.stdin)['document_id'])")
curl -s "http://localhost:8765/documents/$ID/safe" | python3 -c "import sys,json;d=json.load(sys.stdin);print('counts',d['category_counts'])"
# Expected 12 categories fired in the test sample: EMAIL, PHONE, SSN, PASSPORT, IBAN,
# ADDRESS, MEDICAL_RECORD_NUMBER, BITCOIN_ADDRESS, QUOTATION_ID, COST_VALUE,
# DIRECTOR_NAME, SWIFT.
ls /opt/data/projects/doc_reader/data/documents_safe/ /opt/data/projects/doc_reader/data/redaction_maps/
```

## Cross-platform restart snippet (for /restart endpoint)
```python
import os, sys
if os.name == 'nt':
    subprocess.Popen(['wscript.exe', str(SCRIPT_DIR/'restart_helper.vbs')])
    # then exit current process
else:
    os.execv(sys.executable, [sys.executable, __file__])  # re-exec in place on POSIX
```
