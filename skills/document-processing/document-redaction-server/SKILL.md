---
name: document-redaction-server
description: Enhance and verify the doc_reader PII redaction server.
category: document-processing
version: "1.0"
author: hermes
license: mit
hermes:
  tags: [redaction, pii, phi, document-processing, local, web-server, ui]
  related_skills: [pdf, ocr-and-documents, web-ui-document-reader]
---

# Document Redaction Server — Enhancement & Operations

## When to Use
Use when the user asks to **enhance, fix, redeploy, restyle, or add categories to the
fully-local OAKAI/Document Reader redaction tool** (`doc_reader_onefile.py`), or to
verify that redaction actually works end-to-end. Also relevant when the user reports a
UI change "didn't take effect" or that redaction silently missed a category.

Core facts (project invariants — confirmed live):
- Single self-contained file `doc_reader_onefile.py` (stdlib only, no pip needed).
- Serves an HTML UI on **port 8765** (bind `0.0.0.0` so the Windows browser can reach
  the WSL2/Docker host — see memory note on container isolation).
- 100% local; no external API. Reversible variable mapping: originals stored ONLY in
  the redaction map, NEVER in the safe output.
- Storage is script-directory-local: when run from `projects/doc_reader/`,
  `DATA_DIR = /opt/data/projects/doc_reader/data/` with
  `documents_safe/<id>_safe.json` and `redaction_maps/<id>_redaction_map.json`.

## Enhancement workflow (do this, in order)
1. **Find the LIVE running directory first.** The running process loads code from
   wherever it was started — NOT from `Samples/`. Confirm with `ls -la` of the project
   dir and `curl -s http://localhost:8765/health`. Edit/deploy there.
2. **Deploy into the live dir, do not just copy to a side folder.** `cp enhanced.py
   /opt/data/projects/doc_reader/doc_reader_onefile.py` then `POST /restart`. Copies
   in `Samples/enhanced_*/` have ZERO effect on the running server.
3. Validate syntax before/after: `python3 -c "import ast;ast.parse(open('doc_reader_onefile.py').read())"`.
4. Redeploy + restart, then re-run the verification probe (below).

## MUST-DO for a real UI "redesign"
- **Rebuild structure, not just colors.** A first pass that only swaps hex values in
  CSS leaves the HTML byte-identical → user reports "display all still looks the same".
  Replace the whole `HTML_UI` string (or the relevant block) with new markup + classes,
  then verify the new class names appear in `curl http://localhost:8765/` and the old
  ones are GONE (use `search_files` for `old_class` and confirm 0 matches).

## Category logic must be DATA-DRIVEN
- **Pitfall:** `redact()` must NOT use a hard-coded `priority_order` list. When new
  categories were added to `SECURITY_POLICY`, a hard-coded list silently excluded them —
  they showed as toggleable in Settings but were never applied. Build the order
  dynamically from `SECURITY_POLICY` group order and append any custom categories. This
  guarantees future-added categories auto-apply.
- Group order matters: PII and BUSINESS_SENSITIVE first, then GOVERNMENT_IDS, FINANCIAL,
  LOCATION_DATA, HEALTH_INFORMATION, CREDENTIALS (later groups should not clobber
  earlier, higher-priority matches).

## Cross-platform self-restart
- The `/restart` endpoint must work WITHOUT Windows. The original only shelled out to
  `restart_helper.vbs` via `wscript.exe`. On POSIX use `os.execv(sys.executable,
  [sys.executable, __file__])` to re-exec the script in place. Keep the VBS path for
  Windows clients; branch on `os.name` / `sys.platform`.

## Smart Dummy mode (value-preserving redaction) — NON-BREAKING / opt-in
The user's core requirement: **keep document labels & structure intact, replace ONLY
the sensitive VALUE with a realistic, format-preserving, deterministic dummy** (e.g.
`account number: 97652345334` → `account number: X0003455334`, `Name: Seow` →
`Name: Abraham`). The real→dummy mapping is stored (reversible). **Token mode
(opaque `{PREFIX_n}`) stays the DEFAULT toggle** so existing behavior is never broken.

Architecture (added in v2):
- `redact(text, style=None)` → 5-tuple `(safe_text, redaction_map, category_counts,
  redactions, real_to_dummy)`. `style="smart"` swaps the value; `style="token"`
  (default) uses opaque tokens. When `style=None` it reads
  `engine.settings["redaction_style"]`.
- `make_dummy(category, dummy_prefix, original, value)` looks up `DUMMY_GENERATORS`
  (per-category fns: `gen_account`, `gen_email`, `gen_phone`, `gen_iban`, `gen_swift`,
  `gen_address`, `gen_cost`, `gen_condition`, `gen_name`, …) and falls back to
  `gen_generic` (returns `REDACTED_xxxx`). Each generator preserves shape/length and
  keeps separators (spaces, slashes, currency symbol, street type).
- **Determinism:** seeded by `random.Random(hashlib.sha256(real_value.encode()).digest())`
  so the SAME real value always maps to the SAME dummy within a run (and across runs,
  since the seed is content-derived, not time-derived). Store `real_to_dummy` in the
  map file; `reverse_map` is its inverse for reversal.
