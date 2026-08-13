# Local-First Gate Model Picks

Why run locally (no API call) for the routing/retrieval gate, and which models.

## Task classification (16 USE_AS categories) + triage
- **Qwen2.5-1.5B-Instruct** via Ollama / llama.cpp on CPU (~1 GB quantized).
  - Multilingual (ms/zh/ta/en) — fits Malaysian client base.
  - Removes the routing dependency on remote free tiers entirely.
  - Light triage/specifier alternative: Qwen2.5-0.5B (~0.4 GB).

## Embeddings for skill/fact retrieval
- **BAAI/bge-m3** (multilingual, 100+ languages, 8192-tok context, dense+sparse) ≈ 2.2 GB.
- **DO NOT use `all-MiniLM-L6-v2`** — it is English-only (384-dim). With BM/zh/ta/en clients it silently mis-ranks retrieval, corrupting the local-first gate's output.

## Why this matters
The original design named `laguna-xs` / `ling-3.0-tiny` as the "local" router — but those are OpenRouter `:free` (remote) models, defeating local-first and re-adding the free-tier dependency. The genuine local pick is Qwen2.5-1.5B.

## Container notes
- Bundle inside the Docker/WSL2 container so the gate is offline-first.
- CPU-only is acceptable at 1.5B for classification latency.
