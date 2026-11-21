#!/usr/bin/env python3
"""Real-code benchmark: run the engine on upstream security fixes (benchmark/cases.yaml).

For every case the vulnerable revision (first parent of the fix) and the fixed revision are
checked out from a blobless clone, the touched C/C++ files are analysed with the full
deterministic layer (clang-tidy, Clang Static Analyzer, cppcheck), and findings are compared
with the lines the fix changes:

* vulnerable side: lines the fix removes or rewrites; for a pure insertion, the lines on both
  sides of the insertion point. A finding counts when it lies within --near lines of that region.
* detected:   a finding whose CERT rule is one of the case's `cert` rules, or whose rule shares
  a CWE with the case.
* wrong-rule: findings in the region, none of them matching.
* miss:       no finding in the region.
* fixed side: findings within --near lines of the lines the fix adds (false-positive load), and
  whether a matching finding is still reported there (then the detection is not fix-sensitive).

Without a real build there is no exact compile database; a file where clang-tidy reports
compile errors, or whose analysis times out, makes the case `partial`. Partial cases are scored
like the others and listed separately.

    python3 tools/run_real_benchmark.py --cache ~/.cache/cert-review-bench --jobs 8
    python3 tools/run_real_benchmark.py --only ceph-fix-2b4bef17 --keep
    python3 tools/run_real_benchmark.py --report-only        # re-render docs from results.json
"""
from __future__ import annotations

import argparse
import fnmatch
import glob
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cert_review import engine, profiles, rules as R, toolrun as T  # noqa: E402

CASES = ROOT / "benchmark" / "cases.yaml"
RESULTS = ROOT / "benchmark" / "results.json"
DOC = ROOT / "docs" / "benchmark-real.md"
HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")

