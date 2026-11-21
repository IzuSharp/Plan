# DB-CPP-01 Linux handoff

## Current state: baseline frozen; migration not yet implemented

The owner authorized the database-only Rust-to-C++ migration, tests, three-repository documentation, PRs and normal merges. DB-API-01 and DB-Perf-01 are separate and not started. No migration acceptance is claimed.

| Repository | Observed merged main input | Working branch |
|---|---|---|
| NativeWeave | `465cd0f90e6af05ec50eb581156240377cf0825b` | `task/DB-CPP-01-linux` |
| NativeWeave-Design | `8298dc4128b745cf1809bad0c3cf02c45eb7f522` | `task/DB-CPP-01-linux` |
| Plan | `1fe52a8bd792ccdbb4bbea17ba59b0ad0c24349d` | `task/DB-CPP-01-linux` |

Local ROOT is `/workspace/scratch/b938bf45c750`. The three worktrees are under `ROOT/.worktree/DB-CPP-01-linux/`; bare remote mirrors are under `ROOT/.repos/`. The detached Rust reference is `ROOT/baseline/rust`. Validation tools are being prepared separately in `ROOT/_validation/`; only the reference environment will expose Rust.

## Completed observations

- Read all three current root AGENTS.md files, current product documentation and DB-Scope-01 Plan/design. This explicit owner instruction supersedes their previous batch's stop/scope statements.
- Queried all three remote main branches and branch collections. The observed main inputs equal the supplied starts. No DB-CPP-01 branch or batch handoff existed when work began.
- Found an orphan old Design worktree and old .NET SDK under `/workspace/scratch/58d2a6adf1c3`, consuming approximately 610 MiB allocated disk space. Its Git administration directory no longer existed. Every one of its 2,919 non-Git files matched a blob reachable from remote Design history. Removed the entire old task directory under the user's explicit cleanup authorization and verified absence; see cleanup-linux.json.
- Fresh source mirrors/worktrees and fixed product reference were created successfully.
- Initial product inventory counted 23,335 lines across the top-level native database/interop Rust modules. This is a whole execution/ownership migration, not a library name substitution.
- Query source research identified SeaQuery 1.0.2, existing runtime arena validation and dialect-specific parameter rules. Upstream/toolchain research and validation-tool installation are in progress.

## Tests and PRs

No C++ product build, runtime test, sanitizer test or migration PR/main CI has run yet. No reference package has yet been retrieved or built. Initial Plan structure validation is recorded with the first published checkpoint. PR/commit links will be appended after publication, not predicted.

## Next work

Publish the Plan-first checkpoint and create its draft PR. Then publish the Design C++ decision and common ABI/module boundaries before product edits. Obtain or build the exact Rust candidate with provenance; prepare LLVM/CMake/Ninja/.NET/PostgreSQL in user-owned tool directories. Implement an early complete C++ provider path, then the remaining compatibility matrix. Keep the migration table and evidence honest at every stage.
