# Local model recommendations for the local-first routing gate

The Master+Specialist design needs (a) a local embedding model for the retrieval gate and
(b) a local classifier/router model for task tagging — both MUST run in-container, NOT via a
remote `:free` API (naming a remote free model "local" reintroduces the free-tier dependency).

## Embedding (retrieval gate) — choose MULTILINGUAL
Clients are Malaysian (Bahasa Malaysia, Chinese, Tamil, English). `all-MiniLM-L6-v2` is
**English-only (384-dim)** — reject it for this user.
- Primary: **`BAAI/bge-m3`** — 100+ languages, 8192-token ctx, dense+sparse+ColBERT; heavier but
  correct for multilingual.
- Light alternative: **`paraphrase-multilingual-MiniLM-L12-v2`** (covers ms/zh/ta/en, ~420MB) if
  container RAM is tight.
- Avoid: `all-MiniLM-L6-v2`, `all-mpnet-base-v2` (English-only).

## Router / classifier (16-class task tagging + triage-specifier)
- **`Qwen2.5-1.5B-Instruct`** (or `Qwen2.5-Coder-1.5B`) via **Ollama / llama.cpp on CPU** inside
  Docker/WSL2. ~1GB quantized, runs on CPU, strong multilingual — fits the regional-language need and
  the 16-category routing job. For pure triage/specifier, even `Qwen2.5-0.5B` suffices.
- This removes the routing dependency on remote free tiers entirely.

## Why this matters
The PDF architecture diagram claims "task classification via local small model (no API call)". Using
`laguna-xs`/`ling-3.0-tiny` (OpenRouter `:free`, remote) violates that. Real local inference closes it.
