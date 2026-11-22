"""Diff mode must not write into the user's repository and must analyse the post-image."""
import subprocess
from pathlib import Path

from cert_review import api, diffutil

DIFF = """diff --git a/src/a.cc b/src/a.cc
--- a/src/a.cc
+++ b/src/a.cc
@@ -1,1 +1,2 @@
 old
+new
"""


def test_prepare_diff_workspace_uses_temp_not_repo(tmp_path):
    repo = tmp_path / "proj"
    repo.mkdir()
    before = list(repo.rglob("*"))
    ws = diffutil.prepare_diff_workspace(str(repo), DIFF)
    try:
        assert ws.root != repo.resolve()
        assert (ws.root / "src/a.cc").is_file()
        assert not (repo / "src/a.cc").exists()
    finally:
        ws.cleanup()
    assert list(repo.rglob("*")) == before


def test_git_diff_uses_merge_base_syntax(tmp_path):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--allow-empty", "-qm", "1"],
        check=True,
    )
    (tmp_path / "f.c").write_text("a\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t", "add", "f.c"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "2"],
        check=True,
    )
    (tmp_path / "f.c").write_text("b\n")
    out = diffutil.git_diff(tmp_path, "HEAD~1", "HEAD")
    assert "+++ b/f.c" in out


def test_review_packet_hunk_paths_are_absolute_under_temp(tmp_path):
    repo = tmp_path / "r"
    repo.mkdir()
    pk = api.review_packet(repo=str(repo), diff_text=DIFF, run_static=False)
    paths = {h["file"] for h in pk["hunks"]}
    assert len(paths) == 1
    p = paths.pop()
    assert p.endswith("src/a.cc") and Path(p).is_absolute()