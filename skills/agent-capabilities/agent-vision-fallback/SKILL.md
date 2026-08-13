---
name: agent-vision-fallback
description: Read images via a VLM sub-agent.
triggers:
  - Agent must read a screenshot/diagram/photo but the active chat model has no native vision.
  - Built-in vision_analyze returns 404 or "no image capability" / "Couldn't find that".
  - User asks to "see"/read/transcribe an image and the configured vision model is wrong or unreachable.
---

# Agent Vision Fallback (VLM sub-agent)

## Why this exists
The reasoning model may have no native vision. The built-in `vision_analyze`
tool routes the configured VLM through `auxiliary.vision.provider` — if that
provider is wrong it 404s. This skill makes the agent read images RELIABLY by
calling a VLM directly via API and consuming its TEXT output. The VLM acts as a
sub-agent; the agent "sees" via returned text (no native multimodal input needed).

## Working pattern (vision_bridge.py shape)
1. Pick a multimodal (vision) model reachable from the egress.
2. Read the API key from a local `.env` (never hardcode, never echo to output).
3. Base64-encode the image; send as a data-URL in a chat-completions call.
4. Return the VLM's caption/transcription as TEXT to the agent.

## VERIFIED provider/model facts (critical — these 404 if wrong)
- **NVIDIA NIM**: model id is `nvidia/nemotron-nano-12b-v2-vl` (WITH `v2`).
  `nvidia/nemotron-nano-12b-vl` (no v2) → 404. NVIDIA catalog does NOT use the
  OpenRouter `:free` suffix — bare id only.
- **Endpoint**: `https://integrate.api.nvidia.com/v1/chat/completions`
  (key from `NVIDIA_API_KEY` in `.env`). Returns 200 with the correct id.
- **OpenRouter**: routing `nvidia/nemotron-nano-12b-v2-vl` through OpenRouter
  returns 404 ("Couldn't find that") — the VLM only lives on NVIDIA's endpoint.
  So `auxiliary.vision.provider` MUST be `nvidia`, not `openrouter`.
- **Gemini** (PAID, needs explicit per-use approval): `gemini-2.5-flash` is
  multimodal and reachable from this egress; far more accurate than the free
  NVIDIA VLM (less drift). Use only with approval.

## Pitfalls
- Setting `auxiliary.vision.model` to a TEXT model (e.g. `stepfun/step-3.7-flash`)
  → vision_analyze 404s / no capability. The model MUST be a VLM.
- The `:free` suffix from OpenRouter configs breaks NVIDIA calls. Normalize keys.
- Free NVIDIA VLM is non-deterministic (≈1-in-3 drift / off-topic). For reliable
  OCR, prefer Gemini (paid, approved) or retry-and-pick-best.
- OpenRouter free models intermittently 404 even for valid ids ("couldn't find
  that") — not always a config error. Retry before concluding.

## Verification
Call the VLM on a known image; assert expected text appears (e.g. a known
username). See references/nvidia_vlm.md for the exact request shape.

## User protocol (embed in every build for this user)
- DESIGN DIGEST + open questions BEFORE writing any script; wait for explicit 'go'.
- Close with an HONEST RESIDUAL (design ≠ running system unless built + tested).
- Acknowledge the validity of the user's thinking before counterpoints.
- MATCH SCOPE TO THE PROBLEM: a one-line config fix does not need a library.
