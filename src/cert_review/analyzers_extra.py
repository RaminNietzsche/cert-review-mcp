"""Optional analyzers: Semgrep (bundled CERT rules), Infer and CodeQL.

Each runner returns (raw findings, ToolStatus) like the runners in toolrun.py.
A missing binary yields status "missing" and a note; nothing is installed or
downloaded here. All three write only to a private temporary directory.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import checkers_map as CM
from .paths import data_dir
from .profiles import Profile
from .toolrun import RawFinding, ToolStatus, fallback_flags, lang_of, version, which

OPTIONAL_TOOLS = ("semgrep", "infer", "codeql")


def _sanitize_untrusted_tool_output(text: str, limit: int = 300) -> str:
    """Sanitize external tool output before surfacing it in LLM-visible notes."""
    s = (text or "").replace("\r", " ").replace("\n", " ")
    s = re.sub(r"[\x00-\x1f\x7f]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:limit]


CODEQL_SUITES = {
    "c": "codeql/cert-c-coding-standards:codeql-suites/cert-c-default.qls",
    "cpp": "codeql/cert-cpp-coding-standards:codeql-suites/cert-cpp-default.qls",
}
INSTALL_HINT = {
    "semgrep": "semgrep not installed (pip install semgrep)",
    "infer": "infer not installed (Linux x86_64 and macOS arm64 releases: "
             "https://github.com/facebook/infer/releases)",
    "codeql": "codeql not installed (https://github.com/github/codeql-cli-binaries; then "
              "`codeql pack download codeql/cert-c-coding-standards "
              "codeql/cert-cpp-coding-standards`)",
}
COMPILE_ERROR = re.compile(r"^(?P<file>[^:\s][^:]*):\d+:\d+: (?:fatal )?error: ")


def available(tool: str) -> bool:
    return which(tool) is not None


def semgrep_rules_dir() -> Path:
    return data_dir() / "semgrep"


def _chunks(seq: list[str], n: int):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


# ------------------------------------------------------------------ semgrep
def run_semgrep(files: list[str], profile: Profile, root: Path | None, jobs: int = 4,
                timeout: int = 300) -> tuple[list[RawFinding], ToolStatus]:
    """Run the bundled CERT rules (data/semgrep/*.yml) with the Semgrep CLI."""
    exe = which("semgrep")
    st = ToolStatus("semgrep", bool(exe), _semgrep_version(exe) if exe else "")
    if not exe:
        st.notes.append(INSTALL_HINT["semgrep"])
        return [], st
    rules = semgrep_rules_dir()
    if not any(rules.glob("*.yml")):
        st.available = False
        st.notes.append(f"no Semgrep rules found in {rules}")
        return [], st
    raw: list[RawFinding] = []
    env = dict(os.environ, SEMGREP_SEND_METRICS="off", SEMGREP_ENABLE_VERSION_CHECK="0")
    partial = set()
    for chunk in _chunks(files, 400):
        cmd = [exe, "scan", "--config", str(rules), "--json", "--metrics=off",
               "--disable-version-check", "--no-git-ignore", "--quiet",
               "-j", str(max(1, jobs)), "--timeout", str(min(timeout, 120)), *chunk]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, env=env,
                               timeout=timeout * max(1, len(chunk) // max(1, jobs)))
        except subprocess.TimeoutExpired:
            st.notes.append(f"timeout on {len(chunk)} file(s)")
            st.timed_out.extend(chunk)
            continue
        try:
            doc = json.loads(r.stdout or "{}")
        except json.JSONDecodeError:
            st.notes.append(f"unreadable semgrep output (exit {r.returncode}): {r.stderr.strip()[:200]}")
            st.files_with_errors.extend(chunk)
            continue
        for e in doc.get("errors", []):
            kind = str(e.get("type", ""))
            path = e.get("path") or (e.get("spans") or [{}])[0].get("file")
            if "Timeout" in kind and path:
                st.timed_out.append(path)
            elif path:
                partial.add(path)      # semgrep recovers from parse errors and keeps matching
        for res in doc.get("results", []):
            check = res["check_id"].rsplit(".", 1)[-1]
            raw.append(RawFinding("semgrep", check, res["path"], int(res["start"]["line"]),
                                  int(res["start"].get("col", 1)),
                                  " ".join(res["extra"].get("message", "").split())))
    st.files = len(files)
    st.raw_findings = len(raw)
    if partial:
        st.notes.append(f"{len(partial)} file(s) parsed only partly by semgrep (macros or "
                        "unsupported syntax); matching continued on the rest")
    return raw, st


def _semgrep_version(exe: str) -> str:
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=60,
                             env=dict(os.environ, SEMGREP_ENABLE_VERSION_CHECK="0")).stdout
    except Exception:
        return ""
    return out.strip().splitlines()[-1] if out.strip() else ""


# ------------------------------------------------------------------ compile commands
def _compile_entries(files: list[str], profile: Profile, compdb: Path | None,
                     root: Path | None) -> list[dict]:
    """One compile_commands.json entry per file: the project's entry when `compdb`
    has one, otherwise the guessed flags clang-tidy uses (toolrun.fallback_flags)."""
    known: dict[str, dict] = {}
    if compdb and (compdb / "compile_commands.json").exists():
        for e in json.loads((compdb / "compile_commands.json").read_text()):
            p = Path(e["file"])
            p = p if p.is_absolute() else Path(e["directory"]) / p
            known[str(p.resolve())] = e
    out = []
    for f in files:
        rp = str(Path(f).resolve())
        if rp in known:
            e = dict(known[rp])
            e["file"] = rp
            out.append(e)
            continue
        lang = lang_of(f)
        cc = "clang" if lang == "c" else "clang++"
        flags = [x for x in fallback_flags(f, lang, profile, root) if x != "-ferror-limit=0"]
        out.append({"directory": str(Path(rp).parent), "file": rp,
                    "arguments": [cc, "-x", "c" if lang == "c" else "c++", *flags, "-c", rp,
                                  "-o", os.devnull]})
    return out


def _common_root(files: list[str]) -> Path:
    paths = [str(Path(f).resolve().parent) for f in files]
    return Path(os.path.commonpath(paths)) if paths else Path.cwd()


# ------------------------------------------------------------------ infer
INFER_CHECKERS = ["--pulse", "--bufferoverrun", "--liveness", "--racerd", "--starvation", "--siof"]


def run_infer(files: list[str], profile: Profile, compdb: Path | None, root: Path | None,
              jobs: int = 4, timeout: int = 300) -> tuple[list[RawFinding], ToolStatus]:
    """Run Infer (Pulse, InferBO, liveness, RacerD, starvation, SIOF) on the files."""
    exe = which("infer")
    st = ToolStatus("infer", bool(exe), version("infer") if exe else "")
    if not exe:
        st.notes.append(INSTALL_HINT["infer"])
        return [], st
    wanted = {c for (tool, c) in CM.reverse_index() if tool == "infer"}
    project = _common_root(files)
    raw: list[RawFinding] = []
    with tempfile.TemporaryDirectory(prefix="cert-review-infer-") as tmp:
        cdb = Path(tmp) / "compile_commands.json"
        cdb.write_text(json.dumps(_compile_entries(files, profile, compdb, root)))
        out = Path(tmp) / "infer-out"
        cmd = [exe, "run", "--compilation-database", str(cdb), "--keep-going", "-o", str(out),
               "--project-root", str(project), "-j", str(max(1, jobs)), "--no-progress-bar",
               *INFER_CHECKERS]
        budget = max(timeout, timeout * len(files) // max(1, jobs))
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=min(budget, 6 * 3600),
                               cwd=str(project))
        except subprocess.TimeoutExpired:
            st.notes.append("timeout")
            st.timed_out.extend(files)
            st.files = len(files)
            return [], st
        log = (r.stdout or "") + "\n" + (r.stderr or "")
        bad = set()
        for line in log.splitlines():
            m = COMPILE_ERROR.match(line.strip())
            if m:
                p = Path(m["file"])
                bad.add(str(p if p.is_absolute() else (project / p).resolve()))
        sel = {str(Path(f).resolve()) for f in files}
        st.files_with_errors = sorted(bad & sel)
        st.parse_errors = len(st.files_with_errors)
        report = out / "report.json"
        if not report.exists():
            st.notes.append(f"no report (exit {r.returncode}): {log.strip()[-300:]}")
            st.files = len(files)
            return [], st
        for it in json.loads(report.read_text()):
            if it.get("bug_type") not in wanted:
                continue
            p = Path(it["file"])
            p = p if p.is_absolute() else project / p
            raw.append(RawFinding("infer", it["bug_type"], str(p), int(it.get("line", 1)),
                                  max(1, int(it.get("column", 1) or 1)), it.get("qualifier", "")))
    st.files = len(files)
    st.raw_findings = len(raw)
    return raw, st


# ------------------------------------------------------------------ codeql
def _codeql_packs_ok(exe: str, langs: set[str]) -> list[str]:
    """Names of the CERT query packs that are not installed."""
    missing = []
    for lang in sorted(langs):
        spec = CODEQL_SUITES[lang].split(":", 1)[0]
        r = subprocess.run([exe, "resolve", "queries", CODEQL_SUITES[lang], "--format=json"],
                           capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            missing.append(spec)
    return missing


def run_codeql(files: list[str], profile: Profile, compdb: Path | None, root: Path | None,
               jobs: int = 4, timeout: int = 300) -> tuple[list[RawFinding], ToolStatus]:
    """Build a CodeQL database for the files and run the CERT C/C++ query packs.

    With a compilation database the files are compiled (traced build); without one
    the database is extracted with --build-mode=none from a copy of the files.
    """
    exe = which("codeql")
    st = ToolStatus("codeql", bool(exe), version("codeql") if exe else "")
    if not exe:
        st.notes.append(INSTALL_HINT["codeql"])
        return [], st
    langs = {lang_of(f) for f in files}
    missing = _codeql_packs_ok(exe, langs)
    if missing:
        st.available = False
        st.notes.append("CodeQL query packs not installed: " + ", ".join(missing) +
                        " (run `codeql pack download " + " ".join(missing) + "`)")
        return [], st
    wanted = {c for (tool, c) in CM.reverse_index() if tool == "codeql"}
    project = _common_root(files)
    raw: list[RawFinding] = []
    budget = min(6 * 3600, max(900, timeout * len(files) // max(1, jobs)))
    with tempfile.TemporaryDirectory(prefix="cert-review-codeql-") as tmp:
        t = Path(tmp)
        db = t / "db"
        origin: dict[str, str] = {}
        use_build = compdb is not None and (compdb / "compile_commands.json").exists()
        if use_build:
            entries = _compile_entries(files, profile, compdb, root)
            script = t / "build.sh"
            lines = ["#!/bin/sh"]
            allowed_compilers = {"cc", "gcc", "g++", "clang", "clang++", "c++", "cl"}
            skipped_unsafe = 0
            for e in entries:
                raw_args = e.get("arguments") or _split(e["command"])
                if not raw_args:
                    skipped_unsafe += 1
                    continue
                exe_name = Path(str(raw_args[0])).name
                if exe_name not in allowed_compilers:
                    skipped_unsafe += 1
                    continue
                args = _sanitize_compile_args(raw_args)
                lines.append(f"cd {_q(e['directory'])} && " + " ".join(_q(a) for a in _drop_output(args))
                             + " -fsyntax-only || true")
            if len(lines) == 1:
                st.available = False
                st.notes.append("CodeQL traced build blocked: no safe compiler commands found in compile_commands.json")
                return [], st
            if skipped_unsafe:
                st.notes.append(f"CodeQL traced build skipped {skipped_unsafe} non-compiler compile_commands.json entries")
            script.write_text("\n".join(lines) + "\n")
            script.chmod(0o755)
            src_root = project
            cmd = [exe, "database", "create", str(db), "--language=cpp", f"--source-root={src_root}",
                   f"--command={script}", "--overwrite", "-q", f"--threads={max(1, jobs)}"]
            for f in files:
                origin[str(Path(f).resolve())] = str(Path(f).resolve())
        else:
            src_root = t / "src"
            for f in files:
                rp = Path(f).resolve()
                rel = rp.relative_to(project) if rp.is_relative_to(project) else Path(rp.name)
                dst = src_root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(rp, dst)
                origin[str(dst)] = str(rp)
            cmd = [exe, "database", "create", str(db), "--language=cpp", "--build-mode=none",
                   f"--source-root={src_root}", "--overwrite", "-q", f"--threads={max(1, jobs)}"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=budget)
        except subprocess.TimeoutExpired:
            st.notes.append("timeout while creating the database")
            st.timed_out.extend(files)
            st.files = len(files)
            return [], st
        if r.returncode != 0:
            st.notes.append(f"database creation failed (untrusted tool output): {_sanitize_untrusted_tool_output(r.stderr or r.stdout)}")
            st.files_with_errors.extend(files)
            st.files = len(files)
            return [], st
        sarif = t / "out.sarif"
        cmd = [exe, "database", "analyze", str(db), *[CODEQL_SUITES[x] for x in sorted(langs)],
               "--format=sarifv2.1.0", f"--output={sarif}", f"--threads={max(1, jobs)}", "-q",
               "--no-print-diagnostics-summary", "--no-print-metrics-summary"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=budget)
        except subprocess.TimeoutExpired:
            st.notes.append("timeout while running queries")
            st.timed_out.extend(files)
            st.files = len(files)
            return [], st
        if r.returncode != 0 or not sarif.exists():
            st.notes.append(
                f"query run failed (untrusted tool output): "
                f"{_sanitize_untrusted_tool_output(r.stderr or r.stdout)}"
            )
            st.files = len(files)
            return [], st
        doc = json.loads(sarif.read_text())
        for run in doc.get("runs", []):
            for res in run.get("results", []):
                qid = res.get("ruleId")
                if qid not in wanted:
                    continue
                loc = (res.get("locations") or [{}])[0].get("physicalLocation", {})
                uri = loc.get("artifactLocation", {}).get("uri")
                if not uri:
                    continue
                p = Path(uri)
                p = str((p if p.is_absolute() else Path(src_root) / p).resolve())
                region = loc.get("region", {})
                raw.append(RawFinding("codeql", qid, origin.get(p, p), int(region.get("startLine", 1)),
                                      int(region.get("startColumn", 1)),
                                      res.get("message", {}).get("text", "")))
    st.files = len(files)
    st.raw_findings = len(raw)
    return raw, st


def _q(s: str) -> str:
    import shlex
    return shlex.quote(s)


def _split(cmd: str) -> list[str]:
    import shlex
    return shlex.split(cmd)


def _sanitize_compile_args(args: list[str]) -> list[str]:
    """Drop high-risk flags from compile_commands entries before execution."""
    out: list[str] = []
    skip_next = False
    deny_exact_with_value = {
        "-Xclang", "-load", "-plugin", "-specs", "--specs", "-B", "-fplugin-arg",
        "-fplugin", "-wrapper", "--config", "-T", "-Wl,-plugin-opt"
    }
    deny_exact = {
        "-fintegrated-cc1", "-fplugin=", "-fplugin", "-Wl,-plugin"
    }
    deny_prefix = (
        "@",                # response files
        "-fplugin=",        # GCC plugin loading
        "-Xclang=",         # clang driver passthrough
        "-Wl,@",            # linker response files
    )
    for a in args:
        if skip_next:
            skip_next = False
            continue
        if a in deny_exact_with_value:
            skip_next = True
            continue
        if a in deny_exact:
            continue
        if any(a.startswith(p) for p in deny_prefix):
            continue
        out.append(a)
    return out


def _drop_output(args: list[str]) -> list[str]:
    """Remove `-o <file>` and `-c` so the command only parses the file."""
    out, skip = [], False
    for a in args:
        if skip:
            skip = False
            continue
        if a == "-o":
            skip = True
            continue
        if a.startswith("-o") and len(a) > 2:
            continue
        if a == "-c":
            continue
        out.append(a)
    return out
