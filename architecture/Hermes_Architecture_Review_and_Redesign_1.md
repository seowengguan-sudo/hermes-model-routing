# Hermes Meta-Intelligence — Architecture Review & Redesign

## Part 1: Honest Assessment of the Current Design

### What's genuinely good
- **Master + Specialist hierarchy** is a sound pattern (supervisor/worker agents). Keeping industries in separate profiles is the right instinct for client data isolation.
- **Gated learning** (dual confirmation + user approval before writing new knowledge) is a good safety brake against silent drift/corruption of the knowledge base.
- **Sub-segment context loading** shows you already understand that dumping the whole knowledge base into context is wasteful — you just haven't gone far enough with it (see Part 2).

### The real problems

**1. The document describes outcomes, not mechanisms.**
Sections like "Anti-Hallucination Assurance" and "Knowledge Graph Integration" state *what* should happen ("every claim traced to source," "real-time querying against an integrated, versioned knowledge graph") without saying *how*. There's no knowledge graph anywhere in the storage map — just flat folders of markdown. This is the classic trap of writing the spec with an LLM that fills gaps with confident-sounding architecture buzzwords. None of it is a lie exactly, but none of it is buildable as written either.

**2. "100% free-tier" is a liability, not a feature.**
Free API tiers exist to let providers absorb exploration traffic — <cite index="2-1">they're well-suited for exploration and are not designed for production workloads, with rate limits acting as the cost-allocation mechanism rather than a flaw to work around</cite>. Worse, <cite index="5-1">the free-model lineup actively rotates — DeepSeek and Mistral both had popular free variants that no longer exist on OpenRouter as of mid-2026</cite>. A system that auto-switches providers when one is exhausted is good engineering, but if you're relying on free tiers *exclusively* for client deliverables, you have no floor — the whole tier can disappear under you with a provider's roadmap change, not just a quota reset. This also cuts against your own "data sovereignty" pillar: free tiers usually mean broader logging/retention terms than paid enterprise agreements, so routing client data through six different free providers to save money is in tension with the isolation guarantee you're promising.

**3. The knowledge storage is the actual bottleneck for your stated goal (token efficiency), and it's not solved.**
Right now: `knowledge/master/pattern-library/`, `skills/payments/`, etc. are just folders of files. To "reuse past learnings" the agent has to load and re-read files every session — there's no indexing, no relevance ranking, no way to pull *only* the 200 tokens that matter out of a 5,000-token file. This is the opposite of what you asked for.

**4. No decay, dedup, or conflict handling.**
Nothing in the spec says what happens when two learnings contradict each other, when a pattern becomes stale, or when the pattern-library grows to thousands of entries. Without pruning, your "self-improving" system just accumulates cruft that costs tokens forever.

**5. Single point of failure at Master.**
Every task routes through one Master Agent for classification + delegation + synthesis. Fine at small scale; becomes your bottleneck and your biggest hallucination-risk surface as task volume grows, since Master is doing the most cognitively demanding work with the least specific context.

---

## Part 2: Redesigned Architecture

The core fix, since it's your main ask: **replace "load files" with "retrieve facts."** Everything below is designed around one rule — *nothing enters context unless it's the specific thing needed for the specific task.*

### 2.1 Memory Tiering (hot / warm / cold)

```
HOT   — current task working memory (in-context, ephemeral, cleared after task)
WARM  — vector-indexed knowledge, retrieved top-k on demand (SQLite+vector or LanceDB)
COLD  — compressed archival log, never loaded directly, only re-summarized periodically
```

Instead of `knowledge/master/pattern-library/*.md` as loose files, every learned unit becomes a **memory card**:

```json
{
  "id": "pat_0472",
  "type": "pattern | fact | skill | correction",
  "industry": "fintech",
  "sub_segment": "payments",
  "text": "Chargebacks under $10 are rarely worth disputing — avg recovery < processing cost",
  "source": "session_2026-07-14 / user-confirmed",
  "confidence": "verified",      // verified | inferred | unknown | contradicted
  "embedding": [...],
  "created": "2026-07-14",
  "last_used": "2026-08-01",
  "use_count": 6,
  "supersedes": null,
  "client_scrubbed": true
}
```

This single change gets you three things at once:
- **Retrieval instead of loading**: Master/Specialist queries the vector store for the top 5–10 relevant cards for *this specific task* — typically a few hundred tokens instead of loading entire skill files.
- **Reuse tracking**: `use_count` / `last_used` let you see what's actually earning its keep.
- **Built-in dedup surface**: before writing a new card, embed it and check cosine similarity against existing cards. High similarity → update/merge instead of duplicate.

### 2.2 Confidence Ladder, made concrete
Your Rule 2 ("Verified / Inferred / Unknown / Contradictory") is good but was unimplemented. Concretely:
- **Verified**: user-confirmed or cross-checked against a cited external source at write time.
- **Inferred**: agent-derived, not yet confirmed — usable, but must be flagged in output.
- **Contradictory**: two cards disagree — auto-flagged, routed to Master for resolution before either is reused, not silently dropped.
- Every retrieval returns its confidence tag alongside the content, so a Specialist's output can say "per verified pattern pat_0472" or "based on an unconfirmed inference, flagging for review" — this is what actually gets you traceability, not an unbacked "every claim traced to source" claim.

