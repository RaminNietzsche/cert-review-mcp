"""Optional, user-supplied guideline texts for MISRA and AUTOSAR.

The MISRA and AUTOSAR guideline texts are copyrighted, so this project ships none of
them. A user who holds a licence can point cert-review at a local text file; the texts
are then shown by get_rule, used to verify `quote` in validate_findings, and passed to
the cppcheck MISRA addon (--rule-texts) so its messages carry the headline.

Where the paths come from (first match wins per standard):
  * environment: CERT_REVIEW_MISRA_C_TEXTS, CERT_REVIEW_MISRA_CPP_TEXTS,
    CERT_REVIEW_AUTOSAR_TEXTS
  * the active profile: `rule_texts: {misra-c-2012: /path, ...}` (see profiles.Profile)

Accepted file formats (UTF-8, Latin-1 or Windows-1252):
  1. The cppcheck MISRA addon format: an optional "Appendix A Summary of guidelines"
     line, then blocks of
         Rule 10.4 Required            (or "Dir 4.1", "Rule 8.2.2", "Rule A5-2-2")
         Headline text, possibly wrapped
         over several lines
  2. One guideline per line: "<ID><TAB or ' - ' or ': '><text>", e.g.
         MISRA-C-2012-10.4<TAB>Headline text
         A5-2-2: Headline text
Lines starting with '#' are ignored. Nothing is ever written or uploaded.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from . import rules as R

ENV = {"misra-c-2012": "CERT_REVIEW_MISRA_C_TEXTS",
       "misra-cpp-2023": "CERT_REVIEW_MISRA_CPP_TEXTS",
       "autosar-cpp14": "CERT_REVIEW_AUTOSAR_TEXTS"}

_HEAD = re.compile(r"^(?:(Rule|Dir|Directive)\s+)?([AM]?\d+(?:[.-]\d+){1,2})"
                   r"(?:\s+\(?(Mandatory|Required|Advisory|Document)\b.*)?$", re.I)
_CLASS_ONLY = re.compile(r"^\(?(Mandatory|Required|Advisory|Document)\)?$", re.I)
_LINE = re.compile(r"^([A-Za-z0-9:+._ -]+?)(?:\t+|\s+-\s+|:\s+)(.+)$")

_cache: dict[tuple[str, str, float], dict[str, str]] = {}
_profile_paths: dict[str, str] = {}


def _read(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8", "windows-1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def parse(text: str, standard: str) -> dict[str, str]:
    """Rule-texts file content -> {canonical ID: text}."""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if "Appendix A" in ln and "Summary of guidelines" in ln:
            lines = lines[i + 1:]
            break
    out: dict[str, str] = {}
    cur: str | None = None
    for ln in lines:
        s = ln.strip()
        if s.startswith("Appendix B"):
            break
        if not s or s.startswith("#"):
            cur = None if not s else cur
            continue
        if _CLASS_ONLY.match(s):
            continue
        m = _HEAD.match(s)
        if m:
            kind = (m.group(1) or "").lower()
            num = m.group(2)
            rid = R.resolve_id(("Dir " if kind.startswith("dir") else "") + num, standard)
            cur = rid if rid and R.standard_of(R.every_rule()[rid]) == standard else None
            continue
        m = _LINE.match(s)
        if m:
            rid = R.resolve_id(m.group(1).strip(), standard)
            if rid and R.standard_of(R.every_rule()[rid]) == standard:
                out[rid] = m.group(2).strip()
                cur = None
                continue
        if cur:
            out[cur] = (out[cur] + " " + s).strip() if cur in out else s
    return out


def set_profile_paths(paths: dict[str, str] | None) -> None:
    """Called when a profile with `rule_texts` is loaded."""
    _profile_paths.clear()
    for k, v in (paths or {}).items():
        if k in ENV and v:
            _profile_paths[k] = str(Path(os.path.expanduser(str(v))))


def path_for(standard: str) -> str | None:
    p = os.environ.get(ENV.get(standard, ""), "") or _profile_paths.get(standard, "")
    return p or None


def load(standard: str) -> dict[str, str]:
    p = path_for(standard)
    if not p:
        return {}
    path = Path(p).expanduser()
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return {}
    key = (standard, str(path), mtime)
    if key not in _cache:
        _cache[key] = parse(_read(path), standard)
    return _cache[key]


def text_for(rule_id: str) -> str | None:
    r = R.get(rule_id)
    if not r or R.is_cert(r):
        return None
    return load(R.standard_of(r)).get(r["id"]) or None


def status() -> dict[str, dict]:
    """Which standards have licensed texts loaded (counts only, never the text)."""
    out = {}
    for std in ENV:
        p = path_for(std)
        out[std] = {"configured": bool(p), "loaded": len(load(std)) if p else 0,
                    "env": ENV[std]}
    return out
