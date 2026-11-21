import json

from cert_review import formatters as Fm
from cert_review import findings as F
from cert_review import profiles as P


def sample(rule="EXP34-C", **kw):
    f = F.make(rule, "/repo/src/a.c", 12, 5, "clang-tidy", "cert-x", "null deref", 0.8, P.load("default"))
    d = f.to_dict()
    d.update(kw)
    return d


def test_sarif_structure():
    s = Fm.to_sarif([sample(), sample("ERR33-C")], root="/repo")
    assert s["version"] == "2.1.0" and s["$schema"].endswith("sarif-2.1.0.json")
    run = s["runs"][0]
    assert [r["id"] for r in run["tool"]["driver"]["rules"]] == ["ERR33-C", "EXP34-C"]
    res = run["results"][0]
    assert res["ruleId"] == "EXP34-C" and res["level"] == "error"
    loc = res["locations"][0]["physicalLocation"]
    assert loc["artifactLocation"]["uri"] == "src/a.c" and loc["region"]["startLine"] == 12
    assert run["tool"]["driver"]["rules"][1]["helpUri"].startswith("https://cmu-sei.github.io/")
    json.dumps(s)


def test_github_review_payload():
    p = Fm.to_github_review([sample()], root="/repo")
    assert p["event"] == "COMMENT"
    c = p["comments"][0]
    assert c["path"] == "src/a.c" and c["line"] == 12 and c["side"] == "RIGHT"
    assert "CERT EXP34-C" in c["body"] and "Rule: https://" in c["body"]
    assert "nothing is posted" in p["body"]


def test_gitlab_payload_has_placeholders():
    d = Fm.to_gitlab_discussions([sample()], root="/repo")[0]
    assert d["position"]["new_path"] == "src/a.c" and d["position"]["new_line"] == 12
    assert d["position"]["head_sha"].startswith("<")


def test_comment_contains_compliant_example_and_quote():
    body = Fm.comment_body(sample(quote="Dereferencing a null pointer is undefined behavior"))
    assert "Compliant approach" in body and "> Dereferencing a null pointer" in body


def test_markdown_and_styles():
    assert "No SEI CERT findings" in Fm.to_markdown([])
    assert "EXP34-C" in Fm.format_review([sample()], "markdown")
    import pytest
    with pytest.raises(ValueError):
        Fm.format_review([], "html")
