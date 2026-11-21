# CI examples

`ci/gitlab-ci.cert-review.yml` (GitLab merge requests) and
`ci/github/cert-review.yml` (GitHub pull requests) run `cert-review diff` on the
changed lines and produce a SARIF file plus a Markdown summary.

**Both are examples. Do not enable either without Ramin's approval.** Neither
posts comments: they only publish SARIF (GitHub code scanning) or job artifacts
(GitLab). Turning findings into MR/PR review comments is a separate, manual step:
`cert-review diff --format github|gitlab` prints the payload; a human reviews the
text and decides whether to send it.

Tips: pass `--compdb` with a real `compile_commands.json` for accurate results; use
`--fail-on error` only after you have measured the noise on your tree; the `ceph`
profile expects paths relative to a Ceph root.
