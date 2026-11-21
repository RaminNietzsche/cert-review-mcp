import json
from pathlib import Path

import pytest

from cert_review import engine, findings as F, profiles as P, toolrun as T
from conftest import need_clang_tidy, need_cppcheck


def raw(tool, checker, file, line=1, msg="m"):
    return T.RawFinding(tool, checker, file, line, 1, msg)


def test_alias_maps_to_specific_rule_with_high_confidence(tmp_path):
    f = tmp_path / "a.c"
    f.write_text("int x;\n")
    kept, dropped = engine.normalize([raw("clang-tidy", "cert-err34-c", str(f))], P.load("default"))
    assert [(k.rule_id, k.confidence) for k in kept] == [("ERR34-C", 0.9)]


def test_cpp_file_prefers_cpp_rules(tmp_path):
    f = tmp_path / "a.cc"
    f.write_text("int x;\n")
    kept, _ = engine.normalize([raw("clang-tidy", "cert-oop54-cpp", str(f))], P.load("default"))
    assert kept and kept[0].rule_id == "OOP54-CPP"
    kept, _ = engine.normalize([raw("clang-tidy", "cert-err33-c", str(f))], P.load("default"))
    assert kept[0].rule_id == "ERR33-C" and kept[0].confidence < 0.9   # C rule on a C++ file


def test_clang_analyzer_names_map_through_clangsa(tmp_path):
    f = tmp_path / "a.c"
    f.write_text("int x;\n")
    kept, _ = engine.normalize([raw("clang-tidy", "clang-analyzer-unix.Malloc", str(f))], P.load("default"))
    assert {k.rule_id for k in kept} >= {"MEM30-C"}


def test_inline_ignore_and_profile_suppression(tmp_path):
    f = tmp_path / "a.cc"
    f.write_text("// cert-review: ignore ERR34-C documented\nint a = atoi(s);\nint b = atoi(s);\n")
    kept, dropped = engine.normalize([raw("clang-tidy", "cert-err34-c", str(f), 2),
                                      raw("clang-tidy", "cert-err34-c", str(f), 3)], P.load("default"))
    assert [k.line for k in kept] == [3] and dropped[0].suppressed == "inline cert-review: ignore"


def test_disabled_and_level_filtering(tmp_path):
    f = tmp_path / "a.cc"
    f.write_text("int x;\n")
    prof = P.load("ceph")
    kept, dropped = engine.normalize([raw("clang-tidy", "cert-dcl59-cpp", str(f))], prof)
    assert not kept and "disabled rule" in dropped[0].suppressed


def test_dedupe_merges_tools_and_raises_confidence():
    prof = P.load("default")
    a = F.make("MEM31-C", "/x/a.c", 4, 1, "cppcheck", "memleak", "leak", 0.65, prof)
    b = F.make("MEM31-C", "/x/a.c", 4, 9, "clangsa", "unix.Malloc", "leak", 0.5, prof)
    out = F.dedupe([a, b])
    assert len(out) == 1 and out[0].confidence > 0.65 and out[0].also_found_by


def test_cap_per_location_keeps_best():
    prof = P.load("default")
    fs = [F.make(r, "/x/a.c", 4, 1, "clangsa", "unix.Malloc", "m", c, prof)
          for r, c in (("MEM30-C", 0.4), ("MEM31-C", 0.6), ("MEM34-C", 0.5))]
    kept = engine.cap_per_location(fs, 2)
    assert sorted(f.rule_id for f in kept) == ["MEM31-C", "MEM34-C"]


def test_normalized_schema_fields(tmp_path):
    f = tmp_path / "a.c"
    f.write_text("int x;\n")
    kept, _ = engine.normalize([raw("clang-tidy", "cert-err34-c", str(f))], P.load("default"))
    d = kept[0].to_dict()
    for k in ("rule_id", "lang", "file", "line", "col", "severity", "priority", "level", "tool",
              "checker", "message", "confidence"):
        assert k in d
    assert d["severity"] == "warning" and d["level"] == "L2" and d["priority"] == 6


@need_clang_tidy
def test_clang_tidy_flags_noncompliant_but_not_compliant(tmp_path):
    bad = tmp_path / "bad.c"
    good = tmp_path / "good.c"
    bad.write_text("#include <stdlib.h>\nint f(const char *s) { return atoi(s); }\n")
    good.write_text("#include <stdlib.h>\n#include <errno.h>\nint f(const char *s) {\n"
                    "  errno = 0; char *e; long v = strtol(s, &e, 10);\n"
                    "  if (errno || e == s) return -1; return (int)v;\n}\n")
    res = engine.check([str(bad), str(good)], "default", tools=("clang-tidy",), root=tmp_path)
    flagged = {(Path(f.file).name, f.rule_id) for f in res.findings}
    assert ("bad.c", "ERR34-C") in flagged
    assert not any(n == "good.c" and r == "ERR34-C" for n, r in flagged)


@need_clang_tidy
def test_diff_mode_only_changed_lines(tmp_path):
    f = tmp_path / "a.c"
    f.write_text("#include <stdlib.h>\nint a(const char *s) { return atoi(s); }\n"
                 "int b(const char *s) { return atoi(s); }\n")
    res = engine.check([str(f)], "default", tools=("clang-tidy",), root=tmp_path,
                       changed_lines={str(f): {3}})
    assert [x.line for x in res.findings if x.rule_id == "ERR34-C"] == [3]


@need_cppcheck
def test_cppcheck_adapter(tmp_path):
    f = tmp_path / "a.c"
    f.write_text("#include <stdlib.h>\nvoid g(void) { char *p = malloc(4); free(p); free(p); }\n")
    res = engine.check([str(f)], "default", tools=("cppcheck",), root=tmp_path)
    assert any(x.rule_id in ("MEM30-C", "MEM36-C") and x.tool == "cppcheck" for x in res.findings)


def test_missing_tools_are_reported_not_fatal(tmp_path, monkeypatch):
    monkeypatch.setattr(T, "which", lambda t: None)
    f = tmp_path / "a.c"
    f.write_text("int x;\n")
    res = engine.check([str(f)], "default", root=tmp_path)
    assert res.findings == [] and all(not t.available for t in res.tools)


def test_cppcheck_conditional_messages_lose_confidence(tmp_path):
    f = tmp_path / "a.cc"
    f.write_text("int x;\n")
    plain, _ = engine.normalize([raw("cppcheck", "negativeIndex", str(f), 1, "Array 'a[4]' accessed at index -1")],
                                P.load("default"))
    cond, _ = engine.normalize([raw("cppcheck", "negativeIndex", str(f), 1,
                                    "Either the condition 'n<0' is redundant or the array is accessed at index -1")],
                               P.load("default"))
    assert cond[0].confidence < plain[0].confidence
