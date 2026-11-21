"""Deterministic layer: run tools, normalize, apply profile, dedupe."""
from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import checkers_map as CM
from . import findings as F
from . import profiles as P
from . import rules as R
from . import toolrun as T

INLINE_IGNORE = re.compile(r"cert-review:\s*ignore\s+([A-Z]{3}\d{2}-(?:C|CPP)(?:\s*,\s*[A-Z]{3}\d{2}-(?:C|CPP))*)",
                           re.I)
DEFAULT_TOOLS = ("clang-tidy", "clangsa", "cppcheck")


@dataclass
class Result:
    findings: list[F.Finding] = field(default_factory=list)
    suppressed: list[F.Finding] = field(default_factory=list)
    tools: list[T.ToolStatus] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    profile: str = "default"
    notes: list[str] = field(default_factory=list)

    def to_dict(self, include_suppressed: bool = False) -> dict:
        d = {"profile": self.profile, "files": self.files,
             "findings": [f.to_dict() for f in self.findings],
             "tools": [vars(t) for t in self.tools], "notes": self.notes,
             "suppressed_count": len(self.suppressed)}
        if include_suppressed:
            d["suppressed"] = [f.to_dict() for f in self.suppressed]
        return d


class _Source:
    def __init__(self):
        self._c: dict[str, list[str]] = {}

    def lines(self, path: str) -> list[str]:
        if path not in self._c:
            try:
                self._c[path] = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                self._c[path] = []
        return self._c[path]

    def line(self, path: str, n: int) -> str | None:
        ls = self.lines(path)
        return ls[n - 1] if 1 <= n <= len(ls) else None


def _rules_for(tool: str, checker: str, lang: str) -> list[tuple[str, bool, float]]:
    """-> [(rule_id, specific, confidence)] for a raw checker hit on a file of `lang`."""
    key_tool = tool
    key_checker = checker
    if tool == "clang-tidy" and checker.startswith("clang-analyzer-"):
        key_tool, key_checker = "clangsa", checker.removeprefix("clang-analyzer-")
    entries = CM.reverse_index().get((key_tool, key_checker), [])
    want_cpp = lang == "cpp"
    sel = [e for e in entries if e["rule_id"].endswith("-CPP") == want_cpp]
    penalty = 1.0
    if not sel and want_cpp:        # e.g. cert-err33-c has only a C rule
        sel = [e for e in entries if not e["rule_id"].endswith("-CPP")]
        penalty = 0.85
    out = []
    n = max(1, len(sel))
    for e in sel:
        if e["specific"]:
            conf = 0.9
        else:
            conf = 0.65 if n == 1 else max(0.3, 0.65 - 0.06 * (n - 1))
        out.append((e["rule_id"], e["specific"], conf * penalty))
    return out


def _inline_ignored(src: _Source, path: str, line: int, rule_id: str) -> bool:
    for n in (line, line - 1):
        s = src.line(path, n)
        if s:
            m = INLINE_IGNORE.search(s)
            if m and rule_id.upper() in {x.strip().upper() for x in m.group(1).split(",")}:
                return True
    return False


def normalize(raw: list[T.RawFinding], profile: P.Profile, src: _Source | None = None,
              keep_suppressed: bool = True) -> tuple[list[F.Finding], list[F.Finding]]:
    src = src or _Source()
    kept, dropped = [], []
    for r in raw:
        lang = T.lang_of(r.file)
        for rid, specific, conf in _rules_for(r.tool, r.checker, lang):
            f = F.make(rid, r.file, r.line, r.col, r.tool, r.checker, r.message, conf, profile)
            if f is None:
                continue
            reason = profile.disabled(rid)
            if reason:
                f.suppressed = f"disabled rule: {reason}"
            else:
                s = profile.suppression(rid, r.checker, r.file, src.line(r.file, r.line))
                if s:
                    f.suppressed = s["reason"]
                elif _inline_ignored(src, r.file, r.line, rid):
                    f.suppressed = "inline cert-review: ignore"
            if not profile.include_recommendations and R.get(rid)["kind"] == "recommendation":
                f.suppressed = f.suppressed or "recommendations hidden by profile"
            if F.LEVEL_ORDER.get(f.level, 3) > F.LEVEL_ORDER.get(profile.min_level, 3):
                f.suppressed = f.suppressed or f"below profile min_level {profile.min_level}"
            (dropped if f.suppressed else kept).append(f)
    return kept, dropped


