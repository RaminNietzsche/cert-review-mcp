"""MCP server (stdio) exposing the SEI CERT rule database and review engine.

Nothing here writes files, uses the network, or posts to GitHub or GitLab:
review comments are only formatted.
"""
from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from mcp.types import ToolAnnotations

from . import api
from . import profiles as P
from . import rules as R

try:                                   # mcp >= 2
    from mcp.server.mcpserver import MCPServer as _Server
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError:                    # mcp 1.x (>= 1.10 for title/annotations/structured output)
    from mcp.server.fastmcp import FastMCP as _Server
    from mcp.server.fastmcp.exceptions import ToolError

SERVER_NAME = "cert-review"
WEBSITE = "https://github.com/RaminNietzsche/cert-review-mcp"

INSTRUCTIONS = """\
SEI CERT C/C++ secure-coding review for local source trees. Every tool only reads local
files and bundled data and runs local analyzers (clang-tidy, clang, cppcheck); nothing is
written, uploaded or posted.
Rule lookup: list_rules (structured filters), search_rules (keywords), get_rule (one rule's
full text), get_rule_coverage (what checkers can detect).
Review flow:
1. check_diff for a change, or check_files for whole files or directories.
2. build_review_packet for rules no checker decides; judge each hunk and write findings
   that cite a candidate rule_id and quote that rule's text verbatim.
3. validate_findings to drop ungrounded findings.
4. format_findings to draft markdown, GitHub or GitLab review payloads, SARIF or GitLab reports.
Use absolute paths and profile "ceph" for Ceph trees. A tool status "partial" or non-empty
warnings means some files did not compile, so a clean result is not proof.
Never post review comments without the user approving the exact text."""

# ---------------------------------------------------------------- shared types
Profile = Annotated[str, Field(
    description="Review profile: 'default' (plain SEI CERT), 'ceph' (Ceph severities, "
                "suppressions and idioms) or an absolute path to a profile .yaml file.",
    examples=["default", "ceph"])]
RuleId = Annotated[str, Field(
    description="SEI CERT rule ID: three-letter category, two digits, then -C or -CPP; "
                "case-insensitive.",
    pattern=r"^[A-Za-z]{3}\d{2}-(?:[Cc]|[Cc][Pp][Pp])$", examples=["EXP34-C", "MEM50-CPP"])]
Tool = Literal["clang-tidy", "clangsa", "cppcheck"]
ALL_TOOLS: list[str] = ["clang-tidy", "clangsa", "cppcheck"]
Tools = Annotated[list[Tool], Field(
    description="Analyzers to run. clang-tidy = clang-tidy cert-*/bugprone checks plus Clang "
                "Static Analyzer checks; clangsa = standalone `clang --analyze` (adds alpha "
                "checkers); cppcheck = cppcheck. Missing binaries are skipped and reported.",
    min_length=1, json_schema_extra={"uniqueItems": True})]
MinConfidence = Annotated[float, Field(
    ge=0.0, le=1.0,
    description="Drop findings below this confidence. Rule-specific checkers score 0.9, "
                "general checkers 0.3-0.65, +0.1 when two tools agree. 0.5 keeps most real hits.")]
IncludeSuppressed = Annotated[bool, Field(
    description="Also return findings hidden by the profile or by `// cert-review: ignore "
                "<RULE>` comments, each with its suppression reason (for audits).")]
Compdb = Annotated[str | None, Field(
    description="Absolute path of the directory that contains compile_commands.json. Strongly "
                "recommended: without it files are compiled with guessed flags and often fail "
                "to parse. Omitted: auto-detected in root, root/build or root/build-clang.",
    examples=["/home/me/ceph/build"])]
LANGS = Literal["any", "c", "cpp"]
CATEGORY = Literal["any", "API", "ARR", "CON", "CTR", "DCL", "ENV", "ERR", "EXP", "FIO", "FLP",
                   "INT", "MEM", "MSC", "OOP", "POS", "PRE", "SIG", "STR", "WIN"]


def _opt(v: str) -> str | None:
    return None if v == "any" else v


