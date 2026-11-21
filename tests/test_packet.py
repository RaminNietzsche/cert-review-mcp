from cert_review import packet as PK
from cert_review import api

CODE = """#include <stdlib.h>
#include <string.h>
void f(const char *s, size_t n) {
  char *p = malloc(n * 4);
  strcpy(p, s);
  memcpy(p, s, n);
  free(p);
  free(p);
}
"""


def hunks(tmp_path, name="a.c", code=CODE):
    p = tmp_path / name
    p.write_text(code)
    return PK.build_hunks({str(p): [(1, len(code.splitlines()))]}), str(p)


def test_heuristics_select_memory_rules(tmp_path):
    h, _ = hunks(tmp_path)
    m = PK.match_rules(h[0]["raw"], "c")
    assert "MEM30-C" in m and "ARR38-C" in m and "STR31-C" in m


def test_packet_skips_rules_with_a_specific_checker(tmp_path):
    code = "#include <stdlib.h>\nint f(const char*s){return atoi(s);}\n"
    h, _ = hunks(tmp_path, code=code)
    pk = PK.build(h, "default")
    ids = [c["rule_id"] for x in pk["hunks"] for c in x["candidate_rules"]]
    assert "ERR34-C" not in ids          # deterministic: cert-err34-c covers it
    pk2 = PK.build(h, "default", only_uncovered=False)
    assert "ERR34-C" in [c["rule_id"] for x in pk2["hunks"] for c in x["candidate_rules"]]


def test_packet_contains_rule_text_and_instructions(tmp_path):
    h, _ = hunks(tmp_path)
    pk = PK.build(h, "default")
    c = pk["hunks"][0]["candidate_rules"][0]
    assert c["text"] and c["url"].startswith("https://") and "quote" in pk["instructions"]
    assert "quote" in pk["finding_schema"] and pk["rule_database"]


def test_ceph_profile_adds_idioms_and_notes(tmp_path):
    code = "void g(){ auto m = ceph::make_mutex(\"x\"); m.lock(); ceph_assert(x); m.unlock(); }\n"
    h, _ = hunks(tmp_path, "a.cc", code)
    pk = PK.build(h, "ceph")
    assert {"ceph_mutex", "ceph_assert"} <= {i["id"] for i in pk["hunks"][0]["idioms"]}
    notes = [c["profile_note"] for c in pk["hunks"][0]["candidate_rules"] if c["profile_note"]]
    assert notes


def test_api_review_packet_for_file_and_validation_roundtrip(tmp_path):
    _, path = hunks(tmp_path)
    pk = api.review_packet(path, profile="default", run_static=False)
    assert pk["hunks"]
    rule = pk["hunks"][0]["candidate_rules"][0]
    quote = rule["text"].splitlines()[2][:60]
    res = api.validate_findings([{"rule_id": rule["rule_id"], "file": path, "line": 4,
                                  "message": "m", "quote": quote}], pk, "default")
    assert res["summary"]["accepted"] == 1, res
