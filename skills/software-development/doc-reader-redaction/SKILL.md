---
name: doc-reader-redaction
version: 1
author: hermes
license: mit
description: Build/debug the OAKAI local doc redaction POC.
metadata:
  hermes:
    tags: [redaction, pii, doc-reader, oakai, local, single-file]
    related_skills: [pdf, ocr-and-documents]
---

# OAKAI Document Reader (local POC redaction engine)

## When to Use
- User asks to add / fix a redaction CATEGORY or toggle in doc_reader_onefile.py.
- False positives or false negatives in redaction output (over-redacting prose, missing entities).
- Adding a Smart Dummy vs Token mode, deterministic fake-value mapping, or co-occurrence rules.
- Refreshing / deploying / cleaning the running single-file reader (port 8765, Docker host net).
- Debugging the re.IGNORECASE/(?-i:...) regex pitfall or label-aware value capture.

Single-file HTTP server: `doc_reader_onefile.py`. 100% local, no external API. Reversible
redaction map stored in `data/redaction_maps/`. Runs on port 8765 inside a Docker container
with host networking — bind `0.0.0.0`; Windows reaches it via SSH tunnel / browser, NOT a C: mount.

## Project layout (live = true running dir)
- `/opt/data/projects/doc_reader/doc_reader_onefile.py` — the app (self-contained). This is the
  file to deploy and copy to Windows.
- `/opt/data/projects/doc_reader/data/` — live storage: `documents_safe/`, `redaction_maps/`,
  `redaction_settings.json`, `uploads/`.
- Synced copy: `/opt/data/workspace/Samples/enhanced_doc_reader_v2/doc_reader_onefile.py`
  (keep byte-identical via `cmp -s`).
- Build-time patch scripts like `fix_catrow.py` are NOT runtime files and NOT needed — their edits
  are already baked into the main file. Verify with `grep -c` before discarding.

## Core engine model
- Categories live in the `SECURITY_POLICY` dict, grouped under group keys
  (PII, BUSINESS_SENSITIVE, HEALTH_INFORMATION, GOVERNMENT_IDS, FINANCIAL, LOCATION_DATA,
  CREDENTIALS). Each category: `patterns` (named-group regexes), `description`, `dummy_prefix`,
  `critical`.
- `redact(text, style)` drives dynamically from `SECURITY_POLICY`. `style="token"` → opaque
  `{PREFIX_n}`; `style="smart"` → replace ONLY the sensitive value with a realistic dummy
  (labels and document structure preserved).
- Pattern matches MUST name the value group `(?P<val>…)` and optionally a label `(?P<label>…)`
  so labels survive redaction (e.g. `account number: X0003455334` keeps `account number: `).
- `DUMMY_GENERATORS` maps category → generator fn; `make_dummy` dispatches by
  `cat_info["dummy_prefix"]`.

## CRITICAL PITFALL — global re.IGNORECASE breaks uppercase char classes
All SECURITY_POLICY patterns are compiled with `re.IGNORECASE` globally. A value group like
`[A-Z]{6}` (SWIFT) or `[A-Z][a-z]+` (names) then ALSO matches lowercase text → "Diagnosis" gets
eaten by the SWIFT pattern, "approved the quotation" by the name pattern. Silent, confusing false
positives. FIX: wrap case-sensitive value groups in the inline `(?-i:…)` scope override:
  `r'(?P<val>(?-i:[A-Z]{6}[A-Z0-9]{2,5}))'`
Also: never use `\s+` inside a value group that may span lines — use `[ ]+` (spaces only) so a
name value (`Seow Eng Guan`) does not grab the next line (`\nEmail:`). Full reproduction + fix
table in references/regex_ignorecase_pitfall.md.

## Smart Dummy deterministic mapping
Seed = `hashlib.sha256(real_value.encode()).digest()`; `random.Random(seed)` → the SAME real value
always maps to the SAME dummy (reversible via the redaction map file). Preserve format/shape:
- phone → `+700****<last4>` (clean non-digits first)
- cost → keep currency symbol AND a possible space (`RM ` preserved, not `RM`)
- address → keep street-type token (Street/Road/Jalan/…), fake only house no. + road name
- IBAN → keep 2-char country prefix, fake the rest; preserve internal spaces
- product/part → keep Brand+Model shape, swap to a fake brand+model

## Co-occurrence ("married-together") clustering
For entity records whose fields only matter together (e.g. a standard off-the-shelf part:
number + description + cost), add a post-pass in `redact()` BEFORE sorting/processing matches:
- Collect candidate matches of the field categories + `COST_VALUE` (+ `PRODUCT_NAME` matches that
  share a row with an anchor field).
- Union candidates that are on the SAME ROW (no `\n` between them, or ≤60 chars gap).
- Relabel the whole connected cluster as one category when `≥1` part field AND (`≥1` cost OR
  `≥2` part fields).
