"""MISRA C:2012, MISRA C++:2023 and AUTOSAR C++14 support."""
import asyncio
import json
import re
from pathlib import Path

import pytest
import yaml

from cert_review import api, engine, formatters, profiles as P, rules as R, ruletexts
from cert_review import checkers_map as CM
from cert_review import validator as V
from cert_review.mcp_server import RULE_ID_PATTERN, build_server
from cert_review.paths import data_dir

from conftest import need_cppcheck

GL = json.loads((data_dir() / "guidelines.json").read_text())
OVERLAY = yaml.safe_load((data_dir() / "guideline_overlay.yaml").read_text())
# Invented placeholder sentences for tests only: they are not MISRA or AUTOSAR text.
FAKE_TEXTS = """Appendix A Summary of guidelines
Rule 10.4 Required
Placeholder headline number one used only by the
cert-review unit tests
Dir 4.1
Required
Placeholder directive text for the unit tests only
Appendix B
Rule 10.5 Advisory
Must not be read because it follows Appendix B
"""


@pytest.fixture(autouse=True)
def _no_texts(monkeypatch):
    for v in ruletexts.ENV.values():
        monkeypatch.delenv(v, raising=False)
    ruletexts.set_profile_paths(None)
    yield
    ruletexts.set_profile_paths(None)


# ---------------------------------------------------------------- data
def test_counts_and_classifications():
    counts = {s: sum(1 for g in GL["guidelines"] if g["standard"] == s) for s in GL["standards"]}
    assert counts == {"misra-c-2012": 221, "misra-cpp-2023": 178, "autosar-cpp14": 397}
    for g in GL["guidelines"]:
        assert g["classification"] in {"mandatory", "required", "advisory", "document"}
        assert g["kind"] in {"rule", "directive"}
        assert g["id"].startswith(R.PREFIX[g["standard"]])
    ids = [g["id"] for g in GL["guidelines"]]
    assert len(ids) == len(set(ids))
    assert not set(ids) & set(R.cert_rules())
    assert sum(1 for g in GL["guidelines"] if g["kind"] == "directive") == 21 + 4


def test_no_guideline_text_is_shipped():
    """Legal guard: only facts and our short summaries; no headline/rationale fields."""
    assert GL["text_shipped"] is False
    allowed = {"id", "standard", "local_id", "lang", "kind", "classification", "category",
               "category_name", "summary", "decidability", "enforcement", "cert", "checkers",
               "target"}
    for g in GL["guidelines"]:
        assert set(g) <= allowed, set(g) - allowed
        if g["summary"]:
            assert len(g["summary"]) <= 110, g["id"]
    notice = (data_dir().parent / "NOTICE").read_text()
    assert "MISRA" in notice and "AUTOSAR" in notice


def test_overlay_ids_exist():
    for std, m in OVERLAY["summaries"].items():
        for local in m:
            assert R.PREFIX[std] + local in R.guidelines(), (std, local)
    for std, m in OVERLAY["checkers"].items():
        for local in m:
            assert R.PREFIX[std] + local in R.guidelines(), (std, local)


def test_cert_cross_references():
    g = R.get("MISRA-C-2012-21.3")
    assert any(c["id"] == "MEM31-C" or c["id"].startswith("API0") for c in g["cert"])
    a = R.get("AUTOSAR-A5-2-2")
    assert {"EXP39-C", "EXP57-CPP"} <= {c["id"] for c in a["cert"]}
    for x in GL["guidelines"]:
        for c in x["cert"]:
            assert c["id"] in R.cert_rules()
    refs = api.explain_rule("EXP34-C")["cross_references"]
    assert any(r["id"] == "AUTOSAR-A5-3-2" for r in refs)


# ---------------------------------------------------------------- IDs and lookup
@pytest.mark.parametrize("raw,std,want", [
    ("misra-c2012-10.4", None, "MISRA-C-2012-10.4"),
    ("MISRA C:2012 Rule 10.4", None, "MISRA-C-2012-10.4"),
    ("Dir 4.1", None, "MISRA-C-2012-DIR-4.1"),
    ("MISRA C:2012 Directive 4.12", None, "MISRA-C-2012-DIR-4.12"),
    ("Rule 8.2.2", None, "MISRA-CPP-2023-8.2.2"),
    ("MISRA C++:2023 Rule 8.2.2", None, "MISRA-CPP-2023-8.2.2"),
    ("Dir 15.8.1", None, "MISRA-CPP-2023-DIR-15.8.1"),
    ("a5-2-2", None, "AUTOSAR-A5-2-2"),
    ("AUTOSAR C++14 M6-4-1", None, "AUTOSAR-M6-4-1"),
    ("4.1", "misra-c-2012", "MISRA-C-2012-4.1"),
    ("exp34-c", None, "EXP34-C"),
    ("Rule 99.99", None, None),
])
def test_resolve_id(raw, std, want):
    assert R.resolve_id(raw, std) == want


