# Baselines

A large tree such as Ceph has hundreds of existing findings. A baseline records them once, so
later runs, CI gates and reviews show only findings that are new.

## Create and use

```bash
cert-review baseline create src --compdb build              # writes .cert-review-baseline.json
git add .cert-review-baseline.json

cert-review check src --compdb build --baseline .cert-review-baseline.json --fail-on warning
cert-review diff --base origin/main --baseline .cert-review-baseline.json
```

Use the same `--profile`, `--tools` and `--min-confidence` for `baseline create` as for the
runs that read it. `create` refuses to overwrite an existing file unless `--force` is given.

`cert-review baseline update PATHS...` re-analyses the given paths and replaces the entries of
the analysed files with the current findings. Entries for other files are kept, so a team can
refresh one directory at a time. It prints how many entries were added and removed.

The baseline is always built from whole files (`check`), because a diff only sees changed lines.

## Where it works

| Front end | How |
|---|---|
| CLI | `--baseline FILE` on `check` and `diff`; the summary on stderr shows new, baselined and fixed counts |
| MCP | `baseline_path` on `check_files` and `check_diff`; the result gains a `baseline` object |
| GitHub Action | `baseline: .cert-review-baseline.json`; output `baselined` |
| GitLab include | `CERT_REVIEW_BASELINE: .cert-review-baseline.json` |

Findings hidden by the baseline are not reported, annotated, formatted or counted for
`--fail-on` / `fail-on`.

The MCP `baseline` object:

| Field | Meaning |
|---|---|
| `entries` | Entries in the file |
| `new` | Findings returned (not in the baseline) |
| `baselined` | Findings hidden because they match an entry |
| `fixed` | Entries for analysed files that no longer match any finding; `null` for `check_diff`, which only sees changed lines |
| `fixed_entries` | Up to 50 of those entries (`rule_id`, `file`, `line`, `message`) |

## How fingerprints work

Line numbers change with every edit above a finding, so they are stored only for information.
Each entry identifies a finding by:

- `rule_id`, for example `ERR34-C`;
- `file`, relative to the directory that contains the baseline (so the file can be committed
  and used on any checkout path);
- `line_hash`: a hash of the flagged source line with all whitespace collapsed, so
  re-indentation does not matter;
- `context_hash`: a hash of the two nearest non-blank lines before and after it, normalized
  the same way.

A finding matches an entry in three passes, strictest first, and each entry absorbs at most
one finding:

1. rule, file, line hash and context hash;
2. rule, file and line hash (the code moved, its neighbours changed);
3. rule, file and context hash (the flagged line itself was edited in place).

So inserting or deleting lines elsewhere, reformatting, or moving a block keeps old findings
hidden. Two identical lines with the same rule need two entries; a third copy is reported as new.
A different rule on the same line is new. When a file cannot be read, the analyzer message
stands in for the line text.

## File format

```json
{
  "version": 1,
  "generator": "cert-review",
  "entries": [
    {"rule_id": "ERR34-C", "file": "src/parse.c", "line_hash": "c26b25e29b04264d",
     "context_hash": "e09b85aa652cd029", "fingerprint": "b7759db542d7142f",
     "line": 24, "checker": "clang-tidy:cert-err34-c", "message": "'atoi' used ..."}
  ]
}
```

Entries are sorted by file and line so updates give small, reviewable diffs.
