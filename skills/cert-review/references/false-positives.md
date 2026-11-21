# False-positive guidance

Static findings are mapped from checker names to rules; the mapping is not
exact. Use the tier and confidence to decide how much to trust a finding.

| Source | Trust | Notes |
|---|---|---|
| `clang-tidy:cert-*` (rule-specific alias) | high | The checker was written for that rule. Still confirm the context. |
| `cppcheck:*`, `clangsa:*` mapped to a rule | medium | General bug finders. A leak checker may be mapped to several MEM rules; pick the best fit and report once. |
| LLM review (validated) | depends on the quote and the path you can show | Never report without a concrete path. |

## Quick triage

1. Open the line. Does the code do what the message says?
2. Is the operation guarded (check, bound, owner) in a way the analyzer cannot see?
3. Is the construct a documented project idiom (see the profile's `idioms` and
   `suppress` entries)? Profiles suppress known-noisy combinations with a reason.
4. Does the finding sit in a header-only macro or a third-party tree? Those are
   excluded by the profile; if one slips through, ignore it.
5. If it is a false positive that will recur, suggest a profile `suppress` entry
   (rule, path or code regex, and a reason) rather than silencing it inline.

## Known sources of noise

- **Files that do not compile standalone.** clang-tidy skips checks after a
  fatal error. Missing `compile_commands.json` is the usual cause; say so
  rather than reporting "no findings".
- **Macros** (`assert`-like, logging): PRE30/PRE31 style findings on project
  macros that evaluate their arguments once.
- **One checker, many rules.** General analyzers map to several rules;
  `--max-rules-per-location` keeps the best few.
- **Test code and generated parsers.** Profiles relax or skip these.

## Inline suppression

`// cert-review: ignore EXP34-C <reason>` on the line or the line before it.
Use only with the owner's agreement and always give a reason.
