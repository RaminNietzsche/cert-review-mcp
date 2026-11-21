"""explain_finding: rule summary, closest example pair, fix suggestion."""
import json

from cert_review import cli
from cert_review import explain as EX


def test_picks_matching_example_and_api_fix(tmp_path):
    f = tmp_path / "a.c"
    f.write_text("#include <stdlib.h>\nint p(const char *buff) {\n  int si = atoi(buff);\n  return si;\n}\n")
    d = EX.explain({"rule_id": "err34-c", "file": str(f), "line": 3, "tool": "clang-tidy",
                    "checker": "cert-err34-c", "message": "'atoi' used to convert a string"})
    assert d["rule"]["id"] == "ERR34-C" and d["rule"]["summary"]
    assert "atoi" in d["example"]["noncompliant"]["heading"]
    assert "strtol" in d["example"]["compliant"]["code"]
    assert "strtol" in d["fix"]["summary"]
    assert "+" in d["fix"]["example_diff"] and "strtol" in d["fix"]["example_diff"]
    assert any("rule-specific" in w for w in d["why"])
    assert ">    3|" in d["finding"]["snippet"]


def test_code_snippet_steers_example_choice():
    by_free = EX.explain({"rule_id": "MEM30-C", "code": "free(p); return p->next;"})
    assert by_free["example"] is not None and by_free["fix"]["steps"]
    assert by_free["example"]["similarity"] >= 0


def test_deterministic():
    f = {"rule_id": "STR31-C", "code": "strcpy(buf, argv[1]);"}
    assert EX.explain(f) == EX.explain(dict(f))
    assert "strcpy" in EX.explain(f)["fix"]["summary"]


def test_category_advice_without_api():
    d = EX.explain({"rule_id": "INT32-C", "code": "int r = a + b;"})
    assert d["fix"]["category_advice"] and d["fix"]["steps"]


def test_unknown_rule():
    assert "error" in EX.explain({"rule_id": "XYZ99-C"})


def test_cli_explain_finding(tmp_path, capsys):
    p = tmp_path / "f.json"
    p.write_text(json.dumps([{"rule_id": "ERR34-C", "code": "x = atoi(s);"}]))
    assert cli.main(["explain-finding", "--finding", str(p)]) == 0
    out = capsys.readouterr().out
    assert "Suggested fix:" in out and "strtol" in out
    assert cli.main(["explain-finding", "ERR34-C", "--code", "x = atoi(s);", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["rule"]["id"] == "ERR34-C"
    assert cli.main(["explain-finding"]) == 2
