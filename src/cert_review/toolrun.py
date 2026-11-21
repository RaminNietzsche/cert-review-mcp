"""Run clang-tidy, the Clang Static Analyzer and cppcheck; parse raw output."""
from __future__ import annotations

import functools
import json
import os
import re
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from . import checkers_map as CM
from .paths import data_dir
from .profiles import Profile

CT_LINE = re.compile(r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+): (?P<sev>warning|error): "
                     r"(?P<msg>.*?) \[(?P<chk>[^\]]+)\]\s*$")
CSA_LINE = CT_LINE
CPPCHECK_LINE = re.compile(r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+):(?P<sev>[a-z]+):(?P<id>[A-Za-z0-9_.-]+):(?P<msg>.*)$")

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
    timed_out: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        """missing | partial (some files did not parse or timed out) | ok."""
        if not self.available:
            return "missing"
        return "partial" if self.parse_errors or self.files_with_errors or self.timed_out else "ok"


def parse_warnings(tools) -> list[str]:
    """Human-readable lines for every tool that could not fully analyse its input:
    files with compile errors and files whose analysis timed out.
    `tools` is a list of ToolStatus or their dict form."""
    out = []
    for t in tools or []:
        g = (lambda k, d=None: t.get(k, d)) if isinstance(t, dict) else (lambda k, d=None: getattr(t, k, d))
        files = list(g("files_with_errors") or [])
        if files or g("parse_errors"):
            shown = ", ".join(files[:5]) + (f" (+{len(files) - 5} more)" if len(files) > 5 else "")
            out.append(f"{g('tool')}: {len(files) or g('parse_errors')} file(s) had compile errors and were "
                       f"only partly analysed, so a clean result is not proof: {shown}. "
                       "Pass a real compile_commands.json (--compdb) built with the project's dependencies.")
        timed = list(g("timed_out") or [])
        if timed:
            shown = ", ".join(timed[:5]) + (f" (+{len(timed) - 5} more)" if len(timed) > 5 else "")
            out.append(f"{g('tool')}: {len(timed)} file(s) timed out and were not analysed, so a clean "
                       f"result is not proof: {shown}.")
    return out


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


def _checks_for_clang_tidy(profile: Profile, standards=None) -> tuple[list[str], list[str]]:
    """(clang-tidy checks, clang-analyzer checks) that map to the selected standards' rules."""
    ct = {c.split("@", 1)[0] for c in CM.checkers_for_tool("clang-tidy", standards=standards)}
    sa = {f"clang-analyzer-{c.split('@', 1)[0]}" for c in CM.checkers_for_tool("clangsa", standards=standards)}
    return sorted(ct), sorted(sa)


def run_clang_tidy(files: list[str], profile: Profile, compdb: Path | None,
                   root: Path | None, jobs: int = 4, timeout: int = 300,
                   with_csa: bool = True, standards=None) -> tuple[list[RawFinding], ToolStatus]:
    exe = which("clang-tidy")
    st = ToolStatus("clang-tidy", bool(exe), version("clang-tidy") if exe else "")
    if not exe:
        st.notes.append("clang-tidy not installed")
        return [], st
    ct, sa = _checks_for_clang_tidy(profile, standards)
    checks = ["-*"] + ct + (sa if with_csa else []) + profile.extra_checks
    checks_arg = ",".join(checks)
    mapped_ct = set(CM.checkers_for_tool("clang-tidy", standards=standards))
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
                st.timed_out.append(path)
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
                    if c in CHECKER_VARIANTS:
                        c = checker_variant(c, m["msg"])
                        if c not in mapped_ct:
                            continue
                    raw.append(RawFinding("clang-tidy", c, m["file"], int(m["line"]),
                                          int(m["col"]), m["msg"]))
    st.raw_findings = len(raw)
    return raw, st


