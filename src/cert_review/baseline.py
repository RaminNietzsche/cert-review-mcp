"""Baselines: remember existing findings so that only new ones are reported.

A baseline entry does not store the line number. It stores the rule ID, the file path
relative to the baseline's directory, a hash of the normalized source line and a hash of
the surrounding code. Findings therefore stay matched when lines are inserted or removed
above them, when indentation changes, and (through the context hash) when the flagged line
itself is edited while its neighbourhood is unchanged.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

FORMAT_VERSION = 1
DEFAULT_FILE = ".cert-review-baseline.json"
CONTEXT_LINES = 2          # non-blank lines taken on each side of the finding
_WS = re.compile(r"\s+")


def normalize(line: str) -> str:
    """Whitespace-insensitive form of a source line (indentation and spacing ignored)."""
    return _WS.sub(" ", line).strip()


def _h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:16]


class _Lines:
    def __init__(self) -> None:
        self._c: dict[str, list[str]] = {}

    def get(self, path: str) -> list[str]:
        if path not in self._c:
            try:
                self._c[path] = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                self._c[path] = []
        return self._c[path]


def _context(lines: list[str], idx: int, n: int = CONTEXT_LINES) -> str:
    before, after = [], []
    i = idx - 1
    while i >= 0 and len(before) < n:
        s = normalize(lines[i])
        if s:
            before.insert(0, s)
        i -= 1
    i = idx + 1
    while i < len(lines) and len(after) < n:
        s = normalize(lines[i])
        if s:
            after.append(s)
        i += 1
    return "\n".join(before + ["<finding>"] + after)


def rel_path(file: str, root: str | Path) -> str:
    try:
        r = os.path.relpath(Path(file).resolve(), Path(root).resolve())
    except ValueError:                      # different drive on Windows
        r = file
    return Path(r).as_posix()


def fingerprint_parts(finding: dict, root: str | Path, cache: _Lines | None = None) -> dict:
    """Line-number-free identity of a finding: rule, relative file, line hash, context hash."""
    cache = cache or _Lines()
    path = finding["file"]
    lines = cache.get(path)
    idx = int(finding.get("line") or 0) - 1
    if 0 <= idx < len(lines):
        code = normalize(lines[idx])
        ctx = _context(lines, idx)
    else:                                   # file unreadable: fall back to the message
        code = "msg:" + normalize(finding.get("message", ""))
        ctx = ""
    rel = rel_path(path, root)
    rule = finding["rule_id"].upper()
    line_hash, context_hash = _h(code), _h(ctx)
    return {"rule_id": rule, "file": rel, "line_hash": line_hash, "context_hash": context_hash,
            "fingerprint": _h(f"{rule}|{rel}|{line_hash}|{context_hash}")}


def fingerprints(findings: Iterable[dict], root: str | Path) -> list[dict]:
    cache = _Lines()
    return [fingerprint_parts(f, root, cache) for f in findings]


# ---------------------------------------------------------------- file format
def make_entries(findings: list[dict], root: str | Path) -> list[dict]:
    out = []
    for f, fp in zip(findings, fingerprints(findings, root)):
        out.append({**fp, "line": f.get("line"), "checker": f"{f.get('tool', '')}:{f.get('checker', '')}",
                    "message": (f.get("message") or "")[:200]})
    out.sort(key=lambda e: (e["file"], e["line"] or 0, e["rule_id"], e["fingerprint"]))
    return out


def build(findings: list[dict], root: str | Path) -> dict:
    return {"version": FORMAT_VERSION, "generator": "cert-review",
            "note": "Fingerprints of accepted findings; line numbers are informational only.",
            "entries": make_entries(findings, root)}


def load(path: str | Path) -> dict:
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"baseline not found: {path}")
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        raise ValueError(f"{path} is not a cert-review baseline (missing 'entries')")
    if int(data.get("version", 0)) > FORMAT_VERSION:
        raise ValueError(f"{path} uses baseline format {data['version']}; this version reads <= {FORMAT_VERSION}")
    return data


def dump(data: dict, path: str | Path) -> None:
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def root_of(path: str | Path) -> Path:
    """Paths in a baseline are relative to the directory that contains it."""
    return Path(path).expanduser().resolve().parent


# ---------------------------------------------------------------- matching
def match(findings: list[dict], entries: list[dict], root: str | Path) -> tuple[list[int], list[int], list[int]]:
    """Return (new finding indexes, baselined finding indexes, unmatched entry indexes).

    Each baseline entry absorbs at most one finding. Passes, strictest first:
    1. rule + file + line hash + context hash
    2. rule + file + line hash            (code moved, neighbours changed)
    3. rule + file + context hash         (the flagged line itself was edited)
    """
    fps = fingerprints(findings, root)
    free = set(range(len(entries)))
    matched: set[int] = set()
    keys = (("rule_id", "file", "line_hash", "context_hash"),
            ("rule_id", "file", "line_hash"),
            ("rule_id", "file", "context_hash"))
    for k in keys:
        idx: dict[tuple, list[int]] = defaultdict(list)
        for i in sorted(free):
            e = entries[i]
            if all(e.get(x) for x in k):
                idx[tuple(e[x] for x in k)].append(i)
        for fi, fp in enumerate(fps):
            if fi in matched:
                continue
            cand = idx.get(tuple(fp[x] for x in k))
            if cand:
                ei = cand.pop(0)
                free.discard(ei)
                matched.add(fi)
    new = [i for i in range(len(findings)) if i not in matched]
    return new, sorted(matched), sorted(free)


def apply(result: dict, baseline_path: str | Path, scope: str = "files") -> dict:
    """Filter a check_files/check_diff result in place against a baseline file.

    `scope` is "files" (whole files were analysed, so unmatched entries in analysed files
    are fixed) or "diff" (only changed lines were analysed, so unmatched entries are only
    out of scope and are not reported as fixed).
    """
    data = load(baseline_path)
    root = root_of(baseline_path)
    entries = data["entries"]
    findings = result["findings"]
    new, old, free = match(findings, entries, root)
    analysed = {rel_path(f, root) for f in result.get("files", [])}
    gone = [entries[i] for i in free if entries[i].get("file") in analysed]
    info = {
        "path": str(Path(baseline_path).expanduser().resolve()),
        "entries": len(entries),
        "new": len(new),
        "baselined": len(old),
        "fixed": len(gone) if scope == "files" else None,
        "fixed_entries": [{k: e.get(k) for k in ("rule_id", "file", "line", "message")}
                          for e in gone[:50]] if scope == "files" else [],
        "note": ("fixed counts baseline entries in analysed files that no longer match a finding"
                 if scope == "files" else
                 "diff scope: baseline entries outside the changed lines are not checked, so fixed is null"),
    }
    result["findings"] = [findings[i] for i in new]
    result["baseline"] = info
    return result


def update(data: dict | None, findings: list[dict], analysed_files: list[str],
           root: str | Path) -> tuple[dict, dict]:
    """Replace entries of analysed files with current findings; keep the rest. Returns (data, stats)."""
    root = Path(root)
    analysed = {rel_path(f, root) for f in analysed_files}
    old = (data or {}).get("entries", [])
    kept = [e for e in old if e.get("file") not in analysed]
    fresh = make_entries(findings, root)
    before = {e["fingerprint"] for e in old if e.get("file") in analysed}
    after = {e["fingerprint"] for e in fresh}
    entries = sorted(kept + fresh, key=lambda e: (e["file"], e.get("line") or 0, e["rule_id"], e["fingerprint"]))
    out = build([], root)
    out["entries"] = entries
    stats = {"entries": len(entries), "added": len(after - before), "removed": len(before - after),
             "kept_outside_scope": len(kept)}
    return out, stats