# Minimal configuration headers so that project sources parse without running configure.
# They only declare what a typical Linux/glibc build would detect; anything else stays off.
_POSIX = """#define HAVE_UNISTD_H 1
#define HAVE_STDINT_H 1
#define HAVE_INTTYPES_H 1
#define HAVE_STDLIB_H 1
#define HAVE_STRING_H 1
#define HAVE_STRINGS_H 1
#define HAVE_SYS_TYPES_H 1
#define HAVE_SYS_STAT_H 1
#define HAVE_SYS_TIME_H 1
#define HAVE_FCNTL_H 1
#define HAVE_LIMITS_H 1
#define HAVE_ERRNO_H 1
#define HAVE_STDBOOL_H 1
#define HAVE_SYS_SOCKET_H 1
#define HAVE_NETINET_IN_H 1
#define HAVE_ARPA_INET_H 1
#define HAVE_NETDB_H 1
#define HAVE_SYS_SELECT_H 1
#define HAVE_POLL_H 1
#define HAVE_SYS_IOCTL_H 1
#define HAVE_SIGNAL_H 1
#define HAVE_TIME_H 1
#define HAVE_LOCALE_H 1
#define HAVE_SIZE_T 1
#define SIZEOF_INT 4
#define SIZEOF_LONG 8
#define SIZEOF_LONG_LONG 8
#define SIZEOF_SIZE_T 8
#define SIZEOF_OFF_T 8
#define SIZEOF_TIME_T 8
#define SIZEOF_VOIDP 8
#define STDC_HEADERS 1
"""
CONFIG_TEXT = {
    "curl": _POSIX + """#if !__has_include(<curl/curlbuild.h>)
#define SIZEOF_CURL_OFF_T 8
#endif
#define HAVE_BOOL_T 1
#define HAVE_STRUCT_TIMEVAL 1
#define HAVE_SOCKET 1
#define HAVE_SELECT 1
#define HAVE_RECV 1
#define HAVE_SEND 1
#define HAVE_SOCKADDR_IN6_SIN6_SCOPE_ID 1
#define HAVE_STRUCT_SOCKADDR_STORAGE 1
#define HAVE_LONGLONG 1
#define HAVE_FCNTL_O_NONBLOCK 1
#define HAVE_GETADDRINFO 1
#define HAVE_FREEADDRINFO 1
#define HAVE_SIGACTION 1
#define HAVE_POSIX_STRERROR_R 1
#define HAVE_STRERROR_R 1
#define HAVE_SNPRINTF 1
#define HAVE_STRDUP 1
#define HAVE_STRCASECMP 1
#define HAVE_STRTOLL 1
#define HAVE_FTRUNCATE 1
#define HAVE_GETTIMEOFDAY 1
#define HAVE_CLOCK_GETTIME_MONOTONIC 1
#define HAVE_IOCTL_FIONBIO 1
#define HAVE_PIPE 1
#define HAVE_SOCKETPAIR 1
#define CURL_SA_FAMILY_T sa_family_t
#define HAVE_SA_FAMILY_T 1
#define RECV_TYPE_ARG1 int
#define RECV_TYPE_ARG2 void *
#define RECV_TYPE_ARG3 size_t
#define RECV_TYPE_ARG4 int
#define RECV_TYPE_RETV ssize_t
#define SEND_TYPE_ARG1 int
#define SEND_QUAL_ARG2 const
#define SEND_TYPE_ARG2 void *
#define SEND_TYPE_ARG3 size_t
#define SEND_TYPE_ARG4 int
#define SEND_TYPE_RETV ssize_t
#define RECVFROM_TYPE_ARG1 int
#define RECVFROM_TYPE_ARG2 void
#define RECVFROM_TYPE_ARG2_IS_VOID 1
#define RECVFROM_TYPE_ARG3 size_t
#define RECVFROM_TYPE_ARG4 int
#define RECVFROM_TYPE_ARG5 struct sockaddr
#define RECVFROM_TYPE_ARG6 socklen_t
#define RECVFROM_TYPE_RETV ssize_t
#define GETNAMEINFO_TYPE_ARG1 struct sockaddr *
#define USE_IPV6 1
#define ENABLE_IPV6 1
#define OS "x86_64-pc-linux-gnu"
#define USE_NTLM 1
#define USE_NTRESPONSES 1
#define USE_OPENLDAP 1
#define USE_OPENSSL 1
#define CURL_DISABLE_LDAPS 0
""",
    "expat": _POSIX + """#define BYTEORDER 1234
#define HAVE_MEMMOVE 1
#define XML_DEV_URANDOM 1
#define HAVE_GETRANDOM 1
""",
    "libtiff": "#include <stdint.h>\n#include <stddef.h>\n" + _POSIX + """#define TIFF_INT64_T int64_t
#define TIFF_UINT64_T uint64_t
#define TIFF_SSIZE_T int64_t
#define TIFF_SIZE_T size_t
#define HAVE_IEEEFP 1
#define HOST_FILLORDER FILLORDER_LSB2MSB
#define HOST_BIGENDIAN 0
#define TIFF_INT8_T signed char
#define TIFF_UINT8_T unsigned char
#define TIFF_INT16_T signed short
#define TIFF_UINT16_T unsigned short
#define TIFF_INT32_T signed int
#define TIFF_UINT32_T unsigned int
#define TIFF_PTRDIFF_T ptrdiff_t
#define TIFF_INT32_FORMAT "%d"
#define TIFF_UINT32_FORMAT "%u"
#define TIFF_INT64_FORMAT "%ld"
#define TIFF_UINT64_FORMAT "%lu"
#define TIFF_SSIZE_FORMAT "%ld"
#define TIFF_SIZE_FORMAT "%zu"
#define SIZEOF_SIGNED_LONG 8
#define SIZEOF_UNSIGNED_LONG 8
#define SIZEOF_SIGNED_INT 4
#define SIZEOF_UNSIGNED_CHAR_P 8
#define LZW_SUPPORT 1
#define PACKBITS_SUPPORT 1
#define HAVE_GETOPT 1
#define HAVE_MMAP 1
#define HAVE_ASSERT_H 1
""",
    "libarchive": _POSIX + """#define HAVE_WCHAR_H 1
#define HAVE_WCHAR_T 1
#define HAVE_INTMAX_T 1
#define HAVE_UINTMAX_T 1
#define HAVE_UNSIGNED_LONG_LONG 1
#define HAVE_LONG_LONG_INT 1
#define HAVE_DECL_SIZE_MAX 1
#define HAVE_DECL_INT64_MAX 1
#define HAVE_DECL_INT64_MIN 1
#define HAVE_DECL_UINT64_MAX 1
#define HAVE_DECL_UINT32_MAX 1
#define HAVE_DECL_INT32_MAX 1
#define HAVE_DECL_INT32_MIN 1
#define HAVE_DECL_INTMAX_MAX 1
#define HAVE_DECL_INTMAX_MIN 1
#define HAVE_DECL_UINTMAX_MAX 1
#define HAVE_ZLIB_H 1
#define HAVE_GRP_H 1
#define HAVE_PWD_H 1
#define HAVE_LANGINFO_H 1
#define HAVE_NL_LANGINFO 1
#define HAVE_STRFTIME 1
#define HAVE_LOCALTIME_R 1
#define HAVE_TIMEGM 1
#define HAVE_DIRENT_H 1
#define HAVE_SYS_WAIT_H 1
#define HAVE_UTIME_H 1
#define HAVE_CTYPE_H 1
#define HAVE_STDARG_H 1
""",
    "c-ares": _POSIX + """#define HAVE_SYS_UIO_H 1
#define HAVE_ARPA_NAMESER_H 1
#define HAVE_ARPA_NAMESER_COMPAT_H 1
#define HAVE_BOOL_T 1
#define HAVE_STRUCT_TIMEVAL 1
#define HAVE_SOCKET 1
#define HAVE_RECV 1
#define HAVE_SEND 1
#define HAVE_RECVFROM 1
#define HAVE_GETHOSTNAME 1
#define HAVE_STRDUP 1
#define HAVE_STRCASECMP 1
#define HAVE_STRNCASECMP 1
#define HAVE_FCNTL_O_NONBLOCK 1
#define HAVE_STRUCT_SOCKADDR_IN6 1
#define HAVE_STRUCT_ADDRINFO 1
#define HAVE_STRUCT_IN6_ADDR 1
#define HAVE_AF_INET6 1
#define HAVE_PF_INET6 1
#define HAVE_GETSERVBYPORT_R 1
#define GETSERVBYPORT_R_ARGS 6
#define GETHOSTNAME_TYPE_ARG2 size_t
#define RECV_TYPE_ARG1 int
#define RECV_TYPE_ARG2 void *
#define RECV_TYPE_ARG3 size_t
#define RECV_TYPE_ARG4 int
#define RECV_TYPE_RETV ssize_t
#define RECVFROM_TYPE_ARG1 int
#define RECVFROM_TYPE_ARG2 void *
#define RECVFROM_TYPE_ARG3 size_t
#define RECVFROM_TYPE_ARG4 int
#define RECVFROM_TYPE_ARG5 struct sockaddr *
#define RECVFROM_TYPE_ARG6 socklen_t *
#define RECVFROM_TYPE_RETV ssize_t
#define RECVFROM_QUAL_ARG5
#define SEND_TYPE_ARG1 int
#define SEND_QUAL_ARG2 const
#define SEND_TYPE_ARG2 void *
#define SEND_TYPE_ARG3 size_t
#define SEND_TYPE_ARG4 int
#define SEND_TYPE_RETV ssize_t
#define HAVE_WRITEV 1
""",
}


