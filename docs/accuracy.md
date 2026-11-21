# Accuracy of the deterministic layer

Corpus: 1548 code examples taken from the CERT rule pages (commit `73ee7a0dbe77`); 708 noncompliant, 840 compliant.

Toolchain: clang-tidy 19.1.7, clangsa 19.1.7, cppcheck 2.17.1, semgrep 1.186.0, infer 1.3.0, codeql 2.27.5. CodeQL ran the `codeql/cert-c-coding-standards` and `codeql/cert-cpp-coding-standards` packs (codeql/cert-c-coding-standards 2.63.0, codeql/cert-cpp-coding-standards 2.63.0).

Run time: core 277s, semgrep 16s, infer 91s, codeql 6680s.

A noncompliant example is *detected* when the engine reports that example's own rule in the file; a compliant example is a *false positive* when it does. Precision = TP/(TP+FP), recall = TP/(TP+FN). *Scored rules* are the rules with at least one checker in the toolset; *corpus-wide* counts every example, including rules no checker covers, so it is the number to compare across toolsets. The examples are short fragments and many do not compile standalone, so absolute numbers understate what the tools achieve on real code, and precision is optimistic because compliant fragments are tiny.

## Summary

| Toolset | Scored rules | TP | FN | FP | TN | Precision | Recall (scored) | Corpus-wide recall | Corpus-wide FP rate |
|---|---|---|---|---|---|---|---|---|---|
| baseline: clang-tidy, clangsa, cppcheck | 106 | 109 | 150 | 6 | 310 | 95% | 42% | 15% (109/708) | 1% (6/840) |
| reference image: + semgrep | 124 | 145 | 151 | 6 | 361 | 96% | 49% | 20% (145/708) | 1% (6/840) |
| + infer | 131 | 146 | 161 | 6 | 375 | 96% | 48% | 21% (146/708) | 1% (6/840) |
| + codeql (all analyzers) | 199 | 204 | 218 | 29 | 496 | 88% | 48% | 29% (204/708) | 3% (29/840) |

## Dev and held-out rules

Every rule, with all of its examples, is assigned to one half by a hash of its ID (`sha256("cert-review-split-v1:<rule>") % 2`). Checkers and mappings were tuned on dev rules only; held-out rules show whether that generalises. Precision and recall are corpus-wide (every example of the half counts). *Before* is release 1.2.0 (same corpus and analyzer versions).

| Toolset | Half | Rules | TP | FN | FP | TN | Precision | Recall | Before: precision | Before: recall |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline: clang-tidy, clangsa, cppcheck | dev | 177 | 55 | 269 | 3 | 378 | 95% | 17% | 95% | 16% (52) |
| baseline: clang-tidy, clangsa, cppcheck | held-out | 194 | 54 | 330 | 3 | 456 | 95% | 14% | 96% | 14% (53) |
| reference image: + semgrep | dev | 177 | 80 | 244 | 3 | 378 | 96% | 25% | 96% | 24% (77) |
| reference image: + semgrep | held-out | 194 | 65 | 319 | 3 | 456 | 96% | 17% | 97% | 17% (64) |
| + infer | dev | 177 | 81 | 243 | 3 | 378 | 96% | 25% | 96% | 24% (78) |
| + infer | held-out | 194 | 65 | 319 | 3 | 456 | 96% | 17% | 97% | 17% (64) |
| + codeql (all analyzers) | dev | 177 | 99 | 225 | 17 | 364 | 85% | 31% | 85% | 30% (97) |
| + codeql (all analyzers) | held-out | 194 | 105 | 279 | 12 | 447 | 90% | 27% | 90% | 27% (104) |

### The 106 rules the baseline scores

Same rules for every toolset, so the rows differ only by what the added analyzers find.

| Toolset | TP | FN | FP | TN | Precision | Recall |
|---|---|---|---|---|---|---|
| baseline: clang-tidy, clangsa, cppcheck | 109 | 150 | 6 | 310 | 95% | 42% |
| reference image: + semgrep | 122 | 137 | 6 | 310 | 95% | 47% |
| + infer | 122 | 137 | 6 | 310 | 95% | 47% |
| + codeql (all analyzers) | 142 | 117 | 20 | 296 | 88% | 55% |

### By tier: baseline: clang-tidy, clangsa, cppcheck

