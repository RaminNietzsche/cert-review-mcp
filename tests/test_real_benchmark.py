"""Real-code benchmark: corpus schema and the scoring helpers (no network, no analyzers)."""
import importlib.util
import re
from pathlib import Path

import yaml

from cert_review import rules as R

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_real_benchmark", ROOT / "tools/run_real_benchmark.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)

SHA = re.compile(r"^[0-9a-f]{40}$")


def test_cases_schema():
    spec = yaml.safe_load((ROOT / "benchmark/cases.yaml").read_text())
    projects, cases = spec["projects"], spec["cases"]
    assert len(cases) >= 30
    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids))
    for c in cases:
        assert c["project"] in projects, c["id"]
        assert SHA.match(c["fix_commit"]) and SHA.match(c["vulnerable_commit"]), c["id"]
        assert c["fix_commit"] != c["vulnerable_commit"]
        assert c["kind"] in ("cve", "security-fix")
        assert (c["kind"] == "cve") == bool(c.get("cve")), c["id"]
        assert c["files"] and all(re.search(r"\.(c|cc|cpp|h|hpp)$", f) for f in c["files"]), c["id"]
        assert all(re.match(r"^CWE-\d+$", w) for w in c["cwe"]), c["id"]
        for r in c["cert"]:
            assert R.get(r), (c["id"], r)
        assert c["sources"] and all(s.startswith("https://") for s in c["sources"])
    assert sum(c["project"] == "ceph" for c in cases) >= 15


def test_regions_old_and_new_side():
    diff = """diff --git a/x.c b/x.c
--- a/x.c
+++ b/x.c
@@ -10,2 +10,3 @@ f()
-a
-b
+a2
+b2
+c2
@@ -20,0 +22,2 @@ g()
+check
+check2
@@ -30 +32,0 @@ h()
-gone
"""
    old, new = B.regions(diff)
    assert old["x.c"] == {10, 11, 20, 21, 30}
    assert new["x.c"] == {10, 11, 12, 22, 23, 31, 32}


def test_score_outcomes():
    case = {"cert": ["INT31-C"], "cwe": ["CWE-122"]}
    old = {"a.c": {10}}
    new = {"a.c": {10}}
    hit = {"file": "a.c", "line": 12, "rule": "INT31-C", "checker": "c"}
    other = {"file": "a.c", "line": 9, "rule": "DCL00-C", "checker": "c"}
    far = {"file": "a.c", "line": 40, "rule": "INT31-C", "checker": "c"}
    side = lambda fs: {"findings": fs, "partial_files": []}  # noqa: E731
    r = B.score(case, side([hit]), side([]), old, new, 3)
    assert r["outcome"] == "detected" and r["fix_sensitive"]
    r = B.score(case, side([hit]), side([hit]), old, new, 3)
    assert r["outcome"] == "detected" and not r["fix_sensitive"] and r["fixed_region_matching"] == 1
    assert B.score(case, side([other]), side([]), old, new, 3)["outcome"] == "wrong-rule"
    assert B.score(case, side([far]), side([]), old, new, 3)["outcome"] == "miss"
    assert B.score({"cert": [], "cwe": []}, side([hit]), side([]), old, new, 3)["outcome"] == "not-applicable"


def test_match_by_cwe():
    # a rule that lists the case's CWE counts even when it is not the hand-picked rule
    rid = next(r["id"] for r in R.all_rules().values() if "CWE-476" in (r.get("cwe") or []))
    assert B.matches(rid, {"cert": ["XXX00-C"], "cwe": ["CWE-476"]})
    assert not B.matches("DCL00-C", {"cert": ["EXP34-C"], "cwe": ["CWE-476"]})
