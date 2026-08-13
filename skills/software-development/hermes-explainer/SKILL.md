---
name: hermes-explainer
description: Explain Hermes internals real agent step-by-step.
category: software-development
---

# hermes-explainer

## Hard rule from this user
Explain the **REAL, currently-running Hermes agent** — never the v3.x design docs (v3.3–v3.6 were explicitly set aside as "proposals, not running code"). If you start describing a router / interrupt-poller / metacognition layer that isn't actually running, STOP and label it *design*, not current behavior.

## Style this user wants
- **Deep clarity**, not summary. Layer-by-layer mechanism.
- **Step-by-step**, labeling each party (You / Runtime / Model / Tool backend) every step.
- **Concrete practical examples** — real prompt → trace every message + actual data.
- **Separate "what's real" from "what's designed"** when ambiguous.
- **Inspect actual source/config over guessing.** Real paths this session:
  - `/opt/hermes/skills/` (bundled 71) and `/opt/data/skills/` (profile 85, incl `.hub/`)
  - `/opt/data/config.yaml` — **active config** (HERMES_HOME=/opt/data), NOT `/opt/hermes/config.yaml`
  - `hermes_cli/models.py` (free catalog), `agent/model_metadata.py` (context lengths)
  - `tools/mcp_tool.py`, `mcp_serve.py`, `hermes_tools_mcp_server.py`, `optional-mcps/*/manifest.yaml`
  - `tools/code_execution_tool.py` (`hermes_tools` gen + SANDBOX_ALLOWED_TOOLS), `tools/file_operations.py` (write_file lint: `python -m py_compile`)

## Pitfalls to avoid (learned this session)
- **No "single active model per session".** `config.yaml` has a MAIN model (e.g. `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free`) PLUS AUXILIARY free-tier models per sub-task: vision→nemotron-3-super-120b, web_extract→step-3.7-flash, compression→hy3, **mcp→deepseek-v4-flash**, approval→gemini-2.5-flash, skills_hub→step-3.7-flash, triage→poolside/laguna-xs. Say "one primary model + auxiliary routing per sub-task".
- **Don't overstate MCP.** MCP is optional bridge (server exposes conversations/tools; client consumes `mcp_servers`). Core tools (terminal, read_file, delegate_task) are NATIVE. MCP client OFF unless `mcp_servers` in config.
- **Never guess token/context numbers** — verify live. Stale listings misled earlier (laguna-s context).
- **Security posture:** per-client isolation, secrets out of skills/context, external MCP = separate account meter (NOT Hermes model tokens), local MCP (blender/unreal) = $0 external.

## Deliverable shape that worked
(0) one-sentence frame; (1) sources/inputs; (2) construction pipeline in order; (3) annotated example of real artifact; (4) deep-dive per step; (5) worked examples A/B/C; (6) ASCII funnel; (7) honest limits. Then offer live inspection ("want me to read the actual file?").

## See also
- `hermes-model-catalog` skill for free/paid provider landscape.
