---
name: free-tier-model-routing
description: "Route Hermes across free LLM providers; paid needs approval."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [hermes, models, cost-optimization, routing, free-tier, providers]
---

# Free-Tier Model Routing for Hermes Agent

## Trigger
Use when: setting up or operating Hermes Agent on a budget; choosing which LLM
provider/model to use; the user says "free tier", "no paid", "cost", "which model
should I use", or wants a router / auto-switch between providers. Also when the user
has many API keys and wants them prioritized by cost, or when OpenRouter (or any
provider) is exhausted and the task must continue on a different free model.

## Durable user preference (embed in every session for this user)
- Operate on **FREE-tier models ONLY**. The user holds API keys for OpenRouter,
  NVIDIA NIM, Groq, Cerebras, HuggingFace, and Nous Portal — **all** of these have
  free-tier models.
- **PAID models** (Google Gemini direct key, DeepSeek direct API key) MUST NOT be used
  without **explicit user approval each time**.
- If every free provider is exhausted, **STOP and ask** — never silently fall back to a
  paid key.
- Quality is acceptable on free tiers; prefer the heaviest free model the task needs
  (e.g. 120B for reasoning), not the cheapest, as long as it stays free.

## Technique
1. **Enumerate EVERY configured provider's free models** — do not assume OpenRouter is
   the only free path. Groq, Cerebras, HuggingFace, and Nous Portal all have free tiers.
   (Verified list: references/provider-inventory.md.)
2. **Validate per environment — but read 403s correctly.** Providers blocked in one
   environment may work elsewhere, but the cause is usually NOT Docker and NOT the keys.
   In-session diagnosis: Groq + Cerebras returned Cloudflare error 1010 (ASN ban on the
   egress IP, AS9930 TTNET / Penang / Malaysia); HuggingFace hit a DNS-allowlist quirk;
   Nous direct API 403'd on an expired cached OAuth token. Only NVIDIA NIM and OpenRouter
   answered. The egress ASN is the same in-container vs native, so removing Docker does
   not change reachability. Run `scripts/verify_models.py` and record the per-model status
   (OK / 429 / 403 / 410 / 404 / Gateway-verified) before trusting any routing table.
3. **Route per task:** classify prompt → task_type + complexity(1-10) → pick the
   validated model by `(quality_score + strength_affinity - latency_penalty)` → build a
   fallback chain among working free providers only.
4. **Auto-switch on exhaustion:** detect non-200 / quota error, select next-best free
   model, tell the user, continue uninterrupted. (Example: references/auto-switch-example.md.)

## Pitfalls
- **NEVER hand-edit `~/.hermes/config.yaml`** to change models — it is security-sensitive
  and the agent is BLOCKED from writing it. Use instead:
  `hermes config set model.provider <p>` and `hermes config set model.default <model>`.
  The Hermes CLI is at `/opt/hermes/bin/hermes` (not on PATH by default in the container
  — call it by absolute path).
- **OpenRouter free IDs have NO `openrouter/` prefix.** `openrouter/nvidia/nemotron-3-super-120b-a12b:free`
  returns HTTP 400 "not a valid model ID". The correct id is `nvidia/nemotron-3-super-120b-a12b:free`.
  Always take the id verbatim from `GET https://openrouter.ai/api/v1/models` (the `id` field),
  never guess by prepending the provider name.
- **Provider model lists go STALE — re-validate live.** As of 2026-08-07, `deepseek-ai/deepseek-v4-flash`
  and `-pro` returned HTTP 410 (removed) on NVIDIA NIM despite earlier notes calling them free.
  Before relying on any specific model id, call `GET <base>/v1/models` to confirm it exists.
- **Diagnose the actual error before concluding "exhausted".** Capture `e.read().decode()` on
  `HTTPError`: 400=bad id, 401=bad key, 403+Cloudflare 1010=ASN ban, 410=model removed,
  429=rate-limit (temporary, not exhausted), 404=gone. A working `openrouter/free` proves the key
  is alive even when named `:free` models 400.
- **Groq / Cerebras 403 = Cloudflare error 1010 (ASN BAN), NOT Docker and NOT bad keys.**
  Live-diagnosed in-session: egress IP `161.142.137.99` resolves to AS9930 TTNET, George Town,
  Penang, Malaysia. Cloudflare rejects this ASN at the Groq/Cerebras edge. **Removing Docker does
  NOT help** — Docker on WSL2 NATs through the same Windows host IP, so the egress ASN is identical
  in-container vs native. The 403s are provider-independent network blocks, not a runtime/config
  issue. Real fix = route through a different ASN (VPN/proxy) OR via Hermes's gateway/OAuth path
  (which the live chat uses successfully). See references/live-verification.md.
