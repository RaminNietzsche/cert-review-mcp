# Changelog

## Unreleased

### Added

- `explain_finding` MCP tool and `cert-review explain-finding` command: for one finding, the rule
  summary, why the finding matches (checker mapping, APIs, shared identifiers), the rule's
  noncompliant/compliant example pair closest to the flagged code, a diff between the two and
  concrete fix steps. Deterministic and offline. The server now has 10 tools.
- Baselines: `cert-review baseline create|update` writes `.cert-review-baseline.json` with
  line-number-free fingerprints (rule, file, hash of the normalized line, hash of its
  neighbours). `--baseline FILE` on `check` and `diff`, `baseline_path` on the `check_files` and
  `check_diff` tools, the Action's `baseline` input (and `baselined` output) and the GitLab
  template's `CERT_REVIEW_BASELINE` report only new findings and count baselined and fixed
  ones. See `docs/baseline.md`.

## 1.1.2 (2026-11-21)

### Added

- `server.json` for the official MCP Registry: `io.github.RaminNietzsche/cert-review-mcp`,
  OCI package `docker.io/raminnietzsche/cert-review-mcp`.
- `Dockerfile.mcp` sets the `io.modelcontextprotocol.server.name` label that the registry uses
  to verify image ownership.
- `mcp-registry` workflow: after a release image is pushed, publishes `server.json` to the
  registry with GitHub OIDC (no stored token).

No changes to the tools, the CLI or the GitHub Action.

## 1.1.1 (2026-11-21)

### Fixed

- `check_diff` and `build_review_packet` with `diff_text` now materialize missing files from the
  patch instead of returning empty results when the MCP host cannot see the local checkout (e.g.
  remote/Glama servers with a placeholder `repo` path).
- MCP `check_diff` no longer requires `repo` to exist on disk when `diff_text` is provided.

## 1.1.0 (2026-11-21)

### Breaking changes for MCP clients

The CLI (`cert-review ...`), the GitHub Action and the GitLab CI templates are unchanged.
Only clients that call the MCP tools by name need updating.

| Before | After |
|---|---|
| `explain_rule(id, ...)` | `get_rule(rule_id, ...)` |
| `rule_coverage` | `get_rule_coverage` |
| `check_file` | `check_files` |
| `review_packet` | `build_review_packet` |
| `format_review` | `format_findings` |
| `list_rules`, `search_rules`, `check_diff`, `validate_findings` | unchanged names |

- `validate_findings` takes `findings` (JSON array) and `packet` (JSON object) instead of the
  `findings_json` and `packet_json` strings. `format_findings` takes `findings` as an array.
- `check_diff` requires `repo`; git refs and `diff_text` paths are resolved against it.
- Enum filters use `"any"` for "no filter" instead of `null` (`lang`, `category`, `kind`,
  `level`, `coverage`). Unknown values are rejected instead of returning an empty list.
- `list_rules` returns 50 summaries by default (was 200); raise `limit` up to 400.
- Unknown rule IDs, unknown profiles and missing paths are tool errors instead of empty or
  `{"error": ...}` results.
- Requires `mcp>=1.15`.

### Added

- Every tool has a title, MCP annotations (read-only, non-destructive, idempotent, closed
  world), a description of every parameter and, except `format_findings`, an output schema.
- `get_rule(include_examples=false)` returns text and risk without code examples.
- `build_review_packet(compdb=...)`, so the static pass inside it can use a compilation database.
- `format_findings(warnings=...)` carries partial-analysis warnings into markdown, GitHub and
  SARIF output; `codequality` and `gitlab-sast` styles are listed.
- `Dockerfile.mcp` and [docs/docker.md](docs/docker.md): an image that runs the MCP server over stdio (and the CLI with
  `--entrypoint cert-review`), for local use and the Glama registry build.
- `glama.json`.
- `.github/workflows/docker-publish.yml`: on a `v*.*.*` tag, builds `Dockerfile.mcp` for
  linux/amd64 and linux/arm64, checks that it answers `tools/list`, and pushes
  `<DOCKERHUB_USERNAME>/cert-review-mcp:<version>` and `:latest`.

### Fixed

- An analyzer timeout (300 s per file and tool) makes the tool status `partial` and adds a
  warning, like a compile error; it used to appear only under `notes`. `--fail-on-parse-error`
  (new alias `--fail-on-partial`) and the Action input `fail-on-parse-error` fail on it.
- Error messages reach mcp 2.x clients (they were replaced by "Error executing tool ...").
- `pip install` from a wheel or git URL ships `data/` and `profiles/`; previously every tool
  failed unless `CERT_REVIEW_HOME` was set.
