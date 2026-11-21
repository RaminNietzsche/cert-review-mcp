"""Entry point of the GitHub Action (and usable from any CI).

Reads the action inputs from INPUT_* environment variables, runs the engine in
diff or full mode, writes SARIF and a Markdown job summary, optionally posts
ONE pull-request review with inline comments (only if review-comments is
true and a token is given), and sets the exit code from fail-on.
"""
from __future__ import annotations

import fnmatch
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from . import api, diffutil, formatters

SEV = {"note": 1, "warning": 2, "error": 3}


def inp(name: str, default: str = "") -> str:
    v = os.environ.get("INPUT_" + name.upper().replace("-", "_"), "")
    return v.strip() if v.strip() else default


def truthy(v: str) -> bool:
    return v.strip().lower() in ("1", "true", "yes", "on")


def split_globs(v: str) -> list[str]:
    return [x.strip() for x in v.replace(",", "\n").splitlines() if x.strip()]


def log(level: str, msg: str) -> None:
    print(f"::{level}::{msg}" if os.environ.get("GITHUB_ACTIONS") else f"{level}: {msg}", flush=True)


def event() -> dict:
    p = os.environ.get("GITHUB_EVENT_PATH")
    if p and Path(p).exists():
        try:
            return json.loads(Path(p).read_text())
        except ValueError:
            return {}
    return {}


def git(repo: str, *args: str) -> str:
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or f"git {' '.join(args)} failed")
    return r.stdout.strip()


def resolve_base(repo: str, base_input: str, ev: dict) -> str:
    """Merge-base of the requested base and HEAD, so only the PR's own lines are reviewed."""
    candidates = []
    if base_input:
        candidates += [base_input, f"origin/{base_input}"]
    pr = ev.get("pull_request") or {}
    if pr.get("base", {}).get("sha"):
        candidates.append(pr["base"]["sha"])
    if os.environ.get("GITHUB_BASE_REF"):
        candidates.append("origin/" + os.environ["GITHUB_BASE_REF"])
    candidates += ["origin/HEAD", "HEAD~1"]
    for c in candidates:
        try:
            return git(repo, "merge-base", c, "HEAD")
        except RuntimeError:
            continue
    raise RuntimeError("cannot determine the base commit; use actions/checkout with fetch-depth: 0 "
                       "or pass the base-ref input")


def filter_paths(findings: list[dict], root: str, include: list[str], exclude: list[str]) -> list[dict]:
    def rel(f: dict) -> str:
        return os.path.relpath(f["file"], root)

    def ok(f: dict) -> bool:
        r = rel(f)
        if include and not any(fnmatch.fnmatch(r, g) for g in include):
            return False
        return not any(fnmatch.fnmatch(r, g) for g in exclude)
    return [f for f in findings if ok(f)]


def summary_md(res: dict, findings: list[dict], root: str, mode: str, profile: str,
               failing: bool, threshold: str) -> str:
    n = len(findings)
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in ("error", "warning", "note")}
    tools = ", ".join(f"{t['tool']} {t['version']}" if t["available"] else f"{t['tool']} (missing)"
                      for t in res.get("tools", []))
    out = [f"## SEI CERT review ({mode} mode, profile `{profile}`)", "",
           f"**{n} finding(s)**: {counts['error']} error, {counts['warning']} warning, {counts['note']} note"
           f" in {len(res.get('files', []))} file(s). Tools: {tools}.", ""]
    if failing:
        out += [f"> Failing: at least one finding is at or above `{threshold}`.", ""]
    if n:
        out += ["| Rule | Severity | Location | Message | Found by |", "|---|---|---|---|---|"]
        for f in findings[:100]:
            msg = f["message"].strip().replace("|", "\\|").replace("\n", " ")[:160]
            out.append(f"| [{f['rule_id']}]({f.get('url')}) | {f['severity']} | "
                       f"`{os.path.relpath(f['file'], root)}:{f['line']}` | {msg} | "
                       f"`{f['tool']}:{f['checker']}` |")
        if n > 100:
            out.append(f"\n_{n - 100} more in the SARIF file._")
    else:
        out.append("No findings.")
    parse_err = sum(len(t.get("files_with_errors", [])) for t in res.get("tools", []))
    if parse_err:
        out += ["", f"_{parse_err} file(s) had compile errors and were only partly analysed; "
                    "pass `compile-commands` for accurate results._"]
    return "\n".join(out) + "\n"


