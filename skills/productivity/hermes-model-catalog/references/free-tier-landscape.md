# Free-tier / paid model landscape (verified 2026-08-10)

## Provider structure
- **Nous Portal** — free catalog in `hermes_cli/models.py`. Free: `tencent/hy3:free` (262K), `nvidia/nemotron-3-ultra-550b-a55b:free` (1M), `nvidia/nemotron-3-super-120b-a12b:free` (262K), `poolside/laguna-m.1:free`, `openrouter/elephant-alpha`, `inclusionai/ring-2.6-1t:free`. `laguna-s` / `step-3.7-flash` are NOT on Nous free.
- **NVIDIA NIM** — 128 models, many free/dev. Highlights: `nemotron-3-ultra` (1M ctx), `nemotron-3-super/nano-30b`, `glm-5.2`, `inkling` (multimodal), `mingling`, `qwen-image`/`qwen-image-edit`, `nemotron-ocr-v2`, `minimax-m3`. Free tier ~40 rpm.
- **OpenRouter** — live `/v1/models`. FREE (prompt=0 & completion=0) verified count 17: includes `nvidia/nemotron-3-ultra-550b-a55b:free` (976K), `poolside/laguna-s-2.1:free` (262K), `laguna-xs-2.1:free` (262K), `gemma-4-26b/31b-it:free`, `inclusionai/ling-3.0-tiny:free`, `cohere/north-mini-code:free`, `openai/gpt-oss-20b:free`, `nemotron-nano-12b-v2-vl:free` (vision). Near-free paid: `deepseek-v4-flash` (~$0.08/1M in, 1M ctx).
- **DeepSeek** — PAID ONLY. `deepseek-v4-flash` (1M, $0.14/1M in miss, $0.28 out; cache hit $0.0028 in), `deepseek-v4-pro` (1M, $0.435 in, $0.87 out). Warns prices will rise. The Hermes `auxiliary.mcp` model is set to this.
- **Google Gemini** — PAID (free trial credit only). `gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`, `gemini-3.1-pro-preview`, `gemini-3-flash-preview`, `gemini-2.5-flash`/`pro`, Nano Banana 2/Pro (image), Omni Flash (video). No permanent free model.

## Gotchas
- Context windows / free flags DRIFT. `poolside/laguna-s-2.1:free` showed 1.05M in one listing but 262K live — never reuse old numbers; re-probe.
- Best free large-context: `nvidia/nemotron-3-ultra-550b-a55b:free` (≈1M) on Nous + OpenRouter.
- External MCP (Linear/Figma/Comfy) bills the EXTERNAL account, NOT Hermes model tokens. Local MCP (Blender/Unreal/n8n-selfhosted) = $0 external.
- The in-app model **dropdown** uses `hermes_cli/models.py` + optional live probe; it is SEPARATE from `models.md`. The dropdown's "refresh" can show stale data — `models.md` is the authoritative daily reference.
