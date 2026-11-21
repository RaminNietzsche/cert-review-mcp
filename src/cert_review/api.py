"""Shared API behind the CLI and the MCP server (all functions return plain data)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from . import baseline as BL
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
               coverage: str | None = None, limit: int = 500, standard: Any = None,
               classification: str | None = None) -> dict:
    out = []
    for r in R.list_rules(lang=lang, category=category, kind=kind, level=level, detectable=detectable,
                          standard=standard, classification=classification):
        e = CM.rule_entry(r["id"])
        if coverage and e["tier_runnable"] != coverage and e["tier"] != coverage:
            continue
        s = R.summary(r)
        s["coverage"] = e["tier"]
        s["coverage_runnable"] = e["tier_runnable"]
        out.append(s)
    return {"count": len(out), "rules": out[:limit], "truncated": len(out) > limit}


def _guideline_record(r: dict, prof: P.Profile) -> dict:
    from . import ruletexts
    e = CM.rule_entry(r["id"])
    std = R.standard_of(r)
    lic = ruletexts.text_for(r["id"])
    return {
        "id": r["id"], "title": R.title(r), "lang": r["lang"], "kind": r["kind"],
        "category": r["category"], "url": R.url(r), "cwe": [], "risk": None,
        "text": R.rule_text(r), "exceptions": None, "examples": [],
        "automated_detection": None, "related_guidelines": None,
        "standard": std, "display_name": R.display_name(r), "local_id": r["local_id"],
        "classification": r["classification"], "category_name": r.get("category_name"),
        "summary": r.get("summary"), "decidability": r.get("decidability"),
        "enforcement": r.get("enforcement"), "target": r.get("target"),
        "cert": r.get("cert", []),
        "text_source": "licensed-file" if lic else "summary-only",
        "quote_required": bool(lic),
        "coverage": {"tier": e["tier"], "tier_runnable": e["tier_runnable"],
                     "checkers": [{k: c[k] for k in ("tool", "checker", "specific", "available")}
                                  | {"source": c.get("source")} for c in e["checkers"]]},
        "profile": {"name": prof.name, "override": prof.override(r["id"]),
                    "disabled": prof.disabled(r["id"]), "idioms": []},
        "source": {**R.guideline_info()["standards"].get(std, {}),
                   "data_sources": R.guideline_info()["sources"],
                   "notice": R.guideline_info()["notice"]},
    }


def related_guidelines_for_cert(cert_id: str) -> list[dict]:
    """MISRA/AUTOSAR guidelines that cite (or are cited by) a SEI CERT rule."""
    out = []
    for g in R.guidelines().values():
        for c in g.get("cert", []):
            if c["id"] == cert_id:
                out.append({"id": g["id"], "standard": g["standard"],
                            "name": R.display_name(g), "relation": c["relation"],
                            "source": c["source"]})
    return out


def explain_rule(rule_id: str, profile: str = "default") -> dict:
    r = R.get(rule_id)
    if r is None:
        near = [x["id"] for x in R.search(rule_id, 5, standard="all")]
        return {"error": f"unknown rule {rule_id}", "did_you_mean": near}
    prof = P.load(profile)
    if not R.is_cert(r):
        return _guideline_record(r, prof)
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
        "standard": R.standard_of(r),
        "cross_references": related_guidelines_for_cert(r["id"]),
    }


def explain_finding(finding: dict, profile: str = "default", context_lines: int = 3) -> dict:
    from . import explain as EX
    return EX.explain(finding, profile, context_lines)


def write_baseline(result: dict, path: str, update: bool = False) -> dict:
    """Create or update a baseline file from a check_file/check_diff result."""
    root = BL.root_of(path)
    old = BL.load(path) if update and Path(path).expanduser().exists() else None
    data, stats = BL.update(old, result["findings"], result.get("files", []), root)
    BL.dump(data, Path(path).expanduser())
    stats["path"] = str(Path(path).expanduser().resolve())
    return stats


def search_rules(query: str, limit: int = 10, lang: str | None = None, standard: Any = None) -> dict:
    return {"query": query, "results": R.search(query, limit, lang, standard)}


def _collect(paths: list[str]) -> list[str]:
    return [str(Path(p).expanduser()) for p in paths]


def check_file(path: str | list[str], profile: str = "default", lang: str | None = None,
               compdb: str | None = None, root: str | None = None,
               tools: list[str] | None = None, min_confidence: float = 0.0,
               include_suppressed: bool = False, jobs: int = 4,
               max_rules_per_location: int = 2, standards: Any = None,
               baseline: str | None = None) -> dict:
    paths = [path] if isinstance(path, str) else list(path)
    res = engine.check(_collect(paths), profile, lang, compdb, root,
                       tuple(tools) if tools else engine.DEFAULT_TOOLS,
                       None, jobs, max_rules_per_location, min_confidence, include_suppressed,
                       standards)
    d = res.to_dict(include_suppressed)
    if baseline:
        BL.apply(d, baseline, scope="files")
    d["summary"] = summarize(d["findings"])
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
               min_confidence: float = 0.0, include_suppressed: bool = False, jobs: int = 4,
               max_rules_per_location: int = 2, standards: Any = None,
               baseline: str | None = None) -> dict:
    text = _diff_text(repo, base, head, diff_text)
    changed = diffutil.parse_unified_diff(text)
    root_p, abs_changed = diffutil.prepare_diff_workspace(repo, text)
    root = str(root_p)
    prof = P.load(profile)
    files = engine.select_files(list(abs_changed), prof, None, root_p)
    res = engine.check(files, prof, None, compdb, root,
                       tuple(tools) if tools else engine.DEFAULT_TOOLS,
                       abs_changed, jobs, max_rules_per_location, min_confidence, include_suppressed,
                       standards)
    d = res.to_dict(include_suppressed)
    if baseline:
        BL.apply(d, baseline, scope="diff")
    d["summary"] = summarize(d["findings"])
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
        root, abs_changed = diffutil.prepare_diff_workspace(repo, text)
        hunk_ctx = diffutil.hunks_with_context(text, context_lines)
        ranges = {str(root / k): v for k, v in hunk_ctx.items()}
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


def rule_coverage(lang: str | None = None, kind: str | None = None, include_ids: bool = False,
                  standard: Any = None) -> dict:
    stds = R.expand_standards(standard)
    c = CM.coverage(lang, kind, stds)
    if not include_ids:
        c.pop("rules_all_mappings")
        c.pop("rules_runnable")
    c["standards"] = list(stds)
    c["definitions"] = CM.info()["tier_definitions"]
    c["sources"] = CM.info()["sources"]
    if set(stds) - set(R.CERT_STANDARDS):
        from . import ruletexts
        g = R.guideline_info()
        c["definitions"] = {**c["definitions"],
                            "deterministic": c["definitions"]["deterministic"]
                            + "; for MISRA/AUTOSAR: a checker that reports exactly this guideline "
                              "(e.g. the cppcheck MISRA addon)"}
        c["sources"] = {**c["sources"], "guidelines": g["sources"]}
        c["toolchain"] = {**c["toolchain"], **{k: v for k, v in
                                               R._load_guidelines().get("toolchain_versions", {}).items() if v}}
        by_std = {}
        for s in stds:
            if s in R.CERT_STANDARDS:
                continue
            sc = CM.coverage(lang, kind, (s,))
            by_std[s] = {"total": sc["total"], "all_mappings": sc["all_mappings"],
                         "runnable_toolchain": sc["runnable_toolchain"],
                         "summaries": (g["standards"].get(s) or {}).get("summaries")}
        c["by_standard"] = by_std
        c["licensed_texts"] = {k: v for k, v in ruletexts.status().items() if k in stds}
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
