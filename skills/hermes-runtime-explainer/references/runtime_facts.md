# Hermes Runtime Facts (verified from source, this session)

Condensed, reusable internals. Paths are from the user's container
(HERMES_HOME=/opt/data; Hermes install at /opt/hermes).

## 1. Context construction (every turn)
Runtime concatenates, in order:
  system prompt → injected MEMORY.md + USER.md → skills INDEX (names only)
  → conversation HISTORY (this session) → new user message.
Then `model.generate(context)`. History accumulates within a session; it is
compacted (summarized) when too long — verbatim old turns are dropped, gist
kept. Across sessions, history resets; only MEMORY.md/USER.md (auto-injected)
and the SQLite session store (via `session_search`) persist.

## 2. Skills: TWO directories (explains 71 vs 81 in UI)
- Bundled: `/opt/hermes/skills/` → 71 SKILL.md (shipped with Hermes).
- Profile: `/opt/data/skills/` → 85 SKILL.md (HERMES_HOME/skills; where
  install/edit/learn land) incl. `.hub/` (installed hub skills) + `.usage.json`.
- UI count = deduped union of both, minus disabled. So 71 bundled + 85
  profile → 81 shown. NOT a leak; all local to container.
- LobeHub = installed hub skills under `/opt/data/skills/.hub/` + read-only
  marketplace catalog cache `index-cache/*.json` (Anthropic 16, LobeHub 505
  agents, OpenAI 0). Browsable/installable; not auto-loaded.
- Toolset = a UI grouping tab (`getToolsets()`), not a storage location.
- `get_skills` backend: `tools/skills_tool.py:_find_all_skills()` scans
  `[active_skills_dir] + get_external_skills_dirs()`; dedupes by name;
  skips disabled. Provenance tagged bundled/hub/agent.

## 3. execute_code + hermes_tools (auto-generated stub)
- `hermes_tools` is GENERATED at runtime by
  `tools/code_execution_tool.py:generate_hermes_tools_module()` from
  `SANDBOX_ALLOWED_TOOLS ∩ enabled_tools`.
- Importable (UDS RPC to runtime): web_search, web_extract, read_file,
  write_file, search_files, patch, terminal. Plus helpers: json_parse,
  shell_quote, retry.
- Limits: DEFAULT_TIMEOUT=300s, MAX_TOOL_CALLS=50, MAX_STDOUT=50KB,
  MAX_STDERR=10KB.
- Importing a non-allowed tool → ImportError. Results are DICTS, not strings.

## 4. write_file syntax gate (fail-closed, pre-write)
- `tools/file_operations.py:LINTERS`:
  `.py`→`python -m py_compile {file} 2>&1`, `.js`→`node --check`,
  `.ts`→`npx tsc --noEmit`, `.go`→`go vet`, `.rs`→`rustfmt --check`.
- `_check_lint_delta()` lints pre-write AND new content; only NEWLY
  introduced errors surfaced (pre-existing filtered out).
- `.json`/`.yaml`/`.toml` parsed in-process (json.loads / yaml.safe_load).
- On success returns `verified:true` (on-disk hash confirmed) — do NOT
  re-read to confirm. `.ts/.go/.rs` shell linters are phantom-prone; LSP
  carries real signal when configured.

## 5. Tool invocation model (local)
- terminal: spawns shell in container; python3 runs interpreter (venv if
  activated; state persists across calls).
- execute_code: runs script in session venv python, captures stdout.
- file tools (read/write/patch/search): direct OS ops via runtime, with
  path resolution + cross-agent lock + staleness checks.
- All execution is INSIDE the container. Nous (model provider) only sees
  the TEXT of tool calls + results (same channel as user messages).

## 6. Model selection (real default agent)
- CONFIG/PROFILE level, not per-task. One active model per session
  (e.g. tencent/hy3:free via Nous). Set by runtime/config.yaml + profile.
- NO autonomous free-tier router in the default agent (that was a design).
- Per-sub-task model switching does not happen. Paid model only via
  explicit UI approval (paid-approval gate).
- Some TOOLS have own backends (image_generate=FAL, vision_analyze=aux
  model) — those are tool features, not the serving model switching.
- Active model with no vision endpoint (e.g. hy3) → vision_analyze 404s;
  no silent fallback router.

## 7. Memory vs skills vs context
- Memory (MEMORY.md/USER.md): durable facts, auto-injected every turn.
- Skills: procedural knowledge on disk; INDEX in context, BODY loaded
  on-demand via skill_view. Author new ones via skill_manage.
- History: this session's messages; compacted when long.
