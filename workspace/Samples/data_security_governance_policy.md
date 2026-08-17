# Data Security Governance Policy for Document Content Extraction
## Exclusion Categories for AI Agent Processing

### Policy Statement
All content extracted from documents processed by AI agents must be screened against the following categories of confidential/sensitive information. Information matching any category below **MUST NOT** be sent to any LLM, stored in agent memory, or included in agent context without explicit authorization.

---

### Category 1: Personal Identifiable Information (PII)
Information that can identify an individual person.

| Sub-category | Examples | Regulations |
|---|---|---|
| **Direct Identifiers** | Full name, alias, nickname, maiden name, initials combined with context | GDPR, CCPA, PIPEDA |
| **Government IDs** | Social Security Number (SSN), passport number, driver's license, national ID number, tax ID (TIN/EIN) | GDPR, HIPAA, CCPA, GLBA |
| **Contact Information** | Home address, street address, city, state, ZIP, postal code, country; personal phone numbers, mobile numbers, fax numbers; personal email addresses (non-corporate) | GDPR, CCPA |
| **Digital Identifiers** | Username/handle, IP address, MAC address, device ID, advertising ID, cookie ID | GDPR, CCPA, COPPA |
| **Biometric Data** | Fingerprint, face recognition template, iris scan, voiceprint, DNA, genetic data, gait analysis | GDPR, BIPA, CCPA |
| **Date/Place of Birth** | Full date, year, month, day; birth city, hospital name | HIPAA (Safe Harbor), GDPR |
| **Photographic Images** | Any image of an individual's face or identifying features | GDPR, BIPA |

### Category 2: Protected Health Information (PHI)
Health-related information that can identify an individual.

| Sub-category | Examples | Regulations |
|---|---|---|
| **Medical Records** | Medical history, diagnosis, treatment plan, test results, lab reports, imaging results, medication lists, dosages | HIPAA, HITECH |
| **Health Insurance** | Insurance policy number, member ID, group number, coverage details, claims history | HIPAA |
| **Healthcare Identifiers** | Medical Record Number (MRN), Health Plan Beneficiary ID, Account Number, Certificate/License Number, Vehicle Identifier | HIPAA (18 identifiers) |
| **Clinical Trial Data** | Participant IDs, trial enrollment info, adverse event reports, informed consent documents | HIPAA, GDPR |
| **Mental Health** | Psychiatric notes, therapy session notes, mental health diagnosis, treatment for mental conditions | HIPAA (special protection), 42 CFR Part 2 |
| **Substance Abuse** | Addiction treatment records, rehabilitation records | 42 CFR Part 2 |
| **Reproductive Health** | Prenatal care records, fertility treatment, abortion records | HIPAA, state laws |
| **Vital Statistics** | Date and time of death, autopsy reports | HIPAA |
| **Biometric Health** | Blood type, organ transplant info, genetic test results, family medical history | GINA, HIPAA, GDPR |

### Category 3: Financial Information
Data related to financial accounts, transactions, and credit.

| Sub-category | Examples | Regulations |
|---|---|---|
| **Payment Card Data** | Primary Account Number (PAN), Card Verification Value (CVV/CVC), magnetic stripe data, chip data, expiration date | PCI DSS |
| **Banking Information** | Bank account numbers, routing numbers, SWIFT/BIC codes, checkbook details | GLBA, SOX |
| **Credit/Investment** | Credit card numbers, loan numbers, mortgage details, investment account numbers, brokerage info, portfolio holdings | GLBA, FCRA, SOX |
| **Income/Earnings** | Salary amounts, bonus details, tax returns, W-2 forms, 1099 forms, pay stubs | GLBA, IRS |
| **Insurance Data** | Policy numbers, claim numbers, premium amounts, coverage limits, deductible amounts | GLBA |
| **Financial Transaction Details** | Transaction amounts, timestamps, merchant names, account balances, wire transfer details | PCI DSS, GLBA |

### Category 4: Authentication & Access Credentials
Secrets and tokens used to authenticate or authorize access.

