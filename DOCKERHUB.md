# cert-review-mcp

An MCP server that reviews C and C++ code against the SEI CERT C and C++ coding standards.
It runs clang-tidy, cppcheck and Semgrep (bundled CERT rules), maps their findings to CERT rules, and gives MCP clients
tools to look up rules, check files or a diff, and build a review packet.

Source, documentation and changelog: [github.com/RaminNietzsche/cert-review-mcp](https://github.com/RaminNietzsche/cert-review-mcp)

## What is in the image

- `cert-review-mcp`, the MCP server over stdio (the entrypoint)
- the `cert-review` CLI
- clang 19, clang-tidy 19, cppcheck and Semgrep 1.186.0

Platforms: `linux/amd64`, `linux/arm64`. Tags: `latest` and one per release, such as `1.1.1`.

## Tools

All tools are read-only and never write to the project.

| Tool | What it does |
|---|---|
| `list_rules` | List CERT rules, filtered by language, category, kind, level or coverage |
| `get_rule` | Full details for one rule, such as `EXP33-C` |
| `search_rules` | Search rule titles and text |
| `check_files` | Run the analyzers on files and return CERT-mapped findings (optionally only those not in a baseline) |
| `check_diff` | Same, limited to lines changed in a git diff |
| `explain_finding` | Explain one finding and suggest a fix from the rule's compliant example |
| `build_review_packet` | Diff plus the rules worth checking by hand, for a reviewer |
| `validate_findings` | Check findings against the rule catalog |
| `get_rule_coverage` | Count rules by how they can be checked |
| `format_findings` | Render findings as Markdown, GitHub or GitLab review comments, SARIF or Code Quality JSON |

## Use it from an MCP client

Mount the project at the same absolute path inside the container, because the tools take
host paths:

```json
{
  "mcpServers": {
    "cert-review": {
      "command": "docker",
      "args": ["run", "-i", "--rm",
               "-v", "/home/me/proj:/home/me/proj:ro",
               "raminnietzsche/cert-review-mcp:latest"]
    }
  }
}
```

Claude Code:

```bash
claude mcp add cert-review -- docker run -i --rm -v "$PWD:$PWD:ro" raminnietzsche/cert-review-mcp:latest
```

Keep `-i` and do not add `-t`; a TTY corrupts the JSON-RPC stream. A `compile_commands.json`
must be visible at the path it names, and its include paths must exist in the container.

## Use the CLI

```bash
docker run --rm -v "$PWD:$PWD" -w "$PWD" --entrypoint cert-review \
  raminnietzsche/cert-review-mcp:latest \
  diff --repo "$PWD" --base origin/main --format markdown
```

More: [Docker guide](https://github.com/RaminNietzsche/cert-review-mcp/blob/main/docs/docker.md).

License: Apache-2.0.
