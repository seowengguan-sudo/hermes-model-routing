Consultant/developer via Hermes on WSL2 (/opt/data). Security-conscious, per-client isolation. GitHub: github.com/seowengguan-sudo. Thinks in systems; prefers validation/accuracy. NEVER overclaim unless enforced — always close with honest residual (design≠running system unless code built). Excel readable.
§
Egress (WSL2 Docker): IP 161.142.137.99 (TTNET, Penang MY). Cloudflare WAF blocks Groq/Cerebras (1010); HF DNS-blocked; Nous API rate-limited. Fix = gateway or different ASN/VPN. Free-tier priority: Nous→OR→NIM→Paid (approval). OR=50/day, NIM=one-time credit, Nous~50RPM. Paid: gemini-2.5-flash/deepseek-v4-flash(-pro). Local: Qwen2.5-1.5B + bge-m3. xlsx via openpyxl only.
§
Visual deliverables: wants HIGH-CONTRAST/sharp/readable — saturated fills, white bold text, dark outlines, dark caption. Light tints + thin grey lines read as washed-out. Confirmed in architecture-PDF work.
§
Style: bottom-line answer FIRST, then justification (verdict→why→next action).
§
Document reader agent: fully local PII/PHI redaction. Earlier multi-file build at /opt/data/ (redaction_engine.py etc.) superseded by the single-file OAKAI Document Reader doc_reader_onefile.py @ /opt/data/projects/doc_reader/ (live :8765).
§
Skills: hermes-cron-model-pinning (Pitfall #15). Document reader agent built & verified (10/10). Added bash-heredoc-pitfall ref to python-venv-setup skill.
§
User operates in a Docker container under WSL2 (Windows host). Docker uses network_mode: host. Server binding to 127.0.0.1 is NOT reachable from Windows browser. Must bind to 0.0.0.0 and provide SSH tunnel instructions for browser access. Container IP (e.g. 172.174.0.2) is reachable from WSL2 but not directly from Windows. NOTE: /opt/data inside container is isolated ext4 mount - WSL2 cannot access these paths. Users share error screenshots as XTR*.jpg in /opt/data/workspace/Samples/ - use vision_analyze to read them.
§
OAKAI Document Reader POC: single-file doc_reader_onefile.py @ /opt/data/projects/doc_reader/ (live :8765, synced to enhanced_doc_reader_v2/). Redaction design pref = co-occurrence/same-row clustering, not per-field regex. 'Good enough'=stop, do NOT auto-build flagged residuals.