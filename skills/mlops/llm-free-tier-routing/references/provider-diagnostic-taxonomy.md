# Provider / Model Diagnostic Taxonomy (live-check playbook)

Captured 2026-08-07 from a WSL2/Docker Hermes deployment. Use this to
interpret raw API errors when validating free-tier providers so you
diagnose correctly instead of guessing "Docker is blocking it" or
"the key is dead."

## Egress reality (kills the usual wrong theory)
- Docker on WSL2 NATs through the Windows host. The provider sees your
  residential ISP IP, NOT a datacenter ASN. So "remove Docker and it'll
  work" is FALSE -- the egress IP is identical in or out of the container.
- Always check the real egress IP: query an IP-echo service then ipinfo.io
  for org/country. If it's a consumer ISP, that's the ASN providers may ban.

## Error to meaning table
| Symptom | True cause | Action |
|---|---|---|
| HTTP 403 + Cloudflare error code 1010 | Provider behind Cloudflare; your ASN is banned (reputation/geo), not a key or format problem. | Switch egress ASN (VPN/cellular) OR route via the provider's OAuth gateway path. Not a Docker fix. |
| HTTP 429 | Rate-limited / throttled -- NOT blocked, NOT exhausted forever. | Back off; retry later. Often recovers. |
| HTTP 410 + "end of life on <timestamp>" | Model retired by the provider (e.g. NVIDIA deepseek-v4-flash EOL 2026-08-07). | Remove from free pool; do NOT relist. Was NOT a token-quota issue. |
| HTTP 404 | Model ID no longer exists on that provider (renamed/relocated). | Re-query /v1/models for the current slug. |
| HTTP 400 + "not a valid model ID" | Wrong slug format, not exhaustion. OpenRouter free IDs are nvidia/...:free -- do NOT prepend openrouter/. | Use the exact ID from the provider's /v1/models list. |
| Name or service not known (DNS fail) | Subdomain not in sandbox DNS allowlist (e.g. api-inference.huggingface.co). | Network-policy quirk, not a model problem. |
| The read operation timed out | Model present but queued/slow (free-tier contention). | Raise timeout, retry; usually recoverable. |

## Provider-specific facts (this deployment, 2026-08-07)
- OpenRouter free: 14 :free models total. 13/14 live-OK; gemma-4-31b-it:free was 429. Slugs are bare (nvidia/...:free), NO openrouter/ prefix. Key alive -- confirmed by openrouter/free returning OK.
- NVIDIA NIM free: meta/llama-3.1-8b-instruct (validated 9.83/10, ~0.7s) and meta/llama-3.1-70b-instruct working. llama-3.3-70b-instruct timed out (queued). DeepSeek-V4 FLASH+PRO = HTTP 410 (EOL). Only deepseek-coder-6.7b-instruct remains.
- Nous Portal: works via OAuth gateway (live chat uses tencent/hy3:free). Raw portal.nousresearch.com/v1 calls from a script get 429 (Vercel Security Checkpoint) -- gateway-vs-direct gap, NOT model unavailability. Use Hermes's native provider path to verify Nous models.
- Groq / Cerebras: Cloudflare 1010 from this ASN. GLM-5.2 is paid-only on BOTH OpenRouter and NVIDIA now (no :free slug) -- the earlier free fallback was a temporary NVIDIA promo that ended.
- DeepSeek direct: deepseek/deepseek-v4-flash is paid on OpenRouter (~0.09/M tok). The "exhausted" log earlier was a paid credit limit, not a global token cap.

## Live-check recipe
```python
import json, urllib.request, urllib.error
KEYS={}
for line in open('/opt/data/.env'):
    line=line.strip()
    if '=' in line and not line.startswith('#'):
        k,v=line.split('=',1); KEYS[k]=v.strip()
def test(provider, model, key, timeout=25):
    url = ('https://openrouter.ai/api/v1/chat/completions' if provider=='openrouter'
           else 'https://integrate.api.nvidia.com/v1/chat/completions')
    payload={'model':model,'messages':[{'role':'user','content':'hi'}],'max_tokens':5}
    req=urllib.request.Request(url, data=json.dumps(payload).encode(),
         headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})
    try:
        urllib.request.urlopen(req, timeout=timeout).read(); return 'OK'
    except urllib.error.HTTPError as e: return f'HTTP {e.code}'
    except Exception as e: return str(e)[:40]
# Enumerate real free IDs first: GET {base}/models, filter ':free'
```
Always enumerate /v1/models and filter :free BEFORE testing -- never
hardcode slugs from memory (they drift; DeepSeek-V4 and old GLM free tiers
proved this).
