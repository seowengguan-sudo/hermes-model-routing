---
name: hermes-model-catalog
description: Maintain Hermes model catalog free paid daily refresh.
category: productivity
---

# hermes-model-catalog

## When to use
- User asks which models are free, compares providers, wants the largest-context model, or says the model list/dropdown is stale.
- You need an accurate free/paid split for Nous Portal, NVIDIA NIM, OpenRouter, DeepSeek, Google Gemini.

## Refresh mechanism (deployed 2026-08-10)
Generator `/opt/data/refresh_models.py` **overwrites** `/opt/data/models.md` daily.
- Fetches **live** OpenRouter `/v1/models`; filters free tier (`prompt=0 & completion=0`) and near-free paid.
- Appends **curated** tables for Nous/NIM/DeepSeek/Gemini (keys/HTML docs → maintained lists w/ verified-date note, not live-scraped).
- Cron job `daily-models-md-refresh` runs it at `0 9 * * *` UTC, `deliver=local`, overwrite semantics (idempotent).
- Force-refresh: `python3 /opt/data/refresh_models.py`. Verified run = 17 live free models.

## CRITICAL caveat — tell the user
`models.md` is the **agent-readable daily reference**; it does **NOT** update the in-app **dropdown** (that reads `hermes_cli/models.py` static catalog + optional probe). Fixing the dropdown = patch `hermes_cli/models.py` / model-fetch path (separate task; ask before editing Hermes source).

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

## Always re-probe, never guess (numbers drift)
```
curl -s https://openrouter.ai/api/v1/models | python3 -c \
"import sys,json;d=json.load(sys.stdin);[print(m['id'],m.get('context_length')) for m in d['data'] if float(m.get('pricing',{}).get('prompt',1))==0 and float(m.get('pricing',{}).get('completion',1))==0]"
```
Trap hit this session: `poolside/laguna-s-2.1:free` was once listed at 1.05M context but live data showed 262K — a stale listing that had already misled an answer. Always verify live.

## See also
- `references/free-tier-landscape.md` — provider structure + gotchas.
- `scripts/refresh_models.py` — re-runnable generator (copy if rebuilding).
