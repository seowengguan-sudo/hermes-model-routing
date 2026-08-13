# NVIDIA VLM — exact working request

## Verified working call (returns 200, reads image as text)
Tested this session on `/opt/data/GitHub.jpg` via `vision_bridge.py` plus a
direct chat-completions probe. Two facts were confirmed the hard way:

- **Model id MUST be `nvidia/nemotron-nano-12b-v2-vl` (with `v2`).**
  `nvidia/nemotron-nano-12b-vl` (no v2) → HTTP 404 "page not found".
- **Provider MUST be `nvidia`.** Routing the VLM through OpenRouter 404s
  ("Couldn't find that") — the model only lives on NVIDIA's endpoint.

```python
import os, json, base64, urllib.request

key = None
for line in open("/opt/data/.env"):
    line = line.strip()
    if line.startswith("NVIDIA_API_KEY="):
        key = line.split("=", 1)[1].strip().strip('"').strip("'")

img = base64.b64encode(open("/opt/data/IMAGE.jpg", "rb").read()).decode()
body = json.dumps({
    "model": "nvidia/nemotron-nano-12b-v2-vl",   # MUST have v2; no :free suffix
    "messages": [{"role": "user", "content": [
        {"type": "text", "text": "Transcribe visible text."},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}}
    ]}]
}).encode()

req = urllib.request.Request(
    "https://integrate.api.nvidia.com/v1/chat/completions",
    data=body,
    headers={"Content-Type": "application/json",
             "Authorization": f"Bearer {key}"},
    method="POST")
with urllib.request.urlopen(req, timeout=90) as r:
    resp = json.loads(r.read())
    print(resp["choices"][0]["message"]["content"])
```

## Gotchas confirmed this session
- Two distinct 404s, same diagnosis — verify via the model list endpoint first:
  `GET https://integrate.api.nvidia.com/v1/models` (auth: `Bearer <key>`).
- Free NVIDIA VLM is **non-deterministic**: ~1-in-3 calls drifted off-topic.
  Mitigation (verified): on a drifted result, **retry once with a tightened
  prompt** ("ONLY transcribe visible text; do not describe the scene.
  Do not fabricate."). Do not trust the first answer on free tier.
- `auxiliary.vision.provider` MUST be `nvidia` so the built-in `vision_analyze`
  tool dispatches correctly; otherwise it routes to a 404.
- `stepfun/step-3.7-flash` is a **text** model — cannot ingest images at all.
