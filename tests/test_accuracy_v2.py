"""Message variants, Clang Static Analyzer taint/bounds checkers, the size-arithmetic
Semgrep rule and the dev / held-out split of the accuracy corpus."""
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

from cert_review import analyzers_extra as EX, checkers_map as CM, engine, profiles as P
from cert_review import toolrun as T

ROOT = Path(__file__).resolve().parents[1]
need_clang = pytest.mark.skipif(shutil.which("clang") is None, reason="clang not installed")
need_semgrep = pytest.mark.skipif(shutil.which("semgrep") is None, reason="semgrep not installed")


@pytest.mark.parametrize("checker,msg,variant", [
    ("bugprone-narrowing-conversions",
     "narrowing conversion from 'long' to signed type 'int' is implementation-defined", "int-to-int"),
    ("bugprone-narrowing-conversions", "narrowing conversion from 'double' to 'int'", "float-to-int"),
    ("bugprone-narrowing-conversions", "narrowing conversion from 'double' to 'float'", "float-to-float"),
    ("bugprone-narrowing-conversions", "narrowing conversion from 'long' to 'double'", "int-to-float"),
    ("bugprone-narrowing-conversions",
     "narrowing conversion from constant value 4294967295 (0xFFFFFFFF) of type 'unsigned int' to signed "
     "type 'int' is implementation-defined", "int-to-int"),
    ("alpha.security.taint.GenericTaint",
     "Untrusted data is used as a format string (CWE-134: Uncontrolled Format String)", "format-string"),
    ("alpha.security.taint.GenericTaint", "Untrusted data is passed to a system call", "system-call"),
    ("alpha.security.taint.GenericTaint", "Untrusted data is used to specify the buffer size", "buffer-size"),
    ("alpha.security.ArrayBoundV2", "Potential out of bound access to 'b' with tainted index", "tainted"),
    ("alpha.security.ArrayBoundV2", "Out of bound access to memory after the end of 'b'", "untainted"),
    ("alpha.unix.cstring.OutOfBounds", "String copy function overflows the destination buffer", "string"),
    ("alpha.unix.cstring.OutOfBounds", "Memory copy function accesses out-of-bound array element", "memory"),
])
def test_checker_variant(checker, msg, variant):
    assert T.checker_variant(checker, msg) == f"{checker}@{variant}"


def test_checker_without_variants_keeps_its_name():
    assert T.checker_variant("unix.Malloc", "Potential leak") == "unix.Malloc"


def test_variant_mappings():
    idx = CM.reverse_index()
    rules = lambda tool, chk: {e["rule_id"] for e in idx.get((tool, chk), [])}
    assert rules("clangsa", "alpha.security.taint.GenericTaint@format-string") == {"FIO30-C"}
    assert rules("clangsa", "alpha.security.ArrayBoundV2@tainted") == {"ARR30-C", "INT04-C"}
    assert rules("clangsa", "alpha.security.ArrayBoundV2@untainted") == set()
    assert "INT04-C" in rules("clangsa", "optin.taint.TaintedAlloc")
    assert rules("clangsa", "alpha.unix.cstring.OutOfBounds@string") == {"STR31-C"}
    # a lower confidence for integer narrowing ranks it below more specific findings
    assert [e["confidence"] for e in idx[("clang-tidy", "bugprone-narrowing-conversions@int-to-int")]] == [0.45]


def test_variant_checkers_are_available_by_base_name():
    m = json.loads((ROOT / "data/checker_map.json").read_text())["rules"]
    c = [x for x in m["FIO30-C"]["checkers"] if x["checker"].endswith("@format-string")]
    assert c and c[0]["available"]


def test_clang_tidy_enables_base_names_only():
    ct, sa = T._checks_for_clang_tidy(P.load("default"))
    assert "bugprone-narrowing-conversions" in ct
    assert not any("@" in c for c in ct + sa)


