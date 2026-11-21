"""cert-review command line: check | diff | explain | coverage | packet | rules | validate."""
from __future__ import annotations

import argparse
import json
import sys

from . import api, formatters


def _emit(findings: list[dict], fmt: str, root: str | None, out: str | None,
          warnings: list[str] | None = None) -> None:
    if fmt == "json":
        text = json.dumps(findings, indent=2)
    else:
        text = formatters.dumps(formatters.format_review(findings, fmt, root, warnings))
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    else:
        print(text)


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--profile", default="default", help="profile name or YAML path (default, ceph)")
    p.add_argument("--compdb", help="directory containing compile_commands.json")
    p.add_argument("--tools", default="clang-tidy,clangsa,cppcheck")
    p.add_argument("--format", default="markdown",
                   choices=["markdown", "json", "sarif", "github", "gitlab", "codequality", "gitlab-sast"])
    p.add_argument("--output", "-o")
    p.add_argument("--report", help="also write the full result (tool status, suppressed findings) as JSON")
    p.add_argument("--min-confidence", type=float, default=0.0)
    p.add_argument("--fail-on", choices=["error", "warning", "note", "never"], default="never",
                   help="exit 1 if a finding at or above this severity exists")
    p.add_argument("--fail-on-parse-error", "--fail-on-partial", dest="fail_on_parse_error",
                   action="store_true",
                   help="exit 1 if the analysis was partial: a file had compile errors or timed out")
    p.add_argument("--include-suppressed", action="store_true")
    p.add_argument("--standards", help="comma-separated standards to map findings to, overriding the "
                   "profile: cert, misra, autosar, misra-c-2012, misra-cpp-2023, autosar-cpp14, all")
    p.add_argument("--max-rules-per-location", type=int, default=2,
                   help="many CERT rules map to one checker; keep the best N per line")


def _stds(a: argparse.Namespace) -> list[str] | None:
    return [x for x in a.standards.split(",") if x.strip()] if getattr(a, "standards", None) else None


