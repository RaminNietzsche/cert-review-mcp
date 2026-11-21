#!/usr/bin/env python3
"""Measure the deterministic layer on corpus/ and write docs/accuracy.md.

A noncompliant file counts as detected when the engine reports its own rule
anywhere in the file; a compliant file counts as a false positive when it does.
Fragments that do not compile limit what analyzers can see.

The core analyzers (clang-tidy, Clang Static Analyzer, cppcheck) run together,
as in a normal check. Each optional analyzer (semgrep, infer, codeql) runs on
its own, and toolset rows are the union of the files each one flags; that is
what a combined run reports, because findings of different tools are merged,
never removed (the evaluation sets max_rules_per_location high and
min_confidence to 0).

CodeQL is run with one database per corpus file and only the queries mapped to
that file's rule. Putting all fragments into one database would make
whole-program queries (one-definition rule, incompatible declarations) fire
across unrelated examples that all define `f()` or `main()`.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cert_review import analyzers_extra as EX          # noqa: E402
from cert_review import checkers_map as CM            # noqa: E402
from cert_review import engine, profiles               # noqa: E402
from cert_review import toolrun as T                   # noqa: E402

CORE = ("clang-tidy", "clangsa", "cppcheck")
NOTE = """
## Reading these numbers

* **Semgrep figures are in-sample.** The bundled rules in `data/semgrep/` were written while
  looking at these CERT examples, so their recall here overstates what they find in other code.
  An out-of-sample check on Ceph is in [analyzers.md](analyzers.md).
* **CodeQL** ran with one database per example and only the queries mapped to that example's
  rule. Whole-program queries (DCL40-C, DCL60-CPP) need two translation units, which a single
  example file does not have.
* **Infer** needs code that compiles; most fragments here do not compile standalone, so its
  recall on this corpus is low. It is more useful with a real `compile_commands.json`.
* **Deterministic tier** (a rule-specific `cert-*` check or CodeQL CERT query): misses come
  from fragments that do not compile, deliberately narrow checks, and checks that only look at
  headers. **Partial tier** (general checkers and Semgrep rules): typical patterns, not the
  whole rule.
* **llm-only** rules are not measured here. Their quality depends on the review packet and the
  reviewer, and is bounded by the grounding validator (rule ID plus a verbatim quote).
* False positives on compliant examples are mostly mapping noise from general analyzers (for
  example a leak checker mapped to several MEM rules); `--max-rules-per-location` and the
  confidence score rank these below rule-specific findings.
