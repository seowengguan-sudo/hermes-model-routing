# Model Selection — Real Runtime Architecture (verified Aug 2026)

Source of truth: `/opt/data/config.yaml` (`hermes config get auxiliary`) and
`/opt/hermes/agent/auxiliary_client.py`. Do NOT conflate with the SET ASIDE
v3.x Excel design (`Provider-Model_FINAL_0_v2.xlsx`, `Category_Sequence` sheet).

## Two layers, not one
1. **Main loop** — single pinned model (`model.default` + `model.provider`).
   NO per-task routing. Switches only via config edit or the self-heal cron.
2. **Auxiliary tasks** — per-task routing IS live, driven by
   `config.yaml auxiliary.<task>`. `auxiliary_client.py` resolves the model
   at call time. This is where capability-matched model selection lives.

## The 11 explicitly-assigned auxiliary USE AS slots (verified live config)
| USE AS task | Model | Provider |
|---|---|---|
| vision | nvidia/nemotron-nano-12b-v2-vl:free | openrouter |
| web_extract | tencent/hy3:free | nous |
| compression | tencent/hy3:free | nous |
| skills_hub | tencent/hy3:free | nous |
| approval | tencent/hy3:free | nous |
| mcp | poolside/laguna-s-2.1:free | openrouter |
| title_generation | tencent/hy3:free | nous |
| triage_specifier | poolside/laguna-xs-2.1:free | openrouter |
| kanban_decomposer | tencent/hy3:free | nous |
| profile_describer | tencent/hy3:free | nous |
| curator | tencent/hy3:free | nous |

## 7 auxiliary tasks set to `provider: auto` (use main model)
`memory_query_rewrite`, `tts_audio_tags`, `goal_judge`, `monitor`,
`background_review`, `moa_reference`, `moa_aggregator`.

→ So "11 categories" in `refresh_models.py` == the 11 explicitly-assigned USE
AS slots. The Excel's 16 was a FLAT mix of main-loop + auxiliary; the script
splits them into a `main` chain (reasoning/coding/prof-doc/general-chat/aux)
+ 11 auxiliary categories. The 5 "missing" Excel rows (reasoning, coding,
professional-documentation, general-chat, auxiliary) live in the separate
`main` chain, NOT inside the 11.

## Running automation (deployed, not design)
- Cron `daily-models-md-refresh` runs `python3 /opt/data/refresh_models.py` at
  **00:01 MYT** daily.
- Generates: `/opt/data/models.md` (catalog), `/opt/data/models_sequence.json`
  (11 cat + main chain free-first lists + paid fallback gated).
- `self_heal_main_model()`: if pinned main model leaves the free catalog,
  re-pins next free via `hermes config set`.
- This is the REAL Aug 5-8 work. The SET ASIDE v3.x artifacts are separate.

## Critical gaps (honest boundary — NOT yet built)
- `models_sequence.json` is DORMANT — no runtime consumer reads it. Phase 3
  Model Gateway unbuilt.
- NO aux-level health-check/fallback: if a pinned aux model 404s, no automatic
  next-model attempt. Verified this session: `vision_analyze` on
  `nemotron-nano-12b-vl` returned `404 No endpoints found that support image
  input` (egress ASN block — same class as Groq/Cerebras 1010).
- "Never says no capability" is NOT guaranteed until aux fallback + Gateway
  exist. The foundation (config + catalog + sequence JSON) is in place; the
  runtime consumer that turns it into always-picks-a-working-model is missing.

## Distinction to keep sharp
- DESIGN (SET ASIDE): v3.x multi-agent architecture, Excel `Category_Sequence`
  (16 flat rows), `Provider-Model_FINAL_0_v2.xlsx`.
- REAL (running): single main model + 11 auxiliary USE AS config slots + daily
  `refresh_models.py` cron.