def sh(args: list[str], cwd: Path | None = None, check: bool = True, timeout: int = 3600) -> str:
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(args[:6])}: {r.stderr.strip()[:400]}")
    return r.stdout


def git(bare: Path, *a: str, **kw) -> str:
    return sh(["git", "--git-dir", str(bare), *a], **kw)


# ---------------------------------------------------------------- checkout

def ensure_clone(cache: Path, name: str, repo: str) -> Path:
    bare = cache / "repos" / f"{name}.git"
    if not bare.exists():
        bare.parent.mkdir(parents=True, exist_ok=True)
        print(f"[clone] {repo} (blobless)", flush=True)
        sh(["git", "clone", "--bare", "--filter=blob:none", "--quiet", repo, str(bare)])
        # lazy blob fetches add many small packs; an automatic gc in the middle of a run is slow
        git(bare, "config", "gc.auto", "0")
        git(bare, "config", "maintenance.auto", "false")
    return bare


def ensure_commit(bare: Path, sha: str) -> None:
    if subprocess.run(["git", "--git-dir", str(bare), "cat-file", "-e", sha + "^{commit}"],
                      capture_output=True).returncode != 0:
        git(bare, "fetch", "--quiet", "--filter=blob:none", "origin", sha)


def checkout(bare: Path, wt: Path, sha: str, sparse: list[str] | None, files: list[str]) -> None:
    if not wt.exists():
        git(bare, "worktree", "add", "--no-checkout", "--detach", str(wt), sha)
        if sparse:
            sh(["git", "sparse-checkout", "init", "--no-cone"], cwd=wt)
            pats = list(sparse) + ["/" + f for f in files]
            sh(["git", "sparse-checkout", "set", "--no-cone", *pats], cwd=wt)
    sh(["git", "checkout", "--quiet", "--force", "--detach", sha], cwd=wt)


