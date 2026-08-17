# Settings persistence & category-toggle bugs (doc_reader_onefile.py)

Captured 2026-08-16 from a session where the Settings UI appeared broken after
adding Smart Dummy + STANDARD_PART. Both bugs passed at engine level but failed live.

## Bug A — `/settings` POST clobbers the settings file

**Symptom:** GET `/settings` returned `{"categories":…}` once, then the `categories`
key vanished after a save. Settings modal rendered empty / save looked like it
reverted. Root cause: POST handler did `save_settings(json.loads(body))` — a partial
POST (e.g. `{"redaction_style":"smart"}`) overwrote `redaction_settings.json` to
`{"redaction_style":"smart"}` with NO `categories`.

**Minimal fix (POST handler):**
```python
incoming = json.loads(body)
defaults = get_default_settings()
merged = defaults                      # fresh full category tree, never clobbered
if isinstance(incoming, dict):
    if incoming.get("redaction_style") in ("token", "smart"):
        merged["redaction_style"] = incoming["redaction_style"]
    inc_cats = incoming.get("categories", {})
    if isinstance(inc_cats, dict):
        for g, gd in inc_cats.items():
            if g not in merged["categories"]:
                merged["categories"][g] = {"enabled": True, "subcategories": {}}
            if isinstance(gd, dict):
                if "enabled" in gd: merged["categories"][g]["enabled"] = bool(gd["enabled"])
                for ck, cv in gd.get("subcategories", {}).items():
                    if ck in merged["categories"][g]["subcategories"] and isinstance(cv, dict):
                        if "enabled" in cv: merged["categories"][g]["subcategories"][ck]["enabled"] = bool(cv["enabled"])
if isinstance(incoming.get("custom"), list):
    merged["custom"] = incoming["custom"]
save_settings(merged)
engine.settings = merged; globals()["settings"] = merged
engine._build_patterns()
```

**Repair a clobbered file:** `save_settings(get_default_settings())` then confirm
`GET /settings` shows 7 groups / 25 subcats.

## Bug B — disabling a category does not stop redaction

**Symptom:** toggle EMAIL off → upload a doc with an email → still redacted.
Root cause: `_build_patterns()` only appends to `self.categories`, never resets it,
so a category built at startup stays active forever.

**Minimal fix:** at the very top of `_build_patterns(self)`:
```python
self.categories = {}   # reset fully so disabled categories are removed
```

## Verification discipline (why these slipped through)
- Engine-level `EnhancedRedactionEngine(settings=…).redact(...)` does NOT reproduce these:
  Bug A is about the HTTP handler / on-disk file; Bug B depends on whether the engine
  was (re)built BEFORE the disable (a fresh engine disables correctly).
- ALWAYS verify through the live API after a settings change:
  1. partial POST `{"redaction_style":"smart"}` → GET `/settings` must still show `categories`.
  2. disable EMAIL via POST → POST `/process` a doc with an email → `category_counts`
     must NOT contain EMAIL; re-enable → must contain it.
- curl usage: `curl -s -X POST localhost:8765/settings -H 'Content-Type: application/json'
  -d '{"redaction_style":"smart"}'`. Python urllib: `urllib.request.Request(..., method="POST")`.