| Group | Rules | TP | FN | FP | TN | Precision | Recall |
|---|---|---|---|---|---|---|---|
| all_scored | 106 | 109 | 150 | 6 | 310 | 95% | 42% |
| deterministic | 38 | 41 | 25 | 0 | 79 | 100% | 62% |
| partial | 68 | 68 | 125 | 6 | 231 | 92% | 35% |
| llm-only (not scored) | 265 | | | | | | |

### By tier: reference image: + semgrep

| Group | Rules | TP | FN | FP | TN | Precision | Recall |
|---|---|---|---|---|---|---|---|
| all_scored | 124 | 145 | 151 | 6 | 361 | 96% | 49% |
| deterministic | 38 | 41 | 25 | 0 | 79 | 100% | 62% |
| partial | 86 | 104 | 126 | 6 | 282 | 95% | 45% |
| llm-only (not scored) | 247 | | | | | | |

### By tier: + infer

| Group | Rules | TP | FN | FP | TN | Precision | Recall |
|---|---|---|---|---|---|---|---|
| all_scored | 131 | 146 | 161 | 6 | 375 | 96% | 48% |
| deterministic | 38 | 41 | 25 | 0 | 79 | 100% | 62% |
| partial | 93 | 105 | 136 | 6 | 296 | 95% | 44% |
| llm-only (not scored) | 240 | | | | | | |

### By tier: + codeql (all analyzers)

| Group | Rules | TP | FN | FP | TN | Precision | Recall |
|---|---|---|---|---|---|---|---|
| all_scored | 199 | 204 | 218 | 29 | 496 | 88% | 48% |
| deterministic | 186 | 199 | 193 | 28 | 461 | 88% | 51% |
| partial | 13 | 5 | 25 | 1 | 35 | 83% | 17% |
| llm-only (not scored) | 172 | | | | | | |

## Per rule: reference image: + semgrep

