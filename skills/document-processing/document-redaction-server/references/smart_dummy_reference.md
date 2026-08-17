# Smart Dummy mode — reference detail

Companion to the Smart Dummy section in SKILL.md. Condensed, for fast reuse.

## What the user asked for (verbatim requirement)
"keep the account number: label, replace only 97652345334 with a logical dummy like
X0003455334; keep RHB Bank untouched; Name: Seow → Name: Abraham; contact:
0102224536 → contact: +700****4499. Mapping real→dummy stored. Make it deterministic
but keep Token as the default toggle."

Decision made: Smart Dummy is OPT-IN; Token stays default. Same real value → same
dummy (seeded by sha256 of the value), so the map is trivially invertible.

## Per-category dummy generators (shape-preserving)
| Category | Generator | Output shape example | Notes |
|---|---|---|---|
| BANK_ACCOUNT | `gen_account` | `97652345334` → `X7945146034` | prefixes soft `X` if short; preserves length |
| SSN | `gen_ssn` | `123-45-6789` → `3-digit-2-4` | keeps dashes |
| EMAIL | `gen_email` | `john@x.com` → `wei.dummy437@example.com` | local part faked, domain forced `example.com` |
| PHONE | `gen_phone` | `0102224536` → `+700****4536` | keeps last 4 of real number |
| CREDIT_CARD | `gen_credit_card` | grouped digits, same group count | — |
| DIRECTOR_NAME | `gen_name` | `Seow Eng Guan` → `Priya Novak` | preserves "Last, First" / "Title First Last" |
| COMPANY_NAME | `gen_company` | fake root + suffix (Sdn Bhd etc.) | — |
| QUOTATION_ID | `gen_quote` | `Q-2024-0145` → `REF-499716` | keeps prefix + 4 digits |
| COST_VALUE | `gen_cost` | `RM 1,250.00` → `RM31199.00` | preserves `$ € £ RM` symbol incl. space |
| MEDICAL_RECORD_NUMBER | `gen_mrn` | `MRN 987654` | — |
| IBAN | `gen_iban` | `GB29 NWBK …` → `GB29 LCQA …` | re-inserts original spacing layout |
| SWIFT | `gen_swift` | `NWBKGB2L` → `CJGD56IH` | 6 letters + 2 digits + 2 letters |
| BITCOIN_ADDRESS | `gen_btc` | `1A1z…` → `1<alpha>` | keeps leading `1` |
| ADDRESS | `gen_address` | `12 Jalan Bukit, Taman Damai, 56000 KL` → `655 Novak Bukit, Taman Damai, 56000 KL` | fakes ONLY house# + road name; keeps street type (Jalan/Bukit/…) + postcode/city tail |
| GPS_COORDINATES | `gen_gps` | jittered coords | — |
| PASSPORT | `A` + 7 digits | `A7999124` | — |
| DRIVER_LICENSE | `D` + 7 digits | — | — |
| TAX_ID | `2 digits - 7 digits` | — | — |
| CONDITION | `gen_condition` | `Type 2 Diabetes` → `Asthma 7 Migraine` | swaps term, preserves digit count + word count |
| USERNAME | `gen_username` | lowercasename + 2 digits | — |
| PASSWORD | `gen_password` | `********` (never echoes fake plaintext) | — |
| API_KEY | `gen_apikey` | `AKIA` + 16 digits | — |

Fallback chain: `DUMMY_GENERATORS.get(category) or .get(dummy_prefix) or gen_generic`
(`gen_generic` → `REDACTED_xxxx`). Wrap generator calls in try/except → `gen_generic`.

## Label-aware pattern shape (critical for structure preservation)
```
(?P<label>(?:account\s*(?:number|no|#)?|acct|mykad|ic(?:\s*/\s*mykad)?)\s*[:=#]?\s*)
(?P<val>\d{6,20})
```
- `label` group is OUTSIDE `val`; redact() keeps `text[match.start():match.val_start]`
  as `label_prefix` and only replaces the `val` span.
- Value group uses `(?-i:…)` to defeat global IGNORECASE on uppercase-only fields.
- Intra-value separators use `[ ]+` (spaces only), NOT `\s+`, to avoid cross-line grabs.

## Live end-to-end verification (smart vs token)
```
BASE=http://127.0.0.1:8765
# set smart
curl -s -X POST $BASE/settings -H 'Content-Type: application/json' \
  -d '{"redaction_style":"smart"}' >/dev/null
ID=$(curl -s -X POST $BASE/process -H 'Content-Type: application/json' \
  -d '{"file_path":"/opt/data/projects/doc_reader/sample_test.txt"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['document_id'])")
curl -s $BASE/documents/$ID/safe | python3 -c "import sys,json;print(json.load(sys.stdin)['all_text'])"
# expect: labels preserved, values replaced (Account Number: X…, Name: …, etc.)
# reset to default token
curl -s -X POST $BASE/settings -H 'Content-Type: application/json' -d '{"redaction_style":"token"}' >/dev/null
```
Assert the safe text contains the dummy values AND still contains the original labels
(`Account Number:`, `Name:`, `IBAN:`, …). Also confirm the map file
`data/redaction_maps/<id>_redaction_map.json` contains `"redaction_style":"smart"`
and a `map` dict of `real -> dummy`.

## Regression guard
A clean document ("Meeting notes: the project is on track…") must produce 0 redactions
in both modes. If it doesn't, a value pattern is over-matching prose — fix with
`(?-i:…)` / `[ ]+` / stricter label gating.
