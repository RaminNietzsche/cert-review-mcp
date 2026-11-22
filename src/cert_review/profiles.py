"""Review profiles (profiles/*.yaml): severity tuning, suppressions, idioms."""
from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .paths import profiles_dir

SEV_ORDER = {"error": 3, "warning": 2, "note": 1}


@dataclass
class Profile:
    name: str
    raw: dict
    _suppress: list = field(default_factory=list)

    # ---- lookup -----------------------------------------------------------
    @property
    def min_level(self) -> str:
        return self.raw.get("min_level", "L3")

    @property
    def standards(self) -> tuple[str, ...]:
        """Standards whose IDs findings are mapped to (profile key `standards`, default cert)."""
        from .rules import expand_standards
        return expand_standards(self.raw.get("standards") or ["cert"])

    def classification_severity(self, classification: str | None) -> str:
        """Finding severity for a MISRA/AUTOSAR classification."""
        m = self.raw.get("severity_from_classification",
                         {"mandatory": "error", "required": "warning", "advisory": "note",
                          "document": "note"})
        return m.get((classification or "").lower(), "warning")

    @property
    def include_recommendations(self) -> bool:
        return bool(self.raw.get("include_recommendations", False))

    @property
    def clang_tidy_args(self) -> list[str]:
        return list((self.raw.get("clang_tidy") or {}).get("extra_args", []))

    @property
    def header_filter(self) -> str | None:
        return (self.raw.get("clang_tidy") or {}).get("header_filter")

    @property
    def extra_checks(self) -> list[str]:
        return list((self.raw.get("clang_tidy") or {}).get("checks_extra", []))

    def disabled(self, rule_id: str) -> str | None:
        from .rules import norm_id
        rid = norm_id(rule_id)
        for d in self.raw.get("disabled_rules", []):
            if norm_id(str(d["id"])) == rid:
                return d["reason"]
        return None

    def override(self, rule_id: str) -> dict:
        from .rules import norm_id
        ov = self.raw.get("rule_overrides") or {}
        if rule_id.upper() in ov:
            return ov[rule_id.upper()]
        rid = norm_id(rule_id)
        for k, v in ov.items():
            if norm_id(str(k)) == rid:
                return v
        return {}

    def excluded_path(self, path: str) -> bool:
        p = path.lstrip("./")
        return any(fnmatch.fnmatch(p, g) or fnmatch.fnmatch("/" + p, g)
                   for g in self.raw.get("exclude_paths", []))

    def suppression(self, rule_id: str, checker: str | None, path: str,
                    code_line: str | None, message: str | None = None) -> dict | None:
        """First matching suppression rule, or None."""
        p = path.lstrip("./")
        for s in self.raw.get("suppress", []):
            ids = []
            if "id" in s:
                ids = [s["id"].upper()]
            idp = s.get("id_prefixes")
            if ids and rule_id.upper() not in ids:
                continue
            if idp is not None and not any(rule_id.upper().startswith(x.upper()) for x in idp):
                continue
            if "checker" in s and s["checker"] != checker:
                continue
            if "id" not in s and idp is None and "checker" not in s:
                continue
            if "paths" in s and not any(
                    fnmatch.fnmatch(p, g) or _glob_tail(p, g) for g in s["paths"]):
                continue
            if "code_regex" in s:
                if code_line is None or not re.search(s["code_regex"], code_line):
                    continue
            if "code_not_regex" in s:
                # suppress unless the line matches: for checks known to misfire
                if code_line is not None and re.search(s["code_not_regex"], code_line):
                    continue
            if "message_regex" in s:
                if message is None or not re.search(s["message_regex"], message):
                    continue
            return s
        return None

    def idioms_in(self, text: str) -> list[dict]:
        out = []
        for i in self.raw.get("idioms", []):
            if re.search(i["detect"], text):
                out.append(i)
        return out

    def focus_categories(self, path: str) -> set[str]:
        p = path.lstrip("./")
        cats: set[str] = set()
        for f in self.raw.get("path_focus", []):
            if any(fnmatch.fnmatch(p, g) for g in f["paths"]):
                cats |= set(f.get("boost_categories", []))
        return cats

    def cert_severity(self, cert_sev: str | None) -> str:
        m = self.raw.get("severity_from_cert", {"High": "error", "Medium": "warning", "Low": "note"})
        return m.get(cert_sev or "", "warning")

    def diff_context_default(self) -> int:
        return int((self.raw.get("diff_review") or {}).get("diff_context", 0))

    def synthetic_compdb_default(self) -> bool:
        dr = self.raw.get("diff_review") or {}
        if "synthetic_compdb" in dr:
            return bool(dr["synthetic_compdb"])
        return self.name == "ceph"

    def synthetic_compdb_cache_default(self) -> bool:
        dr = self.raw.get("diff_review") or {}
        if "synthetic_compdb_cache" in dr:
            return bool(dr["synthetic_compdb_cache"])
        return self.name == "ceph"

    def synthetic_compdb_excludes(self) -> tuple[str, ...]:
        return tuple(self.raw.get("exclude_paths") or ())


def _glob_tail(p: str, g: str) -> bool:
    # allow `src/tools/**/*.c`-style globs: treat ** as *
    return fnmatch.fnmatch(p, g.replace("**/", "*"))


def available() -> list[str]:
    return sorted(p.stem for p in profiles_dir().glob("*.yaml"))


def load(name_or_path: str = "default") -> Profile:
    p = Path(name_or_path)
    if not p.suffix:
        p = profiles_dir() / f"{name_or_path}.yaml"
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    from . import ruletexts
    ruletexts.set_profile_paths(raw.get("rule_texts"))
    return Profile(name=raw.get("name", p.stem), raw=raw)