| Rule | Tier | TP | FN | FP | TN | Precision | Recall |
|---|---|---|---|---|---|---|---|
| ARR30-C | partial | 0 | 0 | 0 | 7 | n/a | n/a |
| ARR32-C | partial | 0 | 2 | 0 | 2 | n/a | 0% |
| ARR38-C | partial | 4 | 3 | 0 | 7 | 100% | 57% |
| CON31-C | partial | 0 | 1 | 0 | 1 | n/a | 0% |
| CON33-C | partial | 1 | 0 | 0 | 1 | 100% | 100% |
| CON34-C | partial | 1 | 3 | 0 | 5 | 100% | 25% |
| CON36-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| CON39-C | partial | 0 | 1 | 0 | 1 | n/a | 0% |
| CON40-C | partial | 3 | 0 | 0 | 3 | 100% | 100% |
| CON41-C | partial | 1 | 0 | 0 | 2 | 100% | 100% |
| CON50-CPP | partial | 0 | 1 | 0 | 2 | n/a | 0% |
| CON54-CPP | deterministic | 0 | 1 | 0 | 2 | n/a | 0% |
| CTR50-CPP | partial | 0 | 3 | 0 | 5 | n/a | 0% |
| CTR51-CPP | partial | 0 | 1 | 0 | 2 | n/a | 0% |
| CTR56-CPP | deterministic | 0 | 2 | 0 | 2 | n/a | 0% |
| DCL03-C | deterministic | 1 | 0 | 0 | 2 | 100% | 100% |
| DCL16-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| DCL30-C | partial | 3 | 0 | 0 | 4 | 100% | 100% |
| DCL37-C | deterministic | 2 | 3 | 0 | 5 | 100% | 40% |
| DCL41-C | partial | 1 | 0 | 0 | 1 | 100% | 100% |
| DCL50-CPP | deterministic | 0 | 0 | 0 | 2 | n/a | n/a |
| DCL51-CPP | deterministic | 2 | 2 | 0 | 4 | 100% | 50% |
| DCL54-CPP | deterministic | 2 | 0 | 0 | 2 | 100% | 100% |
| DCL57-CPP | partial | 0 | 5 | 0 | 2 | n/a | 0% |
| DCL58-CPP | deterministic | 2 | 0 | 0 | 3 | 100% | 100% |
| DCL59-CPP | deterministic | 0 | 4 | 0 | 3 | n/a | 0% |
| ENV30-C | partial | 1 | 1 | 0 | 3 | 100% | 50% |
| ENV31-C | partial | 0 | 2 | 0 | 3 | n/a | 0% |
| ENV33-C | deterministic | 2 | 0 | 0 | 4 | 100% | 100% |
| ENV34-C | partial | 0 | 2 | 0 | 4 | n/a | 0% |
| ERR30-C | partial | 1 | 2 | 0 | 4 | 100% | 33% |
| ERR33-C | deterministic | 4 | 1 | 0 | 6 | 100% | 80% |
| ERR34-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| ERR51-CPP | partial | 0 | 2 | 0 | 2 | n/a | 0% |
| ERR52-CPP | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| ERR55-CPP | partial | 0 | 2 | 0 | 3 | n/a | 0% |
| ERR58-CPP | deterministic | 3 | 0 | 0 | 4 | 100% | 100% |
| ERR60-CPP | deterministic | 0 | 1 | 0 | 2 | n/a | 0% |
| ERR61-CPP | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| EXP30-C | partial | 1 | 2 | 0 | 5 | 100% | 33% |
| EXP33-C | partial | 3 | 3 | 0 | 6 | 100% | 50% |
| EXP34-C | partial | 3 | 0 | 1 | 2 | 75% | 100% |
| EXP37-C | partial | 0 | 4 | 0 | 5 | n/a | 0% |
| EXP39-C | partial | 1 | 3 | 0 | 4 | 100% | 25% |
| EXP42-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| EXP44-C | partial | 3 | 1 | 0 | 4 | 100% | 75% |
| EXP45-C | partial | 3 | 0 | 0 | 7 | 100% | 100% |
| EXP46-C | partial | 1 | 0 | 0 | 1 | 100% | 100% |
| EXP50-CPP | partial | 2 | 2 | 0 | 6 | 100% | 50% |
| EXP51-CPP | partial | 1 | 0 | 0 | 1 | 100% | 100% |
| EXP52-CPP | partial | 2 | 0 | 0 | 2 | 100% | 100% |
| EXP53-CPP | partial | 0 | 4 | 0 | 4 | n/a | 0% |
| EXP54-CPP | partial | 2 | 5 | 0 | 8 | 100% | 29% |
| EXP55-CPP | partial | 3 | 0 | 0 | 2 | 100% | 100% |
| EXP58-CPP | partial | 1 | 1 | 0 | 3 | 100% | 50% |
| EXP61-CPP | partial | 1 | 0 | 0 | 2 | 100% | 100% |
| EXP62-CPP | partial | 1 | 1 | 0 | 2 | 100% | 50% |
| EXP63-CPP | partial | 1 | 1 | 0 | 3 | 100% | 50% |
| FIO30-C | partial | 2 | 0 | 0 | 3 | 100% | 100% |
| FIO34-C | partial | 2 | 1 | 0 | 3 | 100% | 67% |
| FIO37-C | partial | 1 | 0 | 0 | 1 | 100% | 100% |
| FIO38-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| FIO39-C | partial | 0 | 1 | 0 | 1 | n/a | 0% |
| FIO42-C | partial | 1 | 3 | 0 | 4 | 100% | 25% |
| FLP30-C | deterministic | 2 | 0 | 0 | 2 | 100% | 100% |
| FLP32-C | partial | 0 | 4 | 0 | 4 | n/a | 0% |
| FLP34-C | partial | 1 | 1 | 1 | 1 | 50% | 50% |
| FLP37-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| INT04-C | partial | 1 | 2 | 1 | 2 | 50% | 33% |
| INT09-C | deterministic | 1 | 0 | 0 | 3 | 100% | 100% |
| INT30-C | partial | 1 | 2 | 0 | 8 | 100% | 33% |
| INT31-C | partial | 1 | 5 | 0 | 6 | 100% | 17% |
| INT32-C | partial | 0 | 7 | 0 | 11 | n/a | 0% |
| INT33-C | partial | 2 | 0 | 0 | 2 | 100% | 100% |
| INT34-C | partial | 3 | 0 | 0 | 3 | 100% | 100% |
| INT36-C | partial | 3 | 0 | 0 | 2 | 100% | 100% |
| MEM30-C | partial | 3 | 1 | 1 | 3 | 75% | 75% |
| MEM31-C | partial | 1 | 0 | 0 | 1 | 100% | 100% |
| MEM34-C | partial | 2 | 0 | 1 | 1 | 67% | 100% |
| MEM35-C | partial | 2 | 0 | 0 | 3 | 100% | 100% |
| MEM36-C | partial | 1 | 0 | 0 | 2 | 100% | 100% |
| MEM50-CPP | partial | 4 | 0 | 0 | 7 | 100% | 100% |
| MEM51-CPP | partial | 8 | 0 | 0 | 8 | 100% | 100% |
| MEM52-CPP | partial | 1 | 1 | 0 | 5 | 100% | 50% |
| MEM53-CPP | partial | 0 | 2 | 0 | 2 | n/a | 0% |
| MEM54-CPP | partial | 3 | 0 | 0 | 3 | 100% | 100% |
| MEM56-CPP | partial | 1 | 2 | 0 | 3 | 100% | 33% |
| MEM57-CPP | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| MSC12-C | partial | 0 | 7 | 0 | 10 | n/a | 0% |
| MSC24-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| MSC30-C | deterministic | 1 | 0 | 0 | 2 | 100% | 100% |
| MSC32-C | deterministic | 0 | 1 | 0 | 2 | n/a | 0% |
| MSC33-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| MSC37-C | partial | 0 | 3 | 0 | 2 | n/a | 0% |
| MSC50-CPP | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| MSC51-CPP | deterministic | 2 | 0 | 0 | 1 | 100% | 100% |
| MSC52-CPP | partial | 1 | 1 | 0 | 2 | 100% | 50% |
| MSC53-CPP | partial | 0 | 1 | 0 | 1 | n/a | 0% |
| MSC54-CPP | deterministic | 0 | 2 | 0 | 2 | n/a | 0% |
| OOP50-CPP | partial | 1 | 0 | 0 | 1 | 100% | 100% |
| OOP51-CPP | partial | 1 | 1 | 0 | 4 | 100% | 50% |
| OOP52-CPP | partial | 0 | 2 | 0 | 1 | n/a | 0% |
| OOP53-CPP | partial | 0 | 2 | 0 | 2 | n/a | 0% |
| OOP54-CPP | deterministic | 1 | 0 | 0 | 3 | 100% | 100% |
| OOP57-CPP | deterministic | 2 | 1 | 0 | 3 | 100% | 67% |
| OOP58-CPP | deterministic | 0 | 0 | 0 | 1 | n/a | n/a |
| POS34-C | partial | 1 | 0 | 0 | 3 | 100% | 100% |
| POS36-C | partial | 0 | 1 | 0 | 1 | n/a | 0% |
| POS44-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| POS47-C | deterministic | 2 | 0 | 0 | 1 | 100% | 100% |
| POS48-C | partial | 0 | 1 | 0 | 1 | n/a | 0% |
| POS50-C | partial | 1 | 1 | 0 | 4 | 100% | 50% |
| POS52-C | partial | 0 | 1 | 0 | 2 | n/a | 0% |
| POS53-C | partial | 0 | 1 | 0 | 1 | n/a | 0% |
| PRE02-C | partial | 2 | 3 | 0 | 2 | 100% | 40% |
| PRE31-C | partial | 2 | 1 | 0 | 5 | 100% | 67% |
| SIG30-C | deterministic | 1 | 2 | 0 | 3 | 100% | 33% |
| STR02-C | partial | 0 | 2 | 0 | 2 | n/a | 0% |
| STR30-C | partial | 3 | 0 | 0 | 3 | 100% | 100% |
| STR31-C | partial | 2 | 6 | 1 | 11 | 67% | 25% |
| STR34-C | deterministic | 1 | 2 | 0 | 2 | 100% | 33% |
| STR51-CPP | partial | 1 | 0 | 0 | 1 | 100% | 100% |
| STR52-CPP | partial | 0 | 1 | 0 | 3 | n/a | 0% |
| STR53-CPP | partial | 0 | 1 | 0 | 0 | n/a | 0% |

