"""Shared API behind the CLI and the MCP server (all functions return plain data)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from . import checkers_map as CM
from . import diffutil
from . import engine
from . import formatters
from . import packet as PK
from . import profiles as P
from . import rules as R
from . import validator as V


def list_rules(lang: str | None = None, category: str | None = None, kind: str | None = None,
               level: str | None = None, detectable: bool | None = None,
               coverage: str | None = None, limit: int = 500) -> dict:
    out = []
    for r in R.list_rules(lang=lang, category=category, kind=kind, level=level, detectable=detectable):
        e = CM.rule_entry(r["id"])
        if coverage and e["tier_runnable"] != coverage and e["tier"] != coverage:
            continue
        s = R.summary(r)
        s["coverage"] = e["tier"]
        s["coverage_runnable"] = e["tier_runnable"]
        out.append(s)
    return {"count": len(out), "rules": out[:limit], "truncated": len(out) > limit}


def explain_rule(rule_id: str, profile: str = "default") -> dict:
    r = R.get(rule_id)
    if r is None:
        near = [x["id"] for x in R.search(rule_id, 5)]
        return {"error": f"unknown rule {rule_id}", "did_you_mean": near}
    prof = P.load(profile)
    e = CM.rule_entry(r["id"])
    return {
        "id": r["id"], "title": r["title"], "lang": r["lang"], "kind": r["kind"],
        "category": r["category"], "url": r["url"], "cwe": r["cwe"], "risk": r["risk"],
        "text": R.rule_text(r), "exceptions": r["exceptions"],
        "examples": r["examples"],
        "automated_detection": r["automated_detection"],
        "related_guidelines": r["related_guidelines"],
        "coverage": {"tier": e["tier"], "tier_runnable": e["tier_runnable"],
                     "checkers": [{k: c[k] for k in ("tool", "checker", "specific", "available")}
                                  for c in e["checkers"]]},
        "profile": {"name": prof.name, "override": prof.override(r["id"]),
                    "disabled": prof.disabled(r["id"]),
                    "idioms": [i["id"] for i in prof.raw.get("idioms", []) if r["id"] in i["rules"]]},
        "source": R.source_info(),
    }


def search_rules(query: str, limit: int = 10, lang: str | None = None) -> dict:
    return {"query": query, "results": R.search(query, limit, lang)}


def _collect(paths: list[str]) -> list[str]:
    return [str(Path(p).expanduser()) for p in paths]


def check_file(path: str | list[str], profile: str = "default", lang: str | None = None,
               compdb: str | None = None, root: str | None = None,
               tools: list[str] | None = None, min_confidence: float = 0.0,
               include_suppressed: bool = False, jobs: int = 4) -> dict:
    paths = [path] if isinstance(path, str) else list(path)
    res = engine.check(_collect(paths), profile, lang, compdb, root,
                       tuple(tools) if tools else engine.DEFAULT_TOOLS,
                       None, jobs, 2, min_confidence, include_suppressed)
    d = res.to_dict(include_suppressed)
    d["summary"] = summarize(res.findings)
    return d


def _diff_text(repo: str | None, base: str | None, head: str | None, diff_text: str | None) -> str:
    if diff_text:
        return diff_text
    if not (repo and base):
        raise ValueError("provide diff_text, or repo and base (and optionally head)")
    return diffutil.git_diff(repo, base, head)


def check_diff(repo: str | None = None, base: str | None = None, head: str | None = None,
               diff_text: str | None = None, profile: str = "default",
               compdb: str | None = None, tools: list[str] | None = None,
               min_confidence: float = 0.0, include_suppressed: bool = False, jobs: int = 4) -> dict:
    text = _diff_text(repo, base, head, diff_text)
    changed = diffutil.parse_unified_diff(text)
    root = str(Path(repo).resolve()) if repo else str(Path.cwd())
    abs_changed = {str(Path(root) / k): v for k, v in changed.items()}
    prof = P.load(profile)
    files = engine.select_files([p for p in abs_changed if Path(p).exists()], prof, None, Path(root))
    res = engine.check(files, prof, None, compdb, root,
                       tuple(tools) if tools else engine.DEFAULT_TOOLS,
                       abs_changed, jobs, 2, min_confidence, include_suppressed)
    d = res.to_dict(include_suppressed)
    d["summary"] = summarize(res.findings)
    d["changed_files"] = sorted(changed)
    d["root"] = root
    return d


def review_packet(path: str | list[str] | None = None, repo: str | None = None,
                  base: str | None = None, head: str | None = None, diff_text: str | None = None,
                  profile: str = "default", run_static: bool = True, compdb: str | None = None,
                  max_rules_per_hunk: int | None = None, context_lines: int = 3) -> dict:
    prof = P.load(profile)
    existing: list[dict] = []
    if diff_text or (repo and base):
        text = _diff_text(repo, base, head, diff_text)
        root = Path(repo).resolve() if repo else Path.cwd()
        ranges = {str(root / k): v for k, v in diffutil.hunks_with_context(text, context_lines).items()}
        ranges = {k: v for k, v in ranges.items() if Path(k).exists()}
        files = engine.select_files(list(ranges), prof, None, root)
        ranges = {k: v for k, v in ranges.items() if k in set(files)}
        if run_static and files:
            st = check_diff(repo, base, head, diff_text, profile, compdb)
            existing = st["findings"]
    elif path:
        files = engine.select_files(_collect([path] if isinstance(path, str) else list(path)), prof)
        ranges = PK.whole_file_ranges(files)
        if run_static and files:
            existing = check_file(files, profile, compdb=compdb)["findings"]
    else:
        raise ValueError("provide path, or diff_text, or repo and base")
    hunks = PK.build_hunks(ranges, (prof.raw.get("llm_review") or {}).get("max_hunk_lines", 60))
    pk = PK.build(hunks, prof, existing, max_rules_per_hunk)
    pk["static_findings"] = existing
    return pk


def validate_findings(findings: list[dict] | str, packet: dict | None = None,
                      profile: str = "default") -> dict:
    import json
    if isinstance(findings, str):
        findings = json.loads(findings)
    if isinstance(findings, dict) and "findings" in findings:
        findings = findings["findings"]
    return V.validate(findings, packet, profile)


def rule_coverage(lang: str | None = None, kind: str | None = None, include_ids: bool = False) -> dict:
    c = CM.coverage(lang, kind)
    if not include_ids:
        c.pop("rules_all_mappings")
        c.pop("rules_runnable")
    c["definitions"] = CM.info()["tier_definitions"]
    c["sources"] = CM.info()["sources"]
    return c


def format_review(findings: list[dict] | str, style: str = "markdown", root: str | None = None) -> Any:
    import json
    if isinstance(findings, str):
        findings = json.loads(findings)
    if isinstance(findings, dict) and "findings" in findings:
        findings = findings["findings"]
    return formatters.format_review(findings, style, root)


def summarize(findings) -> dict:
    items = [f.to_dict() if hasattr(f, "to_dict") else f for f in findings]
    by_sev: dict[str, int] = {}
    by_rule: dict[str, int] = {}
    for f in items:
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
        by_rule[f["rule_id"]] = by_rule.get(f["rule_id"], 0) + 1
    return {"total": len(items), "by_severity": by_sev,
            "top_rules": sorted(by_rule.items(), key=lambda x: -x[1])[:10]}
