from cert_review import validator as V

Q = "Detect and handle memory allocation errors"


def f(**kw):
    d = {"rule_id": "MEM52-CPP", "file": "a.cc", "line": 6, "message": "unchecked", "quote": Q}
    d.update(kw)
    return d


def test_accepts_grounded_finding():
    r = V.validate([f()])
    assert r["summary"] == {"accepted": 1, "rejected": 0}
    assert r["accepted"][0]["tool"] == "llm-review" and r["accepted"][0]["quote"] == Q


def test_rejects_unknown_rule():
    r = V.validate([f(rule_id="FOO99-C")])
    assert "unknown rule_id FOO99-C" in r["rejected"][0]["reasons"]


def test_rejects_missing_or_invented_quote():
    assert V.validate([f(quote="")])["rejected"]
    r = V.validate([f(quote="this sentence does not appear in the rule at all")])
    assert any("quote not found" in x for x in r["rejected"][0]["reasons"])


def test_rejects_short_quote():
    r = V.validate([f(quote="memory")])
    assert any("shorter than" in x for x in r["rejected"][0]["reasons"])


def test_quote_whitespace_and_markdown_insensitive():
    assert V.quote_supported("MEM52-CPP", "  detect   AND handle\nmemory allocation errors ")


def test_quote_from_other_rule_rejected():
    r = V.validate([f(quote="Dereferencing a null pointer is undefined behavior")])
    assert r["rejected"]


def test_cpp_rule_on_c_file_rejected():
    r = V.validate([f(file="a.c")])
    assert any("C++ rule" in x for x in r["rejected"][0]["reasons"])


def test_missing_fields():
    assert V.validate([{"rule_id": "MEM52-CPP", "quote": Q}])["rejected"]


def test_disabled_rule_rejected_in_ceph_profile():
    q = "Do not return from a function declared [[noreturn]]"
    r = V.validate([f(rule_id="MSC53-CPP", quote=q)], profile="ceph")
    assert any("disabled by profile" in x for x in r["rejected"][0]["reasons"])


def test_packet_scope_enforced():
    packet = {"hunks": [{"file": "a.cc", "start_line": 1, "end_line": 10,
                         "candidate_rules": [{"rule_id": "MEM52-CPP"}]}]}
    assert V.validate([f()], packet)["summary"]["accepted"] == 1
    assert V.validate([f(line=99)], packet)["rejected"]
    other = f(rule_id="EXP34-C", quote="Dereferencing a null pointer is undefined behavior")
    r = V.validate([other], packet)
    assert any("not a candidate" in x for x in r["rejected"][0]["reasons"])
