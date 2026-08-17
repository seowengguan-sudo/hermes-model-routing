×

×

## Contact Us

Tell us about your stack and the privacy problems you're trying to solve. We typically respond within one business day.

Prefer email? [support@philterd.ai](mailto:support@philterd.ai)

NameEmailMessage

Please do not enter PII or PHI in this form. If you need to share an example, use a sanitized one.

Send Message

We use cookies for analytics and visitor identification to understand how this site is used.
By continuing to browse you accept this use. You can opt out at any time via the
Cookie Settings link in the footer. See our [Privacy Policy](https://philterd.ai/privacy-policy/) for details.

Got itOpt out

Compliance

# Compliance Matrix

Which Philterd products address which regulations: HIPAA, GDPR, PIPEDA, Law 25, CCPA, PCI DSS, GLBA, FERPA, SOX, FedRAMP, and more. For your security review.

- ![HIPAA](https://philterd.ai/badges/hipaa.jpg)
- ![EU GDPR Compliant](https://philterd.ai/badges/gdpr.jpg)
- ![CCPA Compliant](https://philterd.ai/badges/ccpa.png)

This matrix is provided for informational purposes only and does not constitute legal or compliance advice. Consult with your security team and legal counsel to determine whether Philterd's products meet the specific requirements of your regulatory environment. Detection is probabilistic and depends on your data, so validate precision and recall before relying on any policy; because Philterd products are self-hosted, you remain the data controller responsible for the output.

## Regulation coverage

Every Philterd product is self-hosted: your data never leaves your infrastructure. The matrix below maps each regulation to the products and capabilities that address it, including [PHI redaction](https://philterd.ai/phi-redaction/) for HIPAA. For the security posture behind it (threat model, vulnerability disclosure, audit trail, and BAA/DPA stance), see [Security & Trust](https://philterd.ai/security/).

| Regulation | Scope | Products | Key capabilities | Policy |
| --- | --- | --- | --- | --- |
| **HIPAA Safe Harbor**<br>45 CFR 164.514(b)(2) | All 18 PHI identifiers must be removed for data to qualify as de-identified. | [Philter](https://philterd.ai/philter/) [Phileas](https://philterd.ai/phileas/) [PhEye](https://philterd.ai/ph-eye/) [Arbiter](https://philterd.ai/arbiter/) | Detection of PHI identifiers including names, dates, geographic subdivisions, ages over 89, MRNs, and other unique identifiers. Healthcare NLP lens for clinical text. Human review via Arbiter. | Yes |
| **HIPAA Expert Determination**<br>45 CFR 164.514(b)(1) | Qualified statistician certifies re-identification risk is very small. | [Philter](https://philterd.ai/philter/) [Phileas](https://philterd.ai/phileas/) [Philter Diffuse](https://philterd.ai/philter-diffuse/) | Redaction of direct identifiers. Differential privacy for aggregate analytics on residual data. | Configurable |
| **GDPR**<br>EU 2016/679 | Personal data of EU data subjects must be processed lawfully; right to erasure. | [Philter](https://philterd.ai/philter/) [Phileas](https://philterd.ai/phileas/) [Phinder](https://philterd.ai/phinder/) [Philter AI Proxy](https://philterd.ai/philter-ai-proxy/) | PII discovery across data stores (Phinder). Redaction of personal data categories: names, addresses, national IDs, dates of birth, email, phone. Prompt/response redaction for LLM workloads (AI Proxy). | Configurable |
| **PIPEDA**<br>S.C. 2000, c. 5 | Personal information of individuals in Canada collected, used, or disclosed in commercial activities by private-sector organizations. | [Philter](https://philterd.ai/philter/) [Phileas](https://philterd.ai/phileas/) [Phinder](https://philterd.ai/phinder/) [Philter AI Proxy](https://philterd.ai/philter-ai-proxy/) | Redaction of personal information categories: names, SINs, addresses, dates of birth, health information, financial details, contact information. Phinder scans data stores for personal information. Self-hosted deployment keeps data within Canada. | Configurable |
| **Law 25 (Quebec)**<br>An Act respecting the protection of personal information in the private sector | Personal information of Quebec residents; strict data residency requirements and bilingual processing obligations. | [Philter](https://philterd.ai/philter/) [Phileas](https://philterd.ai/phileas/) | Self-hosted deployment satisfies data residency requirements (deploy in a Canadian AWS, Azure, or GCP region). Multilingual redaction handles French and English text with a policy per language. Canadian identifier detection (SIN, provincial health card patterns). | Configurable |
| **CCPA / CPRA**<br>Cal. Civ. Code 1798.100 | California consumers' personal information; right to delete. | [Philter](https://philterd.ai/philter/) [Phileas](https://philterd.ai/phileas/) [Phinder](https://philterd.ai/phinder/) | Same detection and redaction capabilities as GDPR. Phinder scans for personal information across S3, GCS, Azure Blob, and local filesystems. | Configurable |
| **PCI DSS**<br>v4.0, Req 3.2-3.4 | Cardholder data: PAN, CVV, track data. PAN must be rendered unreadable when stored. | [Philter](https://philterd.ai/philter/) [Phileas](https://philterd.ai/phileas/) [Phinder](https://philterd.ai/phinder/) | Credit card number detection with Luhn validation. Masking PAN to last 4 digits (Req 3.4). Full redaction of CVV/CVC (Req 3.2). PII discovery in logs, transcripts, and storage. | Yes |
| **GLBA**<br>Gramm-Leach-Bliley Act | [Nonpublic personal information (NPPI)](https://philterd.ai/guides/what-is-nppi-nonpublic-personal-information/) of financial institution customers. | [Philter](https://philterd.ai/philter/) [Phileas](https://philterd.ai/phileas/) [Phinder](https://philterd.ai/phinder/) | Detection of NPPI: SSNs, account numbers, income data, credit history references. Discovery scanning across document stores. | Configurable |
| **FRBP 9037**<br>Bankruptcy Rule | Court filings must show only last 4 of SSN/taxpayer ID, year of birth, initials of minors, last 4 of financial accounts. | [Philter](https://philterd.ai/philter/) [Phileas](https://philterd.ai/phileas/) [Arbiter](https://philterd.ai/arbiter/) | Last-4 masking for SSNs and account numbers. Year-only date truncation. Initials for minor names. Attorney QC review via Arbiter. | Yes |
| **FRCP 5.2**<br>Federal Civil Procedure | Same redaction requirements as FRBP 9037, applied to all federal civil and criminal filings. | [Philter](https://philterd.ai/philter/) [Phileas](https://philterd.ai/phileas/) [Arbiter](https://philterd.ai/arbiter/) | Same capabilities as FRBP 9037. Applies to electronically filed documents in all federal courts. | Yes |
| **FERPA**<br>20 U.S.C. 1232g | Student education records: names, IDs, grades, disciplinary records. | [Philter](https://philterd.ai/philter/) [Phileas](https://philterd.ai/phileas/) | Detection of student names, student IDs, dates of birth, addresses, and education-record-specific identifiers. | Configurable |
| **SOX**<br>Sarbanes-Oxley Act, Section 802 | Financial records and audit trails must be preserved but sensitive data must be controlled. | [Philter](https://philterd.ai/philter/) [Phileas](https://philterd.ai/phileas/) [Phield](https://philterd.ai/phield/) | Redaction of PII in financial documents. Phield monitors PII trends across financial data pipelines to detect anomalous flows. | Configurable |
| **FedRAMP**<br>NIST 800-53 | Cloud services used by federal agencies must meet NIST 800-53 controls. | [Philter](https://philterd.ai/philter/) | Deployable in FedRAMP-authorized environments: AWS GovCloud, Azure Government, Google Distributed Cloud Hosted. Self-hosted with no outbound dependencies. | N/A |
| **CMMC**<br>Cybersecurity Maturity Model | Defense contractors must protect Controlled Unclassified Information (CUI). | [Philter](https://philterd.ai/philter/) | Air-gapped deployment. No external API calls. Self-contained Docker images. | N/A |
| **ITAR**<br>International Traffic in Arms | Technical data related to defense articles must be controlled. | [Philter](https://philterd.ai/philter/) | Air-gapped deployment in classified environments. No data leaves the perimeter. | N/A |

## Product capabilities by compliance function

| Function | Product | What it does |
| --- | --- | --- |
| **Detect PII in text** | [Philter](https://philterd.ai/philter/) [Phileas](https://philterd.ai/phileas/) | 30+ entity types. Pattern-based detection (regex, checksums, format validators) plus NLP-based detection via PhEye lenses. |
| **Redact / mask / encrypt** | [Philter](https://philterd.ai/philter/) [Phileas](https://philterd.ai/phileas/) | Multiple strategies per entity type: full redaction, masking to last N characters, year-only date truncation, initials, format-preserving encryption, synthetic value replacement. |
| **Discover PII across data stores** | [Phinder](https://philterd.ai/phinder/) | Crawls S3, GCS, Azure Blob, and local filesystems. Reports entity types and counts per file or object. |
| **Monitor PII trends** | [Phield](https://philterd.ai/phield/) | Receives PII type counts via API or Kafka. Stores in MongoDB time-series or in-memory. Alerts via PagerDuty or Slack when counts deviate from established trends. |
| **Human review of automated redactions** | [Arbiter](https://philterd.ai/arbiter/) | Accept, override, or exempt each detection. Structured exemption codes. Per-reviewer throughput and audit reporting. |
| **Benchmark redaction accuracy** | [Philter Scope](https://philterd.ai/philter-scope/) | Precision, recall, F1 per entity type against gold-standard test data. Entity type confusion matrix. CI/CD integration for regression detection. |
| **Differentially private analytics** | [Philter Diffuse](https://philterd.ai/philter-diffuse/) | Formal epsilon-budget differential privacy for aggregate queries (counts, sums, averages) on PII telemetry. Membership-inference resistant. |
| **Redact PII from LLM prompts** | [Philter AI Proxy](https://philterd.ai/philter-ai-proxy/) | Drop-in proxy for OpenAI, Anthropic, Gemini, and Ollama. Redacts PII from prompts before the model sees them. |
| **Build and edit redaction policies** | [Redaction Policy Editor](https://philterd.ai/redaction-policy-editor/) | Visual, no-code policy builder. Exports valid Philter-compatible policies. |

## Deployment models

All Philterd products are self-hosted. Your data stays in your infrastructure.

| Deployment | Products supported | Notes |
| --- | --- | --- |
| **Cloud VPC (AWS, GCP, Azure)** | All | Standard deployment. Cloud marketplace listings available for Philter. |
| **AWS GovCloud / Azure Government** | Philter | FedRAMP Moderate and High. |
| **Air-gapped / disconnected** | Philter | Self-contained Docker images. No outbound network required. |
| **On-premises** | All | Docker or bare-metal. No SaaS dependency. |

## Pre-built redaction policies

Ready-to-use policy files for common regulations. Available in the [policy library](https://philterd.ai/policies/) and on [GitHub](https://github.com/philterd/pii-redaction-policies).

| Policy | Regulation | What it covers |
| --- | --- | --- |
| **HIPAA Safe Harbor** | HIPAA 45 CFR 164.514(b)(2) | Targets all 18 Safe Harbor identifier categories, each with an appropriate redaction strategy. |
| **PCI DSS Scope Reduction** | PCI DSS Req 3.2-3.4 | PAN masking to last 4, full CVV/CVC redaction. |
| **Rule 9037 Bankruptcy** | FRBP 9037 | SSN/taxpayer ID to last 4, dates to year only, minor names to initials, financial accounts to last 4. |
| **General Purpose** | Multiple | Broad entity detection for names, SSNs, credit cards, dates, addresses, phone numbers, emails. |
| **LLM Training Data** | AI/ML governance | Aggressive PII stripping for training-corpus preparation. |
| **Clinical Notes for Research** | HIPAA | Optimized for narrative clinical text with healthcare NLP lens. |

Community-contributed policies are welcome via [pull request](https://github.com/philterd/pii-redaction-policies/blob/main/CONTRIBUTING.md).