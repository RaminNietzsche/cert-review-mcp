"""Grounding validator for LLM findings.

A finding is accepted only when
  * it has a rule_id that exists in the database (and fits the file language),
  * it quotes the rule: the quote is at least 20 characters and appears,
    after whitespace/markdown normalization, in the rule's own text
    (SEI CERT always; MISRA/AUTOSAR only when the user supplied a licensed
    rule-texts file, because their texts are not bundled: otherwise the quote is
    optional, unchecked, and the finding is marked grounding="rule-id-only"),
  * it names a file and a positive line (inside a packet hunk when a packet
    is supplied),
  * its message is non-empty,
  * and the rule is not disabled by the profile.
"""
from __future__ import annotations

import re
from typing import Any

from . import findings as F
from . import profiles as P
from . import rules as R

MIN_QUOTE = 20


def _norm(s: str) -> str:
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = re.sub(r"[`*_]", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def rule_corpus(r: dict) -> str:
    return _norm(R.rule_text(r, include_examples=True))


def quote_supported(rule_id: str, quote: str) -> bool:
    r = R.get(rule_id)
    if not r or not quote:
        return False
    q = _norm(quote).strip(" .\u2026")
    q = re.sub(r"^\.\.\.|\.\.\.$", "", q).strip()
    if R.is_cert(r):
        return len(q) >= MIN_QUOTE and q in rule_corpus(r)
    from . import ruletexts
    lic = ruletexts.text_for(r["id"])
    if not lic:
        return False
    corpus = _norm(lic).strip(" .")
    # headlines are short: accept 20+ characters, or the whole headline
    return (len(q) >= MIN_QUOTE or q == corpus) and q in corpus


def quote_required(rule_id: str) -> bool:
    """SEI CERT: always. MISRA/AUTOSAR: only when a licensed text for the rule is loaded."""
    r = R.get(rule_id)
    if not r:
        return True
    if R.is_cert(r):
        return True
    from . import ruletexts
    return bool(ruletexts.text_for(r["id"]))


_C_ONLY = ("misra-c-2012",)
_CPP_ONLY = ("cert-cpp", "misra-cpp-2023", "autosar-cpp14")
_CPP_EXT = (".cc", ".cpp", ".cxx", ".hpp", ".hh", ".hxx")


def validate(findings: list[dict[str, Any]], packet: dict | None = None,
             profile: P.Profile | str = "default") -> dict:
    prof = P.load(profile) if isinstance(profile, str) else profile
    hunks = (packet or {}).get("hunks") or []
    accepted, rejected = [], []
    for raw in findings:
        why = []
        rid = str(raw.get("rule_id", "")).strip().upper()
        rule = R.get(rid) if rid else None
        if rule is not None:
            rid = rule["id"]
        if not rid:
            why.append("missing rule_id")
        elif rule is None:
            why.append(f"unknown rule_id {rid}")
        file = raw.get("file")
        line = raw.get("line")
        if not file:
            why.append("missing file")
        if not isinstance(line, int) or line < 1:
            why.append("missing or invalid line")
        if not str(raw.get("message", "")).strip():
            why.append("missing message")
        quote = str(raw.get("quote") or "")
        grounding = "quote"
        if rule is not None:
            needs_quote = quote_required(rid)
            if not needs_quote:
                grounding = "rule-id-only"
            elif not quote.strip():
                why.append("missing quote")
            elif not quote_supported(rid, quote):
                why.append("quote not found in the text of " + rid
                           + (f" (shorter than {MIN_QUOTE} characters)"
                              if len(_norm(quote)) < MIN_QUOTE else ""))
            reason = prof.disabled(rid)
            if reason:
                why.append(f"rule disabled by profile: {reason}")
            std = R.standard_of(rule)
            if file and std in _C_ONLY and str(file).lower().endswith(_CPP_EXT):
                why.append(f"{rid} is a MISRA C rule but {file} is a C++ file")
            # SEI CERT C rules may apply to C++ files; no rejection
            if file and std in _CPP_ONLY and str(file).lower().endswith(".c"):
                why.append(f"{rid} is a C++ rule but {file} is a C file")
        if hunks and file and isinstance(line, int):
            inside = any(h["file"] == file and h["start_line"] <= line <= h["end_line"] for h in hunks)
            if not inside:
                why.append("line is outside every hunk in the packet")
            elif rule is not None:
                cand = {c["rule_id"] for h in hunks if h["file"] == file
                        and h["start_line"] <= line <= h["end_line"] for c in h["candidate_rules"]}
                # packets list candidates per standard; only enforce when the packet has
                # candidates from this rule's standard (SEI CERT packets for MISRA findings
                # are checked for hunk bounds only)
                cand_stds = {R.standard_of(R.get(c)) for c in cand if R.get(c)}
                if rid not in cand and (R.is_cert(rule) or R.standard_of(rule) in cand_stds):
                    why.append(f"{rid} was not a candidate rule for that hunk")
        if why:
            rejected.append({"finding": raw, "reasons": why})
            continue
        f = F.make(rid, str(file), int(line), int(raw.get("col") or 1), "llm-review", "llm",
                   str(raw["message"]).strip(), float(raw.get("confidence") or 0.5), prof)
        if raw.get("severity") in ("error", "warning", "note"):
            f.severity = raw["severity"]
        d = f.to_dict()
        d["quote"] = quote.strip()
        d["fix"] = raw.get("fix")
        d["grounding"] = grounding
        accepted.append(d)
    return {"accepted": accepted, "rejected": rejected,
            "summary": {"accepted": len(accepted), "rejected": len(rejected)}}
