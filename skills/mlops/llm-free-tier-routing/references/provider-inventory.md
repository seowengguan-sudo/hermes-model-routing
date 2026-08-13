# Free-Tier Provider Inventory (captured in-session)

## Validated WORKING in the WSL/Docker sandbox
- **NVIDIA NIM** (`https://integrate.api.nvidia.com/v1`): `meta/llama-3.1-8b-instruct` scored 9.83/10 (4.5s) — TOP model. Also `meta/llama-3.3-70b-instruct`, `mistralai/*`, `google/gemma-*`, `z-ai/glm-5.2`, `deepseek-ai/deepseek-v4-flash|pro`. Free tier = 1000 calls/month.
- **OpenRouter** (`https://openrouter.ai/api/v1`): `nvidia/nemotron-3-super-120b-a12b:free` 8.83/10, `nvidia/nemotron-3-ultra-550b-a55b:free` 8.17/10 (1M ctx), `openrouter/free`, `nvidia/nemotron-3-nano-30b-a3b:free`. Free models tagged `:free`.

## Blocked at egress in the sandbox (403/timeout) — likely work from laptop
- **Groq** (`https://api.groq.com/openai/v1`): `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `groq/compound`, `openai/gpt-oss-120b`, `qwen/qwen3.6-27b`. 30 req/min, 14400/day.
- **Cerebras** (`https://api.cerebras.ai/v1`): `gpt-oss-120b`, `gemma-4-31b`, `zai-glm-4.7`. Ultra-low latency.
- **HuggingFace** (`https://api-inference.huggingface.co/models/{id}`): `Qwen/Qwen2.5-*`, `Qwen/Qwen3-Coder-*`, `meta-llama/Llama-3.1-8B-Instruct`. Serverless, format differs (see SKILL.md pitfalls).
- **Nous Portal** (OAuth built-in): various open models via subscription.

## Paid (NEVER auto-use without approval)
- **Google Gemini** (`GEMINI_API_KEY`)
- **DeepSeek direct** (`DEEPSEEK_API_KEY`)
- Note: OpenRouter also exposes DeepSeek as a *paid* model (`deepseek/deepseek-v4-flash`) — do NOT confuse with NVIDIA's *free* `deepseek-ai/deepseek-v4-flash`.

## Key: DeepSeek V4 Flash is FREE on NVIDIA NIM, PAID on OpenRouter
When OpenRouter credits exhaust, fall back to `provider: nvidia, model: deepseek-ai/deepseek-v4-flash` (free). The Hermes active-model switch message confirms the fallback chain is live.
