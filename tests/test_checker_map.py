import json
from pathlib import Path

from cert_review import checkers_map as CM
from cert_review import rules as R

DATA = json.loads((Path(__file__).resolve().parents[1] / "data/checker_map.json").read_text())


def test_every_rule_has_an_entry():
    assert set(DATA["rules"]) == set(R.all_rules())


def test_tiers_are_valid_and_consistent():
    for rid, e in DATA["rules"].items():
        assert e["tier"] in ("deterministic", "partial", "llm-only")
        assert e["tier_runnable"] in ("deterministic", "partial", "llm-only")
        assert (e["tier"] == "llm-only") == (not e["checkers"])
        if e["tier"] == "deterministic":
            assert any(c["specific"] for c in e["checkers"])


def test_cert_aliases_are_deterministic():
    for rid in ("ERR33-C", "ERR34-C", "MSC30-C", "DCL58-CPP", "OOP54-CPP", "ERR58-CPP"):
        assert CM.tier(rid, runnable=False) == "deterministic", rid
    assert CM.tier("ERR34-C", runnable=True) == "deterministic"


def test_summary_matches_rules():
    for lang, kind in (("c", "rule"), ("c", "recommendation"), ("cpp", "rule")):
        cov = CM.coverage(lang, kind)
        s = DATA["summary"][f"{lang}_{kind}_tier"]
        assert cov["all_mappings"] == {k: s[k] for k in ("deterministic", "partial", "llm-only")}
        assert cov["total"] == s["total"]


def test_sources_recorded():
    src = DATA["sources"]
    assert len(src["codechecker"]["commit"]) == 40 and len(src["llvm"]["commit"]) == 40
    assert src["toolchain_versions"]["clang-tidy"]


def test_overlay_entries_applied():
    e = CM.rule_entry("MEM30-C")
    assert any(c["checker"] == "doubleFree" and "curated-overlay" in c["origins"] for c in e["checkers"])


def test_reverse_index_lookup():
    rules = CM.reverse_index()[("clang-tidy", "cert-err34-c")]
    assert {"rule_id": "ERR34-C", "specific": True} in rules
