import json
import subprocess
from pathlib import Path

from cert_review.api import _resolve_compdb
from cert_review.ceph_compdb import build_compdb, is_ceph_tree
from cert_review.profiles import load


def _git_commit_all(repo: Path, message: str) -> None:
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "cert-review-test"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=repo, check=True)


def test_is_ceph_tree(tmp_path: Path):
    assert not is_ceph_tree(tmp_path)
    src = tmp_path / "src" / "include"
    src.mkdir(parents=True)
    (src / "config-h.in.cmake").write_text("#cmakedefine FOO\n")
    assert is_ceph_tree(tmp_path)


def test_build_compdb_minimal(tmp_path: Path):
    src = tmp_path / "src"
    (src / "include").mkdir(parents=True)
    (src / "include" / "config-h.in.cmake").write_text("#cmakedefine HAVE_X 1\n")
    (src / "ceph_ver.h.in.cmake").write_text("@CEPH_GIT_VER@\n")
    (src / "ceph_release.h.in.cmake").write_text("@CEPH_RELEASE@\n")
    (src / "common" / "options").mkdir(parents=True)
    f = src / "rgw" / "foo.cc"
    f.parent.mkdir(parents=True)
    f.write_text("int main() { return 0; }\n")
    out = build_compdb(tmp_path, tmp_path / "out", relpaths=["src/rgw/foo.cc"])
    data = json.loads((out / "compile_commands.json").read_text())
    assert len(data) == 1
    assert data[0]["file"].endswith("src/rgw/foo.cc")


def test_build_compdb_git_show_when_missing_on_disk(tmp_path: Path):
    src = tmp_path / "src"
    (src / "include").mkdir(parents=True)
    (src / "include" / "config-h.in.cmake").write_text("#cmakedefine FOO\n")
    (src / "ceph_ver.h.in.cmake").write_text("0\n")
    (src / "ceph_release.h.in.cmake").write_text("0\n")
    (src / "common" / "options").mkdir(parents=True)
    _git_commit_all(tmp_path, "init")
    only_git = src / "rgw" / "only_in_git.cc"
    only_git.parent.mkdir(parents=True, exist_ok=True)
    only_git.write_text("int main() { return 0; }\n")
    _git_commit_all(tmp_path, "add rgw")
    only_git.unlink()
    out = build_compdb(tmp_path, tmp_path / "out", relpaths=["src/rgw/only_in_git.cc"], git_ref="HEAD")
    data = json.loads((out / "compile_commands.json").read_text())
    assert len(data) == 1
    assert "only_in_git" in data[0]["file"]


def test_resolve_compdb_synthetic_when_no_build(tmp_path: Path):
    src = tmp_path / "src"
    (src / "include").mkdir(parents=True)
    (src / "include" / "config-h.in.cmake").write_text("#cmakedefine FOO\n")
    (src / "ceph_ver.h.in.cmake").write_text("0\n")
    (src / "ceph_release.h.in.cmake").write_text("0\n")
    (src / "common" / "options").mkdir(parents=True)
    f = src / "a.cc"
    f.write_text("int x;\n")
    prof = load("ceph")
    cdb, tmp, notes = _resolve_compdb(
        None, prof, str(tmp_path), changed_relpaths=["src/a.cc"], base="HEAD", head="HEAD")
    assert cdb
    assert tmp and tmp.exists()
    assert any("synthetic" in n.lower() for n in notes)
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)