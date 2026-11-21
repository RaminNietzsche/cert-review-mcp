"""Unified-diff parsing and git helpers for diff mode."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def parse_unified_diff(text: str) -> dict[str, set[int]]:
    """Map path (b-side) -> set of added/changed line numbers in the new file."""
    out: dict[str, set[int]] = {}
    cur: str | None = None
    new_line = 0
    for line in text.splitlines():
        if line.startswith("+++ "):
            p = line[4:].split("\t")[0].strip()
            if p == "/dev/null":
                cur = None
            else:
                cur = p[2:] if p.startswith("b/") else p
                out.setdefault(cur, set())
            continue
        if line.startswith("--- ") or line.startswith("diff ") or line.startswith("index "):
            continue
        m = HUNK_RE.match(line)
        if m:
            new_line = int(m.group(1))
            continue
        if cur is None:
            continue
        if line.startswith("+"):
            out[cur].add(new_line)
            new_line += 1
        elif line.startswith("-"):
            continue
        elif line.startswith("\\"):
            continue
        else:
            new_line += 1
    return {k: v for k, v in out.items() if v}


def git_diff(repo: str | Path, base: str, head: str | None = None) -> str:
    cmd = ["git", "-C", str(repo), "diff", "-U0", "--no-color", "--no-ext-diff"]
    cmd.append(f"{base}..{head}" if head else base)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git diff failed: {r.stderr.strip()}")
    return r.stdout


def hunks_with_context(diff_text: str, context: int = 3) -> dict[str, list[tuple[int, int]]]:
    """Return merged (start, end) line ranges per file including context lines."""
    changed = parse_unified_diff(diff_text)
    res: dict[str, list[tuple[int, int]]] = {}
    for path, lines in changed.items():
        ranges: list[list[int]] = []
        for ln in sorted(lines):
            s, e = max(1, ln - context), ln + context
            if ranges and s <= ranges[-1][1] + 1:
                ranges[-1][1] = max(ranges[-1][1], e)
            else:
                ranges.append([s, e])
        res[path] = [(a, b) for a, b in ranges]
    return res