def populate_submodules(cache: Path, bare: Path, wt: Path, sha: str, paths: list[str]) -> list[str]:
    """Check out header-only submodules (e.g. Ceph's src/fmt) at the commit the superproject pins."""
    done = []
    try:
        gm = git(bare, "show", f"{sha}:.gitmodules")
    except RuntimeError:
        return done
    urls = dict(re.findall(r"path\s*=\s*(\S+)\s+url\s*=\s*(\S+)", gm))
    for path in paths:
        ent = git(bare, "ls-tree", sha, path, check=False).split()
        if len(ent) < 3 or ent[1] != "commit" or path not in urls:
            continue
        url = urls[path]
        if url.startswith("../"):
            url = "https://github.com/ceph/" + url[3:]
        sub = ensure_clone(cache, "sub-" + path.replace("/", "_"), url)
        try:
            ensure_commit(sub, ent[2])
        except RuntimeError:
            continue
        dst = wt / path
        if (dst / ".git").exists():
            sh(["git", "checkout", "--quiet", "--force", "--detach", ent[2]], cwd=dst)
        else:
            shutil.rmtree(dst, ignore_errors=True)
            git(sub, "worktree", "prune")
            git(sub, "worktree", "add", "--force", "--detach", str(dst), ent[2])
        done.append(path)
    return done


# ---------------------------------------------------------------- diff regions

def regions(diff: str) -> tuple[dict[str, set[int]], dict[str, set[int]]]:
    """-> (vulnerable lines per file on the old side, fixed lines per file on the new side)."""
    old: dict[str, set[int]] = defaultdict(set)
    new: dict[str, set[int]] = defaultdict(set)
    cur = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            p = line[4:].strip()
            cur = p[2:] if p.startswith("b/") else None
            continue
        m = HUNK.match(line)
        if not m or cur is None:
            continue
        os_, oc = int(m[1]), int(m[2]) if m[2] is not None else 1
        ns, nc = int(m[3]), int(m[4]) if m[4] is not None else 1
        if oc:
            old[cur].update(range(os_, os_ + oc))
        else:  # pure insertion after old line os_: both neighbours
            old[cur].update({os_, os_ + 1})
        if nc:
            new[cur].update(range(ns, ns + nc))
        else:
            new[cur].update({ns - 1, ns})
    return old, new


def widen(lines: set[int], near: int) -> set[int]:
    return {x for n in lines for x in range(n - near, n + near + 1)}


# ---------------------------------------------------------------- build flags

def ceph_std(date: str) -> str:
    y = int(date[:4])
    return "c++14" if y <= 2017 else "c++17" if y <= 2020 else "c++20" if y <= 2023 else "c++23"


GENERATED_MARK = "/* generated by run_real_benchmark.py */\n"


def config_headers(proj: dict) -> list[dict]:
    ch = proj.get("config_header") or []
    return [ch] if isinstance(ch, dict) else list(ch)


def write_compdb(case: dict, proj: dict, wt: Path, files: list[str], out: Path,
                 generated: list[Path]) -> tuple[Path | None, str]:
    """Write compile_commands.json for `files`; files created in the checkout go to `generated`."""
    out.mkdir(parents=True, exist_ok=True)
    if proj.get("compdb") == "ceph":
        dirs = sorted({str(Path(f).parent) for f in files})
        r = subprocess.run([sys.executable, str(ROOT / "tools/ceph_compdb.py"), "--ceph", str(wt),
                            "--out", str(out), "--std", ceph_std(case["fix_date"]), *dirs],
                           capture_output=True, text=True)
        if r.returncode != 0 or not (out / "compile_commands.json").exists():
            return None, "ceph_compdb failed: " + r.stderr.strip()[-300:]
        db = json.loads((out / "compile_commands.json").read_text())
        extra = [f"-I{wt / d}" for d in proj.get("includes", []) if (wt / d).is_dir()]
        for e in db:
            e["arguments"][1:1] = extra
        args = db[0]["arguments"][:-2] if db else []
        have = {e["file"] for e in db}
        for f in files:   # headers and files outside the listed dirs
            p = str(wt / f)
            if p not in have and args:
                lang = ["-x", "c++-header"] if p.endswith((".h", ".hpp")) else []
                db.append({"directory": str(wt / "src"), "file": p, "arguments": [*args, *lang, "-c", p]})
        (out / "compile_commands.json").write_text(json.dumps(db, indent=1))
        return out, "ceph_compdb.py"
    inc = out / "inc"
    if inc.exists():
        shutil.rmtree(inc)
    inc.mkdir()
    for dst, src in (proj.get("copy_if_missing") or {}).items():
        if not (wt / dst).exists() and (wt / src).exists():
            shutil.copyfile(wt / src, wt / dst)
            generated.append(wt / dst)
    for dst, pats in (proj.get("header_links") or {}).items():
        d = inc / dst
        d.mkdir(parents=True, exist_ok=True)
        for pat in pats:
            for h in sorted(glob.glob(str(wt / pat))):
                link = d / Path(h).name
                if not link.exists():
                    link.symlink_to(h)
    cfg_dirs = []
    for ch in config_headers(proj):
        p = wt / ch["path"]
        if not p.exists() or p.read_text(errors="replace").startswith(GENERATED_MARK):
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(GENERATED_MARK + CONFIG_TEXT.get(ch["text"], _POSIX))
            generated.append(p)
        cfg_dirs.append(p.parent)
    flags = ["-D_GNU_SOURCE", "-Wno-everything", "-ferror-limit=0"]
    flags += [f"-D{d}" for d in proj.get("defines", [])]
    if proj.get("header_links"):
        flags.append(f"-I{inc}")
    flags += [f"-I{wt / d}" for d in proj.get("includes", [])]
    flags += [f"-I{d}" for d in dict.fromkeys(cfg_dirs)]
    db = []
    for f in files:
        p = wt / f
        cpp = p.suffix in (".cc", ".cpp", ".cxx", ".hpp")
        cc = "clang++" if cpp else "clang"
        std = "-std=c++17" if cpp else "-std=gnu11"
        db.append({"directory": str(p.parent), "file": str(p),
                   "arguments": [cc, std, *flags, f"-I{p.parent}", "-c", str(p)]})
    (out / "compile_commands.json").write_text(json.dumps(db, indent=1))
    return out, "generated flags"


