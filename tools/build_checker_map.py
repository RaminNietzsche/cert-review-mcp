#!/usr/bin/env python3
"""Build data/checker_map.json: CERT rule ID -> deterministic checkers.

Inputs (all pinned; commits and tool versions are recorded in the output):
  * CodeChecker label files (config/labels/analyzers/*.json): the
    `sei-cert-c:<id>` / `sei-cert-cpp:<id>` labels of clang-tidy, clangsa,
    cppcheck and gcc checkers.
  * clang-tidy `cert-*` aliases, from the LLVM docs (checks/cert/*.md).
  * The locally installed clang-tidy, clang and cppcheck, to record which
    mapped checkers actually exist in the toolchain the engine will run.
  * The bundled Semgrep rules (data/semgrep/*.yml): each rule names its CERT
    rule(s) in metadata.cert.
  * Infer issue types, mapped in data/checker_overlay.yaml; availability comes
    from `infer help --list-issue-types` when Infer is installed.
  * The CodeQL CERT query packs (codeql/cert-c-coding-standards and
    codeql/cert-cpp-coding-standards from github/codeql-coding-standards, MIT),
    when downloaded with `codeql pack download`: each query's
    `external/cert/id/<rule>` tag.

Tiers
  deterministic  a rule-specific checker exists (a clang-tidy cert-* alias or a
                 CodeQL CERT query)
  partial        only general checkers or narrow pattern rules (Semgrep) are
                 mapped; they catch some patterns
  llm-only       no checker; needs human or LLM review

`tier` counts every mapping. `tier_runnable` counts checkers present in the
reference toolchain (clang-tidy, Clang Static Analyzer, cppcheck and the
bundled Semgrep rules), which is what the Docker image runs. `tier_extended`
adds the optional analyzers (Infer, CodeQL) when they were installed while the
map was built.
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
REFERENCE_TOOLS = {"clang-tidy", "clangsa", "cppcheck", "semgrep"}
EXTENDED_TOOLS = REFERENCE_TOOLS | {"infer", "codeql"}
SEMGREP_CONFIDENCE = {"high": 0.8, "medium": 0.65, "low": 0.45}
CODEQL_PACKS = ("cert-c-coding-standards", "cert-cpp-coding-standards")
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
    infer = {line.split(":", 1)[0] for line in run(["infer", "help", "--list-issue-types"]).splitlines()
             if line and line[0].isupper()}
    ver = {
        "clang-tidy": (run(["clang-tidy", "--version"]).split("version")[-1].split()[:1] or ["?"])[0],
        "clangsa": (run(["clang", "--version"]).split("version")[-1].split()[:1] or ["?"])[0],
        "cppcheck": (run(["cppcheck", "--version"]).split()[-1:] or ["?"])[0],
    }
    sg = run(["semgrep", "--version"]).strip()
    if sg:
        ver["semgrep"] = sg.splitlines()[-1]
    if infer:
        ver["infer"] = (re.findall(r"v(\d+\.\d+\.\d+)", run(["infer", "--version"])) or ["?"])[0]
    cq = re.findall(r"release (\d+\.\d+\.\d+)", run(["codeql", "version"]))
    if cq:
        ver["codeql"] = cq[0]
    return {"clang-tidy": ct, "clangsa": sa, "cppcheck": cpp, "gcc": set(), "infer": infer}, ver


def load_semgrep(d: Path):
    """(rule_id, check_id, confidence) for every bundled Semgrep rule."""
    out = []
    for f in sorted(d.glob("*.yml")):
        for r in yaml.safe_load(f.read_text())["rules"]:
            md = r.get("metadata") or {}
            for rid in md.get("cert", []):
                out.append((rid, r["id"], SEMGREP_CONFIDENCE.get(md.get("confidence"), 0.65)))
    return out


def codeql_pack_dirs(base: Path | None):
    """Installed CodeQL CERT packs: {pack name: (version, path)}."""
    roots = [base] if base else [Path.home() / ".codeql/packages/codeql"]
    found = {}
    for root in roots:
        for name in CODEQL_PACKS:
            vers = sorted((root / name).glob("*/qlpack.yml")) if (root / name).is_dir() else []
            if vers:
                q = vers[-1].parent
                found[name] = (q.name, q)
    return found


def load_codeql(packs: dict):
    """(rule_id, query_id) for each query a pack's default suite runs."""
    out = []
    for name, (_, d) in sorted(packs.items()):
        for q in sorted(d.glob("rules/**/*.ql")):
            head = q.read_text(errors="replace").split("*/", 1)[0]
            qid = re.search(r"@id\s+(\S+)", head)
            # the engine runs each pack's default suite: rules only, nothing default-disabled
            if (not qid or "external/cert/default-disabled" in head
                    or "external/cert/obligation/recommendation" in head):
                continue
            for rid in re.findall(r"external/cert/id/([a-z]{3}\d{2}-c(?:pp)?)\b", head):
                out.append((rid.upper(), qid.group(1)))
    return out


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
    ap.add_argument("--codeql-packs", type=Path, default=None,
                    help="directory holding codeql/cert-*-coding-standards packs "
                         "(default ~/.codeql/packages/codeql)")
    a = ap.parse_args()

    rules = {r["id"]: r for r in json.loads(a.rules.read_text())["rules"]}
    avail, versions = installed()
    mapping: dict[str, dict[tuple, dict]] = {}

    packs = codeql_pack_dirs(a.codeql_packs)
    codeql_queries = load_codeql(packs)
    avail["codeql"] = {q for _, q in codeql_queries}
    avail["semgrep"] = {c for _, c, _ in load_semgrep(ROOT / "data/semgrep")}

    def add(rid, tool, checker, origin, specific, sev=None, target=None, confidence=None):
        if rid not in rules:
            return
        key = (tool, checker)
        e = mapping.setdefault(rid, {}).setdefault(key, {
            "tool": tool, "checker": checker, "origins": [], "specific": False,
            "available": checker in avail.get(tool, set()) or
                         (tool == "cppcheck" and checker.removeprefix("cppcheck-") in avail["cppcheck"]),
        })
        if confidence is not None:
            e["confidence"] = confidence
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

    for rid, check_id, conf in load_semgrep(ROOT / "data/semgrep"):
        add(rid, "semgrep", check_id, "cert-review-semgrep", False, confidence=conf)
    for rid, qid in codeql_queries:
        add(rid, "codeql", qid, "codeql-coding-standards", True)

    overlay = yaml.safe_load((ROOT / "data/checker_overlay.yaml").read_text())
    for o in overlay:
        for rid in o["rules"]:
            add(rid, o["tool"], o["checker"], "curated-overlay", False)
    excl = yaml.safe_load((ROOT / "data/checker_exclusions.yaml").read_text())
    for x in excl:
        for rid in x["rules"]:
            mapping.get(rid, {}).pop((x["tool"], x["checker"]), None)
    out_rules = {}
    tiers = {"all": {}, "runnable": {}}
    for rid, r in sorted(rules.items()):
        chk = sorted(mapping.get(rid, {}).values(), key=lambda e: (e["tool"], e["checker"]))
        def tier(cs):
            if any(c["specific"] for c in cs):
                return "deterministic"
            return "partial" if cs else "llm-only"
        run_chk = [c for c in chk if c["available"] and c["tool"] in REFERENCE_TOOLS]
        ext_chk = [c for c in chk if c["available"] and c["tool"] in EXTENDED_TOOLS]
        out_rules[rid] = {
            "tier": tier(chk), "tier_runnable": tier(run_chk), "tier_extended": tier(ext_chk),
            "checkers": chk,
            "cert_detectable": (r.get("risk") or {}).get("detectable"),
        }
    summary = {}
    for lang in ("c", "cpp"):
        for kind in ("rule", "recommendation"):
            ids = [i for i, r in rules.items() if r["lang"] == lang and r["kind"] == kind]
            if not ids:
                continue
            for key in ("tier", "tier_runnable", "tier_extended"):
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
            "exclusions": {"file": "data/checker_exclusions.yaml", "entries": len(excl)},
            "semgrep": {"files": "data/semgrep/*.yml",
                        "rules": len(avail["semgrep"])},
            "codeql": {"repository": "https://github.com/github/codeql-coding-standards",
                       "license": "MIT",
                       "packs": {f"codeql/{n}": v for n, (v, _) in sorted(packs.items())},
                       "queries": len(avail["codeql"])},
            "toolchain_versions": versions,
            "reference_toolchain": sorted(REFERENCE_TOOLS),
            "extended_toolchain": sorted(EXTENDED_TOOLS),
        },
        "tier_definitions": {
            "deterministic": "a rule-specific checker exists (clang-tidy cert-* alias or CodeQL CERT query)",
            "partial": "only general checkers or narrow Semgrep pattern rules are mapped; some violation patterns are caught",
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