"""

TOOLSETS = [
    ("baseline: clang-tidy, clangsa, cppcheck", ("core",)),
    ("reference image: + semgrep", ("core", "semgrep")),
    ("+ infer", ("core", "semgrep", "infer")),
    ("+ codeql (all analyzers)", ("core", "semgrep", "infer", "codeql")),
]


def profile():
    prof = profiles.load("default")
    prof.raw["min_level"] = "L3"
    prof.raw["include_recommendations"] = True
    prof.raw["suppress"] = []
    prof.raw["exclude_paths"] = []
    return prof


def flagged_by_engine(targets, tools, jobs):
    res = engine.check(targets, profile(), root=ROOT / "corpus", jobs=jobs, tools=tools,
                       max_rules_per_location=99, include_suppressed=False)
    out = defaultdict(set)
    for f in res.findings:
        out[f.file].add(f.rule_id)
    return out, res.tools


def codeql_queries() -> dict[str, Path]:
    """query id -> .ql path in the installed CERT packs."""
    out = {}
    base = Path.home() / ".codeql/packages/codeql"
    for q in base.glob("cert-*-coding-standards/*/rules/**/*.ql"):
        m = re.search(r"@id\s+(\S+)", q.read_text(errors="replace").split("*/", 1)[0])
        if m:
            out[m.group(1)] = q
    return out


def flagged_by_codeql_isolated(files, jobs):
    exe = T.which("codeql")
    st = T.ToolStatus("codeql", bool(exe), T.version("codeql") if exe else "")
    out = defaultdict(set)
    if not exe:
        return out, [st]
    qpath = codeql_queries()
    by_rule = defaultdict(list)
    for (tool, chk), ents in CM.reverse_index().items():
        if tool == "codeql" and chk in qpath:
            for e in ents:
                by_rule[e["rule_id"]].append(qpath[chk])
    prof = profile()

    def one(m):
        rule = m["rule"]
        qs = sorted(set(by_rule.get(rule, [])))
        if not qs:
            return m, None, "no-query"
        src = ROOT / "corpus" / m["file"]
        with tempfile.TemporaryDirectory(prefix="cr-eval-cq-") as tmp:
            t = Path(tmp)
            (t / "src").mkdir()
            dst = t / "src" / src.name
            dst.write_bytes(src.read_bytes())
            r = subprocess.run([exe, "database", "create", str(t / "db"), "--language=cpp",
                                "--build-mode=none", f"--source-root={t / 'src'}", "-q",
                                "--threads=2"], capture_output=True, text=True)
            if r.returncode != 0:
                return m, None, "db-failed"
            r = subprocess.run([exe, "database", "analyze", str(t / "db"), *map(str, qs),
                                "--format=sarifv2.1.0", f"--output={t / 'o.sarif'}", "--threads=2",
                                "-q"], capture_output=True, text=True)
            if r.returncode != 0:
                return m, None, "analyze-failed: " + r.stderr[-200:]
            doc = json.loads((t / "o.sarif").read_text())
        raw = []
        for run in doc.get("runs", []):
            for res in run.get("results", []):
                loc = res["locations"][0]["physicalLocation"]
                raw.append(T.RawFinding("codeql", res["ruleId"], str(src),
                                        loc.get("region", {}).get("startLine", 1), 1,
                                        res["message"]["text"]))
        kept, _ = engine.normalize(raw, prof, root=ROOT / "corpus")
        return m, {f.rule_id for f in kept}, "ok"

    errors = defaultdict(int)
    with ThreadPoolExecutor(max_workers=max(1, jobs // 2)) as ex:
        for m, rules, status in ex.map(one, files):
            errors[status.split(":")[0]] += 1
            if rules:
                out[str((ROOT / "corpus" / m["file"]).resolve())] |= rules
    st.files = len(files)
    st.notes.append(", ".join(f"{k}={v}" for k, v in sorted(errors.items())))
    return out, [st]


def score(files, flagged, tools_for_tier):
    per = defaultdict(lambda: {"tp": 0, "fn": 0, "fp": 0, "tn": 0})
    for m in files:
        path = str(Path(ROOT / "corpus" / m["file"]).resolve())
        hit = m["rule"] in flagged.get(path, set())
        c = per[m["rule"]]
        if m["violates"]:
            c["tp" if hit else "fn"] += 1
        else:
            c["fp" if hit else "tn"] += 1
    rows = []
    for rid, c in sorted(per.items()):
        tier = CM.tier_for_tools(rid, tools_for_tier)
        tp, fn, fp, tn = c["tp"], c["fn"], c["fp"], c["tn"]
        rows.append({"rule": rid, "tier": tier, "tp": tp, "fn": fn, "fp": fp, "tn": tn,
                     "precision": tp / (tp + fp) if tp + fp else None,
                     "recall": tp / (tp + fn) if tp + fn else None})
    return rows


def agg(rs):
    tp = sum(r["tp"] for r in rs); fn = sum(r["fn"] for r in rs)
    fp = sum(r["fp"] for r in rs); tn = sum(r["tn"] for r in rs)
    return {"rules": len(rs), "tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None}


def _rel(path: str) -> str:
    try:
        return str(Path(path).resolve().relative_to((ROOT / "corpus").resolve()))
    except ValueError:
        return path


def pct(x):
    return "n/a" if x is None else f"{100 * x:.0f}%"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0, help="only the first N files (debug)")
    ap.add_argument("--rules", default="", help="comma-separated rule IDs to measure (debug)")
    ap.add_argument("--tools", default="core,semgrep,infer,codeql",
                    help="analyzer groups to measure: core (clang-tidy+clangsa+cppcheck), semgrep, "
                         "infer, codeql; missing ones are skipped")
    ap.add_argument("--out-json", default=str(ROOT / "data/accuracy.json"))
    ap.add_argument("--out-md", default=str(ROOT / "docs/accuracy.md"))
    ap.add_argument("--reuse", default="",
                    help="take the per-analyzer results of these groups from an earlier --out-json "
                         "(comma-separated group names) instead of running them again")
    ap.add_argument("--from-json", default="",
                    help="re-render the Markdown from an earlier --out-json without running analyzers")
    a = ap.parse_args()

    man = json.loads((ROOT / "corpus/manifest.json").read_text())
    files = man["files"]
    if a.rules:
        want = {r.strip().upper() for r in a.rules.split(",")}
        files = [m for m in files if m["rule"] in want]
    files = files[:a.limit] if a.limit else files
    if a.from_json:
        Path(a.out_md).write_text(render(json.loads(Path(a.from_json).read_text()), files))
        return 0
    targets = [str(ROOT / "corpus" / m["file"]) for m in files]
    groups = [g.strip() for g in a.tools.split(",") if g.strip()]
    flagged: dict[str, dict] = {}
    statuses, secs = [], {}
    prev = json.loads(Path(a.out_json).read_text()) if a.reuse and Path(a.out_json).exists() else {}
    reuse = {g.strip() for g in a.reuse.split(",") if g.strip()}
    for g in groups:
        t0 = time.time()
        if g in reuse and g in prev.get("flagged", {}):
            flagged[g] = defaultdict(set, {str((ROOT / "corpus" / k).resolve()): set(v)
                                           for k, v in prev["flagged"][g].items()})
            secs[g] = prev["seconds"][g]
            statuses += [t for t in prev["tools"] if t["tool"] in (CORE if g == "core" else (g,))]
            print(g, "reused", flush=True)
            continue
        if g == "core":
            flagged[g], st = flagged_by_engine(targets, CORE, a.jobs)
        elif g == "codeql":
            if not EX.available("codeql"):
                print("codeql not installed; skipped"); continue
            flagged[g], st = flagged_by_codeql_isolated(files, a.jobs)
        else:
            if not EX.available(g):
                print(f"{g} not installed; skipped"); continue
            flagged[g], st = flagged_by_engine(targets, (g,), a.jobs)
        secs[g] = round(time.time() - t0, 1)
        statuses += [{**vars(s), "status": s.status} for s in st]
        print(g, "done in", secs[g], "s", flush=True)

    n_nc = sum(1 for m in files if m["violates"])
    n_ok = len(files) - n_nc
    results = []
    for label, need in TOOLSETS:
        if not all(g in flagged for g in need):
            continue
        union = defaultdict(set)
        for g in need:
            for k, v in flagged[g].items():
                union[k] |= v
        tools = [*(CORE if "core" in need else ()), *(g for g in need if g != "core")]
        rows = score(files, union, tools)
        scored = [r for r in rows if r["tier"] != "llm-only"]
        summary = {"all_scored": agg(scored)}
        for t in ("deterministic", "partial"):
            summary[t] = agg([r for r in scored if r["tier"] == t])
        summary["llm-only(not scored)"] = {"rules": sum(1 for r in rows if r["tier"] == "llm-only")}
        whole = agg(rows)
        summary["corpus_wide"] = whole | {"noncompliant": n_nc, "compliant": n_ok}
        results.append({"label": label, "groups": list(need), "tools": tools,
                        "summary": summary, "rules": rows})

    base_ids = {r["rule"] for r in results[0]["rules"] if r["tier"] != "llm-only"} if results else set()
    out = {"corpus_files": len(files), "source_commit": man["source_commit"],
           "seconds": secs, "tools": statuses, "toolsets": results,
           "baseline_rules": sorted(base_ids),
           "flagged": {g: {_rel(k): sorted(v) for k, v in sorted(f.items()) if v}
                       for g, f in flagged.items()}}
    Path(a.out_json).write_text(json.dumps(out, indent=1) + "\n")
    Path(a.out_md).write_text(render(out, files))
    for r in results:
        print(r["label"], json.dumps(r["summary"]["all_scored"]), json.dumps(r["summary"]["corpus_wide"]))
    return 0


def render(out, files) -> str:
    res = out["toolsets"]
    vers = {}
    for t in out["tools"]:
        if t["available"]:
            vers[t["tool"]] = t["version"]
    n_nc = sum(1 for m in files if m["violates"])
    L = ["# Accuracy of the deterministic layer", "",
         f"Corpus: {len(files)} code examples taken from the CERT rule pages "
         f"(commit `{out['source_commit'][:12]}`); {n_nc} noncompliant, {len(files) - n_nc} compliant.", "",
         "Toolchain: " + ", ".join(f"{k} {v}" for k, v in vers.items()) +
         ". CodeQL ran the `codeql/cert-c-coding-standards` and `codeql/cert-cpp-coding-standards` "
         "packs (" + ", ".join(f"{k} {v}" for k, v in CM.info()["sources"].get("codeql", {}).get("packs", {}).items()) + ").", "",
         "Run time: " + ", ".join(f"{k} {v:.0f}s" for k, v in out["seconds"].items()) + ".", "",
         "A noncompliant example is *detected* when the engine reports that example's own rule in the "
         "file; a compliant example is a *false positive* when it does. Precision = TP/(TP+FP), "
         "recall = TP/(TP+FN). *Scored rules* are the rules with at least one checker in the toolset; "
         "*corpus-wide* counts every example, including rules no checker covers, so it is the "
         "number to compare across toolsets. The examples are short fragments and many do not "
         "compile standalone, so absolute numbers understate what the tools achieve on real code, "
         "and precision is optimistic because compliant fragments are tiny.", "",
         "## Summary", "",
         "| Toolset | Scored rules | TP | FN | FP | TN | Precision | Recall (scored) | Corpus-wide recall | Corpus-wide FP rate |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in res:
        s, w = r["summary"]["all_scored"], r["summary"]["corpus_wide"]
        L.append(f"| {r['label']} | {s['rules']} | {s['tp']} | {s['fn']} | {s['fp']} | {s['tn']} | "
                 f"{pct(s['precision'])} | {pct(s['recall'])} | {pct(w['tp'] / w['noncompliant'])} "
                 f"({w['tp']}/{w['noncompliant']}) | {pct(w['fp'] / w['compliant'])} ({w['fp']}/{w['compliant']}) |")
    base = set(out["baseline_rules"])
    if base and len(res) > 1:
        L += ["", f"### The {len(base)} rules the baseline scores", "",
              "Same rules for every toolset, so the rows differ only by what the added analyzers find.", "",
              "| Toolset | TP | FN | FP | TN | Precision | Recall |", "|---|---|---|---|---|---|---|"]
        for r in res:
            s = agg([x for x in r["rules"] if x["rule"] in base])
            L.append(f"| {r['label']} | {s['tp']} | {s['fn']} | {s['fp']} | {s['tn']} | "
                     f"{pct(s['precision'])} | {pct(s['recall'])} |")
    for r in res:
        s = r["summary"]
        L += ["", f"### By tier: {r['label']}", "",
              "| Group | Rules | TP | FN | FP | TN | Precision | Recall |", "|---|---|---|---|---|---|---|---|"]
        for k in ("all_scored", "deterministic", "partial"):
            v = s[k]
            L.append(f"| {k} | {v['rules']} | {v['tp']} | {v['fn']} | {v['fp']} | {v['tn']} | "
                     f"{pct(v['precision'])} | {pct(v['recall'])} |")
        L.append(f"| llm-only (not scored) | {s['llm-only(not scored)']['rules']} | | | | | | |")
    for r in (res[1:2] + res[-1:]) if len(res) > 1 else res:
        L += ["", f"## Per rule: {r['label']}", "",
              "| Rule | Tier | TP | FN | FP | TN | Precision | Recall |", "|---|---|---|---|---|---|---|---|"]
        for x in r["rules"]:
            if x["tier"] == "llm-only":
                continue
            L.append(f"| {x['rule']} | {x['tier']} | {x['tp']} | {x['fn']} | {x['fp']} | {x['tn']} | "
                     f"{pct(x['precision'])} | {pct(x['recall'])} |")
    L += ["", NOTE.strip()]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main())
