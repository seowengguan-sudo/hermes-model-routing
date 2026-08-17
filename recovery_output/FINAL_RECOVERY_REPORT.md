# Hermes Recovery Report — August 12, 2026

## Root Cause
The `state.db` SQLite file at `/opt/data/state.db` was **zeroed out** (~0 bytes) at **13:18:05 on Aug 12, 2026**. The `sessions` table is empty (0 rows). The WAL file (`state.db-wal`, 4.9MB) was committed to git in commit `c2e637c` and contains recoverable session data. Docker was NOT the cause (daemon not running, no containers).

## What Was Recovered

### Sessions (3 from WAL — only pre-13:14 data captured before the zeroing)
| Session ID | Model | Provider | System Prompt Length |
|---|---|---|---|
| `20260805_083757_d656eb` | stepfun/step-3.7-flash:free | Nous | 3,753 chars |
| `20260808_113940_51be22` | tencent/hy3:free | Nous | 1,183 chars |
| `20260810_152811_058f5f` | poolside/laguna-s-2.1:free | Nous | 3,284 chars |

Plus 15 cron sessions (cron IDs with tencent/hy3:free provider=Nous).

### Conversation Messages (6 from main session 20260810_152811_058f5f, page 7891)
1. assistant: "✅ Found it — checking /opt/data/GithubToken.txt"
2. tool: read_file — token file is 40 bytes, shows `«redacted:ghp_…»`
3. assistant: "⚠️ The file exists but appears empty or redacted" — attempted shell check
4. tool: Error — `Tool 'shell' does not exist. Available tools: [full list of 30+ tools]`
5. assistant: Used `execute_code` to read token in binary — hex starts with `6768705f7867` (`ghp_xg...`)
6. tool: `{"status": "success", "output": "Raw bytes: 40, Hex dump: 6768705f7867..., ✅ Valid token format detected"}`

### Architecture / Guardrails / Approval Config

**THESE WERE NOT LOST** — they exist on disk as files and skills:

1. **`/opt/data/skills/model-selection-policy/SKILL.md`** (4,761 bytes) — THE approval gate criteria skill
   - GATE 1: Daily refresh of model catalog (once per active day)
   - GATE 2: Per-category model pick (walk free list, skip exhausted, auto-fallback)
   - PAID RULES: Paid fallback = Gemini (vision) or DeepSeek-v4-flash (else). **deepseek-v4-pro: NEVER auto. Requires explicit user approval.**
   - LIMIT RULES: Nous Portal=20RPM/500TPM, NIM=lifetime 1000 credits (permanently removed when exhausted), OpenRouter resets MYT 08:00 daily, DeepSeek/Gemini are PAID (balance from user)
   - Auto-switch on 429 (rate-limit, not exhaustion), STOP and ask on paid

2. **`/opt/data/skills/mlops/free-tier-model-routing/SKILL.md`** (17,277 bytes) — Free-tier routing with approval gates
   - Durable preference: FREE-tier only, PAID needs explicit approval each time
   - If all free exhausted → STOP and ask
   - ASN ban on Groq/Cerebras (Cloudflare 1010 on egress IP 161.142.137.99)

3. **`/opt/data/model_config_snippet.yaml`** (2,165 bytes) — Model config with approval gates
   - All 11 USE_AS categories set to free-tier defaults
   - PAID FALLBACKS section (gated): vision→gemini-3.5-flash, mcp→deepseek-v4-flash, approval→gemini-2.5-flash, etc.
   - "Apply only after user approval"

4. **`/opt/data/model_state.json`** — Local proxy counters for rate/credit limits
5. **`/opt/data/model_perf_log.md`** — Learning loop log (quality tracking per model)

### Memory & User Profile (from /opt/data/memories/)
- **MEMORY.md** (2,119 bytes): User environment, egress info, model priority, KB map, cron verification notes
- **USER.md** (2,524 bytes): Identity (AI Consultant), mission (POC scaffolding for OAKAI), working style, model/cost posture

