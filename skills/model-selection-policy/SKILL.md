---
name: model-selection-policy
description: Enforce free-first, limit-aware, approval-gated model selection across 11 usage categories + main loop. Daily refresh gate. Auto-fallback on rate-limit. Learning loop via perf log. Use at session start and before any model-dependent task.
---

# Model Selection Policy (procedural)

This skill governs HOW the agent picks models for every task. It is a **procedure** the
agent follows — not a runtime patch. It maximizes free-tier usage, auto-advances on
rate-limit, and gates paid models behind explicit user approval.

## Files (all under /opt/data)
- `models.md` — live catalog (free tiers per provider). Refreshed daily.
- `models_sequence.json` — 11 categories + main chain, free-first priority lists.
- `model_state.json` — local proxy counters (RPM/TPM/credit), exhausted flags.
- `model_perf_log.md` — outcome records for the learning loop.

## GATE 1 — Daily refresh (once per active day, before any task)
At session start / before the first model-dependent task:
1. Read `models.md` header `Last refreshed:` date.
2. If it is NOT today → run `python3 /opt/data/refresh_models.py` (overwrites both
   `models.md` and `models_sequence.json`). This resequences all categories against the
   live catalog + limits. One refresh max per day.
3. If the cron (12:01 AM MYT) already ran today, skip — the stamp matches.

## GATE 2 — Per-category model pick (before using a model)
For the task's usage category (vision / mcp / skill_hub / approval / web_extract /
compression / title_gen / triage_specifier / kanban_decomposer / curator /
profile_describer) OR the main loop:
1. Load the category's sequence from `models_sequence.json`.
2. Walk the **free list** (1st → 2nd → 3rd …):
   a. Check `model_state.json` for that model: if `exhausted==true` (limit hit) → skip to next.
   b. Else use it. Increment `req_count` and estimate `token_count` in state.
   c. If a 429/limit error returns → set `exhausted=true` (rolling) for Nous/NIM RPM/TPM,
      or for NIM add estimated credits; advance to next free model.
3. If ALL free options exhausted/inadequate for task complexity:
   a. Propose the `paid_fallback` (Gemini if category suits vision/multimodal, else
      DeepSeek-v4-flash). **Never deepseek-v4-pro** without approval.
   b. STOP and `clarify` the user with clear reasons + estimated cost.
   c. Only on explicit approval, use the paid model and track estimated spend in state.

## MAIN LOOP (free-first chain, no paid)
- Sequence: hy3:free → nemotron-3-ultra:free → laguna-s:free → nemotron-3-super:free → ling-tiny:free.
- On exhaustion of current main: agent edits `config.yaml` `model.default` to next free
  in chain for the NEXT session (seamless, no approval — all free).
- Paid is NEVER auto-selected for main. If all free exhausted, tell user (wait for reset
  or approve paid).

## LIMIT RULES (from user)
- **Nous Portal:** 20 RPM / 500 TPM (rolling per minute). Exhausted → skip to next free.
- **NVIDIA NIM:** 40 RPM, **lifetime 1000 credits**. When `credit_used ≥ 1000` → set
  `exhausted=true` AND append model to `nim_removed_models` in state → it is PERMANENTLY
  removed from all sequences (never chosen again).
- **OpenRouter:** resets MYT 08:00 daily; heavy paid models → watchdog warns on token burn.
- **DeepSeek / Gemini (paid):** estimate spend = tokens × published price; warn before
  large calls. User verifies real balance.

## PAID RULES
- Paid fallback = Gemini if category suits it (vision/multimodal), else DeepSeek-v4-flash.
- **deepseek-v4-pro: NEVER auto. Requires explicit user approval.**
- Always `clarify` with reasons before any paid engagement.

## LEARNING LOOP
After each task using a model, append to `model_perf_log.md`:
`[ts] category=X model=Y quality=(good|ok|poor) reason=...`
- quality=poor → on next daily refresh, demote that model for that category in
  `models_sequence.json` (move down the free list). Over time the sequences sharpen.

## OBSERVABILITY NOTE (honest boundary)
The in-app ModelsPage reads the static catalog + live probe; it does NOT live-animate
per-category active models or mid-session switches. Switching is observable via:
- `model_state.json` (which models were used/exhausted),
- `model_perf_log.md` (outcomes),
- a clear runtime message when the agent advances/falls back,
- and the `config.yaml` reflecting main-model change after next reload.

## NON-GOALS
- No automatic prompt-splitting across many models (that is the set-aside v3.x design).
- No runtime patch to Hermes boot. This skill is procedural only.
- `config.yaml` is only edited by the agent for main-model free→free fallback, or when
  the user explicitly approves applying the auxiliary YAML snippet.
