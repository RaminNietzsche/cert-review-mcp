# Running cert-review correctly

What the engine needs before its output is trustworthy, especially for **Ceph** and **diff mode**.

## Requirements

| Requirement | Why |
|---|---|
| **Compilable inputs** | clang-tidy and cppcheck need real flags and headers. Without them, `tools[].status` is `partial` and a clean result is not proof. |
| **`compile_commands.json`** | Best source of flags. Real project build (`-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`) beats guessed flags. |
| **Linux for full Ceph trees** | RGW and several daemons need Linux headers and a Linux toolchain; macOS often cannot parse them (see `profiles/ceph.yaml`). |
| **Diff mode scope** | Findings are kept on **changed lines** only (profile `ceph` adds **3 lines of context** by default via `diff_review.diff_context`). |
| **Confidence cut-offs** | `min_confidence: 0.5` hides many partial checker mappings; use `0` only when exploring noise. |

## Ceph

1. **Preferred:** build the same revision you review and pass `compdb` pointing at the directory that contains `compile_commands.json`:
   ```bash
   cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ...
   cert-review diff --repo "$CEPH" --base d4f5ce --profile ceph \
     --compdb "$CEPH/build" --tools clang-tidy,clangsa,cppcheck,semgrep
   ```
2. **Without a full build:** approximate database for changed files only:
   ```bash
   python3 tools/ceph_compdb.py --ceph "$CEPH" --out /tmp/ceph-compdb \
     --git-diff d4f5ce..HEAD
   cert-review diff --repo "$CEPH" --base d4f5ce --profile ceph --compdb /tmp/ceph-compdb
   ```
3. **MCP `check_diff`:** pass `compdb` explicitly. The server discovers `build/` under **`repo`**, not under the private diff workspace. Since 1.3.1, entries match by `src/...` paths so diff workspaces still use the database flags.

## What partial analysis means

- **clang-tidy `partial`:** compile errors on some files; mapped CERT findings may be missing or only on lines that parsed.
- **cppcheck `partial`:** syntax/preprocessor errors; `--project=` is used only for files present in the database.
- **clangsa `ok` with zero findings:** the analyzer ran; it is not a security sign-off.

## Limits (not bugs)

- Static CERT coverage is **partial** on large frameworks; RGW lifecycle and protocol bugs still need **teuthology / QA** and human review (`build_review_packet` candidates).
- Diff mode does not replace full-tree audits or project test gates.

See also [ceph-trial.md](ceph-trial.md), [benchmark-real.md](benchmark-real.md), [skills/ceph-cert-review/SKILL.md](../skills/ceph-cert-review/SKILL.md).