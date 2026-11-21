# Security Policy

## Supported versions

Security fixes go into the latest 1.x release (the newest `v1.*` tag and the
`raminnietzsche/cert-review-mcp:latest` image). Older releases are not patched.

## Reporting a vulnerability

Please report vulnerabilities privately through GitHub Security Advisories:
[Report a vulnerability](https://github.com/RaminNietzsche/cert-review-mcp/security/advisories/new).
Do not open a public issue for security problems.

Include the affected version, how to reproduce the problem and its impact. You can expect
a first response within 7 days. Once a fix is released, the advisory is published with
credit to the reporter unless you prefer otherwise.

## Scope

The MCP server and CLI are read-only: they read source files, diffs and the bundled rule
data, run local analyzers (clang-tidy, the Clang Static Analyzer, cppcheck), and return
results. They never write to the analyzed project and never post comments or send data to
GitHub, GitLab or any other service. Reports about path handling, analyzer invocation,
the Docker images and the GitHub Action are in scope.
