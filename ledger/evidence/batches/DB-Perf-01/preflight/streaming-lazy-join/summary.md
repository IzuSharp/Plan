# TypedStream lazy join: affected AOT checks

The selected `TypedStream` change passed the actual Linux x64 Native AOT checks described here. **This is affected-module correctness and a narrowly bounded allocation regression, not the external-package before/after result or whole-framework zero-allocation acceptance.** The public consumer measurements remain a separate experiment.

## Source and binary identity

The source-review decision and frozen candidate hashes are in [production-snapshot-002.md](../../reviews/production-snapshot-002.md). Only the reviewed `src/Data.Streaming/TypedStream.cs` change, three new Streaming test files and the test entry-point additions were applied. No `DbWire`, decimal codec, native source or public API change was included.

The [build command](build-command.json) records the actual checkout HEAD at build time, `565e693b36060cb0582abce522670392cb6f5dfe`, plus the five modified file hashes. That HEAD identifies the surrounding checkout; the candidate production change was still uncommitted and is identified by `TypedStream.cs` SHA-256 `91294bd51fcba16aec116512ce89f08866108de73751dd47ef255218201bf6af`. All five reviewed file hashes were unchanged across publication.

| Artifact | SHA-256 |
| --- | --- |
| Actual AOT `Korda.Data.Streaming.Tests` executable | `4f9721ab476bd24ef991b5fbbe6baf4411bc1ac2420f56a03cd13e7ce6b073f0` |
| Copied `libkorda_streaming_fixture.so` | `fa14bd2923d051260c0131b00b4c9afe295d4ade674e6239dde8166c4e978789` |

Publication used the real .NET SDK 11.0.100 and Clang 23.1.5, ordinary serial MSBuild options, committed AOT lock inputs, and a read-only fallback view of the verified SDK support packages. [publish.log](publish.log) records the successful build. No JIT consumer was executed.

## Results

| Check | Raw result | Evidence |
| --- | --- | --- |
| Isolated synchronous numeric in-batch allocation gate | 16 measured windows, 4,095 rows each, 65,520 rows total; sum of raw allocation deltas **0 B**; each individual window **0 B**; no fetch or incomplete move inside any window | [Raw counters](allocation-gate/allocation-probe-sync-inbatch.json), [log](allocation-gate.log) |
| Deterministic lifecycle races | **46 assertions passed**: pending start/fetch, rejected concurrent move, two disposers, blocked synchronous mapper, mapper error, cleanup error and cancellation token/retirement ordering | [log](lifecycle-races.log), [commands](test-commands.json) |
| Existing actual-provider Streaming suite | **615 assertions and 60 cases passed**, 30 cases per provider, plus six shape-preflight checks; `dynamicCodeSupported=false` | [raw results](provider-results/results.json), [complete log](aot-all-streaming-providers.log) |
| Final owner checks in the provider suite | `managed-live-bytes=0`, `native-wrappers=0`; all observed native retirement and lease-release checks passed | [complete log](aot-all-streaming-providers.log) |
| Isolated PostgreSQL shutdown | Normal fast stop; server exit code **0** | [shutdown](provider-postgres-stop.log), [cluster receipt](provider-cluster.json) |

The full provider suite also invoked the same allocation gate and lifecycle races, with a second independent gate record at [provider-results/allocation-probe-sync-inbatch.json](provider-results/allocation-probe-sync-inbatch.json). This repetition follows the default test entry point; it is not counted as an external public-package process or a long-load segment.

The actual-provider cases cover empty/single/multiple-batch results, slow consumption, early break, mapper failure, large-field rejection, buffered row/byte limits, First/Single semantics, value defaults, scalars, lease disposal, NULL, method/enumerator cancellation, concurrent disposal, cleanup failures and malformed wire payloads. PostgreSQL method cancellation, enumerator cancellation and concurrent disposal reported `reusable-probe=0`, while retirement and lease release still passed. A retired connection was not reported as reusable.

The zero-allocation boundary starts after acquisition and parsing of the first row's batch. It excludes stream creation, fetch, parsing, final false and disposal. Numeric values are consumed as value types with checksums; business reference outputs are absent. A per-row zero result therefore does not establish a per-query or per-batch zero result. The actual-provider correctness suite's broader allocation/RSS observations include its test machinery and are not used as a performance comparison.

## Reused native fixture, newly executed managed checks

The native code was unchanged by this experiment. Instead of recompiling an unrelated C++ closure, the previously verified fixture was read from the DB-Rename verification artifacts and copied into this task's own directory. Its receipt SHA-256 was checked before and after copying. **All 95 recorded native/CMake/format input files matched the current worktree byte for byte** before execution and were checked again after the run. The current managed test binary was newly compiled and all provider cases were newly executed.

[native-fixture-reuse.json](native-fixture-reuse.json) retains every matched input, the original source/artefact receipt paths and hashes, and the copied fixture hash. [fixture-dependencies.log](fixture-dependencies.log) records the loaded system dependency resolution. No file in the old worktree was modified, and no old managed test result was reused as a result of the new source.

The provider suite used a newly initialized PostgreSQL cluster in `/workspace/scratch/754bc732518e/streaming-lazy-join-validation/provider-postgres-data`, with its own loopback TCP port and `-k ''`, `fsync=on`, `synchronous_commit=on`, and `full_page_writes=on`. It did not use another agent's cluster. Initialization, test execution and shutdown commands with times and exit codes are retained in [provider-test-commands.json](provider-test-commands.json). The host was not reserved, so elapsed durations in those command records are diagnostic only.

The existing correctness JSON contains a historical `memoryScope` description mentioning SQLx/Tokio. Those labels are a stale test-description string, not observed runtime components. The fixture provenance and 95 matched current C++ inputs establish which native implementation was exercised. The raw result was preserved unchanged rather than rewriting historical field text after execution.

## Reproduction and limits

Use the exact arrays in [build-command.json](build-command.json), [test-commands.json](test-commands.json) and [provider-test-commands.json](provider-test-commands.json), with a fresh task-owned PostgreSQL data directory and free TCP port. A reused fixture must match every entry in [native-fixture-reuse.json](native-fixture-reuse.json); otherwise build the fixture from the selected source before running the provider suite.

This run did not execute the sample/API-documentation substeps of `tests/Data.Streaming/verify.py`, did not measure sustained load, CPU or latency, and did not validate either after package. The parent task owns official bundle creation and affected downstream/API checks. The unchanged external package consumer will supply matching before/after process-wide allocation measurements, package/executable/native hashes and complete-query costs.
