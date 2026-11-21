# DB-CPP-01 Linux handoff

## Current state: first C++ candidate published; stream-retirement correction before packaging

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
- Finite source selection is recorded in Design PR15: the runtime query arena follows fixed SeaQuery 1.0.2 semantics; direct libpq 18.0 and the exact baseline SQLite 3.51.3 engine execute SQL. LLVM 23.1.5, CMake 4.3.3, Ninja 1.13.2 and .NET 11.0.100 are installed with recorded hashes.

## Published checkpoints and reference

- Plan draft [PR #26](https://github.com/IzuSharp/Plan/pull/26), initial head `94ade5e6e7df2113be1a500d8ba33c0f0b8d8f11`; [CI 44948458663](https://github.com/IzuSharp/Plan/actions/runs/44948458663) succeeded, including unchanged historical gates.
- Design draft [PR #15](https://github.com/IzuSharp/NativeWeave-Design/pull/15), head `b1ec01dc94626b9480a96c32b7dd539a53a1799e`; [current-contract CI](https://github.com/IzuSharp/NativeWeave-Design/actions/runs/44948861357) and [historical CI](https://github.com/IzuSharp/NativeWeave-Design/actions/runs/44948861317) succeeded. The decision is C++20 with a runtime query arena, direct libpq 18.0 and SQLite 3.51.3.
- Product draft [PR #21](https://github.com/IzuSharp/NativeWeave/pull/21), first candidate `b383c130903daba059c364ff0615d80798da1a3f`, tree `4bd509e639f9779092f5d037c7690a57cf8a28d4`. [PR CI 44955442617](https://github.com/IzuSharp/NativeWeave/actions/runs/44955442617) was still running at this checkpoint. This is a reviewable implementation, not completed acceptance. Design subsequently records source/dependency refinements at `f851d0cd5803c11836b4c298cf600f6ab9281da5`.
- Retrieved all 12 fixed Rust reference packages from [merged product CI 44924918463](https://github.com/IzuSharp/NativeWeave/actions/runs/44924918463), candidate artifact `14715983822`. Archive SHA-256 `7a7982ccda96d3a5d7f3f4b00713a8668ae5548ec189419e3c22af5493248a11`; exact package and extracted-library hashes are in `rust-reference-provenance.json` and `rust-reference-packages.json`.
- Official SQLite 3.51.3 amalgamation `sqlite3.c`/`sqlite3.h` are byte-identical to the fixed Rust libsqlite3-sys 0.37.0 copies. The migration changes implementation ownership, not SQLite's file-format engine version.

## Local implementation and tests (preliminary)

The product candidate contains `native/cpp` Contracts, Interop, scalar codecs, query arena/renderers/cache, mutations/relations, both providers, Host/ABI/transactions/streaming and migration/catalog administration, plus root CMake presets and Clang tooling. The preliminary runs below retain their original development boundary; the following committed-candidate section identifies the source-bound reruns.

- `linux-x64-release` configured with the exact Clang real paths and `x86_64-unknown-linux-gnu` target. Both separate provider libraries and the combined test Host linked successfully.
- Existing Data.NativeHost two-provider C# integration ran 482 assertions / 174 retirements with zero remaining diagnostic owners. This was a development run and must be repeated with the final committed binaries.
- Independent component work passed 52 exact dialect SQL/parameter goldens, 630 query/mutation assertions, C#-generated Contracts fixtures and malformed-input rejections, 17 scalar codecs with conversion boundaries, 19,673 Interop assertions and 634 executor assertions. These will be rerun from a committed product tree before acceptance.
- Actual SQLite and PostgreSQL migration/catalog tests passed 69 assertions, including atomicity, history/checksum, concurrent idempotence and recovery of failed nontransactional PostgreSQL DDL.
- ASan/UBSan component runs passed with leak scanning disabled. Local LeakSanitizer cannot initialize because the execution host blocks ptrace. Linux CI must still execute the full sanitizer preset with leak scanning enabled; local results are not a leak-safety acceptance claim.
- Independent review is finding and correcting Host lifecycle issues before formal consumer acceptance. No existing gate has been waived. An inherited SeaQuery constraint-name quoting defect and the existing migration-script trigger restriction are being recorded separately.

## Component-port checkpoint (development evidence, not final acceptance)

- Original Interop A01–A08 and A20 consumers, examples and API/XML checks executed as JIT and Native AOT. A20 retained 8,925 assertions, 72 orderings, two subprocess cases, 20,000 fuzz inputs and actual sanitizer-fatal controls. Static-libc++ replay evidence is under `ROOT/_validation/logs/interop-libcxx-{replay,fuzz}`.
- Original Query.Binding JIT/AOT passed 66/67 assertions and ten families; Query.Native passed 52 cases and 180/181 managed assertions against the fixed 52 old SQL/ordered-parameter/row oracles. Model/DTO changes retained the native hash.
- Original SQLite fourteen native families passed 140,219 assertions, including 40,000 rows, actual lock/collation interruption, durable commit with lost acknowledgement, finite admission, physical retirement and last-parent closure. Its unchanged managed JIT/AOT each passed 44 assertions.
- Original PostgreSQL eleven families passed real TLS, timeout/failed-transaction state, savepoints, backend reuse, CTE conflict snapshot, delayed drain/quarantine, admitted close and parent retirement. The actual TCP proxy observed successful server COMMIT, dropped the response and independently confirmed durable data while the client retained Unknown. A new run binds the patched libpq source; no unpatched run is presented as patch validation.
- Original B05 transaction managed consumers passed 29 assertions / eleven families in both modes, and the native port passed thirteen families / fifty checks. Original B06 streaming consumers passed 598 assertions / 58 cases per mode across both providers; its native port passed six families / 127 checks. B07 ran 120 real database roundtrips per mode plus 4,189 malformed refusals without increased provider sends.
- Original B01 abstractions passed 149 compiled API entries, twelve families, ten goldens, 43 malformed and seventeen scalar cases, including ordinary package JIT/AOT. The Core package verifier passed the six-component external PackageReference closure in both modes, missing-native controls, CPU and dynamic-runtime checks.
- These results are working-tree integration evidence. Formal producer/verifier receipts still require an unchanged committed source. A15 is being rerun after correcting an old verifier input list that omitted five current Core source directories; public signatures and failure controls remain unchanged.
- Removed 142 replaced Rust product/test source and Cargo-toolchain files. The product-scope check now finds zero Rust product inputs. Public C ABI/header/signature and C# contract bytes remain retained. The package producer now uses the shared Release install tree, source/patch/dependency locks, exact Clang binary hashes and static LLVM libc++/libc++abi.
- Final resource review found and is fixing aggregate row-payload budgeting and administrative wait/close-cancel semantics. Each fix has a targeted retained-contract regression. The source-bound business parity consumer is now versioned under `tests/Migration.Cpp`; its fixed-Rust half is executing first.

## Next work

Correct the observed streaming retirement race without weakening the existing immediate-credit or three-second completion assertions, then publish a new product source and rerun the affected native/managed gates. Produce the twelve-package candidates and run the candidate half of the same business source against both databases × JIT/AOT, direct old-data handover, independent SQL and model-change hash checks. Complete the unchanged managed regressions, clean Linux image build/package/runtime, CI LeakSanitizer and source-bound review. Record normal merges and exact merged-main CI. Update acceptance only with hash-bound complete evidence; the migration is still in progress.

## First committed candidate: actual results and open failure

All identities in this section are product `b383c130903daba059c364ff0615d80798da1a3f` / tree `4bd509e639f9779092f5d037c7690a57cf8a28d4`, unless explicitly identified as the Rust baseline. Result summaries are preserved under `checkpoints/candidate-1/`.

- The source-bound `python3 eng/build.py native` producer passed from a clean tree, using the exact Release preset and patched libpq provenance. SQLite native SHA-256 is `2f427ff458be3136e4be6e249dbccaef577f6ec29acc03d151a212842812f9f5`; PostgreSQL native SHA-256 is `e2e840926369779568c8f3022c3039f7382386ee110fa39712cb83933dfdff0a`. These first-candidate binaries will not be packaged as the final migration if native source changes.
- The pinned full project clang-tidy scan passed. Local `dotnet format` could not start its Roslyn build host because this execution environment prohibits Unix-domain sockets; the mandatory CI formatting step remains enabled.
- Formal A15 compatibility passed with `prepare_only=false`, clean and stable source: 20 JIT/AOT matrix rows, 30 policy cases, six actual NuGet closure controls, five XML rejection controls and all 85 commands.
- Formal B05 transactions passed all 24 commands, including the original managed JIT/AOT consumers with 29 assertions and eleven families, bound to the exact historical Design inputs.
- Formal B06 stopped at its native test: one three-second `streaming control timeout`. Five immediate replays passed, but separate diagnostic replay and the full Release CTest exposed a second real failure: `wide-row refusal returns staging and wire credits`. Release CTest passed 18/19. Investigation identified retirement publication/worker ownership and a possible lost wake-up; no retry has been counted as acceptance and no assertion or deadline has been relaxed.
- The fixed Rust side of `tests/Migration.Cpp` completed all four provider/JIT/AOT cells, seed/observe/continue in 12 independent processes. Each cell ran 26/25/30 semantic groups; independent SQL and the 24 ABI refusal cases passed, with all six native-owner counters zero. Four historical database snapshots and their hashes are retained in `ROOT/_validation/migration-compare-final-1/baseline`. The result SHA-256 is `621f5547ef5b9391fdc70569c39a469b983d7ec6195d6187c740c7c79c84e04d`. Candidate execution remains pending; matching consumer/input hashes permit reuse after a native-only correction while recording each actual source identity.
- The current libpq patch is `a6c33133d9900b5bd6460245331ad7d9a8b256786dcd1bd927b5491b52921ddd`. Formal local C++ work must select `NativeWeave/artifacts/postgres-cpp-tools/install/bin` and its CMake prefix; the older unpatched tool directory is reference/development only.