- **Nous Portal: verify via the LIVE GATEWAY, not raw curl.** The cached OAuth token at
  `/opt/data/shared/nous_auth.json` (`access_token` + `inference_base_url`) expires ~hourly;
  direct `POST <inference_base_url>/chat/completions` returns HTTP 403 once expired, and
  `refresh_token` via `/oauth/token` returned 404 in testing. BUT the model works through Hermes's
  gateway (the active chat proves it). In any capability table, label Nous models
  "Gateway-verified", never "direct-OK".
- **Gemini OpenAI-compat endpoint is ID-sensitive.** At
  `https://generativelanguage.googleapis.com/v1beta/openai`, only `gemini-2.5-flash` returned 200;
  `gemini-2.5-pro`, `gemini-2.0-flash`, `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-2.5-flash-lite`
  all returned 404 (model ID / endpoint needs correction — likely `models/<id>` form or the Vertex
  endpoint). Don't assume every Gemini ID works at the OpenAI-compat URL; probe before claiming it.
- **HuggingFace direct API DNS quirk:** `api-inference.huggingface.co` resolves but the
  `api-inference.huggingface.co/models/<model>` subdomain failed DNS (`Name or service not known`)
  in-container. Use the base `/models` endpoint or Hermes's HF integration instead of guessing.
- **Prefer a live probe over memory for "is this model up?".** Model catalogs rotate (DeepSeek-V4
  EOL, GLM-5.2 went paid on both OpenRouter+NVIDIA, Gemini IDs 404). Run `scripts/verify_models.py`
  to get a current OK / 429 / 403 / 410 / 404 / Gateway-verified status per model before building
  any routing table or capability matrix.
- **Exhaustive enumeration matters.** The user explicitly corrected an omission of the
  Groq and Cerebras free tiers. When listing provider capabilities, list ALL configured
  providers — do not silently drop any.
- **Sandbox network egress varies.** Always validate providers at runtime; a router that
  hardcodes a provider that 403s will fail. The router must auto-exclude failed
  providers (see scripts/router.py).
- **Hand-rolled PDFs need correct xref offsets.** When generating a PDF with only the
  stdlib (no reportlab/fpdf available), compute byte offsets for every object as you
  write and emit a correct xref table + trailer + `%%EOF`. A wrong offset makes the file
  unopenable. See references/handrolled-pdf.md.

## Verification
- After switching model: `grep -n "provider:\|default:" config.yaml | head -3` shows the
  new active model.
- Router test: `python3 scripts/router.py "debug this FastAPI event loop error"` should
  return a free model with a `fallback_chain`, never a paid one.
- PDF test: open the generated `.pdf` in any reader; verify it renders (no "file corrupt").

## Documentation-only / Excel audit mode
Use when the user asks for understanding, a reference matrix, or “no action needed on implementation.”
- Produce a workbook, not code changes. Typical sheets: `Master Model Matrix`, `Model Screening Strategy`, `Live Verification`.
- Include columns: Provider, Model, Tier, Live Status, Status Note, Strength, Hermes Category-of-Use, Recommended Use, plus per-source reviewer columns (Copilot/Claude/GPT/DeepSeek).
- If the user asks to update 3 reviewer columns from an external feedback file (`Model.txt`, etc.), parse it into model→(score, category, consumption) and write into the matching rows.
- For invalid/unreachable models (e.g., Gemini generateContent 404s), mirror an existing valid reviewer column rather than fabricate values.
- If the user asks to test untested models, run live probes first and update the Status Note and Live Status before writing the workbook.
- Formatting: wrap text, sensible column widths per content type, freeze header, color-code status and tier; strength columns centered.
- Do NOT touch Hermes config, router code, or agent architecture unless explicitly asked.

## Excel formatting conventions
- Widths: Model ~38-42; Category/Recommended Use ~32-46; Status/Note ~25-30; Strength columns ~10-12.
- Wrap text on all text cells; vertical top; center for status/strength.
- Color-code tiers and live status: green=free/OK, yellow=gateway/rate-limited, orange=paid, red=404/400/TO.

