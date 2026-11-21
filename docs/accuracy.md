# Accuracy of the deterministic layer

Corpus: 1548 code examples taken from the CERT rule pages (commit `73ee7a0dbe77`); 708 noncompliant, 840 compliant. Run time 180s.

Toolchain: clang-tidy 19.1.7, clangsa 19.1.7, cppcheck 2.17.1

A noncompliant example is *detected* when the engine reports that example's own rule in the file; a compliant example is a *false positive* when it does. Precision = TP/(TP+FP), recall = TP/(TP+FN). Only rules with at least one runnable checker are scored; the rest are `llm-only` and are not measured here. The examples are short fragments, many do not compile standalone, so absolute numbers understate what the tools achieve on real code and the precision figure is optimistic because compliant fragments are tiny.

## Summary

| Group | Rules | TP | FN | FP | TN | Precision | Recall |
|---|---|---|---|---|---|---|---|
| all_scored | 103 | 105 | 147 | 5 | 303 | 95% | 42% |
| deterministic | 38 | 41 | 25 | 0 | 79 | 100% | 62% |
| partial | 65 | 64 | 122 | 5 | 224 | 93% | 34% |
| llm-only(not scored) | 268 | | | | | | |

## Per rule (rules with a runnable checker)

| Rule | Tier | TP | FN | FP | TN | Precision | Recall |
|---|---|---|---|---|---|---|---|
| ARR30-C | partial | 0 | 0 | 0 | 7 | n/a | n/a |
| ARR32-C | partial | 0 | 2 | 0 | 2 | n/a | 0% |
| ARR38-C | partial | 1 | 6 | 0 | 7 | 100% | 14% |
| CON33-C | partial | 1 | 0 | 0 | 1 | 100% | 100% |
| CON36-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
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
| EXP34-C | partial | 1 | 2 | 1 | 2 | 50% | 33% |
| EXP37-C | partial | 0 | 4 | 0 | 5 | n/a | 0% |
| EXP39-C | partial | 1 | 3 | 0 | 4 | 100% | 25% |
| EXP42-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| EXP50-CPP | partial | 2 | 2 | 0 | 6 | 100% | 50% |
| EXP51-CPP | partial | 1 | 0 | 0 | 1 | 100% | 100% |
| EXP53-CPP | partial | 0 | 4 | 0 | 4 | n/a | 0% |
| EXP54-CPP | partial | 2 | 5 | 0 | 8 | 100% | 29% |
| EXP55-CPP | partial | 3 | 0 | 0 | 2 | 100% | 100% |
| EXP58-CPP | partial | 1 | 1 | 0 | 3 | 100% | 50% |
| EXP61-CPP | partial | 1 | 0 | 0 | 2 | 100% | 100% |
| EXP62-CPP | partial | 1 | 1 | 0 | 2 | 100% | 50% |
| EXP63-CPP | partial | 1 | 1 | 0 | 3 | 100% | 50% |
| FIO38-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| FIO39-C | partial | 0 | 1 | 0 | 1 | n/a | 0% |
| FIO42-C | partial | 1 | 3 | 0 | 4 | 100% | 25% |
| FLP30-C | deterministic | 2 | 0 | 0 | 2 | 100% | 100% |
| FLP32-C | partial | 0 | 4 | 0 | 4 | n/a | 0% |
| FLP34-C | partial | 1 | 1 | 1 | 1 | 50% | 50% |
| FLP37-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| INT09-C | deterministic | 1 | 0 | 0 | 3 | 100% | 100% |
| INT31-C | partial | 1 | 5 | 0 | 6 | 100% | 17% |
| INT32-C | partial | 0 | 7 | 0 | 11 | n/a | 0% |
| INT33-C | partial | 0 | 2 | 0 | 2 | n/a | 0% |
| INT34-C | partial | 0 | 3 | 0 | 3 | n/a | 0% |
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
| POS34-C | partial | 0 | 1 | 0 | 3 | n/a | 0% |
| POS36-C | partial | 0 | 1 | 0 | 1 | n/a | 0% |
| POS44-C | deterministic | 1 | 0 | 0 | 1 | 100% | 100% |
| POS47-C | deterministic | 2 | 0 | 0 | 1 | 100% | 100% |
| POS52-C | partial | 0 | 1 | 0 | 2 | n/a | 0% |
| PRE02-C | partial | 2 | 3 | 0 | 2 | 100% | 40% |
| PRE31-C | partial | 2 | 1 | 0 | 5 | 100% | 67% |
| SIG30-C | deterministic | 1 | 2 | 0 | 3 | 100% | 33% |
| STR30-C | partial | 0 | 3 | 0 | 3 | n/a | 0% |
| STR31-C | partial | 2 | 6 | 1 | 11 | 67% | 25% |
| STR34-C | deterministic | 1 | 2 | 0 | 2 | 100% | 33% |
| STR51-CPP | partial | 1 | 0 | 0 | 1 | 100% | 100% |
| STR52-CPP | partial | 0 | 1 | 0 | 3 | n/a | 0% |
| STR53-CPP | partial | 0 | 1 | 0 | 0 | n/a | 0% |

## Reading these numbers

* **Deterministic tier** (a rule-specific `cert-*` checker exists): no false positives on the compliant
  examples, but recall is limited. Misses come from three causes: the example does not compile on its own
  (clang-tidy skips files with fatal errors), the check is deliberately narrow (for example
  `cert-msc24-c` only reports `_s`-style replacements when Annex K is available), or the check looks at
  declarations in headers only (`cert-dcl59-cpp` ignores anonymous namespaces in `.cc` files).
* **Partial tier** (general checkers mapped to the rule): they catch typical patterns, not the rule.
  Expect low recall; precision on this corpus is high because compliant fragments are tiny.
* **llm-only** rules are not measured here. Their quality depends on the review packet and the
  reviewer, and is bounded by the grounding validator (rule ID plus a verbatim quote).
* The five false positives are mapping noise from general analyzers (for example a leak checker that
  maps to MEM34-C); `--max-rules-per-location` and the confidence score exist to rank these below
  rule-specific findings.

