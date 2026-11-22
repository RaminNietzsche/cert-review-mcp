"""Approximate compile_commands.json for a Ceph checkout without a full build."""
from __future__ import annotations

import fnmatch
import hashlib
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

EXTRA_DEFS = """
#define HAVE_SYS_TYPES_H 1
#define HAVE_LINUX_TYPES_H 1
#define USE_OPENSSL 1
#define HAVE_STDINT_H 1
#define HAVE_UNISTD_H 1
#define HAVE_PTHREAD_H 1
#define PROJECT_NAME "ceph"
#define CEPH_LIBDIR "/usr/lib"
#define CEPH_PKGLIBDIR "/usr/lib/ceph"
#define CMAKE_INSTALL_LIBDIR "lib"
#define CMAKE_INSTALL_SYSCONFDIR "/etc"
#define CMAKE_INSTALL_PREFIX "/usr"
#define CEPH_INSTALL_FULL_PKGLIBDIR "/usr/lib/ceph"
#define CEPH_INSTALL_DATADIR "/usr/share/ceph"
"""

COMPAT_INCLUDES = ("cstdint", "cstring", "memory", "string", "stdexcept", "limits", "algorithm",
                   "functional")
OPTION_VARS = {"ms_bind_retry_count": "3", "ms_bind_retry_delay": "5"}
_CPP_EXTS = {".cc", ".cpp", ".cxx", ".c", ".h", ".hpp", ".hh"}

# Globs relative to the Ceph repo root (not only `src/`).
DEFAULT_TRACKED_EXCLUDES = (
    "src/boost/*", "src/rocksdb/*", "src/seastar/*", "src/spdk/*", "src/dpdk/*",
    "src/googletest/*", "src/fmt/*", "src/arrow/*", "src/isa-l/*", "src/c-ares/*",
    "src/blkin/*", "src/jaegertracing/*", "src/opentelemetry-cpp/*", "src/xxHash/*",
    "src/zstd/*", "src/lua/*", "src/libkmip/*", "src/rgw/jwt-cpp/*", "src/rgw/picojson/*",
    "src/rgw/madler/*",
)

CACHE_DIRNAME = ".cert-review/compdb-cache"


def is_ceph_tree(root: str | Path) -> bool:
    r = Path(root).expanduser().resolve()
    return (r / "src/include/config-h.in.cmake").is_file() or (r / "src/ceph_ver.h.in.cmake").is_file()


def render_cmake_header(src: Path, subst: dict[str, str]) -> str:
    if not src.exists():
        return f"/* {src.name} not present in this tree */\n"
    out = []
    for line in src.read_text().splitlines():
        m = re.match(r"#cmakedefine01\s+(\w+)", line)
        if m:
            out.append(f"#define {m.group(1)} 0")
            continue
        m = re.match(r"#cmakedefine\s+(\w+)", line)
        if m:
            out.append(f"/* #undef {m.group(1)} */")
            continue
        out.append(re.sub(r"@(\w+)@", lambda k: subst.get(k.group(1), "0"), line))
    return "\n".join(out) + "\n"


