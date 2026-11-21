import json

from cert_review import cli


def test_explain(capsys):
    assert cli.main(["explain", "EXP34-C"]) == 0
    out = capsys.readouterr().out
    assert "Do not dereference null pointers" in out and "Coverage:" in out


def test_explain_unknown(capsys):
    assert cli.main(["explain", "XYZ99-C", "--json"]) == 1


def test_coverage_json(capsys):
    cli.main(["coverage", "--lang", "c", "--kind", "rule"])
    d = json.loads(capsys.readouterr().out)
    assert d["total"] == 122 and set(d["all_mappings"]) == {"deterministic", "partial", "llm-only"}


def test_rules_listing(capsys):
    cli.main(["rules", "--lang", "cpp", "--coverage", "deterministic"])
    assert capsys.readouterr().out.count("-CPP") >= 18


def test_validate_exit_code(tmp_path, capsys):
    p = tmp_path / "f.json"
    p.write_text(json.dumps([{"rule_id": "NOPE00-C", "file": "a", "line": 1, "message": "x", "quote": "y"}]))
    assert cli.main(["validate", str(p)]) == 1


def test_diff_from_stdin_text(tmp_path, monkeypatch, capsys):
    f = tmp_path / "a.c"
    f.write_text("#include <stdlib.h>\nint a(const char *s) { return atoi(s); }\n")
    d = tmp_path / "x.diff"
    d.write_text("--- a/a.c\n+++ b/a.c\n@@ -0,0 +1,2 @@\n+#include <stdlib.h>\n+int a(const char *s) { return atoi(s); }\n")
    rc = cli.main(["diff", "--repo", str(tmp_path), "--diff-file", str(d), "--tools", "clang-tidy",
                   "--format", "json", "--fail-on", "warning"])
    out = capsys.readouterr().out
    import shutil
    if shutil.which("clang-tidy"):
        assert rc == 1 and "ERR34-C" in out
