"""
model_router.py -- Runtime model-selection library for Hermes Agent.

Goal (design discussion 2026-08): make auxiliary model selection
capability-aware and self-healing instead of a fixed dead-pin.

This module is the consumer that was missing: it reads the daily
``models_sequence.json`` produced by ``refresh_models.py`` (the daily cron)
and resolves, for each auxiliary task, the *best currently-available* model
from that task's free-first chain. When a model fails in flight
(404 / 429 / timeout), mark_unhealthy() records it so the next resolution
skips it.

Design invariants:
  * FAIL-SAFE: any error (missing file, bad JSON, import failure) returns
    ``None`` / unchanged values so the caller keeps its original model.
    This module NEVER breaks the live loop.
  * NO network calls at import or at selection time -- reads a local JSON
    file and an in-memory + on-disk dead-list. Health is fed in by callers.
  * Lives in HERMES_HOME (/opt/data) so it is writable and survives container
    rebuilds. For in-process runtime hooking, copy to /opt/hermes/agent/ and
    patch auxiliary_client._resolve_task_provider_model (see INTEGRATION).

Integration points:
  * apply_routing.py imports select_aux_model()/select_main_model() and writes
    the chosen models back into config.yaml via `hermes config set`, which the
    running agent reads on every call. This is the deployable path today.
  * For per-call fallback inside the agent process, hook
    auxiliary_client.py: call select_aux_model() in _resolve_task_provider_model()
    and mark_unhealthy() in the transient-retry failure path.
"""

from __future__ import annotations

import json
import os
import threading
import time
from typing import Dict, List, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_SEQ_PATH = os.path.join(_HERE, "models_sequence.json")
_DEAD_PATH = os.path.join(_HERE, "model_deadlist.json")

# config.yaml auxiliary.<task> key -> category key in models_sequence.json
_TASK_TO_CATEGORY = {
    "vision": "vision",
    "mcp": "mcp",
    "skill_hub": "skill_hub",
    "skills_hub": "skill_hub",
    "approval": "approval",
    "web_extract": "web_extract",
    "compression": "compression",
    "title_generation": "title_gen",
    "title_gen": "title_gen",
    "triage_specifier": "triage_specifier",
    "kanban_decomposer": "kanban_decomposer",
    "profile_describer": "profile_describer",
    "curator": "curator",
}

_DEAD_TTL = 30 * 60  # 30 minutes

_lock = threading.Lock()
_dead: Dict[str, float] = {}
_loaded_at: float = 0.0
_cached_seq: Optional[dict] = None


def _now() -> float:
    return time.time()


def _load_seq() -> Optional[dict]:
    global _loaded_at, _cached_seq
    try:
        if _cached_seq is not None and (_now() - _loaded_at) < 60:
            return _cached_seq
        with open(_SEQ_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        _cached_seq = data
        _loaded_at = _now()
        return data
    except Exception:
        return None


def _load_dead() -> None:
    global _dead
    try:
        if os.path.exists(_DEAD_PATH):
            with open(_DEAD_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                cutoff = _now() - _DEAD_TTL
                _dead = {k: v for k, v in raw.items()
                         if isinstance(v, (int, float)) and v > cutoff}
    except Exception:
        _dead = {}


def _save_dead() -> None:
    try:
        with open(_DEAD_PATH, "w", encoding="utf-8") as f:
            json.dump(_dead, f)
    except Exception:
        pass


def _is_dead(model: str) -> bool:
    if not model:
        return False
    expiry = _dead.get(model)
    if expiry is None:
        return False
    if expiry < _now():
        with _lock:
            _dead.pop(model, None)
            _save_dead()
        return False
    return True


def mark_unhealthy(provider: str, model: str) -> None:
    """Record that ``model`` just failed so the next resolution skips it."""
    if not model:
        return
    with _lock:
        _load_dead()
        _dead[model] = _now() + _DEAD_TTL
        _save_dead()


def select_aux_model(task: str, configured_provider: str = "",
                     configured_model: str = "") -> Tuple[str, str]:
    """Return (provider, model) for an auxiliary task.

    Resolution:
      1. Configured model healthy -> return unchanged.
      2. Else walk the category free chain, skipping dead models.
      3. Nothing healthy -> return configured model unchanged (fail-safe).
    """
    configured_model = (configured_model or "").strip()
    category = _TASK_TO_CATEGORY.get((task or "").strip().lower(), "")

    if configured_model and not _is_dead(configured_model):
        return configured_provider or "", configured_model

    seq = _load_seq()
    if not seq:
        return configured_provider or "", configured_model

    chain: List[str] = []
    try:
        cats = seq.get("categories", {})
        if category and category in cats:
            chain = list((cats[category] or {}).get("free", []) or [])
        main = seq.get("main", {}) or {}
        chain = chain + list(main.get("free_chain", []) or [])
    except Exception:
        return configured_provider or "", configured_model

    seen = set()
    for m in chain:
        m = (m or "").strip()
        if not m or m in seen:
            continue
        seen.add(m)
        if _is_dead(m):
            continue
        if configured_model and m == configured_model:
            return configured_provider or "", m
        if configured_model:
            # configured was dead -> return this healthy fallback
            return configured_provider or "", m

    if configured_model:
        return configured_provider or "", configured_model
    for m in chain:
        m = (m or "").strip()
        if m:
            return configured_provider or "", m
    return "", ""


def select_main_model() -> Tuple[str, str]:
    """Return (provider, model) for the main loop from the free chain."""
    seq = _load_seq()
    if not seq:
        return "", ""
    try:
        main = seq.get("main", {}) or {}
        chain = list(main.get("free_chain", []) or [])
    except Exception:
        return "", ""
    seen = set()
    for m in chain:
        m = (m or "").strip()
        if not m or m in seen:
            continue
        seen.add(m)
        if not _is_dead(m):
            return "", m
    for m in chain:
        m = (m or "").strip()
        if m:
            return "", m
    return "", ""


def router_available() -> bool:
    return _load_seq() is not None
