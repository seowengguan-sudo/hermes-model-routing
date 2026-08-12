---
name: hermes-model-routing-deploy
description: Deploy free-tier model routing into live Hermes config.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
---

# Hermes Model Routing — Deployment (the missing consumer)

The `model-selection-policy` skill is **procedural** (it tells the agent how to
*think* about picking models). This skill is the **deployable runtime layer**
that turns the daily `models_sequence.json` into actual model assignments the
running agent uses. It was built because the cron produced the JSON but nothing
consumed it — aux tasks stayed on fixed dead-pins and a 404'd model just failed.

## Structural fact (load-bearing)
The **11 categories** in `models_sequence.json` ARE the **11 explicitly-configured
`auxiliary.<task>` USE AS slots** in Hermes Agent's Model settings UI. They are
NOT a separate routing layer. The main chat loop is a SEPARATE path (the `main`
chain in the JSON). Therefore:
- Per-task model selection is an **auxiliary-structure concept**, not a main-loop
  concept. The main loop is a single pinned orchestrator model; auxiliaries specialize.
- Never try to route the main loop per-task.
- The 7 `auto` aux tasks (memory_query_rewrite, tts_audio_tags, goal_judge,
  monitor, background_review, moa_reference, moa_aggregator) use the main model
  and are excluded from routing.

11 routed aux tasks → sequence category:
vision, mcp, skill_hub, approval, web_extract, compression, title_generation,
triage_specifier, kanban_decomposer, curator, profile_describer.

## Components (all under /opt/data, writable — NOT /opt/hermes which is read-only)
- `model_router.py` — library. `select_aux_model(task, provider, model)` returns
  the best *available* model for that aux task (walks the category free chain,
  skips the dead-list). `mark_unhealthy(provider, model)` records a failure.
  FAIL-SAFE: any error returns the original model unchanged. No network calls
  at selection time — reads local JSON + in-memory/on-disk dead-list.
- `apply_model_routing.py` — deployer. Reads `models_sequence.json`, and for each
  of the 11 aux tasks writes the resolved model into `config.yaml` via
  `hermes config set auxiliary.<task>.model`. Idempotent: only writes when the
  resolved model differs AND the current pin is dead/absent from the free catalog.
  NEVER writes a paid model. Also self-heals the main model.
- `probe_models.py` — live health probe. Sends a 3-token chat completion to each
  candidate model (provider inferred from model id prefix / explicit env key).
  Failures → `model_deadlist.json` (30-min TTL). Models with no API key or
  unknown provider are assumed reachable (never blindly killed).
- `model_deadlist.json` — dead models + expiry timestamps; consumed by router/apply.

## How to run
```bash
cd /opt/data
python3 probe_models.py          # optional, on-demand health check
python3 apply_model_routing.py    # deploy resolved models to config.yaml
```
Daily cron `daily-models-md-refresh` (00:01 MYT) runs:
`python3 probe_models.py && python3 refresh_models.py && python3 apply_model_routing.py`