| Sub-category | Examples | Regulations |
|---|---|---|
| **Passwords & Secrets** | Plain text passwords, password hashes, API keys, secret keys, OAuth tokens, bearer tokens, JWT tokens | PCI DSS, NIST |
| **Certificates & Keys** | SSL/TLS private keys, SSH keys, PGP private keys, X.509 certificates, digital signatures | PCI DSS, NIST |
| **Multi-factor Auth** | OTP seeds, TOTP secrets, hardware token serial numbers, biometric templates, security questions/answers | NIST, ISO 27001 |
| **Session Identifiers** | Session IDs, session tokens, cookies containing auth state, CSRF tokens | OWASP, PCI DSS |
| **Database Credentials** | Connection strings with embedded passwords, database admin credentials, service account passwords | SOC 2, ISO 27001 |

### Category 5: Corporate & Business Confidential Information
Trade secrets, proprietary data, and internal business information.

| Sub-category | Examples | Regulations |
|---|---|---|
| **Intellectual Property** | Trade secrets, source code, algorithms, patent applications, R&D data, product roadmaps | DTSA, EU Trade Secrets Directive |
| **Business Strategies** | M&A plans, acquisition targets, strategic partnerships, marketing plans, pricing strategies, competitive analysis | SOX, common law |
| **Financial Business Data** | Revenue figures, profit margins, budget allocations, cost structures, forecast data | SOX |
| **Vendor/Partner Information** | Supplier contracts, vendor pricing, partner agreements, channel partner lists, reseller margins | NDA, common law |
| **Internal Communications** | Board meeting minutes, executive communications, internal audit reports, employee disciplinary records | SOX, NLRB |
| **Customer/Partner Lists** | Client lists with contact info, customer databases, partner contact directories | GDPR, trade secret laws |

### Category 6: National Security & Government Information
Classified or sensitive government-related data.

| Sub-category | Examples | Regulations |
|---|---|---|
| **Classified Information** | Confidential, Secret, Top Secret, Restricted, Confidential Financial Information (CFI) | National Security Act, ITAR, EAR |
| **Government Contracts** | Contract numbers, award amounts, contractor performance evaluations, bid proposals | FAR, DFARS |
| **Defense Information** | Export control data, technical data, ITAR/EAR-controlled items, military project details | ITAR, EAR, DFARS 252.204-7012 |
| **Critical Infrastructure** | SCADA system details, utility grid information, nuclear facility data, transportation security | NERC CIP, CFATS, NIST Cybersecurity Framework |
| **Law Enforcement** | Investigation details, arrest records, informant identities, officer safety info, case numbers | CJIS, FOIA exemptions |

### Category 7: Specialized Industry Data
Industry-specific sensitive information.

| Sector | Data Types | Regulations |
|---|---|---|
| **Education** | Student records, transcripts, grades, disciplinary records, financial aid info, parent contact info | FERPA, COPPA, GDPR |
| **Children's Data** | Children's full names, home addresses, parent contact info, school names, grades | COPPA, GDPR (Art. 8) |
| **Legal** | Attorney-client communications, case strategy, settlement amounts, court sealed records, witness lists | Attorney-Client Privilege, ABA Model Rules |
| **Labor/Employment** | Personnel files, salary data, performance reviews, disciplinary actions, union membership | NLRA, NLRB, state wage laws |
| **Real Estate** | Property ownership records, mortgage details, MLS data, appraisal reports, lease agreements | Privacy of Credit (FCRA), state real estate laws |
| **Energy/Utilities** | Grid infrastructure details, energy consumption patterns, smart meter data | NERC CIP, FERC |
| **Agriculture** | Farm subsidy data, crop yields, pesticide application records | USDA privacy, EPA |
| **Transportation** | Driver logs, passenger manifests, GPS tracking data, flight records | HIPAA (transporters), TSA |

### Category 8: Technical Infrastructure & Security
System-level sensitive information that could enable attacks.

| Sub-category | Examples | Regulations |
|---|---|---|
| **Network Information** | Internal IP ranges, subnet layouts, firewall rules, DNS zone files, VLAN configurations | CIS, NIST, ISO 27001 |
| **System Architecture** | Server names, hostnames, container configurations, architecture diagrams with details, backup paths | ISO 27001, SOC 2 |
| **Vulnerability Data** | CVE exploit details, zero-day information, penetration test results, security scan outputs | ISO 27001, SOC 2 |
| **Deployment Details** | Kubernetes manifests with secrets, Docker credentials, deployment scripts with hardcoded values, CI/CD tokens | OWASP, DevSecOps |

