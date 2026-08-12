# Verified Hermes Runtime File Map (inspected session)

Confirmed by direct `search_files` / `read_file` / `terminal` inspection of the
installed runtime. Paths are relative to `/opt/hermes` unless noted.

## Dual skill directories
- Bundled (runtime): `/opt/hermes/skills/` — 71 SKILL.md (11 categories).
- Profile (`$HERMES_HOME/skills` = `/opt/data/skills/`): 85 SKILL.md.
- UI (`web/src/pages/SkillsPage.tsx` → `api.getSkills`) shows the **deduped union**
  of both via `tools/skills_tool.py::_find_all_skills`, minus disabled → ~81.
- Hub-installed skills live under `/opt/data/skills/.hub/` (LobeHub/GitHub/etc.).
- `index-cache/*.json` (anthropics/lobehub/openai) = read-only marketplace
  CATALOGS, NOT your skills; your local paths are absent from them.

## MCP — two directions (NOT core tool plumbing)
- Server (conversations bridge): `mcp_serve.py` (`hermes mcp serve`, FastMCP,
  stdio). Exposes conversations/messages/events/approvals to Claude Code/Cursor/Codex.
- Server (tools → Codex): `agent/transports/hermes_tools_mcp_server.py`.
  Exposes web/browser/vision/skill/tts/kanban (NOT terminal/file/delegate/memory).
- Client (consume external): `tools/mcp_tool.py` (`register_mcp_servers`,
  StdioServerParameters + ClientSession, list_tools → registry), wired from
  `agent/coding_context.py::_enabled_mcp_servers` reading config `mcp_servers:`.
  Transports: stdio / streamable-http / sse. Has reconnect/keepalive, cred scrub.
- Optional catalog (NOT required): `/opt/hermes/optional-mcps/` manifests:
  blender, comfy-cloud, figma, linear, n8n, unreal-engine. UI lists these as
  "not installed" — app-store style. Installing one connects Hermes to THAT
  external service (needs its token). None auto-connect.

## Tool execution (native, not MCP)
- `tools/code_execution_tool.py`: `generate_hermes_tools_module` auto-builds the
  `hermes_tools` stub module for `execute_code`. Allowed set
  (`SANDBOX_ALLOWED_TOOLS`): web_search, web_extract, read_file, write_file,
  search_files, patch, terminal. Plus helpers json_parse/shell_quote/retry.
  Transport = UDS socket (local) / file RPC — NOT MCP.
  Limits: 5-min timeout, 50 tool calls, 50KB stdout.
- `tools/file_operations.py`: `write_file` runs a pre-write syntax gate.
  LINTERS = {'.py':'python -m py_compile', '.js':'node --check', '.ts'/'go'/'rs'
  via tsc/go vet/rustfmt but flagged LSP-redundant}. Only NEWLY-introduced errors
  surfaced (delta vs pre-write). `.json`/`.yaml`/`.toml` parsed in-process.
  Returns `verified:true` = on-disk hash confirmed.

## Config (real, `/opt/data/config.yaml`)
- `model.provider: openrouter`, `default: nvidia/nemotron-3-ultra-550b-a55b:free`
  (note: may differ from session-injected model line).
- `web.backend: firecrawl`, `use_gateway: true` → NATIVE web tools, not MCP.
- `browser.cloud_provider: browser-use`, `use_gateway: true` → native.
- `auxiliary.*`: per-task free models (vision→nemotron-3-super-120b,
  web_extract→step-3.7-flash, compression→hy3, mcp→deepseek-v4-flash,
  approval→gemini-2.5-flash, skills_hub→step-3.7-flash). Real auxiliary fan-out.
- No `mcp_servers:` key → MCP client mode OFF for this user.

## Skills UI tabs
`web/src/pages/SkillsPage.tsx`: tabs = Skills (union count), Toolsets
(`getToolsets`, a grouping dimension not a storage location), Browse hub
(catalog search of external sources).