## Per rule: + codeql (all analyzers)

| Rule | Tier | TP | FN | FP | TN | Precision | Recall |
|---|---|---|---|---|---|---|---|
| ARR30-C | deterministic | 0 | 0 | 0 | 7 | n/a | n/a |
| ARR32-C | deterministic | 1 | 1 | 1 | 1 | 50% | 50% |
| ARR36-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| ARR37-C | deterministic | 1 | 0 | 0 | 2 | 100% | 100% |
| ARR38-C | deterministic | 4 | 3 | 1 | 6 | 80% | 57% |
| ARR39-C | deterministic | 0 | 3 | 0 | 3 | n/a | 0% |
| CON30-C | deterministic | 1 | 0 | 0 | 2 | 100% | 100% |
| CON31-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| CON32-C | deterministic | 0 | 1 | 0 | 2 | n/a | 0% |
| CON33-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| CON34-C | deterministic | 1 | 3 | 1 | 4 | 50% | 25% |
| CON35-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| CON36-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| CON37-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| CON38-C | deterministic | 1 | 0 | 1 | 2 | 50% | 100% |
| CON39-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| CON40-C | deterministic | 3 | 0 | 1 | 2 | 75% | 100% |
| CON41-C | deterministic | 1 | 0 | 0 | 2 | 100% | 100% |
| CON43-C | partial | 0 | 3 | 0 | 4 | n/a | 0% |
| CON50-CPP | deterministic | 0 | 1 | 0 | 2 | n/a | 0% |
| CON51-CPP | deterministic | 0 | 0 | 0 | 2 | n/a | n/a |
| CON52-CPP | deterministic | 0 | 1 | 0 | 2 | n/a | 0% |
| CON53-CPP | deterministic | 0 | 1 | 0 | 2 | n/a | 0% |
| CON54-CPP | deterministic | 0 | 1 | 0 | 2 | n/a | 0% |
| CON55-CPP | deterministic | 0 | 1 | 0 | 2 | n/a | 0% |
| CON56-CPP | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| CTR50-CPP | deterministic | 0 | 3 | 0 | 5 | n/a | 0% |
| CTR51-CPP | deterministic | 0 | 1 | 0 | 2 | n/a | 0% |
| CTR52-CPP | deterministic | 1 | 1 | 0 | 5 | 100% | 50% |
| CTR53-CPP | deterministic | 1 | 1 | 0 | 2 | 100% | 50% |
| CTR54-CPP | deterministic | 0 | 4 | 0 | 1 | n/a | 0% |
| CTR55-CPP | deterministic | 0 | 1 | 1 | 0 | 0% | 0% |
| CTR56-CPP | deterministic | 0 | 2 | 0 | 2 | n/a | 0% |
| CTR57-CPP | deterministic | 2 | 0 | 0 | 2 | 100% | 100% |
| CTR58-CPP | deterministic | 0 | 2 | 0 | 2 | n/a | 0% |
| DCL03-C | deterministic | 1 | 0 | 0 | 2 | 100% | 100% |
| DCL16-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| DCL30-C | deterministic | 3 | 0 | 1 | 3 | 75% | 100% |
| DCL31-C | deterministic | 1 | 2 | 0 | 3 | 100% | 33% |
| DCL37-C | deterministic | 2 | 3 | 0 | 5 | 100% | 40% |
| DCL38-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| DCL39-C | deterministic | 0 | 3 | 0 | 5 | n/a | 0% |
| DCL40-C | deterministic | 0 | 1 | 0 | 5 | n/a | 0% |
| DCL41-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| DCL50-CPP | deterministic | 0 | 0 | 0 | 2 | n/a | n/a |
| DCL51-CPP | deterministic | 2 | 2 | 0 | 4 | 100% | 50% |
| DCL53-CPP | deterministic | 3 | 0 | 0 | 3 | 100% | 100% |
| DCL54-CPP | deterministic | 2 | 0 | 1 | 1 | 67% | 100% |
| DCL55-CPP | deterministic | 0 | 3 | 0 | 3 | n/a | 0% |
| DCL56-CPP | deterministic | 1 | 1 | 0 | 2 | 100% | 50% |
| DCL57-CPP | deterministic | 1 | 4 | 0 | 2 | 100% | 20% |
| DCL58-CPP | deterministic | 2 | 0 | 0 | 3 | 100% | 100% |
| DCL59-CPP | deterministic | 0 | 4 | 0 | 3 | n/a | 0% |
| DCL60-CPP | deterministic | 0 | 3 | 0 | 5 | n/a | 0% |
| ENV30-C | deterministic | 1 | 1 | 0 | 3 | 100% | 50% |
| ENV31-C | deterministic | 0 | 2 | 0 | 3 | n/a | 0% |
| ENV32-C | deterministic | 1 | 1 | 0 | 1 | 100% | 50% |
| ENV33-C | deterministic | 2 | 0 | 1 | 3 | 67% | 100% |
| ENV34-C | deterministic | 1 | 1 | 0 | 4 | 100% | 50% |
| ERR30-C | deterministic | 2 | 1 | 0 | 4 | 100% | 67% |
| ERR32-C | deterministic | 1 | 1 | 0 | 2 | 100% | 50% |
| ERR33-C | deterministic | 4 | 1 | 3 | 3 | 57% | 80% |
| ERR34-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| ERR50-CPP | deterministic | 0 | 0 | 0 | 1 | n/a | n/a |
| ERR51-CPP | deterministic | 0 | 2 | 0 | 2 | n/a | 0% |
| ERR52-CPP | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| ERR53-CPP | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| ERR54-CPP | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| ERR55-CPP | deterministic | 0 | 2 | 0 | 3 | n/a | 0% |
| ERR56-CPP | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| ERR57-CPP | deterministic | 0 | 2 | 0 | 4 | n/a | 0% |
| ERR58-CPP | deterministic | 3 | 0 | 0 | 4 | 100% | 100% |
| ERR59-CPP | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| ERR60-CPP | deterministic | 0 | 1 | 0 | 2 | n/a | 0% |
| ERR61-CPP | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| ERR62-CPP | deterministic | 1 | 0 | 0 | 2 | 100% | 100% |
| EXP30-C | deterministic | 1 | 2 | 0 | 5 | 100% | 33% |
| EXP32-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| EXP33-C | deterministic | 3 | 3 | 0 | 6 | 100% | 50% |
| EXP34-C | deterministic | 3 | 0 | 1 | 2 | 75% | 100% |
| EXP35-C | deterministic | 3 | 0 | 1 | 3 | 75% | 100% |
| EXP36-C | deterministic | 0 | 3 | 0 | 3 | n/a | 0% |
| EXP37-C | deterministic | 1 | 3 | 0 | 5 | 100% | 25% |
| EXP39-C | deterministic | 2 | 2 | 0 | 4 | 100% | 50% |
| EXP40-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| EXP42-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| EXP43-C | deterministic | 3 | 3 | 0 | 6 | 100% | 50% |
| EXP44-C | deterministic | 3 | 1 | 0 | 4 | 100% | 75% |
| EXP45-C | deterministic | 3 | 0 | 0 | 7 | 100% | 100% |
| EXP46-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| EXP50-CPP | deterministic | 4 | 0 | 0 | 6 | 100% | 100% |
| EXP51-CPP | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| EXP52-CPP | deterministic | 2 | 0 | 0 | 2 | 100% | 100% |
| EXP53-CPP | deterministic | 0 | 4 | 0 | 4 | n/a | 0% |
| EXP54-CPP | deterministic | 2 | 5 | 0 | 8 | 100% | 29% |
| EXP55-CPP | deterministic | 3 | 0 | 0 | 2 | 100% | 100% |
| EXP56-CPP | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| EXP57-CPP | deterministic | 1 | 1 | 0 | 3 | 100% | 50% |
| EXP58-CPP | deterministic | 1 | 1 | 0 | 3 | 100% | 50% |
| EXP59-CPP | deterministic | 0 | 2 | 0 | 2 | n/a | 0% |
| EXP60-CPP | deterministic | 0 | 2 | 0 | 2 | n/a | 0% |
| EXP61-CPP | deterministic | 1 | 0 | 0 | 2 | 100% | 100% |
| EXP62-CPP | deterministic | 1 | 1 | 0 | 2 | 100% | 50% |
| EXP63-CPP | deterministic | 1 | 1 | 0 | 3 | 100% | 50% |
| FIO30-C | deterministic | 2 | 0 | 0 | 3 | 100% | 100% |
| FIO32-C | deterministic | 0 | 2 | 0 | 2 | n/a | 0% |
| FIO34-C | deterministic | 3 | 0 | 2 | 1 | 60% | 100% |
| FIO37-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| FIO38-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| FIO39-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| FIO40-C | deterministic | 1 | 0 | 1 | 0 | 50% | 100% |
| FIO41-C | deterministic | 0 | 2 | 0 | 2 | n/a | 0% |
| FIO42-C | deterministic | 1 | 3 | 0 | 4 | 100% | 25% |
| FIO44-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| FIO45-C | deterministic | 1 | 0 | 0 | 2 | 100% | 100% |
| FIO46-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| FIO47-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| FIO50-CPP | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| FIO51-CPP | deterministic | 1 | 0 | 0 | 2 | 100% | 100% |
| FLP30-C | deterministic | 2 | 0 | 0 | 2 | 100% | 100% |
| FLP32-C | deterministic | 1 | 3 | 1 | 3 | 50% | 25% |
| FLP34-C | deterministic | 1 | 1 | 1 | 1 | 50% | 50% |
| FLP36-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| FLP37-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| INT04-C | partial | 1 | 2 | 1 | 2 | 50% | 33% |
| INT09-C | deterministic | 1 | 0 | 0 | 3 | 100% | 100% |
| INT30-C | deterministic | 3 | 0 | 0 | 8 | 100% | 100% |
| INT31-C | deterministic | 3 | 3 | 1 | 5 | 75% | 50% |
| INT32-C | deterministic | 3 | 4 | 0 | 11 | 100% | 43% |
| INT33-C | deterministic | 2 | 0 | 0 | 2 | 100% | 100% |
| INT34-C | deterministic | 3 | 0 | 0 | 3 | 100% | 100% |
| INT35-C | deterministic | 1 | 0 | 0 | 5 | 100% | 100% |
| INT36-C | deterministic | 3 | 0 | 0 | 2 | 100% | 100% |
| INT50-CPP | deterministic | 1 | 0 | 1 | 2 | 50% | 100% |
| MEM04-C | partial | 0 | 2 | 0 | 2 | n/a | 0% |
| MEM30-C | deterministic | 3 | 1 | 1 | 3 | 75% | 75% |
| MEM31-C | deterministic | 1 | 0 | 1 | 0 | 50% | 100% |
| MEM33-C | deterministic | 0 | 3 | 0 | 3 | n/a | 0% |
| MEM34-C | deterministic | 2 | 0 | 1 | 1 | 67% | 100% |
| MEM35-C | deterministic | 2 | 0 | 1 | 2 | 67% | 100% |
| MEM36-C | deterministic | 1 | 0 | 0 | 2 | 100% | 100% |
| MEM50-CPP | deterministic | 4 | 0 | 0 | 7 | 100% | 100% |
| MEM51-CPP | deterministic | 8 | 0 | 0 | 8 | 100% | 100% |
| MEM52-CPP | deterministic | 1 | 1 | 0 | 5 | 100% | 50% |
| MEM53-CPP | deterministic | 1 | 1 | 0 | 2 | 100% | 50% |
| MEM54-CPP | deterministic | 3 | 0 | 0 | 3 | 100% | 100% |
| MEM55-CPP | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| MEM56-CPP | deterministic | 1 | 2 | 0 | 3 | 100% | 33% |
| MEM57-CPP | deterministic | 1 | 0 | 1 | 0 | 50% | 100% |
| MSC12-C | partial | 0 | 7 | 0 | 10 | n/a | 0% |
| MSC24-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| MSC30-C | deterministic | 1 | 0 | 0 | 2 | 100% | 100% |
| MSC32-C | deterministic | 0 | 1 | 0 | 2 | n/a | 0% |
| MSC33-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| MSC37-C | deterministic | 1 | 2 | 0 | 2 | 100% | 33% |
| MSC38-C | deterministic | 0 | 2 | 0 | 2 | n/a | 0% |
| MSC39-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| MSC40-C | deterministic | 3 | 1 | 0 | 3 | 100% | 75% |
| MSC50-CPP | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| MSC51-CPP | deterministic | 2 | 0 | 0 | 1 | 100% | 100% |
| MSC52-CPP | deterministic | 2 | 0 | 0 | 2 | 100% | 100% |
| MSC53-CPP | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| MSC54-CPP | deterministic | 0 | 2 | 0 | 2 | n/a | 0% |
| OOP50-CPP | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| OOP51-CPP | deterministic | 1 | 1 | 0 | 4 | 100% | 50% |
| OOP52-CPP | deterministic | 0 | 2 | 0 | 1 | n/a | 0% |
| OOP53-CPP | deterministic | 1 | 1 | 0 | 2 | 100% | 50% |
| OOP54-CPP | deterministic | 1 | 0 | 0 | 3 | 100% | 100% |
| OOP55-CPP | deterministic | 0 | 2 | 0 | 2 | n/a | 0% |
| OOP56-CPP | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| OOP57-CPP | deterministic | 2 | 1 | 0 | 3 | 100% | 67% |
| OOP58-CPP | deterministic | 0 | 0 | 0 | 1 | n/a | n/a |
| POS34-C | partial | 1 | 0 | 0 | 3 | 100% | 100% |
| POS36-C | partial | 0 | 1 | 0 | 1 | n/a | 0% |
| POS44-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| POS47-C | deterministic | 2 | 0 | 0 | 1 | 100% | 100% |
| POS48-C | partial | 0 | 1 | 0 | 1 | n/a | 0% |
| POS50-C | partial | 1 | 1 | 0 | 4 | 100% | 50% |
| POS51-C | partial | 0 | 1 | 0 | 1 | n/a | 0% |
| POS52-C | partial | 0 | 1 | 0 | 2 | n/a | 0% |
| POS53-C | partial | 0 | 1 | 0 | 1 | n/a | 0% |
| PRE02-C | partial | 2 | 3 | 0 | 2 | 100% | 40% |
| PRE31-C | deterministic | 2 | 1 | 0 | 5 | 100% | 67% |
| PRE32-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| SIG30-C | deterministic | 2 | 1 | 0 | 3 | 100% | 67% |
| SIG31-C | deterministic | 1 | 0 | 0 | 2 | 100% | 100% |
| SIG34-C | deterministic | 0 | 1 | 0 | 2 | n/a | 0% |
| SIG35-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| STR02-C | partial | 0 | 2 | 0 | 2 | n/a | 0% |
| STR30-C | deterministic | 3 | 0 | 0 | 3 | 100% | 100% |
| STR31-C | deterministic | 2 | 6 | 2 | 10 | 50% | 25% |
| STR32-C | deterministic | 0 | 3 | 0 | 4 | n/a | 0% |
| STR34-C | deterministic | 1 | 2 | 0 | 2 | 100% | 33% |
| STR37-C | deterministic | 0 | 1 | 0 | 1 | n/a | 0% |
| STR38-C | deterministic | 0 | 3 | 0 | 2 | n/a | 0% |
| STR50-CPP | deterministic | 0 | 3 | 0 | 2 | n/a | 0% |
| STR51-CPP | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| STR52-CPP | deterministic | 0 | 1 | 0 | 3 | n/a | 0% |
| STR53-CPP | deterministic | 0 | 1 | 0 | 0 | n/a | 0% |

