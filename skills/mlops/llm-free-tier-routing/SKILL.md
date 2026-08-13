---
name: llm-free-tier-routing
description: "Benchmark and route free LLM models per task."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [llm, routing, cost-optimization, benchmarking, free-tier, multi-provider]
---

# LLM Free-Tier Routing & Validation

## When to use
- You hold several LLM provider API keys (OpenRouter, NVIDIA NIM, Groq, Cerebras, HuggingFace, Nous Portal) and want every agent task routed to the **most cost-effective free model** automatically.
- You want **automatic model switching** when a provider is exhausted or rate-limited — validation-driven, not guessed.
- You want **empirical quality scoring** instead of assuming which free model is "good enough."
- You must **never** silently spend on paid models (Gemini paid, DeepSeek direct paid) without explicit user approval.

## Approach (end to end)
1. **Inventory** free models per provider. **Do NOT assume a provider is absent or paid — enumerate EVERY provider the user has a key for and check its free tier explicitly.** In one session the user corrected this exact omission: Groq and Cerebras keys were present and both are free-tier, but were initially left out of the inventory. Query each provider's models endpoint (OpenAI-compatible: `GET {base}/models`; NVIDIA/HF differ) or hardcode known free IDs. Separate FREE from PAID via pricing fields or `:free` suffixes.
2. **Validate**: per `(provider, model)` run fixed benchmark prompts covering task types — `simple_factual`, `code_generation_basic`, `code_generation_complex`, `debugging_reasoning`, `architecture_design`, `cross_domain_synthesis`. Score each output heuristically 0–10. Record latency.
3. **Persist** to `results.json`: `{models:{key:{provider,model,strength,tasks:{tid:{score,latency,note}},avg_score,avg_latency,status}}, provider_health:{prov:"ok/total"}}`.
4. **Route**: given a prompt, classify task type + complexity (1–10), rank by `combined = avg_score + (2.0 if strength in preferred else 0) - min(latency/10, 1.0)`, exclude providers that scored 0 across the board, return best + top-5 fallback chain.
5. **Gate paid models**: FREE allowlist only. Paid providers selected ONLY on explicit user approval flag.

## Resilient validation (key pitfall)
- **Sandboxed Docker/WSL deployments often BLOCK some providers at network egress** (HTTP 403/timeout) even with valid keys. This is NOT a model-quality verdict — do NOT record it as score 0 and discard the model. Run validation, then have the router **auto-exclude providers that returned 0 successful calls**, storing `provider_health` separately from per-model scores. Re-run the validation from a different network (user's laptop) to unlock them.
- Use **parallel workers** (`ThreadPoolExecutor(max_workers=8)`) with **per-call timeout ~25s**. A sequential sweep with 60s timeouts over 200+ calls takes hours and one slow provider stalls everything.

## Router design details
- `classify_complexity(prompt)`: word count + signal keywords → 1–10 (design/architect→7, debug/error→6, class/function→5, cross/analyze/compare→8).
- `classify_task_type(prompt)`: keyword routing (debug/error→debugging_reasoning; design/system→architecture_design; cross/compare→cross_domain_synthesis; class/algorithm→code_generation_complex; function/code→code_generation_basic; what is/port→simple_factual).
- `STRENGTH_AFFINITY`: task_type → preferred model strengths (architecture_design→[reasoning, expert, code+]).
- Working providers go first in fallback chain; failed ones dropped.

## Anti-paid gating rule
- FREE allowlist. `route(prompt, force_provider=None)`. Paid model requires explicit `approve_paid=True` (or confirmed intent). Router NEVER quietly escalates to a paid key.

## Pitfalls
- Don't score quality on raw token counts — use task-specific heuristics: code tasks check `def `/`class `/docstring/`import`; debugging checks `event loop`/`asyncio`/`nest`; architecture checks `service`/`micro`/`failure`/`retry`.
- Not all providers are OpenAI-compatible. **HuggingFace serverless** uses `POST https://api-inference.huggingface.co/models/{id}` with `{"inputs":prompt,"parameters":{"max_new_tokens":N}}` → `[{generated_text}]`.
- Don't write results incrementally in a crash-prone way — dump full JSON at end (checkpoint to temp file if needed).
- Don't assume a key works because non-empty — validate connectivity with one quick call before a big sweep.
- **Don't leave a keyed provider out of the inventory.** The user treats every keyed provider's free tier as fair game; omitting one (e.g. Groq/Cerebras with valid free keys) is a real correction, not a nitpick. When listing providers, start from the user's actual `.env` keys, not from memory of "which providers usually have free tiers."

### Diagnostic pitfalls (learned 2026-08-07 — see `references/provider-diagnostic-taxonomy.md`)
- **HTTP 403 Cloudflare 1010 = ASN ban, NOT Docker, NOT a dead key.** Docker/WSL2 NATs through the host, so egress IP is identical in/out of the container. Removing Docker will NOT fix a 1010. Fix = different egress ASN or the provider's OAuth gateway path.
- **HTTP 410 "end of life" = model retired, NOT token exhaustion.** NVIDIA DeepSeek-V4 FLASH/PRO went EOL 2026-08-07 (HTTP 410) — do not relist or call it "run out of tokens". DeepSeek "exhausted" on OpenRouter was a *paid credit* limit, separate from the NVIDIA free EOL.
- **OpenRouter free slug format: `nvidia/nemotron-3-super-120b-a12b:free` — do NOT prepend `openrouter/`.** The wrong prefix returns HTTP 400 "not a valid model ID", which looks like exhaustion but is just a bad slug.
- **Nous Portal: verify via Hermes's OAuth gateway, not raw `portal.nousresearch.com/v1` REST.** A script calling the raw endpoint gets 429 (Vercel Security Checkpoint); the model is fine through the gateway (the live chat proves it). A 429 here means "use the gateway path", not "Nous is down".
- **Enumerate `/v1/models` and filter `:free` BEFORE testing.** Free slugs drift (DeepSeek-V4, GLM-5.2 both lost their free tiers). Hardcoding from memory produces 400/404.

## References
- `references/provider-inventory.md` — 6-provider free-model inventory captured in-session.
- `references/validation-schema.md` — exact `results.json` shape and scoring rubric.
- `references/provider-diagnostic-taxonomy.md` — error→cause table (1010/429/410/404/400/DNS), egress-IP reality, and the 2026-08-07 live provider snapshot. START HERE when a provider "fails" validation.

## Scripts
- `scripts/validate.py` — parallel benchmark harness template.
- `scripts/router.py` — validation-driven router template.

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
