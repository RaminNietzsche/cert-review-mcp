# Changelog

## Unreleased

### Added

- Optional analyzers, normalised into the same finding schema and checker map:
  - **Semgrep** with 40 CERT rules shipped in `data/semgrep/` for INT30/33/34/36-C,
    EXP34/44/45/46-C, EXP52-CPP, MEM30/34/35-C, MEM50/51-CPP, CON31/34/36/39/40/41-C,
    CON50/54-CPP, POS34/48/50/53-C, ENV30-C, FIO30/34/37-C and STR30-C. Included in both
    Docker images (amd64 and arm64).
  - **Infer** (Pulse, InferBO, liveness, RacerD, starvation, SIOF); 28 issue types mapped in
    `data/checker_overlay.yaml`. Not in the images (about 1.2 GB, no Linux arm64 release).
  - **CodeQL** with the `codeql/cert-c-coding-standards` and `codeql/cert-cpp-coding-standards`
    packs (232 queries mapped). Opt-in; not in the images and not run in CI.
- `tools` (CLI `--tools`, MCP `tools`, Action `tools`) accepts `semgrep`, `infer`, `codeql` and
  `auto`. The default is now `auto`: the core tools plus Semgrep and Infer when they are on
  `PATH`. A requested analyzer that is not installed adds a `warnings` entry.
- `tier_extended` per rule and `extended_toolchain` in `get_rule_coverage`: coverage with Infer
  and CodeQL installed. `tier_runnable` now counts the reference toolchain of the images,
  which includes Semgrep.
- `docs/analyzers.md`: install notes, tiers, what each analyzer covers, a Ceph sanity check of
  the Semgrep rules.
- `tools/eval_accuracy.py` measures each toolset (baseline, + Semgrep, + Infer, + CodeQL) and
  reports corpus-wide recall; CodeQL is evaluated with one database per example.

### Accuracy (CERT examples, docs/accuracy.md)

- Corpus-wide recall (detected noncompliant examples / 708): 15% with clang-tidy, clangsa and
  cppcheck; 20% with Semgrep added (the image toolchain; in-sample, the rules were written
  against these examples); 20% with Infer; 28% with CodeQL. False positives on the 840
  compliant examples: 5, 5, 5 and 28.
- On the 103 rules the baseline scores: precision/recall 95%/42% before, 96%/46% with Semgrep,
  88%/54% with all analyzers.

### Changed

- Docker images grow by about 330 MB (MCP image 787 MB to 1.12 GB, Action image 957 MB to
  1.29 GB, uncompressed, amd64) for Semgrep.

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
