# Data Security Governance Policy — Exclusion Categories for Document Readers

## 10 Categories agents MUST NOT receive in any extracted document content

1. **PII** — names, SSN, addresses, phones, emails, biometrics, DOB
2. **PHI** — medical records, diagnoses, treatments, insurance, MRNs, mental health
3. **Financial** — credit cards (PAN/CV2), bank accounts, loans, investments, tax returns
4. **Credentials** — passwords, API keys, certs, MFA tokens, session IDs
5. **Corporate** — trade secrets, IP, source code, M&A plans, vendor contracts
6. **National Security** — classified info, ITAR/EAR, defense data
7. **Industry Data** — student records (FERPA), children's data (COPPA), legal privileged
8. **Infrastructure** — internal IPs, network diagrams, firewall configs, vuln data
9. **Behavioral** — GPS location, browsing history, shopping habits, political opinions
10. **Composite** — user IDs, quasi-identifiers, derived risk scores, re-identifiable aggregates

## Implementation in local-document-reader-agent
The RedactionEngine replaces all matching data with template variables:
- `{SSN_1}`, `{CREDIT_CARD_1}`, `{EMAIL_1}`, `{PERSON_NAME_1}`, `{API_KEY_1}`, etc.
- Redaction map saved to `/opt/data/redaction_maps/<doc_id>_redaction_map.json` (LOCAL ONLY)
- Safe JSON sent to agents contains ONLY variables, never originals

## Compliance Frameworks Covered
GDPR, HIPAA, CCPA, PCI DSS, GLBA, FERPA, COPPA, SOX, ITAR, ISO 27001, SOC 2, NIST, EU AI Act

## Full Policy
See `/opt/data/knowledge/data_security_governance_policy.md` (12.6KB, full crosswalk)