- UI toggle: Settings modal has a **🪄 Smart Dummy Mode** switch that sets
  `currentSettings.redaction_style = 'smart' | 'token'` and POSTs `/settings`.

### 🔴 Regex pitfalls discovered while building Smart Dummy (encode these)
1. **Global `re.IGNORECASE` silently breaks uppercase-only value groups.** Every
   pattern is compiled with `re.IGNORECASE`. A value group like `[A-Z]{6}[A-Z0-9]{2,5}`
   (SWIFT) then ALSO matches lowercase prose → "Diagnosis" was eaten as a SWIFT code,
   "Anderson approved the quotation" as a DIRECTOR_NAME. **Fix: wrap case-sensitive
   value groups in `(?-i:…)`** even though the flag is set globally, e.g.
   `(?P<val>(?-i:[A-Z]{6}[A-Z0-9]{2,5}))`. The label prefix group stays case-insensitive.
2. **Never read the value via `match.group(1)`.** With a `(?P<label>…)(?P<val>…)`
   pattern, group(1) is the LABEL, not the value → the engine replaced the label
   ("Name:") instead of the value. **Always extract via `match.groupdict().get('val')`,
   falling back to `match.group(1)` only when there is exactly one capture group, else
   `match.group()`.** The redact loop computes `vstart/vend` from the same decision.
3. **`\s+` between name/value tokens grabs ACROSS newlines** (because `\s` includes
   `\n`). A bare-name DIRECTOR pattern `Seow Eng Guan\nEmail` over-matched into the next
   line. **Use `[ ]+` (spaces only) for intra-value separators** in name/address/
   condition patterns; keep `\s*[:=#]?` only in the label prefix where a newline won't
   appear.
4. **Settings-closure staleness.** `process_file` originally read the module-level
   `settings` closure, but the `/settings` handler only rebound `engine.settings` to a
   NEW dict → `process_file` kept using the stale (token) settings, so toggling Smart
   Dummy had no effect. **Fix:** read style from `engine.settings` inside `process_file`,
   AND in the `/settings` handler do `globals()["settings"] = new_settings` so the
   closure stays in sync. Also have `load_settings()` backfill new keys
   (`redaction_style: "token"`) so a fresh GET returns a valid default and the UI
   toggle initializes correctly.
5. **Spaced / locale formats must be allowed.** IBAN `GB29 NWBK 6016 …` (spaces),
   `RM 1,250.00` (space after currency), `Jalan/Bukit/Taman` addresses, `MyKad` label
   for IC — add `[ ]?` and extra label aliases so they match AND keep their shape in
   the dummy (the generator must re-insert the original spacing, not just the digits).

## Verification probe (run after every change)
```
# 1. sample with one value per category
printf 'Contact a@b.com call +1-555-123-4567 SSN 123-45-6789 Passport A1234567 IBAN DE89370400440532013000 123 Main St MRN 987654 BTC 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa Quote QTN-2024-0847 $12,500 CEO Mr approved\n' > /tmp/s.txt
# 2. upload
ID=$(curl -s -F "file=@/tmp/s.txt" http://localhost:8765/upload | python3 -c "import sys,json;print(json.load(sys.stdin)['document_id'])")
# 3. assert every expected category fired
curl -s "http://localhost:8765/documents/$ID/safe" | python3 -c "import sys,json;d=json.load(sys.stdin);print('counts',d['category_counts']);assert '{EMAIL_1}' in d['all_text'] and 'a@b.com' not in d['all_text']"
# 4. confirm files on disk
ls -la /opt/data/projects/doc_reader/data/documents_safe/ /opt/data/projects/doc_reader/data/redaction_maps/
```
Assert: (a) `category_counts` includes every enabled group, (b) the safe text contains
`{TOKEN_n}` and NO raw sensitive values, (c) the matching `_redaction_map.json` exists.

## Communicating the result to the user (avoid confusion)
- If you already deployed to the live dir, tell them **ONE action**: hard-refresh the
  browser (Ctrl+Shift+R) at `http://localhost:8765`, then open ⚙️ Settings to see the
  new categories. Do NOT also list multiple "copy from here" paths — it produced
  "i feel more confused now" / "i just need the files that will allow me to test".
- Only mention copy locations if they explicitly keep a separate Windows-side copy; then
  name exactly the 2 files that matter: `doc_reader_onefile.py` (essential) and
  `restart_helper.vbs` (Windows Reset button). Everything else is optional.
- Always state the honest residual: broad added-category regexes may over-match prose
  (e.g. grabbing "CEO Mr" as DIRECTOR_NAME, "approved" as SWIFT). The core PII patterns
  from the original are untouched. Offer to tune per document type.

## Category groups reference
Full table of groups → categories and the verification recipe: see
`references/categories_and_verify.md`.

## Smart Dummy reference
Per-category generator table, label-aware pattern shape, and the live smart-vs-token
verification recipe: see `references/smart_dummy_reference.md`.

## Honesty guard
Never claim "done" on a UI change without confirming the new markup is served
(search_files the live landing page). Never claim a category "works" without the probe above
showing it in `category_counts`. Design ≠ running system until verified on port 8765.
