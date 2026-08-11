#!/usr/bin/env python3
"""
vision_bridge.py -- Standalone vision ingestion for Hermes Agent.

Problem it solves: the active reasoning model (e.g. hy3:free) has NO native
vision, and the built-in vision_analyze tool routes the VLM through OpenRouter
where nvidia/nemotron-nano-12b-v2-vl:free returns 404. But the SAME VLM works
perfectly via the NVIDIA endpoint (proven by probe_models.py).

This script is the self-fix: it calls the VLM directly on the NVIDIA endpoint
and returns a TEXT description. The reasoning model consumes that text -- so
the agent "sees" the image without needing native multimodal input.

Usage:
  python3 vision_bridge.py <image_path> ["optional question"]

It reads NVIDIA_API_KEY from /opt/data/.env (not from env, to avoid leaks).
The model used is nvidia/nemotron-nano-12b-v2-vl:free (the only free VLM in
the catalog). Returns the VLM's caption/answer as plain text on stdout.

This is also what model_router should fall back to when vision_analyze 404s.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
_ENV = os.path.join(_HERE, ".env")
_MODEL = "nvidia/nemotron-nano-12b-v2-vl"
_URL = "https://integrate.api.nvidia.com/v1/chat/completions"


def _load_nvidia_key() -> str:
    try:
        with open(_ENV, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("NVIDIA_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return os.environ.get("NVIDIA_API_KEY", "")


def _b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def describe(image_path: str, question: str = "Describe this image in detail.") -> str:
    key = _load_nvidia_key()
    if not key:
        return "[vision_bridge] ERROR: NVIDIA_API_KEY not found in .env"
    if not os.path.exists(image_path):
        return f"[vision_bridge] ERROR: image not found: {image_path}"

    mime = "image/jpeg"
    if image_path.lower().endswith(".png"):
        mime = "image/png"

    payload = {
        "model": _MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {
                    "url": f"data:{mime};base64,{_b64(image_path)}"}},
            ],
        }],
        "max_tokens": 1024,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(_URL, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
        "User-Agent": "hermes-vision-bridge/1.0",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read().decode("utf-8"))
        return resp["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[vision_bridge] ERROR: {e}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: vision_bridge.py <image_path> [question]")
        sys.exit(1)
    q = sys.argv[2] if len(sys.argv) > 2 else "Describe this image in detail."
    print(describe(sys.argv[1], q))
