# DB-CPP-01 — database native implementation migration, Linux x64

**Status: in progress.** This report is being assembled from actual source-bound evidence. The Design decision has merged. Clean C++ production, the twelve-package feed and the complete same-source four-cell business comparison have passed; full retained regression has exposed an additional SQLite input-admission difference, so its correction, required product CI and final merge acceptance remain open. The authoritative machine-readable status is [acceptance.json](acceptance.json). A failed or missing gate is not accepted by this document.

## Scope and frozen reference

The owner authorized migrating the already delivered PostgreSQL/SQLite database product from Rust to C++, including implementation, tests, documentation, commits, PRs and normal merges. Public C# contracts, the C ABI, the twelve NuGet identities and persistent database state are the compatibility boundary. DB-API-01, DB-Perf-01, new ORM capabilities, a benchmark campaign, public NuGet publication and Windows/macOS acceptance are outside this task.

The first remote reads found the following merged main commits. Unmerged branches and earlier performance experiments were not added to the baseline.

| Repository | Frozen Rust-era input | Git tree |
| --- | --- | --- |
| [NativeWeave](https://github.com/IzuSharp/NativeWeave/tree/465cd0f90e6af05ec50eb581156240377cf0825b) | `465cd0f90e6af05ec50eb581156240377cf0825b` | `5f5d74ec7cfa502a4f8d119bb89e2e2776d4b65b` |
| [NativeWeave-Design](https://github.com/IzuSharp/NativeWeave-Design/tree/8298dc4128b745cf1809bad0c3cf02c45eb7f522) | `8298dc4128b745cf1809bad0c3cf02c45eb7f522` | `74f886a74a38d0478d1c4b4a22ea17383dfd0424` |
| [Plan](https://github.com/IzuSharp/Plan/tree/1fe52a8bd792ccdbb4bbea17ba59b0ad0c24349d) | `1fe52a8bd792ccdbb4bbea17ba59b0ad0c24349d` | `1124fde6d1b76cdf8f36ce4f10457b5386461990` |

The requested initial cleanup removed an orphaned old worktree/tool directory using approximately 610 MiB of allocated space. All 2,919 non-Git files had first been matched to reachable Design history; no unique source was discarded. [cleanup-linux.json](cleanup-linux.json) records the checks and removal. New work uses `task/DB-CPP-01-linux` in `ROOT/.worktree/DB-CPP-01-linux/{NativeWeave,NativeWeave-Design,Plan}`. The old product source is a separate read-only checkout at `ROOT/baseline/rust`.

The behavioral reference packages came from [merged product CI 44924918463](https://github.com/IzuSharp/NativeWeave/actions/runs/44924918463), artifact `14715983822`. Its ZIP SHA-256 is `7a7982ccda96d3a5d7f3f4b00713a8668ae5548ec189419e3c22af5493248a11`. All twelve package repository commits equal the fixed product commit. Common packages use `0.1.0-db-scope.1.1`; the five changed identities use `0.1.0-db-scope.1.2`. The extracted PostgreSQL library SHA-256 is `47ccb6e5752e74140a104fb3e2bc2558290f180528a0691771b01df2c963e3a7`, and SQLite is `a003326ce24eff467af1b88f40b03dcacf665fc71710db0ca85b29595471f0e9`. See [reference provenance](rust-reference-provenance.json), [individual package hashes](rust-reference-packages.json) and the versioned product `tests/Migration.Cpp/reference.lock.json`.

## Implementation and library decisions

The first published implementation checkpoint is product `b383c130903daba059c364ff0615d80798da1a3f`, tree `4bd509e639f9779092f5d037c7690a57cf8a28d4`, in [PR21](https://github.com/IzuSharp/NativeWeave/pull/21). The second checkpoint is `1d6935cdcfb381cc9ccd9ccc143d4bfaf1d4d690`, tree `e1949554a18fc18139501009c7fb5fecf07824f8`, with [CI 44957450975](https://github.com/IzuSharp/NativeWeave/actions/runs/44957450975). Its clean-source native producer, all 19 Release tests, full format/tidy and twelve-package preparation passed. It is not accepted: the real SQLite AOT comparison exposed a savepoint disposal/commit race after both JIT cells passed. The third candidate is `3e49cee95d206468a32c94f0a3b98e923f02acbf`, tree `f696ce6db636a3371ccf52ec777f710afa8c2a55`, with [CI 44959150281](https://github.com/IzuSharp/NativeWeave/actions/runs/44959150281). It contains the targeted savepoint correction and complete DocFX guide inputs. Clean-source production, twelve-package preparation and the complete same-source PostgreSQL/SQLite JIT/AOT business comparison have passed. The retained suite subsequently failed an original SQLite physical-input refusal assertion, described below; correction and fresh final gates are required. No final migration acceptance is claimed.

The maintained implementation is C++20, with C17 ABI callers and the existing C# facade. Business tables, columns, expressions, entities and DTO shapes remain runtime metadata. The query arena owns mutable builders and generation-bearing expression/alias identities; freezing produces immutable plans and ordered parameter descriptors. The application does not compile C++ when an ordinary C# model or DTO changes.

| Existing responsibility | C++ implementation | Selected upstream and reason |
| --- | --- | --- |
| Core ABI, handles, lifetime, owned buffers, errors, callbacks, async completion and executor retirement | `native/cpp/src/interop.cpp`, maintained fixtures and original public headers | C++ standard ownership/threading primitives; preserve the existing ABI and lifecycle contracts |
| Metadata, canonical schemas, scalar conversion, parameter and row-batch wire format | `contracts.cpp`, `scalar.cpp`, generated schema | nlohmann/json 3.12.0 for checked metadata parsing; retain db-wire/1 and the existing codec registry |
| Fluent builders, freeze/clone, aliases, ordered parameters, dialects and prepared query plans | `query.cpp` | Port the fixed NativeWeave validator and SeaQuery 1.0.2 semantics; keep all 52 exact SQL/parameter goldens |
| Relations, CRUD, bulk operations and optimistic concurrency | `mutations.cpp`, Host execution | Runtime relational metadata and actual provider statements; retain the current C# surface |
| PostgreSQL connections, TLS, prepared execution, incremental rows and cleanup | `provider.cpp` | PostgreSQL/libpq 18.0 asynchronous APIs, prepare/describe and single-row mode |
| SQLite connections, locks, prepared execution and persistence | `provider.cpp` plus static engine | SQLite 3.51.3 amalgamation, byte-identical to the fixed Rust libsqlite3-sys 0.37.0 engine sources |
| Source/pool/session ownership, admission, transactions, savepoints, streams and C entry points | `host.cpp`, `host_abi.cpp` | Finite queues and workers with explicit close/join boundaries; no new public execution abstraction |
| Migrations, catalog, history/checksum, concurrency and nontransactional recovery | `administration.cpp` | Direct provider APIs with the existing ledgers, SHA-384 migration checksums and dedicated administrative lease |
| Native production, package inventory and runtime closure | root CMake/presets and existing Packaging components | Pinned Clang/Ninja/CMake, Release installation, source and linked-input inventories; existing provider package split |

The finite source comparison is documented in [ADR-0006](https://github.com/IzuSharp/NativeWeave-Design/blob/main/docs/decisions/ADR-0006-database-cpp-native.md) and [the migration specification](https://github.com/IzuSharp/NativeWeave-Design/blob/main/docs/database/cpp-migration.md). KDb demonstrates runtime schema descriptions, but would add Qt and a second schema contract. sqlpp11/sqlpp23 emphasize C++ schema types and do not fit arbitrary business schemas admitted through C# metadata. Drogon provided an asynchronous provider reference, but its SQLite result collection does not satisfy the retained bounded stream behavior. Arrow ADBC informed independent stream/batch ownership. WCDB was a SQLite/bridge reference. None of those frameworks is a runtime dependency.

### Provider semantics

PostgreSQL prepares and describes the statement before exposing result metadata, starts execution on the first fetch and frees each single-row `PGresult`. It drains through the final null result on early exit. The fixed SQLx implementation did not send a cancel-key request when stopping a reader; preserving that behavior prevents ordinary reader disposal from newly aborting an enclosing transaction. Cancellation and deadlines stop business admission while the native owner remains responsible for bounded cleanup. Failure to prove a clean protocol state causes physical discard. An error received while draining unread results also discards the connection.

Loss of COMMIT acknowledgement remains `Unknown`; an independent connection seeing durable data does not rewrite that client outcome. A failed-transaction `25P02` probe followed by explicit rollback yields a known rolled-back outcome. The retained tests include a real framed TCP proxy which observes successful server COMMIT/idle messages, suppresses their acknowledgement and checks persistence independently.

The selected libpq source has a small hash-locked configuration patch which ignores ambient `PG*` defaults inside that library. The Host still rejects its original thirteen prohibited environment overrides. This preserves the fixed SQLx configuration boundary without modifying the process environment. Explicit TLS trust, hostname checks, plaintext opt-in and client-file behavior remain controlled by the provider configuration; tests include invalid default files under an isolated child process home.

SQLite executes prepare/bind/step/finalize on finite workers. The observable busy timeout, BUSY/LOCKED handling, transaction modes, read-only/query-only behavior, isolation refusal, journal/synchronous settings and actual autocommit state are retained. Early exit finalizes the statement without collecting all remaining rows. A real commit hook holds COMMIT beyond the configured 20 ms deadline: the public outcome becomes `Unknown`, then an independent connection confirms persistence after the hook is released, without rewriting that outcome. Old files keep the same SQLite engine and on-disk format.

Streams retain one bounded batch and bounded lookahead; transferred batches keep their reservation until release, including after cursor closure. Column shape is checked completely before decoding, and each field consumes the remaining aggregate row budget. These are the existing NativeWeave resource contracts, not a new whole-process RSS or performance claim.

### Dependency, license and toolchain identity

The product dependency lock records exact archive/source/patch/tool hashes. Candidate package inventories additionally record consumed headers, static archives, dynamic dependencies, exported symbols and actual binary hashes. The selected licenses are MIT (NativeWeave, nlohmann/json and adapted SeaQuery algorithms), PostgreSQL license (libpq), public domain (SQLite), Apache-2.0 WITH LLVM-exception (libc++/libc++abi), Apache-2.0 (platform OpenSSL) and the zlib license. Original notice files accompany the provider leaves. The DesktopPlatform fixed commit was a configuration reference; its AGPL implementation was not copied.

Linux uses LLVM 23.1.5, CMake 4.3.3, Ninja 1.13.2 and .NET SDK 11.0.100. CMake rejects GCC or a different upstream LLVM version and records compiler real paths, version and target triple. Maintained C ABI/CPU probes also explicitly select the locked Clang binary. Linux statically links the pinned libc++/libc++abi archives, libpq frontend archives and SQLite; declared platform OpenSSL 3, zlib and glibc dependencies remain visible in the ELF audit. SQLite and PostgreSQL are separate product leaves; the combined Host is a test-only artifact.

Windows convention is the same LLVM version with `clang-cl`, MSVC ABI/runtime and Windows SDK. Formal macOS convention is upstream LLVM with an Apple SDK; local Apple Clang must record its actual version/build separately. These conventions share the source and language standard but are not Windows/macOS acceptance results.

## Compatibility and verification

The original public C header and 42-signature inventory are byte-identical to the frozen reference. The private C++ declaration view only renames the C parameter identifier `template`, which is a C++ keyword; it changes no symbol, layout, calling convention or value. Existing C# public signatures, namespaces, nullability/defaults, generated entities/DTOs, async/cancellation/errors/disposal and package identities remain gates. Native exceptions are converted within the ABI boundary.

The retained twelve identities are `NativeWeave.Interop.Abi`, `NativeWeave.Core`, `NativeWeave.Data`, `NativeWeave.Database.Transactions`, `NativeWeave.Data.Streaming`, `NativeWeave.Query.Binding`, `NativeWeave.Query.Generator`, `NativeWeave.Database`, `NativeWeave.Database.Sqlite`, `NativeWeave.Database.Sqlite.Native`, `NativeWeave.Database.PostgreSql`, and `NativeWeave.Database.PostgreSql.Native`. Ordinary PackageReference consumers receive precompiled provider assets. Native AOT still has its normal .NET/platform linker prerequisites; ordinary model changes do not invoke a NativeWeave C++ build.

### One business source, old and new implementations

`tests/Migration.Cpp` contains the versioned C# business consumer, required cases, fixed reference lock, direct ABI refusal oracle and process driver. Reference and candidate runs use the same controlled source/input hashes, database version/options and equivalent snapshots. They execute in separate processes. SQLite files and PostgreSQL dumps created by the old package are handed directly to the candidate for read, continued write and migration-idempotence checks. Independent sqlite3/psql queries check stored data and ledgers, alongside the cross-implementation comparisons.

The fresh formal comparison at candidate `3e49cee95d206468a32c94f0a3b98e923f02acbf` passes all four cells. Both halves use the same clean consumer commit and separately verified business/driver/DTO/ABI/config hashes. The Rust libraries and packages remain fixed at `465cd0f`. Rust executes twelve business processes; C++ executes sixteen, including a rebuilt DTO variant in each cell. Each seed/observe/continue phase covers 26/25/30 semantic groups. All 24 actual C ABI refusal results match and all six observed native-owner counters return to zero. Neither consumer builds a Rust or C++ product library.

| Provider / mode | Fixed Rust baseline | C++ candidate 3 | Old data / continued writes / DTO hash |
| --- | --- | --- | --- |
| SQLite JIT | Passed | Passed | Passed |
| SQLite Native AOT | Passed | Passed | Passed |
| PostgreSQL JIT | Passed | Passed | Passed |
| PostgreSQL Native AOT | Passed | Passed | Passed |

Independent SQL confirms committed rows `10`, `11` and `12`, absence of savepoint-rolled-back row `90` and outer-rolled-back row `99`, the expected optimistic version/update/delete outcomes, and the same three migration history entries/checksums/success flags. Reapplying migrations is idempotent. Changing the DTO from three projected fields to four leaves the actual SQLite SHA-256 `14e5fd153b441cafb396ccfcb90ca67c366ccd05a403d9ddd75996e05dd338db` and PostgreSQL SHA-256 `7de544ad5550449535915b16ac323d4aa84da2b6025ebdec31081c06889fcdbf` unchanged.

The [complete comparison evidence](checkpoints/candidate-3/business-comparison/comparison.json) contains each semantic comparison, package inventory and ABI result. Safe exports retain the original raw artifact hashes: comparison `2a5e2f25fd825ac61fa1c886e2108c9670d4c89d5e814f7ba49598af2a39279b`, Rust result `516d16feecbd3ceaefde02a6ef08738fa8cf79a458e1a31189b676d435f96da0`, and C++ result `b653c790953dd0f4f97bb03824dbfccde89213c25a3825267d3c8e4069e39058`. The candidate-2 failure is preserved separately; it was not overwritten or reclassified.

### Original regression and fault gates

The [native correspondence](https://github.com/IzuSharp/NativeWeave/blob/task/DB-CPP-01-linux/native/cpp/tests/ported-tests.md) maps original Rust families to C++ and unchanged C# consumers. A01–A08/A20, B01–B07, query binding/native/Fluent, materialization, migrations, relations, compatibility, Core packaging and database package/release/runtime checks remain executable gates. These include original 52 SQL/ordered-parameter cases, real provider TLS/process/lock/COMMIT faults, transaction/savepoint outcomes, bounded large results, partial-read release and concurrent shutdown.

First-candidate formal A15 passed 20 JIT/AOT matrix rows, 30 policy cases, six actual NuGet closure controls, five XML rejection controls and all 85 commands. B05 passed its 24 commands and original JIT/AOT consumers. B06 and a separate Release CTest run exposed stream-retirement failures; those failures are preserved under [candidate-1](checkpoints/candidate-1/index.json), and do not count as acceptance.

The corrections establish two concrete barriers. A cursor completion ticket is published under the waiter's mutex only after actual cleanup and the worker's Cursor owner release, preserving immediate credit return after the last actual cursor/batch owner releases. Source operation retirement decrements its last pending owner under the same mutex used by Source join. Controlled tests pause precisely in the ownership and predicate/wait windows; deliberate early-return/unlocked-decrement mutations are rejected. The original deadlines and immediate-zero resource assertions remain intact.

The second candidate's SQLite AOT historical-data continuation found an additional savepoint lifetime difference. After explicit rollback/release, asynchronous disposal of the already removed token could incorrectly close the outer transaction when the next Commit owned the Session gate. With unchanged binaries and fresh copies of the same old snapshot, the candidate failed 11/12 bounded replays while the Rust reference passed 4/4. This is a product compatibility failure, not a flaky test to retry into success; its exact record is retained in [candidate-2 evidence](checkpoints/candidate-2/index.json). Candidate 3 now checks Closed/missing savepoint tokens before taking the Session gate and distinguishes genuine ordering failures from ordinary parent closure. Both disposal paths use that coordinator. Deterministic real-owner/file-database tests, independent SQL and two deliberately restored faulty implementations validate the correction at development scope; [the source-bound correction records](checkpoints/candidate-3-corrections/index.json) retain that boundary. The subsequent fresh packaged four-cell comparison above passed, including the previously failing SQLite AOT continuation.

Candidate 3 also exposed an original hard resource boundary in the full Orm.Relations suite. Under `MaxParameterBytes=8192`, the fixed SQLite provider rejects a roughly 7000-character JSON mutation after operation admission but before SQL dispatch: its finite input grant counts SQL bytes plus two complete canonical wire copies. C++ omitted that grant and accepted the operation. The unchanged C# assertion failed after all component verifiers and four complete JIT/AOT suites had passed. This is a compatibility defect, not a performance target; the original limit and the valid 3000-character case remain unchanged. [The failed source-bound receipt](receipts/candidate3-resource-failure.json) is retained, and a native-only correction is in progress.

The local environment prohibits Unix-domain sockets used by Roslyn's formatting build host and process inspection used by LeakSanitizer. Local ASan/UBSan results with `detect_leaks=0` are identified as such. The first product CI did execute .NET formatting successfully; final CI must execute the full sanitizer preset with `detect_leaks=1`. No local environment limitation substitutes for a required passing CI gate.

### Preserved limitations and verifier corrections

- SeaQuery 1.0.2's existing embedded-quote defect in a PostgreSQL conflict constraint name is preserved explicitly: a name `a"b` renders `ON CONSTRAINT "a"b"`. This migration does not silently change that public SQL output behavior.
- The accepted migration statement guard rejects a SQLite trigger body's terminal `; END;`. The restriction remains documented and tested.
- The old SQLx checksum-mismatch advisory-lock issue is retained as a named isolated negative-control setup; it is not presented as successful cleanup.
- The deliberately unconfirmed-retirement subprocess retains a finite quarantine and exits as an isolated negative control. It is not counted as successful resource release or a passing leak-sanitizer case.
- SQLx-private argument-buffer/drop-counter tests and chrono/SeaQuery-private value adapters are replaced by meaningful C++ canonical-wire/provider checks where the shape exists. A chrono leap-second/nanosecond shape unavailable in the public C#/wire contract is not claimed as a same-shaped C++ test.
- A15's old verifier omitted five Core source directories and referenced a missing package-rewrite helper. Those maintenance defects were corrected. XML classification now uses actual delegate metadata, with five rejection controls preserving the public documentation gate.
- First CI stopped on a missing `shlex` import in the migrated A02 harness after native/build/format gates had passed. Additional review corrected the offline SDK cache path, package receipt task labels, explicit Clang selection for maintained C probes and the fresh-builder versus pristine-SDK evidence labels. PostgreSQL-only native administration assertions are now explicitly wired into isolated Release and sanitizer runs. The second CI then exposed a missing input in standalone DocFX guide composition. Candidate 3 includes and hashes the shared C++ guide, retains warnings-as-errors and all API/XML controls, and saves nested diagnostics. These changes preserve checks rather than accepting skipped coverage.

## Build and reproduction

The shared presets are `native-base`, `linux-x64-release`, `linux-x64-asan-ubsan`, `windows-x64-release` and `macos-release`. Release and sanitizer build trees are isolated. Maintainers select the pinned tools, original API declaration inputs and a disposable PostgreSQL 18 endpoint. Consumers install the precompiled packages.

```sh
python3 eng/cpp_toolchain.py
. artifacts/toolchain/environment.sh
bash eng/postgres-tools.sh
export NW_POSTGRES_BIN="$PWD/artifacts/postgres-tools/install/bin"
export CMAKE_PREFIX_PATH="$PWD/artifacts/postgres-tools/install"

pre-commit install
pre-commit run clang-format --all-files
cmake --preset linux-x64-release
cmake --build --preset linux-x64-release
ctest --preset linux-x64-release
cmake --install artifacts/cmake/linux-x64-release
python3 eng/check_native.py tidy
bash eng/verify-cpp-sanitizers.sh
```

The pre-commit formatter uses fixed mirror commit `ce4bd7270237e95464b37d808b942f02785192c4` / clang-format 23.1.5. CI enforces the same version/rules even without a local hook. Generated ABI declarations retain their generator/byte checks. The incremental Git attributes/ignore changes preserve C# and NuGet rules, exclude local build/cache/compile-command/user-preset files and track shared presets.

For complete source-bound verification, begin with a committed clean checkout, provide the fixed API inputs at `artifacts/frozen-design` (`c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`) and `artifacts/frozen-plan` (`8afa0311f45ab8a8157fc45c51e95a0b17dd09f2`), and set `NW_TEST_POSTGRES` to a disposable PostgreSQL 18 server:

```sh
python3 eng/build.py verify --version 0.1.0-db-cpp.1 --compare-rust-reference
bash eng/verify-task04-linux.sh
bash eng/verify-task07-linux.sh
bash eng/verify-cpp-clean.sh
```

The migration comparison verifies the fixed old artifact before use. `NW_RUST_REFERENCE_ARCHIVE` supports an already verified offline copy. Ordinary future `eng/build.py verify` omits that finite historical comparison and requires no Rust toolchain, Rust source build or expiring old artifact. The fresh-builder image produces native libraries and packages with Rust absent; the separate pinned SDK image verifies pristine package consumption, and a runtime-only image receives only verified AOT outputs. The candidate publication policy remains local/CI packages; no new public release workflow is introduced.

## Review, PRs, CI and remaining work

| Repository | PR | Actual status |
| --- | --- | --- |
| NativeWeave-Design | [15](https://github.com/IzuSharp/NativeWeave-Design/pull/15) | Merged as `de1f4796dc199250b405ea99f2129d611f17b1f6`; tested and merged tree both `8dbb89bb028be6f0f910f43daa3042c1a84289ac` |
| NativeWeave | [21](https://github.com/IzuSharp/NativeWeave/pull/21) | Draft; corrections and final source-bound acceptance pending |
| Plan | [26](https://github.com/IzuSharp/Plan/pull/26) | Draft; handoff/evidence and this report in progress |

Design's exact merged-main [current-design CI](https://github.com/IzuSharp/NativeWeave-Design/actions/runs/44956543416) and [historical acceptance CI](https://github.com/IzuSharp/NativeWeave-Design/actions/runs/44956543440) passed. Independent technical review is recorded as an honest COMMENT under the existing GitHub identity, without impersonating another approver. The [first product CI](https://github.com/IzuSharp/NativeWeave/actions/runs/44955442617) failed in the A02 harness and is retained as failed evidence. Plan checkpoint [CI 44956128270](https://github.com/IzuSharp/Plan/actions/runs/44956128270) passed its current progress and unchanged historical gates.

The migration remains incomplete until the corrected product commit passes full retained regression, dual-provider same-source JIT/AOT comparison, old-data handover, source-tree-external package consumption, clean no-Rust production/runtime, full CI sanitizers, review, normal merge and exact merged-main CI. This report will be finalized from those receipts; it does not predeclare their results.
