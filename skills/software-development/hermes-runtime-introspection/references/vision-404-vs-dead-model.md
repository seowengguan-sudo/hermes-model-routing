# Transient Errors vs. Dead Models (vision routing case study)

A 404 on `vision_analyze` does **not** prove a model is dead.

## The case (this session)
- `auxiliary.vision.provider: openrouter` + model `nvidia/nemotron-nano-12b-v2-vl:free`
  → `vision_analyze` returns `404 "Couldn't find that, sorry"`.
- Same model via `provider: nvidia` (id `nvidia/nemotron-nano-12b-v2-vl`) → **200 OK, image read**.
- `stepfun/step-3.7-flash` on OpenRouter → 404 (text model, no vision).

## Diagnostic recipe
1. Is the endpoint reachable with this key?
   `GET https://integrate.api.nvidia.com/v1/models` → 200 == key+endpoint fine.
2. Is the **model id** exactly right? Compare against `/v1/models` names.
   Real id: `nvidia/nemotron-nano-12b-v2-vl` (note **v2**, no `:free`).
3. A 404 from provider A is NOT proof the model is gone — try provider B.

## Self-fix pattern
- Set `auxiliary.<task>.provider` to the provider whose endpoint exposes the model.
- Use the **bare catalog id** (NVIDIA drops the `:free` suffix).
- `probe_models.py` checks reachability; if its "OK" feels wrong, re-probe both
  the `/v1/models` list and a chat-completions call.

## Why this matters
Trusting a transient 404 as "model dead" leads to wrong fallbacks and wasted time.
Verify endpoint + id first. See `hermes-runtime-introspection` skill.
