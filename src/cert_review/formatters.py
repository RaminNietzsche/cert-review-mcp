"""Format findings as review comments or SARIF. Formatting only: nothing is posted."""
from __future__ import annotations

import json
import os
from typing import Any

from . import rules as R
from . import __version__

SARIF_LEVEL = {"error": "error", "warning": "warning", "note": "note"}
MARKER = "<!-- cert-review -->"


def _first_paragraph(text: str, limit: int = 420) -> str:
    para = (text or "").strip().split("\n\n")[0].replace("\n", " ")
    return para if len(para) <= limit else para[: limit - 1].rsplit(" ", 1)[0] + "\u2026"


def compliant_snippet(rule_id: str, max_lines: int = 14) -> str | None:
    r = R.get(rule_id)
    if not r:
        return None
    for ex in r["examples"]:
        for c in ex["compliant"]:
            for b in c["code"]:
                lines = b["code"].strip("\n").splitlines()
                if lines:
                    snip = "\n".join(lines[:max_lines])
                    if len(lines) > max_lines:
                        snip += "\n/* ... */"
                    return f"```{b['lang'] or ''}\n{snip}\n```"
    return None


def comment_body(f: dict, with_example: bool = True) -> str:
    r = R.get(f["rule_id"]) or {}
    head = (f"**CERT {f['rule_id']}** \u2014 {f.get('title') or r.get('title', '')}  \n"
            f"severity: {f['severity']} \u00b7 priority P{f['priority']} \u00b7 level {f['level']}")
    parts = [head, "", f["message"].strip()]
    why = _first_paragraph(r.get("risk_text", "")) or _first_paragraph(r.get("intro", ""))
    if why:
        parts += ["", f"**Why it matters:** {why}"]
    if f.get("fix"):
        parts += ["", "**Suggested fix:**", "```", str(f["fix"]).strip(), "```"]
    elif with_example:
        snip = compliant_snippet(f["rule_id"])
        if snip:
            parts += ["", "**Compliant approach (from the rule):**", snip]
    if f.get("quote"):
        parts += ["", f"> {f['quote']}"]
    if f.get("note"):
        parts += ["", f"**Project note:** {f['note']}"]
    url = f.get("url") or r.get("url")
    src = f"{f['tool']}:{f['checker']}" if f.get("tool") else ""
    foot = f"Rule: {url}" + (f" \u00b7 found by `{src}` (confidence {f.get('confidence')})" if src else "")
    parts += ["", foot]
    return "\n".join(p for p in parts if p is not None).strip()


def _rel(path: str, root: str | None) -> str:
    root = root or (os.getcwd() if os.path.isabs(path) else None)
    if root:
        try:
            return os.path.relpath(path, root)
        except ValueError:
            return path
    return path


def to_markdown(findings: list[dict], root: str | None = None) -> str:
    if not findings:
        return "No SEI CERT findings.\n"
    out = [f"# SEI CERT review: {len(findings)} finding(s)\n"]
    by_file: dict[str, list[dict]] = {}
    for f in findings:
        by_file.setdefault(_rel(f["file"], root), []).append(f)
    for path, fs in by_file.items():
        out.append(f"## `{path}`\n")
        for f in sorted(fs, key=lambda x: x["line"]):
            out.append(f"- **{f['rule_id']}** (line {f['line']}, {f['severity']}, P{f['priority']}/{f['level']}): "
                       f"{f['message'].strip()} \u2014 `{f['tool']}:{f['checker']}`")
    return "\n".join(out) + "\n"


def to_github_review(findings: list[dict], root: str | None = None, summary: str | None = None) -> dict:
    """Body for `POST /repos/{o}/{r}/pulls/{n}/reviews` (event COMMENT). Not sent."""
    comments = [{"path": _rel(f["file"], root), "line": f["line"], "side": "RIGHT",
                 "body": comment_body(f)} for f in findings]
    body = summary or (f"SEI CERT review: {len(findings)} finding(s). "
                       "Drafted for human review; nothing is posted automatically.")
    return {"event": "COMMENT", "body": body, "comments": comments}


def to_gitlab_discussions(findings: list[dict], root: str | None = None) -> list[dict]:
    """Bodies for `POST /projects/:id/merge_requests/:iid/discussions`.

    `position` needs the MR's diff_refs (base_sha, start_sha, head_sha); they
    are left as placeholders for the caller to fill. Nothing is sent.
    """
    out = []
    for f in findings:
        out.append({"body": comment_body(f),
                    "position": {"position_type": "text", "base_sha": "<diff_refs.base_sha>",
                                 "start_sha": "<diff_refs.start_sha>", "head_sha": "<diff_refs.head_sha>",
                                 "old_path": _rel(f["file"], root), "new_path": _rel(f["file"], root),
                                 "new_line": f["line"]}})
    return out


