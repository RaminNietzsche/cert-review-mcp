"""Checker mappings and reverse lookups (checker -> rules).

SEI CERT: data/checker_map.json. MISRA/AUTOSAR: the `checkers` of each record in
data/guidelines.json (cppcheck MISRA addon, cppcheck's own guideline mapping, and
curated clang-tidy / Clang Static Analyzer mappings).
"""
from __future__ import annotations

import functools
import json
from typing import Iterable

from .paths import data_dir
from .rules import norm_id

TIERS = ("deterministic", "partial", "llm-only")


@functools.lru_cache(maxsize=1)
def _load() -> dict:
    return json.loads((data_dir() / "checker_map.json").read_text(encoding="utf-8"))


def info() -> dict:
    d = _load()
    return {k: d[k] for k in ("sources", "tier_definitions", "summary")}


def _tier(checkers: list[dict]) -> str:
    if any(c["specific"] for c in checkers):
        return "deterministic"
    return "partial" if checkers else "llm-only"


@functools.lru_cache(maxsize=1)
def _guideline_entries() -> dict[str, dict]:
    from . import rules as R
    out = {}
    for rid, r in R.guidelines().items():
        cs = [{**c, "available": c.get("available", True)} for c in r.get("checkers", [])]
        out[rid] = {"tier": _tier(cs), "tier_runnable": _tier([c for c in cs if c["available"]]),
                    "checkers": cs, "cert_detectable": None}
    return out


def rule_entry(rule_id: str) -> dict | None:
    rid = norm_id(rule_id)
    return _load()["rules"].get(rid) or _guideline_entries().get(rid)


def tier(rule_id: str, runnable: bool = True) -> str:
    e = rule_entry(rule_id)
    if not e:
        return "unknown"
    return e["tier_runnable" if runnable else "tier"]


def tier_for_tools(rule_id: str, tools) -> str:
    """Tier counting only available checkers of the given tools."""
    e = rule_entry(rule_id)
    if not e:
        return "unknown"
    cs = [c for c in e["checkers"] if c["available"] and c["tool"] in set(tools)]
    if any(c["specific"] for c in cs):
        return "deterministic"
    return "partial" if cs else "llm-only"


@functools.lru_cache(maxsize=1)
def calibrated_confidence() -> dict[str, float]:
    """Per-checker precision on the dev corpus (data/confidence_calibration.json)."""
    p = data_dir() / "confidence_calibration.json"
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("scores") or {}
    except (OSError, ValueError, AttributeError):
        return {}


@functools.lru_cache(maxsize=1)
def reverse_index() -> dict[tuple[str, str], list[dict]]:
    """(tool, checker) -> [{rule_id, specific, confidence?}] for SEI CERT."""
    idx: dict[tuple[str, str], list[dict]] = {}
    for rid, e in _load()["rules"].items():
        for c in e["checkers"]:
            ent = {"rule_id": rid, "specific": c["specific"]}
            if c.get("confidence") is not None:
                ent["confidence"] = c["confidence"]
            idx.setdefault((c["tool"], c["checker"]), []).append(ent)
    return idx


@functools.lru_cache(maxsize=1)
def guideline_reverse_index() -> dict[tuple[str, str], list[dict]]:
    """(tool, checker) -> [{rule_id, specific, standard}] for MISRA/AUTOSAR."""
    from . import rules as R
    idx: dict[tuple[str, str], list[dict]] = {}
    for rid, e in _guideline_entries().items():
        std = R.guidelines()[rid]["standard"]
        for c in e["checkers"]:
            idx.setdefault((c["tool"], c["checker"]), []).append(
                {"rule_id": rid, "specific": c["specific"], "standard": std,
                 "line_regex": c.get("line_regex")})
    return idx


def checkers_for_tool(tool: str, lang: str | None = None, available_only: bool = True,
                      standards: Iterable[str] | None = None) -> set[str]:
    """Checker names of `tool` that map to the selected standards (default SEI CERT)."""
    from . import rules as R
    stds = set(R.expand_standards(standards))
    out = set()
    if stds & set(R.CERT_STANDARDS):
        for e in _load()["rules"].values():
            for c in e["checkers"]:
                if c["tool"] == tool and (c["available"] or not available_only):
                    out.add(c["checker"])
    for rid, e in _guideline_entries().items():
        if R.guidelines()[rid]["standard"] not in stds:
            continue
        for c in e["checkers"]:
            if c["tool"] == tool and (c["available"] or not available_only):
                out.add(c["checker"])
    return out


def coverage(lang: str | None = None, kind: str | None = None,
             standard: str | Iterable[str] | None = None) -> dict:
    from . import rules as R
    res: dict[str, list[str]] = {t: [] for t in TIERS}
    res_run: dict[str, list[str]] = {t: [] for t in TIERS}
    res_ext: dict[str, list[str]] = {t: [] for t in TIERS}
    for r in R.list_rules(lang=lang, kind=kind, standard=standard):
        e = rule_entry(r["id"])
        res[e["tier"]].append(r["id"])
        res_run[e["tier_runnable"]].append(r["id"])
        res_ext[e.get("tier_extended", e["tier_runnable"])].append(r["id"])
    n = sum(len(v) for v in res.values())
    return {"total": n,
            "all_mappings": {k: len(v) for k, v in res.items()},
            "runnable_toolchain": {k: len(v) for k, v in res_run.items()},
            "extended_toolchain": {k: len(v) for k, v in res_ext.items()},
            "rules_all_mappings": res, "rules_runnable": res_run, "rules_extended": res_ext,
            "toolchain": _load()["sources"]["toolchain_versions"]}
