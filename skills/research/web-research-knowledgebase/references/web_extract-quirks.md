# web_extract behavior quirks (observed in production)

Use when building research-into-knowledge-base pipelines with `web_extract`.

## 1. Truncation + full-text cache
Long pages are truncated in the returned `content` (head + tail shown, total clean
chars reported in the footer). The FULL page is auto-saved to:
`/opt/data/cache/web/<host>-<hash>.md`
For "full extracts" raw archives, `read_file` those cache files instead of
re-fetching. Short pages return full text inline and may not produce a cache file.

## 2. Result-array item drop
When you request 6 URLs in ONE `web_extract` call, the returned `results` array can
silently omit the LAST item (observed: 6th URL absent from a 6-URL batch).
Mitigation: after the batch, assert you received N results; re-extract any missing
URL in a SEPARATE `web_extract` call.

## 3. char_limit
Set per call (e.g. `20000`). Applies per page; larger pages still truncate and cache.
Raise it only if you need more of the head than the default window shows.

## 4. Source quality
Facebook/Instagram and similar embeds often don't extract to useful text — skip them
for depth. Prefer long-form articles, vendor guides, and regulatory pages (SEDA/TNB)
for workflow + pain-point substance.
