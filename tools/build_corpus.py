#!/usr/bin/env python3
"""Build corpus/ from the CERT noncompliant and compliant code examples.

Each fenced example in data/rules.json becomes one file:
    corpus/<RULE>/nc<pair>_<n>.<c|cc>   noncompliant (must be flagged for RULE)
    corpus/<RULE>/ok<pair>_<n>.<c|cc>   compliant    (must not be flagged for RULE)
A prelude of common standard headers is prepended so that fragments that rely
on them still parse. corpus/manifest.json records the expectation per file.
The examples are MIT licensed upstream (see NOTICE).
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C_PRELUDE = """\
#include <assert.h>
#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <math.h>
#include <pthread.h>
#include <signal.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <wchar.h>
"""
CPP_PRELUDE = """\
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <mutex>
#include <new>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>
"""
C_LANGS = {"c", "C"}
CPP_LANGS = {"cpp", "c++", "cc", "C++", "cplusplus"}


def main() -> int:
    data = json.loads((ROOT / "data/rules.json").read_text())
    out = ROOT / "corpus"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    manifest = []
    for r in data["rules"]:
        rid = r["id"]
        for pi, ex in enumerate(r["examples"], 1):
            groups = []
            if ex["noncompliant"]:
                groups.append(("nc", True, [ex["noncompliant"]]))
            if ex["compliant"]:
                groups.append(("ok", False, ex["compliant"]))
            for kind, bad, items in groups:
                n = 0
                for it in items:
                    for b in it["code"]:
                        lang = (b["lang"] or "").strip()
                        want_cpp = r["lang"] == "cpp"
                        if lang in C_LANGS:
                            is_cpp = False
                        elif lang in CPP_LANGS:
                            is_cpp = True
                        elif not lang:
                            is_cpp = want_cpp
                        else:
                            continue      # shell, text, etc.
                        q = b.get("quality")
                        if q == "bad" and not bad or q == "good" and bad:
                            continue      # block quality disagrees with its heading
                        n += 1
                        d = out / rid
                        d.mkdir(exist_ok=True)
                        name = f"{kind}{pi}_{n}.{'cc' if is_cpp else 'c'}"
                        pre = CPP_PRELUDE if is_cpp else C_PRELUDE
                        (d / name).write_text(f"// corpus: {rid} {'noncompliant' if bad else 'compliant'}\n"
                                              + pre + "\n" + b["code"] + "\n")
                        manifest.append({"rule": rid, "file": f"{rid}/{name}", "violates": bad,
                                         "lang": "cpp" if is_cpp else "c",
                                         "heading": it["heading"]})
    (out / "manifest.json").write_text(json.dumps(
        {"source_commit": data["source"]["commit"], "files": manifest}, indent=1) + "\n")
    print(len(manifest), "corpus files;",
          sum(1 for m in manifest if m["violates"]), "noncompliant")
    return 0


if __name__ == "__main__":
    sys.exit(main())
