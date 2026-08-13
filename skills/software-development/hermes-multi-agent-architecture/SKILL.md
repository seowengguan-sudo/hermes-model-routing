---
name: hermes-multi-agent-architecture
description: "Master and per-domain Specialist Agents via Hermes profiles."
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Hermes Multi-Agent Architecture (Master + Specialists)

Design an enterprise-grade setup where a **Master Agent** strategizes and
routes to **per-industry/per-client Specialist Agents**, each isolated via a
Hermes profile, with structured knowledge, user-approved learning, and
anti-hallucination checks.

## When to use
- User wants to serve multiple clients/industries without cross-contamination.
- User asks for "Super Agent" vs "separate agents per industry" guidance.
- Architecting a self-improving, cost-efficient agentic system.

## Core design (validated in a real session)
- **Master Agent** (default profile): classification engine (confidence ≥80% →
  proceed; <80% → ask the user, never assume), cross-domain pattern library,
  model-tier selection, synthesis, and proposing learnings for approval.
- **Specialist Agents**: one Hermes **profile** per industry (e.g. `fintech`,
  `healthcare`), each with its own `state.db`, `memory/`, `skills/`.
- **Sub-segments**: within a specialist, organize knowledge by sub-domain
  (Payments, Lending, ...). Load only the relevant sub-segment into context to
  control token cost.
- **Knowledge taxonomy**:
  - `knowledge/master/` (meta-skills, cross-domain patterns, industry summaries)
  - `knowledge/specialists/<industry>/` (domain skills, per-client, patterns)
  - `knowledge/shared/` (tool configs, style guides, templates)
  - `archive/` for deprecated knowledge (searchable, not loaded)

## Learning cadence (user-approved)
A learning is written ONLY after:
1. Specialist confirms it is useful for its domain.
2. Master Agent analyzes cross-domain applicability and drafts a proposal with
   background/context.
3. **User approves or comments.** Trivial fixes (typo, rate-limit workaround,
   obvious correction) may be auto-applied with notification; new patterns,
   skill edits, memory facts, and new-industry creation require explicit approval.
This prevents silent knowledge corruption and keeps user + agent growing together.

## Anti-hallucination rules (embed in every specialist skill)
- Every output cites a stored source (file:line). No trace → flag uncertainty.
- Certainty ladder: Verified / Inferred (flagged) / Unknown (stop & ask) /
  Contradictory (stop & show both).
- Verification checklist at end of each task: tested, claimed traced, unknowns
  flagged, no client-confidential data leaked, cross-checked vs Master patterns.

## Model tiering integrates here
Master + specialists run on free tiers (see `hermes-model-tiering`). Master uses
strong free model; specialists use smaller free models by task complexity.
PAID models (Gemini/DeepSeek direct) require user permission.

## Pitfalls
- Do NOT put all clients in one profile/volume — no isolation, cross-leak risk.
- Do NOT inject all skills/memory every session — context bloat. Use sub-segment
  loading + on-demand `skill_view`.
- Do NOT auto-write knowledge without approval — corrupts the knowledge base.
- Containers: verify no Windows (`/mnt/c`) or host bind mounts; prefer named
  Docker volumes. A single `state.db` holds all conversations (SQLite binary,
  not plain text) — browse via DB viewer, not text editor.