# Some checkers report different weaknesses under one name; the message tells them apart.
# A finding is renamed to "<checker>@<variant>" so that each variant maps to its own rules
# in the checker map (an unmapped variant is dropped). The first matching pattern wins.
_FLOAT = r"(?:float|double|long double|_Float\d+|__fp16|__bf16)"
CHECKER_VARIANTS: dict[str, list[tuple[str, str]]] = {
    "alpha.security.taint.GenericTaint": [
        (r"used as a format string", "format-string"),
        (r"passed to a system call", "system-call"),
        (r"specify the buffer size", "buffer-size"),
        (r"", "other"),
    ],
    "alpha.security.ArrayBoundV2": [
        (r"tainted", "tainted"),
        (r"", "untainted"),
    ],
    "alpha.unix.cstring.OutOfBounds": [
        (r"^String ", "string"),
        (r"", "memory"),
    ],
    # clang-tidy: "narrowing conversion from [constant] 'T1' to [signed type] 'T2' ..."
    "bugprone-narrowing-conversions": [
        (rf"from (?:constant )?(?:value )?'?{_FLOAT}'? to (?:\w+ )*'?{_FLOAT}'?", "float-to-float"),
        (rf"from (?:constant )?(?:value )?'?{_FLOAT}'?", "float-to-int"),
        (rf"to (?:\w+ )*'{_FLOAT}'", "int-to-float"),
        (r"", "int-to-int"),
    ],
}
CSA_VARIANTS = CHECKER_VARIANTS


def checker_variant(checker: str, message: str) -> str:
    for rx, name in CHECKER_VARIANTS.get(checker, []):
        if re.search(rx, message):
            return f"{checker}@{name}"
    return checker


csa_variant = checker_variant


@functools.lru_cache(maxsize=4)
def csa_supported(exe: str) -> frozenset[str] | None:
    """Checker names this clang knows (stable and alpha), or None if it cannot list them.
    An unknown -analyzer-checker aborts the whole analysis, and the checker map is built
    against clang 19 while older clangs (e.g. 18) lack some checkers."""
    names: set[str] = set()
    for flag in ("-analyzer-checker-help", "-analyzer-checker-help-alpha"):
        try:
            out = subprocess.run([exe, "-cc1", flag], capture_output=True, text=True, timeout=30).stdout
        except (OSError, subprocess.SubprocessError):
            return None
        names |= set(re.findall(r"^  ([a-z][\w]*(?:\.[\w]+)+)", out, re.M))
    return frozenset(names) or None


def taint_config() -> Path:
    """Extra taint sources and propagation rules (data/csa-taint.yaml)."""
    return data_dir() / "csa-taint.yaml"


def csa_compile_args(path: str, profile: Profile, compdb: Path | None,
                     root: Path | None) -> tuple[list[str], str | None]:
    """(flags, working directory) for `clang --analyze` on `path`: the file's entry in the
    compilation database when there is one (compiler, -c, -o and the file itself removed),
    otherwise the guessed flags."""
    lang = lang_of(path)
    if compdb and (compdb / "compile_commands.json").exists():
        rp = str(Path(path).resolve())
        try:
            entries = json.loads((compdb / "compile_commands.json").read_text())
        except (OSError, ValueError):
            entries = []
        for e in entries:
            f = Path(e.get("file", ""))
            f = f if f.is_absolute() else Path(e.get("directory", ".")) / f
            if str(f.resolve()) != rp:
                continue
            import shlex
            args = list(e.get("arguments") or shlex.split(e.get("command", "")))[1:]
            out, skip = [], False
            for a in args:
                if skip:
                    skip = False
                    continue
                if a in ("-o", "-MF", "-MT", "-MQ"):
                    skip = True
                    continue
                if a in ("-c", "-MD", "-MMD") or (a.startswith("-o") and len(a) > 2):
                    continue
                if a in (e.get("file"), rp):
                    continue
                out.append(a)
            return out + ["-Wno-everything", "-Qunused-arguments"], e.get("directory")
    return fallback_flags(path, lang, profile, root), None


