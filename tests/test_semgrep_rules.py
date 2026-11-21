"""The bundled Semgrep rules (data/semgrep): metadata, checker-map wiring, and
results on the CERT noncompliant/compliant examples in corpus/."""
import glob
import shutil
from pathlib import Path

import pytest
import yaml

from cert_review import analyzers_extra as EX, checkers_map as CM, engine, profiles as P, rules as R

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
need_semgrep = pytest.mark.skipif(shutil.which("semgrep") is None, reason="semgrep not installed")


def all_rules():
    out = []
    for f in sorted(glob.glob(str(EX.semgrep_rules_dir() / "*.yml"))):
        out += yaml.safe_load(Path(f).read_text())["rules"]
    return out


def cert_ids(rule):
    c = rule["metadata"]["cert"]
    return c if isinstance(c, list) else [c]


def test_rules_have_cert_metadata():
    rules = all_rules()
    assert len(rules) >= 40
    assert len({r["id"] for r in rules}) == len(rules)
    for r in rules:
        assert r["metadata"]["confidence"] in ("high", "medium", "low"), r["id"]
        for rid in cert_ids(r):
            assert R.get(rid), (r["id"], rid)
        if not any(rid.endswith("-CPP") for rid in cert_ids(r)):
            assert "c" in r["languages"], f"{r['id']} would skip .c files"


def test_every_rule_is_in_the_checker_map():
    idx = CM.reverse_index()
    for r in all_rules():
        ents = idx.get(("semgrep", r["id"]))
        assert ents, r["id"]
        assert {e["rule_id"] for e in ents} == set(cert_ids(r))
        assert all(not e["specific"] and 0 < e["confidence"] < 1 for e in ents)


def test_custom_checks_cover_int_exp_mem_con():
    cats = {rid[:3] for r in all_rules() for rid in cert_ids(r)}
    assert {"INT", "EXP", "MEM", "CON"} <= cats


# Noncompliant CERT examples each rule is expected to detect (measured; the
# rules were written against these examples, so this guards against regressions,
# it is not an out-of-sample accuracy figure).
DETECTED = {
    "CON34-C": ["nc1_1.c"], "CON36-C": ["nc1_1.c"], "CON40-C": ["nc1_1.c", "nc2_1.c", "nc3_1.c"],
    "CON41-C": ["nc1_1.c"], "ENV30-C": ["nc2_1.c"], "EXP34-C": ["nc1_1.c", "nc2_1.c", "nc3_1.c"],
    "EXP44-C": ["nc1_1.c", "nc2_1.c", "nc4_1.c"], "EXP45-C": ["nc2_1.c", "nc3_1.c", "nc4_1.c"],
    "EXP46-C": ["nc1_1.c"], "EXP52-CPP": ["nc1_1.cc", "nc2_1.cc"], "FIO30-C": ["nc1_1.c", "nc2_1.c"],
    "FIO34-C": ["nc2_1.c", "nc3_1.c"], "FIO37-C": ["nc1_1.c"], "INT30-C": ["nc3_1.c"],
    "INT33-C": ["nc1_1.c", "nc2_1.c"], "INT34-C": ["nc1_1.c", "nc2_1.c", "nc3_1.c"],
    "INT36-C": ["nc1_1.c", "nc2_1.c", "nc3_1.c"], "MEM30-C": ["nc1_1.c", "nc2_1.c"],
    "MEM34-C": ["nc1_1.c", "nc2_1.c"], "MEM35-C": ["nc1_1.c", "nc2_1.c"], "MEM50-CPP": ["nc1_1.cc"],
    "MEM51-CPP": ["nc1_1.cc", "nc3_1.cc", "nc4_1.cc", "nc5_1.cc", "nc7_1.cc", "nc8_1.cc"],
    "POS34-C": ["nc1_1.c"], "POS50-C": ["nc1_1.c"], "STR30-C": ["nc1_1.c", "nc2_1.c", "nc3_1.c"],
}


def run(files):
    raw, st = EX.run_semgrep([str(f) for f in files], P.load("default"), None)
    assert st.status in ("ok", "partial"), st.notes
    kept, _ = engine.normalize(raw, P.load("default"))
    hits = {}
    for f in kept:
        hits.setdefault(str(Path(f.file).resolve()), set()).add(f.rule_id)
    return hits


@pytest.fixture(scope="module")
def corpus_hits():
    targets = sorted({rid for r in all_rules() for rid in cert_ids(r)})
    files = [p for rid in targets if (CORPUS / rid).is_dir() for p in sorted((CORPUS / rid).iterdir())
             if p.suffix in (".c", ".cc", ".cpp")]
    return files, run(files)


@need_semgrep
def test_detects_cert_noncompliant_examples(corpus_hits):
    _, hits = corpus_hits
    for rid, names in DETECTED.items():
        for n in names:
            p = str((CORPUS / rid / n).resolve())
            assert rid in hits.get(p, set()), f"{rid}/{n} not detected"


@need_semgrep
def test_no_own_rule_hit_on_compliant_examples(corpus_hits):
    files, hits = corpus_hits
    fps = [f"{p.parent.name}/{p.name}" for p in files
           if p.name.startswith("ok") and p.parent.name in hits.get(str(p.resolve()), set())]
    assert fps == []


@need_semgrep
@pytest.mark.parametrize("rid", ["CON50-CPP", "CON54-CPP"])
def test_cpp_examples_stored_as_c(tmp_path, rid):
    # These two CERT examples are C++ but sit in .c files in the corpus; check them as .cpp.
    files = []
    for p in sorted((CORPUS / rid).iterdir()):
        dst = tmp_path / f"{p.stem}.cpp"
        dst.write_text(p.read_text())
        files.append(dst)
    hits = run(files)
    got = {Path(p).stem for p, rs in hits.items() if rid in rs}
    assert got == {"nc1_1"}


CON_LOCAL = {
    "CON31-C": ("""#include <threads.h>
mtx_t m;
void f(void) { mtx_lock(&m); mtx_destroy(&m); }
""", """#include <threads.h>
mtx_t m;
void f(void) { mtx_lock(&m); mtx_unlock(&m); mtx_destroy(&m); }
"""),
    "CON39-C": ("""#include <threads.h>
int g(void *a) { return 0; }
void f(void) { thrd_t t; thrd_create(&t, g, 0); thrd_join(t, 0); thrd_detach(t); }
""", """#include <threads.h>
int g(void *a) { return 0; }
void f(void) { thrd_t t; thrd_create(&t, g, 0); thrd_join(t, 0); }
"""),
}


@need_semgrep
@pytest.mark.parametrize("rid", sorted(CON_LOCAL))
def test_con_rules_single_function_form(tmp_path, rid):
    # The CERT examples for these rules spread the defect over two threads, which a
    # pattern rule does not follow; the rules catch the single-function form.
    nc, ok = CON_LOCAL[rid]
    (tmp_path / "nc.c").write_text(nc)
    (tmp_path / "ok.c").write_text(ok)
    hits = run([tmp_path / "nc.c", tmp_path / "ok.c"])
    assert rid in hits.get(str((tmp_path / "nc.c").resolve()), set())
    assert rid not in hits.get(str((tmp_path / "ok.c").resolve()), set())
