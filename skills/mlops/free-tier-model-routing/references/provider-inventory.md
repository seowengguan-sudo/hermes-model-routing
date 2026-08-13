# Free-Tier Provider Inventory (verified across sessions)

Keys the user holds: `OPENROUTER_API_KEY`, `NVIDIA_API_KEY`, `GROQ_API_KEY`,
`CEREBRAS_API_KEY`, `HF_TOKEN`, and Nous Portal OAuth. Gemini + DeepSeek direct
keys exist but are PAID — never use without approval.

## LIVE RE-VALIDATION (this session, API key check on 2026-08-07)
Used `GET https://openrouter.ai/api/v1/models` and direct chat calls to confirm
current free models. Findings:

### OpenRouter — key is ALIVE, NOT exhausted
- 14 free models listed; 13 responded OK, 1 (`google/gemma-4-31b-it:free`) was
  HTTP 429 (temporary rate-limit, not exhaustion).
- **WORKING free IDs:** `nvidia/nemotron-3-super-120b-a12b:free`,
  `nvidia/nemotron-3-ultra-550b-a55b:free` (1M ctx),
  `nvidia/nemotron-3-nano-30b-a3b:free`, `openai/gpt-oss-20b:free`,
  `google/gemma-4-26b-a4b-it:free`, `poolside/laguna-s-2.1:free`,
  `poolside/laguna-xs-2.1:free`, `cohere/north-mini-code:free`,
  `google/gemma-4-31b-it:free` (intermittent 429), `inclusionai/ling-3.0-tiny:free`,
  `nvidia/nemotron-3.5-content-safety:free`, `nvidia/nemotron-nano-12b-v2-vl:free`,
  `nvidia/nemotron-nano-9b-v2:free`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`.
- **CRITICAL ID-FORMAT PITFALL:** the model id used in the API is WITHOUT the
  `openrouter/` prefix. `openrouter/nvidia/nemotron-3-super-120b-a12b:free`
  returns HTTP 400 "not a valid model ID". Use `nvidia/nemotron-3-super-120b-a12b:free`.

### NVIDIA NIM — key is ALIVE
- **WORKING:** `meta/llama-3.1-8b-instruct` (fast, ~0.7s), `meta/llama-3.1-70b-instruct` (~0.6s).
- **REMOVED (now HTTP 410/404):** `deepseek-ai/deepseek-v4-flash` and
  `deepseek-ai/deepseek-v4-pro` — these IDs no longer exist on NVIDIA. The earlier
  `deepseek-v4-pro` 25s timeout was also unreliable; treat the v4-flash/pro DeepSeek
  line as GONE from NVIDIA. `meta/llama-3.3-70b-instruct` timed out (queued, not dead).
- Other tried IDs 404 (nemotron-ultra-253b, palmyra-fin-70b, mistral-7b) — confirm via
  `GET https://integrate.api.nvidia.com/v1/models` before relying on them.

## Providers BLOCKED — ROOT CAUSES (unchanged from prior session)

| Provider | Error | Root cause |
|---|---|---|
| Groq | HTTP 403, Cloudflare 1010 | ASN reputation block (AS9930 TTNET blocked) |
| Cerebras | HTTP 403, Cloudflare 1010 | Same ASN block |
| HuggingFace | DNS fail for `api-inference.huggingface.co` | Sandbox DNS allowlist |
| Nous Portal direct API | HTTP 429 rate limited | Free tier quota exhausted |

**Egress IP:** `161.142.137.99` (AS9930, George Town, Penang)
- **Not a Docker issue** — egress is the same if run natively
- Cloudflare blocks this ASN for Groq/Cerebras

## Diagnostic technique (do this, don't guess)
When a provider "fails", capture the real error body, don't assume exhaustion:
1. Print `e.read().decode()` on HTTPError — distinguishes 400 (bad id) / 401 (key) /
   403 (ASN/Cloudflare 1010) / 410 (model removed) / 429 (rate-limit) / 404 (gone).
2. `GET /v1/models` to list what actually exists right now (providers rotate models).
3. A 403 with Cloudflare "error 1010" = ASN ban, NOT a key or Docker problem.

## Key gotcha
- `deepseek/deepseek-v4-flash` = PAID on OpenRouter
- `deepseek-ai/deepseek-v4-flash` = was FREE on NVIDIA NIM — **now REMOVED (HTTP 410)**
- Check the **endpoint**, not just the model name

## Update after re-validation
Run: `python3 model_benchmark/validate.py` → check `model_benchmark/results.json`
Or just `GET /v1/models` per provider to refresh the live list.
