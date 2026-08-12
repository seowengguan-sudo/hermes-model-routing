# Self-Heal Main Model — Implementation Contract

Verified working pattern (built + tested 2026-08). Use when a free-tier model pinned in
`model.default` may be removed by the provider.

## Trigger
Run at every model-catalog refresh (cron 12:01 AM MYT, or the stale-check gate on agent start).

## Algorithm (pseudo)
```
MAIN_CHAIN = [  # performance-ordered; (model_id, provider)
  ("nvidia/nemotron-3-ultra-550b-a55b:free", "nous"),
  ("tencent/hy3:free", "nous"),
  ("nvidia/nemotron-3-super-120b-a12b:free", "nous"),
  ("poolside/laguna-xs-2.1:free", "openrouter"),
  ("inclusionai/ling-3.0-tiny:free", "openrouter"),
]
HERMES_BIN = "/opt/hermes/.venv/bin/hermes"

free_ids = {live OpenRouter :free models} | {Nous/NIM curated free ids}

cur = run([HERMES_BIN, "config", "get", "model.default"]).stdout.strip()
if cur in free_ids: return            # still free — no heal
for mid, prov in MAIN_CHAIN:
    if mid in free_ids:
        run([HERMES_BIN, "config", "set", "model.default", mid])
        run([HERMES_BIN, "config", "set", "model.provider", prov])
        log_swap(cur, mid)            # append to model_perf_log.md
        return
# none free: leave as-is; agent reports at runtime
```

## Hard-won facts
- `hermes config get/set` is the ONLY sanctioned write path; direct `config.yaml` file write
  is REFUSED by a guard. The binary is at `/opt/hermes/.venv/bin/hermes` (not on PATH; plain
  `python3` lacks `yaml`).
- Self-heal lands on NEXT session reload, not mid-session.
- After any `config set model.default`, re-pin cron jobs or they "fail closed" (see SKILL.md).
- DeepSeek `/v1/models` returns 401 without a key — fall back to known names, don't invent.

## Test it
Temporarily `config set model.default "tencent/hy3:REMOVED"`, run the refresh script, confirm
it auto-advances to the next free model and logs the swap, then restore the intended primary.
