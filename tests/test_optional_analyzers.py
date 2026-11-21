"""Optional analyzers: tool selection, missing-tool warnings, and the Infer and
CodeQL adapters with the external commands replaced by fakes."""
import json
import subprocess
from pathlib import Path

import pytest

from cert_review import analyzers_extra as EX, checkers_map as CM, engine, profiles as P


def fake_which(present):
    return lambda tool: f"/usr/bin/{tool}" if tool in present else None


@pytest.fixture
def only(monkeypatch):
    def set_(*present):
        monkeypatch.setattr(EX, "which", fake_which(set(present)))
        monkeypatch.setattr(EX, "available", lambda t: t in set(present))
    return set_


def test_auto_adds_installed_optional_tools(only):
    only("semgrep")
    assert engine.resolve_tools(None) == (("clang-tidy", "clangsa", "cppcheck", "semgrep"), False)
    assert engine.resolve_tools(["auto"])[1] is False
    only("semgrep", "infer", "codeql")
    tools, _ = engine.resolve_tools([])
    assert "infer" in tools and "codeql" not in tools      # codeql is opt-in


def test_explicit_selection_and_unknown_names(only):
    only()
    assert engine.resolve_tools(["cppcheck", "codeql"]) == (("cppcheck", "codeql"), True)
    assert engine.resolve_tools(["auto", "codeql"])[0] == ("clang-tidy", "clangsa", "cppcheck", "codeql")
    with pytest.raises(ValueError, match="coverity"):
        engine.resolve_tools(["coverity"])


def test_missing_requested_tool_is_a_warning(only, tmp_path):
    only()
    f = tmp_path / "a.c"
    f.write_text("int main(void) { return 0; }\n")
    res = engine.check([str(f)], "default", tools=["infer", "semgrep"])
    d = res.to_dict()
    assert {t["tool"]: t["status"] for t in d["tools"]} == {"infer": "missing", "semgrep": "missing"}
    assert any(w.startswith("infer: requested but not run") for w in d["warnings"])
    assert any("pip install semgrep" in w for w in d["warnings"])


def test_auto_mode_notes_but_does_not_warn(only, tmp_path):
    only()
    f = tmp_path / "a.c"
    f.write_text("int x;\n")
    res = engine.check([str(f)], "default", tools=None)
    assert not any(t.tool in EX.OPTIONAL_TOOLS for t in res.tools)
    assert not engine.missing_warnings(res.tools)


def test_infer_checkers_map_to_cert_rules():
    idx = CM.reverse_index()
    assert {e["rule_id"] for e in idx[("infer", "NULLPTR_DEREFERENCE")]} == {"EXP34-C"}
    assert {"MEM30-C", "MEM50-CPP"} <= {e["rule_id"] for e in idx[("infer", "USE_AFTER_FREE")]}
    assert CM.tier_for_tools("EXP34-C", ["infer"]) == "partial"


def test_infer_adapter(monkeypatch, tmp_path, only):
    only("infer")
    monkeypatch.setattr(EX, "version", lambda t: "1.3.0")
    good, bad = tmp_path / "a.c", tmp_path / "b.c"
    good.write_text("int main(void) { int *p = 0; return *p; }\n")
    bad.write_text("syntax error here\n")
    seen = {}

    def run(cmd, **kw):
        seen["cmd"] = cmd
        out = Path(cmd[cmd.index("-o") + 1])
        cdb = json.loads(Path(cmd[cmd.index("--compilation-database") + 1]).read_text())
        seen["cdb"] = cdb
        out.mkdir()
        (out / "report.json").write_text(json.dumps([
            {"bug_type": "NULLPTR_DEREFERENCE", "file": "a.c", "line": 1, "column": 31,
             "qualifier": "pointer `p` last assigned on line 1 could be null"},
            {"bug_type": "SOME_UNMAPPED_TYPE", "file": "a.c", "line": 1, "column": 1, "qualifier": "x"},
        ]))
        return subprocess.CompletedProcess(cmd, 0, f"{bad}:1:1: error: unknown type name 'syntax'\n", "")

    monkeypatch.setattr(EX.subprocess, "run", run)
    raw, st = EX.run_infer([str(good), str(bad)], P.load("default"), None, None, jobs=2)
    assert "--pulse" in seen["cmd"] and len(seen["cdb"]) == 2
    assert [(r.checker, Path(r.file).name, r.line) for r in raw] == [("NULLPTR_DEREFERENCE", "a.c", 1)]
    assert st.status == "partial" and st.files_with_errors == [str(bad.resolve())]
    kept, _ = engine.normalize(raw, P.load("default"))
    assert {k.rule_id for k in kept} == {"EXP34-C"}


