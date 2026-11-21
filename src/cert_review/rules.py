"""Access to the bundled rule databases.

SEI CERT C/C++ (data/rules.json, full text) plus MISRA C:2012, MISRA C++:2023 and
AUTOSAR C++14 (data/guidelines.json: IDs, classification, mappings and original
one-line summaries only; the official texts are copyrighted and not shipped).
"""
from __future__ import annotations

import functools
import json
import re
from typing import Iterable

from .paths import data_dir

ID_RE = re.compile(r"^[A-Za-z]{3}\d{2}-(?:C|CPP)$")

CERT_STANDARDS = ("cert-c", "cert-cpp")
GUIDELINE_STANDARDS = ("misra-c-2012", "misra-cpp-2023", "autosar-cpp14")
STANDARDS = CERT_STANDARDS + GUIDELINE_STANDARDS
STANDARD_GROUPS = {
    "cert": CERT_STANDARDS,
    "misra": ("misra-c-2012", "misra-cpp-2023"),
    "autosar": ("autosar-cpp14",),
    "all": STANDARDS,
}
STANDARD_NAMES = {
    "cert-c": "SEI CERT C", "cert-cpp": "SEI CERT C++", "misra-c-2012": "MISRA C:2012",
    "misra-cpp-2023": "MISRA C++:2023", "autosar-cpp14": "AUTOSAR C++14",
}
PREFIX = {"misra-c-2012": "MISRA-C-2012-", "misra-cpp-2023": "MISRA-CPP-2023-",
          "autosar-cpp14": "AUTOSAR-"}


def expand_standards(spec: str | Iterable[str] | None) -> tuple[str, ...]:
    """'cert' / 'misra' / 'autosar' / 'all' / a standard name, or a list of them.
    None means SEI CERT (the default everywhere)."""
    if spec is None:
        return CERT_STANDARDS
    items = [spec] if isinstance(spec, str) else list(spec)
    out: list[str] = []
    for it in items:
        k = str(it).strip().lower()
        if k in ("", "any"):
            continue
        group = STANDARD_GROUPS.get(k, (k,) if k in STANDARDS else None)
        if group is None:
            raise ValueError(f"unknown standard {it!r}; use one of "
                             f"{', '.join(list(STANDARD_GROUPS) + list(STANDARDS))}")
        out += [g for g in group if g not in out]
    return tuple(out) or CERT_STANDARDS


@functools.lru_cache(maxsize=1)
def _load() -> dict:
    return json.loads((data_dir() / "rules.json").read_text(encoding="utf-8"))


@functools.lru_cache(maxsize=1)
def _load_guidelines() -> dict:
    p = data_dir() / "guidelines.json"
    if not p.exists():
        return {"standards": {}, "guidelines": [], "sources": {}}
    return json.loads(p.read_text(encoding="utf-8"))


def source_info() -> dict:
    return _load()["source"]


def guideline_info() -> dict:
    d = _load_guidelines()
    return {"standards": d.get("standards", {}), "sources": d.get("sources", {}),
            "notice": d.get("notice", "")}


@functools.lru_cache(maxsize=1)
def cert_rules() -> dict[str, dict]:
    return {r["id"]: r for r in _load()["rules"]}


@functools.lru_cache(maxsize=1)
def guidelines() -> dict[str, dict]:
    return {r["id"]: r for r in _load_guidelines()["guidelines"]}


def all_rules() -> dict[str, dict]:
    """SEI CERT rules only (kept for compatibility); see every_rule() for all standards."""
    return cert_rules()


@functools.lru_cache(maxsize=1)
def every_rule() -> dict[str, dict]:
    return {**cert_rules(), **guidelines()}


def standard_of(r: dict) -> str:
    return r.get("standard") or ("cert-cpp" if r["lang"] == "cpp" else "cert-c")


def is_cert(r_or_id: dict | str) -> bool:
    r = get(r_or_id) if isinstance(r_or_id, str) else r_or_id
    return bool(r) and standard_of(r) in CERT_STANDARDS


