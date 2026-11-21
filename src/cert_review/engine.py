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

_IGN_ID = r"[A-Z][A-Z0-9]*(?:[-.:][A-Z0-9]+)+"
INLINE_IGNORE = re.compile(rf"cert-review:\s*ignore\s+({_IGN_ID}(?:\s*,\s*{_IGN_ID})*)", re.I)
DEFAULT_TOOLS = ("clang-tidy", "clangsa", "cppcheck")


@dataclass
class Result:
    findings: list[F.Finding] = field(default_factory=list)
    suppressed: list[F.Finding] = field(default_factory=list)
    tools: list[T.ToolStatus] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    profile: str = "default"
    notes: list[str] = field(default_factory=list)
    standards: list[str] = field(default_factory=lambda: list(R.CERT_STANDARDS))

    def to_dict(self, include_suppressed: bool = False) -> dict:
        d = {"profile": self.profile, "standards": self.standards, "files": self.files,
             "findings": [f.to_dict() for f in self.findings],
             "tools": [{**vars(t), "status": t.status} for t in self.tools], "notes": self.notes,
             "warnings": T.parse_warnings(self.tools),
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


def _rules_for(tool: str, checker: str, lang: str,
               standards: tuple[str, ...] = R.CERT_STANDARDS,
               code_line: str | None = None) -> list[tuple[str, bool, float]]:
    """-> [(rule_id, specific, confidence)] for a raw checker hit on a file of `lang`."""
    key_tool = tool
    key_checker = checker
    if tool == "clang-tidy" and checker.startswith("clang-analyzer-"):
        key_tool, key_checker = "clangsa", checker.removeprefix("clang-analyzer-")
    out = _guideline_rules_for(key_tool, key_checker, lang, standards, code_line)
    if not set(standards) & set(R.CERT_STANDARDS):
        return out
    return _cert_rules_for(key_tool, key_checker, lang) + out


def _guideline_rules_for(tool: str, checker: str, lang: str, standards: tuple[str, ...],
                         code_line: str | None = None) -> list[tuple[str, bool, float]]:
    """MISRA/AUTOSAR mapping: only standards for the file's language (MISRA C on C files,
    MISRA C++ and AUTOSAR on C++ files); `line_regex` mappings need a matching source line."""
    sel = [e for e in CM.guideline_reverse_index().get((tool, checker), [])
           if e["standard"] in standards and R.guidelines()[e["rule_id"]]["lang"] == lang
           and (not e.get("line_regex") or re.search(e["line_regex"], code_line or ""))]
    out = []
    by_std: dict[str, int] = {}
    for e in sel:
        by_std[e["standard"]] = by_std.get(e["standard"], 0) + 1
    for e in sel:
        n = by_std[e["standard"]]
        conf = 0.9 if e["specific"] else (0.6 if n == 1 else max(0.3, 0.6 - 0.06 * (n - 1)))
        out.append((e["rule_id"], e["specific"], conf))
    return out


def _cert_rules_for(key_tool: str, key_checker: str, lang: str) -> list[tuple[str, bool, float]]:
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
            if m and rule_id.upper() in {R.norm_id(x.strip()) for x in m.group(1).split(",")}:
                return True
    return False


def relpath(path: str, root: Path | None) -> str:
    base = root or Path.cwd()
    try:
        return str(Path(path).resolve().relative_to(base.resolve()))
    except ValueError:
        return str(path).lstrip("/")


def normalize(raw: list[T.RawFinding], profile: P.Profile, src: _Source | None = None,
              root: Path | None = None,
              standards: tuple[str, ...] | None = None) -> tuple[list[F.Finding], list[F.Finding]]:
    """Map raw tool hits to rule findings (SEI CERT, plus MISRA/AUTOSAR when selected).
    Paths are made absolute so that reports from different tools for the same location merge."""
    src = src or _Source()
    stds = standards or profile.standards
    kept, dropped = [], []
    for r in raw:
        r.file = str(Path(r.file).resolve())
        rel = relpath(r.file, root)
        lang = T.lang_of(r.file)
        code = src.line(r.file, r.line) if set(stds) - set(R.CERT_STANDARDS) else None
        for rid, specific, conf in _rules_for(r.tool, r.checker, lang, stds, code):
            if r.tool == "cppcheck" and r.message.startswith("Either the condition"):
                conf *= 0.6      # cppcheck: a path-sensitive guess, not a proven defect
            msg = r.message
            if r.tool == "cppcheck" and msg.startswith("misra violation"):
                # the addon has no headline without a licensed rule-texts file
                g = R.get(rid)
                msg = f"{R.display_name(g)}: {R.title(g)}"
            f = F.make(rid, r.file, r.line, r.col, r.tool, r.checker, msg, conf, profile)
            if f is None:
                continue
            reason = profile.disabled(rid)
            if reason:
                f.suppressed = f"disabled rule: {reason}"
            else:
                s = profile.suppression(rid, r.checker, rel, src.line(r.file, r.line), r.message)
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
        by_loc.setdefault((f.file, f.line, f.checker, f.standard in R.CERT_STANDARDS or f.standard),
                          []).append(f)
    out = []
    for fs in by_loc.values():
        fs.sort(key=lambda f: (-f.confidence, -f.priority, f.rule_id))
        out.extend(fs[:max_rules])
    return out


def select_files(paths: list[str], profile: P.Profile, lang: str | None = None,
                 root: Path | None = None) -> list[str]:
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
                if profile.excluded_path(relpath(s, root)):
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
          include_suppressed: bool = True,
          standards: tuple[str, ...] | list[str] | str | None = None) -> Result:
    prof = P.load(profile) if isinstance(profile, str) else profile
    stds = R.expand_standards(standards) if standards else prof.standards
    rootp = Path(root).resolve() if root else None
    files = select_files(paths, prof, lang, rootp)
    # Headers are analysed through the sources that include them; analysing a
    # bare header works for clang-tidy, so keep them when passed explicitly.
    res = Result(profile=prof.name, files=files, standards=list(stds))
    if not files:
        res.notes.append("no C/C++ files selected")
        return res
    cdb = Path(compdb) if compdb else (T.find_compdb(rootp) if rootp else None)
    raw: list[T.RawFinding] = []
    if "clang-tidy" in tools:
        r, st = T.run_clang_tidy(files, prof, cdb, rootp, jobs=jobs, with_csa="clangsa" in tools,
                                 standards=stds)
        raw += r
        res.tools.append(st)
    if "clangsa" in tools:
        r, st = T.run_clang_sa(files, prof, cdb, rootp, jobs=jobs, standards=stds)
        raw += r
        res.tools.append(st)
    if "cppcheck" in tools:
        r, st = T.run_cppcheck(files, prof, rootp, jobs=jobs, standards=stds)
        raw += r
        res.tools.append(st)
    # restrict to the files requested (clang-tidy may report headers)
    raw = [x for x in raw if not prof.excluded_path(relpath(x.file, rootp))]
    kept, dropped = normalize(raw, prof, root=rootp, standards=stds)
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
