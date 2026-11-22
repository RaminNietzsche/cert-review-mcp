#!/usr/bin/env python3
"""CLI wrapper for cert_review.ceph_compdb."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cert_review.ceph_compdb import build_compdb, ensure_cached_compdb, is_ceph_tree  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ceph", required=True, type=Path)
    ap.add_argument("--out", type=Path,
                    help="output dir for --git-diff; tracked mode uses .cert-review/compdb-cache")
    ap.add_argument("--std", default="c++23")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--tracked", action="store_true",
                    help="all src/ C/C++ at HEAD minus vendor trees (cached under .cert-review)")
    ap.add_argument("--git-diff", metavar="REV",
                    help="only C/C++ files touched in this git diff (e.g. origin/main..HEAD)")
    ap.add_argument("dirs", nargs="*", help="directories relative to the ceph root, e.g. src/common")
    a = ap.parse_args()
    if not a.tracked and not a.git_diff and not a.dirs:
        print("provide --tracked, --git-diff and/or dirs", file=sys.stderr)
        return 2
    if a.tracked:
        dest = ensure_cached_compdb(a.ceph, force=a.force)
        if not dest:
            return 1
        out = dest
    else:
        if not a.out:
            print("--out is required without --tracked", file=sys.stderr)
            return 2
        out = build_compdb(a.ceph, a.out, git_diff=a.git_diff, dirs=a.dirs or None, std=a.std)
    n = len(json.loads((out / "compile_commands.json").read_text()))
    print(f"{n} compile commands -> {out}/compile_commands.json")
    if is_ceph_tree(a.ceph) and (a.ceph / ".cert-review/compdb-cache/current").exists():
        print(f"current -> {(a.ceph / '.cert-review/compdb-cache/current').resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())