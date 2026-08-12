# Model Performance Log (learning loop)

Agent appends one block per task that used an auxiliary/main model.
Used to re-rank `models_sequence.json` free-first ordering over time.

Format:
- [timestamp] category=... model=... quality=(good|ok|poor) reason=...
- quality=poor → demote model for that category in next sequence rebuild.

---
<!-- entries appended by agent at runtime -->

- [2026-08-10T15:03:53] main_model old=tencent/hy3:REMOVED new=nvidia/nemotron-3-ultra-550b-a55b:free reason='tencent/hy3:REMOVED' not in live free catalog (removed/exhausted)
- [2026-08-10T15:04:45] main_model old=nvidia/nemotron-3-ultra:REMOVED new=nvidia/nemotron-3-ultra-550b-a55b:free reason='nvidia/nemotron-3-ultra:REMOVED' not in live free catalog (removed/exhausted)