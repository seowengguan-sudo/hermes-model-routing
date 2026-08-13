Consultant/developer via Hermes on WSL2 (/opt/data). Security-conscious, per-client isolation. GitHub: github.com/seowengguan-sudo. Thinks in systems; prefers validation/accuracy. NEVER overclaim unless enforced — always close with honest residual (design≠running system unless code built). Excel readable.
§
Egress (WSL2 Docker): IP 161.142.137.99 (TTNET, Penang MY). Cloudflare WAF blocks Groq/Cerebras (1010); HF DNS-blocked; Nous API rate-limited. Fix = gateway or different ASN/VPN. Free-tier priority: Nous→OR→NIM→Paid (approval). OR=50/day, NIM=one-time credit, Nous~50RPM. Paid: gemini-2.5-flash/deepseek-v4-flash(-pro). Local: Qwen2.5-1.5B + bge-m3. xlsx via openpyxl only.
§
Visual deliverables: wants HIGH-CONTRAST/sharp/readable — saturated fills, white bold text, dark outlines, dark caption. Light tints + thin grey lines read as washed-out. Confirmed in architecture-PDF work.
§
Style: user wants bottom-line answer FIRST, then justification. Cut preamble; 'just give me the answer' / 'stop over-engineering'. Verdict (1) → why (1 para) → next action (1 line).
§
MODEL (2026-08): main=poolside/laguna-s-2.1:free (Nous Portal free). Cron jobs PINNED to tencent/hy3:free (Nous) — model-default changes break unpinned crons (#44585 drift guard). hy3 fallback=500TPM. Vision=nvidia/nemotron-nano-12b-v2-vl (NVIDIA, requires -vl). KB: /opt/data/knowledge/INDEX.md map — mentor/ (AI edu), by_industry/<vertical>/<client>/, raw/, workspace/ (daily digest + 14d auto-prune). Cron mentor-ai-daily (15:00/03:00 MYT) + learn-pensolar (15:00 MYT), deliver=local. ≤5 bullets/pull, full→raw.
§
CRON VERIFICATION (pending): All 6 crons pinned. Gateway fix: was stopped because s6 service slot never registered; fixed via S6ServiceManager().register_profile_gateway('default'). Gateway running PID 46427, status=ok.