---
name: local-document-reader-agent
trigger: "When you need to read PDF, Excel, Word, PPT, TXT, and images locally with automatic PII redaction."
description: "Local doc reader with PII redaction."
---

# Local Multi-Format Document Reader Agent

## Trigger
Use when you need to read PDF, CSV, Excel, Word, PowerPoint, RTF, images, or text files entirely locally without external LLM/API.

## Files
- /opt/data/redaction_engine.py — PII/PHI redaction engine
- /opt/data/safe_format.py — Safe output format generator
- /opt/data/doc_reader_desktop.py — PySide6 desktop UI + CLI + HTTP API server

## Venv
/opt/data/.venv-docreader/bin/python3

## Usage
Desktop: python3 /opt/data/doc_reader_desktop.py
CLI: python3 /opt/data/doc_reader_desktop.py --process <file>
API: python3 /opt/data/doc_reader_desktop.py --api-server 8765

## Redaction Categories (10)
1. PII — names, SSN, addresses, phones, emails, biometrics
2. PHI — medical records, insurance, MRNs, mental health
3. Financial — credit cards, bank accounts, loans, investments
4. Credentials — passwords, API keys, certs, MFA tokens
5. Corporate — trade secrets, IP, source code, M&A plans
6. National Security — classified info, ITAR/EAR, defense data
7. Industry Data — student records (FERPA), children's data (COPPA)
8. Infrastructure — internal IPs, network diagrams, firewall configs
9. Behavioral — GPS location, browsing history, shopping habits
10. Composite — user IDs, quasi-identifiers, derived risk scores

## Safe Output Format
to_safe_dict() produces JSON safe for LLM consumption — contains only template variables like {SSN_1}, {PERSON_NAME_1}. Redaction map saved to /opt/data/redaction_maps/<id>_redaction_map.json — NEVER included in agent output.

## Pitfalls
- redaction_engine.py may show "binary file" in read_file — use terminal with sed -n
- spaCy model: /opt/data/.venv-docreader/bin/python3 -m spacy download en_core_web_sm
- NER runs first, then regex — order matters for correct variable assignment
- Pyright false positives for PySide6/spacy — packages are in separate venv