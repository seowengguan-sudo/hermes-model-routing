# Free-Tier Provider Inventory (condensed)

Verified model IDs available on each provider's free tier (no per-token cost).
Source of truth: live API listing of each provider + `.env` keys present at
session time. A key existing ≠ the model is free (DeepSeek on OpenRouter is paid).
Re-validated 2026-08-07 — providers rotate models, so confirm via `GET /v1/models`.

## NVIDIA NIM — `https://integrate.api.nvidia.com/v1` (key: NVIDIA_API_KEY)
Limit: 1000 calls/month. FREE and confirmed live:
- `meta/llama-3.1-8b-instruct` (fast, ~0.7s) — practical TOP performer
- `meta/llama-3.1-70b-instruct` (~0.6s)
- (verify others via `GET /v1/models` — several documented models 404/removed)
REMOVED / NO LONGER FREE (HTTP 410/404 as of 2026-08-07):
- `deepseek-ai/deepseek-v4-flash` — was free, now GONE from NVIDIA
- `deepseek-ai/deepseek-v4-pro` — now GONE
- `writer/palmyra-fin-70b`, `writer/palmyra-med-70b`, `mistralai/mistral-large-2-instruct`,
  `mistralai/mixtral-8x22b-v0.1`, `stepfun-ai/step-3.7-flash`, `z-ai/glm-5.2`,
  `google/gemma-4-31b-it` — verify; some 404'd in live test.

## Groq — `https://api.groq.com/openai/v1` (key: GROQ_API_KEY)
Limit: 30 req/min, 14,400 req/day. Free (blocked from ASN in this sandbox, see below):
- `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `groq/compound`, `groq/compound-mini`,
  `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.6-27b`.

## Cerebras — `https://api.cerebras.ai/v1` (key: CEREBRAS_API_KEY)
Extremely fast inference (wafer-scale). Free (blocked from ASN in this sandbox):
- `gpt-oss-120b`, `gemma-4-31b`, `zai-glm-4.7`.

## OpenRouter free — `https://openrouter.ai/api/v1` (key: OPENROUTER_API_KEY)
Free-tagged models (`:free` suffix, $0). 14 listed, 13 working as of 2026-08-07.
**ID FORMAT: no `openrouter/` prefix.** Use `nvidia/nemotron-3-super-120b-a12b:free`,
NOT `openrouter/nvidia/...` (that gives HTTP 400).
- `nvidia/nemotron-3-super-120b-a12b:free` (263k ctx) — recommended for reasoning
- `nvidia/nemotron-3-ultra-550b-a55b:free` (1M ctx)
- `nvidia/nemotron-3-nano-30b-a3b:free`
- `openai/gpt-oss-20b:free`, `google/gemma-4-26b-a4b-it:free`, `google/gemma-4-31b-it:free`
  (intermittent 429), `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`,
  `cohere/north-mini-code:free`, `inclusionai/ling-3.0-tiny:free`
- `openrouter/free` (auto-routes to best free model)
NOTE: `deepseek/deepseek-v4-flash` here is PAID — do NOT confuse with NIM's free one.

## HuggingFace — `https://api-inference.huggingface.co/models` (key: HF_TOKEN)
Thousands of serverless inference models. `api-inference.huggingface.co` DNS fails in
this sandbox; works from a normal network. Popular text-gen: `Qwen/Qwen2.5-*-Instruct`,
`meta-llama/Llama-3.1-8B-Instruct`. Slower / rate-limited; last-resort fallback.

## Nous Portal — built into Hermes (OAuth, no key)
Automatic fallback target when all provider keys exhaust. Various open models.

## Sandbox egress note (WSL2→Docker on this host)
Egress IP `161.142.137.99` (AS9930 TTNET, Penang). Groq + Cerebras get Cloudflare 1010
(ASN ban) — NOT a Docker or key problem. NVIDIA + OpenRouter work. HF fails on DNS only.
These blocks are network/ASN-specific, not durable rules about the providers.
