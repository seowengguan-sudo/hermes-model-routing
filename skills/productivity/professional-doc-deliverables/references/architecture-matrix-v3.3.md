# Hermes Multi-Agent Architecture — Model Selection & Verification (v3.3)

Condensed, swappable reference for the deliverable built in the Aug-8 session.
Use as the knowledge bank for any architecture-matrix / PDF update task; replace
provider/model specifics when the project changes.

## Provider priority (free-tier chain)
Nous Portal  →  OpenRouter  →  NVIDIA NIM  →  Paid (Gemini / DeepSeek, approval-gated).
Groq / Cerebras / HF are WAF-blocked from the user's egress ASN (TTNET MY) — excluded.

## Provider limits (verify against live plan; sources vary)
- Nous Portal free: 50 RPM / 500K TPM, daily reset MYT 08:00 (user claimed 200 RPM — flagged to confirm plan tier).
- OpenRouter free: 20 req/min, **50 req/day** — binding constraint for agentic multi-call work.
- NVIDIA NIM free: **one lifetime credit** — exhaustion is permanent; router must escalate to paid, never retry.
- Paid (Gemini): only gemini-2.5-flash reachable (pro / 1.5-* / 2.0-* return 404).
- Paid (DeepSeek): v4-flash + v4-pro OK. v4-Pro reserved for super-complex reasoning / pro-doc ONLY.

## 16 USE_AS categories → 4-slot sequence [Nous → OR → NIM → Paid]
"—" = no suitable free model at that tier; router skips to next slot.
- auxiliary: step-3.7-flash → nemotron-3-nano-30b → llama-3.1-8b → deepseek-v4-flash
- vision: — → nemotron-nano-12b-vl → — → gemini-2.5-flash  (hy3 is NOT a vision model)
- web-expert: minimax-m2 → gemma-4-26b → llama-3.1-70b → gemini-2.5-flash
- compression: hy3 → nemotron-nano-9b-v2 → llama-3.1-8b → deepseek-v4-flash
- skill-hub: deepseek-v3.2 → gpt-oss-20b → llama-3.1-70b → deepseek-v4-flash
- approval: — → nemotron-3.5-content-safety → — → gemini-2.5-flash  (hy3 is NOT moderation)
- mcp: — → gpt-oss-20b → llama-3.1-70b → deepseek-v4-flash  (hy3 is NOT tool-use)
- title-gen: hy3 → nemotron-nano-9b-v2 → llama-3.1-8b → deepseek-v4-flash
- triage-specifier: laguna-xs → ling-3.0-tiny → llama-3.1-8b → deepseek-v4-flash
- kanban-decomposer: laguna-s → laguna-xs → llama-3.1-70b → deepseek-v4-flash  (distinct, not dup)
- profile-describer: minimax-m2 → gemma-4-26b → llama-3.1-70b → gemini-2.5-flash
- curator: hy3.1 → nemotron-3-super-120b → llama-3.1-70b → deepseek-v4-flash
- reasoning: step-3.7-flash → nemotron-3-ultra-550b → llama-3.1-70b → deepseek-v4-flash
- coding: deepseek-v3.2 → north-mini-code → llama-3.1-70b → deepseek-v4-flash
- professional-documentation: minimax-m2 → nemotron-3-ultra-550b → llama-3.1-70b → deepseek-v4-flash
- general-chat: hy3 → gemma-4-26b → llama-3.1-8b → gemini-2.5-flash

## Local models (truly offline gate — no API call)
- Classify (16 USE_AS) + triage: Qwen2.5-1.5B-Instruct (Ollama/CPU, multilingual, ~1GB).
- Embeddings: BAAI/bge-m3 (multilingual — NOT all-MiniLM-L6-v2 which is English-only, would mis-rank BM/zh).
- Optional light triage: Qwen2.5-0.5B.

## 17-step agentic control loop (closed, grounded)
1 Local Classifier → 2 Local Embedding → 3 Coverage Gate → 4 Situation Read (atomic state.db; stale>TTL→UNKNOWN) →
5 Budget Check → 6 Sequence Selector (UCB exploration) → 7 Token Pre-Estimate → 8 Checkpoint Save → 9 Dispatch →
10 Verify-then-Accept **+ FACTUAL GROUNDING (claim→source; reject unsupported)** → 11 Repair Loop →
12 Learn (INDEPENDENT score: user-weight + gold-set; write to CANDIDATE matrix, staged) →
13 Paid Escalation Gate (UI approval) → 14 Failure/Contradiction (adjudication queue) →
15 Probe Liveness (stale→UNKNOWN→escalate/stop) → 16 Contradiction Adjudication → 17 Goal Termination (timeout→explain).

## Hallucination / learning-safety rules (do NOT over-claim)
- Verify step must trace claims→sources; self-confidence NOT trusted.
- "Verified" memory ≠ proven-true; contradictions→adjudication, never silent pick.
- Learning scored independently (gold-set + user weight), not self-rated; correctness floor (wrong→efficiency 0).
- Staging matrix + rollback; UCB exploration prevents ossification; weekly anti-drift gold-set.

## Artifact scope rule
User wanted the DESIGN DOC / MATRIX updated — NOT the agent system built. Keep that separation.