This prevents a lone `ABC-1234` reference or a standalone `RM 50000` budget from being redacted —
bare fields only redact when co-occurring with a price. That is the "smart" guard against false
positives the user asked for ("pattern of information married together in the file closely or
within same row").

## Workflow preferences (this user)
- Substantial builds: present a DESIGN DIGEST + open questions FIRST; wait for an explicit 'go'
  before coding. State honest tool/UI boundaries; never overclaim.
- "i think good enough for now" = accept current state, defer additions. Stop extending.
- When user says "do not do anything regarding the residuals" / "leave as-is" → respect it; do
  not re-touch those items even if you see further polish possible.
- Bottom-line answer FIRST, then justification (verdict → why → next action).

## CRITICAL BUGS — settings persistence & category toggles (found 2026-08-16)
Two silent bugs broke the Settings UI this session. They PASS at the engine level but FAIL live,
so ALWAYS verify through the HTTP API (see Verification recipe), never only `EnhancedRedactionEngine`
in isolation.

**Bug A — `/settings` POST clobbers the settings file.** The handler did
`save_settings(json.loads(body))` blindly. Any partial POST (e.g. only `{"redaction_style":"smart"}`)
overwrote `redaction_settings.json` to `{"redaction_style":"smart"}` with NO `categories`. Then
`_build_patterns()` built nothing and the Settings modal rendered empty/broken. FIX: merge incoming
over a FRESH `get_default_settings()` (keep the full category tree), validate `redaction_style ∈
{token,smart}`, overlay only `enabled` flags + `custom`. Never overwrite the file with the raw body.
Repair a clobbered file: `save_settings(get_default_settings())`. Symptom that tipped it off: GET
`/settings` returned `categories` once, then the `categories` key vanished after a save.

**Bug B — disabling a category does NOT stop redaction.** `_build_patterns()` only *appends* to
`self.categories` and never clears it, so a category enabled at startup stays active forever even
after the user toggles it off. FIX: at the top of `_build_patterns()` set `self.categories = {}`
before the loop. Verify: disable EMAIL via POST, `/process` a doc containing an email — it must NOT
appear in `category_counts`. Full reproduction + minimal patch in references/settings_persistence_bugs.md.

**Bug C — switch input CSS `display: none` makes toggle switch UNCLICKABLE.** When fixing
the toggle click area (removing label `for` attr) combined with `.switch input { display: none }`,
ALL buttons on the page appear to break because clicking the slider does nothing (the input is
not rendered). This is the **silent root cause** of the "all buttons stopped working" regression.
FIX: use `opacity: 0; width: 100%; height: 100%; z-index: 2;` instead of `display: none`. Full
details in references/ui_interaction_fixes.md.

(See also references/regex_ignorecase_pitfall.md for the regex pitfall.)

**Hard rule after ANY settings change:** the POST handler must (1) call `engine._build_patterns()`
so `self.categories` reflects current enabled flags, and (2) update BOTH `engine.settings` AND the
module-level `settings` closure. `process_file` reads `engine.settings`; if it re-reads from disk via
`load_settings()` it can diverge from the live toggle.

## Safe cleanup of the project dir
- The app depends ONLY on `doc_reader_onefile.py` + `data/`. Everything else is scaffolding or
  session scratch.
- Remove: session test scratch (`*_test.txt`), build-patch scripts whose change is already baked
  in, `/tmp/*.log` test logs.
- ARCHIVE (mv into `_archive_<date>/`), do NOT hard-delete, the user's own scaffolding (.md, .sh,
  portable/ zip) — recoverable if they want it back.
- After cleanup confirm: `/health` 200, main file md5 unchanged, `data/` intact.

## Deploy / restart
- Restart: `pkill -f doc_reader_onefile.py`, then `nohup python3 doc_reader_onefile.py &` (or the
  `/restart` endpoint does `os.execv`). Verify `/health` returns 200.
- Toggle state: the UI Smart Dummy switch POSTs to `/settings` which must update BOTH
  `engine.settings` AND the module-level `settings` closure (or `process_file` reads a stale
  `redaction_style`). Also backfill `redaction_style` in `load_settings` defaults.
- Windows refresh: `docker cp <cid>:/opt/data/projects/doc_reader/doc_reader_onefile.py
  C:\Users\<you>\<project>\` — the container path is NOT reachable from Windows File Explorer.

## Verification recipe (run after ANY pattern change)
Instantiate `EnhancedRedactionEngine(settings=load_settings())`, call
`redact(text, style)` for BOTH `token` and `smart`. Build a positive/negative case table
(e.g. product names, part rows, guard sentences like "we will price the solution next quarter").
Assert `category_counts` — positives should appear, guards should not. Then deploy + curl `/health`.
