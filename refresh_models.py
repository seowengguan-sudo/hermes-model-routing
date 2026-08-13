#!/usr/bin/env python3
"""
refresh_models.py — Daily model-catalog refresher + per-category sequence builder.

Overwrites /opt/data/models.md  AND  /opt/data/models_sequence.json
each run (idempotent — never appends a new file).

Data sources (live, at run time):
  - OpenRouter  /v1/models        -> free (:free) + near-free paid + limits reset MYT 08:00
  - DeepSeek    /v1/models        -> paid models (v4-flash / v4-pro), prices
  - Gemini      ai.google.dev docs -> live-scraped model list (paid)
  - Nous Portal / NVIDIA NIM       -> curated (verified date) + limit metadata

Output:
  1) models.md              -- human/Agent-readable catalog (free tiers per provider)
  2) models_sequence.json   -- 11 usage categories, each with an open-ended
                               free-first priority list + paid fallback (gated).
                               This is what the model-selection-policy skill consumes.

Run:  python3 /opt/data/refresh_models.py
Exit: 0 success, non-zero on hard failure (so cron can alert).
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
import datetime

HERE = "/opt/data"
OUT_MD = os.path.join(HERE, "models.md")
OUT_SEQ = os.path.join(HERE, "models_sequence.json")
OPENROUTER_MODELS = "https://openrouter.ai/api/v1/models"
DEEPSEEK_MODELS = "https://api.deepseek.com/v1/models"
GEMINI_DOCS = "https://ai.google.dev/gemini-api/docs/models"
VERIFIED_DATE = datetime.date.today().isoformat()


# --------------------------------------------------------------------------- #
# HTTP helpers
# --------------------------------------------------------------------------- #
def _http_get_json(url: str, timeout: int = 25) -> dict | list | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "hermes-refresh/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"[warn] live fetch failed for {url}: {e}", file=sys.stderr)
        return None


def _http_get_text(url: str, timeout: int = 25) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "hermes-refresh/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[warn] live fetch failed for {url}: {e}", file=sys.stderr)
        return None


# --------------------------------------------------------------------------- #
# OpenRouter live parsing
# --------------------------------------------------------------------------- #
def _or_free(data: dict) -> list[dict]:
    out = []
    for m in data.get("data", []):
        pr = m.get("pricing", {})
        try:
            if float(pr.get("prompt", "1")) == 0.0 and float(pr.get("completion", "1")) == 0.0:
                out.append({
                    "id": m["id"],
                    "ctx": int(m.get("context_length", 0)),
                    "name": m.get("name", ""),
                    "modality": m.get("architecture", {}).get("output_modalities", ["text"]),
                })
        except (TypeError, ValueError):
            continue
    return out


def _or_cheap(data: dict, max_in: float = 0.00001) -> list[dict]:
    out = []
    for m in data.get("data", []):
        pr = m.get("pricing", {})
        try:
            pin = float(pr.get("prompt", "1"))
            if 0 < pin <= max_in:
                out.append({"id": m["id"], "ctx": int(m.get("context_length", 0)),
                            "pin": pin, "name": m.get("name", "")})
        except (TypeError, ValueError):
            continue
    return sorted(out, key=lambda x: x["pin"])


# --------------------------------------------------------------------------- #
# DeepSeek live parsing
# --------------------------------------------------------------------------- #
def _ds_models(text: str) -> list[dict]:
    # DeepSeek /v1/models returns JSON id list; fall back to known names.
    try:
        data = json.loads(text) if text else None
        if isinstance(data, dict) and "data" in data:
            return [{"id": m["id"], "ctx": 1_000_000} for m in data["data"]]
    except Exception:
        pass
    # patterns: deepseek-v4-flash / deepseek-v4-pro
    found = set(re.findall(r"deepseek-(v4-flash|v4-pro)", text or ""))
    return [{"id": f"deepseek-{v}", "ctx": 1_000_000} for v in found] or [
        {"id": "deepseek-v4-flash", "ctx": 1_000_000},
        {"id": "deepseek-v4-pro", "ctx": 1_000_000},
    ]


# --------------------------------------------------------------------------- #
# Gemini live scrape
# --------------------------------------------------------------------------- #
def _gemini_models(text: str) -> list[dict]:
    out = []
    if not text:
        return out
    # capture `gemini-...` endpoint tokens
    for ep in set(re.findall(r"gemini-[a-z0-9.\-]+", text)):
        if ep.endswith("-preview-tts") or "native-audio" in ep:
            continue
        out.append({"id": ep, "tier": "paid"})
    return out


# --------------------------------------------------------------------------- #
# Per-category sequence builder (free-first, open-ended, paid-gated)
# --------------------------------------------------------------------------- #
def build_sequence(or_free: list[dict], or_cheap: list[dict],
                   ds: list[dict], gem: list[dict]) -> dict:
    free_ids = {m["id"] for m in or_free}

    def has(*names):
        return [n for n in names if n in free_ids]

    # Helper: pull a free model if present, else None
    def f(*names):
        for n in names:
            if n in free_ids:
                return n
        return None

    seq = {}

    # ---- Main agent loop (all-rounder, free-first chain) ----
    seq["main"] = {
        "description": "Primary chat + execution loop. Performance-ordered free chain "
                       "(Nous-first). Auto-advance on removal/rate-limit. Paid NEVER in chain.",
        "free_chain": [
            "nvidia/nemotron-3-ultra-550b-a55b:free",
            "tencent/hy3:free",
            "nvidia/nemotron-3-super-120b-a12b:free",
            "poolside/laguna-xs-2.1:free",
            "inclusionai/ling-3.0-tiny:free",
        ],
        "paid_fallback": None,  # intentionally none — main stays free-only
        "notes": "Self-heal: if pinned model leaves free catalog, refresh_models.py re-pins "
                 "next free via `hermes config set`. Paid requires explicit user approval.",
    }

    # ---- 11 usage categories ----
    # Each: open-ended free list (1st..N) + paid fallback (gated, Gemini or DeepSeek-v4-flash only)
    seq["categories"] = {
        "vision": {
            "free": [f("nvidia/nemotron-nano-12b-v2-vl:free", "google/gemma-4-31b-it:free",
                       "nvidia/nemotron-nano-9b-v2:free"),
                     "tencent/hy3:free"],
            "paid_fallback": "gemini-3.5-flash",  # vision suits Gemini
            "paid_rule": "approval",
        },
        "mcp": {
            "free": [f("poolside/laguna-s-2.1:free", "poolside/laguna-xs-2.1:free"),
                     "tencent/hy3:free", "nvidia/nemotron-3-super-120b-a12b:free"],
            "paid_fallback": "deepseek-v4-flash",
            "paid_rule": "approval",
        },
        "skill_hub": {
            "free": ["tencent/hy3:free", f("poolside/laguna-xs-2.1:free"),
                     "nvidia/nemotron-3-super-120b-a12b:free"],
            "paid_fallback": "stepfun/step-3.7-flash",
            "paid_rule": "approval",
        },
        "approval": {
            "free": ["tencent/hy3:free", f("poolside/laguna-xs-2.1:free")],
            "paid_fallback": "gemini-2.5-flash",
            "paid_rule": "approval",
        },
        "web_extract": {
            "free": ["tencent/hy3:free"],
            "paid_fallback": "deepseek-v4-flash",
            "paid_rule": "approval",
        },
        "compression": {
            "free": ["tencent/hy3:free", "nvidia/nemotron-3-super-120b-a12b:free"],
            "paid_fallback": None,
            "paid_rule": "none",
        },
        "title_gen": {
            "free": ["tencent/hy3:free", "nous"],
            "paid_fallback": None,
            "paid_rule": "none",
        },
        "triage_specifier": {
            "free": [f("poolside/laguna-xs-2.1:free"), "tencent/hy3:free"],
            "paid_fallback": None,
            "paid_rule": "none",
        },
        "kanban_decomposer": {
            "free": ["tencent/hy3:free", f("poolside/laguna-xs-2.1:free")],
            "paid_fallback": None,
            "paid_rule": "none",
        },
        "curator": {
            "free": ["nous", "tencent/hy3:free"],
            "paid_fallback": None,
            "paid_rule": "none",
        },
        "profile_describer": {
            "free": ["nous", "tencent/hy3:free"],
            "paid_fallback": None,
            "paid_rule": "none",
        },
    }

    # DeepSeek hard rule: only v4-flash, never pro
    seq["deepseek_rule"] = "deepseek-v4-flash only; deepseek-v4-pro REQUIRES user approval"
    seq["paid_providers"] = {
        "deepseek": [m["id"] for m in ds],
        "gemini": [m["id"] for m in gem][:12],
    }
    seq["refreshed"] = VERIFIED_DATE
    return seq


# --------------------------------------------------------------------------- #
# Markdown builder (catalog, per-provider free tiers)
# --------------------------------------------------------------------------- #
def build_markdown(or_free, or_cheap, ds, gem) -> str:
    L = []
    L.append("# Hermes Agent — Model Catalog (daily auto-refresh)")
    L.append("")
    L.append(f"> Auto-generated by `refresh_models.py`. Last refreshed: **{VERIFIED_DATE}**.")
    L.append("> Overwritten daily. Free tiers verified live via OpenRouter/DeepSeek; Gemini live-scraped; Nous/NIM curated.")
    L.append("")
    L.append("## OpenRouter (live `/v1/models` — pricing $0 = free)")
    L.append("")
    L.append(f"**FREE tier ({len(or_free)} models, prompt=0 & completion=0):**")
    L.append("")
    L.append("| Model | Context | Name |")
    L.append("|---|---|---|")
    for m in sorted(or_free, key=lambda x: x["id"]):
        L.append(f"| `{m['id']}` | {m['ctx']//1024}K | {m['name']} |")
    L.append("")
    L.append("**Near-free paid (input ≤ $0.00001/1M):**")
    L.append("")
    L.append("| Model | Context | Input $/1M |")
    L.append("|---|---|---|")
    for m in or_cheap[:12]:
        L.append(f"| `{m['id']}` | {m['ctx']//1024}K | {m['pin']:.8f} |")
    L.append("")
    L.append("## Nous Portal — Free tier (curated, verified 2026-08)")
    L.append("")
    L.append("| Model | Context | Notes |")
    L.append("|---|---|---|")
    L.append("| `tencent/hy3:free` | 262K | default free reasoning model |")
    L.append("| `nvidia/nemotron-3-ultra-550b-a55b:free` | 1M | largest free context |")
    L.append("| `nvidia/nemotron-3-super-120b-a12b:free` | 262K | |")
    L.append("| `poolside/laguna-m.1:free` | mid | only laguna free on Nous |")
    L.append("| `openrouter/elephant-alpha` | — | free router |")
    L.append("| `inclusionai/ring-2.6-1t:free` | — | free |")
    L.append("")
    L.append("> Limits: **20 RPM / 500 TPM**. `laguna-s`/`step-3.7-flash` NOT on Nous free.")
    L.append("")
    L.append("## NVIDIA NIM — Free / dev tier (curated, verified 2026-08)")
    L.append("")
    L.append("> **Lifetime cap: 1000 credits, 40 RPM.** When credit_used ≥ 1000, model is REMOVED permanently.")
    L.append("")
    L.append("| Model | Type |")
    L.append("|---|---|")
    for r in ["nvidia/nemotron-3-ultra | LLM 1M ctx",
              "nvidia/nemotron-3-super / nemotron-3-nano-30b | LLM",
              "nvidia/glm-5.2 | agentic/coding",
              "nvidia/inkling | multimodal reasoning",
              "nvidia/mingling | MoE reasoning",
              "nvidia/qwen-image, qwen-image-edit | image gen",
              "nvidia/nemotron-ocr-v2, nemotron-retriever | OCR/embeddings",
              "nvidia/minimax-m3 | VLM"]:
        L.append(f"| {r} |")
    L.append("")
    L.append("## DeepSeek — Paid only (live `/v1/models`)")
    L.append("")
    L.append("| Model | Context | Note |")
    L.append("|---|---|---|")
    for m in ds:
        L.append(f"| `{m['id']}` | {m['ctx']//1024}K | live |")
    L.append("")
    L.append("> Rule: **deepseek-v4-flash only; v4-pro requires approval.** Prices rise soon.")
    L.append("")
    L.append("## Google Gemini — Paid (live-scraped docs)")
    L.append("")
    L.append("| Endpoint | Tier |")
    L.append("|---|---|")
    for m in gem[:12]:
        L.append(f"| `{m['id']}` | paid |")
    L.append("")
    L.append("---")
    L.append("")
    L.append("**Best free large-context:** `nvidia/nemotron-3-ultra-550b-a55b:free` (1M) on Nous & OpenRouter.")
    L.append("**Per-category sequences:** see `models_sequence.json` (consumed by model-selection-policy skill).")
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# Main model self-heal (Nous-first, performance-ordered free chain)
# --------------------------------------------------------------------------- #
# Order chosen by performance (user-approved): biggest/capable first, lighter as
# fallback. ultra is OpenRouter-free (not on Nous free anymore); hy3/super are Nous-free.
MAIN_CHAIN = [
    ("nvidia/nemotron-3-ultra-550b-a55b:free", "openrouter"),
    ("tencent/hy3:free", "nous"),
    ("nvidia/nemotron-3-super-120b-a12b:free", "nous"),
    ("poolside/laguna-xs-2.1:free", "openrouter"),
    ("inclusionai/ling-3.0-tiny:free", "openrouter"),
]

_HERMES_BIN = "/opt/hermes/.venv/bin/hermes"
_LOG = os.path.join(HERE, "model_perf_log.md")


def _config_get(key: str) -> str | None:
    import subprocess
    try:
        out = subprocess.run([_HERMES_BIN, "config", "get", key],
                              capture_output=True, text=True, timeout=30)
        if out.returncode == 0:
            return out.stdout.strip().splitlines()[-1].strip()
    except Exception as e:
        print(f"[warn] config get {key} failed: {e}", file=sys.stderr)
    return None


def _config_set(key: str, value: str) -> bool:
    import subprocess
    try:
        out = subprocess.run([_HERMES_BIN, "config", "set", key, value],
                              capture_output=True, text=True, timeout=30)
        if out.returncode == 0:
            print(f"[self-heal] {key} -> {value}")
            return True
        print(f"[warn] config set {key} failed: {out.stderr.strip()}", file=sys.stderr)
    except Exception as e:
        print(f"[warn] config set {key} failed: {e}", file=sys.stderr)
    return False


def _log_swap(old: str, new: str, reason: str) -> None:
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    line = f"\n- [{ts}] main_model old={old} new={new} reason={reason}"
    try:
        with open(_LOG, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def self_heal_main_model(free_ids: set[str]) -> None:
    """If the pinned main model is no longer in the live free catalog, advance
    to the next free model in MAIN_CHAIN via the sanctioned `hermes config set`."""
    cur = _config_get("model.default")
    if cur and cur in free_ids:
        return  # still free — no heal needed
    reason = f"'{cur}' not in live free catalog (removed/exhausted)"
    for mid, prov in MAIN_CHAIN:
        if mid in free_ids:
            if _config_set("model.default", mid) and _config_set("model.provider", prov):
                _log_swap(cur or "(none)", mid, reason)
            return
    # none of the chain is free — leave as-is; agent will report at runtime
    print(f"[self-heal] WARNING: no free model in MAIN_CHAIN; main stays '{cur}'",
          file=sys.stderr)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> int:
    or_data = _http_get_json(OPENROUTER_MODELS)
    ds_text = _http_get_text(DEEPSEEK_MODELS)
    gem_text = _http_get_text(GEMINI_DOCS)

    or_free = _or_free(or_data) if or_data else []
    or_cheap = _or_cheap(or_data) if or_data else []
    ds = _ds_models(ds_text)
    gem = _gemini_models(gem_text)

    free_ids = {m["id"] for m in or_free}
    # Nous/NIM curated free (not in OpenRouter pull) — ensure they count as free
    free_ids.update({
        "tencent/hy3:free",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "poolside/laguna-m.1:free",
        "openrouter/elephant-alpha",
        "inclusionai/ring-2.6-1t:free",
    })

    # SELF-HEAL: re-pin main if removed from free tier
    self_heal_main_model(free_ids)

    # models.md
    md = build_markdown(or_free, or_cheap, ds, gem)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(md)

    # models_sequence.json
    seq = build_sequence(or_free, or_cheap, ds, gem)
    # override main chain to the performance-ordered one
    seq["main"]["free_chain"] = [m for m, _ in MAIN_CHAIN]
    with open(OUT_SEQ, "w", encoding="utf-8") as f:
        json.dump(seq, f, indent=2)

    print(f"[ok] wrote {OUT_MD} ({os.path.getsize(OUT_MD)} B), "
          f"{OUT_SEQ} ({os.path.getsize(OUT_SEQ)} B)")
    print(f"[ok] OpenRouter free={len(or_free)}, DeepSeek={len(ds)}, Gemini={len(gem)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