def post_review(payload: dict, repo: str, pr: int, token: str, api_url: str) -> None:
    req = urllib.request.Request(
        f"{api_url}/repos/{repo}/pulls/{pr}/reviews", data=json.dumps(payload).encode(),
        method="POST", headers={"Authorization": f"Bearer {token}",
                                "Accept": "application/vnd.github+json",
                                "X-GitHub-Api-Version": "2022-11-28",
                                "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        r.read()


def set_output(name: str, value: str) -> None:
    p = os.environ.get("GITHUB_OUTPUT")
    if p:
        with open(p, "a", encoding="utf-8") as fh:
            fh.write(f"{name}={value}\n")


def main() -> int:
    ws = os.environ.get("GITHUB_WORKSPACE") or os.getcwd()
    working = inp("working-directory", ".")
    root = str(Path(ws, working).resolve())
    subprocess.run(["git", "config", "--global", "--add", "safe.directory", root], capture_output=True)
    ev = event()
    profile = inp("profile", "default")
    is_pr = os.environ.get("GITHUB_EVENT_NAME", "").startswith("pull_request")
    mode = inp("mode", "diff" if is_pr or inp("base-ref") else "full").lower()
    include, exclude = split_globs(inp("include")), split_globs(inp("exclude"))
    compdb = inp("compile-commands") or None
    if compdb:
        compdb = str(Path(root, compdb).resolve())
        if compdb.endswith("compile_commands.json"):
            compdb = str(Path(compdb).parent)
    tools = [t.strip() for t in inp("tools", "clang-tidy,cppcheck").split(",") if t.strip()]
    min_conf = float(inp("min-confidence", "0.5"))
    threshold = inp("fail-on", "never").lower()
    sarif_path = str(Path(root, inp("sarif-file", "cert-review.sarif")))

    try:
        if mode == "diff":
            base = resolve_base(root, inp("base-ref"), ev)
            head = (ev.get("pull_request") or {}).get("head", {}).get("sha")
            try:
                head = head if head and git(root, "cat-file", "-t", head) == "commit" else None
            except RuntimeError:
                head = None
            res = api.check_diff(root, base, head or "HEAD", None, profile, compdb, tools, min_conf)
        elif mode == "full":
            paths = [str(Path(root, p)) for p in split_globs(inp("paths", "."))]
            res = api.check_file(paths, profile, None, compdb, root, tools, min_conf)
        else:
            log("error", f"mode must be diff or full, got {mode!r}")
            return 2
    except Exception as e:                       # report, do not hide, a setup problem
        log("error", f"cert-review failed: {e}")
        return 2

    findings = filter_paths(res["findings"], root, include, exclude)
    failing = threshold != "never" and any(SEV[f["severity"]] >= SEV[threshold] for f in findings)

    Path(sarif_path).write_text(json.dumps(formatters.to_sarif(findings, root)), encoding="utf-8")
    md = summary_md(res, findings, root, mode, profile, failing, threshold)
    summ = os.environ.get("GITHUB_STEP_SUMMARY")
    if summ:
        with open(summ, "a", encoding="utf-8") as fh:
            fh.write(md)
    else:
        print(md)
    for f in findings[:50]:        # workflow annotations (also visible without code scanning)
        lvl = {"error": "error", "warning": "warning", "note": "notice"}[f["severity"]]
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::{lvl} file={os.path.relpath(f['file'], root)},line={f['line']},"
                  f"title=CERT {f['rule_id']}::{f['message'].strip()[:200]}")
    set_output("sarif-file", sarif_path)
    set_output("findings", str(len(findings)))
    set_output("errors", str(sum(1 for f in findings if f["severity"] == "error")))

    if truthy(inp("review-comments", "false")):
        token = inp("github-token")
        pr = (ev.get("pull_request") or {}).get("number")
        repo = os.environ.get("GITHUB_REPOSITORY")
        fork = (ev.get("pull_request") or {}).get("head", {}).get("repo", {}).get("fork")
        if not (token and pr and repo):
            log("warning", "review-comments needs github-token and a pull_request event; skipped")
        elif fork:
            log("warning", "pull request comes from a fork (read-only token); review comments skipped")
        elif findings:
            limit = int(inp("max-comments", "30"))
            top = sorted(findings, key=lambda f: (-SEV[f["severity"]], -f["priority"], -f["confidence"]))[:limit]
            payload = formatters.to_github_review(
                top, root, f"SEI CERT review: {len(findings)} finding(s)"
                + (f", showing the {limit} most important" if len(findings) > limit else "")
                + ". Posted by the cert-review action.")
            try:
                post_review(payload, repo, int(pr), token,
                            os.environ.get("GITHUB_API_URL", "https://api.github.com"))
                log("notice", f"posted a review with {len(top)} comment(s)")
            except urllib.error.HTTPError as e:
                log("warning", f"could not post the review: HTTP {e.code} {e.read()[:200]!r}")
            except Exception as e:
                log("warning", f"could not post the review: {e}")
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
