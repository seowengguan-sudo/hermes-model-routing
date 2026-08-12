---
name: hermes-model-tiering
description: "Free-tier model routing and per-model validation for Hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Hermes Model Tiering (Free-Tier Routing)

Make Hermes run on **$0 LLM spend** by routing every task to the best available
**free-tier** model, and auto-switching when a provider is exhausted.

## When to use
- User says "use only free models", "minimize cost", "don't use paid keys".
- User wants a model router / fallback chain across providers.
- You are setting up or auditing the `model:` config in `~/.hermes/config.yaml`.
- User has multiple API keys in `.env` and wants them leveraged efficiently.

## Hard rules (learned from real failures)
1. **Enumerate EVERY provider from the actual `.env` keys.** Do not assume a
   subset. A session missed Groq and Cerebras because the agent only listed 4
   providers — both had free-tier keys and were valid. Read `.env`, list every
   `*_API_KEY` / `HF_TOKEN`, then classify free vs paid.
2. **Validate PER-MODEL, not per-provider.** Users care which specific model
   handles which task. A provider having "free models" is not enough — test each
   model ID individually (see `scripts/model_benchmark.py`).
3. **A model is not free on every provider — and catalogs rotate.** Classic gotcha:
  - `deepseek/deepseek-v4-flash` → **PAID** on OpenRouter (credits run out)
  - `deepseek-ai/deepseek-v4-flash` → was **FREE** on NVIDIA NIM, but as of
    2026-08-07 returns HTTP 410 (model removed from NVIDIA). Confirm via
    `GET https://integrate.api.nvidia.com/v1/models` before relying on it.
  Same family, opposite tier — and provider model lists go STALE. Always pull
  the live id list; never hardcode free-model assumptions.

## Provider free-tier inventory (condensed)
Full table in `references/free_provider_inventory.md`. Highlights:
- **NVIDIA NIM** (`https://integrate.api.nvidia.com/v1`, key `NVIDIA_API_KEY`):
  `meta/llama-3.1-8b-instruct` (fast), `meta/llama-3.1-70b-instruct`,
  `meta/llama-3.3-70b-instruct`. Limit: 1000 calls/month. NOTE: `deepseek-ai/deepseek-v4-flash`
  and `-pro` were removed (HTTP 410 as of 2026-08-07) — verify via `GET /v1/models`.
- **Groq** (`https://api.groq.com/openai/v1`, key `GROQ_API_KEY`):
  `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `groq/compound`,
  `openai/gpt-oss-120b`, `qwen/qwen3.6-27b`. Limit: 30 req/min, 14.4k/day.
- **Cerebras** (`https://api.cerebras.ai/v1`, key `CEREBRAS_API_KEY`):
  `gpt-oss-120b` (fastest inference), `gemma-4-31b`, `zai-glm-4.7`.
- **OpenRouter** (`https://openrouter.ai/api/v1`, key `OPENROUTER_API_KEY`):
  `openrouter/free`, `nvidia/nemotron-3-ultra-550b-a55b:free` (1M ctx),
  `nvidia/nemotron-3-super-120b-a12b:free`, `google/gemma-4-31b-it:free`,
  `openai/gpt-oss-20b:free`, `cohere/north-mini-code:free`, Poolside laguna.
- **HuggingFace** (`https://api-inference.huggingface.co/models`, key `HF_TOKEN`):
  thousands of serverless models, e.g. `Qwen/Qwen2.5-32B-Instruct`,
  `Qwen/Qwen3-Coder-30B-A3B-Instruct`, `meta-llama/Llama-3.1-8B-Instruct`.
- **Nous Portal** (OAuth, built into Hermes, no key): various open models; the
  automatic fallback target when all keys exhaust.

## Hermes auto-fallback behavior (important)
Hermes already auto-switches the active provider when the configured one is
exhausted — you'll see a system message: "The active model for this chat has
changed to X via provider Y." **Design your primary + fallback to use the SAME
model family on different free providers** so quality is preserved across the
switch (e.g. primary OpenRouter DeepSeek-paid → fallback NVIDIA NIM
`deepseek-ai/deepseek-v4-flash` free). Do NOT rely on this alone for cost
control — explicitly set free models in config so you never drift to paid.

## Task → complexity → model tier
- Score 1-3 (simple): fast small models — `groq/llama-3.1-8b-instant`,
  `nvidia/meta-llama-3.1-8b-instruct`, `inclusionai/ling-3.0-flash:free`.
- Score 4-6 (standard): `nvidia/meta/llama-3.1-70b-instruct`,
  `groq/openai/gpt-oss-20b`, `openrouter/cohere/north-mini-code:free`.
- Score 7-8 (complex/strategic): `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free`
  (1M ctx), `groq/llama-3.3-70b-versatile`, `nvidia/z-ai/glm-5.2`.
- PAID (Gemini / DeepSeek direct) → **always ask user permission first**.

## Validation workflow
1. Build the model×task matrix (see `scripts/model_benchmark.py`).
2. Run each model against 6 task categories: simple_factual, code_gen_basic,
   code_gen_complex, debugging_reasoning, architecture_design,
   cross_domain_synthesis.
3. Heuristically score output (0-10) + measure latency.
4. Persist to `results.json`; pick best free model per task category.
5. Wire the winner into `config.yaml` `model:` with a fallback provider.

## Pitfalls
- Don't treat `.env` as the source of truth for *what's free* — a key existing
  does not mean the model is free (DeepSeek on OpenRouter is paid).
- HuggingFace free inference is rate-limited per model popularity and slower;
  use it as a last-resort fallback, not primary.
- NVIDIA NIM's 1000-calls/month is the tightest limit — reserve it for the
  highest-value tasks or as a quality fallback, not high-frequency calls.

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