## Reading these numbers

* **Semgrep figures are in-sample.** The bundled rules in `data/semgrep/` were written while
  looking at these CERT examples, so their recall here overstates what they find in other code.
  This holds for both halves of the split: those rules predate it. An out-of-sample check on Ceph
  is in [analyzers.md](analyzers.md).
* **Dev and held-out rules.** Changes made after the split (the Clang taint and bounds checkers,
  the message-based split of `bugprone-narrowing-conversions`, the size-arithmetic Semgrep rule)
  were tuned on dev rules only, and the held-out rows are the check on them. The split is by rule,
  so a held-out rule (for example INT30-C, INT32-C, STR31-C, FLP34-C) was never looked at during
  that work, not even through a sibling example.
* **CodeQL** ran with one database per example and only the queries mapped to that example's
  rule. Whole-program queries (DCL40-C, DCL60-CPP) need two translation units, which a single
  example file does not have.
* **Infer** needs code that compiles; most fragments here do not compile standalone, so its
  recall on this corpus is low. It is more useful with a real `compile_commands.json`.
* **Deterministic tier** (a rule-specific `cert-*` check or CodeQL CERT query): misses come
  from fragments that do not compile, deliberately narrow checks, and checks that only look at
  headers. **Partial tier** (general checkers and Semgrep rules): typical patterns, not the
  whole rule.
* **llm-only** rules are not measured here. Their quality depends on the review packet and the
  reviewer, and is bounded by the grounding validator (rule ID plus a verbatim quote).
* False positives on compliant examples are mostly mapping noise from general analyzers (for
  example a leak checker mapped to several MEM rules); `--max-rules-per-location` and the
  confidence score rank these below rule-specific findings.
* For recall on real security bugs (upstream CVE and memory-safety fixes in Ceph, curl, libtiff,
  expat, libarchive, c-ares and OpenSSL) see [benchmark-real.md](benchmark-real.md).