# ---------------------------------------------------------------- scoring

def cwe_of(rule_id: str) -> set[str]:
    return set((R.get(rule_id) or {}).get("cwe") or [])


def matches(rule_id: str, case: dict) -> bool:
    return rule_id in case["cert"] or bool(cwe_of(rule_id) & set(case["cwe"]))


def analyse(wt: Path, files: list[str], compdb: Path | None, prof, jobs: int) -> dict:
    paths = [str(wt / f) for f in files if (wt / f).exists()]
    t0 = time.time()
    res = engine.check(paths, prof, root=wt, compdb=compdb, jobs=jobs,
                       max_rules_per_location=99, include_suppressed=False)
    partial, notes = [], []
    for st in res.tools:
        for p in st.files_with_errors + st.timed_out:
            rel = os.path.relpath(p, wt)
            if rel in files and rel not in partial:
                partial.append(rel)
        notes += st.notes
    fnd = [{"file": os.path.relpath(f.file, wt), "line": f.line, "rule": f.rule_id, "tool": f.tool,
            "checker": f.checker, "confidence": f.confidence, "message": f.message[:200]}
           for f in res.findings]
    return {"findings": fnd, "partial_files": partial, "seconds": round(time.time() - t0, 1),
            "tools": {st.tool: st.status for st in res.tools}, "notes": notes[:5]}


def in_region(fs: list[dict], reg: dict[str, set[int]], near: int) -> list[dict]:
    w = {k: widen(v, near) for k, v in reg.items()}
    return [f for f in fs if f["line"] in w.get(f["file"], ())]


def score(case: dict, vul: dict, fix: dict, old: dict, new: dict, near: int) -> dict:
    v_hits = in_region(vul["findings"], old, near)
    f_hits = in_region(fix["findings"], new, near)
    v_match = [f for f in v_hits if matches(f["rule"], case)]
    f_match = [f for f in f_hits if matches(f["rule"], case)]
    if not case["cert"]:
        outcome = "not-applicable"
    elif v_match:
        outcome = "detected"
    elif v_hits:
        outcome = "wrong-rule"
    else:
        outcome = "miss"
    return {
        "outcome": outcome,
        "fix_sensitive": bool(v_match) and not f_match,
        "partial": bool(vul["partial_files"] or fix["partial_files"]),
        "vulnerable_region_rules": sorted({f["rule"] for f in v_hits}),
        "matching": [{k: f[k] for k in ("file", "line", "rule", "checker")} for f in v_match],
        "fixed_region_findings": len(f_hits),
        "fixed_region_rules": sorted({f["rule"] for f in f_hits}),
        "fixed_region_matching": len(f_match),
        "file_findings_vulnerable": len(vul["findings"]),
        "file_findings_fixed": len(fix["findings"]),
        "region_lines": sum(len(v) for v in old.values()),
    }


def bench_profile():
    prof = profiles.load("default")
    prof.raw["min_level"] = "L3"
    prof.raw["include_recommendations"] = True
    prof.raw["suppress"] = []
    prof.raw["exclude_paths"] = []
    return prof


