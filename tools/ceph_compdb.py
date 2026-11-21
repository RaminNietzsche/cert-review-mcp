#!/usr/bin/env python3
"""Create a cheap compile_commands.json for a Ceph checkout without building it.

A real build (cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON) is better. This helper
exists so the engine can analyse a partial checkout: it renders the headers
cmake would generate (acconfig.h, ceph_ver.h, ceph_release.h) with neutral
values into a side directory and writes one compile command per source file.

    python3 tools/ceph_compdb.py --ceph /path/to/ceph --out /tmp/ceph-compdb \
        src/common src/rgw
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

EXTRA_DEFS = """
#define HAVE_SYS_TYPES_H 1
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


OPTION_VARS = {"ms_bind_retry_count": "3", "ms_bind_retry_delay": "5"}


def render_cmake_header(src: Path, subst: dict[str, str]) -> str:
    if not src.exists():   # older trees lack some templates (e.g. ceph_release.h.in.cmake)
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ceph", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--std", default="c++23")
    ap.add_argument("dirs", nargs="+", help="directories relative to the ceph root, e.g. src/common")
    a = ap.parse_args()
    src = a.ceph / "src"
    gen = a.out / "gen"
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
    # <name>_legacy_options.h comes from common/options/*.yaml.in via y2c.py
    opt = src / "common/options"
    tmp = a.out / "options"
    tmp.mkdir(exist_ok=True)
    for yin in sorted(opt.glob("*.yaml.in")):
        name = yin.name[: -len(".yaml.in")]
        y = tmp / f"{name}.yaml"
        y.write_text(re.sub(r"@(\w+)@", lambda m: OPTION_VARS.get(m.group(1), "x"), yin.read_text()))
        subprocess.run([sys.executable, str(opt / "y2c.py"), "--input", str(y),
                        "--output", str(tmp / f"{name}_options.cc"),
                        "--legacy", str(gen / "include" / f"{name}_legacy_options.h"),
                        "--name", name], check=False, capture_output=True)
    sysroot = []
    if platform.system() == "Darwin":
        try:
            sdk = subprocess.run(["xcrun", "--show-sdk-path"], capture_output=True, text=True,
                                 check=True).stdout.strip()
            sysroot = ["-isysroot", sdk]
        except (OSError, subprocess.CalledProcessError):
            print("warning: xcrun --show-sdk-path failed; system headers may be missing", file=sys.stderr)
        print("note: Ceph needs Linux headers (linux/version.h, ...) and Linux-only Boost.Asio "
              "features, so files such as src/rgw/radosgw-admin/radosgw-admin.cc cannot be parsed on "
              "macOS. Run the analysis on Linux, the Docker image or the GitHub Action.", file=sys.stderr)
    incs = [src, src / "include", gen, gen / "include", src / "rapidjson/include",
            src / "dmclock/support/src", src / "dmclock/src", src / "s3select/include",
            src / "xxHash", src / "BLAKE3/c", src / "fmt/include"]
    flags = [f"-std={a.std}", "-DHAVE_CONFIG_H", "-D_FILE_OFFSET_BITS=64", "-D__linux__=1",
             "-DBOOST_ASIO_DISABLE_THREAD_KEYWORD_EXTENSION", "-Wno-everything", *sysroot]
    flags += [f"-I{p}" for p in incs if p.exists()]
    cmds = []
    for d in a.dirs:
        for f in sorted((a.ceph / d).rglob("*.cc")):
            cmds.append({"directory": str(src), "file": str(f),
                         "arguments": ["clang++", *flags, "-c", str(f)]})
    (a.out / "compile_commands.json").write_text(json.dumps(cmds, indent=1))
    print(f"{len(cmds)} compile commands -> {a.out}/compile_commands.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
