---
name: hermes-runtime-source-verification
description: Verify how real Hermes works by checking installed source.
category: hermes-internals
---

# hermes-runtime-source-verification

## When to use
- User asks "how does Hermes do X" (context construction, tool invocation, skills storage, MCP, memory injection, model selection/switching).
- User wants the REAL current default behavior, explicitly separate from designed/aspirational architecture docs.

## Core method
The system prompt and bundled docs describe the *intended* agent. The *actual* runtime is the installed code. To answer accurately:
1. Inspect the real source under `/opt/hermes` and config at `$HERMES_HOME/config.yaml` (usually `/opt/data/config.yaml`).
2. Use `search_files` / `read_file` / `terminal` (grep) to confirm file paths and logic BEFORE stating how something works.
3. Explicitly separate "real current behavior" from "designed/aspirational" whenever the user has set design docs aside.

## Verified file map
See `references/real-hermes-filemap.md` — confirmed by direct inspection:
- MCP server (conversations bridge): `mcp_serve.py`
- MCP server (Hermes tools → Codex): `agent/transports/hermes_tools_mcp_server.py`
- MCP client (consumes external servers): `tools/mcp_tool.py`, `agent/coding_context.py`, config `mcp_servers:`
- Skills: bundled `/opt/hermes/skills` + profile `/opt/data/skills` (`$HERMES_HOME/skills`); UI shows the deduped union, not just the bundled 71.
- Tool execution: `tools/code_execution_tool.py` (auto-generates `hermes_tools` stubs), `tools/file_operations.py` (write_file lint), `tools/file_tools.py`.
- Config: `/opt/data/config.yaml` (model defaults, `web.backend`, auxiliary per-task models).

## Pitfalls (encode these)
- **Don't confuse design with runtime.** Separate "v3.x architecture" proposals from the running default agent. Answer only the real runtime unless asked.
- **MCP is NOT how core tools work.** Native tools (terminal, read_file, write_file, delegate_task, etc.) are direct runtime calls. MCP is an OPTIONAL bridge: (a) for Hermes to consume external tool servers, and (b) for other AIs (Claude Code/Cursor/Codex) to drive Hermes.
- **Web search is native, not MCP.** `web.backend: firecrawl` + `use_gateway: true` is a built-in integration. The 6 "optional MCP" catalog entries under `/opt/hermes/optional-mcps/` are NOT required for search/browser; they're an app-store-style catalog of add-ons (Blender, Comfy-Cloud, Figma, Linear, n8n, Unreal-Engine).
- **Two skill directories exist.** Counting only `/opt/hermes/skills` undercounts; the UI union with `/opt/data/skills` (incl. `.hub/` installed skills) is what's displayed.
- **Active (session-injected) model may differ from `config.yaml` `model.default`.** Both are real in their context — don't claim a single fixed model without checking config.
- **`hermes_tools` inside `execute_code` is auto-generated** from `SANDBOX_ALLOWED_TOOLS` (7 tools + 3 helpers); only those importable. Transport is a UDS socket (local) / file RPC, not MCP.

## Communication preference (this user)
For architecture/explain questions, the user wants: **deep clarity**, **step-by-step party-by-party flows** (You → Runtime/TUI → Model → Tool backend → back), and **concrete worked examples**. Favor thoroughness over brevity here. Acknowledge the validity of their reasoning before offering counterpoints. They explicitly set aside design docs and want ONLY the real current agent — do not blend the two.

## Overlap note
Bundled skill `hermes-runtime-explainer` covers the *conceptual* "explain the real agent" class and is protected (cannot be patched here). This skill is the complementary *verification-method + verified file map* layer. If a curator adopts `hermes-runtime-explainer`, merge this file map into it.