def run_case(case: dict, proj: dict, cache: Path, prof, jobs: int, near: int, keep: bool,
             slot: int = 0) -> dict:
    bare = ensure_clone(cache, case["project"], proj["repo"])
    ensure_commit(bare, case["fix_commit"])
    parent = git(bare, "rev-parse", case["fix_commit"] + "^1").strip()
    if parent != case["vulnerable_commit"]:
        raise RuntimeError(f"vulnerable_commit {case['vulnerable_commit']} is not the first parent {parent}")
    files = case["files"]
    diff = git(bare, "diff", "-U0", "--no-color", parent, case["fix_commit"], "--", *files)
    old, new = regions(diff)
    wt = cache / "work" / (case["project"] + (f"-{slot}" if slot else ""))
    out: dict = {"id": case["id"]}
    sides = {}
    for side, sha in (("vulnerable", parent), ("fixed", case["fix_commit"])):
        checkout(bare, wt, sha, proj.get("sparse"), files)
        populate_submodules(cache, bare, wt, sha, proj.get("submodules", []))
        generated: list[Path] = []
        cdb, how = write_compdb(case, proj, wt, files, cache / "compdb" / case["id"] / side, generated)
        sides[side] = analyse(wt, files, cdb, prof, jobs)
        sides[side]["flags"] = how
        for p in generated:   # keep the next checkout clean
            p.unlink(missing_ok=True)
    out.update(score(case, sides["vulnerable"], sides["fixed"], old, new, near))
    out["seconds"] = round(sides["vulnerable"]["seconds"] + sides["fixed"]["seconds"], 1)
    out["flags"] = sides["vulnerable"]["flags"]
    out["partial_files"] = sorted(set(sides["vulnerable"]["partial_files"]) | set(sides["fixed"]["partial_files"]))
    out["tool_status"] = sides["vulnerable"]["tools"]
    if not keep:
        shutil.rmtree(cache / "compdb" / case["id"], ignore_errors=True)
    return out


# ---------------------------------------------------------------- report

def pct(a: int, b: int) -> str:
    return f"{100 * a / b:.0f}%" if b else "n/a"


