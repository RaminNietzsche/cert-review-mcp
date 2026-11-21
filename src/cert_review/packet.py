"""LLM review packet: code hunks plus the rule texts worth reading.

Candidate rules are chosen deterministically from token/API heuristics
(data/heuristics.yaml), the active profile's idioms and path focus, and the
deterministic findings already produced. The reviewer must answer in the
schema below and every answer is checked by validator.py.
"""
from __future__ import annotations

import functools
import re
from pathlib import Path

import yaml

from . import checkers_map as CM
from . import rules as R
from .paths import data_dir
from .profiles import Profile
from . import profiles as P

FINDING_SCHEMA = {
    "rule_id": "CERT ID such as EXP34-C or MEM51-CPP (must exist in the database)",
    "file": "path exactly as shown in the hunk header",
    "line": "line number inside the shown hunk",
    "severity": "optional: error | warning | note",
    "message": "what is wrong in this code and why it violates the rule",
    "quote": "verbatim sentence copied from that rule's text (>= 20 characters)",
    "fix": "optional: a compliant replacement for the offending code",
    "confidence": "optional 0..1",
}

INSTRUCTIONS = """\
You are reviewing the code hunks below against the listed SEI CERT rules.
1. Report a violation only when the code shown actually violates a listed rule.
   Prefer silence to a speculative finding.
2. Every finding MUST cite a rule_id from `candidate_rules` and MUST include a
   `quote`: a verbatim passage copied from that rule's `text`. Findings without
   a valid rule ID, or whose quote is not found in the rule text, are rejected.
3. Respect `idioms` and `profile_notes`: they describe project conventions that
   change how a rule applies.
4. Lines in `existing_findings` are already reported by static analysis; do not
   repeat them.
5. Answer with a JSON list using the `finding_schema`; an empty list is a valid
   answer.
"""


@functools.lru_cache(maxsize=1)
def _heur() -> dict:
    d = yaml.safe_load((data_dir() / "heuristics.yaml").read_text(encoding="utf-8"))
    comp = {k: [re.compile(p, re.M) for p in v] for k, v in d["rules"].items()}
    cat = {k: [re.compile(p, re.M) for p in v] for k, v in d["categories"].items()}
    return {"rules": comp, "categories": cat}


def match_rules(text: str, lang: str, profile: Profile | None = None) -> dict[str, list[str]]:
    """rule id -> matched token strings (why it was selected)."""
    h = _heur()
    out: dict[str, list[str]] = {}
    for r in R.list_rules(lang=lang):
        if r["kind"] != "rule":
            continue
        pats = h["rules"].get(r["id"]) or h["categories"].get(r["category"], [])
        why = []
        for p in pats:
            m = p.search(text)
            if m:
                why.append(m.group(0).strip()[:40])
        if why and (r["id"] in h["rules"] or r["category"] in h["categories"]):
            # category-only fallback is weak: require 2 matches unless rule-specific
            if r["id"] not in h["rules"] and len(why) < 2:
                continue
            out[r["id"]] = why[:4]
    return out


def _excerpt(r: dict, max_chars: int) -> str:
    return R.rule_text(r, include_examples=True, max_chars=max_chars)


def build_hunks(paths_ranges: dict[str, list[tuple[int, int]]], max_lines: int = 60) -> list[dict]:
    hunks = []
    for path, ranges in paths_ranges.items():
        try:
            lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for a, b in ranges:
            a = max(1, a)
            b = min(len(lines), b)
            # split long ranges into windows
            start = a
            while start <= b:
                end = min(b, start + max_lines - 1)
                body = "\n".join(f"{i:>5}: {lines[i - 1]}" for i in range(start, end + 1))
                hunks.append({"file": path, "start": start, "end": end, "code": body,
                              "raw": "\n".join(lines[start - 1:end])})
                start = end + 1
    return hunks


def whole_file_ranges(files: list[str], window: int = 60) -> dict[str, list[tuple[int, int]]]:
    out = {}
    for f in files:
        try:
            n = len(Path(f).read_text(encoding="utf-8", errors="replace").splitlines())
        except OSError:
            continue
        out[f] = [(1, n)] if n else []
    return out


def build(hunks: list[dict], profile: Profile | str = "default", existing_findings: list | None = None,
          max_rules_per_hunk: int | None = None, rule_chars: int = 3500,
          only_uncovered: bool = True) -> dict:
    prof = P.load(profile) if isinstance(profile, str) else profile
    cap = max_rules_per_hunk or (prof.raw.get("llm_review") or {}).get("max_rules_per_hunk", 6)
    existing = existing_findings or []
    packet_hunks = []
    for h in hunks:
        lang = "c" if h["file"].lower().endswith(".c") else "cpp"
        text = h["raw"]
        matched = match_rules(text, lang, prof)
        idioms = prof.idioms_in(text)
        idiom_rules = {}
        for i in idioms:
            for rid in i["rules"]:
                if R.is_valid_id(rid) and R.get(rid)["lang"] == lang:
                    idiom_rules.setdefault(rid, []).append(f"idiom:{i['id']}")
        boost = prof.focus_categories(h["file"])
        scored = []
        for rid in set(matched) | set(idiom_rules):
            r = R.get(rid)
            if prof.disabled(rid):
                continue
            tier = CM.tier(rid, runnable=True)
            if only_uncovered and tier == "deterministic":
                continue          # a rule-specific checker already covers it
            risk = r.get("risk") or {}
            score = len(matched.get(rid, [])) * 2 + len(idiom_rules.get(rid, [])) * 3
            score += 4 if r["category"] in boost else 0
            score += int((risk.get("priority") or "P0").lstrip("P") or 0) / 6
            score += {"llm-only": 2, "partial": 1}.get(tier, 0)
            scored.append((score, rid, tier))
        scored.sort(key=lambda x: (-x[0], x[1]))
        cands = []
        for score, rid, tier in scored[:cap]:
            r = R.get(rid)
            risk = r.get("risk") or {}
            cands.append({
                "rule_id": rid, "title": r["title"], "tier": tier,
                "matched": matched.get(rid, []) + idiom_rules.get(rid, []),
                "severity": risk.get("severity"), "priority": risk.get("priority"),
                "level": risk.get("level"),
                "profile_note": prof.override(rid).get("note"),
                "text": _excerpt(r, rule_chars), "url": r["url"],
            })
        ex = [f for f in existing
              if f.get("file") == h["file"] and h["start"] <= f.get("line", 0) <= h["end"]]
        packet_hunks.append({
            "file": h["file"], "start_line": h["start"], "end_line": h["end"], "code": h["code"],
            "idioms": [{"id": i["id"], "hint": " ".join(i["hint"].split())} for i in idioms],
            "candidate_rules": cands,
            "existing_findings": [{"rule_id": f["rule_id"], "line": f["line"],
                                   "checker": f["checker"]} for f in ex],
        })
    return {
        "instructions": INSTRUCTIONS,
        "finding_schema": FINDING_SCHEMA,
        "profile": prof.name,
        "hunks": [h for h in packet_hunks if h["candidate_rules"]],
        "skipped_hunks": [(h["file"], h["start_line"], h["end_line"]) for h in packet_hunks
                          if not h["candidate_rules"]],
        "rule_database": R.source_info()["commit"],
    }