def _exit_code(findings: list[dict], fail_on: str, parse_failed: bool = False) -> int:
    if parse_failed:
        return 1
    order = {"note": 1, "warning": 2, "error": 3}
    if fail_on == "never":
        return 0
    return 1 if any(order[f["severity"]] >= order[fail_on] for f in findings) else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cert-review", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="analyse files or directories")
    c.add_argument("paths", nargs="+")
    c.add_argument("--lang", choices=["c", "cpp"])
    c.add_argument("--root", help="project root (adds include dirs, relativises paths)")
    c.add_argument("-j", "--jobs", type=int, default=4)
    _common(c)

    d = sub.add_parser("diff", help="analyse only changed lines")
    d.add_argument("--repo", default=".")
    d.add_argument("--base", help="git base ref")
    d.add_argument("--head", help="git head ref (default: working tree)")
    d.add_argument("--diff-file", help="unified diff file, or - for stdin")
    d.add_argument("-j", "--jobs", type=int, default=4)
    _common(d)

    e = sub.add_parser("explain", help="show a rule")
    e.add_argument("rule_id")
    e.add_argument("--profile", default="default")
    e.add_argument("--json", action="store_true")

    std_help = "cert (default), misra, autosar, misra-c-2012, misra-cpp-2023, autosar-cpp14 or all"
    cv = sub.add_parser("coverage", help="deterministic / partial / llm-only counts")
    cv.add_argument("--standard", default="cert", help=std_help)
    cv.add_argument("--lang", choices=["c", "cpp"])
    cv.add_argument("--kind", choices=["rule", "recommendation", "directive"])
    cv.add_argument("--ids", action="store_true")

    r = sub.add_parser("rules", help="list or search rules")
    r.add_argument("--standard", default="cert", help=std_help)
    r.add_argument("--classification", choices=["mandatory", "required", "advisory", "document"])
    r.add_argument("--lang", choices=["c", "cpp"])
    r.add_argument("--category")
    r.add_argument("--kind", choices=["rule", "recommendation", "directive"])
    r.add_argument("--level")
    r.add_argument("--coverage", choices=["deterministic", "partial", "llm-only"])
    r.add_argument("--search")

    pk = sub.add_parser("packet", help="build the LLM review packet")
    pk.add_argument("paths", nargs="*")
    pk.add_argument("--repo")
    pk.add_argument("--base")
    pk.add_argument("--head")
    pk.add_argument("--profile", default="default")
    pk.add_argument("--no-static", action="store_true")
    pk.add_argument("--compdb")
    pk.add_argument("-o", "--output")

    v = sub.add_parser("validate", help="validate LLM findings (JSON file or -) against the rules")
    v.add_argument("findings")
    v.add_argument("--packet")
    v.add_argument("--profile", default="default")

    a = ap.parse_args(argv)

    if a.cmd == "check":
        res = api.check_file(a.paths, a.profile, a.lang, a.compdb, a.root,
                             a.tools.split(","), a.min_confidence, a.include_suppressed, a.jobs,
                             a.max_rules_per_location, _stds(a))
        _emit(res["findings"], a.format, a.root, a.output, res.get("warnings"))
        _write_report(res, a.report)
        _status(res)
        return _exit_code(res["findings"], a.fail_on, a.fail_on_parse_error and bool(res.get("warnings")))
    if a.cmd == "diff":
        text = None
        if a.diff_file:
            text = sys.stdin.read() if a.diff_file == "-" else open(a.diff_file, encoding="utf-8").read()
        res = api.check_diff(a.repo, a.base, a.head, text, a.profile, a.compdb, a.tools.split(","),
                             a.min_confidence, a.include_suppressed, a.jobs,
                             a.max_rules_per_location, _stds(a))
        _emit(res["findings"], a.format, res["root"], a.output, res.get("warnings"))
        _write_report(res, a.report)
        _status(res)
        return _exit_code(res["findings"], a.fail_on, a.fail_on_parse_error and bool(res.get("warnings")))
    if a.cmd == "explain":
        res = api.explain_rule(a.rule_id, a.profile)
        if a.json or "error" in res:
            print(json.dumps(res, indent=2))
            return 1 if "error" in res else 0
        from . import rules as R
        print(R.rule_text(R.get(a.rule_id)))
        if res.get("cross_references"):
            print("\nRelated MISRA/AUTOSAR: " + ", ".join(
                f"{x['name']} ({x['relation']})" for x in res["cross_references"]))
        print(f"\nURL: {res['url']}\nCoverage: {res['coverage']['tier']} "
              f"(runnable: {res['coverage']['tier_runnable']}); checkers: "
              + ", ".join(f"{c['tool']}:{c['checker']}" for c in res["coverage"]["checkers"]))
        if res["profile"]["override"]:
            print(f"Profile {a.profile}: {res['profile']['override']}")
        return 0
    if a.cmd == "coverage":
        print(json.dumps(api.rule_coverage(a.lang, a.kind, a.ids, a.standard), indent=2))
        return 0
    if a.cmd == "rules":
        if a.search:
            print(json.dumps(api.search_rules(a.search, 15, a.lang, a.standard), indent=2))
        else:
            for s in api.list_rules(a.lang, a.category, a.kind, a.level, None, a.coverage,
                                    100000, a.standard, a.classification)["rules"]:
                if s.get("classification"):
                    print(f"{s['id']:<24} {s['classification']:<10} "
                          f"{s['coverage_runnable']:<13} {s['title']}")
                    continue
                print(f"{s['id']:<11} {s['level'] or '':<3} {str(s['priority'] or ''):<4} "
                      f"{s['coverage_runnable']:<13} {s['title']}")
        return 0
    if a.cmd == "packet":
        res = api.review_packet(a.paths or None, a.repo, a.base, a.head, None, a.profile,
                                not a.no_static, a.compdb)
        text = json.dumps(res, indent=2)
        if a.output:
            open(a.output, "w", encoding="utf-8").write(text + "\n")
        else:
            print(text)
        return 0
    if a.cmd == "validate":
        raw = sys.stdin.read() if a.findings == "-" else open(a.findings, encoding="utf-8").read()
        pk_ = json.load(open(a.packet, encoding="utf-8")) if a.packet else None
        res = api.validate_findings(raw, pk_, a.profile)
        print(json.dumps(res, indent=2))
        return 1 if res["rejected"] else 0
    return 2


def _write_report(res: dict, path: str | None) -> None:
    if path:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(res, fh)


def _status(res: dict) -> None:
    s = res.get("summary", {})
    tools = ", ".join(f"{t['tool']}={t.get('status') or ('ok' if t['available'] else 'missing')}" for t in res["tools"])
    print(f"# {s.get('total', 0)} finding(s) in {len(res['files'])} file(s); tools: {tools}; "
          f"suppressed: {res['suppressed_count']}", file=sys.stderr)
    for w in res.get("warnings") or []:
        print(f"# WARNING: {w}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
