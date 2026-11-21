import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAN = json.loads((ROOT / "corpus/manifest.json").read_text())
ACC = json.loads((ROOT / "data/accuracy.json").read_text())


def test_manifest_files_exist_and_expectations_recorded():
    assert len(MAN["files"]) == ACC["corpus_files"] == 1548
    for m in MAN["files"]:
        p = ROOT / "corpus" / m["file"]
        assert p.exists()
        head = p.read_text().splitlines()[0]
        assert m["rule"] in head and ("noncompliant" in head) == m["violates"]


def test_corpus_covers_every_rule_with_an_example():
    from cert_review import rules as R
    with_code = {r["id"] for r in R.all_rules().values()
                 if any(e["noncompliant"] and e["noncompliant"]["code"] for e in r["examples"])}
    # CON03-C only has a Java snippet upstream, which cannot be analysed here
    assert with_code - {m["rule"] for m in MAN["files"]} == {"CON03-C"}


def test_recorded_accuracy_is_consistent():
    s = ACC["summary"]
    for g in ("deterministic", "partial", "all_scored"):
        v = s[g]
        assert v["tp"] + v["fn"] + v["fp"] + v["tn"] > 0
    assert s["deterministic"]["fp"] == 0          # rule-specific checkers: no FP on compliant examples
    tot = s["deterministic"]["tp"] + s["partial"]["tp"]
    assert tot == s["all_scored"]["tp"]
