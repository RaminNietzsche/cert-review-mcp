"""Unified-diff parsing and git helpers for diff mode."""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
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
    cmd.append(f"{base}...{head}" if head else base)
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


def _relpath_from_marker(line: str, prefix: str) -> str | None:
    p = line[len(prefix) :].split("\t")[0].strip()
    if p == "/dev/null":
        return None
    if p.startswith("a/") or p.startswith("b/"):
        p = p[2:]
    return p


def reconstruct_file_contents(text: str) -> dict[str, list[str]]:
    """Rebuild post-patch line lists from a unified diff (paths as in +++ b/)."""
    files: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("+++ "):
            current = _relpath_from_marker(line, "+++ ")
            if current is not None:
                files.setdefault(current, [])
            continue
        if current is None:
            continue
        if line.startswith("@@") or line.startswith("---") or line.startswith("diff ") or line.startswith(
            "index "
        ):
            continue
        if line.startswith("\\"):
            continue
        if line.startswith("+"):
            files[current].append(line[1:])
        elif line.startswith(" "):
            files[current].append(line[1:])
        elif line.startswith("-"):
            pass
    return files


def _git_show(repo: Path, rev: str, relpath: str) -> str | None:
    """File contents at `rev:relpath`, or None if the path does not exist at that revision."""
    r = subprocess.run(
        ["git", "-C", str(repo), "show", f"{rev}:{relpath}"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return None
    return r.stdout


def _is_git_repo(path: Path) -> bool:
    try:
        r = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
        )
        return r.returncode == 0
    except OSError:
        return False


@dataclass
class DiffWorkspace:
    """Temporary checkout used for diff-mode analysis; never writes into the user's repo."""

    root: Path
    changed: dict[str, set[int]]
    _tmpdir: tempfile.TemporaryDirectory[str] | None = field(default=None, repr=False)
    _extra_dirs: list[Path] = field(default_factory=list, repr=False)

    def abs_changed(self) -> dict[str, set[int]]:
        return {str((self.root / k).resolve()): v for k, v in self.changed.items()}

    def cleanup(self) -> None:
        if self._tmpdir is not None:
            self._tmpdir.cleanup()
            self._tmpdir = None
        for d in self._extra_dirs:
            shutil.rmtree(d, ignore_errors=True)
        self._extra_dirs.clear()


def materialize_worktree(diff_text: str, root: Path | None = None) -> Path:
    """Write reconstructed files under root (or a new temp dir). Returns the checkout root."""
    files = reconstruct_file_contents(diff_text)
    if root is None:
        root = Path(tempfile.mkdtemp(prefix="cert-review-work-"))
    else:
        root = root.expanduser()
        root.mkdir(parents=True, exist_ok=True)
    root = root.resolve()
    for rel, lines in files.items():
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        body = "\n".join(lines)
        if lines:
            body += "\n"
        dest.write_text(body, encoding="utf-8", errors="surrogateescape")
    return root


def prepare_diff_workspace(
    repo: str | Path | None,
    diff_text: str,
    *,
    content_ref: str | None = None,
) -> DiffWorkspace:
    """Map changed lines to absolute paths under a private temporary tree.

    Never creates or modifies files in `repo`. When `repo` is a git checkout and
    `content_ref` is set (e.g. the diff's head revision), file bodies come from
    `git show content_ref:path` so line numbers match that revision; otherwise
  bodies are rebuilt from the unified diff.
    """
    changed = parse_unified_diff(diff_text)
    reconstructed = reconstruct_file_contents(diff_text)
    tmp = tempfile.TemporaryDirectory(prefix="cert-review-work-")
    root = Path(tmp.name).resolve()

    hint = Path(repo).expanduser() if repo else None
    repo_p = hint.resolve() if hint and hint.is_dir() else None
    use_git = bool(repo_p and content_ref and _is_git_repo(repo_p))

    for rel in set(changed) | set(reconstructed):
        body: str | None = None
        if use_git and rel in changed:
            body = _git_show(repo_p, content_ref, rel)
        if body is None and rel in reconstructed:
            lines = reconstructed[rel]
            body = "\n".join(lines)
            if lines:
                body += "\n"
        if body is None and repo_p and rel in changed and not content_ref:
            on_disk = repo_p / rel
            if on_disk.is_file():
                body = on_disk.read_text(encoding="utf-8", errors="surrogateescape")
        if body is None:
            continue
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8", errors="surrogateescape")

    return DiffWorkspace(root=root, changed=changed, _tmpdir=tmp)