def test_rule_id_schema_pattern():
    rx = re.compile(RULE_ID_PATTERN)
    for ok in ("EXP34-C", "mem50-cpp", "MISRA-C-2012-10.4", "misra-c-2012-dir-4.1",
               "MISRA-CPP-2023-8.2.2", "MISRA-CPP-2023-DIR-0.3.1", "AUTOSAR-A5-2-2", "autosar-m6-4-1"):
        assert rx.match(ok), ok
    assert not rx.match("MISRA-C-2012-8.2.2")


def test_list_rules_default_is_cert():
    assert api.list_rules(limit=1000)["count"] == 388
    assert api.list_rules(standard="misra-c-2012", limit=1000)["count"] == 221
    assert api.list_rules(standard="misra", limit=1000)["count"] == 221 + 178
    m = api.list_rules(standard="misra-c-2012", classification="mandatory", limit=1000)
    assert m["count"] == 23 and all(r["classification"] == "mandatory" for r in m["rules"])
    d = api.list_rules(standard="misra-c-2012", kind="directive", limit=1000)
    assert d["count"] == 21
    assert api.list_rules(standard="all", limit=2000)["count"] == 388 + 221 + 178 + 397


def test_search_by_standard():
    assert all(r["standard"].startswith("cert") for r in api.search_rules("goto")["results"])
    res = api.search_rules("goto", standard="misra-c-2012")["results"]
    assert res and res[0]["id"] in {"MISRA-C-2012-15.1", "MISRA-C-2012-15.2", "MISRA-C-2012-15.3"}
    assert api.search_rules("A5-2-2", standard="autosar")["results"][0]["id"] == "AUTOSAR-A5-2-2"


def test_explain_guideline():
    d = api.explain_rule("misra-c2012-10.4")
    assert d["id"] == "MISRA-C-2012-10.4" and d["standard"] == "misra-c-2012"
    assert d["classification"] == "required" and d["text_source"] == "summary-only"
    assert d["quote_required"] is False and d["examples"] == [] and d["risk"] is None
    assert "not bundled" in d["text"] and "paraphrase" in d["text"]
    assert any(c["checker"] == "misra-c2012-10.4" and c["specific"] for c in d["coverage"]["checkers"])
    a = api.explain_rule("AUTOSAR-A0-1-1")
    assert a["enforcement"] == "automated" and "Language-independent" in a["text"]


def test_coverage_by_standard():
    c = api.rule_coverage()
    assert c["total"] == 388 and c["all_mappings"]["deterministic"] == 186   # incl. CodeQL CERT queries
    m = api.rule_coverage(standard="misra-c-2012")
    assert m["total"] == 221 and sum(m["all_mappings"].values()) == 221
    assert m["all_mappings"]["deterministic"] >= 131          # cppcheck MISRA addon rules
    assert "misra-c-2012" in m["by_standard"]
    a = api.rule_coverage(standard="autosar", include_ids=True)
    assert "AUTOSAR-A5-2-2" in a["rules_all_mappings"]["deterministic"]


# ---------------------------------------------------------------- mapping and engine
def test_mapping_respects_language_and_standards():
    cert_only = engine._rules_for("cppcheck", "uninitvar", "c")
    assert cert_only and all(R.is_cert(r) for r, _, _ in cert_only)
    both = engine._rules_for("cppcheck", "uninitvar", "c", R.expand_standards(["cert", "misra"]))
    assert "MISRA-C-2012-9.1" in {r for r, _, _ in both}
    assert engine._rules_for("cppcheck", "misra-c2012-10.4", "cpp", ("misra-c-2012",)) == []
    hit = engine._rules_for("cppcheck", "misra-c2012-10.4", "c", ("misra-c-2012",))
    assert hit == [("MISRA-C-2012-10.4", True, 0.9)]
    a = engine._rules_for("clang-tidy", "google-readability-casting", "cpp", ("autosar-cpp14",))
    assert ("AUTOSAR-A5-2-2", True, 0.9) in a
    # line_regex: the braces check maps to M6-4-1 on if lines and M6-3-1 on loop lines
    ifl = engine._rules_for("clang-tidy", "readability-braces-around-statements", "cpp",
                            ("autosar-cpp14",), "  if (x) return;")
    assert {r for r, _, _ in ifl} == {"AUTOSAR-M6-4-1"}


