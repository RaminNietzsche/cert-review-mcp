#!/usr/bin/env python3
"""Build data/guidelines.json: MISRA C:2012, MISRA C++:2023 and AUTOSAR C++14 records.

Only facts are recorded (guideline IDs, classification, enforcement, checker mappings,
CERT cross-references) plus the original one-line summaries in
data/guideline_overlay.yaml. No MISRA or AUTOSAR text is read into the output.

Inputs:
  --cppcheck   checkout of https://github.com/danmar/cppcheck at the pinned tag
               (lib/checkers.cpp: guideline IDs and classification;
                lib/checkersidmapping.cpp: cppcheck warning ID -> guideline;
                addons/misra.py: MISRA C rules the open-source addon reports)
  --autosar    `pdftotext -layout` output of the public AUTOSAR_RS_CPP14Guidelines.pdf
               (rule IDs, classification, enforcement; Appendix B.4 CERT traceability)

Usage:
  python3 tools/build_guidelines.py --cppcheck ../cppcheck --autosar /tmp/autosar.txt
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CPPCHECK_TAG = "2.17.1"
AUTOSAR_URL = "https://www.autosar.org/fileadmin/standards/R22-11/AP/AUTOSAR_RS_CPP14Guidelines.pdf"

STANDARDS = {
    "misra-c-2012": {
        "name": "MISRA C:2012",
        "edition": "MISRA C:2012 with Amendments 1-4 (the guideline set of MISRA C:2023)",
        "lang": "c", "publisher": "The MISRA Consortium Limited",
        "url": "https://misra.org.uk/misra-c/", "prefix": "MISRA-C-2012-",
    },
    "misra-cpp-2023": {
        "name": "MISRA C++:2023", "edition": "MISRA C++:2023 (C++17)",
        "lang": "cpp", "publisher": "The MISRA Consortium Limited",
        "url": "https://misra.org.uk/misra-cpp/", "prefix": "MISRA-CPP-2023-",
    },
    "autosar-cpp14": {
        "name": "AUTOSAR C++14", "edition": "AUTOSAR C++14 Coding Guidelines, AP Release 19-03",
        "lang": "cpp", "publisher": "AUTOSAR",
        "url": AUTOSAR_URL, "prefix": "AUTOSAR-",
    },
}
# MISRA C++:2023 directives (the rest of the list are rules)
CPP2023_DIRECTIVES = {"0.3.1", "0.3.2", "5.7.2", "15.8.1"}
CLASS = {"Req": "required", "Adv": "advisory", "Man": "mandatory", "Doc": "document"}
CPPCHECK_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def _block(src: str, name: str) -> str:
    i = src.index(name)
    return src[i:src.index("};", i)]


def git_head(path: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:                                       # noqa: BLE001
        return ""


def cppcheck_lists(cc: Path) -> dict:
    s = (cc / "lib" / "checkers.cpp").read_text()
    dirs = re.findall(r"\{(\d+),(\d+),(\w+),(\d+)\}", _block(s, "misraC2012Directives ="))
    rules = re.findall(r"\{(\d+),(\d+),(\w+),(\d+)\}", _block(s, "misraC2012Rules ="))
    cpp23 = re.findall(r"\{(\d+),(\d+),(\d+),(\w+)\}", _block(s, "misraCpp2023Rules ="))
    m = (cc / "lib" / "checkersidmapping.cpp").read_text()

    def idmap(name: str) -> dict[str, list[str]]:
        out = {}
        for g, ids in re.findall(r'\{"([^"]+)",\s*"([^"]*)"\}', _block(m, name)):
            toks = [t.strip() for t in ids.split(",")]
            toks = [t for t in toks if CPPCHECK_ID.match(t) and t != "error"]
            if toks:
                out[g] = toks
        return out

    addon = (cc / "addons" / "misra.py").read_text()
    reported = set()
    for a, b in re.findall(r"reportError\([^,()]+(?:\([^)]*\))?,\s*(\d+),\s*(\d+)\)", addon):
        reported.add(f"{int(a)}.{int(b)}")
    for n in re.findall(r"executeCheck\((\d+),", addon):
        n = int(n)
        reported.add(f"{n // 100}.{n % 100}")
    return {"dirs": dirs, "rules": rules, "cpp23": cpp23,
            "map_c": idmap("idMappingMisraC{"), "map_cpp23": idmap("idMappingMisraCpp2023{"),
            "map_autosar": idmap("idMappingAutosar{"), "addon_rules": reported}


def autosar_rules(txt: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for rid, attrs in re.findall(r"^\s*Rule ([AM]\d+-\d+-\d+) \(([^)]*)\)", txt, re.M):
        parts = [re.sub(r"\s+", " ", p).strip() for p in attrs.split(",")]
        cls, target, enf = parts[0].lower(), parts[1].lower(), parts[-1].lower()
        enf = enf.replace("not automated", "non-automated").replace("partially automated",
                                                                     "partially-automated")
        out.setdefault(rid, {"classification": cls,
                             "target": [t.strip() for t in target.split("/")],
                             "enforcement": enf})
    return out


def autosar_cert_trace(txt: str) -> dict[str, dict]:
    """Appendix B.4: CERT C++ rule -> related AUTOSAR rules with relation 1-3."""
    lines = txt.split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.startswith("B.4 Traceability to SEI CERT"))
    end = next(i for i in range(start, len(lines)) if lines[i].startswith("B.5 Traceability"))
    rows, cur = [], None
    for ln in lines[start:end]:
        if re.match(r"^ ?[A-Z]{3}\d{2}-", ln):
            cur = [ln]
            rows.append(cur)
        elif cur is not None:
            if "AUTOSAR CONFIDENTIAL" in ln or "Document ID" in ln:
                cur = None
                continue
            cur.append(ln)
    rel_re = re.compile(r"(\d) - (Identical|Small differences|Significant differences|Rejected|"
                        r"Not yet analyzed)")
    out = {}
    for r in rows:
        m = re.match(r"^ ?([A-Z]{3}\d{2}-)(CPP|C)?", r[0])
        cid = m.group(1) + (m.group(2) or ("CPP" if len(r) > 1 and r[1].strip().startswith("CPP")
                                           else "C"))
        rel = next((rel_re.search(x) for x in r[:2] if rel_re.search(x)), None)
        if not rel:
            continue
        n = int(rel.group(1))
        line_with = next(x for x in r[:2] if rel_re.search(x))
        c = rel.end()
        while c < len(line_with) and line_with[c] == " ":
            c += 1
        col = "".join(x[c - 1:c + 14] for x in r if len(x) > c - 1)
        col = re.sub(r"-\s+", "-", col)
        ids = re.findall(r"[AM]\d+-\d+-\d+", col)
        if n <= 3 and ids:
            out[cid] = {"relation": rel.group(2).lower(), "related": ids}
    return out


def cert_misra_c_refs(rules_json: dict) -> dict[str, list[dict]]:
    """MISRA C IDs cited in the 'Related Guidelines' tables of SEI CERT C (CC BY 4.0)."""
    out: dict[str, list[dict]] = {}
    for r in rules_json["rules"]:
        for g in r.get("related_guidelines") or []:
            tax = g.get("taxonomy", "")
            if "MISRA" not in tax or "C++" in tax:
                continue
            ed = "MISRA C:2025" if "2025" in tax else "MISRA C:2012"
            item = g.get("item", "")
            for kind, nums in re.findall(r"(Dir(?:ective)?|Rule)?\s*((?:\d+\.\d+(?:\s*\([a-z]+\))?"
                                         r"[\s,]*)+)", item):
                for n in re.findall(r"\d+\.\d+", nums):
                    gid = ("DIR-" if kind.startswith("Dir") else "") + n
                    out.setdefault(gid, []).append({"cert": r["id"], "cited_as": ed})
    return out


def toolchain_checks() -> tuple[dict, set[str], set[str]]:
    """clang-tidy checks and Clang Static Analyzer checkers of the local (pinned) toolchain."""
    def run(cmd: list[str]) -> str:
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
        except Exception:                                   # noqa: BLE001
            return ""
    ct = {ln.strip() for ln in run(["clang-tidy", "--list-checks", "-checks=*"]).splitlines()[1:]
          if ln.strip()}
    sa = {ln.split()[0] for ln in run(["clang", "-cc1", "-analyzer-checker-help"]).splitlines()
          if ln.startswith("  ") and ln.split() and "." in ln.split()[0]}
    ver = {}
    for tool in ("clang-tidy", "clang", "cppcheck"):
        m = re.search(r"(\d+\.\d+(?:\.\d+)?)", run([tool, "--version"]))
        ver[tool] = m.group(1) if m else ""
    return ver, ct, sa


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cppcheck", required=True, type=Path)
    ap.add_argument("--autosar", required=True, type=Path)
    a = ap.parse_args()

    cc = cppcheck_lists(a.cppcheck)
    au_txt = a.autosar.read_text(encoding="utf-8", errors="replace")
    au = autosar_rules(au_txt)
    au_cert = autosar_cert_trace(au_txt)
    overlay = yaml.safe_load((ROOT / "data" / "guideline_overlay.yaml").read_text())
    cert = json.loads((ROOT / "data" / "rules.json").read_text())
    cert_ids = {r["id"] for r in cert["rules"]}
    misra_c_cert = cert_misra_c_refs(cert)

    recs: list[dict] = []

    def rec(std: str, local: str, kind: str, cls: str, section: str, **extra) -> dict:
        meta = STANDARDS[std]
        sec_name = overlay["sections"][std].get(section)
        r = {"id": meta["prefix"] + local, "standard": std, "local_id": local,
             "lang": meta["lang"], "kind": kind, "classification": cls,
             "category": section, "category_name": sec_name,
             "summary": overlay["summaries"].get(std, {}).get(local),
             "decidability": None, "enforcement": None, "cert": [], "checkers": []}
        r.update(extra)
        recs.append(r)
        return r

    def add_checker(r: dict, tool: str, checker: str, specific: bool, source: str,
                    line_regex: str | None = None) -> None:
        if not any(c["tool"] == tool and c["checker"] == checker for c in r["checkers"]):
            c = {"tool": tool, "checker": checker, "specific": specific, "source": source}
            if line_regex:
                c["line_regex"] = line_regex
            r["checkers"].append(c)

    # MISRA C:2012 (+ amendments)
    for a1, b, c, _amd in cc["dirs"]:
        rec("misra-c-2012", f"DIR-{a1}.{b}", "directive", CLASS[c], f"D{a1}")
    for a1, b, c, _amd in cc["rules"]:
        r = rec("misra-c-2012", f"{a1}.{b}", "rule", CLASS[c], a1)
        if r["local_id"] in cc["addon_rules"]:
            add_checker(r, "cppcheck", f"misra-c2012-{r['local_id']}", True, "cppcheck-misra-addon")
        for t in cc["map_c"].get(r["local_id"], []):
            add_checker(r, "cppcheck", t, False, "cppcheck-idmapping")
    # MISRA C++:2023
    for a1, b, c, cl in cc["cpp23"]:
        local = f"{a1}.{b}.{c}"
        is_dir = local in CPP2023_DIRECTIVES
        r = rec("misra-cpp-2023", ("DIR-" if is_dir else "") + local,
                "directive" if is_dir else "rule", CLASS[cl], a1)
        for t in cc["map_cpp23"].get(("Dir " if is_dir else "") + local, []):
            add_checker(r, "cppcheck", t, False, "cppcheck-idmapping")
    # AUTOSAR C++14
    def au_key(x: str) -> tuple:
        p, rest = x[0], x[1:]
        return tuple(int(n) for n in rest.split("-")) + (p,)
    for rid in sorted(au, key=au_key):
        info = au[rid]
        r = rec("autosar-cpp14", rid, "rule", info["classification"], rid[1:].split("-")[0],
                enforcement=info["enforcement"], target=info["target"])
        for t in cc["map_autosar"].get(rid.lower(), []):
            add_checker(r, "cppcheck", t, False, "cppcheck-idmapping")

    by_id = {r["id"]: r for r in recs}
    # curated analyzer mappings
    for std, m in overlay["checkers"].items():
        for local, cs in m.items():
            r = by_id[STANDARDS[std]["prefix"] + local]
            for c in cs:
                add_checker(r, c["tool"], c["checker"], bool(c["specific"]), "curated",
                            c.get("line_regex"))
    # CERT cross-references
    for gid, refs in misra_c_cert.items():
        r = by_id.get("MISRA-C-2012-" + gid)
        if not r:
            continue
        for ref in refs:
            if ref["cert"] in cert_ids and not any(x["id"] == ref["cert"] for x in r["cert"]):
                r["cert"].append({"id": ref["cert"], "relation": "related",
                                  "source": f"SEI CERT C 'Related Guidelines' ({ref['cited_as']})"})
    for cid, t in au_cert.items():
        if cid not in cert_ids:
            continue
        for rid in t["related"]:
            r = by_id.get("AUTOSAR-" + rid)
            if r and not any(x["id"] == cid for x in r["cert"]):
                r["cert"].append({"id": cid, "relation": t["relation"],
                                  "source": "AUTOSAR C++14 Appendix B.4"})
    for r in recs:
        r["cert"].sort(key=lambda x: x["id"])
    ver, ct, sa = toolchain_checks()
    for r in recs:
        for c in r["checkers"]:
            if c["tool"] == "clang-tidy":
                c["available"] = c["checker"] in ct
            elif c["tool"] == "clangsa":
                c["available"] = c["checker"] in sa
            else:
                c["available"] = ver.get("cppcheck") == CPPCHECK_TAG

    out = {
        "schema": 1,
        "text_shipped": False,
        "notice": ("Facts only: guideline IDs, classifications, enforcement, checker mappings and "
                   "CERT cross-references. `summary` values are original paraphrases written for "
                   "cert-review-mcp, not MISRA or AUTOSAR text."),
        "sources": {
            "cppcheck": {"repository": "https://github.com/danmar/cppcheck", "tag": CPPCHECK_TAG,
                         "commit": git_head(a.cppcheck), "license": "GPL-3.0-or-later (facts only)",
                         "files": ["lib/checkers.cpp", "lib/checkersidmapping.cpp",
                                   "addons/misra.py"]},
            "autosar": {"document": AUTOSAR_URL,
                        "facts": "rule IDs, classification, allocated target, enforcement; "
                                 "Appendix B.4 traceability to SEI CERT C++"},
            "sei_cert": {"file": "data/rules.json",
                         "facts": "MISRA C IDs in the Related Guidelines tables (CC BY 4.0)"},
            "overlay": {"file": "data/guideline_overlay.yaml",
                        "facts": "section names, original summaries, curated clang-tidy/Clang "
                                 "Static Analyzer mappings"},
        },
        "toolchain_versions": {"clang-tidy": ver.get("clang-tidy"), "clangsa": ver.get("clang"),
                               "cppcheck": ver.get("cppcheck")},
        "standards": {k: {kk: vv for kk, vv in v.items() if kk != "prefix"} | {
            "prefix": v["prefix"],
            "count": sum(1 for r in recs if r["standard"] == k),
            "summaries": sum(1 for r in recs if r["standard"] == k and r["summary"])}
            for k, v in STANDARDS.items()},
        "guidelines": recs,
    }
    (ROOT / "data" / "guidelines.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    for k, v in out["standards"].items():
        print(k, v["count"], "summaries:", v["summaries"])


if __name__ == "__main__":
    main()
