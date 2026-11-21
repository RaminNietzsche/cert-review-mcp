"""Normalized findings: one schema for every tool and for LLM review."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

from . import rules as R
from .profiles import Profile, SEV_ORDER

LEVEL_ORDER = {"L1": 1, "L2": 2, "L3": 3}
# MISRA/AUTOSAR have no CERT risk table: priority and level come from the classification.
CLASS_PRIORITY = {"mandatory": 18, "required": 12, "advisory": 4, "document": 2}
CLASS_LEVEL = {"mandatory": "L1", "required": "L2", "advisory": "L3", "document": "L3"}


@dataclass
class Finding:
    rule_id: str
    lang: str
    file: str
    line: int
    col: int
    severity: str          # error | warning | note
    priority: int          # numeric P value from the CERT risk table (+ profile delta)
    level: str             # L1..L3
    tool: str
    checker: str
    message: str
    confidence: float
    title: str = ""
    cert_severity: str | None = None
    also_found_by: list[str] = field(default_factory=list)
    note: str | None = None
    suppressed: str | None = None   # reason, set only when kept for audit
    standard: str = ""              # cert-c | cert-cpp | misra-c-2012 | misra-cpp-2023 | autosar-cpp14

    def to_dict(self) -> dict:
        d = asdict(self)
        r = R.get(self.rule_id)
        d["url"] = R.url(r) if r else None
        return d


def priority_number(p: str | None) -> int:
    try:
        return int((p or "P0").lstrip("Pp"))
    except ValueError:
        return 0


def make(rule_id: str, file: str, line: int, col: int, tool: str, checker: str,
         message: str, confidence: float, profile: Profile) -> Finding | None:
    r = R.get(rule_id)
    if r is None:
        return None
    ov = profile.override(r["id"])
    if not R.is_cert(r):
        cls = r["classification"]
        return Finding(
            rule_id=r["id"], lang=r["lang"], file=file, line=line, col=col,
            severity=ov.get("severity") or profile.classification_severity(cls),
            priority=CLASS_PRIORITY.get(cls, 4) + int(ov.get("priority_delta", 0)),
            level=CLASS_LEVEL.get(cls, "L3"), tool=tool, checker=checker, message=message,
            confidence=round(confidence, 2), title=R.title(r), cert_severity=None,
            note=ov.get("note"), standard=r["standard"])
    risk = r.get("risk") or {}
    sev = ov.get("severity") or profile.cert_severity(risk.get("severity"))
    prio = priority_number(risk.get("priority")) + int(ov.get("priority_delta", 0))
    return Finding(
        rule_id=r["id"], lang=r["lang"], file=file, line=line, col=col,
        severity=sev, priority=prio, level=risk.get("level", "L3"), tool=tool,
        checker=checker, message=message, confidence=round(confidence, 2),
        title=r["title"], cert_severity=risk.get("severity"), note=ov.get("note"),
        standard=R.standard_of(r))


def dedupe(findings: list[Finding]) -> list[Finding]:
    """Merge findings with the same rule at the same file:line.

    Keeps the highest-confidence report, records the other tools, and raises
    confidence slightly when independent tools agree.
    """
    by_key: dict[tuple, Finding] = {}
    for f in sorted(findings, key=lambda x: -x.confidence):
        key = (f.rule_id, f.file, f.line)
        cur = by_key.get(key)
        if cur is None:
            by_key[key] = f
            continue
        tag = f"{f.tool}:{f.checker}"
        if tag != f"{cur.tool}:{cur.checker}" and tag not in cur.also_found_by:
            cur.also_found_by.append(tag)
            if f.tool != cur.tool:
                cur.confidence = round(min(0.99, cur.confidence + 0.1), 2)
    out = list(by_key.values())
    out.sort(key=lambda f: (f.file, f.line, f.col, f.rule_id))
    return out


def sort_by_importance(findings: list[Finding]) -> list[Finding]:
    return sorted(findings, key=lambda f: (-SEV_ORDER.get(f.severity, 0), -f.priority,
                                           -f.confidence, f.file, f.line))
