"""Explain one finding: why it matches its rule, the closest CERT example pair, and a fix.

Everything is computed from the bundled rule database and, when given, the source file.
No network, no randomness: the same input always gives the same output.
"""
from __future__ import annotations

import difflib
import re
from pathlib import Path

from . import checkers_map as CM
from . import profiles as P
from . import rules as R

_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# Very common words that carry no signal for picking an example.
_STOP = {
    "int", "char", "void", "const", "return", "if", "else", "for", "while", "do", "unsigned",
    "signed", "long", "short", "static", "struct", "include", "h", "the", "a", "an", "of", "to",
    "is", "in", "and", "or", "this", "that", "be", "not", "std", "auto", "bool", "true", "false",
    "null", "nullptr", "func", "f", "i", "j", "n", "x", "p", "s", "error", "handle", "code",
}

# API-level replacements: token in the flagged code -> concrete advice.
API_FIXES: dict[str, str] = {
    "gets": "Replace gets() with fgets(buf, sizeof buf, stdin) and strip the trailing newline.",
    "strcpy": "Replace strcpy() with a bounded copy: check strlen(src) < sizeof dst first, or use snprintf(dst, sizeof dst, \"%s\", src).",
    "strcat": "Replace strcat() with a length-checked append (snprintf or strncat with the remaining space).",
    "sprintf": "Replace sprintf() with snprintf(buf, sizeof buf, ...) and check the return value for truncation.",
    "vsprintf": "Replace vsprintf() with vsnprintf(buf, sizeof buf, ...) and check for truncation.",
    "strncpy": "After strncpy(), terminate explicitly (dst[sizeof dst - 1] = '\\0') or use snprintf.",
    "atoi": "Replace atoi() with strtol(): reset errno, pass an end pointer, and check errno == ERANGE, end == str and *end.",
    "atol": "Replace atol() with strtol() and check errno, the end pointer and the range.",
    "atoll": "Replace atoll() with strtoll() and check errno, the end pointer and the range.",
    "atof": "Replace atof() with strtod() and check errno and the end pointer.",
    "sscanf": "Prefer strtol()/strtod() over sscanf() for numbers, or check sscanf's return count.",
    "rand": "Replace rand() with a properly seeded generator (random() seeded once, arc4random(), or <random> in C++).",
    "srand": "Seed once from a high-entropy source; do not reseed with time(NULL) in a loop.",
    "tmpnam": "Replace tmpnam() with mkstemp() and use the returned descriptor.",
    "tmpfile": "Create temporary files with mkstemp() in a private directory.",
    "mktemp": "Replace mktemp() with mkstemp().",
    "system": "Avoid system(); call execve()/posix_spawn() with an explicit argument vector and a fixed path.",
    "popen": "Avoid popen() with untrusted input; use posix_spawn() with an argument vector.",
    "malloc": "Check the result of malloc() for NULL before use, and compute the size with overflow checks.",
    "calloc": "Check the result of calloc() for NULL before use.",
    "realloc": "Assign realloc() to a temporary, check it for NULL, then replace the original pointer.",
    "free": "Set the pointer to NULL after free() and make sure no other alias is used afterwards.",
    "memcpy": "Check that the destination is large enough and that neither pointer is NULL before memcpy().",
    "strlen": "Make sure the string is null-terminated before calling strlen().",
    "signal": "In signal handlers call only async-signal-safe functions and write only volatile sig_atomic_t objects.",
    "getenv": "Copy the getenv() result before calling getenv() again, and check it for NULL.",
    "fopen": "Check fopen() for NULL; open with \"x\" (C11) or O_EXCL when creating files.",
    "fclose": "Check the return value of fclose() and do not use the FILE* afterwards.",
    "fgets": "Check fgets() for NULL and handle a missing trailing newline (long line).",
    "pthread_mutex_lock": "Check the lock result and unlock on every path (prefer RAII lock guards in C++).",
    "lock": "Use a scoped lock (std::lock_guard / std::unique_lock) so the mutex is released on every path.",
    "thrd_create": "Check thrd_create()'s result and join or detach every thread.",
    "new": "Prefer std::make_unique / std::make_shared over raw new, and match each new with the right delete.",
    "delete": "Match delete with new and delete[] with new[]; prefer smart pointers.",
    "strtok": "strtok() keeps hidden state and modifies its input; use strtok_r() on a copy.",
    "printf": "Never pass untrusted data as the format string: use printf(\"%s\", s).",
    "fprintf": "Never pass untrusted data as the format string: use fprintf(f, \"%s\", s).",
    "syslog": "Never pass untrusted data as the format string: use syslog(prio, \"%s\", s).",
    "setjmp": "Avoid setjmp/longjmp; restructure with return codes or exceptions (C++).",
    "assert": "Do not rely on assert() for input validation; it disappears with NDEBUG.",
    "chmod": "Operate on file descriptors (fchmod) to avoid TOCTOU races.",
    "access": "Do not check with access() then open; open directly and handle the error (TOCTOU).",
}

