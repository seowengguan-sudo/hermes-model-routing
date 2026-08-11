#!/usr/bin/env python3
"""
apply_model_routing.py -- Deploy the daily model-selection decisions to
Hermes runtime config.

reads:  /opt/data/models_sequence.json  (written by refresh_models.py cron)
writes: config.yaml auxiliary.<task>.model  (via `hermes config set`)
        /opt/data/model_deadlist.json     (dead models skipped)

This is the missing consumer: refresh_models.py builds the per-category
sequence, but nothing applied it back to the running agent. This script
does -- for every auxiliary USE AS slot, it picks the best *available*
model from that slot's free-first chain and writes it into config.yaml.
The agent reads auxiliary.<task>.model on every call, so the change takes
effect immediately (no restart needed).

It is FAIL-SAFE: if a task already has a healthy pinned model, it leaves it
alone. It only swaps a model that is (a) dead on the dead-list, or
(b) absent from the live free catalog. Paid fallback is NEVER written -- the
script only ever writes free-tier models.

Run:  python3 /opt/data/apply_model_routing.py
Also invoked by the daily cron after refresh_models.py.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = "/opt/data"
SEQ = os.path.join(HERE, "models_sequence.json")
DEAD = os.path.join(HERE, "model_deadlist.json")
HERMES = "/opt/hermes/bin/hermes"

# config.yaml auxiliary.<task> key -> category key in models_sequence.json
TASK_TO_CATEGORY = {
    "vision": "vision",
    "mcp": "mcp",
    "skill_hub": "skill_hub",
    "approval": "approval",
    "web_extract": "web_extract",
    "compression": "compression",
    "title_generation": "title_gen",
    "triage_specifier": "triage_specifier",
    "kanban_decomposer": "kanban_decomposer",
    "profile_describer": "profile_describer",
    "curator": "curator",
}


def _load_dead() -> dict:
    try:
        if os.path.exists(DEAD):
            with open(DEAD, "r", encoding="utf-8") as f:
                return json.load(f) or {}
    except Exception:
        pass
    return {}


def _config_get(key: str) -> str | None:
    try:
        out = subprocess.run([HERMES, "config", "get", key],
                              capture_output=True, text=True, timeout=30)
        if out.returncode == 0:
            return out.stdout.strip().splitlines()[-1].strip()
    except Exception as e:
        print(f"[warn] config get {key} failed: {e}", file=sys.stderr)
    return None


def _config_set(key: str, value: str) -> bool:
    try:
        out = subprocess.run([HERMES, "config", "set", key, value],
                              capture_output=True, text=True, timeout=30)
        if out.returncode == 0:
            print(f"[apply] {key} -> {value}")
            return True
        print(f"[warn] config set {key} failed: {out.stderr.strip()}",
              file=sys.stderr)
    except Exception as e:
        print(f"[warn] config set {key} failed: {e}", file=sys.stderr)
    return False


def _best_free(chain, dead: dict) -> str | None:
    for m in chain or []:
        m = (m or "").strip()
        if not m:
            continue
        if m in dead:
            continue
        return m
    # fallback: first entry even if dead (TTL may lapse)
    for m in chain or []:
        m = (m or "").strip()
        if m:
            return m
    return None


def main() -> int:
    if not os.path.exists(SEQ):
        print(f"[skip] {SEQ} missing -- run refresh_models.py first",
              file=sys.stderr)
        return 0
    try:
        with open(SEQ, "r", encoding="utf-8") as f:
            seq = json.load(f)
    except Exception as e:
        print(f"[skip] {SEQ} unreadable: {e}", file=sys.stderr)
        return 0

    dead = _load_dead()
    cats = seq.get("categories", {})
    main = seq.get("main", {}) or {}

    applied = 0
    for task, category in TASK_TO_CATEGORY.items():
        cfg_model = _config_get(f"auxiliary.{task}.model") or ""
        entry = cats.get(category) or {}
        chain = list(entry.get("free", []) or [])
        # main chain as last resort
        chain = chain + list(main.get("free_chain", []) or [])

        best = _best_free(chain, dead)
        if not best:
            continue
        if cfg_model == best:
            continue  # already correct, leave alone
        if cfg_model and cfg_model not in dead and cfg_model in (chain or []):
            # configured model is still free & healthy -> keep it
            if cfg_model in [m for m in (chain or []) if m]:
                continue
        if _config_set(f"auxiliary.{task}.model", best):
            applied += 1

    # Main loop self-heal (mirrors refresh_models.self_heal_main_model)
    main_chain = main.get("free_chain", []) or []
    cur = _config_get("model.default") or ""
    if cur and cur not in dead and (not main_chain or cur in main_chain):
        pass  # healthy, leave
    else:
        best = _best_free(main_chain, dead)
        if best and best != cur:
            # provider resolution: try to read current provider
            prov = _config_get("model.provider") or ""
            if _config_set("model.default", best):
                applied += 1
                if prov:
                    _config_set("model.provider", prov)

    print(f"[ok] applied {applied} model routing change(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
