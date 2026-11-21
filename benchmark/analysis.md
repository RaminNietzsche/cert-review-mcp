## What the run shows

Read against the per-case table above (run of 2026-11-22, analyzers of the Docker images:
clang-tidy, Clang Static Analyzer, cppcheck and Semgrep).

**Before and after this round of checker work.** Same 62 cases, same analyzer versions; *before*
is release 1.2.0 run with the same four analyzers (adding Semgrep to the 1.2.0 core set changed
nothing: 5 of 57 either way).

| Measure | 1.2.0 | Now |
|---|---|---|
| Detected (all findings) | 5 of 57 | 6 of 57 |
| Detected and fix-sensitive | 2 | 3 |
| Detected, Ceph | 2 of 33 | 2 of 33 |
| Detected, other projects | 3 of 24 | 4 of 24 |
| Wrong rule only (all findings) | 12 | 12 |
| Wrong rule only, confidence >= 0.5 | n/a | 5 |
| Partial cases (Ceph) | 27 of 33 scored | 18 of 33 scored |
| Findings in the fixed code's region | 54 | 41 |

The one new detection is curl CVE-2017-8816 (NTLM `(userlen + domlen) * 2` style size
arithmetic feeding an allocation): the new `int30-c-unchecked-size-arithmetic` rule reports
INT30-C on the vulnerable line and not on the fixed one. That rule was designed after reading the
integer-overflow misses of the previous run, so this hit is not an independent measurement.

**What was found.** Six detections, all from narrow checks that fire on the exact construct the
fix changed:

- `cert-str34-c` on Ceph's `url_decode` table lookup with a plain `char` index
  (ceph-fix-2b4bef17), and `bugprone-use-after-move` on `m->get_cost()` after `std::move(m)` in
  `DispatchQueue::enqueue` (ceph-fix-58a75129). Both disappear on the fixed revision.
- INT30-C size arithmetic in curl's NTLM code (curl CVE-2017-8816), gone after the fix.
- `cert-err33-c` on an unchecked `_TIFFmalloc` (libtiff CVE-2018-18661) and an unchecked
  `strftime` (libarchive CVE-2025-25724), and integer narrowing (INT31-C) on the one-byte SOCKS5
  length (curl CVE-2023-38545). In these three a matching finding is still reported near the
  fixed code. The SOCKS5 hit comes from the INT31-C narrowing report, which now has confidence
  0.45, so it drops out at `--min-confidence 0.5` (5 detections instead of 6).

**Wrong-rule hits.** Narrowing reports used to be filed as both INT31-C and FLP34-C; they are now
split by message, so integer narrowing is INT31-C only and FLP34-C is left for floating
conversions (Heartbleed now shows INT31-C alone). With the 0.5 cut-off the wrong-rule cases fall
from 12 to 5, at the cost of the SOCKS5 detection above. The remaining close calls are unchanged:
ERR34-C on the `atoi` feeding the divisor in libtiff CVE-2016-3623 and ERR33-C next to the NULL
header in Ceph CVE-2018-7262.

**What did not help.**

- *Clang Static Analyzer taint checkers* produced no finding in any case region. In clang 19
  `read`/`recv` only propagate taint from an already tainted descriptor, the taint configuration
  file cannot override that built-in rule, and `fgets` loses taint on the path where its result is
  tested. Ceph receives input through `bufferlist` and wrapper classes the checkers do not model.
- *Bounds checkers* (`ArrayBoundV2` with a tainted index, `cstring.OutOfBounds`) found nothing in
  the regions either; `MallocOverflow` was left out because most of its reports on the dev rules
  were on compliant examples.
- *Better Ceph parsing* (C++ standard read from the tree's `CMakeLists.txt`, bundled fmt no
  longer hiding `<format>`, pre-included standard headers for old trees, `HAVE_LINUX_TYPES_H`,
  rgw include paths) cut the partial Ceph cases from 27 to 18 but turned no miss into a
  detection: the nine cases that now parse cleanly are still misses or wrong-rule. The Ceph bugs
  in this set (header injection, ownership and lifetime errors, missing null checks after lookups,
  lengths taken from decoded messages) need data-flow or whole-function analysis that these
  checkers do not do on this code.

**Still partial.** Most remaining Ceph partial cases are 2025-26 trees where clang 19 rejects
calls to the consteval `StructVChecker` constructor in `include/denc.h` (GCC accepts them; a
`-Dconsteval=constexpr` workaround breaks libstdc++ and was dropped), plus missing optional
dependencies (`liboath`, `civetweb`, `lua.hpp`, FastCGI, generated `*.frag.cc`) and pre-2019 crypto
headers. A real build of each revision remains the way to firm up the Ceph numbers; the C
projects parse cleanly in 23 of 24 cases.
