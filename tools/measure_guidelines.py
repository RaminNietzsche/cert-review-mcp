#!/usr/bin/env python3
"""Coverage table for docs/misra-autosar.md.

1. Tier counts per standard from the bundled data (all mappings / pinned toolchain).
2. Measured: run check_files (all three analyzers, --standards misra-c-2012) on
   cppcheck's own MISRA addon test file (addons/test/misra/misra-test.c, read from a
   local cppcheck checkout, not shipped here) and compare the reported guideline IDs
   with the IDs that file annotates as expected (`// 10.4` style comments).

Usage: python3 tools/measure_guidelines.py --cppcheck ../cppcheck [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cert_review import api, rules as R  # noqa: E402

STDS = ("misra-c-2012", "misra-cpp-2023", "autosar-cpp14")


def tiers() -> dict:
    out = {}
    for s in STDS:
        c = api.rule_coverage(standard=s)
        g = R.guideline_info()["standards"][s]
        out[s] = {"total": c["total"], "all": c["all_mappings"], "runnable": c["runnable_toolchain"],
                  "summaries": g["summaries"]}
    return out


def measured(cppcheck: Path) -> dict:
    src = cppcheck / "addons" / "test" / "misra" / "misra-test.c"
    text = src.read_text(encoding="utf-8", errors="replace")
    expected: dict[int, set[str]] = {}
    for n, line in enumerate(text.splitlines(), 1):
        m = re.search(r"//\s*(\d+\.\d+(?:\s+\d+\.\d+)*)(?:$|[^\d.])", line)
        if m:
            expected[n] = {f"MISRA-C-2012-{x}" for x in m.group(1).split()}
    with tempfile.TemporaryDirectory() as d:
        dst = Path(d) / "misra-test.c"
        shutil.copy(src, dst)
        for extra in ("misra-test.h",):
            if (src.parent / extra).exists():
                shutil.copy(src.parent / extra, Path(d) / extra)
        res = api.check_file(str(dst), standards=["misra-c-2012"], min_confidence=0.0)
    found: dict[int, set[str]] = {}
    for f in res["findings"]:
        found.setdefault(f["line"], set()).add(f["rule_id"])
    exp_ids = set().union(*expected.values()) if expected else set()
    got_ids = {r for v in found.values() for r in v}
    hit_lines = sum(1 for n, ids in expected.items() if ids & found.get(n, set()))
    return {"file": "cppcheck addons/test/misra/misra-test.c",
            "expected_rule_ids": len(exp_ids), "reported_rule_ids": len(got_ids),
            "expected_ids_reported": len(exp_ids & got_ids),
            "annotated_lines": len(expected), "annotated_lines_hit": hit_lines,
            "findings": len(res["findings"]),
            "tools": {t["tool"]: t["status"] for t in res["tools"]}}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cppcheck", type=Path)
    ap.add_argument("--json")
    a = ap.parse_args()
    out = {"tiers": tiers()}
    if a.cppcheck:
        out["measured"] = measured(a.cppcheck)
    s = json.dumps(out, indent=2)
    if a.json:
        Path(a.json).write_text(s + "\n")
    print(s)


if __name__ == "__main__":
    main()
