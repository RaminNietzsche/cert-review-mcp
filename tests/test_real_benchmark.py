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


def _repo_with(tmp_path, files: dict[str, str]):
    import subprocess
    wt = tmp_path / "src"
    wt.mkdir(parents=True)
    for k, v in files.items():
        (wt / k).parent.mkdir(parents=True, exist_ok=True)
        (wt / k).write_text(v)
    env = ["-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false"]
    subprocess.run(["git", "init", "-q", str(wt)], check=True)
    subprocess.run(["git", *env, "-C", str(wt), "add", "-A"], check=True)
    subprocess.run(["git", *env, "-C", str(wt), "commit", "-q", "-m", "x"], check=True)
    sha = subprocess.run(["git", "-C", str(wt), "rev-parse", "HEAD"], capture_output=True,
                         text=True, check=True).stdout.strip()
    return wt / ".git", sha


def test_tree_cxx_std_from_cmake(tmp_path):
    git_dir, sha = _repo_with(tmp_path, {"src/CMakeLists.txt": "set(CMAKE_CXX_STANDARD 17)\n"})
    assert B.tree_cxx_std(git_dir, sha) == "c++17"


def test_tree_cxx_std_from_flag_and_missing(tmp_path):
    git_dir, sha = _repo_with(tmp_path, {"CMakeLists.txt": 'set(CMAKE_CXX_FLAGS "-std=c++1z")\n'})
    assert B.tree_cxx_std(git_dir, sha) == "c++17"
    git_dir2, sha2 = _repo_with(tmp_path / "b", {"README": "x\n"})
    assert B.tree_cxx_std(git_dir2, sha2) is None


def test_confident_outcome_ignores_low_confidence_findings():
    case = {"cert": ["ARR30-C"], "cwe": ["CWE-787"]}
    old = {"a.c": {10}}
    vul = {"findings": [{"file": "a.c", "line": 10, "rule": "INT31-C", "checker": "x", "confidence": 0.45},
                        {"file": "a.c", "line": 11, "rule": "ARR30-C", "checker": "y", "confidence": 0.65}],
           "partial_files": []}
    fix = {"findings": [], "partial_files": []}
    r = B.score(case, vul, fix, old, {"a.c": {10}}, 3)
    assert r["outcome"] == "detected" and r["outcome_confident"] == "detected"
    vul["findings"] = vul["findings"][:1]
    r = B.score(case, vul, fix, old, {"a.c": {10}}, 3)
    assert r["outcome"] == "wrong-rule" and r["outcome_confident"] == "miss"
