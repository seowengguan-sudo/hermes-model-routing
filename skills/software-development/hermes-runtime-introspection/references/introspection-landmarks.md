# Hermes Introspection Landmarks (verified this session)

## Config
- Active config: `$HERMES_HOME/config.yaml` where `HERMES_HOME=/opt/data` (env). `/opt/hermes/config.yaml` often does NOT exist.
- Real example (this user): `model.provider: openrouter`, `model.default: nvidia/nemotron-3-ultra-550b-a55b:free`. Auxiliary `mcp:` model = `deepseek-v4-flash` (deepseek provider), NOT nous. `web.backend: firecrawl`, `browser.cloud_provider: browser-use` (both `use_gateway: true`) — so web/browser are NATIVE, not MCP.

## Skills layout
- Bundled: `/opt/hermes/skills/` → 71 SKILL.md (category dirs).
- Profile: `$HERMES_HOME/skills/` → 85 SKILL.md + `.hub/` (installed hub skills) + `.usage.json`. UI "total" = deduped union minus disabled.
- Code: `tools/skills_tool.py` `_find_all_skills()` merges both via `get_external_skills_dirs()`; `agent/skill_utils.py` `SKILLS_DIR = HERMES_HOME / "skills"`.
- UI list endpoint: `hermes_cli/web_routers/skills.py` `get_skills()` → `_find_all_skills(skip_disabled=True)`. UI tab: `web/src/pages/SkillsPage.tsx` (Skills / Toolsets / Browse hub).

## MCP
- Catalog dir: `/opt/hermes/optional-mcps/<name>/manifest.yaml`. Shipped 6: blender (stdio uvx, local), comfy-cloud (https, oauth), figma (https, oauth), linear (https, oauth), n8n (stdio git, api_key), unreal-engine (http 127.0.0.1:8000, none).
- Client code: `tools/mcp_tool.py` (StdioServerParameters, ClientSession, reconnect/keepalive, cred scrub). Server code: `mcp_serve.py` (FastMCP, conversations bridge), `agent/transports/hermes_tools_mcp_server.py` (tools-as-MCP for Codex).
- Config write: `hermes_cli/mcp_config.py` `_save_mcp_server()` → `config.mcp_servers.<name>` with `transport`, `env`, `enabled_tools`, `enabled`. Validates against exfiltration-shaped commands.
- n8n real tool schemas (from pinned repo `CyberSamuraiX/hermes-n8n-mcp` @ 7a9ae00): 11 tools; default-enabled 8 (health, list_workflows, get_workflow, find_workflows, list_executions, get_execution, recent_failures, export_workflow). ~470 tokens/turn schema overhead for 8; results 1.5K–15K tokens each, persist in context.

## Model context lengths (verified)
- `hy3` / `hy3-preview`: 262144 (agent/model_metadata.py).
- From OpenRouter/provider pages: laguna-s 1.05M, laguna-xs 256K, step-3.7-flash 256K.
- Free-tier catalog (`hermes_cli/models.py`): `tencent/hy3:free`, `nvidia/nemotron-3-ultra-550b-a55b:free`, `poolside/laguna-m.1:free` (only free laguna), `nvidia/nemotron-3-super-120b-a12b:free`, `openrouter/elephant-alpha`, `inclusionai/ring-2.6-1t:free`. `laguna-s` NOT in free catalog. `step-3.7-flash` listed but not `:free`-tagged.

## Tool invocation
- Native: `tools/terminal_tool.py`, `tools/file_tools.py`, `tools/file_operations.py`, `tools/web_tools.py`.
- `execute_code` hermes_tools stubs: `tools/code_execution_tool.py` `SANDBOX_ALLOWED_TOOLS` = {web_search, web_extract, read_file, write_file, search_files, patch, terminal} + helpers json_parse/shell_quote/retry. Limits: 300s, 50 calls, 50KB stdout.
- `write_file` syntax gate: `tools/file_operations.py` LINTERS (`.py`→`python -m py_compile`); only NEW errors surfaced; `.json/.yaml/.toml` in-process; returns `verified:true`.
