from cert_review import profiles as P
from cert_review import rules as R


def test_available_profiles():
    assert {"default", "ceph"} <= set(P.available())


def test_ceph_profile_rule_ids_exist():
    p = P.load("ceph")
    ids = set(p.raw["rule_overrides"]) | {d["id"] for d in p.raw["disabled_rules"]}
    for i in p.raw["idioms"]:
        ids |= set(i["rules"])
    for s in p.raw["suppress"]:
        if "id" in s:
            ids.add(s["id"])
    assert not [i for i in ids if not R.is_valid_id(i)]


def test_ceph_facts():
    p = P.load("ceph")
    assert p.raw["languages"]["cpp_standard"] == 23
    assert p.raw["languages"]["c_standard"] == 11


def test_every_suppression_has_a_reason():
    for s in P.load("ceph").raw["suppress"] + P.load("ceph").raw["disabled_rules"]:
        assert s["reason"].strip()


def test_pre31_suppressed_for_ceph_assert_only():
    p = P.load("ceph")
    assert p.suppression("PRE31-C", None, "src/osd/OSD.cc", "ceph_assert(f(x++) == 0);")
    assert not p.suppression("PRE31-C", None, "src/osd/OSD.cc", "MAX(a++, b);")


def test_crimson_concurrency_suppressed_but_common_not():
    p = P.load("ceph")
    assert p.suppression("CON51-CPP", None, "src/crimson/osd/pg.cc", "m.lock();")
    assert not p.suppression("CON51-CPP", None, "src/common/Throttle.cc", "m.lock();")


def test_tests_keep_only_memory_rules():
    p = P.load("ceph")
    assert p.suppression("ERR33-C", None, "src/test/foo.cc", "x")
    assert not p.suppression("MEM30-C", None, "src/test/foo.cc", "x")


def test_third_party_excluded():
    p = P.load("ceph")
    assert p.excluded_path("src/rocksdb/db/db_impl.cc")
    assert not p.excluded_path("src/osd/OSD.cc")


def test_idiom_detection():
    p = P.load("ceph")
    ids = [i["id"] for i in p.idioms_in("auto m = ceph::make_mutex(\"x\"); ceph_assert(r == 0);")]
    assert "ceph_mutex" in ids and "ceph_assert" in ids


def test_override_priority_and_severity():
    from cert_review import findings as F
    base = F.make("EXP61-CPP", "a.cc", 1, 1, "t", "c", "m", 0.5, P.load("default"))
    ceph = F.make("EXP61-CPP", "a.cc", 1, 1, "t", "c", "m", 0.5, P.load("ceph"))
    assert ceph.priority == base.priority + 5 and ceph.severity == "error"


def test_message_regex_suppression():
    p = P.load("ceph")
    sign = "narrowing conversion from 'unsigned long' to signed type 'int64_t' is implementation-defined"
    width = "narrowing conversion from 'unsigned long' to 'unsigned int'"
    assert p.suppression("INT31-C", "bugprone-narrowing-conversions", "src/common/a.cc", "x", sign)
    assert not p.suppression("INT31-C", "bugprone-narrowing-conversions", "src/common/a.cc", "x", width)


def test_code_not_regex_suppresses_unless_line_matches():
    p = P.load("ceph")
    assert p.suppression("DCL58-CPP", "cert-dcl58-cpp", "src/include/a.h", "struct foo : std::set<int> {", "m")
    assert not p.suppression("DCL58-CPP", "cert-dcl58-cpp", "src/include/a.h", "namespace std {", "m")


def test_static_string_literal_err58_suppressed():
    p = P.load("ceph")
    line = 'static const std::string CLOG_CHANNEL_NONE = "none";'
    assert p.suppression("ERR58-CPP", "cert-err58-cpp", "src/common/LogEntry.h", line, "m")
    assert not p.suppression("ERR58-CPP", "cert-err58-cpp", "src/common/x.cc", "static std::map<int,int> m = f();", "m")