def render(cases: list[dict], results: dict, meta: dict) -> str:
    by_id = {c["id"]: c for c in cases}
    rs = [results[c["id"]] for c in cases if c["id"] in results and "error" not in results[c["id"]]]
    errs = [r for r in results.values() if "error" in r]
    scored = [r for r in rs if r["outcome"] != "not-applicable"]
    na = [r for r in rs if r["outcome"] == "not-applicable"]
    cnt = Counter(r["outcome"] for r in scored)
    fs = sum(1 for r in scored if r["fix_sensitive"])
    partial = [r for r in rs if r["partial"]]
    full = [r for r in scored if not r["partial"]]
    L = []
    L.append("# Real-code benchmark\n")
    L.append("How the deterministic layer does on real security bugs, not on the CERT rule examples. "
             "Generated by `tools/run_real_benchmark.py` from [`benchmark/cases.yaml`](../benchmark/cases.yaml); "
             "raw results are in [`benchmark/results.json`](../benchmark/results.json).\n")
    L.append("## Setup\n")
    proj = Counter(by_id[r["id"]]["project"] for r in rs)
    kinds = Counter(by_id[r["id"]]["kind"] for r in rs)
    L.append(f"- Corpus: {len(cases)} upstream fixes; {len(rs)} ran, {len(errs)} failed to run. "
             f"By project: " + ", ".join(f"{k} {v}" for k, v in proj.most_common()) + ". "
             f"{kinds.get('cve', 0)} have a CVE, {kinds.get('security-fix', 0)} are memory-safety or "
             "input-handling fixes from the Ceph history without a CVE.")
    L.append(f"- Each case: the vulnerable revision (first parent of the fix) and the fixed revision, "
             f"only the non-test C/C++ files the fix touches. Toolchain: {meta['toolchain']}.")
    L.append("- Profile: `default` with every level and the C recommendations enabled, no suppressions, "
             "`max_rules_per_location` 99, no confidence cut-off (the same settings as "
             "[accuracy.md](accuracy.md)).")
    L.append(f"- A finding is *in the region* when it is within {meta['near']} lines of a line the fix "
             "removes or rewrites (for a pure insertion, of the insertion point). *Detected* means a finding "
             "in the region whose CERT rule is one of the case's `cert` rules or shares a CWE with the case. "
             "*Wrong rule* means findings in the region, none matching. *Miss* means nothing in the region.")
    L.append("- *Fix-sensitive*: detected on the vulnerable side and no matching finding in the corresponding "
             "region of the fixed revision.")
    L.append("- No project was built. Ceph gets the generated compile database of `tools/ceph_compdb.py`; the "
             "C projects get include paths and a small generated config header. A case is *partial* when "
             "clang-tidy reported compile errors in a touched file or an analysis timed out.")
    L.append(f"- Run on {meta['date']}, {meta['seconds']:.0f}s of analysis.\n")
    L.append("## Headline\n")
    L.append("| Measure | Value |")
    L.append("|---|---|")
    L.append(f"| Cases with a CERT rule (scored) | {len(scored)} |")
    L.append(f"| Detected | {cnt['detected']} ({pct(cnt['detected'], len(scored))}) |")
    L.append(f"| Detected and fix-sensitive | {fs} ({pct(fs, len(scored))}) |")
    L.append(f"| Wrong rule only | {cnt['wrong-rule']} ({pct(cnt['wrong-rule'], len(scored))}) |")
    L.append(f"| Miss | {cnt['miss']} ({pct(cnt['miss'], len(scored))}) |")
    fd = sum(1 for r in full if r["outcome"] == "detected")
    L.append(f"| Detected, cases that parsed cleanly | {fd} of {len(full)} ({pct(fd, len(full))}) |")
    L.append(f"| Partial cases (compile errors or timeout) | {len(partial)} of {len(rs)} |")
    L.append(f"| Design/logic flaws without a CERT rule (not scored) | {len(na)} |")
    tot_fixed = sum(r["fixed_region_findings"] for r in rs)
    with_fixed = sum(1 for r in rs if r["fixed_region_findings"])
    L.append(f"| Findings in the fixed code's region (all rules) | {tot_fixed} in {with_fixed} of {len(rs)} cases |")
    L.append(f"| Matching findings still present after the fix | {sum(1 for r in scored if r['fixed_region_matching'])} cases |")
    L.append("")
    L.append("## By category\n")
    L.append("| Category | Cases | Detected | Fix-sensitive | Wrong rule | Miss | Partial | Recall |")
    L.append("|---|---|---|---|---|---|---|---|")
    cats = defaultdict(list)
    for r in scored:
        cats[by_id[r["id"]]["category"]].append(r)
    for k in sorted(cats, key=lambda k: (-len(cats[k]), k)):
        g = cats[k]
        c = Counter(r["outcome"] for r in g)
        L.append(f"| {k} | {len(g)} | {c['detected']} | {sum(r['fix_sensitive'] for r in g)} | {c['wrong-rule']} | "
                 f"{c['miss']} | {sum(r['partial'] for r in g)} | {pct(c['detected'], len(g))} |")
    L.append("")
    L.append("## By project\n")
    L.append("| Project | Cases scored | Detected | Partial | Recall |")
    L.append("|---|---|---|---|---|")
    projs = defaultdict(list)
    for r in scored:
        projs[by_id[r["id"]]["project"]].append(r)
    for k in sorted(projs, key=lambda k: -len(projs[k])):
        g = projs[k]
        d = sum(r["outcome"] == "detected" for r in g)
        L.append(f"| {k} | {len(g)} | {d} | {sum(r['partial'] for r in g)} | {pct(d, len(g))} |")
    L.append("")
    L.append("## Per case\n")
    L.append("| Case | Category | Expected | Outcome | Rules in vulnerable region | Fixed region | Partial |")
    L.append("|---|---|---|---|---|---|---|")
    for c in cases:
        r = results.get(c["id"])
        if not r:
            continue
        name = f"[{c['id']}]({c['sources'][0]})"
        if "error" in r:
            L.append(f"| {name} | {c['category']} | {', '.join(c['cert']) or '-'} | error | | | |")
            continue
        oc = r["outcome"] + (" (fix-sensitive)" if r["fix_sensitive"] else "")
        L.append(f"| {name} | {c['category']} | {', '.join(c['cert']) or '-'} | {oc} | "
                 f"{', '.join(r['vulnerable_region_rules']) or '-'} | {r['fixed_region_findings']} | "
                 f"{'yes' if r['partial'] else ''} |")
    L.append("")
    if errs:
        L.append("Cases that failed to run: " + ", ".join(f"`{r['id']}` ({r['error'][:80]})" for r in errs) + "\n")
    ana = ROOT / "benchmark" / "analysis.md"   # hand-written reading of the latest run
    if ana.exists():
        L.append(ana.read_text().rstrip() + "\n")
    L.append(NOTES)
    return "\n".join(L) + "\n"


