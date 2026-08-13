#!/usr/bin/env python3
"""
validate.py — benchmark every free chat/code model across task types.
Run: python3 validate.py  (writes results.json)
Robust: 8 parallel workers, 25s timeout, skips providers that fail.
"""
import json, os, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

with open('/opt/data/model_benchmark/model_inventory.json') as f:
    DATA = json.load(f)
INVENTORY = DATA['inventory']

KEYS = {}
with open('/opt/data/.env') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            KEYS[k] = v.strip()

PROVIDER_BASE = {
    'nvidia':     'https://integrate.api.nvidia.com/v1',
    'groq':       'https://api.groq.com/openai/v1',
    'openrouter': 'https://openrouter.ai/api/v1',
    'cerebras':   'https://api.cerebras.ai/v1',
    'huggingface':'https://api-inference.huggingface.co/models',
    'nous_portal':'https://portal.nousresearch.com/v1',
}
KEY_ENV = {
    'nvidia': 'NVIDIA_API_KEY', 'groq': 'GROQ_API_KEY', 'openrouter': 'OPENROUTER_API_KEY',
    'cerebras': 'CEREBRAS_API_KEY', 'huggingface': 'HF_TOKEN', 'nous_portal': None,
}
TIMEOUT = 25
BENCHMARKS = {
    'simple_factual':          "What is the default port for PostgreSQL? Reply in one sentence.",
    'code_generation_basic':   "Write a Python function `is_palindrome(s)` that returns True if string s is a palindrome, ignoring spaces and case. Include a docstring.",
    'code_generation_complex': "Write a Python class `LRUCache` with get(key) and put(key, value) methods using OrderedDict and a max_size parameter. Include type hints and a short docstring.",
    'debugging_reasoning':     "A FastAPI app returns intermittent 500 errors: 'RuntimeError: asyncio.run() cannot be called from a running event loop'. What is the root cause and the fix? Keep under 120 words.",
    'architecture_design':     "Design a microservice architecture for a payment reconciliation system. List key services, responsibilities, data flow, and 2 failure modes. Under 250 words.",
    'cross_domain_synthesis':  "Analyze how event sourcing from financial systems could be adapted for healthcare audit trails. Give 3 similarities and 2 critical differences. Under 150 words.",
}

def call_model(provider, model_id, prompt, max_tokens=400):
    if provider == 'huggingface':
        url = f"{PROVIDER_BASE['huggingface']}/{model_id}"
        key = KEYS.get('HF_TOKEN', '')
        payload = json.dumps({"inputs": prompt, "parameters": {"max_new_tokens": max_tokens}}).encode()
        req = urllib.request.Request(url, data=payload, headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    else:
        url = f"{PROVIDER_BASE[provider]}/chat/completions"
        key = KEYS.get(KEY_ENV[provider], '')
        payload = json.dumps({"model": model_id, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.3}).encode()
        req = urllib.request.Request(url, data=payload, headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode()
        lat = time.time() - t0
        obj = json.loads(raw)
        text = obj[0]['generated_text'] if provider == 'huggingface' else obj['choices'][0]['message']['content']
        return text.strip(), lat, None
    except Exception as e:
        return None, time.time() - t0, str(e)[:120]

def score_output(task_id, text):
    if not text: return 0.0, "empty"
    s = 0.0; notes = []; tl = text.lower()
    if task_id == 'simple_factual':
        if '5432' in text: s += 8; notes.append("correct port")
        else: s += 2
        if len(text.split()) < 30: s += 2
    elif task_id.startswith('code_generation'):
        if 'def ' in text or 'class ' in text: s += 4
        if '"""' in text or "'''" in text: s += 2
        if 'def is_palindrome' in text or 'class LRUCache' in text: s += 2
        if 'import' in text or 'from ' in text: s += 1
        if len(text) > 80: s += 1
    elif task_id == 'debugging_reasoning':
        if 'event loop' in tl: s += 3
        if 'asyncio' in tl: s += 2
        if 'nest' in tl or 'already' in tl or 'running' in tl: s += 2
        if 'await' in tl or 'async def' in tl: s += 1
        if 50 < len(text.split()) < 200: s += 2
    elif task_id == 'architecture_design':
        if any(w in tl for w in ['service','micro','api','database','queue','worker']): s += 4
        if any(w in tl for w in ['failure','fail','retry','idempot','consisten']): s += 3
        if 100 < len(text.split()) < 350: s += 3
    elif task_id == 'cross_domain_synthesis':
        if 'event sourcing' in tl: s += 2
        if 'audit' in tl or 'health' in tl: s += 2
        if 'similar' in tl or 'difference' in tl: s += 3
        if 80 < len(text.split()) < 250: s += 3
    return min(s, 10.0), ", ".join(notes) if notes else "ok"

jobs = []
for prov, info in INVENTORY.items():
    if prov == 'nous_portal': continue
    for m in info['models']:
        for tid in BENCHMARKS:
            jobs.append((prov, m['id'], m['strength'], m['context'], tid))

results = {}
provider_health = {}
def run_job(job):
    prov, mid, strength, ctx, tid = job
    return prov, mid, strength, ctx, tid, *call_model(prov, mid, BENCHMARKS[tid])

print(f"Validating {len(jobs)} calls...")
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = [ex.submit(run_job, j) for j in jobs]
    done = 0
    for fut in as_completed(futs):
        prov, mid, strength, ctx, tid, text, lat, err = fut.result()
        key = f"{prov}/{mid}"
        results.setdefault(key, {'provider': prov, 'model': mid, 'strength': strength, 'context': ctx, 'tasks': {}, 'avg_score': 0, 'avg_latency': 0, 'status': 'ok'})
        if err:
            results[key]['tasks'][tid] = {'score': 0, 'latency': round(lat,2), 'error': err[:100]}
            results[key]['status'] = 'partial'
        else:
            sc, note = score_output(tid, text)
            results[key]['tasks'][tid] = {'score': sc, 'latency': round(lat,2), 'note': note}
        provider_health.setdefault(prov, []).append(not bool(err))
        done += 1
        if done % 20 == 0: print(f"  {done}/{len(jobs)}")

for key, rec in results.items():
    scores = [t['score'] for t in rec['tasks'].values() if 'score' in t]
    lats = [t['latency'] for t in rec['tasks'].values() if t.get('latency',0) > 0]
    rec['avg_score'] = round(sum(scores)/len(scores), 2) if scores else 0
    rec['avg_latency'] = round(sum(lats)/len(lats), 2) if lats else 0

with open('/opt/data/model_benchmark/results.json', 'w') as f:
    json.dump({'models': results, 'provider_health': {k: f"{sum(v)}/{len(v)} ok" for k,v in provider_health.items()}, 'validated_at': time.strftime('%Y-%m-%d %H:%M')}, f, indent=2)
print("Done. Wrote results.json")