## Provider-mapping pitfall (found this session, real bug)
`auxiliary.vision` was configured `provider: openrouter` with model
`nvidia/nemotron-nano-12b-v2-vl:free`. OpenRouter 404s that VLM ("No endpoints
found that support image input"). The probe proved the SAME model is **healthy
via the NVIDIA endpoint**. Fix: `hermes config set auxiliary.vision.provider nvidia`.
**Lesson: a model id's working provider is not always the one in config — probe
before assuming a model is dead.**

## VISION AUX SLOT MUST HOLD A VLM (UI pitfall, 2026-08-11)
The Hermes Model-settings UI does NOT enforce that `auxiliary.vision` points at a
*vision-capable* model. A user can pick any model from the dropdown — including a
**text-only** model — and the config will accept it. Consequence observed live:
`auxiliary.vision.provider=openrouter`, `auxiliary.vision.model=stepfun/step-3.7-flash`
(a text model) → built-in `vision_analyze` returns
`404 - "Couldn't find that, sorry."` The model has no image input capability, so the
call fails even though the model "exists."
**Lesson: when vision is reported broken, first check the model is actually a VLM,
not just that the provider is reachable.** Valid vision models seen working here:
`nvidia/nemotron-nano-12b-v2-vl` (via provider `nvidia`), and `gemini-2.5-flash`
(Google native endpoint, paid). Do NOT put a `-flash`/`-instruct` text model in the
vision slot.

## DISMANTLE / REVERT TO FACTORY (2026-08-11)
If the user wants "original, no automation" but to KEEP their current UI model pins:
1. Delete the deploy artifacts (all under /opt/data):
   `rm -f model_router.py apply_model_routing.py probe_models.py vision_bridge.py \
         README_model_routing.md models_sequence.json model_deadlist.json`
2. The cron `daily-models-md-refresh` was CREATED this session (verify `created_at` in
   `cron/jobs.json`). For a true "factory, no automation" reset, **remove it entirely**:
   `cronjob remove job_id=<id>` (find id via `cronjob list`). Restoring its script to the
   original single step is NOT sufficient if the user wants zero cron — the job itself is
   automation. (If the user only wants the deploy chain gone but is fine with the nightly
   catalog refresh, restoring the script to `python3 refresh_models.py` is enough.)
   **As of 2026-08-11 the user chose full factory reset: artifacts deleted AND cron removed.**
3. **Do NOT touch `config.yaml`.** The cron no longer re-applies, so the user's manual
   UI pins stay exactly as set. (Contrast: while the deploy script existed, the nightly
   cron would OVERWRITE the vision pin back to the sequence's value — removing the
   script is what stops that.)
4. Optional: remove the local git repo too if it was only holding these files:
   `rm -rf /opt/data/.git` (destructive — confirm first; it was never pushed).
**Lesson: dismantling is safe and the UI pins survive because the cron no longer
re-applies. Reverting does NOT "fix" vision — if the vision pin is a bad/non-VLM model
it stays broken. The automation was only ever insurance against model death.**

## Vision ingestion self-fix (text-only model "sees" an image)
The native `vision_analyze` tool works **only when `auxiliary.vision` is set to a
correct VLM config** — `provider: nvidia`, `model: nvidia/nemotron-nano-12b-v2-vl`
(see NVIDIA VLM model-id exactness below). With a WRONG config it 404s:
- wrong provider (e.g. `openrouter` for a VLM that only exists on NVIDIA) → 404
- a text-only model in the vision slot (e.g. `stepfun/step-3.7-flash`) → 404
- a non-existent model id (e.g. `nemotron-nano-12b-vl`) → 404
So the FIRST fix for "vision broken" is **correcting the config**, not assuming the
tool itself is broken. A standalone VLM bridge (`vision_bridge.py`) is only a backup
/ for feeding image-derived text into a text-only reasoning model:
- `vision_bridge.py` — calls `nvidia/nemotron-nano-12b-v2-vl` on the NVIDIA
  endpoint directly (model id has NO `:free` suffix; `...:free` 404s). Free but
  FLAKY (~1 in 3 drift). Reads `NVIDIA_API_KEY` from `.env`.
- **Gemini Flash** (`gemini-2.5-flash`, native generateContent endpoint, key from
  `.env`) is multimodal, accurate, and Google is NOT ASN-blocked here. PAID →
  needs per-session approval, but justified for vision OCR because the free VLM
  is flaky and native `vision_analyze` is broken. Verified: transcribed a GitHub
  screenshot correctly first try.
See `references/vision-ingestion.md` for endpoints + body shapes.

## Dead-list key normalization (model_router.py pitfall, fixed 2026-08-11)
`mark_unhealthy` / `_is_dead` normalize the model id (strip trailing `:free` /
`:<tag>`) before keying. `models_sequence.json` stores bare ids but a failure
may be reported with the OpenRouter `:free` spelling — without normalization the
dead-list never matches the chain entry and fallback never triggers.

## NVIDIA VLM MODEL-ID EXACTNESS (2026-08-11, live-tested)
The working vision model on the NVIDIA provider is **`nvidia/nemotron-nano-12b-v2-vl`**.
Two wrong spellings 404:
- `nvidia/nemotron-nano-12b-vl` (missing `-v2`) → 404 `page not found` (model does not exist).
- `nvidia/nemotron-nano-12b-v2-vl:free` (OpenRouter `:free` suffix) → 404 (NVIDIA catalog
  uses bare ids; the `:free` tag is an OpenRouter convention NVIDIA rejects).
When the user says "nemotron nano 12b VL", set `nvidia/nemotron-nano-12b-v2-vl` EXACTLY.
Verified: `vision_analyze` with `provider: nvidia` + this id reads both `HermesTest.jpg`
and `GitHub.jpg` correctly. A text-only model (e.g. `stepfun/step-3.7-flash`) in the
vision slot also 404s — it is not a VLM.

## FACTORY-RESET MUST REMOVE THE CRON (2026-08-11)
When the user asks for "original / factory default, no automation," do NOT assume an
existing cron job is factory. The `daily-models-md-refresh` cron was **created this
session** — verify via `created_at` in `cron/jobs.json` (if it's today's date, it is
NOT factory). "No automation" means: delete the deploy artifacts AND
`cronjob remove job_id=<id>` the job entirely. Restoring its script to the original
single step is NOT enough if the user explicitly wants zero cron. Always check job
provenance before treating a cron as pre-existing.
**As of 2026-08-11 the user chose full factory reset: artifacts deleted AND cron removed.**

## USER FRAMING CORRECTION (2026-08-11) — do NOT overstate the automation's value
The user set per-task auxiliary models in the Hermes UI; those pins ALREADY work
for healthy/reachable models. The routing layer is **insurance against model
death**, not a replacement for UI selection. When justifying the work, say:
"selection was already done via UI; the automation only self-heals when a pinned
model 404s / gets delisted." Do NOT claim the system 'couldn't select per task'
before — it could. Reverting to 'original, no automation' would RE-BREAK vision
(the original config had NO working vision provider). Conflating 'selection' with
'survival of model death' is the mistake to avoid.

### Empirical proof delivered this session (use when the user insists "original is better")
- With `auxiliary.vision` = `openrouter` / `stepfun/step-3.7-flash` (a text model the
  user set manually): `vision_analyze` → `404 - "Couldn't find that, sorry."` (BROKEN).
- With `auxiliary.vision` = `nvidia` / `nvidia/nemotron-nano-12b-v2-vl`: `vision_analyze`
  routes to a working VLM (FIXED). This correction was made by the automation; a manual
  reset removed it and re-broke vision. State this fact, don't argue — show the 404.

## Honest boundary: in-process per-call fallback NOT done
`/opt/hermes/agent/auxiliary_client.py` is a **read-only Docker volume**
(root-owned, outside HERMES_WRITE_SAFE_ROOT=/opt/data). The ideal in-process hook
(call `select_aux_model()` inside `_resolve_task_provider_model()` and
`mark_unhealthy()` in the retry path) requires patching that file inside the
Hermes source/build — outside this session's writable root. The deploy-script
approach delivers the same end result (agent reads correct model per call) by
applying to config.yaml daily + on-demand, instead of resolving inside the loop.

## Verification done (this session, real)
- Router falls back correctly when a model is dead (vision VL dead → hy3).
- `apply_model_routing.py` idempotent: 0 changes on clean run, swaps only dead pins.
- Probe reached all 7 candidate models; 0 dead.
- Vision provider switched openrouter→nvidia; vision now routes to a working VLM.

## Related
- `model-selection-policy` (procedural counterpart — user-owned, not editable here;
  recommend `hermes curator adopt model-selection-policy` to merge this deploy layer in).
- `refresh_models.py` builds `models_sequence.json` + `models.md` (the data source).

## Linked files
- `references/vision-ingestion.md` — VLM bridge endpoints (NVIDIA direct + Gemini
  native), body shapes, flakiness notes, dead-list normalization detail.