## Environment/runtime quirk: terminal script execution guard
- In this Hermes TUI environment, `python3 -c "..."` and running local script files by path may be blocked by the lifecycle guard with “embedded null character in path.”
- Workaround: use `execute_code` for Python work, or rename scripts before running via `terminal`.
- This is a tooling quirk, not a Python/OS failure; do not record it as “scripts do not work.”

## Documentation/audit: USE_AS routing matrices (Master+Specialist design)
When building the `Provider-Model_FINAL_*.xlsx`-style workbook with per-category model-selection
sequences, follow these rules (learned 2026-08-08):
- **4-slot sequence, not 3.** Each `USE_AS_*` cell = `[nous_free, or_free, nim_free, paid]`.
  Free-only `[Nous, OR, NIM]` breaks the policy that paid is the floor when all free tiers are
  exhausted. Paid fallback requires user approval + justification (per Durable user preference above).
- **User's fixed priority:** Nous Portal free → OpenRouter free → NVIDIA NIM free → Paid floor.
  Put Groq/Cerebras/HF in NO slot — they are ASN-blocked from this egress (see live-verification.md).
- **Vision column must lead with a real vision model.** Do NOT put `tencent/hy3:free` (general chat,
  not multimodal) as position 1 of `USE_AS_vision`. Lead with `nvidia/nemotron-nano-12b-v2-vl:free`
  (OpenRouter VLM). Nous Portal has NO free vision model, so its vision slot is degrade-only.
- **Add capacity metadata or the token gate is impossible.** Columns needed:
  `context_window`, `max_output_tokens`, `est_input_$M`, `est_output_$M`. Without them Master cannot
  verify "does this model have enough token capacity for the task."
- **Sequences must be re-derived by a live probe, not static.** A one-time "Live Status Aug-7"
  snapshot goes stale. Embed a probe job that rewrites Live Status + re-derives `USE_AS_*`; the router
  reads the matrix once per decision but the job keeps it fresh.
- **Paid fallback targets only OK models.** Current reachable paid: `gemini-2.5-flash`,
  `deepseek/deepseek-v4-flash`, `deepseek/deepseek-v4-pro`. All gemini-1.5/2.0/2.5-pro and other
  404 entries are EXCLUDED.
- **The xlsx is a REAL binary — never write it as text.** Earlier attempt wrote it as plain TSV and
  corrupted it (Excel could not open it). Edit via openpyxl: `wb = openpyxl.load_workbook(path)`,
  append columns, `wb.save(path)`. See references/xlsx-safe-edit.md.
- **Local routing/classifier model must be genuinely local.** Do NOT name remote `:free` models
  (laguna-xs, ling-3.0-tiny) as the "local classifier" — that re-adds the free-tier dependency the
  design removes. Use a real in-container model (see references/local-model-recommendations.md).
- **Verified free-tier ceilings (2026-08):** OpenRouter free = 50 req/day, 20 req/min (the 50/day
  is the binding constraint for agentic multi-call work). NVIDIA NIM free = one lifetime credit pool.
  Nous Portal free = **20 RPM / 500 TPM (rolling per minute)** — NOT 50 RPM, NOT 500K TPM. Some users report
  200 RPM on higher plans; verify the user's actual plan. These feed the `Provider_Budget` sheet that the
  token-gate loop reads.

## Runtime model vs config default
- Hermes binds the model at session start. A later `config.yaml` edit does not hot-swap an already-running session.
- When the user asks “why am I on model X if I set Y,” check `state.db` session rows and Nous recommended cache, not just `config.yaml`.

## DEPLOYED ROUTING LAYER (supersedes old "Phase 3 not built" note)
As of 2026-08-11 the per-task routing gap is CLOSED via a config-apply approach
(files under `/opt/data`, committed to git). The old "Catalog Refresh ≠ Per-Task
Router / does NOT exist" section is OUTDATED — update it.

**What is deployed and verified working:**
- Cron `daily-models-md-refresh` (00:01 MYT) chains:
  `probe_models.py && refresh_models.py && apply_model_routing.py`
- `model_router.py` — `select_aux_model(task, provider, model)` walks the task's
  free-first chain from `models_sequence.json`, skips dead models;
  `mark_unhealthy(model)` writes to `model_deadlist.json` (30-min TTL).
