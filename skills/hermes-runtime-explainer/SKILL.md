---
name: hermes-runtime-explainer
description: Explain the real Hermes agent, not designs.
category: software-development
---

# Hermes Runtime Explainer

Use this skill whenever the user asks "how does Hermes work", "how are requests
handled", "how is context/skills/memory/tools constructed", or any
internals question about the agent itself.

## CRITICAL SCOPE RULE (workflow correction from user)
- Explain the **real, current default Hermes agent** — the one actually
  running (single model + tools + session + memory + skills, in a TUI).
- **Keep speculative architecture designs SEPARATE.** If the user has
  co-designed a future architecture (e.g. a v3.6 multi-agent / interrupt /
  metacognition design), do NOT present it as "how Hermes works now" unless
  the user explicitly says to. When they say "set the design aside, explain
  the real agent", obey literally. State the boundary explicitly.
- If asked to explain the designed architecture, label it clearly as
  "design / not yet implemented".

## Output standards (style corrections from user — embed, don't just remember)
- **Legibility first.** When producing diagrams/PDFs/tables: use SATURATED
  fills with WHITE BOLD text, DARK stroke outlines (not thin grey), DARKER
  caption/legend text (#333 not #555). The user explicitly flagged low-contrast
  light tints as "not sharp and not friendly for easy reading". Avoid pale
  washes; prefer navy/blue/green/amber/red/purple saturated palettes.
- **Depth + clarity.** User wants IN-DEPTH, step-by-step, with concrete
  worked EXAMPLES. Favor: numbered step sequences naming each party
  (You / Runtime / Model / Tool backend); annotated diagrams;
  "Party ledger" tables; one-line mental-model summaries.
- **No fluff, no overclaim.** Don't say "flawless / no hallucination /
  totally aware" unless a mechanism enforces it. Close with an honest residual
  (design ≠ running system unless built+executed).

## Durable real-runtime facts (verified from source this session)
See references/runtime_facts.md for the evidence-backed details. Highlights:
- Context = system prompt + injected MEMORY.md/USER.md + skills INDEX +
  conversation HISTORY + new message, concatenated every turn by the runtime.
- Skills live in TWO dirs: bundled `/opt/hermes/skills` (71) AND profile
  `/opt/data/skills` (85, because HERMES_HOME=/opt/data); UI "81" = deduped
  union minus disabled. LobeHub = installed hub skills under `.hub/` +
  read-only marketplace catalog cache. Toolset = a UI grouping tab.
- `execute_code` gets an AUTO-GENERATED `hermes_tools` stub (UDS RPC to
  runtime). Only 7 sandbox-allowed tools importable: web_search, web_extract,
  read_file, write_file, search_files, patch, terminal + helpers
  json_parse/shell_quote/retry. Limits: 5min, 50 tool calls, 50KB stdout.
- `write_file` runs a fail-closed syntax gate BEFORE disk write:
  `.py` → `python -m py_compile`, `.js` → `node --check`; only NEWLY
  introduced errors surfaced (pre-existing filtered). Returns verified:true
  (on-disk hash confirmed).
- Model selection has TWO layers (verified Aug 2026 — see
  references/model_selection_runtime.md):
  (1) **Main loop** = ONE pinned model per session (`config.yaml`
  `model.default`/`model.provider`). NO per-task routing here.
  (2) **Auxiliary tasks** = per-task routing IS live: each `USE AS` slot in
  `config.yaml` `auxiliary.<task>` has its own capability-matched model
  (vision→VLM, mcp→laguna-s, etc.), resolved by `auxiliary_client.py` at
  runtime. The 11 explicitly-assigned slots = the Hermes UI "USE AS" page;
  7 other aux tasks are `provider: auto` (use main model). No autonomous
  free-tier router for the MAIN loop; paid switch only via explicit approval.
- Local tools execute INSIDE the container; Nous only sees call/result TEXT.

## MCP — how it works (real, this session)
User repeatedly asked "how does MCP work inside Hermes", what the 6
"not installed" entries are, whether installing costs tokens, and whether
external info search needs MCP. Embed these answers:
- **MCP is NOT how core tools work.** Native tools (terminal, read_file…)
  are called directly by the runtime — not MCP. MCP is an OPTIONAL bridge:
  (a) Hermes-as-SERVER (`hermes mcp serve`, `mcp_serve.py` exposes
  conversations + selected tools to Claude Code/Cursor/Codex via stdio);
  (b) Hermes-as-CLIENT (your `config.yaml` `mcp_servers:` → Hermes connects,
  calls `list_tools()`, registers them into my toolset; I call them via
  JSON-RPC over stdio/HTTP/SSE).
- **The 6 "not installed" = optional catalog** at `/opt/hermes/optional-mcps/`
  (manifests: blender, comfy-cloud, figma, linear, n8n, unreal-engine).
  They are an app-store-style catalog, NOT required. Confirmed via
  `hermes_cli/mcp_catalog.py:list_catalog()` scanning that dir.
- **Installing does NOT consume free-tier MODEL tokens for the external
  app.** External service uses ITS OWN credential (Linear/Figma/Comfy =
  OAuth to your account; n8n = your API key / self-hosted local). Blender &
  Unreal are local (auth:none) → $0 external. The real Hermes-side cost is
  MODEL CONTEXT tokens: tool schemas injected every turn + large results
  (e.g. n8n workflow-JSON) persisted in history. On a free model that just
  burns free quota faster + accelerates compaction — not a bill.
- **Web search does NOT need MCP.** `web.backend: firecrawl` (use_gateway)
  and `browser.cloud_provider: browser-use` are NATIVE integrations in
  `tools/web_tools.py` / `tools/browser_tools.py`. MCP is unrelated to that.
- Install writes an `mcp_servers.<name>` block into `/opt/data/config.yaml`
  (transport + env + `enabled_tools` curation). `_save_mcp_server` validates
  and REJECTS exfiltration-shaped stdio commands. See references/mcp_facts.md.

## When to load references/
- `references/runtime_facts.md` — the evidence-backed internals (paths,
  function signatures, lint commands). Load when giving a deep explanation.
- `references/mcp_facts.md` — MCP dual-role, the 6 catalog entries with
  auth types, exact config block shape, and token economics. Load when the
  user asks about MCP, the MCP UI page, or "will this cost tokens".
- `references/model_selection_runtime.md` — the two-layer model-selection
  reality (main loop pinned; 11 auxiliary USE AS slots live), the running
  `refresh_models.py` cron, the DESIGN-vs-REAL distinction vs the SET ASIDE
  v3.x Excel. Load when the user asks how model selection/routing works or
  what the "11 categories / 16 categories" refer to.
- Add new condensed findings there as the runtime is explored further.