# ---------------------------------------------------------------- output models
class _Out(BaseModel):
    model_config = ConfigDict(extra="allow")


class RuleList(_Out):
    count: int = Field(description="Number of rules matching the filters, before `limit`.")
    truncated: bool = Field(description="True when count > limit and `rules` was cut.")
    rules: list[dict[str, Any]] = Field(description=(
        "Rule summaries: id, title, lang (c|cpp), kind (rule|recommendation), category, "
        "severity, likelihood, priority (P1-P27), level (L1-L3), detectable, url, coverage "
        "(tier over all mappings), coverage_runnable (tier with the pinned toolchain)."))


class SearchResult(_Out):
    query: str = Field(description="The query as received.")
    results: list[dict[str, Any]] = Field(description=(
        "Best match first. Same summary fields as list_rules (without coverage) plus `score`."))


class RuleRecord(_Out):
    id: str = Field(description="Canonical rule ID, e.g. EXP34-C.")
    title: str
    lang: str = Field(description="c or cpp.")
    kind: str = Field(description="rule or recommendation.")
    category: str = Field(description="Three-letter category code.")
    url: str = Field(description="Rule page on the SEI CERT site.")
    cwe: list[str] = Field(description="Related CWE IDs.")
    risk: dict[str, Any] | None = Field(description=(
        "CERT risk assessment: severity, likelihood, remediation, priority, level, "
        "detectable, repairable."))
    text: str = Field(description="Rule text as markdown; examples included unless include_examples=false. "
                                  "Copy `quote` values for validate_findings from here.")
    examples: list[dict[str, Any]] = Field(description="Noncompliant/compliant example pairs; [] when include_examples=false.")
    coverage: dict[str, Any] = Field(description="tier, tier_runnable and checkers[] {tool, checker, specific, available}.")
    profile: dict[str, Any] = Field(description="name, override (severity/priority/note), disabled reason or null, idioms[].")


class Finding(_Out):
    rule_id: str = Field(description="SEI CERT rule ID.")
    file: str = Field(description="Absolute path of the file.")
    line: int = Field(description="1-based line.")
    severity: Literal["error", "warning", "note"]
    message: str = Field(description="Analyzer message.")
    confidence: float = Field(description="0-1.")


class CheckResult(_Out):
    profile: str = Field(description="Profile used.")
    files: list[str] = Field(description="Files analysed (absolute paths).")
    findings: list[Finding] = Field(description=(
        "Sorted by severity, priority, confidence. Each also has lang, col, priority, level, "
        "tool, checker, title, cert_severity, also_found_by[], note, url."))
    tools: list[dict[str, Any]] = Field(description=(
        "Per analyzer: tool, available, version, files, raw_findings, parse_errors, "
        "files_with_errors[], notes[], status ('ok' | 'partial' = some files did not compile | 'missing')."))
    warnings: list[str] = Field(description="One line per analyzer that could not fully parse its input; non-empty means the result is incomplete.")
    notes: list[str] = Field(description="Engine notes, e.g. 'no C/C++ files selected'.")
    suppressed_count: int = Field(description="Findings hidden by the profile or inline ignores.")
    summary: dict[str, Any] = Field(description="total, by_severity {error, warning, note}, top_rules [[rule_id, count], ...].")


class DiffCheckResult(CheckResult):
    changed_files: list[str] = Field(description="Every file in the diff, relative to root, including non-C/C++ files that were skipped.")
    root: str = Field(description="Absolute repository root used to resolve diff paths.")


class Packet(_Out):
    instructions: str = Field(description="How to review the hunks and what makes a finding acceptable.")
    finding_schema: dict[str, Any] = Field(description="Fields each finding must have: rule_id, file, line, message, quote; optional severity, fix, confidence.")
    profile: str
    hunks: list[dict[str, Any]] = Field(description=(
        "file (absolute), start_line, end_line, code (line-numbered), idioms[] {id, hint}, "
        "candidate_rules[] {rule_id, title, tier, matched, severity, priority, level, "
        "profile_note, text (<= 3500 chars), url}, existing_findings[] {rule_id, line, checker}."))
    skipped_hunks: list[Any] = Field(description="[file, start_line, end_line] of hunks with no candidate rule.")
    static_findings: list[dict[str, Any]] = Field(description="Analyzer findings for the same scope; [] when run_static=false.")
    rule_database: str = Field(description="Commit of the bundled rule database.")


