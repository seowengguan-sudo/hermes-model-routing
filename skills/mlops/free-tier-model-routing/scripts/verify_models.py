#!/usr/bin/env python3
"""
verify_models.py — Live-probe every free/paid model and emit a status matrix.

Reads provider keys from /opt/data/.env and the Nous OAuth token from
/opt/data/shared/nous_auth.json, then probes each model with a tiny chat
completion and records the real HTTP outcome.

Output: prints a table AND writes /opt/data/model/verify_results.json
Status codes: OK | 429 | 403 | 400 | 410 | 404 | GW | NO_KEY | TO(timeout)

Run:  python3 scripts/verify_models.py
"""
import json, os, time, urllib.request, urllib.error

ROOT = "/opt/data"
KEYS = {}
with open(os.path.join(ROOT, ".env")) as f:
    for line in f:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            KEYS[k] = v.strip()

# Nous OAuth (gateway verification)
NOUS = {}
try:
    NOUS = json.load(open(os.path.join(ROOT, "shared/nous_auth.json")))
except Exception:
    pass
NOUS_TOKEN = NOUS.get("access_token", "")
NOUS_URL = NOUS.get("inference_base_url", "").rstrip("/") or "https://inference-api.nousresearch.com/v1"


def probe(url, key, model, timeout=20):
    payload = {"model": model, "messages": [{"role": "user", "content": "Reply OK"}],
               "max_tokens": 3, "temperature": 0}
    req = urllib.request.Request(url + "/chat/completions", data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            json.loads(r.read().decode())
        return "OK", round(time.time() - t0, 1)
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}", round(time.time() - t0, 1)
    except Exception as e:
        return str(e)[:30], round(time.time() - t0, 1)


OR_URL = "https://openrouter.ai/api/v1"
NV_URL = "https://integrate.api.nvidia.com/v1"
GEM_URL = "https://generativelanguage.googleapis.com/v1beta/openai"

MODELS = [
    # provider, model, base_url, key
    ("Nous Portal", "tencent/hy3:free", NOUS_URL, NOUS_TOKEN),
    ("Nous Portal", "tencent/hy3.1:free", NOUS_URL, NOUS_TOKEN),
    ("Nous Portal", "deepseek/deepseek-v3.2:free", NOUS_URL, NOUS_TOKEN),
    ("Nous Portal", "minimax/minimax-m2:free", NOUS_URL, NOUS_TOKEN),
    ("OpenRouter", "nvidia/nemotron-3-super-120b-a12b:free", OR_URL, KEYS.get("OPENROUTER_API_KEY", "")),
    ("OpenRouter", "nvidia/nemotron-3-ultra-550b-a55b:free", OR_URL, KEYS.get("OPENROUTER_API_KEY", "")),
    ("OpenRouter", "nvidia/nemotron-3-nano-30b-a3b:free", OR_URL, KEYS.get("OPENROUTER_API_KEY", "")),
    ("OpenRouter", "openai/gpt-oss-20b:free", OR_URL, KEYS.get("OPENROUTER_API_KEY", "")),
    ("OpenRouter", "google/gemma-4-26b-a4b-it:free", OR_URL, KEYS.get("OPENROUTER_API_KEY", "")),
    ("OpenRouter", "google/gemma-4-31b-it:free", OR_URL, KEYS.get("OPENROUTER_API_KEY", "")),
    ("OpenRouter", "poolside/laguna-s-2.1:free", OR_URL, KEYS.get("OPENROUTER_API_KEY", "")),
    ("OpenRouter", "cohere/north-mini-code:free", OR_URL, KEYS.get("OPENROUTER_API_KEY", "")),
    ("OpenRouter", "inclusionai/ling-3.0-tiny:free", OR_URL, KEYS.get("OPENROUTER_API_KEY", "")),
    ("OpenRouter", "nvidia/nemotron-nano-9b-v2:free", OR_URL, KEYS.get("OPENROUTER_API_KEY", "")),
    ("OpenRouter", "nvidia/nemotron-nano-12b-v2-vl:free", OR_URL, KEYS.get("OPENROUTER_API_KEY", "")),
    ("NVIDIA NIM", "meta/llama-3.1-8b-instruct", NV_URL, KEYS.get("NVIDIA_API_KEY", "")),
    ("NVIDIA NIM", "meta/llama-3.1-70b-instruct", NV_URL, KEYS.get("NVIDIA_API_KEY", "")),
    ("NVIDIA NIM", "meta/llama-3.3-70b-instruct", NV_URL, KEYS.get("NVIDIA_API_KEY", "")),
    ("Gemini (Paid)", "gemini-2.5-flash", GEM_URL, KEYS.get("GEMINI_API_KEY", "")),
    ("Gemini (Paid)", "gemini-2.5-pro", GEM_URL, KEYS.get("GEMINI_API_KEY", "")),
    ("Gemini (Paid)", "gemini-2.0-flash", GEM_URL, KEYS.get("GEMINI_API_KEY", "")),
    ("DeepSeek (Paid)", "deepseek/deepseek-v4-flash", OR_URL, KEYS.get("OPENROUTER_API_KEY", "")),
    ("DeepSeek (Paid)", "deepseek/deepseek-v4-pro", OR_URL, KEYS.get("OPENROUTER_API_KEY", "")),
]

results = {}
for prov, model, url, key in MODELS:
    if not key:
        results[(prov, model)] = ("NO_KEY", 0)
        continue
    results[(prov, model)] = probe(url, key, model)

os.makedirs(os.path.join(ROOT, "model"), exist_ok=True)
out = {f"{p}||{m}": {"status": s, "lat": l} for (p, m), (s, l) in results.items()}
json.dump(out, open(os.path.join(ROOT, "model/verify_results.json"), "w"), indent=2)

for (p, m), (s, l) in results.items():
    print(f"  {s:12s} {l:5}s  {p:14s} {m}")

ok = sum(1 for s, _ in results.values() if s == "OK")
print(f"\nProbed {len(results)} models | OK: {ok} | others flagged in verify_results.json")
