"""Access to data/checker_map.json and reverse lookups (checker -> rules)."""
from __future__ import annotations

import functools
import json

from .paths import data_dir
from .rules import norm_id


@functools.lru_cache(maxsize=1)
def _load() -> dict:
    return json.loads((data_dir() / "checker_map.json").read_text(encoding="utf-8"))


def info() -> dict:
    d = _load()
    return {k: d[k] for k in ("sources", "tier_definitions", "summary")}


def rule_entry(rule_id: str) -> dict | None:
    return _load()["rules"].get(norm_id(rule_id))


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
def reverse_index() -> dict[tuple[str, str], list[dict]]:
    """(tool, checker) -> [{rule_id, specific, confidence}]"""
    idx: dict[tuple[str, str], list[dict]] = {}
    for rid, e in _load()["rules"].items():
        for c in e["checkers"]:
            ent = {"rule_id": rid, "specific": c["specific"]}
            if c.get("confidence") is not None:
                ent["confidence"] = c["confidence"]
            idx.setdefault((c["tool"], c["checker"]), []).append(ent)
    return idx


def checkers_for_tool(tool: str, lang: str | None = None, available_only: bool = True) -> set[str]:
    out = set()
    for rid, e in _load()["rules"].items():
        if lang and not (rid.endswith("-CPP") == (lang == "cpp")) and lang in ("c", "cpp"):
            # CodeChecker maps C checkers to both standards; keep rule-language filter
            # on the finding side instead of here.
            pass
        for c in e["checkers"]:
            if c["tool"] == tool and (c["available"] or not available_only):
                out.add(c["checker"])
    return out


def coverage(lang: str | None = None, kind: str | None = None) -> dict:
    from . import rules as R
    res = {"deterministic": [], "partial": [], "llm-only": []}
    res_run = {"deterministic": [], "partial": [], "llm-only": []}
    res_ext = {"deterministic": [], "partial": [], "llm-only": []}
    for r in R.list_rules(lang=lang, kind=kind):
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
