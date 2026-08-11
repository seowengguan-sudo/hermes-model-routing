#!/usr/bin/env python3
"""
probe_models.py -- Lightweight live health probe for the free-tier models
used by Hermes auxiliary tasks + main loop.

For each model in models_sequence.json, send a 3-token chat completion with
a short timeout. On failure (timeout / 4xx / 5xx / connection error) the
model is written to /opt/data/model_deadlist.json (TTL 30 min), which
model_router.py and apply_model_routing.py then skip.

This closes the gap between cron runs: if a model suddenly 404s mid-day,
the next apply_model_routing.py (or next cron) will route around it. It can
also be run manually right after a failure is observed.

Run:  python3 /opt/data/probe_models.py
"""
from __future__ import annotations

import json
import os
import time
import urllib.request

HERE = "/opt/data"
SEQ = os.path.join(HERE, "models_sequence.json")
DEAD = os.path.join(HERE, "model_deadlist.json")
DEAD_TTL = 30 * 60

# Provider -> chat completions endpoint + auth header env (best-effort).
_PROVIDERS = {
    "openrouter": ("https://openrouter.ai/api/v1/chat/completions",
                   "OPENROUTER_API_KEY"),
    "nous": ("https://inference-api.nousresearch.com/v1/chat/completions",
             "NOUS_API_KEY"),
    "nvidia": ("https://integrate.api.nvidia.com/v1/chat/completions",
               "NVIDIA_API_KEY"),
    "deepseek": ("https://api.deepseek.com/v1/chat/completions",
                 "DEEPSEEK_API_KEY"),
}


def _probe(model: str, provider: str, timeout: float = 12.0) -> bool:
    if provider not in _PROVIDERS:
        # Unknown provider -- assume reachable (don't kill it blindly).
        return True
    url, env = _PROVIDERS[provider]
    key = os.environ.get(env, "")
    if not key:
        # No key -- cannot probe; assume reachable to avoid false-dead.
        return True
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 3,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
        "User-Agent": "hermes-probe/1.0",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


def main() -> int:
    if not os.path.exists(SEQ):
        print(f"[skip] {SEQ} missing", file=__import__("sys").stderr)
        return 0
    try:
        with open(SEQ, "r", encoding="utf-8") as f:
            seq = json.load(f)
    except Exception as e:
        print(f"[skip] {SEQ} unreadable: {e}", file=__import__("sys").stderr)
        return 0

    dead = {}
    if os.path.exists(DEAD):
        try:
            dead = json.load(open(DEAD)) or {}
        except Exception:
            dead = {}

    now = time.time()
    dead = {k: v for k, v in dead.items()
            if isinstance(v, (int, float)) and v > now}

    # Collect (model, provider) pairs. Provider is inferred from model prefix
    # where possible (nvidia/..., tencent/..., poolside/... -> openrouter).
    def _prov(m: str) -> str:
        if m.startswith("nvidia/"):
            return "nvidia"
        if m.startswith("tencent/") or m.startswith("minimax/") \
                or m.startswith("inclusionai/") or m.startswith("deepseek/") \
                or m.startswith("nous"):
            return "nous"
        return "openrouter"

    candidates = []
    for m in seq.get("main", {}).get("free_chain", []):
        candidates.append((m, _prov(m)))
    for cat in (seq.get("categories", {}) or {}).values():
        for m in (cat or {}).get("free", []) or []:
            candidates.append((m, _prov(m)))

    checked = set()
    for m, p in candidates:
        m = (m or "").strip()
        if not m or m in checked:
            continue
        checked.add(m)
        ok = _probe(m, p)
        status = "OK" if ok else "DEAD"
        print(f"[probe] {m:45s} {p:10s} {status}")
        if not ok:
            dead[m] = now + DEAD_TTL

    with open(DEAD, "w", encoding="utf-8") as f:
        json.dump(dead, f)
    print(f"[ok] dead-list now has {len(dead)} entry(ies): {list(dead.keys())}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
