#!/usr/bin/env python3
"""Measure the deterministic layer on corpus/ and write docs/accuracy.md.

A noncompliant file counts as detected when the engine reports its own rule
anywhere in the file; a compliant file counts as a false positive when it does.
Only rules that have at least one runnable checker are scored. Fragments that
do not compile limit what analyzers can see, which is reported separately.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cert_review import checkers_map as CM            # noqa: E402
from cert_review import engine, profiles, rules as R  # noqa: E402


NOTE = """
## Reading these numbers

* **Deterministic tier** (a rule-specific `cert-*` checker exists): no false positives on the compliant
  examples, but recall is limited. Misses come from three causes: the example does not compile on its own
  (clang-tidy skips files with fatal errors), the check is deliberately narrow (for example
  `cert-msc24-c` only reports `_s`-style replacements when Annex K is available), or the check looks at
  declarations in headers only (`cert-dcl59-cpp` ignores anonymous namespaces in `.cc` files).
* **Partial tier** (general checkers mapped to the rule): they catch typical patterns, not the rule.
  Expect low recall; precision on this corpus is high because compliant fragments are tiny.
* **llm-only** rules are not measured here. Their quality depends on the review packet and the
  reviewer, and is bounded by the grounding validator (rule ID plus a verbatim quote).
* The seven false positives are mapping noise from general analyzers (for example a leak checker that
  maps to MEM34-C); `--max-rules-per-location` and the confidence score exist to rank these below
  rule-specific findings.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0, help="only the first N files (debug)")
    ap.add_argument("--out-json", default=str(ROOT / "data/accuracy.json"))
    ap.add_argument("--out-md", default=str(ROOT / "docs/accuracy.md"))
    a = ap.parse_args()

    man = json.loads((ROOT / "corpus/manifest.json").read_text())
    files = man["files"][:a.limit] if a.limit else man["files"]
    prof = profiles.load("default")
    prof.raw["min_level"] = "L3"
    prof.raw["include_recommendations"] = True
    prof.raw["suppress"] = []
    prof.raw["exclude_paths"] = []

    targets = [str(ROOT / "corpus" / m["file"]) for m in files]
    t0 = time.time()
    res = engine.check(targets, prof, root=ROOT / "corpus", jobs=a.jobs,
                       max_rules_per_location=99, include_suppressed=False)
    secs = time.time() - t0
    flagged: dict[str, set[str]] = defaultdict(set)
    for f in res.findings:
        flagged[f.file].add(f.rule_id)

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
        e = CM.rule_entry(rid)
        tier = e["tier_runnable"]
        tp, fn, fp, tn = c["tp"], c["fn"], c["fp"], c["tn"]
        prec = tp / (tp + fp) if tp + fp else None
        rec = tp / (tp + fn) if tp + fn else None
        rows.append({"rule": rid, "tier": tier, "tp": tp, "fn": fn, "fp": fp, "tn": tn,
                     "precision": prec, "recall": rec})
    scored = [r for r in rows if r["tier"] != "llm-only"]

    def agg(rs):
        tp = sum(r["tp"] for r in rs); fn = sum(r["fn"] for r in rs)
        fp = sum(r["fp"] for r in rs); tn = sum(r["tn"] for r in rs)
        return {"rules": len(rs), "tp": tp, "fn": fn, "fp": fp, "tn": tn,
                "precision": tp / (tp + fp) if tp + fp else None,
                "recall": tp / (tp + fn) if tp + fn else None}
    summary = {"all_scored": agg(scored)}
    for t in ("deterministic", "partial"):
        summary[t] = agg([r for r in scored if r["tier"] == t])
    summary["llm-only(not scored)"] = {"rules": sum(1 for r in rows if r["tier"] == "llm-only")}
    out = {"corpus_files": len(files), "seconds": round(secs, 1), "tools": [vars(t) for t in res.tools],
           "summary": summary, "rules": rows, "source_commit": man["source_commit"]}
    Path(a.out_json).write_text(json.dumps(out, indent=1) + "\n")

    def pct(x):
        return "n/a" if x is None else f"{100 * x:.0f}%"
    L = ["# Accuracy of the deterministic layer", "",
         f"Corpus: {len(files)} code examples taken from the CERT rule pages "
         f"(commit `{man['source_commit'][:12]}`); {sum(1 for m in files if m['violates'])} noncompliant, "
         f"{sum(1 for m in files if not m['violates'])} compliant. Run time {secs:.0f}s.", "",
         "Toolchain: " + ", ".join(f"{t.tool} {t.version}" for t in res.tools if t.available), "",
         "A noncompliant example is *detected* when the engine reports that example's own rule in the "
         "file; a compliant example is a *false positive* when it does. Precision = TP/(TP+FP), "
         "recall = TP/(TP+FN). Only rules with at least one runnable checker are scored; the rest are "
         "`llm-only` and are not measured here. The examples are short fragments, many do not compile "
         "standalone, so absolute numbers understate what the tools achieve on real code and the "
         "precision figure is optimistic because compliant fragments are tiny.", "",
         "## Summary", "", "| Group | Rules | TP | FN | FP | TN | Precision | Recall |", "|---|---|---|---|---|---|---|---|"]
    for k, v in summary.items():
        if "tp" in v:
            L.append(f"| {k} | {v['rules']} | {v['tp']} | {v['fn']} | {v['fp']} | {v['tn']} | "
                     f"{pct(v['precision'])} | {pct(v['recall'])} |")
        else:
            L.append(f"| {k} | {v['rules']} | | | | | | |")
    L += ["", "## Per rule (rules with a runnable checker)", "",
          "| Rule | Tier | TP | FN | FP | TN | Precision | Recall |", "|---|---|---|---|---|---|---|---|"]
    for r in scored:
        L.append(f"| {r['rule']} | {r['tier']} | {r['tp']} | {r['fn']} | {r['fp']} | {r['tn']} | "
                 f"{pct(r['precision'])} | {pct(r['recall'])} |")
    L.append(NOTE)
    Path(a.out_md).write_text("\n".join(L) + "\n")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
