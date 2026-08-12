# Verified Provider Free-Tier Limits

Source: web_search during 2026-08 session + user-stated ASN constraints. Re-verify before shipping.

## Priority chain (canonical)
Nous Portal (free) → OpenRouter (free) → NVIDIA NIM (free) → Paid (Gemini / DeepSeek-direct).
Groq / Cerebras / HF are EXCLUDED (Cloudflare WAF 1010 from user's egress ASN TTNET MY, Penang).

## Free tiers
| Provider | RPM | TPM | Daily reset | Notes |
|---|---|---|---|---|
| Nous Portal | 50* (third-party guide on $0 tier; user reports 200 on higher plan) | 500K | MYT 08:00 | Verify actual plan RPM before relying on 200. |
| OpenRouter | 20/min, **50/day** | per-model | Daily | 50 req/day is the BINDING agentic constraint; 429 expected mid-task. |
| NVIDIA NIM | n/a | n/a | **ONE-TIME lifetime** | On exhaustion free tier is permanently gone → escalate to paid, never retry. |

## Paid tiers (only the reachable ones are selectable)
- DeepSeek-direct: `deepseek/deepseek-v4-flash` (DEFAULT paid, cheap) + `deepseek/deepseek-v4-pro` (reserve for super-complex only). Others not in matrix.
- Gemini: **only `gemini-2.5-flash`** reachable. The following are 404 from this egress: `gemini-2.5-pro`, `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-2.0-flash`, `gemini-2.0-flash-lite`, `gemini-2.5-flash-lite`.
- **Every paid call requires explicit UI approval** before execution.

## Exhaustion behaviour
- 429 on a tier → router flips to next non-exhausted slot for remaining sub-tasks (whole task not aborted).
- NIM lifetime spent → skip NIM entirely, go to Paid (Slot 4); NIM never retried.
- All free exhausted → queue Paid, notify user w/ justification, continue on free-or-degraded, settle on approval.
