# re.IGNORECASE + (?-i:...) pitfall (OAKAI doc_reader)

## Symptom
After adding a category, redaction grabs WRONG text with no error:
- A SWIFT/BIC pattern `[A-Z]{6}[A-Z0-9]{2,5}` matched `Diagnosis` (a health word).
- A name pattern `[A-Z][a-z]+` matched `approved` / `Anderson` in prose.
- False positives appear ONLY on capitalized words that are NOT the intended entity.

## Root cause
`doc_reader_onefile.py` compiles every SECURITY_POLICY pattern with `re.IGNORECASE` GLOBALLY:
`re.compile(pattern, re.IGNORECASE)`. The inline `(?i)`/global flag is additive — it does NOT
turn off for `[A-Z]`; it makes `[A-Z]` match BOTH cases. So a "uppercase-only" char class silently
accepts lowercase input too.

## Fix
Wrap the case-sensitive value group in an inline scope override `(?-i:…)`:
```
BEFORE:  r'(?P<val>[A-Z]{6}[A-Z0-9]{2,5})'          # matches "Diagnosis"
AFTER:   r'(?P<val>(?-i:[A-Z]{6}[A-Z0-9]{2,5}))'     # only real SWIFT codes
```
This also affects IBAN, PASSPORT, Bitcoin, title-case names, currency codes (USD/EUR),
and any value group that must be uppercase-only.

## Second trap — \s+ across lines
Inside a value group, `\s+` matches newlines. A name value `Seow Eng Guan` then grabs the next
line (`\nEmail: john@...`). Use `[ ]+` (spaces only) between tokens inside a value group:
```
BEFORE:  (?P<val>(?-i:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*))
AFTER:   (?P<val>(?-i:[A-Z][a-z]+(?:[ ]+[A-Z][a-z]+)*))
```
The LABEL group `(?P<label>...\s*[:=#]?\s*)` may still use `\s` because labels sit on one line.

## Verification recipe
After any pattern change, assert negative guards do NOT match:
- `Apple the fruit is delicious`  → not a product (lowercase model + article)
- `Apple Inc.`                     → company, not product
- `We will price the solution`     → not a cost
- `FY 2024`, `US 12`              → not part numbers / SKUs
- `Reference ABC-1234 was used`    → lone ref, not a part record (needs co-occurring cost)
