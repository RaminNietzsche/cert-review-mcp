"""Baseline fingerprints: stable under line shifts and unrelated edits."""
import json

from cert_review import api, baseline as BL, cli

SRC = """#include <stdlib.h>

int parse(const char *s) {
  int v = atoi(s);
  return v;
}

int twice(const char *s) {
  return 2 * atoi(s);
}
"""


def _finding(path, line, rule="ERR34-C"):
    return {"rule_id": rule, "file": str(path), "line": line, "tool": "clang-tidy",
            "checker": "cert-err34-c", "message": "atoi used", "severity": "warning",
            "priority": 6, "confidence": 0.9}


def _line_of(path, needle, nth=1):
    hits = [i for i, l in enumerate(path.read_text().splitlines(), 1) if needle in l]
    return hits[nth - 1]


def _write_baseline(tmp_path, findings):
    p = tmp_path / BL.DEFAULT_FILE
    BL.dump(BL.build(findings, tmp_path), p)
    return p


def test_fingerprint_ignores_line_numbers_and_indentation(tmp_path):
    f = tmp_path / "a.c"
    f.write_text(SRC)
    a = BL.fingerprint_parts(_finding(f, 4), tmp_path)
    f.write_text("/* license */\n\n\n" + SRC.replace("  int v", "\tint   v"))
    b = BL.fingerprint_parts(_finding(f, 7), tmp_path)
    assert a == b
    assert a["file"] == "a.c" and len(a["fingerprint"]) == 16


def test_shifted_findings_stay_baselined(tmp_path):
    f = tmp_path / "a.c"
    f.write_text(SRC)
    p = _write_baseline(tmp_path, [_finding(f, _line_of(f, "atoi")), _finding(f, _line_of(f, "atoi", 2))])
    f.write_text("#include <stdio.h>\n#include <string.h>\n" + SRC)
    res = {"files": [str(f)], "findings": [_finding(f, _line_of(f, "atoi")), _finding(f, _line_of(f, "atoi", 2))]}
    BL.apply(res, p)
    assert res["findings"] == []
    assert res["baseline"]["baselined"] == 2 and res["baseline"]["new"] == 0 and res["baseline"]["fixed"] == 0


def test_edited_flagged_line_matches_by_context(tmp_path):
    f = tmp_path / "a.c"
    f.write_text(SRC)
    p = _write_baseline(tmp_path, [_finding(f, 4)])
    f.write_text(SRC.replace("int v = atoi(s);", "int value = atoi(s); /* parse */"))
    res = {"files": [str(f)], "findings": [_finding(f, 4)]}
    BL.apply(res, p)
    assert res["baseline"]["baselined"] == 1 and not res["findings"]


def test_new_finding_reported_and_fixed_counted(tmp_path):
    f = tmp_path / "a.c"
    f.write_text(SRC)
    p = _write_baseline(tmp_path, [_finding(f, 4), _finding(f, 9)])
    # the first call is fixed, a new one appears in a new function
    f.write_text(SRC.replace("int v = atoi(s);", "int v = (int)strtol(s, NULL, 10);")
                 + "\nlong other(const char *t) {\n  return atol(t);\n}\n")
    new_line = _line_of(f, "atol")
    res = {"files": [str(f)], "findings": [_finding(f, 9), _finding(f, new_line)]}
    BL.apply(res, p)
    assert [x["line"] for x in res["findings"]] == [new_line]
    b = res["baseline"]
    assert (b["new"], b["baselined"], b["fixed"]) == (1, 1, 1)
    assert b["fixed_entries"][0]["line"] == 4


def test_duplicate_lines_each_consume_one_entry(tmp_path):
    f = tmp_path / "a.c"
    f.write_text("void g(char *s) {\n  atoi(s);\n  atoi(s);\n  atoi(s);\n}\n")
    p = _write_baseline(tmp_path, [_finding(f, 2), _finding(f, 3)])
    res = {"files": [str(f)], "findings": [_finding(f, 2), _finding(f, 3), _finding(f, 4)]}
    BL.apply(res, p)
    assert res["baseline"]["baselined"] == 2 and res["baseline"]["new"] == 1


def test_other_rule_same_line_is_new(tmp_path):
    f = tmp_path / "a.c"
    f.write_text(SRC)
    p = _write_baseline(tmp_path, [_finding(f, 4)])
    res = {"files": [str(f)], "findings": [_finding(f, 4, rule="INT31-C")]}
    BL.apply(res, p)
    assert res["baseline"]["new"] == 1


def test_diff_scope_does_not_report_fixed(tmp_path):
    f = tmp_path / "a.c"
    f.write_text(SRC)
    p = _write_baseline(tmp_path, [_finding(f, 4)])
    res = {"files": [str(f)], "findings": []}
    BL.apply(res, p, scope="diff")
    assert res["baseline"]["fixed"] is None and res["baseline"]["fixed_entries"] == []


def test_update_keeps_entries_outside_scope(tmp_path):
    a, b = tmp_path / "a.c", tmp_path / "b.c"
    a.write_text(SRC)
    b.write_text(SRC)
    p = _write_baseline(tmp_path, [_finding(a, 4), _finding(b, 4)])
    st = api.write_baseline({"files": [str(a)], "findings": []}, str(p), update=True)
    assert st == {**st, "entries": 1, "removed": 1, "kept_outside_scope": 1}
    assert [e["file"] for e in json.loads(p.read_text())["entries"]] == ["b.c"]


def test_load_rejects_non_baseline(tmp_path):
    p = tmp_path / "x.json"
    p.write_text("[]")
    try:
        BL.load(p)
    except ValueError as e:
        assert "not a cert-review baseline" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_cli_baseline_round_trip(tmp_path, monkeypatch, capsys):
    f = tmp_path / "a.c"
    f.write_text(SRC)
    monkeypatch.chdir(tmp_path)
    assert cli.main(["baseline", "create", "a.c", "--tools", "clang-tidy"]) == 0
    data = json.loads((tmp_path / BL.DEFAULT_FILE).read_text())
    recorded = len(data["entries"])
    assert cli.main(["baseline", "create", "a.c", "--tools", "clang-tidy"]) == 2   # no overwrite
    f.write_text("/* moved */\n\n" + SRC)
    capsys.readouterr()
    rc = cli.main(["check", "a.c", "--tools", "clang-tidy", "--format", "json",
                   "--baseline", BL.DEFAULT_FILE, "--fail-on", "note"])
    out = json.loads(capsys.readouterr().out)
    assert out == [] and rc == 0
    if recorded:                                   # clang-tidy present: the gate passes only thanks to the baseline
        assert cli.main(["check", "a.c", "--tools", "clang-tidy", "--format", "json",
                         "--fail-on", "note"]) == 1