### 2.3 Compaction instead of accumulation
This is the piece most "self-improving agent" designs skip, and it's the one that actually keeps token costs flat as the system grows:
- Raw session logs live in `sessions/` (as you already have) but are **auto-compacted on a schedule** — e.g. weekly, an agent reviews the week's raw logs, extracts anything durable into new/updated memory cards, then the raw log is compressed and moved to COLD storage (or deleted after N days).
- COLD storage is never loaded for a live task. It only gets re-opened if a human explicitly asks "why did we decide X in July."
- This means your working knowledge base grows *by curated card count*, not by raw transcript volume — the thing you actually query stays lean forever.

### 2.4 Pruning / decay
Add a lightweight decay job:
- Cards unused for 90+ days and with `use_count < 2` get flagged for review, not silently deleted (you don't want to lose something rare-but-critical).
- Contradicted cards that lose resolution get archived, not left live.
- This is the difference between a knowledge base that stays fast to query and one that becomes 10,000 files deep and slow/expensive to search in year two.

### 2.5 Model routing — keep the idea, fix the foundation
Your router logic (classify → match → fallback chain) is solid. Two changes:
1. **Local model for routing/classification itself.** Task classification is cheap and doesn't need a frontier model — run a small local model (even a 1–3B quantized model in your Docker setup) for classify+route decisions, so you're not burning API calls (free or paid) just to decide which API call to make next.
2. **Free tier = burst capacity, not foundation.** Keep the free-tier fallback chain exactly as designed, but add one paid model as the floor for anything client-facing or classified high-stakes. Track $ spend against a hard monthly cap in the cost dashboard you already planned. This gets you real reliability without abandoning the cost-optimization goal — you're optimizing *toward* free, not *depending on* it.

### 2.6 Isolation, made stricter
Your isolation guarantee (separate `state.db` per industry) is good structurally, but the promotion path — Specialist learning → Master pattern-library — is exactly where client data can leak if the "generalization" step isn't enforced in code, not just in prompt instructions. Add an explicit **scrub-before-promote** step: a pattern can only be written to the master pattern-library after passing an automated check (regex/NER pass for names, account numbers, company identifiers) *in addition to* the dual-confirmation gate you already have. Log `client_scrubbed: true/false` on every card so you can audit it later.

### 2.7 Updated storage map

```
/opt/data/.hermes/
├── config.yaml
├── .env                          # keep out of any git-tracked/synced path
├── memory/
│   ├── vector.db                 # embeddings + memory cards (warm tier)
│   ├── cards/                    # human-readable export of cards, for audit
│   └── decay_queue.json          # cards flagged for review/pruning
├── profiles/
│   ├── master/  (state.db, hot working memory only)
│   ├── fintech/ ...
│   ├── healthcare/ ...
├── sessions/                     # raw logs, short retention
├── cold_archive/                 # compressed, never auto-loaded
├── model_benchmark/
└── audit_log/                    # every write: who/what/when/confidence/scrubbed
```

---

## Part 4: Self-Organizing Specialists (no predefined industries)

Since there are no clients yet, don't hardcode `fintech/healthcare/ecommerce`. Let Master grow the tree from actual conversation:

**Trigger logic (runs on every task, cheap/local, not a full LLM call):**
1. Embed the incoming task. Compare against existing specialist profiles' centroid embeddings.
2. **Match found (similarity > threshold)** → route to that Specialist / sub-segment as normal.
3. **No match, but a sub-segment inside an existing Specialist is close** → create new sub-segment under that Specialist (e.g. Master is talking to you about SaaS pricing, already has a `software` Specialist → adds a `pricing-strategy` sub-segment under it).
4. **No match at all** → Master auto-instantiates a brand-new Specialist profile, unconfirmed/provisional status, and starts a fresh `state.db` + empty memory namespace for it.

**Lifecycle beyond creation (this is the part most designs skip):**
- **Promotion**: a sub-segment that accumulates enough distinct, low-similarity-to-parent knowledge (i.e., it's really its own topic, not a subtopic) gets proposed for promotion to a full Specialist. Goes through the same dual-confirmation gate as any other structural change.
- **Merge**: if two Specialists' centroids drift close together over time (you've been treating "retail" and "e-commerce" as separate but they've converged), Master proposes a merge. Same gate.
- **Dormancy**: a Specialist unused for a long stretch gets marked dormant (excluded from routing search, not deleted) so it doesn't slow down classification as the tree grows.
- **Provisional → confirmed**: a newly auto-created Specialist stays "provisional" until it's been used a few times or you explicitly confirm it — this stops one oddly-phrased question from permanently forking a new industry profile.

This gives you exactly what you asked for: the org chart of Specialists grows out of real usage, not a template you have to predict in advance.

## Part 5: The Missing Layer — Procedural Memory (Skills & Tools)

This is the direct fix for the PDF example. Part 2's memory cards are **declarative** memory — facts and patterns ("chargebacks under $10 aren't worth disputing"). "How to lay out a professional PDF" is **procedural** memory — a reusable method, not a fact. Right now Hermes has no place to store that, so it re-derives formatting judgment from scratch (i.e. from your prompt) every single time. Four memory types, not one:

| Type | Example | Where it lives |
|---|---|---|
| **Declarative** | "Chargebacks under $10 rarely worth disputing" | `memory/` (Part 2) |
| **Procedural** | "House PDF report layout: cover page, 2-col body, footer pattern, this font pairing" | `skills/` — NEW |
| **Episodic** | "In the July 14 session, user rejected draft 1 for being too dense" | `episodic/` (renamed from `sessions/`) |
| **Meta** | "Formatting corrections generalize across industries; factual corrections usually don't" | `knowledge/master/meta-skills/` |

**How a skill gets created (using PDF as the running example):**
1. First request for a PDF report → no matching skill exists → Hermes generates it fresh, burning full tokens, using general knowledge/your instructions.
2. A **self-critique pass** runs automatically right after generation — checked against a fixed design rubric (hierarchy, whitespace, consistency, section flow, not "vibes"). This is a cheap local/small-model pass, not another frontier call.
3. If you correct it (or the critique flags issues you confirm), the correction is distilled into a **skill card** — not the whole conversation, just the reusable procedure:
   ```
   skills/output/pdf_report/
     SKILL.md          <- condensed rules: layout grid, heading style, spacing, tone
     theme.css / template.docx   <- the actual reusable asset, not a description of one
     good_example.pdf  <- 1 reference output, kept small
   ```
4. **Next PDF request**: Master checks `skills/registry.json` for a task-type match *before* generating anything. Match found → load the ~200-token `SKILL.md` + template directly, skip re-deriving design judgment, skip re-explaining your preferences. Only the actual content generation costs tokens; the "how to format it" part is now free.
5. Skills version forward (`pdf_report_v1` → `v2`) as they're refined, same confidence/use-count metadata as memory cards, same decay rule if a version stops getting used.

**Tools are the same idea, one level more concrete**: not just "how," but the literal reusable script/template/config, callable directly instead of regenerated. If Hermes writes a working PDF-generation script once, that script goes in `tools/`, gets called directly next time — it's not re-written from a prompt.

## Part 6: Local-First Resolution Order (the actual token rule you asked for)

Every task should hit this sequence *before* any model call that isn't strictly required:

```
1. Skill/tool match?      (procedural — "do I already know how to do this")
   → similarity search over skills/registry.json
2. Declarative match?     (factual — "do I already know this")
   → similarity search over memory/vector.db
3. Combine what's found, compute a coverage score
   → if coverage is high enough, generate using ONLY local resources
     (skill template + retrieved facts), no fresh reasoning-from-scratch needed
4. Only if coverage is low (genuinely new territory) → full LLM call,
   and the result becomes a CANDIDATE new skill/memory card afterward
```

This is the actual mechanism behind "tokens should only be spent if it's beyond existing local resources" — it's a retrieval-and-coverage gate that runs *before* generation, not a hope that the agent will remember to reuse things.

### Updated storage map

```
/opt/data/.hermes/
├── memory/              # declarative (Part 2)
├── skills/              # procedural — NEW
│   ├── registry.json    # task_type -> skill_id, embedding, version, confidence, use_count
│   ├── output/pdf_report/, docx_memo/, pptx_deck/ ...
│   └── domain/<specialist>/<sub-segment>/
├── tools/                # NEW — actual runnable scripts/templates, called directly
├── episodic/             # structured session hindsight (renamed from sessions/)
├── profiles/
│   ├── master/
│   └── <auto-created specialists>/   # no predefined list, provisional→confirmed lifecycle
├── cold_archive/
├── model_benchmark/
└── audit_log/
```

## Part 7: Priority order to actually build this

1. Stand up the vector store (`memory/vector.db`) and the skill registry (`skills/registry.json`) — these two are the actual token-waste fix, build them before anything else.
2. Build the local-first resolution gate (Part 6) — even a crude version (keyword/embedding match, no fancy coverage scoring yet) immediately stops re-deriving things like PDF formatting from scratch.
3. Wire up one real skill end-to-end as a proof case — PDF report generation is a good first one since you already have the pain point. Get the self-critique → skill-card distillation loop working for this single case before generalizing.
4. Add the dynamic Specialist trigger logic (Part 4) — start simple (embedding-distance threshold + provisional status), refine promotion/merge rules once you see real branching happen.
5. Add the scrub-before-promote check to the learning gate — do this before you take on any client work, not after.
6. Swap task classification (and the local-first coverage check) to a small local model — immediate cost + latency win, and removes a dependency on free-tier availability for something that happens on every single task.
7. Add one paid-model floor to the routing fallback chain, with a hard spend cap.
8. Build the weekly compaction job and dormancy/decay rules last, once you have real usage volume to compact and prune.

---

*Note: free-tier API terms and available model lineups change frequently (confirmed as of mid-2026) — re-verify current terms for any provider before routing client work through it, and check this periodically rather than treating today's validation as permanent.*