class Validation(_Out):
    accepted: list[dict[str, Any]] = Field(description="Grounded findings in the check_files finding shape plus quote and fix; pass to format_findings.")
    rejected: list[dict[str, Any]] = Field(description="{finding, reasons[]} for each rejected finding.")
    summary: dict[str, int] = Field(description="{accepted, rejected} counts.")


class Coverage(_Out):
    total: int = Field(description="Rules counted after the lang/kind filters.")
    all_mappings: dict[str, int] = Field(description="Counts per tier using every upstream checker mapping.")
    runnable_toolchain: dict[str, int] = Field(description="Counts per tier using only checkers available in the pinned toolchain.")
    toolchain: dict[str, str] = Field(description="Pinned analyzer versions the tiers were computed for.")
    definitions: dict[str, str] = Field(description="Meaning of deterministic, partial and llm-only.")
    sources: dict[str, Any] = Field(description="Upstream mapping sources and commits.")


# ---------------------------------------------------------------- input models
class FindingIn(BaseModel):
    """A finding written from a build_review_packet hunk."""
    model_config = ConfigDict(extra="allow")
    rule_id: str = Field(description="A rule_id from the hunk's candidate_rules, e.g. EXP34-C.")
    file: str = Field(description="Path exactly as in the hunk's `file` field.")
    line: int = Field(ge=1, description="Line inside that hunk's start_line..end_line.")
    message: str = Field(description="What is wrong in this code and why it violates the rule.")
    quote: str = Field(description="Verbatim passage (>= 20 characters) copied from that rule's text or examples.")
    severity: Literal["error", "warning", "note"] | None = Field(None, description="Overrides the rule's default severity.")
    fix: str | None = Field(None, description="Compliant replacement code.")
    confidence: float | None = Field(None, ge=0, le=1, description="Defaults to 0.5.")


class FindingOut(BaseModel):
    """A finding produced by check_files, check_diff or validate_findings."""
    model_config = ConfigDict(extra="allow")
    rule_id: str
    file: str
    line: int = Field(ge=1)
    severity: Literal["error", "warning", "note"]
    priority: int
    level: str
    message: str
    tool: str
    checker: str


class PacketIn(BaseModel):
    model_config = ConfigDict(extra="allow")
    hunks: list[dict[str, Any]] = Field(description="The packet's hunks; only file, start_line, end_line and candidate_rules[].rule_id are read.")


def _guard(fn):
    """Surface errors to the client: mcp 2.x hides messages of non-ToolError exceptions."""
    @functools.wraps(fn)
    def wrapper(*a, **kw):
        try:
            return fn(*a, **kw)
        except ToolError:
            raise
        except FileNotFoundError as e:
            raise ToolError(f"{e}. Available profiles: {P.available()}") from e
        except Exception as e:                      # noqa: BLE001
            raise ToolError(f"{type(e).__name__}: {e}") from e
    return wrapper


def _exists(path: str) -> str:
    p = Path(path).expanduser()
    if not p.exists():
        raise ToolError(f"path not found: {path} (relative paths resolve against the server's "
                        f"working directory {Path.cwd()}; pass an absolute path)")
    return str(p)


RO = dict(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)


