#!/usr/bin/env python3
"""Build data/checker_map.json: CERT rule ID -> deterministic checkers.

Inputs (all pinned; commits and tool versions are recorded in the output):
  * CodeChecker label files (config/labels/analyzers/*.json): the
    `sei-cert-c:<id>` / `sei-cert-cpp:<id>` labels of clang-tidy, clangsa,
    cppcheck and gcc checkers.
  * clang-tidy `cert-*` aliases, from the LLVM docs (checks/cert/*.md).
  * The locally installed clang-tidy, clang and cppcheck, to record which
    mapped checkers actually exist in the toolchain the engine will run.

Tiers
  deterministic  a rule-specific checker exists (a clang-tidy cert-* alias)
  partial        only general checkers are mapped; they catch some patterns
  llm-only       no checker; needs human or LLM review

`tier` counts every upstream mapping. `tier_runnable` counts only checkers
present in the installed toolchain, which is what the engine can execute.
"""
from __future__ import annotations

import argparse
import json
import yaml
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ["clang-tidy", "clangsa", "cppcheck", "gcc"]
SEV = {"HIGH", "MEDIUM", "LOW", "STYLE", "UNSPECIFIED"}


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=False).stdout
    except FileNotFoundError:
        return ""


def git_head(p: Path):
    return subprocess.check_output(["git", "-C", str(p), "rev-parse", "HEAD"], text=True).strip()


def installed():
    ct = set()
    for pat in ("*", "cert-*", "clang-analyzer-*"):   # '*' omits some aliases
        ct |= set(re.findall(r"^\s+(\S+)$", run(["clang-tidy", "--list-checks", f"-checks={pat}"]), re.M))
    ct.discard("Enabled")
    sa = set(re.findall(r"^\s{2}(\S+)\s", run(["clang", "-cc1", "-analyzer-checker-help",
                                              "-analyzer-checker-help-alpha"]), re.M))
    cpp = set(re.findall(r'id="([^"]+)"', run(["cppcheck", "--errorlist"])))
    ver = {
        "clang-tidy": (run(["clang-tidy", "--version"]).split("version")[-1].split()[:1] or ["?"])[0],
        "clangsa": (run(["clang", "--version"]).split("version")[-1].split()[:1] or ["?"])[0],
        "cppcheck": (run(["cppcheck", "--version"]).split()[-1:] or ["?"])[0],
    }
    return {"clang-tidy": ct, "clangsa": sa, "cppcheck": cpp, "gcc": set()}, ver


def load_codechecker(cc: Path):
    out = []   # (tool, checker, rule_id_upper, severity)
    for tool in TOOLS:
        f = cc / "config/labels/analyzers" / f"{tool}.json"
        if not f.exists():
            continue
        labels = json.loads(f.read_text())["labels"]
        for checker, labs in labels.items():
            sev = next((l.split(":", 1)[1] for l in labs if l.startswith("severity:")), None)
            for l in labs:
                m = re.fullmatch(r"sei-cert-(c|cpp):([a-z]{3}\d{2}-c(?:pp)?)", l)
                if m:
                    out.append((tool, checker, m.group(2).upper(), m.group(1), sev))
    return out


def load_aliases(llvm: Path):
    out = []
    d = llvm / "clang-tools-extra/docs/clang-tidy/checks/cert"
    for f in sorted(d.glob("*.md")):
        m = re.search(r"\{doc\}`([a-z0-9-]+) <", f.read_text())
        # cert-err33-c has its own documentation instead of an alias stub;
        # it is still a rule-specific checker registered by the CERT module.
        out.append((f"cert-{f.stem}", f.stem.upper(), m.group(1) if m else None))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codechecker", required=True, type=Path)
    ap.add_argument("--llvm", required=True, type=Path)
    ap.add_argument("--rules", default=ROOT / "data/rules.json", type=Path)
    ap.add_argument("--out", default=ROOT / "data/checker_map.json", type=Path)
    a = ap.parse_args()

    rules = {r["id"]: r for r in json.loads(a.rules.read_text())["rules"]}
    avail, versions = installed()
    mapping: dict[str, dict[tuple, dict]] = {}

    def add(rid, tool, checker, origin, specific, sev=None, target=None):
        if rid not in rules:
            return
        key = (tool, checker)
        e = mapping.setdefault(rid, {}).setdefault(key, {
            "tool": tool, "checker": checker, "origins": [], "specific": False,
            "available": checker in avail.get(tool, set()) or
                         (tool == "cppcheck" and checker.removeprefix("cppcheck-") in avail["cppcheck"]),
        })
        if origin not in e["origins"]:
            e["origins"].append(origin)
        e["specific"] = e["specific"] or specific
        if sev:
            e["severity_hint"] = sev
        if target:
            e["alias_of"] = target

    for tool, checker, rid, lang, sev in load_codechecker(a.codechecker):
        name = checker.removeprefix("cppcheck-") if tool == "cppcheck" else checker
        add(rid, tool, name, "codechecker", False, sev)
    for name, rid, target in load_aliases(a.llvm):
        add(rid, "clang-tidy", name, "clang-tidy-alias", True, None, target)

    overlay = yaml.safe_load((ROOT / "data/checker_overlay.yaml").read_text())
    for o in overlay:
        for rid in o["rules"]:
            add(rid, o["tool"], o["checker"], "curated-overlay", False)
    out_rules = {}
    tiers = {"all": {}, "runnable": {}}
    for rid, r in sorted(rules.items()):
        chk = sorted(mapping.get(rid, {}).values(), key=lambda e: (e["tool"], e["checker"]))
        def tier(cs):
            if any(c["specific"] for c in cs):
                return "deterministic"
            return "partial" if cs else "llm-only"
        run_chk = [c for c in chk if c["available"]]
        out_rules[rid] = {
            "tier": tier(chk), "tier_runnable": tier(run_chk),
            "checkers": chk,
            "cert_detectable": (r.get("risk") or {}).get("detectable"),
        }
    summary = {}
    for lang in ("c", "cpp"):
        for kind in ("rule", "recommendation"):
            ids = [i for i, r in rules.items() if r["lang"] == lang and r["kind"] == kind]
            if not ids:
                continue
            for key in ("tier", "tier_runnable"):
                c = {"deterministic": 0, "partial": 0, "llm-only": 0}
                for i in ids:
                    c[out_rules[i][key]] += 1
                summary[f"{lang}_{kind}_{key}"] = c | {"total": len(ids)}
    doc = {
        "schema": 1,
        "sources": {
            "codechecker": {"repository": "https://github.com/Ericsson/codechecker",
                            "commit": git_head(a.codechecker),
                            "license": "Apache-2.0", "files": "config/labels/analyzers/*.json"},
            "llvm": {"repository": "https://github.com/llvm/llvm-project",
                     "commit": git_head(a.llvm),
                     "files": "clang-tools-extra/docs/clang-tidy/checks/cert/*.md"},
            "overlay": {"file": "data/checker_overlay.yaml", "entries": len(overlay)},
            "toolchain_versions": versions,
        },
        "tier_definitions": {
            "deterministic": "a rule-specific checker exists (clang-tidy cert-* alias)",
            "partial": "only general checkers are mapped; some violation patterns are caught",
            "llm-only": "no checker is mapped; needs review",
        },
        "summary": summary,
        "rules": out_rules,
    }
    a.out.write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps(summary, indent=1))
    print("versions:", versions)


if __name__ == "__main__":
    sys.exit(main())
