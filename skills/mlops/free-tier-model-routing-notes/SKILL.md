---
name: free-tier-model-routing-notes
description: "Free-tier routing addendum: validated PDF-codegen failure."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [hermes, models, free-tier, routing]
---

# Free-Tier Model Routing — Session Addendum

ADDENDUM to `mlops/free-tier-model-routing` (global store, unpatched from this
profile). Merge into that skill when writable.

## Tested finding: free-tier models FAIL at PDF-code generation
During a session building a PDF architecture doc, the active free models were asked
to author a from-scratch PDF generator. Verified results:
- `openrouter/nvidia/nemotron-3-super-120b-a12b:free`: returned prose describing the
  script (e.g. "class PDF with methods: text(x,y,s...)") instead of runnable code,
  across 5 attempts despite strict "code only, first line import os" instructions.
- `nvidia/meta/llama-3.1-8b-instruct` (top score 9.83/10): real-looking code but broken
  PDF operators — `text()` used `Td` without `BT`/`ET`, `fillrect` wrong `re f` order;
  also truncated mid-string at low `max_tokens`.

**Conclusion:** do NOT delegate PDF generation to the active free model. Import and
run the verified `productivity/pdf-from-stdlib` `scripts/pdf_writer.py` directly —
hand it the content, never the code-generation task.

## Provider-block diagnosis correction (supersedes earlier "sandbox egress" framing)
Earlier notes implied Groq/Cerebras/HF/Nous were "blocked from the sandbox." Refined
diagnosis (see `free-tier-model-routing` → references/live-verification.md):
- Groq + Cerebras 403 = **Cloudflare error 1010 (ASN ban)** on egress IP 161.142.137.99
  (AS9930 TTNET, Penang, MY). Removing Docker does NOT help — same ASN in/out of container.
- HuggingFace = DNS-allowlist quirk on the `/models/<id>` subdomain, not a hard block.
- Nous = expired cached OAuth token on direct API; works through Hermes gateway.
- DeepSeek-V4 on NVIDIA NIM = HTTP 410 (EOL), not a key problem.
- GLM-5.2 = now PAID on both OpenRouter and NVIDIA NIM (no free tier).
The correct takeaway: validate with `scripts/verify_models.py` and read error codes
precisely; do not assume "Docker" or "keys" are the cause of a 403.

## CRITICAL DISTINCTION — Catalog Refresh ≠ Per-Task Router
**What exists today (deployed):**
- Daily cron at 00:01 MYT → `refresh_models.py` fetches live catalogs → writes `models.md` + `models_sequence.json`
- Self-heal: if pinned main model leaves free tier, next daily refresh re-pins via `hermes config set`
- This is a **catalog maintenance layer**, not a runtime router

**What does NOT exist (Phase 3 build target):**
- Per-task category classifier (16-category prompt tagging)
- Real-time probe/fallback chain (15-min TTL health → router)
- Runtime Model Gateway API (`route(category)`) that Hermes calls instead of direct model
- Vision auto-route: `vision_analyze` uses **main model via fast-path** when main is vision-capable (OpenRouter/Nous aggregators). `auxiliary.vision` only engages if main CANNOT see images.
- Mid-session main model hot-swap: config change takes effect on NEXT session start

## NOUS PORTAL LIMIT CORRECTION (verified Aug 2026)
- **20 RPM / 500 TPM** (rolling per minute) — NOT 200 RPM, NOT 500K TPM
- `laguna-s:free` and `step-3.7-flash:free` are **NOT on Nous free tier** (only `laguna-m.1:free` is)
- NIM free tier: 40 RPM, lifetime 1000 credits → PERMANENT removal when exhausted
