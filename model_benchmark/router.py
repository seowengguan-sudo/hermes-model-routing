#!/usr/bin/env python3
"""
Intelligent Model Router — Hermes Agent (validation-driven)
Uses /opt/data/model_benchmark/results.json to pick the best FREE-tier model
per task. Falls back to heuristic when no data. Never selects a provider that
failed validation in this environment unless forced.
"""
import json, os

RESULTS_PATH = '/opt/data/model_benchmark/results.json'

STRENGTH_AFFINITY = {
    'simple_factual':          ['fast', 'general', 'auto'],
    'code_generation_basic':   ['fast', 'code', 'general', 'auto'],
    'code_generation_complex': ['code', 'code+', 'reasoning', 'expert'],
    'debugging_reasoning':     ['reasoning', 'code+', 'expert', 'auto'],
    'architecture_design':     ['reasoning', 'expert', 'code+'],
    'cross_domain_synthesis':  ['expert', 'reasoning', 'auto'],
}
PROVIDER_PRIORITY = ['nvidia', 'openrouter', 'cerebras', 'groq', 'huggingface', 'nous_portal']


def classify_complexity(prompt):
    words = len(prompt.split())
    score = 1
    p = prompt.lower()
    if any(w in p for w in ['design','architect','system','microservice']): score = max(score,7)
    if any(w in p for w in ['debug','fix','error','root cause','why']): score = max(score,6)
    if any(w in p for w in ['class','function','algorithm','implement']): score = max(score,5)
    if any(w in p for w in ['cross','compare','analyze','synthesi','adapt']): score = max(score,8)
    if words > 120: score = max(score,7)
    elif words > 60: score = max(score,5)
    elif words > 30: score = max(score,3)
    return min(score,10)


def classify_task_type(prompt):
    p = prompt.lower()
    if any(w in p for w in ['debug','error','fix','root cause']): return 'debugging_reasoning'
    if any(w in p for w in ['design','architect','microservice','system']): return 'architecture_design'
    if any(w in p for w in ['cross','compare','analyze','synthesi','adapt','between']): return 'cross_domain_synthesis'
    if 'class ' in p or 'algorithm' in p or 'data structure' in p: return 'code_generation_complex'
    if 'function' in p or 'script' in p or 'code' in p: return 'code_generation_basic'
    if any(w in p for w in ['what is','port','how many','true or false','capital']): return 'simple_factual'
    return 'code_generation_basic'


def load_results():
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH) as f:
            d = json.load(f)
        return d.get('models', {}), d.get('provider_health', {})
    return {}, {}


def route(prompt, force_provider=None):
    complexity = classify_complexity(prompt)
    task_type = classify_task_type(prompt)
    models, health = load_results()

    if not models:
        return heuristic_route(prompt, complexity, task_type)

    # Build usable candidate pool (exclude clearly-failed models: score 0 + partial)
    preferred = STRENGTH_AFFINITY.get(task_type, ['general'])
    candidates = []
    for key, rec in models.items():
        sc = rec.get('avg_score', 0)
        if sc <= 0:
            continue  # failed validation in this env
        strength = rec.get('strength','general')
        bonus = 2.0 if strength in preferred else 0.0
        lat_pen = min(rec.get('avg_latency',5)/10.0, 1.0)
        combined = sc + bonus - lat_pen
        candidates.append((combined, key, rec))

    if force_provider:
        candidates = [c for c in candidates if c[2]['provider'] == force_provider]

    candidates.sort(reverse=True)
    chain = [{'provider': c[2]['provider'], 'model': c[2]['model'],
              'score': c[2]['avg_score'], 'latency': c[2].get('avg_latency')}
             for c in candidates[:5]]

    if chain:
        best = chain[0]
        reason = (f"Task '{task_type}' (complexity {complexity}). Validated best free model: "
                  f"{best['provider']}/{best['model']} (score {best['score']}, "
                  f"latency {best['latency']}s). {len(chain)} fallbacks queued.")
        return {'provider': best['provider'], 'model': best['model'],
                'complexity': complexity, 'task_type': task_type,
                'reason': reason, 'fallback_chain': chain}
    return heuristic_route(prompt, complexity, task_type)


def heuristic_route(prompt, complexity, task_type):
    if complexity <= 3: target = 'fast'
    elif complexity <= 6: target = 'code'
    else: target = 'expert'
    defaults = {
        'fast':   ('nvidia', 'meta/llama-3.1-8b-instruct'),
        'code':   ('nvidia', 'meta/llama-3.1-8b-instruct'),
        'expert': ('openrouter', 'nvidia/nemotron-3-ultra-550b-a55b:free'),
    }
    prov, model = defaults.get(target, ('nvidia', 'meta/llama-3.1-8b-instruct'))
    reason = (f"No validation data. Heuristic '{task_type}' complexity {complexity} "
              f"-> {prov}/{model} (free).")
    return {'provider': prov, 'model': model, 'complexity': complexity,
            'task_type': task_type, 'reason': reason,
            'fallback_chain': [{'provider': prov, 'model': model}]}


if __name__ == '__main__':
    import sys
    sample = sys.argv[1] if len(sys.argv) > 1 else "Design a microservice architecture for payment reconciliation."
    print(json.dumps(route(sample), indent=2))
