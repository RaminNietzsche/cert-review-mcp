# Ceph trial

What happens when the engine and the `ceph` profile run on real Ceph code, measured, with
the false positives and the limits stated.

## Setup

- Source: `ceph/ceph` `main` at `5f927c81a9c4eed5a11a524a9c4809c2bf2cd1d7` (2026-11-21), sparse
  checkout of `src/common`, `src/include`, `src/global`, `src/msg`, `src/auth`, `src/osdc`, `src/crush`,
  and the directories their headers need.
- Scope: 162 `.cc` files in `src/common`, `src/msg` (incl. `async`), `src/auth`, `src/osdc`, `src/crush`.
  `src/rgw` was set up in the compile database but not run: the trial was bounded to about
  20 minutes of analysis.
- Compile database: not a real build. `tools/ceph_compdb.py` renders `acconfig.h`, `ceph_ver.h`,
  `ceph_release.h` and the legacy option headers, and writes one command per file (`-std=c++23`).
  Boost from the distribution is older than what some Ceph headers need.
- Toolchain: clang-tidy 19.1.7, cppcheck 2.17.1, profile `ceph`, `--min-confidence 0`, 8 jobs.
  Command: `cert-review check <162 files> --profile ceph --root <ceph> --compdb <db> --report r.json`.

## Results

| Measure | Value |
|---|---|
| Files analysed | 162 |
| Files where clang-tidy hit compile errors (partial analysis) | 58 (36%) |
| Raw clang-tidy diagnostics mapped | 27,476 |
| cppcheck diagnostics mapped | 123 |
| Standalone Clang Static Analyzer findings | 0 (see limits) |
| Kept findings, round 1 (before tuning) | 1,717 |
| Kept findings, round 2 (after the first tuning) | 304 |
| Kept findings, round 3 (after triage, replayed) | 229 |
| Hidden by the profile in round 2 | 27,974 (11,767 recommendations, 10,959 below `min_level` L2, the rest suppressions) |

Round 3 was computed by replaying the new suppressions and mapping exclusions on the saved
round-2 findings, not by a third full run; the numbers are exact for those rules, but any
effect of the changes on tool behaviour would not show.

### Round 3 findings by rule (229)

ERR33-C 69, ERR58-CPP 32, INT31-C 29, ERR34-C 21, DCL57-CPP 15, DCL50-CPP 14, ERR55-CPP 12,
EXP42-C 9, DCL58-CPP 6, EXP34-C 5, CTR50-CPP 3, STR34-C 3, EXP54-CPP 2, others 9.
Severity: 132 error, 37 warning, 60 note. By directory: common 138, msg 29, include 21, crush 17,
mds 12, osdc 7, osd 3, auth 2. Confidence >= 0.8: 53; >= 0.5: 226.

## What tuning removed, and why

| Round 1 noise | Cause | Fix |
|---|---|---|
| 614 FIO34-C + 478 EXP45-C | CodeChecker maps `bugprone-narrowing-conversions` to unrelated rules | Mapping removed, mapped to INT31-C/FLP34-C instead (`data/checker_exclusions.yaml`, overlay) |
| 399 DCL58-CPP | `cert-dcl58-cpp` in clang-tidy 19 reports declarations that only mention std types | Profile keeps it only on a line opening `namespace std` (6 hits remain, all real `namespace std {` blocks) |
| ~2,000 unsigned-to-signed narrowing | `version_t`/`uint64_t` into `int64_t` is pervasive (`dump_int`, ids, epochs) | Profile suppression by message; real width narrowing still reported |
| 27 static `std::string` literals (ERR58-CPP) | Can only throw `bad_alloc` at startup | Profile suppression |
| 48 INT31-C int-to-double | Timing and ratio arithmetic | Profile suppression |
| EnumCastOutOfRange as MEM54-CPP; CallAndMessage as EXP54/EXP53-CPP | Wrong upstream mappings | Mapping exclusions |

## Assessment of the remaining findings

A sample of about 60 findings was read against the code (all of ERR34-C, EXP42-C, the EXP34-C
and CTR50-CPP groups, and samples of the rest). This is one reviewer's judgement, not a
ground truth.

- **Genuine and actionable:** ERR34-C (21: `atoi`/`atol` on config and JSON strings with no error
  reporting), EXP42-C (9: `memcmp` over structs and unions with padding, e.g. `frag_info_t`,
  `nest_info_t`), `realloc` result handling, destructors that may throw (DCL57-CPP, 15).
- **True to the rule, low value in Ceph:** ERR33-C (69): ignored `snprintf` (27), `realloc` (9),
  `clock_gettime`, `localtime_r`, `fprintf`. Worth fixing for `realloc`; the rest is style.
  ERR58-CPP (32): globals with constructors that can throw, mostly benign.
- **False positives seen:** `cert-err33-c` is rule-specific but not context aware; the
  `freebsd_errno.cc` CTR50-CPP hits (cppcheck evaluated a platform table); `sizeof(A*)` hits
  in templates (3 MEM35-C); deterministic RNG engines in CDC chunking (MSC32/MSC51); the
  `NonNullParamChecker` EXP34-C hits in `TrackedOp.cc` (`sdata` is looked up from a shard
  array; a null path is not demonstrated and was not confirmed).
- **Not judged:** `MEM51-CPP` (a `NewDeleteLeaks` report in `compression_onwire.cc`) and the
  ERR55-CPP findings that duplicate DCL57-CPP; both need a maintainer's eye.

Rough precision of the round 3 list on the sample: about half is actionable for Ceph, and
most of the rest is correct by the standard but not worth a review comment. That is why the
profile ranks by CERT priority and the packet/skill tell the reviewer to confirm each lead.

## Limits

- **Not a real build.** 36% of files had compile errors (missing generated or third-party
  headers, an older Boost), so those files were only partly analysed. Absence of findings in
  them is not evidence of absence. Use a real `compile_commands.json` for any claim that matters.
- **Standalone Clang Static Analyzer produced nothing.** It uses fallback flags rather than the
  compile database, so Ceph files do not parse. Static-analyzer results here come only through
  clang-tidy's `clang-analyzer-*` checks. Making it read the compile database is future work.
- **`src/rgw`, `src/osd`, `src/mon`, `src/librbd`, `src/crimson` were not analysed.** The
  crimson and asio idioms in the profile are based on reading code, not on measured results.
- **llm-only rules were not exercised here.** The trial measures the deterministic layer;
  the review-packet and validator are covered by tests, not by a Ceph run.
- **Small triage sample, single reviewer.** Treat the precision estimate as an order of magnitude.
- **CERT's recommendations** (11,767 hidden findings) were excluded by the profile.