def test_csa_compile_args_from_compdb(tmp_path):
    src = tmp_path / "a.c"
    src.write_text("int x;\n")
    (tmp_path / "compile_commands.json").write_text(json.dumps([{
        "directory": str(tmp_path), "file": "a.c",
        "arguments": ["cc", "-DFOO=1", "-Iinc", "-std=gnu99", "-c", "a.c", "-o", "a.o", "-MD", "-MF", "a.d"],
    }]))
    flags, cwd = T.csa_compile_args(str(src), P.load("default"), tmp_path, tmp_path)
    assert cwd == str(tmp_path)
    assert flags[:3] == ["-DFOO=1", "-Iinc", "-std=gnu99"]
    for gone in ("cc", "-c", "a.c", "-o", "a.o", "-MD", "-MF", "a.d"):
        assert gone not in flags


def test_csa_compile_args_fallback(tmp_path):
    src = tmp_path / "b.c"
    src.write_text("int x;\n")
    flags, cwd = T.csa_compile_args(str(src), P.load("default"), None, tmp_path)
    assert cwd is None and flags == T.fallback_flags(str(src), "c", P.load("default"), tmp_path)


def test_taint_config_is_bundled():
    import yaml
    cfg = yaml.safe_load(T.taint_config().read_text())
    assert {"ntohs", "ntohl"} <= {p["Name"] for p in cfg["Propagations"]}


# clang 19 drops the taint of the buffer when fgets' result is tested, so the example
# leaves it unchecked.
TAINT_SRC = """#include <stdio.h>
#include <stdlib.h>
void f(void) {
  char buf[64];
  fgets(buf, sizeof buf, stdin);
  printf(buf);
}
void g(void) {
  char *cmd = getenv("CMD");
  if (cmd) system(cmd);
}
"""


@need_clang
def test_taint_checkers_report_cert_rules(tmp_path):
    p = tmp_path / "t.c"
    p.write_text(TAINT_SRC)
    res = engine.check([str(p)], tools=("clangsa",))
    got = {(f.rule_id, f.line) for f in res.findings}
    assert ("FIO30-C", 6) in got
    assert ("ENV33-C", 10) in got


SIZE_SRC = """#include <stdlib.h>
#include <string.h>
#include <assert.h>
void *f1(size_t n, size_t m) { return malloc(n * m); }
void f2(char *d, const char *s, size_t a, size_t b) { size_t t = a + b; memcpy(d, s, t); }
void f3(char *d, const char *s, size_t a) { memcpy(d, s, a + 1); }
void *f4(size_t n) { return malloc(n * sizeof(int)); }
void f5(char *d, const char *s, size_t a, size_t b) { if (a > 64 || b > 64) return; memcpy(d, s, a + b); }
void f6(char *d, const char *s, size_t a, size_t b) { assert(a + b < 64); memcpy(d, s, a + b); }
void f7(const char *s) { char *p = malloc(strlen(s) + 1); free(p); }
"""


@need_semgrep
def test_size_arithmetic_rule(tmp_path):
    p = tmp_path / "s.c"
    p.write_text(SIZE_SRC)
    raw, st = EX.run_semgrep([str(p)], P.load("default"), None)
    lines = sorted({r.line for r in raw if r.checker == "int30-c-unchecked-size-arithmetic"})
    assert lines == [4, 5]


def _eval_module():
    spec = importlib.util.spec_from_file_location("eval_accuracy", ROOT / "tools/eval_accuracy.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_split_is_fixed_and_balanced():
    ev = _eval_module()
    man = json.loads((ROOT / "corpus/manifest.json").read_text())
    rules = sorted({m["rule"] for m in man["files"]})
    halves = {r: ev.half(r) for r in rules}
    assert set(halves.values()) == {"dev", "held-out"}
    dev = sum(1 for h in halves.values() if h == "dev")
    assert 0.4 < dev / len(rules) < 0.6
    # pinned so that tuning cannot silently move rules between halves
    assert ev.SPLIT_SALT == "cert-review-split-v1"
    assert halves["ARR38-C"] == "dev" and halves["INT30-C"] == "held-out"
