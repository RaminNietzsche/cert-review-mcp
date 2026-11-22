import subprocess

from cert_review import diffutil

DIFF = """diff --git a/src/a.cc b/src/a.cc
--- a/src/a.cc
+++ b/src/a.cc
@@ -3,2 +3,3 @@ ctx
 keep
-old
+new1
+new2
@@ -20,0 +22,1 @@
+tail
diff --git a/gone.cc b/gone.cc
--- a/gone.cc
+++ /dev/null
@@ -1,2 +0,0 @@
-x
-y
"""


def test_parse_unified_diff():
    d = diffutil.parse_unified_diff(DIFF)
    assert d == {"src/a.cc": {4, 5, 22}}


def test_hunks_with_context_merge():
    r = diffutil.hunks_with_context(DIFF, 3)
    assert r["src/a.cc"][0] == (1, 8) and r["src/a.cc"][-1] == (19, 25)


def test_reconstruct_and_materialize():
    files = diffutil.reconstruct_file_contents(DIFF)
    assert "src/a.cc" in files
    assert "new1" in files["src/a.cc"]
    assert "gone.cc" not in files


def test_prepare_diff_workspace_materializes_in_temp(tmp_path):
    repo = tmp_path / "proj"
    repo.mkdir()
    ws = diffutil.prepare_diff_workspace(str(repo), DIFF)
    try:
        p = ws.root / "src/a.cc"
        assert p.is_file()
        assert not (repo / "src").exists()
        assert str(p.resolve()) in ws.abs_changed()
    finally:
        ws.cleanup()


def test_git_diff_roundtrip(tmp_path):
    def git(*a):
        subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                       check=True, capture_output=True)
    git("init", "-q")
    (tmp_path / "x.c").write_text("a\nb\nc\n")
    git("add", "."); git("commit", "-qm", "1")
    (tmp_path / "x.c").write_text("a\nB\nc\nd\n")
    git("commit", "-qam", "2")
    d = diffutil.parse_unified_diff(diffutil.git_diff(tmp_path, "HEAD~1", "HEAD"))
    assert d == {"x.c": {2, 4}}
