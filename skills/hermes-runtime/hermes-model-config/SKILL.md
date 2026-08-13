---
name: hermes-model-config
description: Apply Hermes model config changes via hermes config set.
---

# Hermes Model Config — Safe Edits

## When to use
You need to change `model.default`, `model.provider`, or any `auxiliary.<category>.model/provider`
in Hermes config — e.g. implementing a model-selection policy, switching the main model to a
free-tier alternative, or applying a reviewed config snippet.

## CRITICAL: direct file writes are BLOCKED
The agent CANNOT `patch`/`write_file` `/opt/data/config.yaml` (or `~/.hermes/config.yaml`).
The runtime refuses with:
> Refusing to write to Hermes config file ... Edit ~/.hermes/config.yaml directly or use 'hermes config' instead.

Do NOT retry with raw file writes or symlink tricks. Use the sanctioned CLI path below.

## The sanctioned path: `hermes config set`
1. Locate the binary. It is NOT on the shell PATH by default. Use the project venv:
   `/opt/hermes/.venv/bin/hermes`  (has pyyaml + deps; plain `python3` lacks `yaml`).
2. Set scalar values with nested dot-keys (dict paths are auto-created):
   ```
   /opt/hermes/.venv/bin/hermes config set model.default "tencent/hy3:free"
   /opt/hermes/.venv/bin/hermes config set model.provider "nous"
   /opt/hermes/.venv/bin/hermes config set auxiliary.vision.model "nvidia/nemotron-nano-12b-v2-vl:free"
   /opt/hermes/.venv/bin/hermes config set auxiliary.mcp.provider "openrouter"
   ```
   Each prints `✓ Set <key> = <value> in /opt/data/config.yaml`.
3. Changes take effect on the NEXT session reload — never mid-session. State this to the user.

## Pitfall: cron jobs "fail closed" after a model change
Changing `model.default` / `model.provider` triggers a warning:
> 1 enabled unpinned cron job has stored model_snapshot values that differ ... will fail closed on its next run.

**Fix — re-pin via CLI (NOT the `cronjob` tool).** The `cronjob` action=update wrapper accepts
a `model`/`provider` argument shape but **silently drops them** (returns "No updates provided"
with HTTP 200). Use the terminal instead:
```
hermes cron edit <job_id> --model <model> --provider <provider>
```
Then verify the *persisted* model directly:
```
python3 -c "import json;d=json.load(open('cron/jobs.json'));print([j for j in d['jobs'] if j.get('id')==<id>][0].get('model'))"
```
(Setting model/provider to the new global values resolves the drift; see
`hermes-cron-model-pinning` for the full pin/repair checklist.)

## Pitfall: verify the model spec BEFORE setting it
See `references/verify-model-specs.md` for ready-run probe commands.
Stale cached data causes wrong assertions. In the session that produced this skill,
`poolside/laguna-s-2.1:free` was claimed as 1.05M context from an old listing; the live
OpenRouter `/v1/models` showed **262K**. Always re-probe the provider before committing a
model to config:
- **OpenRouter:** `GET https://openrouter.ai/api/v1/models` → free tier = `pricing.prompt==0 and pricing.completion==0`; read `context_length`.
- **DeepSeek:** `GET https://api.deepseek.com/v1/models` returns **401 without a key** → fall back to known names (`deepseek-v4-flash`, `deepseek-v4-pro`); never invent a 4th free model.
- **Gemini:** live-scrape `https://ai.google.dev/gemini-api/docs/models` (HTML); regex `gemini-[a-z0-9.\-]+`.
- **Never** assert a provider's free-model count or context window from memory — re-verify live.

## DeepSeek rule (if relevant)
Paid only. `deepseek-v4-flash` ≈ $0.14/1M in; `deepseek-v4-pro` ≈ 3× and prices rise soon.
If a policy needs DeepSeek, default to **v4-flash**; gate **v4-pro** behind explicit user approval.

## SELF-HEAL: auto-repin main model when a free model is removed
A model pinned in `model.default` that drops out of the free tier causes every turn to 404
until manually fixed. Automate recovery with a refresh script that re-pins via THIS skill's
path. Verified working pattern (see `references/self-heal-contract.md`):
1. At refresh time (cron or stale-check gate), read `model.default` via `hermes config get`.
2. If it is NOT in the live free catalog → walk a performance-ordered MAIN_CHAIN and
   `hermes config set model.default <next>` + `model.provider <prov>`; log the swap.
3. Changes land on next session reload — no manual fix needed after a free-tier removal.
- The script must hard-code MAIN_CHAIN + the `/opt/hermes/.venv/bin/hermes` binary path.
- Self-heal runs at REFRESH TIME, not mid-session; a mid-session removal still errors until
  the next refresh (acceptable — removals are rare).

## Performance-ordered main chain (user-approved, Nous-first)
All top-3 are Nous free (20 RPM / 500 TPM — steady per-minute, safer than OpenRouter daily bucket):
1. `nvidia/nemotron-3-ultra-550b-a55b:free` (nous)  — biggest/1M ctx, #1 by capability
2. `tencent/hy3:free` (nous)
3. `nvidia/nemotron-3-super-120b-a12b:free` (nous)
4. `poolside/laguna-xs-2.1:free` (openrouter)
5. `inclusionai/ling-3.0-tiny:free` (openrouter)
Put the most CAPABLE Nous model first (not the lightest) when the user wants performance over
latency; the 20RPM/500TPM cap is per-minute and resets continuously, so model size alone does
not change exhaustion risk for a single steady user.

## Provider free-tier limit facts (for limit-aware fallback)
- **Nous Portal:** 20 RPM / 500 TPM (rolling per minute).
- **NVIDIA NIM:** 40 RPM, **lifetime 1000 credits** — on `credit_used ≥ 1000` PERMANENTLY drop
  the model from all sequences (never choose again).
- **OpenRouter:** free-tier resets **MYT 08:00 daily**; heavy PAID models → warn on token burn.
- **DeepSeek / Gemini:** paid; estimate spend = tokens × published price; warn before large
  calls; user verifies real balance. Never auto-select paid for the main loop.

## Companion
Pairs with the (user-owned) `model-selection-policy` skill, which defines free-first per-category
sequences and should apply its config via THIS skill's `hermes config set` path — not raw file
writes. Recommend `hermes curator adopt model-selection-policy` if you want it curator-managed
and patchable; do not hand-patch a user-owned skill.

Also pairs with `hermes-cron-model-pinning` whenever this skill's model change triggers a
drift-guard on cron jobs: after setting `model.default`, immediately re-pin all cron jobs via
`hermes cron edit <job_id> --model <m> --provider <p>` — see that skill's Pitfall #1/#5 for the
silent-failure verification pattern.