### Complete System Prompt (3,749 chars)
Recovered from WAL pages 53, 291, 344, 1441. Contains: identity, docs reference, finishing-the-job rules, parallel tool calls, memory rules, skill safety rules, mid-turn steering, Nous subscription, skills inventory, approval gate logic.

## Directory Recovery Status

### RESTORED from git commit 54c4651:
- `/opt/data/knowledge/` (25 files) — INDEX.md, mentor/, by_industry/solar_energy/pensolar/, raw/, strategy/, templates/
- `/opt/data/workspace/` (9 files) — INDEX.md, PDFs, Excel KPIs, daily brief, cleanup policy
- `/opt/data/skills/` (98 SKILL.md files across 20 categories) — ALL skill files
- `/opt/data/cron/` (5 active cron jobs) — mentor-ai-daily, learn-pensolar, workspace-cleanup-daily, strategic-coo-guidance, marketing-advisor-daily, startup-catchup-enforcement
- `/opt/data/model_state.json`, `/opt/data/model_perf_log.md`, `/opt/data/model_config_snippet.yaml`
- `/opt/data/docs/` (1 file) — OAKAI command center dashboard

### Approval Gate Criteria — WHERE IT LIVES
The approval gate is **NOT** a cron job or a prompt injection. It is a **multi-layer architecture**:

1. **Procedural skill** (`model-selection-policy/SKILL.md`): The agent consults this at session start and before every model-dependent task. It walks the free-first chain, skips exhausted models, and **STOP + clarify()** before using any paid model.

2. **Config layer** (`config.yaml` + `model_config_snippet.yaml`): All 11 `auxiliary.*` USE_AS categories (vision, mcp, skill_hub, **approval**, web_extract, compression, title_generation, triage_specifier, kanban_decomposer, curator, profile_describer) + main loop are set to **free-tier defaults only**. Paid fallbacks exist in the snippet but are explicitly NOT applied to config.yaml — the agent proposes them and waits for user approval.

3. **Runtime enforcement** (`model_state.json`): Tracks req_count/token_count per model, sets `exhausted=true` on 429, tracks NIM lifetime credits (1000 cap → permanent removal).

4. **Daily refresh cron** (`startup-catchup-enforcement` at 06:00 MYT): Runs `enforce_pins.py` + `catchup.py` to ensure all crons are pinned to tencent/hy3:free and fire any missed executions.

### Why You May Still Not See Things
If the Hermes Dashboard/CLI doesn't show the restored files, possible causes:
1. **State cache**: Hermes may cache skill index/sessions in `~/.hermes/` or build state — a restart of the Hermes daemon may be needed.
2. **Skill indexing**: The `.hub/index-cache/hermes-index.json` may need regeneration. Check `hermes skills list` or `hermes status`.
3. **Git tracking**: The skills/knowledge/workspace directories were committed in `54c4651` but deleted in working tree (commit `450adc2` removed them from git tracking while `.gitignore` was being updated). They are now restored to disk but may be showing as untracked in git status.

## Files Saved
All recovery artifacts are at `/opt/data/recovery_output/`:
- `sessions_full.json` — 3 session records with model configs + system prompts
- `all_conversation_messages.json` — 6 messages from main session
- `complete_system_prompt.txt` (~3,749 chars) + `system_prompt_full.txt` (~18,651 chars with full skills inventory)
- `full_memory_block.txt` — memory block with model priority, cost posture
- `full_user_profile.txt` — user profile, environment, architecture intent
- `conversation_search.txt` — keyword search of all 468 WAL pages
- `page_1489_raw.txt`, `page_1513_raw.txt`, `page_1466_raw.txt`, `page_1471_raw.txt` — raw WAL page text

## Remaining Limitations
- **state.db sessions table is still empty** — only WAL (historical) data was recoverable, not the live DB. Sessions exist in git WAL but not in the running system.
- **Full conversation history** beyond 6 messages requires following SQLite overflow page chains, which failed due to B-tree corruption.
- **Docker daemon** is not running — cannot inspect containers (but this was ruled out as the cause).
