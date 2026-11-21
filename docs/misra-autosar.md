# MISRA and AUTOSAR

cert-review covers three guideline sets next to SEI CERT C and C++, with the same
structure (one rule database, one finding schema, the same tools and formats):

| `standard` | Guideline set | Language | Entries | Classification |
|---|---|---|---|---|
| `cert-c` | SEI CERT C (rules + recommendations) | C | 305 | risk row (L1-L3) |
| `cert-cpp` | SEI CERT C++ | C++ | 83 | risk row (L1-L3) |
| `misra-c-2012` | MISRA C:2012 with Amendments 1-4 (the guideline set of MISRA C:2023) | C | 221 (21 directives, 200 rules) | 23 mandatory, 150 required, 48 advisory |
| `misra-cpp-2023` | MISRA C++:2023 | C++ | 178 (4 directives, 174 rules) | 5 mandatory, 123 required, 50 advisory |
| `autosar-cpp14` | AUTOSAR C++14 Coding Guidelines (AP Release 19-03) | C++ | 397 rules | 362 required, 35 advisory |

Groups: `cert` (default), `misra`, `autosar`, `all`.

> **No MISRA or AUTOSAR guideline text is bundled.** Those documents are copyrighted.
> The repository ships only facts about them (IDs, classification, AUTOSAR target and
> enforcement category, section numbers and topic names, checker mappings, SEI CERT
> cross-references) and a one-line summary written for this project in its own words,
> always labelled *"paraphrase written for cert-review; not the official text"*. Not
> every guideline has a summary yet (MISRA C: 221/221, MISRA C++: 51/178, AUTOSAR:
> 53/397); the others show their section name. If you hold a licence you can load your
> own copy of the texts (see [Licensed rule texts](#licensed-rule-texts)). Sources and
> licences: [NOTICE](../NOTICE). MISRA and AUTOSAR are trademarks of their owners; this
> project is not affiliated with or endorsed by them.

## Choosing standards

The default is CERT only, so existing calls, profiles and CI jobs behave as before.

| Where | How |
|---|---|
| MCP `list_rules`, `search_rules`, `get_rule_coverage` | `standard: "misra-c-2012"` (or `misra`, `autosar`, `all`, `cert-cpp`, ...) |
| MCP `get_rule` | any ID: `MISRA-C-2012-10.4`, `MISRA-C-2012-DIR-4.1`, `MISRA-CPP-2023-8.2.2`, `AUTOSAR-A5-2-2`; short forms such as `misra c 10.4`, `Dir 4.1`, `A5-2-2`, `M6-4-1` are accepted |
| MCP `check_files`, `check_diff` | `standards: ["misra-c-2012", "cert"]`; when omitted, the profile decides |
| Profile | `standards: [misra-c-2012, misra-cpp-2023]` |
| CLI | `cert-review check src --standards misra-c-2012,cert`, `cert-review rules --standard autosar --classification required`, `cert-review coverage --standard misra-cpp-2023` |
| GitHub Action / GitLab template | `profile: misra` or `profile: autosar` |

Bundled profiles:

- `profiles/misra.yaml`: MISRA C:2012 on `.c` files, MISRA C++:2023 on C++ files,
  severity from classification (mandatory = error, required = warning, advisory = note).
- `profiles/autosar.yaml`: AUTOSAR C++14, `-std=c++14`, same severity scheme.
- `profiles/default.yaml`, `profiles/ceph.yaml`: `standards: [cert]` (unchanged).

Add `cert` to a profile's `standards` to get both CERT and MISRA/AUTOSAR IDs in one run.
For MISRA/AUTOSAR findings, priority and level come from the classification
(mandatory L1, required L2, advisory L3), so `min_level` filters work the same way.
Inline suppression works with any ID: `// cert-review: ignore MISRA-C-2012-15.5 single exit not wanted here`.

## How findings are mapped

| Analyzer | MISRA C:2012 | MISRA C++:2023 | AUTOSAR C++14 |
|---|---|---|---|
| cppcheck MISRA addon (`--addon=misra`, open source) | 131 guidelines, one specific check each | - | - |
| cppcheck core checks (cppcheck's own `checkersidmapping.cpp`) | 42 mappings | 37 mappings | 63 mappings |
| clang-tidy (curated in `data/guideline_overlay.yaml`) | 13 guidelines | 12 guidelines | 17 guidelines |
| Clang Static Analyzer (curated) | 7 guidelines | 3 guidelines | 3 guidelines |

- With `misra-c-2012` selected, cppcheck runs with the MISRA addon on C files and its
  `misra-c2012-X.Y` IDs map one-to-one. The addon needs `python3` and cppcheck's
  `addons/` directory (both are in the Docker image and in Debian/Ubuntu/Homebrew
  packages). A private `--cppcheck-build-dir` is used, so read-only source trees work.
- No public clang-tidy or Clang Static Analyzer documentation cites MISRA or AUTOSAR
  IDs, so those mappings are curated here. A mapping is `specific` only when the check
  enforces the guideline itself (for example `misc-no-recursion` for MISRA C 17.2,
  `bugprone-switch-missing-default-case` for 16.4, `google-readability-casting` for
  AUTOSAR A5-2-2); general checks are recorded as non-specific and get lower
  confidence (0.6 instead of 0.9). Where one check serves several guidelines, a line
  pattern picks the right one (e.g. `readability-braces-around-statements` maps to
  AUTOSAR M6-3-1 on loops and M6-4-1 on `if`/`else`).
- MISRA C++:2023 is implemented by cppcheck only in its commercial edition; the
  open-source mappings are the cppcheck core checks and clang-tidy above.

## Coverage

Tiers as for CERT: `deterministic` (a guideline-specific check exists), `partial` (only
general checks are mapped), `llm-only` (no checker; manual review). "Runnable" counts
only checks present in the pinned toolchain (clang-tidy/clang 19.1.7, cppcheck 2.17.1).

| Standard | Total | Deterministic | Partial | No checker | Runnable: det / partial / none |
|---|---|---|---|---|---|
| MISRA C:2012 | 221 | 131 | 28 | 62 | 131 / 28 / 62 |
| MISRA C++:2023 | 178 | 4 | 31 | 143 | 4 / 31 / 143 |
| AUTOSAR C++14 | 397 | 5 | 51 | 341 | 5 / 51 / 341 |

AUTOSAR's own enforcement column: 329 automated, 22 partially automated, 46
non-automated; this is the document's view of decidability. MISRA decidability is not
recorded (`decidability: null`): no openly licensed source lists it.

### Measured

`python3 tools/measure_guidelines.py --cppcheck <cppcheck 2.17.1 clone>` (results from
2026-11-21, toolchain above):

- **MISRA C:2012 on cppcheck's addon test file** (`addons/test/misra/misra-test.c`,
  read from the cppcheck clone, not shipped here), all three analyzers,
  `--standards misra-c-2012`: the file annotates 541 lines with 120 distinct
  expected guideline IDs. cert-review reported 108 of the 120 IDs and hit 525 of the
  541 annotated lines (97%), with 914 findings in total.
- **MISRA C++:2023 and AUTOSAR C++14 on the 359 SEI CERT C++ example files**
  (`corpus/*-CPP`): 387 MISRA C++ findings on 20 distinct guidelines and 388 AUTOSAR
  findings on 25 distinct guidelines. No annotated MISRA C++ or AUTOSAR test suite is
  openly available, so precision and recall are not measured for them.

## SEI CERT cross-references

`get_rule` on a CERT rule lists related MISRA/AUTOSAR guidelines, and a MISRA/AUTOSAR
record lists related CERT rules:

- MISRA C:2012 ↔ CERT C: 134 guidelines, from the "Related Guidelines" tables of the
  SEI CERT C standard (CC BY 4.0).
- AUTOSAR C++14 ↔ CERT C++: 105 rules, from Appendix B.4 of the public AUTOSAR
  document (relations "identical", "small differences" and "significant differences").
- MISRA C++:2023: no openly licensed mapping exists; none is shipped.

## Licensed rule texts

If you have a licence for MISRA C:2012, MISRA C++:2023 or AUTOSAR C++14, point
cert-review at a local text file. The texts are then shown by `get_rule` /
`cert-review explain`, used in finding messages (and passed to the cppcheck addon as
`--rule-texts`), and required as quotes by `validate_findings`.

Paths, first match wins per standard:

```bash
export CERT_REVIEW_MISRA_C_TEXTS=/secure/misra_c_2012.txt
export CERT_REVIEW_MISRA_CPP_TEXTS=/secure/misra_cpp_2023.txt
export CERT_REVIEW_AUTOSAR_TEXTS=/secure/autosar_cpp14.txt
```

or in a profile:

```yaml
rule_texts:
  misra-c-2012: /secure/misra_c_2012.txt
  autosar-cpp14: /secure/autosar_cpp14.txt
```

Accepted formats (UTF-8, Windows-1252 or Latin-1; lines starting with `#` are ignored):

1. **The cppcheck addon format**, the same file you would pass to `misra.py --rule-texts`:
   an optional `Appendix A Summary of guidelines` line, then blocks of
   `Rule 10.4 Required` / `Dir 4.1 Required` followed by the headline (one or more lines).
2. **One guideline per line**: `<ID><TAB, " - " or ": "><text>`, with any accepted ID
   form, e.g. `MISRA-C-2012-10.4<TAB>...` or `A5-2-2: ...`.

`get_rule_coverage` reports per standard whether a text file is loaded and how many
entries it has (counts only, never the text). Files are read locally; nothing is
copied into the repository or uploaded. Keep the file outside your repository if your
licence does not allow sharing it.

## validate_findings and quotes

For CERT, an accepted finding must quote the rule text verbatim. For MISRA and AUTOSAR:

- **Without a licensed text file** for that standard, `quote` is optional: a finding is
  accepted on a valid guideline ID (correct language, inside the reviewed hunk,
  checked against the packet when the packet has candidates from that standard) and is
  returned with `grounding: "rule-id-only"`. A quote that is given is not checked,
  because there is no official text to check it against.
- **With a licensed text file**, the quote is required and must match that text, exactly
  as for CERT (`grounding: "quote"`).

`get_rule` returns `quote_required` and `text_source` (`licensed-file` or `none`) for
each guideline so a client can tell which case applies. Review packets
(`build_review_packet`) still select CERT rule texts only.

## Rebuilding the data

```bash
git clone --depth 1 --branch 2.17.1 https://github.com/danmar/cppcheck cppcheck
curl -LO https://www.autosar.org/fileadmin/standards/R22-11/AP/AUTOSAR_RS_CPP14Guidelines.pdf
pdftotext -layout AUTOSAR_RS_CPP14Guidelines.pdf autosar.txt
python3 tools/build_guidelines.py --cppcheck cppcheck --autosar autosar.txt
```

`build_guidelines.py` takes only IDs, classifications, enforcement/target and the CERT
traceability relations from these inputs; summaries and curated mappings come from
`data/guideline_overlay.yaml`. A unit test fails if any record carries a field outside
that set or a summary longer than one short line.

## Limitations

- Most MISRA C++ and AUTOSAR guidelines have no open-source checker; they rely on
  manual review. The MISRA C numbers depend on the cppcheck addon being installed.
- MISRA C:2012 IDs follow cppcheck's 2.17.1 list (Amendments 1-4, the MISRA C:2023
  set). MISRA C:2025 renumbering is not handled.
- AUTOSAR data is AP Release 19-03, the last AUTOSAR C++14 edition; AUTOSAR now points
  to MISRA C++:2023 for new work.
- `.h` files are treated as C++ unless the profile maps them to C.
