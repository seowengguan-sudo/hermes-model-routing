# Verified free-tier limits (2026-08) — feed the Provider_Budget sheet

| Provider | Free tier limit (verified/approx) | Notes |
|---|---|---|
| OpenRouter | **50 requests/day**, 20 req/min | The 50/day is the BINDING constraint for agentic multi-call work; one task with sub-calls can exhaust it in minutes. Daily reset. |
| NVIDIA NIM | one lifetime credit pool | Effectively a fixed pool; once gone, position-3 fails permanently — router must skip to paid, not retry. |
| Nous Portal | **20 RPM / 500 TPM** ($0 tier; some report 200 RPM on higher paid plan — verify) | Daily reset MYT 8am. `laguna-s:free` and `step-3.7-flash:free` are NOT on Nous free tier (only `laguna-m.1:free` is). Works through Hermes gateway; direct API 403s on OAuth expiry. |
| Gemini (paid) | credit-gated | Only `gemini-2.5-flash` reachable; 1.5/2.0/2.5-pro are 404 at the OpenAI-compat URL. Needs user approval before use. |
| DeepSeek (paid) | credit-gated (~$0.09/M for v4-flash) | `deepseek-v4-flash` / `deepseek-v4-pro` OK; needs user approval. |

## Loop behavior the limits imply
- OpenRouter 50/day exhaustion → mid-task 429 → re-route REMAINING sub-tasks, don't abort whole task.
- NIM lifetime empty → drop to paid fallback (if approved) or STOP+ask.
- Paid escalation requires async approval: use a pending-approval queue (notify, continue on
  free-or-degrade, settle paid later) rather than a hard stop that blocks the autonomous loop.

## Source notes
- OpenRouter: official pricing page (50 reqs/day free), klymentiev.com blog (two-tier: 50/day <$10
  spent, 1000/day after).
- Nous Portal: openclawlaunch.com guide (50 RPM / 500K TPM $0 tier) — conflicts with user's stated
  200 RPM; treat 200 as possibly a higher plan and verify.
- NVIDIA: developer forum confirms free-tier RPM cannot be raised.