def to_sarif(findings: list[dict], root: str | None = None, tool_name: str = "cert-review") -> dict:
    rule_ids = sorted({f["rule_id"] for f in findings})
    rules_out = []
    for rid in rule_ids:
        r = R.get(rid) or {}
        risk = r.get("risk") or {}
        rules_out.append({
            "id": rid,
            "name": rid.replace("-", ""),
            "shortDescription": {"text": r.get("title", rid)},
            "fullDescription": {"text": _first_paragraph(r.get("intro", ""), 900) or r.get("title", rid)},
            "helpUri": r.get("url"),
            "help": {"text": comment_body({"rule_id": rid, "severity": risk.get("severity", ""),
                                           "priority": 0, "level": risk.get("level", ""),
                                           "message": r.get("title", ""), "tool": "", "checker": ""},
                                          with_example=True),
                     "markdown": ""},
            "properties": {"tags": ["security", "external/cert/" + rid.lower()] +
                                   [c.lower() for c in r.get("cwe", [])],
                           "certSeverity": risk.get("severity"), "certLikelihood": risk.get("likelihood"),
                           "certPriority": risk.get("priority"), "certLevel": risk.get("level"),
                           "security-severity": {"High": "8.0", "Medium": "5.0", "Low": "2.0"}.get(
                               risk.get("severity", ""), "5.0")},
        })
    idx = {rid: i for i, rid in enumerate(rule_ids)}
    results = []
    for f in findings:
        results.append({
            "ruleId": f["rule_id"], "ruleIndex": idx[f["rule_id"]],
            "level": SARIF_LEVEL.get(f["severity"], "warning"),
            "message": {"text": f["message"].strip()},
            "locations": [{"physicalLocation": {
                "artifactLocation": {"uri": _rel(f["file"], root).replace(os.sep, "/")},
                "region": {"startLine": f["line"], "startColumn": max(1, f.get("col") or 1)}}}],
            "partialFingerprints": {"certReview/v1": f"{f['rule_id']}:{_rel(f['file'], root)}:{f['line']}"},
            "properties": {"tool": f.get("tool"), "checker": f.get("checker"),
                           "confidence": f.get("confidence"), "priority": f.get("priority"),
                           "level": f.get("level"), "alsoFoundBy": f.get("also_found_by", [])},
        })
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{"tool": {"driver": {
            "name": tool_name, "version": __version__,
            "informationUri": "https://cmu-sei.github.io/secure-coding-standards/",
            "rules": rules_out}},
            "results": results,
            "properties": {"ruleDatabaseCommit": R.source_info()["commit"]}}],
    }


def _fingerprint(f: dict, root: str | None) -> str:
    import hashlib
    key = f"{f['rule_id']}:{_rel(f['file'], root)}:{f['line']}:{f['checker']}"
    return hashlib.sha256(key.encode()).hexdigest()


def to_codequality(findings: list[dict], root: str | None = None) -> list[dict]:
    """GitLab Code Quality (Code Climate) report: gl-code-quality-report.json."""
    sev = {"error": "critical", "warning": "major", "note": "minor"}
    return [{
        "description": f"CERT {f['rule_id']}: {f['message'].strip()}",
        "check_name": f["rule_id"],
        "fingerprint": _fingerprint(f, root),
        "severity": sev.get(f["severity"], "major"),
        "location": {"path": _rel(f["file"], root).replace(os.sep, "/"),
                     "lines": {"begin": f["line"]}},
    } for f in findings]


def to_gitlab_sast(findings: list[dict], root: str | None = None) -> dict:
    """GitLab SAST report (schema 15.x): gl-sast-report.json."""
    sev = {"error": "High", "warning": "Medium", "note": "Low"}
    vulns = []
    for f in findings:
        r = R.get(f["rule_id"]) or {}
        ids = [{"type": "cert", "name": f["rule_id"], "value": f["rule_id"], "url": r.get("url")}]
        ids += [{"type": "cwe", "name": c, "value": c.split("-")[-1],
                 "url": f"https://cwe.mitre.org/data/definitions/{c.split('-')[-1]}.html"}
                for c in r.get("cwe", [])]
        vulns.append({
            "id": _fingerprint(f, root),
            "category": "sast",
            "name": f"{f['rule_id']}: {f.get('title') or r.get('title', '')}",
            "message": f["message"].strip(),
            "description": _first_paragraph(r.get("risk_text", "") or r.get("intro", ""), 600),
            "severity": sev.get(f["severity"], "Medium"),
            "confidence": "High" if f.get("confidence", 0) >= 0.8 else
                          "Medium" if f.get("confidence", 0) >= 0.5 else "Low",
            "scanner": {"id": "cert-review", "name": "cert-review"},
            "location": {"file": _rel(f["file"], root).replace(os.sep, "/"), "start_line": f["line"]},
            "identifiers": ids,
        })
    return {"version": "15.0.7",
            "scan": {"analyzer": {"id": "cert-review", "name": "cert-review", "version": __version__,
                                  "vendor": {"name": "cert-review"}},
                     "scanner": {"id": "cert-review", "name": "cert-review", "version": __version__,
                                 "vendor": {"name": "cert-review"}},
                     "type": "sast", "status": "success",
                     "start_time": "1970-01-01T00:00:00", "end_time": "1970-01-01T00:00:00"},
            "vulnerabilities": vulns}


def format_review(findings: list[dict], style: str = "markdown", root: str | None = None) -> Any:
    style = style.lower()
    if style == "markdown":
        return to_markdown(findings, root)
    if style == "github":
        return to_github_review(findings, root)
    if style == "gitlab":
        return to_gitlab_discussions(findings, root)
    if style == "sarif":
        return to_sarif(findings, root)
    if style == "codequality":
        return to_codequality(findings, root)
    if style == "gitlab-sast":
        return to_gitlab_sast(findings, root)
    raise ValueError("style must be one of: github, gitlab, sarif, markdown, codequality, gitlab-sast")


def dumps(obj: Any) -> str:
    return obj if isinstance(obj, str) else json.dumps(obj, indent=2, ensure_ascii=False)
