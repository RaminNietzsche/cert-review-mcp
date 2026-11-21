# Judging rules no checker covers

`rule_coverage` reports which rules are `llm-only` (no checker mapped) and
`partial` (only general checkers). For those, the review packet gives you the
code hunk and candidate rules chosen by token heuristics. The heuristics decide
what to read, not what is wrong.

## Procedure per candidate rule

1. Read the rule's **title and first paragraph**: that is the requirement.
2. Read the **noncompliant example**: that is the pattern to look for.
3. Read the **compliant solution**: that is the shape of an acceptable fix.
4. Check the **exceptions** section if present.
5. Find the matching construct in the hunk. If you cannot point at a line,
   there is no finding.
6. Check the surroundings for what makes it safe: bounds check, `NULL` check,
   smart pointer owner, lock held by the caller, `noexcept`, a size already
   validated by the decoder.
7. Decide: **violation**, **possible violation** (say what is unknown), or
   **not applicable**. Only the first two are reported; label the second.

## What counts as evidence

- A concrete execution path from an untrusted or variable input to the unsafe
  operation, or a missing release on a visible path.
- Not evidence: "this function is long", "this pattern is often wrong", or a
  keyword match alone.

## Typical rule families

| Family | Look for | Usually safe when |
|---|---|---|
| MEM (heap) | allocation without owner, free then use, `delete` of the wrong type | RAII owner, single owner transferred with `std::move` |
| ARR / STR / CTR | index or length from input, `memcpy`/`strncpy` sizes, iterator reuse after mutation | bound checked in the same scope, container API that checks |
| INT | arithmetic on sizes/offsets before allocation or indexing, narrowing casts | range checked first, wider type used throughout |
| EXP | read of uninitialised data, null dereference, lifetime of references/lambdas | initialised at declaration, guard on every path |
| CON | lock/unlock pairing, condition waits without predicate, lock order | RAII guards, predicate overloads |
| ERR | ignored return values, throwing destructors, catch-all swallowing | result stored and checked, deliberate documented ignore |
| FIO / ENV / SIG / POS | unchecked file/process calls, signal-unsafe calls in handlers | checked and logged on failure |

## When to stay silent

- You cannot name the line.
- A check or owner that makes the code safe is visible and you cannot show a path around it.
- The rule's own **Exceptions** section covers the case.
- The rule is disabled by the profile (`disabled_rules`), with a reason.
