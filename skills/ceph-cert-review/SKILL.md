---
name: ceph-cert-review
description: Adds Ceph context to the cert-review skill. Reviews Ceph C++23 and C code against SEI CERT with the ceph profile: ceph_assert is for invariants, dout/ldout are stream based, locks are ceph::mutex with lockdep, RefCountedObject uses intrusive references, buffer::list has its own bounds idioms, errors are negative errno ints, crimson and boost::asio callbacks outlive their frames. Use for "CERT review of this Ceph change", "check my ceph PR for memory/lifetime/bounds issues", or before submitting to ceph/ceph.
compatibility: Needs the cert-review skill and MCP server. A Ceph build's compile_commands.json is strongly preferred; tools/ceph_compdb.py builds an approximate one for a partial checkout.
license: Apache-2.0
---

# ceph-cert-review

Read [../cert-review/SKILL.md](../cert-review/SKILL.md) first; this skill only adds Ceph context.
Everything there applies, including: **draft comments only, and never post
without the human approving the exact text.**

Upstream conventions (CodingStyle, SubmittingPatches) still decide style and
process. CERT findings are *correctness and security* review input, not a
replacement for review by the component maintainers. Do not file or comment on
tracker.ceph.com or ceph/ceph PRs from this skill.

## Setup

- Use `profile: "ceph"` for every tool call.
- Language levels in the tree: C++23 (`CMAKE_CXX_STANDARD 23`, extensions off) and C11 with GNU
  extensions (`src/CMakeLists.txt`). There is no checked-in `.clang-tidy`; the engine
  passes checks explicitly.
- Compile database: a real Ceph build with `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`
  is best. For a partial checkout, `python3 tools/ceph_compdb.py --ceph <root> --out <dir> src/common ...`.
- Review the diff, not the file: `check_diff` with `base` = the target branch.

## Where to spend attention

Ceph profile priorities come from where bugs bite daemons (details in
[references/ceph-idioms.md](references/ceph-idioms.md)):

1. **Untrusted input paths**: `src/msg`, `src/messages`, `src/auth`, `src/mon`,
   `src/mds`, `src/osd`, `src/rgw`, `src/librados`, `src/librbd`. Look at decode
   paths, lengths used as sizes, string handling (ARR, INT, MEM, STR).
2. **Lifetime in callbacks**: `Context`/`Finisher`, `boost::asio` handlers, seastar
   continuations in `src/crimson` (EXP54-CPP, EXP61-CPP, MEM50-CPP).
3. **Refcounts**: `RefCountedObject`, `ceph::ref_t`, `intrusive_ptr`, `Message` (MEM50/51-CPP).
4. **Locks**: `ceph::mutex` discipline (CON50..CON56-CPP); not in crimson.
5. **On-disk formats and I/O**: `src/os`, `src/blk`, `src/kv` (INT, ARR, FIO, ERR).

## Checklist before drafting a comment

Use [references/ceph-checklist.md](references/ceph-checklist.md). In short: is it
`ceph_assert` misused as input validation; is a decoded length trusted; is a
`put()` followed by a use; is a lambda capturing by reference stored; is a lock
taken without RAII; is a `-errno` return ignored; is it test code?

## Do not report

- `PRE31-C` on `ceph_assert`/`dout`/`derr`/`ldout`: they evaluate arguments once.
- `ERR50-CPP` for `ceph_assert`/`ceph_abort`: that is the sanctioned fatal path.
  Report an assert on *external* data instead (the data can come from a peer or client).
- `FIO30-C` on `dout`/`derr`/`fmt` calls: they are not printf-style sinks.
- Concurrency rules inside `src/crimson`: shard-per-core; look for lifetime bugs.
- Anything under third-party trees (`src/boost`, `src/rocksdb`, `src/seastar`, `src/spdk`, ...).

The profile encodes these as `suppress` entries with reasons; if a suppressed
class turns out to hide a real bug in a specific place, say so in the comment
and propose narrowing the suppression.
