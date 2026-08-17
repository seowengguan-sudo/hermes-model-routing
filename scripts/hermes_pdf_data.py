"""Data for Hermes architecture PDF — separate to avoid write cap."""

P1 = [["Step","Source","Type","Persists"],
      ["1","System prompt (bundled)","static","no"],
      ["2","MEMORY.md + USER.md","auto-injected","yes - disk file"],
      ["3","Skills INDEX (names only)","flat list","no"],
      ["4","Conversation history (this session)","compactable","no"],
      ["5","New user message","input","no"]]

P1_FOOT = ["History compaction: oldest verbatim turns are summarized+dropped when context\n grows; gist retained. Across sessions, history resets — only\n MEMORY.md/USER.md and state.db persist (via session_search)."]

P2 = [["Aspect","Reality vs Misconception"],
      ["Model routing","Profile config — ONE active model per session","(per-task router)"],
      ["Active model","tencent/hy3:free @ Nous (pinned)","(multi-model auto-switch)"],
      ["Free-tier","NOT in default agent — was a design spec only","(auto-routed providers)"],
      ["Paid","Explicit UI approval only","(autonomous escalation)"]]

P2_FOOT = ["Skill count: 71 bundled (/opt/hermes/skills) + 85 profile (/opt/data/skills, incl .hub) = 81 deduped."]

P3 = [["Toolset","Execution environment","Boundary to Nous"],
      ["terminal","Shell + python3 in Linux container","Container fs only"],
      ["execute_code","Script in session venv","Persistent venv, same container"],
      ["file (read/write/patch)","Direct runtime OS ops","Path lock + staleness"],
      ["web/image/skills","FAL / search APIs","Same text channel"]]

P3_FOOT = ["Limits: 300s timeout, 50 tool calls/turn, 50KB stdout, 10KB stderr.\nwrite_file lint gate fail-closed: .py->py_compile, .js->node --check,\n .json/.yaml/.toml->parse, .ts/.go/.rs->shell linter. verified:true = hash confirmed."]

P4 = [["Job type","Jobs","How it runs","Output delivered"],
      ["no_agent","watchdog, git-push, cleanup, catchup","Script only — stdout verbatim","Silent = success"],
      ["agent","mentor, pensolar, coo, marketing","LLM reasoning on prompt","Reasoned briefing"]]

P4_FOOT = ["Path rule: no_agent scripts must live under /opt/data/scripts/.\n repeat=-1 = infinite. startup-catchup armed + forever."]

P5 = [["Mechanism","What it is","Scope","How accessed"],
      ["MEMORY.md / USER.md","Durable fact files","All sessions","Auto-injected every turn"],
      ["state.db (SQLite)","Session store + facts DB","All sessions","session_search"],
      ["Conversation history","This session messages","Current session only","In-context; compacted when long"]]

P5_FOOT = ["The model receives: system prompt + MEMORY.md + USER.md + skills INDEX\n + conversational history + new message. It sees neither the filesystem\n nor internal state — only this flattened text."]

P6 = [["Trust zone","Inside container","Outside container"],
      ["Container (/opt/data, /opt/hermes)","Tools, files, venvs, state.db","- (Nous)"],
      ["Nous provider channel","Flattened context text only","Filesystem/disk"],
      ["Browser (Windows host)","Read localhost:8765 for doc-reader","Cannot reach internals"],
      ["Browser-use daemon","Headless Chromium (sanitized)","Sandboxed: no file:// or localhost"]]

P6_FOOT = ["Data never crosses the boundary in binary form — all tool\n results are serialized to text before reaching the model."]
