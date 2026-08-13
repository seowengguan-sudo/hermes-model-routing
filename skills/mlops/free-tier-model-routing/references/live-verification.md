# Live Provider Verification — Findings (2026-08-07)

How to read provider responses when building a free-tier routing table, and what
actually blocked 4 of 6 providers in this deployment's egress environment.

## Egress IP & ASN (the real blocker)
- Outbound IP observed: `161.142.137.99` → **AS9930 TTNET, George Town, Penang, Malaysia**.
- Docker on WSL2 NATs through the Windows host, so the container exit IP = host exit IP.
  Removing Docker does NOT change the egress ASN. Any "provider X works on my laptop but
  not in the container" difference is an *ISP/ASN* difference, not a Docker difference.

## Per-error interpretation (capture `e.read().decode()` on `HTTPError`)
| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK | Use it |
| 400 | Bad model ID (e.g. `openrouter/...` prefix on OpenRouter) | Fix the id from `GET /v1/models` |
| 401 | Bad/expired key | Re-issue key |
| 403 + Cloudflare "error 1010" | ASN banned by provider's Cloudflare edge | Route via different ASN (VPN/proxy) or Hermes gateway |
| 404 | Model/endpoint gone at this URL | Correct endpoint or id |
| 410 | Model removed (EOL) | Drop from free list (e.g. DeepSeek-V4 on NVIDIA NIM) |
| 429 | Rate-limited | Temporary; retry / different IP; NOT "exhausted" |

## Provider-by-provider result (this environment, 2026-08-07)
- **NVIDIA NIM** (`integrate.api.nvidia.com/v1`): `meta/llama-3.1-8b-instruct` OK (fast),
  `meta/llama-3.1-70b-instruct` OK, `meta/llama-3.3-70b-instruct` timeout (slow/queued).
  DeepSeek-V4 flash/pro → HTTP 410 (EOL).
- **OpenRouter** (`openrouter.ai/api/v1`): 13/14 `:free` models OK; `google/gemma-4-31b-it:free`
  = 429 (recoverable). Free IDs have NO `openrouter/` prefix.
- **Groq** (`api.groq.com/openai/v1`): HTTP 403 Cloudflare 1010 (ASN ban).
- **Cerebras** (`api.cerebras.ai/v1`): HTTP 403 Cloudflare 1010 (ASN ban).
- **HuggingFace** (`api-inference.huggingface.co`): DNS fail on `/models/<id>` subdomain in
  container; `api-inference.huggingface.co` root resolves. Use base endpoint or Hermes HF.
- **Nous Portal** (OAuth via Hermes gateway): `tencent/hy3:free` works through the gateway
  (it was the live active model). Direct `POST <inference_base_url>/chat/completions` with the
  cached token in `/opt/data/shared/nous_auth.json` → HTTP 403 (token expires ~hourly; refresh
  via `/oauth/token` returned 404 in test). Label Nous models "Gateway-verified", not "direct-OK".
- **Gemini** (paid; `generativelanguage.googleapis.com/v1beta/openai`): only `gemini-2.5-flash`
  returned 200; `gemini-2.5-pro`, `gemini-2.0-flash`, `gemini-1.5-pro`, `gemini-1.5-flash`,
  `gemini-2.5-flash-lite` → 404 (id/endpoint needs correction).
- **DeepSeek** (paid on OpenRouter): `deepseek/deepseek-v4-flash` + `-pro` both OK (paid).
  NVIDIA free copies are EOL.

## Capability-matrix honesty rule
When writing a model/capability table for the user: set the "Verified" column to real probe
results — `OK`, `429`, `403`, `410`, `404`, or `Gateway-verified`. Never mark a model
"Verified OK" on the basis of documentation alone; flag unverified ones with `?` or
"Gateway-verified". Do not fabricate success for models that 404/403'd.