def test_checker_sets_unchanged_for_cert():
    assert CM.checkers_for_tool("clang-tidy") == CM.checkers_for_tool("clang-tidy", standards=["cert"])
    assert "google-readability-casting" not in CM.checkers_for_tool("clang-tidy")
    assert "misra-c2012-10.4" in CM.checkers_for_tool("cppcheck", standards=["misra-c-2012"])


def test_profiles_select_standards():
    assert P.load("default").standards == R.CERT_STANDARDS
    assert P.load("ceph").standards == R.CERT_STANDARDS
    assert P.load("misra").standards == ("misra-c-2012", "misra-cpp-2023")
    assert P.load("autosar").standards == ("autosar-cpp14",)
    with pytest.raises(ValueError):
        R.expand_standards(["nope"])


def test_profile_disable_accepts_aliases():
    p = P.Profile("t", {"disabled_rules": [{"id": "misra-c2012-15.5", "reason": "x"}],
                        "rule_overrides": {"A5-2-2": {"severity": "error"}}})
    assert p.disabled("MISRA-C-2012-15.5") == "x"
    assert p.override("AUTOSAR-A5-2-2") == {"severity": "error"}


def test_inline_ignore_misra(tmp_path):
    f = tmp_path / "x.c"
    f.write_text("int a; // cert-review: ignore misra-c2012-8.4, EXP34-C\n")
    src = engine._Source()
    assert engine._inline_ignored(src, str(f), 1, "MISRA-C-2012-8.4")
    assert engine._inline_ignored(src, str(f), 1, "EXP34-C")
    assert not engine._inline_ignored(src, str(f), 1, "MISRA-C-2012-10.4")


SAMPLE_C = """#include <stdlib.h>
int f(int x) {
  unsigned char c = 300;
  int y = 0;
  if (x) y = x + c;
  return y;
}
"""


@need_cppcheck
def test_check_files_misra_addon(tmp_path):
    f = tmp_path / "s.c"
    f.write_text(SAMPLE_C)
    ro = tmp_path
    ro.chmod(0o555)                   # the addon must not write next to the sources
    try:
        res = api.check_file(str(f), standards=["misra-c-2012"], tools=["cppcheck"])
    finally:
        ro.chmod(0o755)
    ids = {x["rule_id"] for x in res["findings"]}
    assert {"MISRA-C-2012-10.3", "MISRA-C-2012-10.4"} <= ids, ids
    assert res["standards"] == ["misra-c-2012"]
    hit = next(x for x in res["findings"] if x["rule_id"] == "MISRA-C-2012-10.4")
    assert hit["standard"] == "misra-c-2012" and hit["severity"] == "warning"
    assert "use --rule-texts" not in hit["message"]
    cert = api.check_file(str(f), tools=["cppcheck"])
    assert all(x["rule_id"][:6] != "MISRA-" for x in cert["findings"])


@need_cppcheck
def test_misra_addon_uses_licensed_texts(tmp_path, monkeypatch):
    texts = tmp_path / "texts.txt"
    texts.write_text("Appendix A Summary of guidelines\nRule 14.4 Required\n"
                     "Placeholder headline for the unit tests only\n"
                     "Rule 10.4 Required\nPlaceholder headline for the unit tests only\n")
    monkeypatch.setenv("CERT_REVIEW_MISRA_C_TEXTS", str(texts))
    f = tmp_path / "s.c"
    f.write_text(SAMPLE_C)
    res = api.check_file(str(f), standards=["misra-c-2012"], tools=["cppcheck"])
    hit = next(x for x in res["findings"] if x["rule_id"] == "MISRA-C-2012-10.4")
    assert "Placeholder headline" in hit["message"]


# ---------------------------------------------------------------- licensed texts and validation
def test_ruletexts_parse_formats():
    t = ruletexts.parse(FAKE_TEXTS, "misra-c-2012")
    assert t["MISRA-C-2012-10.4"].startswith("Placeholder headline number one used only by the cert")
    assert t["MISRA-C-2012-DIR-4.1"] == "Placeholder directive text for the unit tests only"
    assert "MISRA-C-2012-10.5" not in t
    t2 = ruletexts.parse("A5-2-2\tPlaceholder text\n# comment\nAUTOSAR-M6-4-1: Other placeholder\n",
                         "autosar-cpp14")
    assert t2 == {"AUTOSAR-A5-2-2": "Placeholder text", "AUTOSAR-M6-4-1": "Other placeholder"}
    assert ruletexts.parse("Rule 8.2.2 Required\nPlaceholder\n", "misra-cpp-2023") == {
        "MISRA-CPP-2023-8.2.2": "Placeholder"}


