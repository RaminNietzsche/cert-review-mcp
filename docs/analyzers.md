# Analyzers

cert-review runs these analyzers and maps their findings to CERT rule IDs through
`data/checker_map.json`:

| Analyzer | Role | In the Docker images | Runs by default | Tested in CI |
|---|---|---|---|---|
| clang-tidy 19 (`cert-*` and mapped checks) | core | yes | yes | yes |
| Clang Static Analyzer (`clangsa`) | core | yes | yes | yes |
| cppcheck 2.17 | core | yes | yes | yes |
| Semgrep 1.186.0 with the CERT rules in `data/semgrep/` | optional | yes (amd64, arm64) | when installed | yes (rule tests on the CERT examples) |
| Infer 1.3.0 (Pulse, InferBO, liveness, RacerD, starvation, SIOF) | optional | no | when installed | no (adapter tested with recorded output) |
| CodeQL 2.27 with the CERT C/C++ query packs | optional | no | only when requested | no (adapter tested with recorded output) |

"When installed" means the binary is on `PATH`. A missing optional analyzer is skipped: with
the default selection a note names it; when it was asked for explicitly (`--tools`, the MCP
`tools` argument, or the Action `tools` input), the report carries a `warnings` entry
"`<tool>: requested but not run: ...`" with an install hint, and the tool status is `missing`.

Since 1.3.0, cppcheck uses `--project=compile_commands.json` when a compilation database is
available (auto-detected under `--compdb` or `root/build`), and syntax/preprocessor failures mark
the run as partial.

Select analyzers with `--tools` (CLI), `tools` (MCP `check_files`, `check_diff`,
`build_review_packet`) or the Action input `tools`:

```bash
cert-review check src                                 # auto: core + Semgrep/Infer when installed
cert-review check src --tools auto,codeql             # also CodeQL
cert-review check src --tools clang-tidy,semgrep      # exactly these
```

## Tiers

Every rule has three tiers in `data/checker_map.json` and in `get_rule` / `get_rule_coverage`:

* `tier_runnable`: checkers of the reference toolchain, the one in the Docker images
  (clang-tidy, Clang Static Analyzer, cppcheck, Semgrep).
* `tier_extended`: the reference toolchain plus Infer and CodeQL.
* `tier`: every mapped checker, including ones the pinned versions do not have.

Semgrep rules are pattern rules written for one rule each, but they only cover the forms
spelled out in the rule, so they count as `partial`, with a confidence set per rule (high 0.8,
medium 0.65, low 0.45). CodeQL queries from the CERT packs are written for one rule each and
count as `deterministic`. Infer issue types are general and count as `partial`.

## Semgrep rules

`data/semgrep/*.yml` holds 41 rules; each names its CERT rule(s) in `metadata.cert`:

| File | Rules covered |
|---|---|
| `int.yml` | INT30-C, INT33-C, INT34-C, INT36-C |
| `exp.yml` | EXP34-C, EXP44-C, EXP45-C, EXP46-C, EXP52-CPP |
| `mem.yml` | MEM30-C, MEM34-C, MEM35-C, MEM50-CPP, MEM51-CPP |
| `con.yml` | CON31-C, CON34-C, CON36-C, CON39-C, CON40-C, CON41-C, CON50-CPP, CON54-CPP, POS48-C, POS50-C, POS53-C |
| `misc.yml` | ENV30-C, FIO30-C, FIO34-C, FIO37-C, POS34-C, STR30-C |
| `size.yml` | INT30-C (unchecked `+` or `*` in an allocation, copy or read size) |

`tests/test_semgrep_rules.py` runs them on the CERT noncompliant and compliant examples in
`corpus/`. The rules were written against those examples, so the corpus figures for Semgrep in
[accuracy.md](accuracy.md) are in-sample. They are intraprocedural: CON31-C and CON39-C catch
the single-function form (lock then destroy, join then detach) and miss the CERT examples,
where two threads are involved.

Out-of-sample check: on 698 Ceph files (`src/common`, `src/os/bluestore`, `src/msg/async`,
`src/osd` at commit `065d8cb97eb6`) the rules report 78 findings. 62 are parameters used as a
divisor (INT33-C, 46) or shift count (INT34-C, 16) without a check in the same function: the
rule's condition holds, but whether a caller can pass zero or a too-large count needs a
reviewer. 2 are `malloc` results used without a null check (EXP34-C). 3 are size
multiplications without an overflow check (INT30-C). The other 11 are false positives:
`wait()` calls on helper types that loop internally and thin wrappers around
condition-variable waits whose callers loop (CON54-CPP 5, CON36-C 2), a
`compare_exchange_weak` retried with `goto` (CON41-C) and three dereference-before-check
reports (EXP34-C).

`size.yml` was added after the rest and was not written against the corpus: INT30-C is a
held-out rule (see [accuracy.md](accuracy.md)). It flags `malloc`, `realloc`, `memcpy`,
`memmove`, `memset`, `strncpy`, `recv`, `read`, `fread`, `new T[...]` and similar calls whose
size argument is (or is a variable just assigned from) a sum or product of two non-constant
operands, unless an `if`, `assert` or `ceph_assert` mentions an operand first. Operands that are
`sizeof`, literals, ALL-CAPS macros or `strlen(...)` are ignored, so `strlen(s) + 1` and
`n * sizeof(T)` are not reported. On the same 698 Ceph files it reports one finding
(`malloc(key.size() + value.size() + 2)` in `src/libcephfs.cc`). Its design follows the
integer-overflow misses in [benchmark-real.md](benchmark-real.md), so gains there are not fully
independent of that benchmark.

