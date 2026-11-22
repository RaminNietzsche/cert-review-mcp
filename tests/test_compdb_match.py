import json
from pathlib import Path

from cert_review import toolrun as T


def test_compdb_entry_matches_workspace_path_by_src_suffix(tmp_path):
    ceph = tmp_path / "ceph"
    src_file = ceph / "src/rgw/foo.cc"
    src_file.parent.mkdir(parents=True)
    src_file.write_text("int x;\n")
    ws = tmp_path / "work"
    ws_file = ws / "src/rgw/foo.cc"
    ws_file.parent.mkdir(parents=True)
    ws_file.write_text("int x;\n")
    db = tmp_path / "db"
    db.mkdir()
    (db / "compile_commands.json").write_text(json.dumps([{
        "directory": str(ceph / "src"),
        "file": str(src_file),
        "arguments": ["clang++", "-Isrc/include", "-std=c++23", "-c", str(src_file)],
    }]))
    e = T.compdb_entry(str(ws_file), db)
    assert e is not None
    flags, _ = T.compile_args_from_entry(e, str(ws_file))
    assert "-std=c++23" in flags