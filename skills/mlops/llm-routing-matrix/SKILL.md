---
name: llm-routing-matrix
description: Build and verify multi-provider LLM routing matrices.
---

# LLM Provider / Model Routing Matrix

Build a decision matrix that maps each task category (USE_AS: vision, auxiliary, mcp, reasoning, coding, compression, approval, …) to an ordered list of candidate models across providers, with real capacity data and a paid fallback. The matrix is the *contract* the router/agent conforms to — produce it (Excel) + the architecture doc (PDF) before any implementation code.

## When to use
- Designing or revising a model-selection matrix (spreadsheet form).
- Documenting the router / agent architecture that consumes such a matrix.
- Triggers: "map each category to the right model", "provider priority", "fallback sequence", "real-time screening", "paid needs approval".

## Core methodology
1. **Gather REAL capability per model**, not just provider name. Each model has an actual role: vision / moderation(safety) / tool-use / coding / reasoning / multilingual / embedding. Source: provider docs, a live probe, or an existing assessor matrix.
2. **Define provider priority tiers** (canonical example: Nous Portal → OpenRouter → NVIDIA NIM → Paid).
3. **Build 4-slot sequences per category**: `[Tier1 free → Tier2 free → Tier3 free → Paid]`.
4. **Use "—" for a slot with NO capable free model at that tier.** Do NOT fill it with the provider's "first model" as a placeholder — that silently breaks the category. The router skips "—" and moves on.
5. **Add capacity metadata columns** to the Master sheet: Context Window, Max Output Tokens, Est $/M In, Est $/M Out — so the Master/router can pre-check token fit before dispatch.
6. **Paid tier is reserved + approval-gated**: default paid model = the cheaper one (e.g. `deepseek/deepseek-v4-flash` or `gemini-2.5-flash`). Reserve the heavy model (e.g. `deepseek/deepseek-v4-pro`) for *super-complex* reasoning / long professional-documentation only. **Every paid call requires explicit UI approval** before execution (notify with justification: which free tiers ran out + token reason + estimated cost; continue on free/degrade; settle on approval).
7. **Encode exhaustion handling**: 429 on a tier → next slot; a lifetime-exhausted tier (e.g. NVIDIA NIM one-time credit) → skip straight to paid, never retry.
8. **Exclude blocked providers** for the deployment ASN (e.g. Groq / Cerebras / HF behind Cloudflare WAF from the user's egress) — never select them.

## Pitfalls (learned the hard way)
- **Capability mismatch** — the #1 error: putting a non-vision model (e.g. `tencent/hy3`) in the *vision* slot, a non-moderation model in *approval*, or a non-tool-use model in *mcp*. Match by capability, not by "it's the first model of the priority provider". If the priority provider has no capable free model for that category, the slot is "—".
- **Duplicate adjacent slots** — slot1 == slot2 (e.g. both `poolside/laguna-s` for kanban). Make adjacent slots distinct (heavy → light: `laguna-s` → `laguna-xs`).
- **Writing .xlsx as plain text / TSV corrupts it** (magic bytes become non-ZIP). Always edit with **openpyxl**. If pip is missing: `uv venv && source hermes-venv/bin/activate && uv pip install openpyxl`. Verify by re-loading + running sanity checks, not by visual open.
- **Static "Live Status"** — a one-time snapshot goes stale. Drive selection from a live quota ledger (per-provider RPM/TPM remaining, daily reset time, lifetime flag) refreshed by a 15-min probe that rewrites status + recomputes sequences.
- **Heavy paid as default** — don't burn v4-Pro on routine work; reserve it for super-complex only.
- **English-only embeddings** — do NOT use `all-MiniLM-L6-v2` (English-only, 384-dim) when clients are multilingual (e.g. Malaysian BM/zh/ta/en). Use a multilingual embedder (`BAAI/bge-m3`) so retrieval ranking isn't silently corrupted.
- **Architecture ↔ Matrix alignment gaps (from Hermes v5 review)**: 
  - Terminology: Architecture's "recipe" = Matrix's `SEQ_*` per category. Unify before Phase 3.
  - Missing Slot 0 (Local): Architecture expects Qwen2.5-1.5B + bge-m3 as first tier; matrix starts at Nous (Slot 1). Add local tier before Nous.
  - Vision SPOF: Only `nemotron-nano-12b-v2-vl:free` on OpenRouter for free vision. Document fallback explicitly.
  - NIM lifetime exhaustion: Router must treat NIM free tier exhaustion as irreversible — no retry, skip to paid.
  - Nous Portal = Gateway-verified only: Label Nous models "Gateway-verified" in matrices; direct API 403s on OAuth expiry.
  - Probe→Router wire: Phase 3 must wire live probe data (15-min TTL) into Model Gateway routing decisions, not just static Category_Sequence.

## Deliverables shape
- **Excel (openpyxl)**: `Master Model Matrix` (capacity cols + 4-slot `SEQ_<category>` columns per row) + `Category_Sequence` sheet (clean per-category 4-slot lookup with notes) + `Provider_Budget` sheet (live quota ledger) + `Router_Control_Loop` sheet (the closed loop spec). Preserve original as `*_original_backup.xlsx`.
- **PDF (reportlab)**: professional architecture doc — problem→solution matrix, corrected provider chain, local-first gate, capacity/budget, real-time screening, exhaustion handling, paid-escalation (approval + reservation), Master degrade-mode, end-to-end walkthrough.

## Verification (run, don't eyeball)
Run `scripts/verify_matrix.py` against the built workbook: it parses each category's 4 slots, flags capability mismatches vs an embedded role map, duplicate adjacent slots, and paid-default violations. See `references/provider-limits.md` for the verified quota numbers and `references/local-models.md` for the local-gate model picks.

## CRITICAL DISTINCTION — Catalog Refresh ≠ Per-Task Router
**What exists today (deployed):**
- Daily cron at 00:01 MYT → `refresh_models.py` fetches live catalogs → writes `models.md` + `models_sequence.json`
- Self-heal: if pinned main model leaves free tier, next daily refresh re-pins via `hermes config set`
- This is a **catalog maintenance layer**, not a runtime router

**What does NOT exist (Phase 3 build target):**
- Per-task category classifier (16-category prompt tagging)
- Real-time probe/fallback chain (15-min TTL health → router)
- Runtime Model Gateway API (`route(category)`) that Hermes calls instead of direct model
- Vision auto-route: `vision_analyze` uses **main model via fast-path** when main is vision-capable (OpenRouter/Nous aggregators). `auxiliary.vision` only engages if main CANNOT see images.
- Mid-session main model hot-swap: config change takes effect on NEXT session start

## NOUS PORTAL LIMIT CORRECTION (verified Aug 2026)
- **20 RPM / 500 TPM** (rolling per minute) — NOT 200 RPM, NOT 500K TPM
- `laguna-s:free` and `step-3.7-flash:free` are **NOT on Nous free tier** (only `laguna-m.1:free` is)
- NIM free tier: 40 RPM, lifetime 1000 credits → PERMANENT removal when exhausted

## References
- `references/provider-limits.md` — verified free-tier limits (Nous 50 RPM*/500K TPM, OpenRouter 20/min·50/day, NVIDIA NIM one-time lifetime), paid 404 exclusions, and the canonical priority chain.
- `references/local-models.md` — why Qwen2.5-1.5B (classify, CPU) + BAAI/bge-m3 (multilingual embed) over English-only MiniLM.
- `scripts/verify_matrix.py` — programmatic sanity checker for the matrix.