_ALIASES = [
    # cppcheck MISRA addon IDs: misra-c2012-10.4
    (re.compile(r"^MISRA[-_ ]?C[-_ ]?2012[-_ ](\d+\.\d+)$"), "MISRA-C-2012-{0}"),
    # MISRA C:2012 Rule 10.4 / MISRA C 2012 Dir 4.1 / MISRA-C-2012-R10.4
    (re.compile(r"^MISRA[-_ ]?C[-_ :]*20(?:12|23|25)[-_ :]*(?:RULE[-_ ]*|R)(\d+\.\d+)$"),
     "MISRA-C-2012-{0}"),
    (re.compile(r"^MISRA[-_ ]?C[-_ :]*20(?:12|23|25)[-_ :]*(?:DIRECTIVE|DIR|D)[-_ .]*(\d+\.\d+)$"),
     "MISRA-C-2012-DIR-{0}"),
    (re.compile(r"^MISRA[-_ ]?C(?:\+\+|PP)[-_ :]*2023[-_ :]*(?:RULE[-_ ]*|R)?(\d+\.\d+\.\d+)$"),
     "MISRA-CPP-2023-{0}"),
    (re.compile(r"^MISRA[-_ ]?C(?:\+\+|PP)[-_ :]*2023[-_ :]*(?:DIRECTIVE|DIR|D)[-_ .]*(\d+\.\d+\.\d+)$"),
     "MISRA-CPP-2023-DIR-{0}"),
    (re.compile(r"^(?:AUTOSAR(?:[-_ ]?C\+\+14)?[-_ :]*)?(?:RULE[-_ ]+)?([AM]\d+-\d+-\d+)$"),
     "AUTOSAR-{0}"),
    # bare numbers: two parts only exist in MISRA C, three parts only in MISRA C++:2023
    (re.compile(r"^(?:RULE[-_ ]*)?(\d+\.\d+)$"), "MISRA-C-2012-{0}"),
    (re.compile(r"^(?:DIRECTIVE|DIR)[-_ .]*(\d+\.\d+)$"), "MISRA-C-2012-DIR-{0}"),
    (re.compile(r"^(?:RULE[-_ ]*)?(\d+\.\d+\.\d+)$"), "MISRA-CPP-2023-{0}"),
    (re.compile(r"^(?:DIRECTIVE|DIR)[-_ .]*(\d+\.\d+\.\d+)$"), "MISRA-CPP-2023-DIR-{0}"),
]


def resolve_id(rule_id: str, standard: str | None = None) -> str | None:
    """Canonical rule ID for any accepted spelling, or None when it does not exist.

    Accepts canonical IDs (EXP34-C, MISRA-C-2012-10.4, MISRA-C-2012-DIR-4.1,
    MISRA-CPP-2023-8.2.2, AUTOSAR-A5-2-2), cppcheck addon IDs (misra-c2012-10.4),
    'Rule 10.4' / 'Dir 4.1' / 'A5-2-2' forms, and bare numbers when `standard` says which
    standard they belong to (two-part numbers default to MISRA C, three-part to MISRA C++)."""
    raw = re.sub(r"\s+", " ", str(rule_id or "").strip().upper())
    if not raw:
        return None
    rules = every_rule()
    if raw in rules:
        return raw
    if standard in PREFIX:
        pre = PREFIX[standard]
        bare = re.sub(r"^(?:RULE|R)[-_ ]*", "", raw)
        for cand in (pre + bare, pre + re.sub(r"^(?:DIRECTIVE|DIR|D)[-_ .]*", "DIR-", bare)):
            if cand in rules:
                return cand
    for rx, fmt in _ALIASES:
        m = rx.match(raw)
        if m:
            cand = fmt.format(m.group(1))
            if cand in rules:
                return cand
    return None


def norm_id(rule_id: str) -> str:
    return resolve_id(rule_id) or rule_id.strip().upper()


def get(rule_id: str) -> dict | None:
    rid = resolve_id(rule_id)
    return every_rule().get(rid) if rid else None


def is_valid_id(rule_id: str) -> bool:
    return resolve_id(rule_id) is not None


def display_name(r_or_id: dict | str) -> str:
    """Human label: 'CERT EXP34-C', 'MISRA C:2012 Rule 10.4', 'AUTOSAR C++14 A5-2-2'."""
    r = get(r_or_id) if isinstance(r_or_id, str) else r_or_id
    if not r:
        return str(r_or_id)
    std = standard_of(r)
    if std in CERT_STANDARDS:
        return f"CERT {r['id']}"
    local = r["local_id"]
    if std == "autosar-cpp14":
        return f"AUTOSAR C++14 {local}"
    kind = "Dir" if local.startswith("DIR-") else "Rule"
    return f"{STANDARD_NAMES[std]} {kind} {local.removeprefix('DIR-')}"


def title(r: dict) -> str:
    """CERT title, or for MISRA/AUTOSAR: the user's licensed headline when loaded, else the
    original summary, else the section name."""
    if is_cert(r):
        return r["title"]
    from . import ruletexts
    t = ruletexts.text_for(r["id"])
    if t:
        return t
    if r.get("summary"):
        return r["summary"]
    sec = f" ({r['category_name']})" if r.get("category_name") else ""
    return f"{display_name(r)}{sec}"