NOTES = """## Reading these numbers

* **This is a recall test on hard cases.** Every case is a bug that shipped, passed review and
  usually other static analysis, and was found later by fuzzing, a reporter or a crash. A
  rule-example corpus ([accuracy.md](accuracy.md)) asks whether a checker fires on the textbook
  pattern; this one asks whether it fires on the line that was actually wrong.
* **The CERT rule per case is a judgement.** `cert` and `cwe` in `cases.yaml` were assigned by
  reading the fix; a different reader could pick a neighbouring rule. Matching by CWE as well as by
  rule ID softens this, and makes the score somewhat generous: a CWE-125 case counts as detected by
  any rule that lists CWE-125.
* **The region is narrow.** Only findings within a few lines of the changed lines count. A bug whose
  root cause is far from the line the fix touches (for example a format string built in one place
  and used in another) can be reported and still score as a miss.
* **No build.** Without the project's real compile flags some files do not parse completely
  (`partial`). The Clang-based checkers then see less of the translation unit; cppcheck is less
  affected. The partial rate is reported, not hidden, and the clean-parse recall is shown separately.
* **Fixed-side findings are not all false positives.** They are findings near the new code, any
  rule; many are the same pre-existing pattern on an untouched neighbouring line.
* **Logic and design flaws** (authorization, protocol, logging of secrets, resource lifetime) have
  no CERT coding rule and are listed with `cert: []`. They are in the corpus to show the boundary
  of a rule-based reviewer, not to be counted as checker misses.
* **Size.** About sixty cases: enough to see which categories the tools reach and which they do
  not, too few for fine-grained per-rule rates. Treat single-digit cells as anecdotes.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cases", default=str(CASES))
    ap.add_argument("--cache", default=os.environ.get("CERT_REVIEW_BENCH_CACHE",
                                                      str(Path.home() / ".cache/cert-review-bench")))
    ap.add_argument("--jobs", type=int, default=4, help="analyzer processes per case")
    ap.add_argument("--workers", type=int, default=1, help="cases analysed in parallel")
    ap.add_argument("--near", type=int, default=3, help="lines around the changed region that count")
    ap.add_argument("--only", nargs="*", help="case ids (fnmatch patterns)")
    ap.add_argument("--keep", action="store_true", help="keep generated compile databases")
    ap.add_argument("--out-json", default=str(RESULTS))
    ap.add_argument("--out-md", default=str(DOC))
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args()

    spec = yaml.safe_load(Path(a.cases).read_text())
    cases, projects = spec["cases"], spec["projects"]
    cache = Path(a.cache).expanduser().resolve()
    prev = json.loads(Path(a.out_json).read_text()) if Path(a.out_json).exists() else {}
    results: dict = dict(prev.get("results", {}))
    meta = prev.get("meta", {})
    if not a.report_only:
        prof = bench_profile()
        sel = [c for c in cases if not a.only or any(fnmatch.fnmatch(c["id"], p) for p in a.only)]
        t0 = time.time()
        lock = threading.Lock()
        slots = queue.Queue()
        for k in range(a.workers):
            slots.put(k)

        def one(i_c):
            i, c = i_c
            slot = slots.get()
            try:
                r = run_case(c, projects[c["project"]], cache, prof, a.jobs, a.near, a.keep, slot)
                msg = (f"{r['outcome']}{' partial' if r['partial'] else ''} "
                       f"rules={r['vulnerable_region_rules']} {r['seconds']}s")
            except Exception as e:  # keep going; the report lists failures
                r = {"id": c["id"], "error": str(e)}
                msg = f"error: {e}"
            finally:
                slots.put(slot)
            with lock:
                results[c["id"]] = r
                print(f"[{i}/{len(sel)}] {c['id']}: {msg}", flush=True)
                Path(a.out_json).write_text(json.dumps({"meta": meta, "results": results}, indent=1) + "\n")

        # clones are created before the pool starts so that workers never race on them
        for name in sorted({c["project"] for c in sel}):
            ensure_clone(cache, name, projects[name]["repo"])
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            list(ex.map(one, enumerate(sel, 1)))
        tc = ", ".join(f"{t} {T.version(t)}" for t in ("clang-tidy", "cppcheck") if T.which(t))
        meta = {"toolchain": tc, "near": a.near, "date": time.strftime("%Y-%m-%d"),
                "seconds": sum(r.get("seconds", 0) for r in results.values()),
                "wall_seconds": round(time.time() - t0)}
        Path(a.out_json).write_text(json.dumps({"meta": meta, "results": results}, indent=1) + "\n")
    Path(a.out_md).write_text(render(cases, results, meta))
    print(f"wrote {a.out_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
