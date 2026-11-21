## What the run shows

Read against the per-case table above (run of 2026-11-21).

**What was found.** Five detections, all from narrow, syntactic checks that fire on the exact
construct the fix changed:

- `cert-str34-c` on Ceph's `url_decode` table lookup with a plain `char` index
  (ceph-fix-2b4bef17), and `bugprone-use-after-move` on `m->get_cost()` after `std::move(m)` in
  `DispatchQueue::enqueue` (ceph-fix-58a75129). Both disappear on the fixed revision.
- `cert-err33-c` on an unchecked `_TIFFmalloc` (libtiff CVE-2018-18661) and an unchecked
  `strftime` (libarchive CVE-2025-25724), and `bugprone-narrowing-conversions` (INT31-C) on the
  one-byte SOCKS5 length (curl CVE-2023-38545). In these three cases a matching finding is still
  reported near the fixed code, so the hit points at the right line but does not tell the
  vulnerable version from the fixed one.

**Wrong-rule hits.** Twelve cases have findings in the region but under another rule. Most are
INT31-C/FLP34-C narrowing reports on lines next to the bug (Heartbleed, libtiff LZW, libarchive
zip, several Ceph buffer handlers): noise that happens to sit near the defect. Two are close
calls: ERR34-C on the `atoi` that feeds the divisor in libtiff CVE-2016-3623 (the fix validates
exactly that value; the case is scored against INT33-C), and ERR33-C next to the NULL header in
Ceph CVE-2018-7262.

**Misses that point at checker work** (useful for the analyzer work in progress):

- *Integer overflow in size computations* (0 of 9): `malloc(len * 2)`, `(userlen + domlen) * 2`,
  `neededSize += keep`, `ctx->num + inl < ctx->length`, unsigned `rem -= line_len + 1`. No current
  checker models INT30-C/INT32-C wrap in an allocation size or a bound check. A taint-style check
  (Semgrep or CodeQL: attacker-sized length reaching `malloc`/`memcpy` without an overflow guard)
  is the obvious gap; this is also the biggest Ceph-relevant group (INT).
- *Length-from-input reaching `memcpy`/`recv`* (Heartbleed, curl NTLM, TFTP, Ceph STS
  `recv_body` into `char buf[256]`, admin socket `message_size`): ARR38-C. The Clang Static
  Analyzer's taint checkers (`alpha.security.taint`, `optin.taint`) are not enabled here and
  would be the first thing to try.
- *Use-after-free through ownership* (`delete lock` inside a loop in RGWLC, a ReadOp freed before
  logging, a reference into a vector kept across `emplace_back`): MEM50-CPP and CTR51-CPP.
  Path-sensitive analysis across the whole function is needed; in this run the Clang Static
  Analyzer reported nothing in any region, partly because many Ceph files did not parse.
- *Null dereference after a missing check* (Ceph CVE-2020-12059, CVE-2016-8626, mds
  `handle_client_link`, `rgw_user`): EXP34-C. Same analyzer limitation.
- *Header/CRLF injection* (three Ceph CORS/response-header CVEs) and the *format string* in
  libradosstriper (built in one statement, used in another): STR02-C and FIO30-C need data-flow
  rules, not AST checks.

**Ceph parsing.** 27 of 33 scored Ceph cases are partial. Ceph builds with GCC and pins its own
Boost; analysing old revisions with clang 19, libstdc++ 14 and Boost 1.83 fails in different
ways per era (missing `fmt` or generated headers before the submodule is fetched, consteval
`StructVChecker` in recent `rgw_zone_types.h`, `<chrono>`/`<format>` mismatches for 2020-era
code, `int_types.h` typedef clashes). A real build of each revision would remove most of this and
is the main way to make the Ceph numbers firmer; the C projects parsed cleanly in 23 of 24 cases.