def build_server() -> Any:
    kw: dict[str, Any] = {"instructions": INSTRUCTIONS}
    try:
        mcp = _Server(SERVER_NAME, website_url=WEBSITE, **kw)
    except TypeError:                               # older 1.x without website_url
        mcp = _Server(SERVER_NAME, **kw)

    # ------------------------------------------------------------ rule lookup
    @mcp.tool(
        title="List SEI CERT rules by filter",
        annotations=ToolAnnotations(title="List SEI CERT rules by filter", **RO),
        structured_output=True,
        description=(
            "List SEI CERT C/C++ rules and recommendations from the bundled database (388 "
            "entries), filtered by language, category, kind, risk level, CERT detectability or "
            "checker coverage. Use to enumerate rules by structured criteria, e.g. all L1 C++ "
            "rules no checker detects. Do not use for free-text lookup (use search_rules) or for "
            "one rule's text and examples (use get_rule). Reads bundled data only; fast, no "
            "analyzers run. Returns summaries without rule text; `count` is the total before "
            "`limit`, so raise limit or narrow filters when `truncated` is true."))
    @_guard
    def list_rules(
        lang: Annotated[LANGS, Field(description="c = SEI CERT C, cpp = SEI CERT C++.")] = "any",
        category: Annotated[CATEGORY, Field(description="Three-letter category, e.g. EXP expressions, MEM memory, INT integers, STR strings, CON concurrency.")] = "any",
        kind: Annotated[Literal["any", "rule", "recommendation"], Field(description="rule = normative rule; recommendation = advisory (C only).")] = "any",
        level: Annotated[Literal["any", "L1", "L2", "L3"], Field(description="CERT priority level; L1 is the most urgent.")] = "any",
        detectable: Annotated[bool | None, Field(description="CERT's own 'Detectable' flag (true = automatable in principle). Omit for both.")] = None,
        coverage: Annotated[Literal["any", "deterministic", "partial", "llm-only"], Field(description=(
            "Checker coverage tier: deterministic = a rule-specific checker exists; partial = only "
            "general checkers; llm-only = no checker, manual review needed. Matches either the "
            "all-mappings or the pinned-toolchain tier."))] = "any",
        limit: Annotated[int, Field(ge=1, le=400, description="Maximum summaries returned (each ~400 bytes).")] = 50,
    ) -> RuleList:
        return api.list_rules(_opt(lang), _opt(category), _opt(kind), _opt(level), detectable,
                              _opt(coverage), limit)

    @mcp.tool(
        title="Search SEI CERT rules by keyword",
        annotations=ToolAnnotations(title="Search SEI CERT rules by keyword", **RO),
        structured_output=True,
        description=(
            "Rank SEI CERT C/C++ rules by keyword relevance to a free-text query: API names "
            "(strcpy, malloc, pthread_mutex_lock), concepts (integer overflow) or a rule ID. Use "
            "when you know what the code does but not which rule applies. Do not use for "
            "structured filters (use list_rules) or to read a rule (use get_rule). Matching is "
            "case-insensitive term counting over titles, rule text and examples, not semantic "
            "search; 1-character tokens are ignored and a query with no usable token returns an "
            "empty list. Reads bundled data only; fast."))
    @_guard
    def search_rules(
        query: Annotated[str, Field(min_length=2, description="Keywords separated by spaces; title hits weigh 8x body hits.", examples=["strcpy buffer", "signal handler", "EXP34-C"])],
        limit: Annotated[int, Field(ge=1, le=50, description="Maximum results.")] = 10,
        lang: Annotated[LANGS, Field(description="Restrict to SEI CERT C (c) or C++ (cpp).")] = "any",
    ) -> SearchResult:
        return api.search_rules(query, limit, _opt(lang))

    @mcp.tool(
        title="Get one SEI CERT rule",
        annotations=ToolAnnotations(title="Get one SEI CERT rule", **RO),
        structured_output=True,
        description=(
            "Return the full record of one SEI CERT rule: text, noncompliant and compliant code "
            "examples, exceptions, CERT risk assessment, CWE IDs, the checkers that detect it, and "
            "how the chosen profile adjusts or disables it. Use before judging or explaining a "
            "finding, or to copy the verbatim `quote` that validate_findings requires. Do not use "
            "to discover rules (use search_rules or list_rules). Reads bundled data only. Records "
            "are large (median ~10 KB, up to ~80 KB); set include_examples=false for text and risk "
            "only. An unknown ID returns an error listing close matches."))
    @_guard
    def get_rule(
        rule_id: RuleId,
        profile: Profile = "default",
        include_examples: Annotated[bool, Field(description="Include code examples in `text` and `examples`.")] = True,
    ) -> RuleRecord:
        d = api.explain_rule(rule_id, profile)
        if "error" in d:
            raise ToolError(f"{d['error']}; did you mean: {', '.join(d['did_you_mean']) or 'none'}")
        if not include_examples:
            d["examples"] = []
            d["text"] = R.rule_text(R.get(rule_id), include_examples=False)
        return d

    @mcp.tool(
        title="Summarize SEI CERT checker coverage",
        annotations=ToolAnnotations(title="Summarize SEI CERT checker coverage", **RO),
        structured_output=True,
        description=(
            "Count SEI CERT rules per detection tier: deterministic (a rule-specific checker "
            "exists), partial (only general checkers map) and llm-only (no checker; manual review "
            "needed), both for all upstream checker mappings and for the pinned reference "
            "toolchain (clang-tidy and Clang Static Analyzer 19.1.7, cppcheck 2.17.1). Use to "
            "judge how much of a review static analysis can carry. Computed from bundled data; it "
            "does not probe the analyzers installed here (check_files reports those in tools[]). "
            "For one rule use get_rule; to list a tier's rules with titles use list_rules with "
            "`coverage`."))
    @_guard
    def get_rule_coverage(
        lang: Annotated[LANGS, Field(description="Count only SEI CERT C (c) or C++ (cpp) rules.")] = "any",
        kind: Annotated[Literal["any", "rule", "recommendation"], Field(description="Count only rules or only recommendations.")] = "any",
        include_ids: Annotated[bool, Field(description="Add rules_all_mappings and rules_runnable: rule ID lists per tier (~10 KB).")] = False,
    ) -> Coverage:
        return api.rule_coverage(_opt(lang), _opt(kind), include_ids)

    # ------------------------------------------------------------ analysis
    @mcp.tool(
        title="Check C/C++ files for SEI CERT violations",
        annotations=ToolAnnotations(title="Check C/C++ files for SEI CERT violations", **RO),
        structured_output=True,
        description=(
            "Run clang-tidy, the Clang Static Analyzer and cppcheck on a C/C++ file or a "
            "directory (recursive) and return every finding mapped to SEI CERT rule IDs. Use for "
            "whole-file or whole-tree audits; for a change set use check_diff, which keeps only "
            "changed lines. Runs the analyzers as local subprocesses (4 in parallel, 300 s "
            "timeout per file and tool) and writes no files. Takes under a second per small file "
            "but minutes for large trees. Pass `compdb` when the project has a compilation "
            "database; without it flags are guessed and project headers are often missing. A "
            "tools[].status of 'partial' or non-empty `warnings` means some files did not "
            "compile, so an empty result is not proof."))
    @_guard
    def check_files(
        path: Annotated[str, Field(description="Absolute path of a C/C++ file or a directory to scan recursively. Files are picked by the profile's extensions and exclude_paths.", examples=["/home/me/proj/src/buf.c", "/home/me/proj/src"])],
        profile: Profile = "default",
        compdb: Compdb = None,
        root: Annotated[str | None, Field(description="Absolute project root: adds root/src, root/include and similar as include paths, enables compdb auto-detection, and is the base for the profile's path globs.")] = None,
        lang: Annotated[LANGS, Field(description="Analyse only .c files (c) or only C++ files (cpp).")] = "any",
        tools: Tools = ALL_TOOLS,
        min_confidence: MinConfidence = 0.0,
        include_suppressed: IncludeSuppressed = False,
    ) -> CheckResult:
        return api.check_file(_exists(path), profile, _opt(lang), compdb, root, list(tools),
                              min_confidence, include_suppressed)

    @mcp.tool(
        title="Check changed C/C++ lines for SEI CERT violations",
        annotations=ToolAnnotations(title="Check changed C/C++ lines for SEI CERT violations", **RO),
        structured_output=True,
        description=(
            "Run the check_files analyzers on the C/C++ files of a change and keep only findings "
            "on added or modified lines. The change is `base`..`head` in the git repo at `repo`, "
            "`base` against the working tree when head is omitted, or a pasted unified diff "
            "(`diff_text`, paths relative to repo). Use for pull-request or pre-commit review; for "
            "whole files use check_files. Runs `git diff` and the analyzers locally; writes "
            "nothing. Files are read from disk, so the working tree must be at `head` or line "
            "numbers will not match. Check tools[].status and `warnings` before trusting an empty "
            "result."))
    @_guard
    def check_diff(
        repo: Annotated[str, Field(description="Absolute path of the git checkout; diff paths are resolved against it.", examples=["/home/me/ceph"])],
        base: Annotated[str | None, Field(description="Base git ref (branch, tag or SHA). Required unless diff_text is given.", examples=["origin/main", "HEAD~1"])] = None,
        head: Annotated[str | None, Field(description="Head git ref. Omit to compare base with the working tree (uncommitted changes included).")] = None,
        diff_text: Annotated[str | None, Field(description="Unified diff text (git diff format, a/ b/ prefixes allowed). Overrides base and head.")] = None,
        profile: Profile = "default",
        compdb: Compdb = None,
        tools: Tools = ALL_TOOLS,
        min_confidence: MinConfidence = 0.0,
        include_suppressed: IncludeSuppressed = False,
    ) -> DiffCheckResult:
        if not (diff_text or base):
            raise ToolError("provide base (git ref) or diff_text")
        return api.check_diff(_exists(repo), base, head, diff_text, profile, compdb, list(tools),
                              min_confidence, include_suppressed)

    # ------------------------------------------------------------ manual review layer
    @mcp.tool(
        title="Build a SEI CERT review packet",
        annotations=ToolAnnotations(title="Build a SEI CERT review packet", **RO),
        structured_output=True,
        description=(
            "Build a packet for reviewing code against SEI CERT rules that analyzers cannot "
            "decide: code hunks, each with up to max_rules_per_hunk candidate rules (picked by "
            "token/API heuristics and profile idioms, rules fully covered by a specific checker "
            "left out) and their text excerpts. Diff mode (`repo` plus `base` or `diff_text`): "
            "changed lines with 3 lines of context. Path mode (`path`): whole files. Hunks are cut "
            "into 60-line windows. Use after check_diff or check_files; judge each hunk, then send "
            "your findings to validate_findings. Read-only; run_static=true also runs the "
            "analyzers (same cost as check_diff/check_files) to mark lines already reported. "
            "Output is large, roughly 5-25 KB per hunk."))
    @_guard
    def build_review_packet(
        path: Annotated[str | None, Field(description="Path mode: absolute path of a file or directory. Ignored when diff mode applies.")] = None,
        repo: Annotated[str | None, Field(description="Diff mode: absolute path of the git checkout.")] = None,
        base: Annotated[str | None, Field(description="Diff mode: base git ref; required with repo unless diff_text is given.")] = None,
        head: Annotated[str | None, Field(description="Diff mode: head git ref; omit for the working tree.")] = None,
        diff_text: Annotated[str | None, Field(description="Diff mode: unified diff text, paths relative to repo.")] = None,
        profile: Profile = "default",
        run_static: Annotated[bool, Field(description="Also run the analyzers and list their findings per hunk so they are not repeated. Set false if you already ran check_diff/check_files.")] = True,
        compdb: Compdb = None,
        max_rules_per_hunk: Annotated[int | None, Field(ge=1, le=20, description="Candidate rules per hunk. Omit to use the profile's value (6 in both bundled profiles).")] = None,
    ) -> Packet:
        if not (path or (repo and base) or diff_text):
            raise ToolError("provide path, or repo with base or diff_text")
        if repo:
            _exists(repo)
        elif path:
            path = _exists(path)
        return api.review_packet(path, repo, base, head, diff_text, profile, run_static, compdb,
                                 max_rules_per_hunk)

    @mcp.tool(
        title="Validate manual SEI CERT findings",
        annotations=ToolAnnotations(title="Validate manual SEI CERT findings", **RO),
        structured_output=True,
        description=(
            "Accept or reject findings written from a build_review_packet review, with reasons. "
            "A finding passes only if its rule_id exists (C++ rules are rejected on .c files), "
            "its quote is a passage of 20+ characters found in that rule's text or examples "
            "(case, whitespace, curly quotes and markdown are normalised), it has a file, a line "
            ">= 1 and a message, and the profile does not disable the rule. With `packet`, the "
            "line must also fall inside a hunk whose candidate_rules include the rule. Use on "
            "every manual finding before format_findings; check_files and check_diff output needs "
            "no validation. Pure computation on the arguments; reads no files."))
    @_guard
    def validate_findings(
        findings: Annotated[list[FindingIn], Field(description="Findings to check; an empty list is valid.")],
        packet: Annotated[PacketIn | None, Field(description="The build_review_packet result (or just {hunks}) to enforce hunk and candidate-rule bounds. Strongly recommended.")] = None,
        profile: Profile = "default",
    ) -> Validation:
        items = [f.model_dump(exclude_none=True) for f in findings]
        pk = packet.model_dump() if packet else None
        return api.validate_findings(items, pk, profile)

    @mcp.tool(
        title="Format SEI CERT findings as a report",
        annotations=ToolAnnotations(title="Format SEI CERT findings as a report", **RO),
        description=(
            "Render findings as a report or review payload without sending it. style: markdown "
            "(string); github (object for POST /repos/{owner}/{repo}/pulls/{n}/reviews, event "
            "COMMENT, one comment per finding); gitlab (array of merge-request discussion bodies; "
            "position SHAs are placeholders to fill from diff_refs); sarif (SARIF 2.1.0 object); "
            "codequality (GitLab Code Quality array); gitlab-sast (GitLab SAST report object). "
            "Use as the last step, then show drafted comments to the user before anyone posts "
            "them. Pass findings unchanged from check_files/check_diff `findings` or "
            "validate_findings `accepted`. Pure formatting: no files, network or posting."))
    @_guard
    def format_findings(
        findings: Annotated[list[FindingOut], Field(description="Findings exactly as returned by check_files, check_diff (findings) or validate_findings (accepted).")],
        style: Annotated[Literal["markdown", "github", "gitlab", "sarif", "codequality", "gitlab-sast"], Field(description="Output format; see the tool description for each shape.")] = "markdown",
        root: Annotated[str | None, Field(description="Absolute repository root; file paths in the output are made relative to it. Omit and paths become relative to the server's working directory.")] = None,
        warnings: Annotated[list[str] | None, Field(description="`warnings` from check_files/check_diff; shown as a partial-analysis notice in markdown, github and sarif.")] = None,
    ) -> Any:
        from . import formatters
        items = [f.model_dump() for f in findings]
        return formatters.format_review(items, style, root, warnings)

    # ------------------------------------------------------------ resources and prompts
    @mcp.resource("rule://{rule_id}", mime_type="text/markdown")
    def rule_resource(rule_id: str) -> str:
        """Text of one SEI CERT rule as markdown, e.g. rule://EXP34-C."""
        r = R.get(rule_id)
        if r is None:
            raise ValueError(f"unknown rule {rule_id}")
        return R.rule_text(r) + f"\n\nSource: {r['url']}\n"

    @mcp.resource("profile://{name}", mime_type="text/yaml")
    def profile_resource(name: str) -> str:
        """YAML of a bundled review profile, e.g. profile://ceph."""
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
            "1. Call check_diff (or check_files) and keep findings with confidence >= 0.5. If any tool "
            "status is 'partial', say which files were not fully analysed.\n"
            "2. Call build_review_packet with run_static=false. For each hunk, read the candidate rules "
            "and decide whether the code really violates one. Prefer no finding over a speculative one.\n"
            "3. Write findings as [{rule_id, file, line, message, quote, fix}], where quote is copied "
            "verbatim from the rule text, then call validate_findings with the packet and drop rejected ones.\n"
            "4. Draft comments with format_findings (style github, gitlab or markdown). Show the exact text "
            "to the user and wait for approval; never post anything yourself.")


def main() -> None:
    build_server().run(transport="stdio")


if __name__ == "__main__":
    main()
