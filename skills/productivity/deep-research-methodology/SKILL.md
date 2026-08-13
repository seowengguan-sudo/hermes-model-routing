# Deep Research Methodology for Task Context Generation

## Trigger
**Use this skill when:** You need to produce high-quality, well-researched deliverables that require understanding domain context, synthesizing multiple sources, and producing professional output (reports, POCs, presentations, documentation).

## Core Principle
**Research-first, then build.** Every task that involves substantive content generation follows a structured research → synthesis → output cycle. Quality is proportional to the depth of the context layer.

## Five-Layer Research Framework

### Layer 1: Task Decomposition & Role Framing
1. **Parse the prompt:** What is explicitly asked vs. implied?
2. **Identify your role:** Are you an AI consultant, technical architect, COO advisor, or executor?
3. **Determine the user's end goal:** What problem are they really solving? (Look beyond surface requests.)
4. **List constraints:** Budget, tech stack, egress realities, model availability, time horizon.
5. **Identify what-else & what-if scenarios:** Edge cases the user hasn't mentioned but could matter.

### Layer 2: Contextual Intelligence Gathering
1. **Check session history (session_search):** Never repeat work, leverage past decisions.
2. **Check knowledge base:** INDEX.md → by_industry → mentor → raw → workspace.
3. **Check existing skills:** Are there relevant skills already available? Load them.
4. **External research (web_search):** Gather authoritative sources on the domain.
5. **Source extraction (web_extract):** Pull full content from the 3-5 most relevant URLs.
6. **Synthesize findings:** Distill into actionable insights, not just facts.

### Layer 3: Architecture Design
1. **Define the output structure:** What sections, tables, frameworks make sense?
2. **Choose the right template:** Match the output format to the skill system.
3. **Identify verification needs:** What must be true for the output to be "correct"?
4. **Plan the verification steps:** Write the test before building.

### Layer 4: Execution with Continuous Verification
1. **Build the generator script first** (Python for PDFs, structured for reproducibility).
2. **Run ad-hoc verification immediately** — test syntax, imports, end-to-end generation, content validation.
3. **Fix issues on the fly** — don't ship unverified code.
4. **Iterate rapidly:** Fix → retest → fix (but know when to stop, max 3 attempts).

### Layer 5: Knowledge Capture & Skill Creation
1. **Document the learning:** What patterns worked? What pitfalls emerged?
2. **Create/update skills:** Capture reusable methodologies.
3. **Update knowledge base:** Add to INDEX.md with cross-references.
4. **Update MEMORY.md:** Record stable conventions and preferences.
5. **Plan next reinforcement:** Where should this learning recur?

## Research-to-Code Flow Template

```
1. web_search(query_1) + web_search(query_2)  # Parallel searches
2. web_extract(top_URLs)                       # Pull full content
3. session_search(query)                       # Check session history
4. read_file(knowledge_source)                 # Read KB
5. skill_view(relevant_skill)                  # Load existing skills
6. → Syntheses all findings → Design structure
7. Write generator_script.py
8. Run hermes-verify-script.py [ad-hoc test]
9. Fix issues, retest (max 3 cycles)
10. Commit + push verified content
11. Update SKILL.md / MEMORY.md / INDEX.md
```

## Ad-Hoc Verification Pattern (Always Use)

```python
#!/usr/bin/env python3
"""hermes-verify-XXX.py — Ad-hoc verification."""
import ast, sys, os, tempfile

# 1. Syntax check (ast.parse)
# 2. Module import (try/except)
# 3. End-to-end execution (generate output)
# 4. Output validation (header, pages, content checks)
# 5. Content extraction + assertion (key sections present)
# 6. Cleanup temp file

passed = 0, total = 0
def check(name, condition, detail=""): ...
```

## Pitfall Catalog (from Aug 12 Incident & PDF Work)

1. **Git auto-sync race condition:** Committing SQLite DBs while they're being written zeros the file. Always gitignore `*.db`, `*.db-wal`, `*.db-shm`.
2. **Egress blockers:** HF DNS-blocked, Groq/Cerebras WAF-throttled. Always check local-first alternatives.
3. **Model drift:** Unpinned cron models break when defaults change. Always pin to specific `provider/model:tag`.
4. **PDF header assertion bug:** `b"%PDF-1."` is 7 bytes, not 6. Use `.startswith()` instead of slicing with wrong length.
5. **Skill duplication:** Two different PDF skills (uppercase `skills/PDF/` vs lowercase `skills/productivity/pdf/`). Always check `skills_list` for duplicates before creating.
6. **Python path issues:** `sys.path.insert(0, 'lazy-packages')` needed for reportlab import.
7. **ReportLab version differences:** `reportlab 5.0.0` has different API surface than older versions. Always verify against installed version.

## Key Tools for Deep Research

| Tool | Purpose | When to use |
|---|---|---|
| `web_search` | Find relevant sources | When external domain knowledge needed |
| `web_extract` | Pull full page content | After narrowing to top 3-5 URLs |
| `session_search` | Recall past decisions | Always — before starting any task |
| `read_file` | Read KB files, skills, code | To understand existing context |
| `skill_view` | Load skill details | Before using any skill |
| `terminal` + `python3 -c` | Ad-hoc verification scripts | After every code generation |
| `git log/show/status` | Understand git history | When investigating incidents |

## Research Query Patterns (What to Search For)

- **Business model research:** "enterprise AI business model [industry] value proposition" + "solution business model framework"
- **Executive framework research:** "[framework name] executive guide overview implementation"
- **Technical pattern research:** "reportlab platypus tutorial flow layout" + "reportlab table wrapping best practices"
- **Industry benchmarking:** "[industry] operational excellence benchmark" + "[industry] pain points"
- **Incident analysis:** Search for root cause patterns in relevant domains

## Continuous Learning Loop

```
Research → Build → Verify → Ship → Document → Skill Update → Repeat
```

Each cycle should ask:
1. What did I learn that wasn't captured before?
2. What pattern can be reused for similar future tasks?
3. What pitfall was encountered and how to prevent it?
4. How can the verification be made more rigorous?

## References
- FourWeekMBA: C3.ai Business Model (VTDF framework)
- 6Sigma.us: 7 Core Pillars of Operational Excellence
- McKinsey: Digital Transformation on the CEO Agenda
- OpenAI: A practical guide to building agents
- Anthropic: Building effective agents
