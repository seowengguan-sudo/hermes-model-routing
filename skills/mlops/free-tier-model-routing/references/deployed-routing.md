# Deployed Model-Selection Routing Layer (Hermes Agent)

Captured 2026-08-11. Supersedes the old "Phase 3 not built" claim in the parent
SKILL.md. The per-task model-selection consumer is now BUILT and DEPLOYED.

## File map (all under /opt/data, committed to local git)

| File | Purpose |
|------|---------|
| `refresh_models.py` | Daily catalog fetch → writes `models.md` + `models_sequence.json` (11 categories + `main` free_chain). Idempotent. |
| `model_router.py` | Library. `select_aux_model(task, provider, model)` → best *available* free model for an aux task from the sequence JSON; skips dead models. `mark_unhealthy(provider, model)` → `model_deadlist.json` (30-min TTL). `select_main_model()`. FAIL-SAFE: any error returns the original configured model. |
| `apply_model_routing.py` | Reads the sequence, writes the chosen model per `auxiliary.<task>.model` into `config.yaml` via `hermes config set`. Idempotent (0 changes on a clean run). Paid models NEVER written. |
| `probe_models.py` | 3-token live health probe per model (OpenRouter/Nous/NVIDIA endpoints); failures → `model_deadlist.json`. |
| `models_sequence.json` | Daily catalog. 11 categories = the 11 explicit `auxiliary.*` USE AS slots + `main` free_chain. |
| `model_deadlist.json` | `{model: expiry_epoch}` — models to skip for 30 min. |

## Cron (name: daily-models-md-refresh, schedule 1 16 * * * = 00:01 MYT)
```
cd /opt/data && python3 probe_models.py && python3 refresh_models.py && python3 apply_model_routing.py
```
Deliver: local (no notification). State: scheduled, enabled.

## Why config-apply instead of in-process patch
`/opt/hermes/agent/` is **READ-ONLY** in the running container (root-owned,
outside `HERMES_WRITE_SAFE_ROOT=/opt/data`). `patch`/`write_file` to that path
returns "Write denied". The agent reads `config.yaml` per aux task on EVERY call,
so writing the resolved model there is functionally equivalent to in-process
routing — and it survives container rebuilds (HERMES_HOME=/opt/data persists).

For TRUE in-process per-call fallback (instant within one session, no waiting for
cron), patch `/opt/hermes/agent/auxiliary_client.py`:
- In `_resolve_task_provider_model()` return path, call
  `model_router.select_aux_model(task, provider, model)`.
- In the transient-retry failure path, call
  `model_router.mark_unhealthy(provider, model)`.
This requires editing the Hermes source / Docker image build — not a session action.

## Verified facts this session
- Vision VLM `nvidia/nemotron-nano-12b-v2-vl:free` 404s via
  `auxiliary.vision.provider: openrouter` but is HEALTHY via `nvidia`.
  Fix: `hermes config set auxiliary.vision.provider nvidia`.
- All 7 probed free models reachable from this egress (Nous ASN note still
  applies to Groq/Cerebras, but NVIDIA/OpenRouter/Nous free models answer).
- `apply_model_routing.py` is idempotent: after fixing vision provider, re-run = 0 changes.

## How to extend
- New aux category: add key to `models_sequence.json` categories + map in
  `apply_model_routing.py` TASK_TO_CATEGORY + `model_router.py` _TASK_TO_CATEGORY.
- New provider probe: add endpoint+env to `probe_models.py` _PROVIDERS.
