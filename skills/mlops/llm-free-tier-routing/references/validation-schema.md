# Validation results JSON shape

```
{
  "models": {
    "nvidia/meta/llama-3.1-8b-instruct": {
      "provider": "nvidia",
      "model": "meta/llama-3.1-8b-instruct",
      "strength": "fast",            # fast|general|code|code+|reasoning|expert|auto
      "context": 131072,
      "tasks": {
        "simple_factual":        {"score": 10.0, "latency": 3.93, "note": "ok"},
        "code_generation_basic": {"score": 10.0, "latency": 2.32, "note": "ok"},
        "code_generation_complex":{"score": 10.0, "latency": 5.82, "note": "ok"},
        "debugging_reasoning":    {"score": 10.0, "latency": 7.62, "note": "ok"},
        "architecture_design":    {"score": 10.0, "latency": 10.34,"note": "ok"},
        "cross_domain_synthesis": {"score": 10.0, "latency": 6.06, "note": "ok"}
      },
      "avg_score": 10.0,
      "avg_latency": 5.97,
      "status": "ok"                # ok | partial (some tasks failed)
    }
  },
  "provider_health": {
    "nvidia": "9/66 calls succeeded",
    "openrouter": "27/66 calls succeeded",
    "groq": "0/42 calls succeeded"   # blocked at egress -> router excludes
  },
  "validated_at": "2026-08-06 16:57"
}
```

## Scoring rubric (0-10, heuristic — no LLM judge needed)
- simple_factual: +8 if "5432" present, +2 if <30 words.
- code_generation_*: +4 if `def `/`class `, +2 docstring, +2 exact symbol, +1 import, +1 len>80.
- debugging_reasoning: +3 event loop, +2 asyncio, +2 nest/already/running, +1 await/async, +2 if 50<words<200.
- architecture_design: +4 service/micro/api/database/queue/worker, +3 failure/retry/idempot/consisten, +3 if 100<words<350.
- cross_domain_synthesis: +2 event sourcing, +2 audit/health, +3 similar/difference, +3 if 80<words<250.

## Router rank formula
combined = avg_score + (2.0 if strength in STRENGTH_AFFINITY[task] else 0) - min(avg_latency/10, 1.0)
Exclude any model with avg_score <= 0 (failed validation in this env).
