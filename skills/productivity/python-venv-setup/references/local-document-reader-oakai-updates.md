# OAKAI Document Reader — Enhanced Build Notes

## Key Evolution: From Prototype to Production Engine (2026-08-15)

### What Changed
The `doc_reader_onefile.py` evolved from a basic file reader to an **Enterprise
Data Anonymization Engine** with:

1. **10 security categories** across 2 groups (PII + Business Sensitive)
2. **Configurable per-client redaction** via Settings page (API: `/settings`)
3. **Custom category support** — users can add new regex patterns
4. **Portable ZIP** for Windows deployment (no Docker needed)
5. **Professional dark-themed UI** with OAKAI branding

### Architecture
Single-file server (1522 lines) with:
- Settings infrastructure (load/save redaction_settings.json)
- EnhancedRedactionEngine (accepts settings, filters categories)
- File extractors (PDF, DOCX, XLSX, PPTX, TXT, MD, CSV, HTML)
- HTML UI (OAKAI-themed, dark mode, responsive)
- Settings modal (category toggles + custom patterns)
- API server (0.0.0.0:8765) with /health, /, /upload, /documents, /settings

### Redaction Categories
| Group | Category | Dummy Prefix | Critical |
|-------|----------|-------------|----------|
| PII | SSN | {SSN_1} | Yes |
| PII | EMAIL | {EMAIL_1} | Yes |
| PII | PHONE | {PHONE_1} | Yes |
| PII | CREDIT_CARD | {CC_1} | Yes |
| PII | BANK_ACCOUNT | {BANKACC_1} | Yes |
| Business Sensitive | COMPANY_NAME | {COMPANY_1} | Yes |
| Business Sensitive | PRODUCT_NAME | {PROD_1} | Yes |
| Business Sensitive | DIRECTOR_NAME | {DIRECTOR_1} | Yes |
| Business Sensitive | QUOTATION_ID | {QUOTE_1} | Yes |
| Business Sensitive | COST_VALUE | {COST_1} | Yes |

### Known Pitfalls
- **Settings change requires engine rebuild**: POST /settings updates the running
  engine via engine._build_patterns(), but if the engine variable scope is not
  properly captured, a restart is needed.
- **BANK_ACCOUNT regex overlap**: \b\d{10,16}\b is greedy and matches parts of
  other long digit sequences. Set higher priority than generic patterns.
- **Product name regex cross-line matching**: Alternation patterns with \s+
  can match across newlines — anchor carefully.
- **PNG images in vision_analyze**: May return 500 on large PNGs — convert to small
  JPG first (resize + RGB conversion).
- **all_text field in safe doc**: Contains ONLY template variables — the
  redaction_map is NEVER included. This prevents leakage.
- **Windows portability**: The ZIP must self-contain all logic. The data/ dir
  is created locally at first run.
- **Settings file persistence**: Settings saved to data/redaction_settings.json
  survive server restarts. When the server restarts, it loads settings from
  this file at startup.