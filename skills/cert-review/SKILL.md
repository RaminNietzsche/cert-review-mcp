---
name: cert-review
description: Reviews C and C++ code against the SEI CERT C and C++ Coding Standards using the cert-review MCP tools. Runs clang-tidy, the Clang Static Analyzer and cppcheck mapped to CERT rule IDs, then reviews the code those tools cannot judge against the rule text, citing a rule ID and quoting the rule for every finding. Drafts review comments with severity, a compliant fix and a link. Use for "check this against CERT", "review this diff for security rules", "does this violate MEM/EXP/ARR/STR/INT/CON/ERR rules", or before opening a PR or MR for C/C++.
compatibility: Needs the cert-review MCP server (or the cert-review CLI), Python 3.11+, git, and clang-tidy, clang and cppcheck for the static layer. A compile_commands.json makes results far more accurate.
license: Apache-2.0
---

# cert-review: SEI CERT C/C++ review

Every comment drafted here is shown to the human first. **Never post to GitHub,
GitLab or any tracker without the human approving the exact text**, and read the
post back afterwards. Drafting and formatting are free; posting is not.

## Tools

| Tool | Use |
|---|---|
| `check_diff` | Static findings on the changed lines of `base..head`, the working tree, or a pasted diff |
| `format_pr_review` | One markdown PR comment: static summary + heuristic hints + style nits (after check_diff + build_review_packet) |
| `check_files` | Static findings for a file or directory |
| `explain_finding` | One finding: why it matches, the closest CERT example pair and a fix to put in `fix` |
| `build_review_packet` | Code hunks plus the rule texts worth reading, for rules no checker covers |
| `validate_findings` | Rejects findings without a real rule ID or a verbatim rule quote |
| `format_findings` | Markdown, GitHub review, GitLab discussions, SARIF or GitLab reports (formatting only) |
| `get_rule`, `search_rules`, `list_rules`, `get_rule_coverage` | Look rules up |

## Procedure

1. **Scope.** Prefer the diff (`check_diff`). Whole-file review is for new files.
   Pass `compdb` (a directory with `compile_commands.json`) whenever one exists.
   Choose the profile: `ceph` for Ceph trees, otherwise `default`.
2. **Static layer.** Run `check_diff`/`check_files`. Treat findings with
   `confidence >= 0.5` as leads, not verdicts: open the code and confirm. Findings
   from a rule-specific checker (`cert-*`) are the most reliable; findings from
   general analyzers mapped to a rule need a sanity check. See
   [references/false-positives.md](references/false-positives.md).
   If the repository has a `.cert-review-baseline.json`, pass it as `baseline_path`
   so only new findings are reviewed. Use `explain_finding` to draft the fix for a
   confirmed finding.
3. **Manual layer.** Call `build_review_packet` (`run_static: false` if step 2 already ran). For each hunk read the candidate rules'
   texts and decide whether the code really violates one. Follow
   [references/judging-llm-only-rules.md](references/judging-llm-only-rules.md).
   Silence is better than a speculative finding.
4. **Ground every finding.** Each finding is
   `{rule_id, file, line, message, quote, fix}` where `quote` is copied verbatim
   (at least 20 characters) from that rule's text. Run `validate_findings`;
   drop what it rejects instead of rewording the quote to fit. Pass the packet
   too, so findings outside its hunks are rejected.
5. **Draft.** Use `format_findings` (pass the `warnings` from step 2) and the template in
   [references/comment-template.md](references/comment-template.md). Show the
   exact text to the human, with the file and line each comment attaches to.
6. **Wait.** Only after the human approves the exact text, and names the target
   PR or MR, post it by whatever means they authorise.

## Rules that save rework

- **Cite, don't paraphrase.** A finding without a valid CERT ID and a quote from
  that rule is noise; the validator will reject it.
- **Rules versus recommendations.** Rules (e.g. EXP34-C) are the default scope.
  Recommendations (e.g. EXP00-C) are advisory; report them only when asked.
- **C rules in C++ files.** The C++ standard has no recommendations and fewer
  rules; C rules (STR31-C, ERR33-C, ...) still apply to C-style code in C++ files,
  but prefer the C++ counterpart (STR50-CPP, ERR50-CPP...) when one exists.
- **Severity comes from the CERT risk row** (High/Medium/Low), possibly tuned by
  the profile. Do not invent a severity.
- **One finding per root cause.** If one defect breaks MEM30-C and MEM50-CPP,
  report the better fit once.
- **Verify before you assert.** Open the code around the line; check for an
  early return, a NULL check, a size bound or an RAII owner that makes the
  finding moot.
- **Suppressions are explicit.** `// cert-review: ignore RULE-ID reason` on the
  line or the line above silences one rule; do not add it to code you are
  reviewing unless the human asks.