def run_clang_sa(files: list[str], profile: Profile, compdb: Path | None, root: Path | None,
                 jobs: int = 4, timeout: int = 300,
                 standards=None) -> tuple[list[RawFinding], ToolStatus]:
    """Standalone `clang --analyze` for mapped checkers (incl. alpha/optin), with the
    project's compile flags when a compilation database is given."""
    exe = which("clang")
    st = ToolStatus("clangsa", bool(exe), version("clang") if exe else "")
    if not exe:
        st.notes.append("clang not installed")
        return [], st
    mapped = CM.checkers_for_tool("clangsa", standards=standards)
    checkers = sorted({c.split("@", 1)[0] for c in mapped})
    known = csa_supported(exe)
    if known is not None:
        missing = [c for c in checkers if c not in known]
        if missing:
            st.notes.append(f"not in this clang, skipped: {', '.join(missing)}")
        checkers = [c for c in checkers if c in known]
    raw: list[RawFinding] = []
    cfg = taint_config()
    taint = any("taint" in c for c in checkers) and cfg.exists()

    def one(path: str):
        lang = lang_of(path)
        cmd = [exe, "--analyze", "-Xanalyzer", "-analyzer-output=text"]
        for c in checkers:
            cmd += ["-Xanalyzer", f"-analyzer-checker={c}"]
        if taint:
            cmd += ["-Xanalyzer", "-analyzer-config", "-Xanalyzer",
                    f"alpha.security.taint.TaintPropagation:Config={cfg}"]
        flags, cwd = csa_compile_args(path, profile, compdb, root)
        cmd += ["-x", "c" if lang == "c" else "c++", *flags, path, "-o", os.devnull]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                               cwd=cwd if cwd and Path(cwd).is_dir() else None)
            return path, r.stderr
        except subprocess.TimeoutExpired:
            return path, "TIMEOUT"

    with ThreadPoolExecutor(max_workers=jobs) as ex:
        for path, out in ex.map(one, files):
            st.files += 1
            if out == "TIMEOUT":
                st.notes.append(f"timeout: {path}")
                st.timed_out.append(path)
                continue
            for line in out.splitlines():
                m = CSA_LINE.match(line)
                if not m or m["sev"] != "warning":
                    continue
                name = csa_variant(m["chk"], m["msg"])
                if name in mapped:
                    raw.append(RawFinding("clangsa", name, m["file"], int(m["line"]),
                                          int(m["col"]), m["msg"]))
    st.raw_findings = len(raw)
    return raw, st


MISRA_ADDON_PREFIX = "misra-c2012-"


def _misra_addon_arg(tmpdir: str) -> str:
    """--addon value for the cppcheck MISRA addon; adds --rule-texts when the user configured
    a licensed MISRA C rule-texts file (the file is only read by cppcheck, never copied)."""
    from . import ruletexts
    texts = ruletexts.path_for("misra-c-2012")
    if not texts or not Path(texts).expanduser().is_file():
        return "misra"
    cfg = Path(tmpdir) / "misra.json"
    cfg.write_text(json.dumps({"script": "misra.py",
                               "args": [f"--rule-texts={Path(texts).expanduser()}"]}))
    return str(cfg)


def run_cppcheck(files: list[str], profile: Profile, root: Path | None, jobs: int = 4,
                 timeout: int = 300, standards=None) -> tuple[list[RawFinding], ToolStatus]:
    exe = which("cppcheck")
    st = ToolStatus("cppcheck", bool(exe), version("cppcheck") if exe else "")
    if not exe:
        st.notes.append("cppcheck not installed")
        return [], st
    wanted = CM.checkers_for_tool("cppcheck", standards=standards)
    misra_c = "misra-c-2012" in (standards or ())
    raw: list[RawFinding] = []
    tmp = tempfile.TemporaryDirectory(prefix="cert-review-") if misra_c else None
    addon = _misra_addon_arg(tmp.name) if tmp else None
    if misra_c:
        st.notes.append("MISRA C:2012 addon enabled for .c files"
                        + (" with your rule-texts file" if addon != "misra" else ""))

    def one(path: str):
        lang = lang_of(path)
        std = profile.raw.get("languages", {})
        cmd = [exe, "--quiet", "--enable=warning,portability,style", "--inline-suppr",
               "--template={file}:{line}:{column}:{severity}:{id}:{message}",
               f"--std={'c' + str(std.get('c_standard', 11)) if lang == 'c' else 'c++' + str(min(std.get('cpp_standard', 20), 20))}",
               "--language=" + ("c" if lang == "c" else "c++")]
        if addon and lang == "c":
            cmd.append(f"--addon={addon}")
            if tmp:
                # keep the addon's .dump files out of the source tree (it may be read-only)
                cmd.append(f"--cppcheck-build-dir={tempfile.mkdtemp(dir=tmp.name)}")
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

    try:
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            for path, out in ex.map(one, files):
                st.files += 1
                if out == "TIMEOUT":
                    st.notes.append(f"timeout: {path}")
                    st.timed_out.append(path)
                    continue
                for line in out.splitlines():
                    m = CPPCHECK_LINE.match(line)
                    if m and m["id"] in wanted:
                        raw.append(RawFinding("cppcheck", m["id"], m["file"], int(m["line"]),
                                              int(m["col"]), m["msg"]))
    finally:
        if tmp:
            tmp.cleanup()
    st.raw_findings = len(raw)
    return raw, st


def find_compdb(start: Path) -> Path | None:
    """Locate a directory containing compile_commands.json (start or build/ below it)."""
    for d in (start, start / "build", start / "build-clang"):
        if (d / "compile_commands.json").exists():
            return d
    return None