def test_validate_without_texts_accepts_id_only():
    f = {"rule_id": "MISRA-C-2012-15.5", "file": "/a/x.c", "line": 3, "message": "two returns"}
    out = V.validate([f])
    assert out["summary"] == {"accepted": 1, "rejected": 0}
    assert out["accepted"][0]["grounding"] == "rule-id-only"
    assert out["accepted"][0]["standard"] == "misra-c-2012"
    # CERT still requires a quote
    assert V.validate([{**f, "rule_id": "EXP34-C"}])["summary"]["rejected"] == 1
    # language checks
    assert V.validate([{**f, "file": "/a/x.cpp"}])["summary"]["rejected"] == 1
    bad = V.validate([{**f, "rule_id": "AUTOSAR-A5-2-2"}])
    assert "C++ rule" in bad["rejected"][0]["reasons"][0]


def test_validate_with_texts_requires_quote(tmp_path, monkeypatch):
    p = tmp_path / "t.txt"
    p.write_text(FAKE_TEXTS)
    monkeypatch.setenv("CERT_REVIEW_MISRA_C_TEXTS", str(p))
    f = {"rule_id": "misra-c2012-10.4", "file": "/a/x.c", "line": 3, "message": "mixed types"}
    assert V.validate([f])["rejected"][0]["reasons"] == ["missing quote"]
    good = V.validate([{**f, "quote": "placeholder headline number one used"}])
    assert good["summary"]["accepted"] == 1 and good["accepted"][0]["grounding"] == "quote"
    assert V.validate([{**f, "quote": "something the rule never says at all"}])["summary"]["rejected"] == 1
    d = api.explain_rule("MISRA-C-2012-10.4")
    assert d["text_source"] == "licensed-file" and d["quote_required"] is True
    assert "Placeholder headline" in d["title"]


def test_validate_packet_bounds_for_guidelines():
    pk = {"hunks": [{"file": "/a/x.c", "start_line": 1, "end_line": 10,
                     "candidate_rules": [{"rule_id": "EXP34-C"}]}]}
    f = {"rule_id": "MISRA-C-2012-15.5", "file": "/a/x.c", "line": 3, "message": "m"}
    assert V.validate([f], pk)["summary"]["accepted"] == 1
    assert V.validate([{**f, "line": 30}], pk)["summary"]["rejected"] == 1


def test_formatters_with_guideline_finding():
    f = V.validate([{"rule_id": "AUTOSAR-A5-2-2", "file": "/a/x.cpp", "line": 3,
                     "message": "C-style cast"}])["accepted"][0]
    md = formatters.format_review([f], "markdown")
    assert "AUTOSAR C++14 review" in md
    body = formatters.comment_body(f)
    assert body.startswith("**AUTOSAR C++14 A5-2-2**")
    sarif = formatters.format_review([f], "sarif")
    rule = sarif["runs"][0]["tool"]["driver"]["rules"][0]
    assert rule["id"] == "AUTOSAR-A5-2-2" and "external/autosar-cpp14/" in rule["properties"]["tags"][1]
    sast = formatters.format_review([f], "gitlab-sast")
    assert sast["vulnerabilities"][0]["identifiers"][0]["type"] == "autosar-cpp14"


# ---------------------------------------------------------------- MCP
def _call(name, args):
    s = build_server()

    async def go():
        r = await s.call_tool(name, args)
        if isinstance(r, tuple):
            r = r[0]
        content = r.content if hasattr(r, "content") else r
        return json.loads(content[0].text)
    return asyncio.run(go())


def test_mcp_standard_parameters():
    a = _call("list_rules", {"standard": "autosar", "classification": "advisory", "limit": 400})
    assert a["count"] == 35 and all(r["standard"] == "autosar-cpp14" for r in a["rules"])
    g = _call("get_rule", {"rule_id": "MISRA-CPP-2023-8.2.2", "include_examples": False})
    assert g["standard"] == "misra-cpp-2023" and g["quote_required"] is False
    c = _call("get_rule_coverage", {"standard": "misra-c-2012"})
    assert c["total"] == 221
    s = _call("search_rules", {"query": "nullptr", "standard": "misra-cpp-2023"})
    assert s["results"][0]["id"] == "MISRA-CPP-2023-7.11.1"
    v = _call("validate_findings", {"findings": [
        {"rule_id": "MISRA-C-2012-17.7", "file": "/x/a.c", "line": 2, "message": "ignored result"}]})
    assert v["summary"]["accepted"] == 1
