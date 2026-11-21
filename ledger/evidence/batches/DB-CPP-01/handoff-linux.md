# DB-CPP-01 Linux handoff

## Current state: C++ candidate linked; behavioral integration in progress

The owner authorized the database-only Rust-to-C++ migration, tests, three-repository documentation, PRs and normal merges. DB-API-01 and DB-Perf-01 are separate and not started. No migration acceptance is claimed.

| Repository | Observed merged main input | Working branch |
|---|---|---|
| NativeWeave | `465cd0f90e6af05ec50eb581156240377cf0825b` | `task/DB-CPP-01-linux` |
| NativeWeave-Design | `8298dc4128b745cf1809bad0c3cf02c45eb7f522` | `task/DB-CPP-01-linux` |
| Plan | `1fe52a8bd792ccdbb4bbea17ba59b0ad0c24349d` | `task/DB-CPP-01-linux` |

Local ROOT is `/workspace/scratch/b938bf45c750`. The three worktrees are under `ROOT/.worktree/DB-CPP-01-linux/`; bare remote mirrors are under `ROOT/.repos/`. The detached Rust reference is `ROOT/baseline/rust`. Validation tools are installed separately in `ROOT/_validation/`. `env-cpp.sh` selects LLVM 23.1.5, CMake 4.3.3, Ninja 1.13.2, .NET 11.0.100 and PostgreSQL 18.0; only `env-rust-baseline.sh` exposes Rust. The reference source is read-only.

## Completed observations

- Read all three current root AGENTS.md files, current product documentation and DB-Scope-01 Plan/design. This explicit owner instruction supersedes their previous batch's stop/scope statements.
- Queried all three remote main branches and branch collections. The observed main inputs equal the supplied starts. No DB-CPP-01 branch or batch handoff existed when work began.
- Found an orphan old Design worktree and old .NET SDK under `/workspace/scratch/58d2a6adf1c3`, consuming approximately 610 MiB allocated disk space. Its Git administration directory no longer existed. Every one of its 2,919 non-Git files matched a blob reachable from remote Design history. Removed the entire old task directory under the user's explicit cleanup authorization and verified absence; see cleanup-linux.json.
- Fresh source mirrors/worktrees and fixed product reference were created successfully.
- Initial product inventory counted 23,335 lines across the top-level native database/interop Rust modules. This is a whole execution/ownership migration, not a library name substitution.
- Query source research identified SeaQuery 1.0.2, existing runtime arena validation and dialect-specific parameter rules. Upstream/toolchain research and validation-tool installation are in progress.

## Published checkpoints and reference

- Plan draft [PR #26](https://github.com/IzuSharp/Plan/pull/26), initial head `94ade5e6e7df2113be1a500d8ba33c0f0b8d8f11`; [CI 44948458663](https://github.com/IzuSharp/Plan/actions/runs/44948458663) succeeded, including unchanged historical gates.
- Design draft [PR #15](https://github.com/IzuSharp/NativeWeave-Design/pull/15), head `b1ec01dc94626b9480a96c32b7dd539a53a1799e`; [current-contract CI](https://github.com/IzuSharp/NativeWeave-Design/actions/runs/44948861357) and [historical CI](https://github.com/IzuSharp/NativeWeave-Design/actions/runs/44948861317) succeeded. The decision is C++20 with a runtime query arena, direct libpq 18.0 and SQLite 3.51.3.
- Retrieved all 12 fixed Rust reference packages from [merged product CI 44924918463](https://github.com/IzuSharp/NativeWeave/actions/runs/44924918463), candidate artifact `14715983822`. Archive SHA-256 `7a7982ccda96d3a5d7f3f4b00713a8668ae5548ec189419e3c22af5493248a11`; exact package and extracted-library hashes are in `rust-reference-provenance.json` and `rust-reference-packages.json`.
- Official SQLite 3.51.3 amalgamation `sqlite3.c`/`sqlite3.h` are byte-identical to the fixed Rust libsqlite3-sys 0.37.0 copies. The migration changes implementation ownership, not SQLite's file-format engine version.

## Local implementation and tests (preliminary)

The product working tree now contains `native/cpp` Contracts, Interop, scalar codecs, query arena/renderers/cache, mutations/relations, both providers, Host/ABI/transactions/streaming and migration/catalog administration, plus root CMake presets and Clang tooling. These files are still being integrated and have not yet been published as an accepted product commit.

- `linux-x64-release` configured with the exact Clang real paths and `x86_64-unknown-linux-gnu` target. Both separate provider libraries and the combined test Host linked successfully.
- Existing Data.NativeHost C# project built without public C# changes: zero warnings/errors. Its actual two-provider integration suite is now running; no pass is claimed here.
- Independent component work passed 52 exact dialect SQL/parameter goldens, 630 query/mutation assertions, C#-generated Contracts fixtures and malformed-input rejections, 17 scalar codecs with conversion boundaries, 19,673 Interop assertions and 634 executor assertions. These will be rerun from a committed product tree before acceptance.
- Actual SQLite and PostgreSQL migration/catalog tests passed 69 assertions, including atomicity, history/checksum, concurrent idempotence and recovery of failed nontransactional PostgreSQL DDL.
- ASan/UBSan component runs passed with leak scanning disabled. Local LeakSanitizer cannot initialize because the execution host blocks ptrace. Linux CI must still execute the full sanitizer preset with leak scanning enabled; local results are not a leak-safety acceptance claim.
- Independent review is finding and correcting Host lifecycle issues before formal consumer acceptance. No existing gate has been waived. An inherited SeaQuery constraint-name quoting defect and the existing migration-script trigger restriction are being recorded separately.

## Next work

Finish original managed two-provider regressions and fault/resource tests, then publish the first product checkpoint. Adapt all relevant native test/build/package paths to CMake, remove replaced Rust product maintenance paths, and produce candidate NuGet packages from the Release install tree. Run the same versioned consumer against the fixed Rust packages and C++ candidates, including old-data handover, independent SQL checks, Linux JIT/AOT, ABI/export/loading checks and model-change hash invariance. Complete isolated Rust-free build/pack verification, PR review, normal merges and merged-main CI before changing acceptance to complete.
