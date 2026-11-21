"""A run where files failed to parse must not look like a clean run."""
import json
import shutil

import pytest

from cert_review import action, cli, formatters as Fm
from cert_review import toolrun as T

TOOLS = [{"tool": "clang-tidy", "available": True, "version": "19", "files_with_errors": ["/r/a.cc"],
          "parse_errors": 1}]


def test_tool_status_values():
    assert T.ToolStatus("x", False).status == "missing"
    assert T.ToolStatus("x", True).status == "ok"
    assert T.ToolStatus("x", True, parse_errors=1, files_with_errors=["a"]).status == "partial"


def test_parse_warnings_accepts_objects_and_dicts():
    st = T.ToolStatus("clang-tidy", True, parse_errors=1, files_with_errors=["/r/a.cc"])
    assert len(T.parse_warnings([st])) == 1 and "/r/a.cc" in T.parse_warnings([st])[0]
    assert T.parse_warnings(TOOLS) and T.parse_warnings([{"tool": "x", "available": True}]) == []


def test_markdown_warns_even_without_findings():
    md = Fm.to_markdown([], warnings=T.parse_warnings(TOOLS))
    assert "partial analysis" in md and "/r/a.cc" in md and md.strip() != "No SEI CERT findings."
    assert Fm.to_markdown([]) == "No SEI CERT findings.\n"


def test_sarif_marks_run_unsuccessful():
    w = T.parse_warnings(TOOLS)
    inv = Fm.to_sarif([], warnings=w)["runs"][0]["invocations"][0]
    assert inv["executionSuccessful"] is False
    assert inv["toolExecutionNotifications"][0]["level"] == "warning"
    ok = Fm.to_sarif([])["runs"][0]["invocations"][0]
    assert ok["executionSuccessful"] is True and ok["toolExecutionNotifications"] == []


def test_github_review_body_carries_warning():
    p = Fm.to_github_review([], warnings=T.parse_warnings(TOOLS))
    assert "partial analysis" in p["body"]


def test_action_summary_and_output():
    md = action.summary_md({"tools": TOOLS, "files": ["a"], "warnings": T.parse_warnings(TOOLS)},
                           [], "/r", "diff", "default", False, "never")
    assert "partial analysis" in md.lower() and "No findings." in md


@pytest.mark.skipif(not shutil.which("clang-tidy"), reason="clang-tidy not installed")
def test_cli_partial_and_fail_on_parse_error(tmp_path, capsys):
    (tmp_path / "a.c").write_text('#include "does_not_exist.h"\nint f(void) { return 0; }\n')
    base = ["check", str(tmp_path / "a.c"), "--tools", "clang-tidy", "--format", "markdown"]
    assert cli.main(base) == 0
    cap = capsys.readouterr()
    assert "partial" in cap.err and "WARNING" in cap.err and "partial analysis" in cap.out
    assert cli.main(base + ["--fail-on-parse-error"]) == 1


def test_report_json_has_status(tmp_path):
    from cert_review import engine
    r = engine.Result(tools=[T.ToolStatus("clang-tidy", True, parse_errors=1, files_with_errors=["a"])])
    d = r.to_dict()
    assert d["tools"][0]["status"] == "partial" and d["warnings"]
    json.dumps(d)
