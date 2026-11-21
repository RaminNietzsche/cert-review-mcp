# Review comment template

Keep comments short, specific and fixable. One comment per finding.

```
**CERT <RULE-ID>** — <rule title>
severity: <error|warning|note> · priority P<n> · level L<n>

<One or two sentences: what in THIS code violates the rule and what can go
wrong (crash, overflow, leak, race).>

**Suggested fix:**
<minimal compliant code, or a pointer to the compliant example in the rule>

> <verbatim quote from the rule, 20+ characters>

Rule: <URL>
```

`format_findings` produces this shape. Guidelines:

- Lead with the consequence, not the rule number.
- The fix must compile in context. If you are unsure, say what to change in
  words instead of writing code that may not build.
- Mention the checker when a tool found it (`found by clang-tidy:cert-err33-c`),
  and say "needs confirmation" when confidence is below 0.6.
- Never include secrets or customer data from the code under review.
- Group trivial repeats ("same pattern at lines 40, 52, 71") in one comment.
- Severity wording: `error` = fix before merge, `warning` = should fix,
  `note` = consider.