def _git_run(ceph: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", "-C", str(ceph), *args], capture_output=True)


def git_tree_id(ceph: Path) -> str | None:
    """Cache key: HEAD, or HEAD+dirty when the worktree has local changes."""
    if _git_run(ceph, "rev-parse", "--is-inside-work-tree").stdout.strip() != b"true":
        return None
    head = _git_run(ceph, "rev-parse", "HEAD").stdout.decode().strip()
    dirty = _git_run(ceph, "status", "--porcelain").stdout
    if not dirty.strip():
        return head
    return f"{head}+{hashlib.sha256(dirty).hexdigest()[:10]}"


def path_excluded(relpath: str, patterns: tuple[str, ...] | list[str]) -> bool:
    p = relpath.lstrip("./")
    return any(fnmatch.fnmatch(p, g) for g in patterns)


def _resolve_source(
    ceph: Path,
    relpath: str,
    out_p: Path,
    git_ref: str | None,
) -> Path | None:
    rel = relpath.lstrip("/")
    on_disk = ceph / rel
    if on_disk.is_file() and on_disk.suffix.lower() in _CPP_EXTS:
        return on_disk.resolve()
    if not git_ref:
        return None
    show = _git_run(ceph, "show", f"{git_ref}:{rel}")
    if show.returncode != 0:
        return None
    staged = out_p / "sources" / rel
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_bytes(show.stdout)
    return staged.resolve()


def git_tracked_sources(
    ceph: Path,
    *,
    git_ref: str = "HEAD",
    exclude: tuple[str, ...] | list[str] | None = None,
    prefix: str = "src/",
) -> list[str]:
    """All C/C++ paths under `prefix` at `git_ref`, minus vendor trees."""
    ex = tuple(exclude or DEFAULT_TRACKED_EXCLUDES)
    r = _git_run(ceph, "ls-tree", "-r", "--name-only", "-z", git_ref, "--", prefix)
    if r.returncode != 0:
        return []
    out = []
    for name in (x.decode() for x in r.stdout.split(b"\0") if x):
        if Path(name).suffix.lower() not in _CPP_EXTS:
            continue
        if path_excluded(name, ex):
            continue
        out.append(name)
    return sorted(out)


def cache_dir(ceph: Path) -> Path:
    return ceph / CACHE_DIRNAME


def ensure_cached_compdb(
    ceph_root: str | Path,
    *,
    git_ref: str = "HEAD",
    exclude: tuple[str, ...] | list[str] | None = None,
    std: str = "c++23",
    force: bool = False,
) -> Path | None:
    """Build or reuse `.cert-review/compdb-cache/<tree-id>/compile_commands.json`."""
    ceph = Path(ceph_root).expanduser().resolve()
    if not is_ceph_tree(ceph):
        return None
    tid = git_tree_id(ceph)
    if not tid:
        return None
    root = cache_dir(ceph)
    dest = root / tid
    meta = dest / "meta.json"
    cdb = dest / "compile_commands.json"
    if not force and cdb.is_file() and meta.is_file():
        try:
            if json.loads(meta.read_text()).get("tree_id") == tid:
                _link_current(root, tid)
                return dest
        except (json.JSONDecodeError, OSError):
            pass
    rels = git_tracked_sources(ceph, git_ref=git_ref, exclude=exclude)
    if not rels:
        return None
    build_compdb(ceph, dest, relpaths=rels, git_ref=git_ref, std=std, exclude=exclude)
    n = len(json.loads(cdb.read_text()))
    meta.write_text(json.dumps({
        "tree_id": tid, "git_ref": git_ref, "entries": n, "synthetic": True,
    }, indent=2) + "\n")
    _link_current(root, tid)
    return dest


def _link_current(root: Path, tid: str) -> None:
    cur = root / "current"
    try:
        if cur.is_symlink() or cur.is_file():
            cur.unlink()
        elif cur.is_dir():
            return
    except OSError:
        return
    try:
        cur.symlink_to(tid, target_is_directory=True)
    except OSError:
        pass


def build_compdb(
    ceph_root: str | Path,
    out: str | Path,
    *,
    git_diff: str | None = None,
    relpaths: list[str] | None = None,
    dirs: list[str] | None = None,
    std: str = "c++23",
    git_ref: str | None = "HEAD",
    exclude: tuple[str, ...] | list[str] | None = None,
) -> Path:
    """Write `out/compile_commands.json` and return `out`."""
    ceph = Path(ceph_root).expanduser().resolve()
    out_p = Path(out).expanduser().resolve()
    out_p.mkdir(parents=True, exist_ok=True)
    src = ceph / "src"
    gen = out_p / "gen"
    (gen / "include").mkdir(parents=True, exist_ok=True)
    acc = render_cmake_header(src / "include/config-h.in.cmake", {}) + EXTRA_DEFS
    (gen / "acconfig.h").write_text(acc)
    (gen / "include/acconfig.h").write_text(acc)
    (gen / "ceph_ver.h").write_text(render_cmake_header(src / "ceph_ver.h.in.cmake", {
        "CEPH_GIT_VER": "0", "CEPH_GIT_NICE_VER": "0", "CEPH_GIT_VER_FULL": "0",
        "CEPH_GIT_VER_NICE": "0"}))
    (gen / "ceph_release.h").write_text(render_cmake_header(src / "ceph_release.h.in.cmake", {
        "CEPH_RELEASE": "20", "CEPH_RELEASE_NAME": "main", "CEPH_RELEASE_TYPE": "dev",
        "CEPH_BUILD_TYPE": "RelWithDebInfo"}))
    opt = src / "common/options"
    tmp = out_p / "options"
    tmp.mkdir(exist_ok=True)
    for yin in sorted(opt.glob("*.yaml.in")):
        name = yin.name[: -len(".yaml.in")]
        y = tmp / f"{name}.yaml"
        y.write_text(re.sub(r"@(\w+)@", lambda m: OPTION_VARS.get(m.group(1), "x"), yin.read_text()))
        subprocess.run([sys.executable, str(opt / "y2c.py"), "--input", str(y),
                        "--output", str(tmp / f"{name}_options.cc"),
                        "--legacy", str(gen / "include" / f"{name}_legacy_options.h"),
                        "--name", name], check=False, capture_output=True)
    sysroot: list[str] = []
    if platform.system() == "Darwin":
        try:
            sdk = subprocess.run(["xcrun", "--show-sdk-path"], capture_output=True, text=True,
                                 check=True).stdout.strip()
            sysroot = ["-isysroot", sdk]
        except (OSError, subprocess.CalledProcessError):
            pass
    incs = [src, src / "include", gen, gen / "include", src / "rapidjson/include",
            src / "dmclock/support/src", src / "dmclock/src", src / "s3select/include",
            src / "xxHash", src / "BLAKE3/c", src / "rgw", src / "rgw/include",
            src / "rgw" / "radosgw-admin", src / "rgw" / "driver" / "rados"]
    flags = [f"-std={std}", "-DHAVE_CONFIG_H", "-D_FILE_OFFSET_BITS=64", "-D__linux__=1",
             "-DWITH_RADOSGW", "-DWITH_RADOSGW_RADOS", "-DWITH_RADOSGW_STANDALONE",
             "-DBOOST_ASIO_DISABLE_THREAD_KEYWORD_EXTENSION", "-Wno-everything", *sysroot]
    flags += [f"-I{p}" for p in incs if p.exists()]
    for h in COMPAT_INCLUDES:
        flags += ["-include", h]
    if (src / "fmt/include/fmt").is_dir():
        side = out_p / "fmt-include"
        side.mkdir(exist_ok=True)
        link = side / "fmt"
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to((src / "fmt/include/fmt").resolve())
        flags.append(f"-I{side}")
    ref: str | None = git_ref
    if git_diff:
        if "..." in git_diff:
            ref = git_diff.split("...", 1)[1] or git_ref
        elif ".." in git_diff:
            ref = git_diff.split("..", 1)[1] or git_ref

    ex = exclude or DEFAULT_TRACKED_EXCLUDES
    rel_names: list[str] = []
    if git_diff:
        r = _git_run(ceph, "diff", "--name-only", "-z", git_diff)
        if r.returncode == 0:
            for name in (x.decode() for x in r.stdout.split(b"\0") if x):
                if Path(name).suffix.lower() in _CPP_EXTS and not path_excluded(name, ex):
                    rel_names.append(name)
    for rel in relpaths or []:
        r = rel.lstrip("/")
        if Path(r).suffix.lower() in _CPP_EXTS and not path_excluded(r, ex):
            rel_names.append(r)
    for d in dirs or []:
        for f in sorted((ceph / d).rglob("*")):
            if f.suffix.lower() in _CPP_EXTS and f.is_file():
                rel = str(f.relative_to(ceph))
                if not path_excluded(rel, ex):
                    rel_names.append(rel)
    cmds = []
    for rel in sorted(set(rel_names)):
        p = _resolve_source(ceph, rel, out_p, ref)
        if p:
            cmds.append({"directory": str(src), "file": str(p),
                         "arguments": ["clang++", *flags, "-c", str(p)]})
    (out_p / "compile_commands.json").write_text(json.dumps(cmds, indent=1) + "\n")
    return out_p