# Category-level advice used when no API matches.
CATEGORY_FIXES: dict[str, str] = {
    "PRE": "Wrap macro parameters and bodies in parentheses, avoid side effects in macro arguments, prefer inline functions.",
    "DCL": "Fix the declaration: give objects the right scope, linkage and qualifiers, and avoid reserved identifiers.",
    "EXP": "Make the expression well defined: check pointers for NULL, avoid unsequenced side effects and respect types.",
    "INT": "Check operands before the operation (range, wraparound, division by zero, shift width) or use a wider type.",
    "FLP": "Do not use floating point for loop counters or exact comparisons; check for domain and range errors.",
    "ARR": "Validate indexes and sizes against the array bounds before access; compute sizes with sizeof on the object.",
    "STR": "Reserve space for the terminating null, use bounded functions, and never modify string literals.",
    "MEM": "Pair every allocation with exactly one release, check allocations, and never use memory after freeing it.",
    "FIO": "Check every I/O call's return value, close what you open, and avoid race-prone file name operations.",
    "ENV": "Do not keep pointers returned by getenv() and similar across calls; copy and validate them.",
    "SIG": "Keep signal handlers minimal: async-signal-safe calls only, volatile sig_atomic_t flags.",
    "ERR": "Detect and handle the error status of every library call (errno, return codes, exceptions).",
    "API": "Validate parameters at the API boundary and document ownership and size contracts.",
    "CON": "Protect shared data with a lock held on every access path, and release locks on every path.",
    "MSC": "Use secure library facilities (strong random numbers, no dead or ambiguous code).",
    "POS": "Use the POSIX interfaces safely: check return values, avoid TOCTOU, drop privileges correctly.",
    "WIN": "Use the Windows API safely: check return values and release handles.",
    "CTR": "Keep iterators and indexes valid: check bounds and do not use iterators invalidated by container changes.",
    "OOP": "Respect object lifetime and construction order; make base class destructors virtual where needed.",
    "OBJ": "Respect object lifetime and construction order; make base class destructors virtual where needed.",
}


def tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "") if t.lower() not in _STOP and len(t) > 1}