def url(r: dict) -> str | None:
    if is_cert(r):
        return r["url"]
    return (guideline_info()["standards"].get(standard_of(r)) or {}).get("url")


def list_rules(lang: str | None = None, category: str | None = None,
               kind: str | None = None, level: str | None = None,
               detectable: bool | None = None,
               ids: Iterable[str] | None = None,
               standard: str | Iterable[str] | None = None,
               classification: str | None = None) -> list[dict]:
    """Filter rules. `standard` defaults to SEI CERT (cert-c + cert-cpp)."""
    out = []
    idset = {norm_id(i) for i in ids} if ids is not None else None
    stds = set(expand_standards(standard))
    pool = list(cert_rules().values()) if stds <= set(CERT_STANDARDS) else list(every_rule().values())
    for r in pool:
        if standard_of(r) not in stds:
            continue
        if lang and r["lang"] != lang.lower():
            continue
        if category and str(r["category"]).upper() != category.upper():
            continue
        if classification and r.get("classification") != classification.lower():
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
    if not is_cert(r):
        return {"id": r["id"], "standard": r["standard"], "lang": r["lang"], "kind": r["kind"],
                "category": r["category"], "category_name": r.get("category_name"),
                "title": title(r), "classification": r["classification"],
                "decidability": r.get("decidability"), "enforcement": r.get("enforcement"),
                "severity": None, "likelihood": None, "priority": None, "level": None,
                "detectable": None, "cert": [c["id"] for c in r.get("cert", [])], "url": url(r)}
    risk = r.get("risk") or {}
    return {"id": r["id"], "standard": standard_of(r), "lang": r["lang"], "kind": r["kind"],
            "category": r["category"], "title": r["title"],
            "severity": risk.get("severity"), "likelihood": risk.get("likelihood"),
            "priority": risk.get("priority"), "level": risk.get("level"),
            "detectable": risk.get("detectable"), "url": r["url"]}


def rule_text(r: dict, include_examples: bool = True, max_chars: int | None = None) -> str:
    """Plain-text rendering of a rule (title, rationale, examples, risk)."""
    if not is_cert(r):
        text = guideline_text(r)
        return text[:max_chars] if max_chars else text
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


def guideline_text(r: dict) -> str:
    """Text for a MISRA/AUTOSAR record: facts, our summary, and the licensed text when the
    user supplied it (see ruletexts)."""
    from . import ruletexts
    std = standard_of(r)
    meta = guideline_info()["standards"].get(std, {})
    parts = [f"{r['id']}. {display_name(r)} ({r['classification']})", ""]
    lic = ruletexts.text_for(r["id"])
    if lic:
        parts += ["## Guideline text (from your licensed copy)", lic, ""]
    if r.get("summary"):
        parts += ["## Summary", r["summary"] + " (paraphrase written for cert-review; not the "
                  "official text)", ""]
    facts = [f"standard: {meta.get('edition') or STANDARD_NAMES[std]}", f"kind: {r['kind']}",
             f"classification: {r['classification']}"]
    if r.get("category_name"):
        facts.append(f"section: {r['category']} {r['category_name']}")
    if r.get("enforcement"):
        facts.append(f"enforcement by static analysis: {r['enforcement']}")
    if r.get("decidability"):
        facts.append(f"decidability: {r['decidability']}")
    if r.get("cert"):
        facts.append("related SEI CERT rules: " + ", ".join(
            f"{c['id']} ({c['relation']})" for c in r["cert"]))
    parts += ["## Facts"] + [f"- {f}" for f in facts]
    if not lic:
        parts += ["", f"The official {STANDARD_NAMES[std]} text is copyrighted and not bundled. "
                  "Load your licensed copy with a rule-texts file (docs/misra-autosar.md) to "
                  f"see it here. Source: {meta.get('url', '')}"]
    return "\n".join(parts)


def search(query: str, limit: int = 10, lang: str | None = None,
           standard: str | Iterable[str] | None = None) -> list[dict]:
    """Keyword search with a simple TF-style score over title, intro, examples."""
    terms = [t for t in re.findall(r"[A-Za-z0-9_]+", query.lower()) if len(t) > 1]
    if not terms:
        return []
    scored = []
    qid = resolve_id(query)
    for r in list_rules(lang=lang, standard=standard):
        title_l = title(r).lower()
        hay = rule_text(r, True).lower()
        score = 0.0
        if qid == r["id"]:
            score += 1000
        for t in terms:
            score += 8 * title_l.count(t) + min(hay.count(t), 12)
            if t == r["id"].lower():
                score += 50
        if score:
            scored.append((score, r))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    return [summary(r) | {"score": s} for s, r in scored[:limit]]