### Category 9: Behavioral & Preference Data
Sensitive personal preferences and behavioral patterns.

| Sub-category | Examples | Regulations |
|---|---|---|
| **Location Data** | GPS coordinates, movement patterns, geofence history, travel itineraries, commute routes | GDPR, CCPA, CPRA |
| **Behavioral Profiling** | Shopping habits, browsing history, purchasing predictions, political opinions, religious beliefs | GDPR, CCPA, CDPA |
| **Preference Data** | Dietary restrictions, accessibility needs, health conditions, lifestyle preferences | GDPR, ADA |
| **Inferred Attributes** | Credit scores, risk scores, personality profiles, health risk assessments | FCRA, GDPR, HIPAA |

### Category 10: Composite & Derived Identifiers
Information that may not be directly identifying but can be combined with other data.

| Sub-category | Examples | Regulations |
|---|---|---|
| **Pseudonymous Data** | User IDs, customer numbers, patient IDs, employee IDs, case numbers | GDPR (Recital 26, 28-30) |
| **Quasi-Identifiers** | Zip code + birth date + gender, job title + industry, education level + age range | GDPR, HIPAA |
| **Derived Risk Scores** | Credit risk scores, insurance risk scores, fraud detection scores, security risk scores | FCRA, GDPR |
| **Aggregate Data** (that can be re-identified) | Statistical tables with small cell sizes, geographic aggregates below certain thresholds, temporal patterns | GDPR (data minimization) |

---

## Implementation Rules

1. **Pre-extraction Filter**: Document reader agent must apply PII/PHI detection BEFORE returning content to any LLM. Use pattern matching (regex) for known formats (SSN, credit cards, etc.) and named-entity recognition for names, organizations, and locations.

2. **Content Redaction**: Any detected sensitive data must be redacted (replaced with `[REDACTED]`) before content is passed to the LLM context.

3. **Metadata Isolation**: File metadata (file paths, timestamps, author names in document properties) must be treated as potential PII and processed through the same filter.

4. **No Persistence**: Extracted text from documents must not be persisted to disk, memory, or logs in un-redacted form. Only redacted versions may be cached.

5. **Agent Memory Exclusion**: No PII/PHI/financial/health/legal data may be written to agent memory (`memory` tool) or skills.

6. **Audit Trail**: All redactions should be logged (count only, no actual content) for compliance auditing.

7. **Threshold-based Escalation**: If more than N redactions are detected in a single document (configurable, e.g. >50), the agent should flag the document for manual review rather than processing it.

---

## Compliance Framework Crosswalk

| Framework | Key Requirements Addressed by Above Categories |
|---|---|
| **GDPR** | Categories 1, 2, 9, 10 — personal data, special category data, pseudonymization (Art. 25, 30, 32) |
| **HIPAA** | Category 2 — all 18 PHI identifiers (45 CFR 164.514) |
| **CCPA/CPRA** | Categories 1, 4, 7, 9 — personal information, login credentials, geolocation, inferences |
| **PCI DSS** | Category 3, 4 — cardholder data, authentication credentials (Req 3.2-3.4, 8.2) |
| **GLBA** | Categories 3, 7 — nonpublic personal information (NPPI), financial data |
| **FERPA** | Category 7 — student education records |
| **COPPA** | Category 7 — children's personal information |
| **SOX** | Category 5, 8 — financial controls, internal communications |
| **ITAR/EAR** | Category 6 — defense trade controls |
| **ISO 27001** | All categories — A.8.2.1, A.8.2.2, A.8.2.3 data classification |
| **SOC 2** | Categories 4, 5, 8 — confidentiality, privacy trust principles |
| **NIST CSF** | All categories — ID.AM, DE.CM, PR.DS |
| **PCI DSS** | Categories 3, 4 — cardholder data, authentication |
| **EU AI Act** | All categories — data governance requirements for high-risk AI systems |