def similarity(a: set[str], b: set[str]) -> float:
    """Jaccard similarity of two token sets (0..1)."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _code(block_list: list[dict]) -> str:
    return "\n".join(b["code"] for b in block_list or []).replace("\u00a0", " ")


def _first_sentence(text: str, limit: int = 400) -> str:
    t = re.sub(r"\s*\[code\]\s*", " ", text or "").strip()
    t = re.sub(r"\s+", " ", t)
    m = re.match(r"(.+?[.!?])(\s|$)", t)
    s = m.group(1) if m else t
    return s[:limit]


def read_snippet(file: str, line: int, context: int = 3) -> tuple[str, str]:
    """(flagged line, numbered snippet) from a local file, or ('', '') if unreadable."""
    try:
        lines = Path(file).expanduser().read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "", ""
    if not 1 <= line <= len(lines):
        return "", ""
    lo, hi = max(1, line - context), min(len(lines), line + context)
    snip = "\n".join(f"{'>' if n == line else ' '}{n:5d}| {lines[n - 1]}" for n in range(lo, hi + 1))
    return lines[line - 1], snip


def pick_example(rule: dict, query: set[str]) -> tuple[dict | None, list[dict]]:
    """Best (noncompliant, compliant) pair for the query tokens, plus the ranked list."""
    ranked = []
    for i, ex in enumerate(rule.get("examples") or []):
        nc = ex.get("noncompliant")
        if not nc or not ex.get("compliant"):
            continue
        nc_code = _code(nc["code"])
        nc_tokens = tokens(nc_code) | tokens(nc.get("heading", ""))
        score = similarity(query, nc_tokens)
        # The compliant solution closest to the noncompliant code is the smallest fix.
        best_c = max(ex["compliant"], key=lambda c: difflib.SequenceMatcher(
            None, nc_code, _code(c["code"])).ratio())
        ranked.append({"index": i, "score": round(score, 3),
                       "shared_tokens": sorted(query & nc_tokens)[:20],
                       "noncompliant": {"heading": nc["heading"], "code": nc_code},
                       "compliant": {"heading": best_c["heading"], "code": _code(best_c["code"]),
                                     "text": _first_sentence(best_c.get("text", ""), 600)}})
    ranked.sort(key=lambda r: (-r["score"], r["index"]))
    return (ranked[0] if ranked else None), ranked


def example_diff(nc_code: str, c_code: str) -> tuple[str, list[str]]:
    """Unified diff from the noncompliant to the compliant example, and the added lines."""
    a = [x.rstrip() for x in nc_code.splitlines()]
    b = [x.rstrip() for x in c_code.splitlines()]
    diff = list(difflib.unified_diff(a, b, "noncompliant", "compliant", lineterm="", n=1))
    added = [x[1:].strip() for x in diff if x.startswith("+") and not x.startswith("+++") and x[1:].strip()]
    return "\n".join(diff), added


def _matching_checker(rule_id: str, tool: str | None, checker: str | None) -> dict | None:
    e = CM.rule_entry(rule_id) or {}
    for c in e.get("checkers", []):
        if checker and c["checker"] == checker and (not tool or c["tool"] == tool):
            return c
    return None


def explain(finding: dict, profile: str = "default", context_lines: int = 3) -> dict:
    rule_id = str(finding.get("rule_id") or "").strip()
    r = R.get(rule_id)
    if r is None:
        near = [x["id"] for x in R.search(rule_id, 5)] if len(rule_id) > 1 else []
        return {"error": f"unknown rule {rule_id}", "did_you_mean": near}
    prof = P.load(profile)
    file, line = finding.get("file"), int(finding.get("line") or 0)
    code = finding.get("code") or ""
    snippet = ""
    if file and line:
        flagged, snippet = read_snippet(file, line, context_lines)
        if not code:
            code = flagged
    message = finding.get("message") or ""
    tool, checker = finding.get("tool"), finding.get("checker")

    # The flagged line and the message decide; the surrounding snippet is only a fallback.
    query = tokens(code) | tokens(message)
    if not query:
        query = tokens(snippet)
    best, ranked = pick_example(r, query)
    rule_vocab = tokens(R.rule_text(r))
    apis = sorted(t for t in (tokens(code) | tokens(message)) if t in API_FIXES and t in rule_vocab)

    # ---- why the finding matches
    why: list[str] = []
    c = _matching_checker(r["id"], tool, checker)
    if c:
        why.append(f"{c['tool']} checker {c['checker']} is mapped to {r['id']} as a "
                   f"{'rule-specific' if c['specific'] else 'general'} checker"
                   + ("" if c["specific"] else "; review the code to confirm the CERT rule applies") + ".")
    elif tool or checker:
        why.append(f"Reported by {tool or 'a tool'}{':' + checker if checker else ''}, mapped to {r['id']}.")
    else:
        why.append(f"The finding cites {r['id']}; no analyzer was named, so the match rests on the code itself.")
    if message:
        why.append(f"Message: {message.strip()[:300]}")
    if apis:
        why.append("The flagged code uses " + ", ".join(f"{a}()" for a in apis)
                   + f", which the text of {r['id']} discusses.")
    if best and best["shared_tokens"]:
        why.append(f"It shares {len(best['shared_tokens'])} identifier(s) with the CERT example "
                   f"'{best['noncompliant']['heading']}': {', '.join(best['shared_tokens'][:8])}.")
    ov = prof.override(r["id"])
    if ov.get("note"):
        why.append(f"Profile {prof.name}: {ov['note']}")
    disabled = prof.disabled(r["id"])
    if disabled:
        why.append(f"Profile {prof.name} disables this rule: {disabled}")

    # ---- fix
    steps: list[str] = []
    diff_text, added = "", []
    if best:
        diff_text, added = example_diff(best["noncompliant"]["code"], best["compliant"]["code"])
        steps.append(f"Follow '{best['compliant']['heading']}': {best['compliant']['text']}")
    for a in apis:
        steps.append(API_FIXES[a])
    cat_tip = CATEGORY_FIXES.get(r["category"])
    if cat_tip and not apis:
        steps.append(cat_tip)
    key_lines = [x for x in added if not x.startswith(("/*", "//", "#include", "}")) and x not in ("{", "/* ... */")]
    if key_lines:
        steps.append("Lines the compliant example adds: " + " | ".join(key_lines[:6]))
    summary = steps[1] if apis and len(steps) > 1 else (steps[0] if steps else cat_tip or "See the rule text.")

    risk = r.get("risk") or {}
    out = {
        "rule": {"id": r["id"], "title": r["title"], "lang": r["lang"], "category": r["category"],
                 "url": r["url"], "severity": risk.get("severity"), "priority": risk.get("priority"),
                 "level": risk.get("level"), "cwe": r.get("cwe", []),
                 "summary": _first_sentence(r.get("intro", ""), 500),
                 "coverage": (CM.rule_entry(r["id"]) or {}).get("tier_runnable")},
        "finding": {"file": file, "line": line or None, "tool": tool, "checker": checker,
                    "message": message or None, "code": code or None, "snippet": snippet or None},
        "why": why,
        "example": None,
        "fix": {"summary": summary, "steps": steps, "example_diff": diff_text,
                "category_advice": cat_tip},
        "alternatives": [{"index": x["index"], "heading": x["noncompliant"]["heading"],
                          "score": x["score"]} for x in ranked[1:4]],
        "profile": prof.name,
    }
    if best:
        out["example"] = {"index": best["index"], "similarity": best["score"],
                          "shared_tokens": best["shared_tokens"],
                          "noncompliant": best["noncompliant"], "compliant": best["compliant"]}
    if lang_warning := _lang_mismatch(r, file):
        out["why"].append(lang_warning)
    return out


def _lang_mismatch(r: dict, file: str | None) -> str | None:
    if file and r["lang"] == "cpp" and Path(file).suffix.lower() == ".c":
        return f"Note: {r['id']} is a C++ rule but {Path(file).name} is a C file."
    return None


def to_text(d: dict) -> str:
    """Plain-text rendering for the CLI."""
    r = d["rule"]
    out = [f"{r['id']}  {r['title']}", r["url"], "", r["summary"], ""]
    f = d["finding"]
    if f.get("file"):
        out.append(f"Finding: {f['file']}:{f.get('line') or '?'}")
    if f.get("snippet"):
        out += [f["snippet"], ""]
    elif f.get("code"):
        out += ["  " + f["code"], ""]
    out.append("Why it matches:")
    out += [f"  - {w}" for w in d["why"]]
    ex = d.get("example")
    if ex:
        out += ["", f"Closest example (similarity {ex['similarity']}): {ex['noncompliant']['heading']}",
                "--- noncompliant", ex["noncompliant"]["code"],
                f"--- {ex['compliant']['heading']}", ex["compliant"]["code"]]
    out += ["", "Suggested fix:"]
    out += [f"  - {s}" for s in d["fix"]["steps"]]
    return "\n".join(out)