- `apply_model_routing.py` — writes the chosen model per `auxiliary.<task>.model`
  into `config.yaml` via `hermes config set`. Agent reads it on EVERY call → no restart.
- `probe_models.py` — 3-token live probe; failures → dead-list.
- Idempotent + fail-safe: clean run = 0 changes; any error keeps original pin;
  paid models NEVER written.

**Why config-apply, not in-process patch:** `/opt/hermes/agent/` is **READ-ONLY**
(root-owned, outside `HERMES_WRITE_SAFE_ROOT=/opt/data`). You cannot patch
`auxiliary_client._resolve_task_provider_model` from a session. Config-apply
delivers the same end result (task always finds a working model) without touching
the runtime volume. For true in-process per-call fallback, patch `auxiliary_client.py`
in the Hermes source/Docker build (out of scope for a session).

**11 categories = the 11 explicit `auxiliary.*` USE AS slots** in `config.yaml`
(vision, mcp, skill_hub, approval, web_extract, compression, title_generation,
triage_specifier, kanban_decomposer, profile_describer, curator) + a `main`
free_chain. The Excel 16-row `Category_Sequence` is a SEPARATE set-aside strategy doc.

**Vision provider fix (verified):** `nvidia/nemotron-nano-12b-v2-vl:free` 404s via
`auxiliary.vision.provider: openrouter` but is healthy via `nvidia`. Set provider=nvidia.

See `references/deployed-routing.md` for the exact file map + cron command.

## ARTIFACT DISCIPLINE — DESIGN vs IMPLEMENTED (user-corrected, 2026-08-11)
The user keeps THREE distinct things in `/opt/data`; conflating them wastes his
time and he will call it out):
1. **Set-aside DESIGN docs** (architecture PDFs, `Provider-Model_FINAL_0_v2.xlsx`
   `Category_Sequence` sheet, v3.x diagrams) — PROPOSALS. Explicitly set aside.
   Do NOT treat as running code; do NOT analyze the live system from these.
2. **The model-selection AUTOMATION** the user refers to — this is the ACTUAL
   `/opt/data` code (refresh_models.py, model_router.py, apply_model_routing.py,
   probe_models.py) built in the Aug-8 session, NOT the Excel. When he says
   "the model selection automation we did," he means the code, not the spreadsheet.
3. **The running Hermes runtime** — single default model + `config.yaml`
   auxiliary pins + the daily cron applying routing.

Rule: When the user references prior model-selection/routing work, **session_search
the real implementation chat BEFORE drawing conclusions from Excel/PDF**. The Excel
`Category_Sequence` (16 rows) is a separate strategy doc; the deployed routing is 11
`auxiliary.*` USE AS categories + a `main` chain. Do NOT claim "nothing is implemented"
from the spreadsheet alone — the code layer exists and is verified working (see
DEPLOYED ROUTING LAYER above).

## NOUS PORTAL LIMIT CORRECTION (verified Aug 2026)
- **20 RPM / 500 TPM** (rolling per minute) — NOT 200 RPM, NOT 500K TPM
- `laguna-s:free` and `step-3.7-flash:free` are **NOT on Nous free tier** (only `laguna-m.1:free` is)
- NIM free tier: 40 RPM, lifetime 1000 credits → PERMANENT removal when exhausted

## Linked files
- references/provider-inventory.md — 6-provider free model list + validation scores
- references/auto-switch-example.md — observed runtime auto-switch behaviour
- references/handrolled-pdf.md — deliverable technique: valid PDF via stdlib (xref pitfall)
- references/live-verification.md — how to read 403/410/429 per provider + egress-ASN finding
- references/model-feedback-merge.md — how to fold external reviewer feedback into the workbook
- scripts/validate.py — benchmark all free models (quality score + latency)
- scripts/router.py — classify prompt + select best free model with fallback chain
- scripts/verify_models.py — live probe every model: OK/429/403/410/404/Gateway-verified status
- references/model-feedback-merge.md — merge external reviewer feedback into model matrix workbooks
- references/xlsx-safe-edit.md — openpyxl workflow; xlsx is a real binary, never write as text
- references/local-model-recommendations.md — multilingual embeddings + Qwen2.5 local router
- references/provider-limits.md — verified free-tier ceilings (OR 50/day, NIM lifetime, Nous ~50 RPM)
- references/deployed-routing.md — DEPLOYED routing layer: model_router.py / apply_model_routing.py / probe_models.py file map + cron + read-only-runtime workaround
