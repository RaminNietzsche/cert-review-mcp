#!/usr/bin/env python3
"""Derive per-checker confidence scores from the dev half of the accuracy corpus.

Writes data/confidence_calibration.json: keys are ``tool:checker``, values are
precision on dev-rule examples (TP / (TP+FP)). Run after changing checker
mappings; `engine._cert_rules_for` prefers these scores over the default 0.9/0.65.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cert_review import engine, profiles as P  # noqa: E402

import importlib.util

def _eval_mod():
    spec = importlib.util.spec_from_file_location("eval_accuracy", ROOT / "tools/eval_accuracy.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--half", default="dev", choices=("dev", "held-out", "all"))
    ap.add_argument("-o", type=Path, default=ROOT / "data" / "confidence_calibration.json")
    ap.add_argument("--tools", default="clang-tidy,clangsa,cppcheck,semgrep")
    args = ap.parse_args()
    ev = _eval_mod()
    man = json.loads((ROOT / "corpus" / "manifest.json").read_text())
    tools = tuple(t.strip() for t in args.tools.split(",") if t.strip())
    tp: dict[str, int] = defaultdict(int)
    fp: dict[str, int] = defaultdict(int)
    prof = P.load("default")
    for ent in man["files"]:
        rule = ent["rule"]
        if args.half != "all" and ev.half(rule) != args.half:
            continue
        path = ROOT / "corpus" / rule / ent["file"]
        nc = ent.get("kind") == "noncompliant"
        res = engine.check([str(path)], prof, tools=tools, include_suppressed=True)
        for f in res.findings + res.suppressed:
            if f.rule_id != rule:
                continue
            key = f"{f.tool}:{f.checker}"
            if nc:
                tp[key] += 1
            else:
                fp[key] += 1
    out = {}
    for key in set(tp) | set(fp):
        t, p = tp[key], fp[key]
        if t + p:
            out[key] = round(t / (t + p), 2)
    args.o.write_text(json.dumps({"half": args.half, "tools": list(tools), "scores": out}, indent=2) + "\n")
    print(f"wrote {len(out)} scores to {args.o}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())