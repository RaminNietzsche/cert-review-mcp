"""MCP server (stdio) exposing the CERT rule database and review engine.

Nothing here posts to GitHub or GitLab: review comments are only formatted.
"""
from __future__ import annotations

import json
from typing import Any

from . import api
from . import profiles as P
from . import rules as R

try:                                   # mcp >= 2
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:                    # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

INSTRUCTIONS = """\
SEI CERT C/C++ review tools. Typical flow:
1. check_file or check_diff for deterministic findings (clang-tidy, Clang Static
   Analyzer, cppcheck mapped to CERT rule IDs).
2. review_packet for the code the tools cannot judge; review it yourself against
   the supplied rule texts and return findings that each cite a rule ID and quote
   the rule.
3. validate_findings to drop anything ungrounded, then format_review.
Never post review comments without the user approving the exact text.
Use profile "ceph" for Ceph source trees."""


def build_server() -> Any:
    mcp = _Server("cert-review", instructions=INSTRUCTIONS)

    @mcp.tool()
    def list_rules(lang: str | None = None, category: str | None = None, kind: str | None = None,
                   level: str | None = None, detectable: bool | None = None,
                   coverage: str | None = None, limit: int = 200) -> dict:
        """List CERT rules. lang: c|cpp; category: 3-letter code (EXP, MEM...); kind: rule|recommendation;
        level: L1|L2|L3; detectable: CERT's own Detectable flag; coverage: deterministic|partial|llm-only."""
        return api.list_rules(lang, category, kind, level, detectable, coverage, limit)

    @mcp.tool()
    def explain_rule(id: str, profile: str = "default") -> dict:
        """Full text, examples, risk row, CWE, detection tools and profile notes for one rule (e.g. EXP34-C)."""
        return api.explain_rule(id, profile)

    @mcp.tool()
    def search_rules(query: str, limit: int = 10, lang: str | None = None) -> dict:
        """Keyword search over rule titles, text and examples."""
        return api.search_rules(query, limit, lang)

    @mcp.tool()
    def check_file(path: str, profile: str = "default", lang: str | None = None,
                   compdb: str | None = None, root: str | None = None,
                   tools: list[str] | None = None, min_confidence: float = 0.0,
                   include_suppressed: bool = False) -> dict:
        """Run static analysis on a file or directory and return findings mapped to CERT rule IDs.
        compdb: directory holding compile_commands.json (recommended); tools: any of clang-tidy, clangsa, cppcheck."""
        return api.check_file(path, profile, lang, compdb, root, tools, min_confidence, include_suppressed)

    @mcp.tool()
    def check_diff(repo: str | None = None, base: str | None = None, head: str | None = None,
                   diff_text: str | None = None, profile: str = "default", compdb: str | None = None,
                   tools: list[str] | None = None, min_confidence: float = 0.0,
                   include_suppressed: bool = False) -> dict:
        """Like check_file but only reports findings on changed lines of git base..head
        (head omitted = working tree), or of a pasted unified diff."""
        return api.check_diff(repo, base, head, diff_text, profile, compdb, tools,
                              min_confidence, include_suppressed)

    @mcp.tool()
    def review_packet(path: str | None = None, repo: str | None = None, base: str | None = None,
                      head: str | None = None, diff_text: str | None = None, profile: str = "default",
                      run_static: bool = True, max_rules_per_hunk: int | None = None) -> dict:
        """Build the LLM review packet: code hunks plus the rule texts most relevant to them
        (chosen by deterministic token/API heuristics), skipping rules a checker already covers."""
        return api.review_packet(path, repo, base, head, diff_text, profile, run_static,
                                 None, max_rules_per_hunk)

    @mcp.tool()
    def validate_findings(findings_json: str, packet_json: str | None = None,
                          profile: str = "default") -> dict:
        """Check LLM findings: each must cite an existing rule ID and quote that rule's text
        (>= 20 chars), and fall inside the packet. Returns accepted and rejected with reasons."""
        pk = json.loads(packet_json) if packet_json else None
        return api.validate_findings(findings_json, pk, profile)

    @mcp.tool()
    def rule_coverage(lang: str | None = None, kind: str | None = None, include_ids: bool = False) -> dict:
        """How many rules are deterministic / partial / llm-only, for all upstream mappings and
        for the checkers installed in this toolchain."""
        return api.rule_coverage(lang, kind, include_ids)

    @mcp.tool()
    def format_review(findings_json: str, style: str = "markdown", root: str | None = None) -> Any:
        """Format findings as github (PR review payload), gitlab (MR discussions), sarif or markdown.
        Formatting only; nothing is posted."""
        return api.format_review(findings_json, style, root)

    @mcp.resource("rule://{rule_id}", mime_type="text/markdown")
    def rule_resource(rule_id: str) -> str:
        r = R.get(rule_id)
        if r is None:
            raise ValueError(f"unknown rule {rule_id}")
        return R.rule_text(r) + f"\n\nSource: {r['url']}\n"

    @mcp.resource("profile://{name}", mime_type="text/yaml")
    def profile_resource(name: str) -> str:
        from .paths import profiles_dir
        p = profiles_dir() / f"{name}.yaml"
        if not p.exists():
            raise ValueError(f"unknown profile {name}; available: {P.available()}")
        return p.read_text(encoding="utf-8")

    @mcp.prompt()
    def cert_review(target: str = "the current change", profile: str = "default") -> str:
        """Review code against SEI CERT C/C++."""
        return _prompt(target, profile, ceph=False)

    @mcp.prompt()
    def ceph_review(target: str = "the current change") -> str:
        """Review Ceph code against SEI CERT with Ceph idioms taken into account."""
        return _prompt(target, "ceph", ceph=True)

    return mcp


def _prompt(target: str, profile: str, ceph: bool) -> str:
    extra = ("Ceph context: ceph_assert is always active but is for invariants, not input validation; "
             "dout/ldout are stream based; locks are ceph::mutex (lockdep); RefCountedObject uses "
             "intrusive refs; crimson/asio callbacks outlive their frames. Read the profile://ceph "
             "resource for details.\n") if ceph else ""
    return (f"Review {target} against the SEI CERT C and C++ standards using the cert-review tools "
            f"(profile '{profile}').\n{extra}"
            "1. Call check_diff (or check_file) and keep findings with confidence >= 0.5.\n"
            "2. Call review_packet. For each hunk, read the candidate rules and decide whether the code "
            "really violates one. Prefer no finding over a speculative one.\n"
            "3. Return findings as JSON [{rule_id, file, line, message, quote, fix}], where quote is copied "
            "verbatim from the rule text, then call validate_findings and drop rejected ones.\n"
            "4. Draft comments with format_review (style github, gitlab or markdown). Show the exact text "
            "to the user and wait for approval; never post anything yourself.")


def main() -> None:
    build_server().run(transport="stdio")


if __name__ == "__main__":
    main()