def cap_per_location(findings: list[F.Finding], max_rules: int = 2) -> list[F.Finding]:
    """Many CERT rules map to one checker; keep the best few per line."""
    by_loc: dict[tuple, list[F.Finding]] = {}
    for f in findings:
        by_loc.setdefault((f.file, f.line, f.checker), []).append(f)
    out = []
    for fs in by_loc.values():
        fs.sort(key=lambda f: (-f.confidence, -f.priority, f.rule_id))
        out.extend(fs[:max_rules])
    return out


def select_files(paths: list[str], profile: P.Profile, lang: str | None = None) -> list[str]:
    exts = profile.raw.get("file_extensions", {})
    c_ext = set(exts.get("c", [".c"]))
    cpp_ext = set(exts.get("cpp", [".cc", ".cpp", ".h"]))
    out = []
    for p in paths:
        pp = Path(p)
        cands = [pp] if pp.is_file() else sorted(x for x in pp.rglob("*") if x.is_file()) if pp.is_dir() else []
        for c in cands:
            ext = c.suffix.lower()
            if ext in c_ext or ext in cpp_ext:
                s = str(c)
                if profile.excluded_path(s.lstrip("/")) or profile.excluded_path(s):
                    continue
                if lang == "c" and ext not in c_ext:
                    continue
                if lang == "cpp" and ext in c_ext:
                    continue
                out.append(s)
    return out


def check(paths: list[str], profile: P.Profile | str = "default", lang: str | None = None,
          compdb: str | Path | None = None, root: str | Path | None = None,
          tools: tuple[str, ...] = DEFAULT_TOOLS, changed_lines: dict[str, set[int]] | None = None,
          jobs: int = 4, max_rules_per_location: int = 2, min_confidence: float = 0.0,
          include_suppressed: bool = True) -> Result:
    prof = P.load(profile) if isinstance(profile, str) else profile
    rootp = Path(root).resolve() if root else None
    files = select_files(paths, prof, lang)
    # Headers are analysed through the sources that include them; analysing a
    # bare header works for clang-tidy, so keep them when passed explicitly.
    res = Result(profile=prof.name, files=files)
    if not files:
        res.notes.append("no C/C++ files selected")
        return res
    cdb = Path(compdb) if compdb else (T.find_compdb(rootp) if rootp else None)
    raw: list[T.RawFinding] = []
    if "clang-tidy" in tools:
        r, st = T.run_clang_tidy(files, prof, cdb, rootp, jobs=jobs, with_csa="clangsa" in tools)
        raw += r
        res.tools.append(st)
    if "clangsa" in tools:
        r, st = T.run_clang_sa(files, prof, cdb, rootp, jobs=jobs)
        raw += r
        res.tools.append(st)
    if "cppcheck" in tools:
        r, st = T.run_cppcheck(files, prof, rootp, jobs=jobs)
        raw += r
        res.tools.append(st)
    # restrict to the files requested (clang-tidy may report headers)
    raw = [x for x in raw if not prof.excluded_path(x.file.lstrip("/"))]
    kept, dropped = normalize(raw, prof)
    if changed_lines is not None:
        norm = {str(Path(k).resolve()): v for k, v in changed_lines.items()}
        def in_diff(f: F.Finding) -> bool:
            ls = norm.get(str(Path(f.file).resolve()))
            return bool(ls and f.line in ls)
        kept = [f for f in kept if in_diff(f)]
        dropped = [f for f in dropped if in_diff(f)]
    kept = cap_per_location(kept, max_rules_per_location)
    kept = [f for f in F.dedupe(kept) if f.confidence >= min_confidence]
    res.findings = F.sort_by_importance(kept)
    res.suppressed = dropped if include_suppressed else []
    return res
