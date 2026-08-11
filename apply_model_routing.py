#!/usr/bin/env python3
"""
apply_model_routing.py -- Deploy the daily model-selection decisions to
Hermes runtime config.

reads:  /opt/data/models_sequence.json  (written by refresh_models.py cron)
        /opt/data/model_deadlist.json   (written by probe_models.py)
writes: config.yaml auxiliary.<task>.model  (+ .provider where needed)
        via `hermes config set`

This is the missing consumer: refresh_models.py builds the per-category
sequence, but nothing applied it back to the running agent. This script
does -- for every auxiliary USE AS slot, it picks the best *available* model
from that slot's free-first chain and writes it (and the correct provider)
into config.yaml. The agent reads auxiliary.<task>.model on every call, so the
change takes effect immediately (no restart needed).

Self-fix for vision: NVIDIA catalog models do NOT use the OpenRouter ":free"
suffix. model_router._MODEL_PROVIDER_FIX maps the bare/free id to the correct
(provider, model-id) so vision_analyze uses nvidia/nemotron-nano-12b-v2-vl via
the NVIDIA endpoint (where it works) instead of OpenRouter (where it 404s).

FAIL-SAFE: if a task already has a healthy pinned model, it is left alone.
Paid fallback is NEVER written -- free-tier only.
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

import model_router as r

TASK_TO_CATEGORY = r._TASK_TO_CATEGORY
MODEL_PROVIDER_FIX = r._MODEL_PROVIDER_FIX


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
    for m in chain or []:
        m = (m or "").strip()
        if m:
            return m
    return None


def _fix_provider(model: str):
    """Return (provider, corrected_model) using the known fix map."""
    return MODEL_PROVIDER_FIX.get(model, (None, model))


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
        chain = chain + list(main.get("free_chain", []) or [])

        best = _best_free(chain, dead)
        if not best:
            continue
        if cfg_model == best:
            continue
        if cfg_model and cfg_model not in dead and cfg_model in (chain or []):
            continue

        prov, corrected = _fix_provider(best)
        if _config_set(f"auxiliary.{task}.model", corrected):
            applied += 1
            if prov:
                cur_prov = _config_get(f"auxiliary.{task}.provider") or ""
                if cur_prov != prov:
                    _config_set(f"auxiliary.{task}.provider", prov)

    # Main loop self-heal
    main_chain = main.get("free_chain", []) or []
    cur = _config_get("model.default") or ""
    if not (cur and cur not in dead and (not main_chain or cur in main_chain)):
        best = _best_free(main_chain, dead)
        if best and best != cur:
            if _config_set("model.default", best):
                applied += 1

    print(f"[ok] applied {applied} model routing change(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
