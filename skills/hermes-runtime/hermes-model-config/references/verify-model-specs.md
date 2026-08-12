# Verify Model Specs Live (before committing to config)

Re-probe providers rather than trusting memory/cached catalogs. Stale data caused a
wrong 1.05M-context claim for `poolside/laguna-s-2.1:free` (actual: 262K on OpenRouter).

## OpenRouter (free tier + context)
```bash
curl -s https://openrouter.ai/api/v1/models | python3 -c "
import sys,json
d=json.load(sys.stdin)
free=[(m['id'],m.get('context_length',0)) for m in d['data']
      if float(m.get('pricing',{}).get('prompt',1))==0 and float(m.get('pricing',{}).get('completion',1))==0]
free.sort()
print('\n'.join(f'{i}  {c//1024}K' for i,c in free))
"
```

## DeepSeek (returns 401 without key — fall back to known names)
```bash
curl -s https://api.deepseek.com/v1/models   # 401 if no DEEPSEEK_API_KEY
# Known paid models: deepseek-v4-flash, deepseek-v4-pro (no free tier)
```

## Gemini (HTML docs — scrape endpoint tokens)
```bash
curl -s https://ai.google.dev/gemini-api/docs/models | grep -oE 'gemini-[a-z0-9.\-]+' | sort -u
```

## Rules
- Free = OpenRouter `pricing.prompt==0 and pricing.completion==0`.
- Never assert a free-model COUNT or CONTEXT from memory. Re-verify live.
- DeepSeek has NO free model; default to v4-flash, gate v4-pro behind approval.
