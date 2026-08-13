# Vision Ingestion — reference detail

Captured 2026-08-11, corrected after live testing.

## KEY CORRECTION: `vision_analyze` is NOT inherently broken
The built-in `vision_analyze` tool works **when `auxiliary.vision` points at a
correct VLM config**. With the right config it reads images perfectly:
- `provider: nvidia`, `model: nvidia/nemotron-nano-12b-v2-vl` → both `HermesTest.jpg`
  and `GitHub.jpg` transcribed correctly (verified).
It only 404s on a WRONG config:
- wrong provider (`openrouter` for a VLM that only exists on NVIDIA),
- a **text-only model** in the vision slot (e.g. `stepfun/step-3.7-flash`),
- a non-existent model id (e.g. `nemotron-nano-12b-vl` — missing `-v2`).
**First fix for "vision broken" = correct the config, not assume the tool is dead.**
The bridge below is for feeding image-derived text into a text-only reasoning
model, or as a fallback when `vision_analyze` config is unavailable.

## Fix A — `vision_bridge.py` (free, NVIDIA VLM, direct call)
Standalone script calling the VLM on the **NVIDIA endpoint directly** and
returning the description as TEXT. The reasoning model reads that text.
- Endpoint: `https://integrate.api.nvidia.com/v1/chat/completions`
- **NVIDIA VLM model id MUST be `nvidia/nemotron-nano-12b-v2-vl` (with `-v2`).**
  `nemotron-nano-12b-vl` (no v2) → 404 "page not found"; `...:free` suffix → 404.
  NVIDIA catalog uses bare ids; the `:free` tag is OpenRouter-only.
- Reads `NVIDIA_API_KEY` from `/opt/data/.env` (not env) — keeps key out of args.
- Message: `content` = `[{type:text},{type:image_url,image_url:{url:"data:image/jpeg;base64,<b64>"}}]`.
- FLAKY on free tier: ~1 in 3 calls drift/hallucinate. Not for reading secrets.

## Fix B — Gemini Flash (PAID, reliable, reachable here)
`gemini-2.5-flash` is multimodal + accurate. Google is NOT ASN-blocked from this
egress (Groq/Cerebras/HF 403 on Cloudflare 1010).
- Use the NATIVE endpoint (not OpenAI-compat, which 404s on most Gemini IDs):
  `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=<GEMINI_API_KEY>`
  body: `{"contents":[{"parts":[{"text":"<prompt>"},{"inline_data":{"mime_type":"image/jpeg","data":"<b64>"}}]}]}`
- Reads `GEMINI_API_KEY` from `/opt/data/.env`. Verified live: transcribed a
  GitHub profile screenshot fully + correctly first try.
- PAID → needs explicit per-session approval (free-tier policy). Justified for
  vision OCR because free NVIDIA VLM is flaky and native `vision_analyze` is
  broken on this egress.

## Recommendation
Prefer Gemini Flash for any vision task needing accuracy (OCR, UI text, diagrams).
Use `vision_bridge.py` only as a free fallback when paid is refused. Either way
the reasoning model consumes the VLM's TEXT output.

## Dead-list key normalization (model_router.py)
`mark_unhealthy` / `_is_dead` key on a NORMALIZED id (strip trailing `:free` /
`:<tag>`). `models_sequence.json` stores bare ids but failures may arrive with
the OpenRouter `:free` spelling; without normalization the dead-list never
matches the chain entry → fallback never triggers. Verified fixed 2026-08-11.
