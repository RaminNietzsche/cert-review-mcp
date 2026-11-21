"""The rule database must be complete: parsing must not drop sections."""
import json
import re
from pathlib import Path

import pytest

from cert_review import rules

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "rules.json").read_text())


def test_counts_match_official_index():
    # Counts taken from the standards' own index pages (see docs/rule-counts.md).
    assert DATA["counts"] == {"c_rule": 122, "c_recommendation": 183, "cpp_rule": 83}
    assert len(DATA["rules"]) == 388


def test_commit_pinned():
    assert re.fullmatch(r"[0-9a-f]{40}", DATA["source"]["commit"])
    assert DATA["source"]["commit"] in (ROOT / "NOTICE").read_text()


def test_every_rule_has_core_fields():
    for r in DATA["rules"]:
        assert re.fullmatch(r"[A-Z]{3}\d{2}-(C|CPP)", r["id"])
        assert r["title"] and (r["intro"] or r["examples"])
        assert r["url"].startswith("https://")
        assert r["lang"] in ("c", "cpp")
        assert r["kind"] in ("rule", "recommendation")
        assert r["id"].endswith("-C") == (r["lang"] == "c") or r["id"].endswith("-CPP")


def test_known_rule_with_all_sections():
    r = rules.get("EXP34-C")
    assert r["risk"] == {"severity": "High", "likelihood": "Likely", "detectable": False,
                         "repairable": True, "priority": "P18", "level": "L1"}
    assert "CWE-476" in r["cwe"]
    assert len(r["examples"]) >= 2
    assert all(e["noncompliant"] for e in r["examples"])
    assert any(d["tool"] == "Cppcheck" for d in r["automated_detection"])


def test_examples_have_code_for_most_rules():
    """If the example parser breaks, almost every rule loses its code."""
    with_code = [r for r in DATA["rules"]
                 if any(e["noncompliant"] and e["noncompliant"]["code"]
                        for e in r["examples"])]
    assert len(with_code) >= 360


def test_risk_present_for_nearly_all():
    missing = [r["id"] for r in DATA["rules"] if not r["risk"]]
    assert missing == ["ENV04-C"]   # upstream page has no risk section


def test_automated_detection_tables_parsed():
    n = sum(1 for r in DATA["rules"] if r["automated_detection"])
    assert n >= 365


def test_raw_html_removed():
    for r in DATA["rules"]:
        for d in r["automated_detection"]:
            assert "<a " not in d["tool"] and "<br" not in d["description"]


def test_cpp_has_no_recommendations():
    assert not rules.list_rules(lang="cpp", kind="recommendation")


def test_search_finds_null_deref():
    ids = [x["id"] for x in rules.search("dereference null pointers", lang="c")]
    assert "EXP34-C" in ids[:3]