def test_codeql_adapter_without_packs(monkeypatch, tmp_path, only):
    only("codeql")
    monkeypatch.setattr(EX, "version", lambda t: "2.27.5")
    monkeypatch.setattr(EX.subprocess, "run",
                        lambda cmd, **kw: subprocess.CompletedProcess(cmd, 2, "", "pack not found"))
    f = tmp_path / "a.c"
    f.write_text("int x;\n")
    raw, st = EX.run_codeql([str(f)], P.load("default"), None, None)
    assert raw == [] and st.status == "missing"
    assert "codeql pack download codeql/cert-c-coding-standards" in st.notes[0]


def test_codeql_adapter_maps_sarif(monkeypatch, tmp_path, only):
    only("codeql")
    monkeypatch.setattr(EX, "version", lambda t: "2.27.5")
    qid = next(c for (tool, c) in CM.reverse_index() if tool == "codeql" and c.startswith("c/cert/"))
    rid = CM.reverse_index()[("codeql", qid)][0]["rule_id"]
    f = tmp_path / "proj" / "a.c"
    f.parent.mkdir()
    f.write_text("int x;\n")
    calls = []

    def run(cmd, **kw):
        calls.append(cmd[1:3])
        if cmd[1:3] == ["database", "create"]:
            src = next(a.split("=", 1)[1] for a in cmd if a.startswith("--source-root="))
            assert (Path(src) / "a.c").exists() and "--build-mode=none" in cmd
        if cmd[1:3] == ["database", "analyze"]:
            out = next(a.split("=", 1)[1] for a in cmd if a.startswith("--output="))
            Path(out).write_text(json.dumps({"runs": [{"results": [
                {"ruleId": qid, "message": {"text": "m"}, "locations": [{"physicalLocation": {
                    "artifactLocation": {"uri": "a.c"}, "region": {"startLine": 1, "startColumn": 5}}}]},
                {"ruleId": "c/not-mapped", "message": {"text": "m"}, "locations": []},
            ]}]}))
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(EX.subprocess, "run", run)
    raw, st = EX.run_codeql([str(f)], P.load("default"), None, None)
    assert ["database", "analyze"] in calls
    assert [(r.checker, r.file, r.line) for r in raw] == [(qid, str(f.resolve()), 1)]
    assert st.status == "ok"
    kept, _ = engine.normalize(raw, P.load("default"))
    assert rid in {k.rule_id for k in kept}


def test_extended_tier_counts_optional_analyzers():
    cov = CM.coverage()
    assert cov["extended_toolchain"]
    e = CM.rule_entry("EXP34-C")
    assert e["tier_runnable"] in ("deterministic", "partial")
    assert "tier_extended" in e


def test_codeql_traced_build_keeps_only_compiler_commands(monkeypatch, tmp_path, only):
    only("codeql")
    monkeypatch.setattr(EX, "version", lambda t: "2.27.5")
    f = tmp_path / "a.c"
    f.write_text("int x;\n")
    (tmp_path / "compile_commands.json").write_text(json.dumps([
        {"directory": str(tmp_path), "file": str(f),
         "arguments": ["/usr/bin/clang-19", "-fplugin=/tmp/p.so", "-Xclang", "-load", "@rsp",
                       "-c", str(f), "-o", "a.o"]}]))
    scripts = []

    def run(cmd, **kw):
        if cmd[1:3] == ["database", "create"]:
            script = next(a.split("=", 1)[1] for a in cmd if a.startswith("--command="))
            scripts.append(Path(script).read_text())
            return subprocess.CompletedProcess(cmd, 1, "", "stop here")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(EX.subprocess, "run", run)
    _, st = EX.run_codeql([str(f)], P.load("default"), tmp_path, None)
    body = scripts[0]
    assert "/usr/bin/clang-19" in body and "-fsyntax-only" in body
    assert "-fplugin" not in body and "-load" not in body and "@rsp" not in body

    (tmp_path / "compile_commands.json").write_text(json.dumps([
        {"directory": str(tmp_path), "file": str(f), "command": f"sh -c 'touch /tmp/x' {f}"}]))
    scripts.clear()
    raw, st = EX.run_codeql([str(f)], P.load("default"), tmp_path, None)
    assert raw == [] and not scripts and "no safe compiler commands" in st.notes[-1]
