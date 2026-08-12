# mentor-ai-daily RUN LOG
Format: YYYY-MM-DD | concept | test-posed | mastery-prediction
---
2026-08-11 | AI stack (LLM+Agent+RAG+Workflow) | (AM; gap: define visibility as DATA) | n/a
2026-08-11 | Tool use vs Agentic workflow | define 3 must-have tools (tool surface) | predicted: grasped
2026-08-11 | Guardrails & autonomy dial | label each tool reversible vs irreversible | predicted: grasped
2026-08-11 | When a tool call is enough vs agentic | one-shot task vs never-loop-without-human | predicted: partial
2026-08-11 | Evals (prove correctness before trust) | get_permit 96% vs auto_schedule 60% dial cutoff | predicted: will grasp
2026-08-11 | Precision/Recall & confusion matrix (accuracy lies for rare events) | auto_schedule 2x2: TP/FP/FN/TN + which metric gates safety | predicted: will grasp
2026-08-11 | Golden set / ground-truth curation (leakage, stratify, freeze+version) | golden_v1 built from live final permit dates scores 100% recall — name the defect, the column fix, and the right block-case count | predicted: high on defect/fix, medium on stratification
2026-08-12 | Golden-set scaffold DELIVERED (golden_v1.csv + score_eval.py) — stopped teaser loop | run score_eval.py on real tool predictions; report 2x2 + ship-gate number + missed block case | predicted: artifact lands; audit sign-off pending
