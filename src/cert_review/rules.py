"""Access to the bundled SEI CERT rule database."""
from __future__ import annotations

import functools
import json
import re
from dataclasses import dataclass
from typing import Iterable

from .paths import data_dir

ID_RE = re.compile(r"^[A-Za-z]{3}\d{2}-(?:C|CPP)$")


def norm_id(rule_id: str) -> str:
    return rule_id.strip().upper()


@functools.lru_cache(maxsize=1)
def _load() -> dict:
    return json.loads((data_dir() / "rules.json").read_text(encoding="utf-8"))


def source_info() -> dict:
    return _load()["source"]


@functools.lru_cache(maxsize=1)
def all_rules() -> dict[str, dict]:
    return {r["id"]: r for r in _load()["rules"]}


def get(rule_id: str) -> dict | None:
    return all_rules().get(norm_id(rule_id))


def is_valid_id(rule_id: str) -> bool:
    return norm_id(rule_id) in all_rules()


def list_rules(lang: str | None = None, category: str | None = None,
               kind: str | None = None, level: str | None = None,
               detectable: bool | None = None,
               ids: Iterable[str] | None = None) -> list[dict]:
    out = []
    idset = {norm_id(i) for i in ids} if ids is not None else None
    for r in all_rules().values():
        if lang and r["lang"] != lang.lower():
            continue
        if category and r["category"] != category.upper():
            continue
        if kind and r["kind"] != kind.lower():
            continue
        if level and (r.get("risk") or {}).get("level") != level.upper():
            continue
        if detectable is not None and (r.get("risk") or {}).get("detectable") != detectable:
            continue
        if idset is not None and r["id"] not in idset:
            continue
        out.append(r)
    return out


def summary(r: dict) -> dict:
    risk = r.get("risk") or {}
    return {"id": r["id"], "lang": r["lang"], "kind": r["kind"],
            "category": r["category"], "title": r["title"],
            "severity": risk.get("severity"), "likelihood": risk.get("likelihood"),
            "priority": risk.get("priority"), "level": risk.get("level"),
            "detectable": risk.get("detectable"), "url": r["url"]}


def rule_text(r: dict, include_examples: bool = True, max_chars: int | None = None) -> str:
    """Plain-text rendering of a rule (title, rationale, examples, risk)."""
    parts = [f"{r['id']}. {r['title']}", "", r["intro"]]
    if include_examples:
        for ex in r["examples"]:
            nc = ex["noncompliant"]
            if nc:
                parts += ["", f"## {nc['heading']}", nc["text"]]
                for b in nc["code"]:
                    parts += [f"```{b['lang'] or ''}", b["code"], "```"]
            for c in ex["compliant"]:
                parts += ["", f"## {c['heading']}", c["text"]]
                for b in c["code"]:
                    parts += [f"```{b['lang'] or ''}", b["code"], "```"]
    if r.get("exceptions"):
        parts += ["", "## Exceptions", r["exceptions"]]
    if r.get("risk"):
        rk = r["risk"]
        parts += ["", "## Risk Assessment", r.get("risk_text", ""),
                  "severity={severity} likelihood={likelihood} priority={priority} "
                  "level={level} detectable={detectable} repairable={repairable}".format(
                      **{k: rk.get(k) for k in ("severity", "likelihood", "priority",
                                                "level", "detectable", "repairable")})]
    text = "\n".join(parts)
    return text[:max_chars] if max_chars else text


def search(query: str, limit: int = 10, lang: str | None = None) -> list[dict]:
    """Keyword search with a simple TF-style score over title, intro, examples."""
    terms = [t for t in re.findall(r"[A-Za-z0-9_]+", query.lower()) if len(t) > 1]
    if not terms:
        return []
    scored = []
    for r in list_rules(lang=lang):
        title = r["title"].lower()
        hay = rule_text(r, True).lower()
        score = 0.0
        if norm_id(query) == r["id"]:
            score += 1000
        for t in terms:
            score += 8 * title.count(t) + min(hay.count(t), 12)
            if t == r["id"].lower():
                score += 50
        if score:
            scored.append((score, r))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    return [summary(r) | {"score": s} for s, r in scored[:limit]]
