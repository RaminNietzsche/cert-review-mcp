"""Run clang-tidy, the Clang Static Analyzer and cppcheck; parse raw output."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from . import checkers_map as CM
from .profiles import Profile

CT_LINE = re.compile(r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+): (?P<sev>warning|error): "
                     r"(?P<msg>.*?) \[(?P<chk>[^\]]+)\]\s*$")
CSA_LINE = CT_LINE
CPPCHECK_LINE = re.compile(r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+):(?P<sev>[a-z]+):(?P<id>[A-Za-z0-9_]+):(?P<msg>.*)$")

C_EXT = {".c"}
CPP_EXT = {".cc", ".cpp", ".cxx", ".c++", ".h", ".hh", ".hpp", ".hxx", ".inl"}


@dataclass
class RawFinding:
    tool: str
    checker: str
    file: str
    line: int
    col: int
    message: str


@dataclass
class ToolStatus:
    tool: str
    available: bool
    version: str = ""
    files: int = 0
    raw_findings: int = 0
    parse_errors: int = 0
    files_with_errors: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def lang_of(path: str) -> str:
    return "c" if Path(path).suffix.lower() in C_EXT else "cpp"


def which(tool: str) -> str | None:
    return shutil.which(tool)


def version(tool: str) -> str:
    try:
        out = subprocess.run([tool, "--version"], capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return ""
    m = re.search(r"(\d+\.\d+(?:\.\d+)?)", out)
    return m.group(1) if m else out.strip()[:40]


def fallback_flags(path: str, lang: str, profile: Profile, root: Path | None) -> list[str]:
    std = profile.raw.get("languages", {})
    flags = [f"-std=c{std.get('c_standard', 11)}"] if lang == "c" else \
            [f"-std=c++{std.get('cpp_standard', 20)}"]
    flags += ["-I" + str(Path(path).resolve().parent)]
    if root:
        for sub in ("src", "src/include", "include", "."):
            d = root / sub
            if d.is_dir():
                flags.append("-I" + str(d))
    flags += ["-Wno-everything", "-ferror-limit=0"]
    if lang == "cpp":
        flags += [x for x in profile.clang_tidy_args if x.startswith("-D")]
    return flags


def _checks_for_clang_tidy(profile: Profile) -> tuple[list[str], list[str]]:
    """(clang-tidy checks, clang-analyzer checks) that map to CERT rules and exist."""
    ct = CM.checkers_for_tool("clang-tidy")
    sa = {f"clang-analyzer-{c}" for c in CM.checkers_for_tool("clangsa")}
    return sorted(ct), sorted(sa)


def run_clang_tidy(files: list[str], profile: Profile, compdb: Path | None,
                   root: Path | None, jobs: int = 4, timeout: int = 300,
                   with_csa: bool = True) -> tuple[list[RawFinding], ToolStatus]:
    exe = which("clang-tidy")
    st = ToolStatus("clang-tidy", bool(exe), version("clang-tidy") if exe else "")
    if not exe:
        st.notes.append("clang-tidy not installed")
        return [], st
    ct, sa = _checks_for_clang_tidy(profile)
    checks = ["-*"] + ct + (sa if with_csa else []) + profile.extra_checks
    checks_arg = ",".join(checks)
    raw: list[RawFinding] = []
    hf = profile.header_filter

    def one(path: str):
        cmd = [exe, "--quiet", f"--checks={checks_arg}"]
        if hf:
            cmd.append(f"--header-filter={hf}")
        if compdb:
            cmd += ["-p", str(compdb)]
            cmd.append(path)
        else:
            cmd.append(path)
            cmd.append("--")
            cmd += fallback_flags(path, lang_of(path), profile, root)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return path, r.stdout + "\n" + r.stderr
        except subprocess.TimeoutExpired:
            return path, "TIMEOUT"

    with ThreadPoolExecutor(max_workers=jobs) as ex:
        for path, out in ex.map(one, files):
            st.files += 1
            if out == "TIMEOUT":
                st.notes.append(f"timeout: {path}")
                continue
            for line in out.splitlines():
                m = CT_LINE.match(line)
                if not m:
                    continue
                chks = [c.strip() for c in m["chk"].split(",")]
                if any(c.startswith("clang-diagnostic") for c in chks):
                    if m["sev"] == "error":
                        st.parse_errors += 1
                        if path not in st.files_with_errors:
                            st.files_with_errors.append(path)
                    continue
                for c in chks:
                    raw.append(RawFinding("clang-tidy", c, m["file"], int(m["line"]),
                                          int(m["col"]), m["msg"]))
    st.raw_findings = len(raw)
    return raw, st


def run_clang_sa(files: list[str], profile: Profile, compdb: Path | None, root: Path | None,
                 jobs: int = 4, timeout: int = 300) -> tuple[list[RawFinding], ToolStatus]:
    """Standalone `clang --analyze` for mapped checkers (incl. alpha/optin)."""
    exe = which("clang")
    st = ToolStatus("clangsa", bool(exe), version("clang") if exe else "")
    if not exe:
        st.notes.append("clang not installed")
        return [], st
    checkers = sorted(CM.checkers_for_tool("clangsa"))
    checker_set = set(checkers)
    raw: list[RawFinding] = []

    def one(path: str):
        lang = lang_of(path)
        cmd = [exe, "--analyze", "-Xanalyzer", "-analyzer-output=text"]
        for c in checkers:
            cmd += ["-Xanalyzer", f"-analyzer-checker={c}"]
        cmd += ["-x", "c" if lang == "c" else "c++"]
        cmd += fallback_flags(path, lang, profile, root)
        cmd.append(path)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return path, r.stderr
        except subprocess.TimeoutExpired:
            return path, "TIMEOUT"

    with ThreadPoolExecutor(max_workers=jobs) as ex:
        for path, out in ex.map(one, files):
            st.files += 1
            if out == "TIMEOUT":
                st.notes.append(f"timeout: {path}")
                continue
            for line in out.splitlines():
                m = CSA_LINE.match(line)
                if m and m["sev"] == "warning" and m["chk"] in checker_set:
                    raw.append(RawFinding("clangsa", m["chk"], m["file"], int(m["line"]),
                                          int(m["col"]), m["msg"]))
    st.raw_findings = len(raw)
    return raw, st


def run_cppcheck(files: list[str], profile: Profile, root: Path | None, jobs: int = 4,
                 timeout: int = 300) -> tuple[list[RawFinding], ToolStatus]:
    exe = which("cppcheck")
    st = ToolStatus("cppcheck", bool(exe), version("cppcheck") if exe else "")
    if not exe:
        st.notes.append("cppcheck not installed")
        return [], st
    wanted = CM.checkers_for_tool("cppcheck")
    raw: list[RawFinding] = []

    def one(path: str):
        lang = lang_of(path)
        std = profile.raw.get("languages", {})
        cmd = [exe, "--quiet", "--enable=warning,portability,style", "--inline-suppr",
               "--template={file}:{line}:{column}:{severity}:{id}:{message}",
               f"--std={'c' + str(std.get('c_standard', 11)) if lang == 'c' else 'c++' + str(min(std.get('cpp_standard', 20), 20))}",
               "--language=" + ("c" if lang == "c" else "c++")]
        if root:
            for sub in ("src", "src/include"):
                if (root / sub).is_dir():
                    cmd.append("-I" + str(root / sub))
        cmd.append(path)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return path, r.stderr + "\n" + r.stdout
        except subprocess.TimeoutExpired:
            return path, "TIMEOUT"

    with ThreadPoolExecutor(max_workers=jobs) as ex:
        for path, out in ex.map(one, files):
            st.files += 1
            if out == "TIMEOUT":
                st.notes.append(f"timeout: {path}")
                continue
            for line in out.splitlines():
                m = CPPCHECK_LINE.match(line)
                if m and m["id"] in wanted:
                    raw.append(RawFinding("cppcheck", m["id"], m["file"], int(m["line"]),
                                          int(m["col"]), m["msg"]))
    st.raw_findings = len(raw)
    return raw, st


def find_compdb(start: Path) -> Path | None:
    """Locate a directory containing compile_commands.json (start or build/ below it)."""
    for d in (start, start / "build", start / "build-clang"):
        if (d / "compile_commands.json").exists():
            return d
    return None