Rebuild the checker map after editing the rules: `python3 tools/build_checker_map.py ...`.

## Clang Static Analyzer: taint and bounds checkers

`clangsa` runs `clang --analyze` with the mapped checkers, including alpha and opt-in ones that
clang-tidy cannot enable, and with the file's flags from the compilation database when one is
given (up to 1.2.0 it always used guessed flags). Checkers that report several weaknesses are
split by message into `<checker>@<variant>`, and each variant maps to its own rules
(`data/checker_overlay.yaml`):

| Checker (clang 19) | Variant | CERT rules |
|---|---|---|
| `alpha.security.taint.GenericTaint` | untrusted format string | FIO30-C |
| | untrusted data passed to `system`/`exec*` | ENV33-C, STR02-C |
| | untrusted value as a size argument | ARR38-C, INT04-C |
| | other configured sinks | INT04-C |
| `optin.taint.TaintedAlloc` | | INT04-C, MEM35-C |
| `alpha.security.ArrayBoundV2` | tainted index | ARR30-C, INT04-C |
| | untainted index | not mapped (noisy on fragments) |
| `alpha.unix.cstring.OutOfBounds` | `mem*` functions | ARR38-C |
| | string functions | STR31-C |

Mapped checkers the installed clang does not list are skipped with a note. Renamed checkers
run under the installed clang's name: `GenericTaint` is `alpha.security.taint.TaintPropagation`
in clang 18 and `optin.taint.GenericTaint` from clang 20, `ArrayBoundV2` is
`security.ArrayBound` in clang 21 (tested with 18.1, 19.1 and 21.1; clang 18 has no
`optin.taint.TaintedAlloc`).

`data/csa-taint.yaml` adds the byte-order helpers (`ntohs`, `be32toh`, ...) and `strtoul` as
taint propagators. Limits measured with clang 19.1.7: the taint sources are standard input,
`getenv` and similar; `read` and `recv` only pass on the taint of their descriptor, which is not
tainted by default, and entries in the configuration file do not override the built-in rules for
those names; the buffer filled by `fgets` loses its taint on the path where the result is
tested. In practice the taint checkers find untrusted format strings and command strings in
small programs, and rarely fire on library code such as Ceph, where input arrives through
network buffers and wrapper classes. `alpha.security.MallocOverflow` was tried and left out: on
the dev rules 3 of its 5 reports were on compliant examples.

`bugprone-narrowing-conversions` (clang-tidy) is split the same way: integer-to-integer
conversions map to INT31-C with confidence 0.45, floating-to-integer and floating-to-floating
conversions to FLP34-C, integer-to-floating conversions to nothing. Before, every narrowing was
reported as both INT31-C and FLP34-C; on real code these reports sit next to many bugs without
being the bug, and the lower confidence ranks them below more specific findings at the same
location and hides them at `--min-confidence 0.5`.

## Infer

Releases: <https://github.com/facebook/infer/releases> (Linux x86_64 and macOS arm64; there is
no Linux arm64 build). Unpacked, the Linux release is about 1.2 GB, which is why it is not in
the images. To add it to an amd64 image:

```dockerfile
FROM raminnietzsche/cert-review-mcp:latest
ADD https://github.com/facebook/infer/releases/download/v1.3.0/infer-linux-x86_64-v1.3.0.tar.xz /tmp/infer.tar.xz
RUN apt-get update && apt-get install -y --no-install-recommends xz-utils \
 && tar -C /opt -xJf /tmp/infer.tar.xz && rm /tmp/infer.tar.xz \
 && ln -s /opt/infer-linux-x86_64-v1.3.0/bin/infer /usr/local/bin/infer
```

cert-review writes a compilation database for the selected files (from `--compdb` when given,
otherwise the fallback flags) and runs `infer run --compilation-database ... --keep-going`
with Pulse, InferBO, liveness, RacerD, starvation and SIOF. Files that fail to compile are
listed under `files_with_errors`, as for the other tools. 28 Infer issue types are mapped
(`data/checker_overlay.yaml`), for example `NULLPTR_DEREFERENCE` to EXP34-C,
`USE_AFTER_FREE` to MEM30-C/MEM50-CPP, `MEMORY_LEAK_C` to MEM31-C, `BUFFER_OVERRUN_L1` to
ARR30-C and `DEADLOCK` to CON35-C/CON53-CPP/POS51-C.

## CodeQL

The CodeQL CLI is free for open-source projects and research, under GitHub's terms
(<https://github.com/github/codeql-cli-binaries>); it is not bundled here. The CERT queries come
from [github/codeql-coding-standards](https://github.com/github/codeql-coding-standards) (MIT):

```bash
codeql pack download codeql/cert-c-coding-standards codeql/cert-cpp-coding-standards
```

The checker map lists the 232 queries of the default suites of version 2.63.0 (queries tagged
`default-disabled` or written for a recommendation are left out). Without the packs, a
requested CodeQL run reports `missing` with the download command.

With a compilation database, cert-review builds the database with a traced
`-fsyntax-only` compile of the selected files; without one it uses `--build-mode=none` on a
copy of the files. All selected files go into one database, which is what whole-program
queries (one-definition rule DCL60-CPP, incompatible declarations DCL40-C, linkage DCL36-C)
need. It also means that unrelated files, such as a folder of standalone examples, are seen as
one program, and those queries then report collisions between them. The accuracy evaluation
therefore builds one database per example.

A database build plus the query run takes 10 to 60 seconds even for a few files, so CodeQL
runs only when asked for.
