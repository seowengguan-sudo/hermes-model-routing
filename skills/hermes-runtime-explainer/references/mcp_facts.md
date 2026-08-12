# MCP Facts (verified from source, this session)

Condensed, reusable internals about Model Context Protocol inside Hermes.
User pressed hard on: how MCP works, the 6 "not installed" entries, whether
installing costs tokens, and whether web search needs MCP.

## 1. MCP is NOT the core tool mechanism
My native tools (terminal, read_file, write_file, patch, search_files,
web_search, browser_*, delegate_task, memory, skill_*) are dispatched
DIRECTLY by the runtime — they are not MCP. MCP is an OPTIONAL bridge layer.

## 2. Hermes plays MCP in TWO directions
- SERVER: `hermes mcp serve` (mcp_serve.py) starts a stdio MCP server exposing
  Hermes CONVERSATIONS as tools (conversations_list, conversation_get,
  messages_read, messages_send, events_poll, permissions_*, channels_list).
  Lets Claude Code / Cursor / Codex drive Hermes.
  Also `agent/transports/hermes_tools_mcp_server.py` exposes a curated subset
  of Hermes tools to a spawned Codex subprocess via stdio (web/browser/vision/
  image_gen/skill_view/tts/kanban). It does NOT expose terminal/file tools or
  delegate_task/memory because those need the live AIAgent loop context.
- CLIENT: your `config.yaml` `mcp_servers:` block. At startup Hermes connects
  (stdio via StdioServerParameters + stdio_client + ClientSession; also HTTP
  Streamable / SSE), calls `list_tools()`, and registers them into my toolset
  as if native. When I emit a matching tool call, runtime sends JSON-RPC
  `tools/call`; external server executes; result returns into my context.
- Robustness (tools/mcp_tool.py): connect timeout 60s, tool timeout 300s,
  up to 5 reconnect retries, exp backoff + jitter, keepalive 180s, parked
  self-probe 300s. `_CREDENTIAL_PATTERN` scrubs secrets from error text; only
  safe env vars (PATH/HOME/...) passed to stdio subprocesses.

## 3. The "6 MCP not installed" = optional catalog (app-store style)
Source: `hermes_cli/mcp_catalog.py:list_catalog()` scans
`/opt/hermes/optional-mcps/<name>/manifest.yaml`. The 6 entries:

| Entry | Connects to | Transport | Auth |
|-------|-------------|-----------|------|
| blender | live Blender on YOUR machine | stdio (uvx) | none (local) |
| comfy-cloud | Comfy Cloud media gen | HTTPS cloud.comfy.org/mcp | oauth |
| figma | Figma design files | HTTPS mcp.figma.com/mcp | oauth |
| linear | Linear issue tracker | HTTPS mcp.linear.app/mcp | oauth |
| n8n | n8n workflows (default 127.0.0.1:5678) | stdio bridge (git-cloned) | api_key |
| unreal-engine | Unreal 5.8 editor (local :8000) | HTTP 127.0.0.1:8000/mcp | none (local) |

They are OFFERS, not requirements. Nothing auto-connects. You only connect
to a service you deliberately install (each needs its own token).

## 4. Does installing cost tokens? (the user's core question)
TWO separate "tokens":
- EXTERNAL APP credential (Linear/Figma/Comfy OAuth; n8n API key; Blender/
  Unreal none). This is auth, NOT consumption. The external service bills its
  OWN plan (e.g. n8n.cloud meters executions) — separate from Hermes, separate
  from the model. Self-hosted n8n/Blender/Unreal = $0 external.
- MODEL CONTEXT tokens (the real Hermes-side cost). Every enabled MCP tool's
  JSON Schema is injected into my context EVERY turn. Plus tool RESULTS
  (e.g. n8n get_workflow returns full workflow JSON) land in history and
  persist until compaction. On a free-tier model this burns free quota
  faster and accelerates compaction — it is NOT a dollar charge.

Net: installing an MCP does NOT make the external app eat your model tokens.
It DOES enlarge your model's prompt (schemas + results). Financially $0 on
free model + self-hosted/local app.

## 5. n8n measured overhead (from real server.py, commit 7a9ae00)
- 8 default-enabled tools (health, list_workflows, get_workflow,
  find_workflows, list_executions, get_execution, recent_failures,
  export_workflow) ~= 470 tokens/turn standing (schema only). All 11 ~= 566.
- Per-call results are the bigger cost: list_workflows(100) ~= 2k-6k;
  get_workflow/export_workflow ~= 1.5k-15k (persists in history);
  recent_failures(25) ~= 3k-7k.
- Mutating tools (activate/deactivate/container_logs) are PRUNED by default;
  enabling them lets me run/activate live workflows (n8n-cloud bills those).
- Safety: server.py redacts credential-bearing fields (SECRET_KEY_RE /
  SECRET_VALUE_RE) before returning data to the model.

## 6. Web search does NOT need MCP
`web.backend: firecrawl` + `use_gateway: true` and `browser.cloud_provider:
browser-use` + `use_gateway: true` (from /opt/data/config.yaml) are NATIVE
integrations in tools/web_tools.py and tools/browser_tools.py. MCP is
unrelated to web fetch. So with zero MCP servers, all web/browser works.

## 7. Exact config block written on install (n8n example)
_save_mcp_server("n8n", ...) writes into /opt/data/config.yaml:
  mcp_servers:
    n8n:
      transport: {type: stdio, command: "<INSTALL_DIR>/.venv/bin/python",
                  args: ["<INSTALL_DIR>/server.py"]}
      env: {N8N_BASE_URL: "http://127.0.0.1:5678", N8N_API_KEY: "<secret>"}
      enabled_tools: [health, list_workflows, get_workflow, find_workflows,
                      list_executions, get_execution, recent_failures,
                      export_workflow]
      enabled: true
API key stored in ~/.hermes/.env (secret:true). _save_mcp_server validates
and rejects exfiltration-shaped stdio commands (validate_mcp_server_entry).

## 8. Provider note (from /opt/data/config.yaml)
Main model: openrouter / nvidia/nemotron-3-ultra-550b-a55b:free.
Auxiliary `mcp:` model: deepseek-v4-flash (DeepSeek, not Nous). So "free tier"
here spans OpenRouter + DeepSeek, not only Nous Portal.
