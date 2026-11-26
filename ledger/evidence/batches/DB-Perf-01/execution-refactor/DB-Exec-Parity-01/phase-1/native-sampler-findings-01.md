# DB-Exec-Parity-01 — actual CPU leaf samples and runtime sensitivity

This is a first-stage diagnostic, not an optimized candidate, parity claim, or long-run acceptance result. Product source and public API were unchanged for these samples. The four Release Native AOT baseline ELFs are the same ones used by the ordinary phase receipts. Sampling, runtime-setting sensitivity, and ordinary timing retain separate identities.

## Instrumentation is demonstrably working

The independent library and reproducible commands are described in [native sampler README](../diagnostics/native_sampler/README.md). Accepted library `builds/03/libparity_sampler.so` SHA-256 is `896c0c8514b4a7f3112a9701543786473aa0e04e8c0485c72f41d8427b302d15`.

The positive five-thread fixture produced 1,241 real CPU samples. Every business thread had samples in its actual noinline hot function, matching ELF symbols, inline source lines, correct TID/RAW timestamps, and self context-switch events. The user-buffer negative control recorded 1,262 dropped raw records and 5,006 dropped markers. The unwrapped-thread control exposed one observed unregistered thread; explicit `parity_touch` then sampled all six threads. These are retained validation results, not assumptions about profiler availability.

The kernel-ring negative control is especially consequential: a one-page ring with a 500 ms drain retained 617 samples, reported **655 lost samples through `PERF_FORMAT_LOST` readback, and emitted zero lost-record payloads**. Therefore the first four-consumer profile using sampler version 02 could not establish complete loss accounting. It was retained separately, and the complete four-path sample was repeated using version 03. The accepted version-03 paths report zero kernel readback loss, emitted loss, user-buffer drops, ring overruns, malformed records, TID mismatch, and backwards sample clocks. Independent binary decoding matches the emitted JSONL record for record. [Validation reports](../diagnostics/native_sampler/validations/)

| Accepted diagnostic | Registered business threads | All CPU samples | Samples inside warm route windows | Collector thread CPU, whole process lifetime |
| --- | ---: | ---: | ---: | ---: |
| SQLite / Korda | 18 | 7,368 | 6,798 | 169.80 ms |
| SQLite / Dapper.AOT | 7 | 357 | 314 | 2.43 ms |
| PostgreSQL / Korda | 18 | 8,425 | 7,774 | 190.19 ms |
| PostgreSQL / Dapper.AOT | 11 | 360 | 285 | 12.01 ms |

The collector is excluded from CPU samples, and its cost is disclosed above. All noncollector TIDs actually observed by periodic `/proc/self/task` scans were registered. This is **observed coverage**, not proof that a short-lived unwrapped thread could not have appeared and disappeared between scans. Registered threads can outnumber observed threads because the wrapper records threads that exit between inventory scans.

Raw data is in [sampled-phases-02](../measurements/sampled-phases-02/). Accepted analysis is in [SQLite](sampled-phases-02-verified/sqlite/) and [PostgreSQL](sampled-phases-02-verified/postgresql/), including `analysis.json` per client, original sampled addresses, module bindings, exact sized `nm` symbols, batched `addr2line`, and actual-ELF disassemblies. The exact analyzer used is retained with each provider analysis. Earlier overstrict rejection of native modules lacking a GNU BuildID remains in `sampled-phases-02/`; the verified analyzer explicitly binds those same ELF bytes through SHA-256, phase `NativeSha256`, path and PT_LOAD mapping rather than inventing a BuildID. All AOT split-debug files have matching BuildIDs and independent file hashes.

## Clock and symbol binding

The original consumer's warm windows have absolute `StartedTicks` and `FinishedTicks`, with Stopwatch frequency 1,000,000,000. The actual four AOT ELFs contain `SystemNative_GetTimestamp → minipal_hires_ticks`; their machine code passes clock ID 1 to `clock_gettime`, proving MONOTONIC for this binary. The matching runtime source has `Stopwatch.GetTimestamp → Interop.Sys.GetTimestamp → minipal_hires_ticks`. CPU samples use RAW. Each process has start/end RAW-before, MONOTONIC, RAW-after brackets; the analyzer interpolates between their midpoint offsets and also tests the full observed offset envelope. No selected sample in these four runs changes window membership within that observed envelope. An arbitrary unobserved intermediate clock adjustment remains outside the proof.

The authoritative leaf-name binding is the actual sampled IP minus runtime load bias inside a sized `nm` function interval. DWARF source/inline output is retained separately. Optimized runtime DWARF can name a neighboring function or line and is not silently promoted to trustworthy source attribution. The sampler has no call chains.

## Confirmed CPU concentration

Each route below contains 768 successful phase operations (three windows of 256). The result is the same ordered 1,000-row two-column DTO list with the original validation contract. Sampling period is 1 ms. Percentages are diagnostic leaf sample shares, not exact exclusive CPU time or a substitution for the ordinary CPU/operation receipts.

| Database | Route | Warm samples | `RhSpinWait` samples | Leaf share |
| --- | --- | ---: | ---: | ---: |
| SQLite | Korda Fluent | 2,313 | 1,350 | 58.37% |
| SQLite | Korda hot Prepare | 2,221 | 1,320 | 59.43% |
| SQLite | Korda Host SQL | 2,264 | 1,339 | 59.14% |
| SQLite | Dapper.AOT | 314 | 0 | 0.00% |
| PostgreSQL | Korda Fluent | 2,607 | 1,379 | 52.90% |
| PostgreSQL | Korda hot Prepare | 2,651 | 1,344 | 50.70% |
| PostgreSQL | Korda Host SQL | 2,516 | 1,332 | 52.94% |
| PostgreSQL | Dapper.AOT | 285 | 96 | 33.68% |

The near-identical Korda Fluent, hot Prepare and direct-Host leaf distributions reinforce the prior evidence that construction alone cannot explain the thousand-row CPU gap. In SQLite hot Prepare, 1,320 `RhSpinWait` samples are split across four TIDs (335, 359, 329, 297); those TIDs also execute managed reader/monitor code. Three different TIDs account for most native SQLite samples. The Dapper SQLite warm window has all 314 CPU samples on its original thread. In PostgreSQL hot Prepare, `RhSpinWait` likewise concentrates on four managed-code-active TIDs (510, 332, 304, 198), while libpq/native work appears mainly on three other TIDs. The current samples establish this division of work; a diagnostic request/batch timeline is required to name the ownership/notification paths causally.

SQLite's remaining named leaves include engine execution, native preflight/advance/BatchWriter, row layout access, DbWire validation, Monitor Enter/Exit, and pthread mutex operations. Dapper SQLite includes engine execution, SafeHandle AddRef/Release, SQLitePCLRaw entry points, column type reads, and P/Invoke transition code. PostgreSQL's non-spin named leaves include `pqParseInput3`, native provider advancement/BatchWriter, allocation/free, managed row work and Monitor operations; Dapper includes Npgsql reader/converter and generated reader paths. Low counts at individual leaves cannot rank tiny optimization candidates precisely. Some libc internal implementation addresses have no sized public symbol and stay explicitly unresolved rather than being labeled as a guessed memcpy or allocator helper.

Self context-switch records corroborate extensive cross-thread scheduling in Korda. For example, the four SQLite hot-Prepare TIDs holding the `RhSpinWait` samples each have roughly 12,000–13,000 switch-outs across the 768-operation warm windows; a separate low-CPU thread has 24,312 switch-outs. Dapper SQLite's sampled thread has one switch-out across those windows. These are self event counts, not FFI calls, SQL dispatches, network round trips, or individual request waits. Pairing found no duplicate-out or backwards-pair anomaly. Complete off-CPU pairs cannot distinguish sleeping from runnable delay, and their times overlap across threads.

## Current runtime source and static machine code

The actual restored compiler package is `runtime.linux-x64.Microsoft.DotNet.ILCompiler/11.0.0`. Its nuspec records [dotnet/dotnet VMR commit 297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f](https://github.com/dotnet/dotnet/tree/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f). That commit's [source manifest](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/source-manifest.json) maps runtime to `deae2e32bf0e018e09d64597b7c59b62b73bb3ce`. Package/asset hashes, exact fetched source bytes, URLs, source hashes and the manifest are in [runtime-source-297acf](../diagnostics/runtime-source-297acf/). The old `da153c2` runtime experiment is not used as this run's source identity.

The current `LowLevelLifoSemaphore` constructor defaults its spin limit to 1024 and calls `AppContextConfigHelper.GetInt16ComPlusOrDotNetConfig`. The helper reads `DOTNET_ThreadPool_UnfairSemaphoreSpinLimit`, then falls back to the COMPlus alias, parses the value as hexadecimal, and accepts zero. `WaitSlow` uses this configured limit for its optimistic exponential-backoff loop. The Native AOT `Thread.SpinWaitInternal` invokes `RuntimeImports.RhSpinWait`. [LowLevelLifoSemaphore source](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Threading/LowLevelLifoSemaphore.cs#L68-L119) · [Configuration helper](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/AppContextConfigHelper.cs#L244-L270) · [AOT Thread](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/coreclr/nativeaot/System.Private.CoreLib/src/System/Threading/Thread.NativeAot.cs#L322-L349)

This read is present in the actual AOT machine code: SQLite Korda's constructor loads the spin-limit string, places default `0x400` in the argument register and calls the configuration helper; the helper loads the `DOTNET_` and fallback `COMPlus_` literals and calls `Environment.GetEnvironmentVariable`. Equivalent functions are retained and disassembled for all four binaries. [Static evidence index](runtime-spin-static-01/index.json)

Static direct callers of `RhSpinWait` also include general `Lock.TryEnterSlow`, `ObjectHeader.TryAcquireUncommon`, `Thread.SpinWait/LongSpinWait`, and a separate `LowLevelLifoSemaphore.WaitAsWaiter` path. Dapper additionally contains a ReaderWriterLockSlim spin caller. A three-level reverse static graph is retained; it does **not** establish which callers supplied the sampled leaf time. Even a zero configured semaphore spin limit does not disable every remaining spin in semaphore or lock code.

## Same-ELF causal sensitivity, not a product optimization

The independently run [spin-sensitivity-01](../measurements/spin-sensitivity-01/) experiments clear both aliases for default and set only the DOTNET alias to zero for `spin0`. Round 1 reverses client/setting order. Both frameworks use the same setting within each comparison, the same unchanged AOT ELF, and 768 operations per route per round. These runs have no sampling preload and remain a bounded diagnostic of the runtime setting, not final acceptance.

| Database/client/route | Round | Default CPU µs/op | Spin-0 CPU µs/op | Default service p50 µs | Spin-0 service p50 µs |
| --- | ---: | ---: | ---: | ---: | ---: |
| SQLite / Korda hot Prepare | 0 | 3,811.408 | 2,036.668 | 1,802.622 | 1,760.814 |
| SQLite / Korda hot Prepare | 1 | 3,654.510 | 2,086.790 | 1,772.745 | 1,805.356 |
| SQLite / Dapper.AOT | 0 | 394.697 | 388.641 | 359.135 | 358.009 |
| SQLite / Dapper.AOT | 1 | 369.568 | 384.008 | 350.287 | 357.944 |
| PostgreSQL / Korda hot Prepare | 0 | 4,105.382 | 2,844.908 | 2,498.735 | 2,764.354 |
| PostgreSQL / Korda hot Prepare | 1 | 4,666.160 | 2,878.413 | 2,849.088 | 2,731.834 |
| PostgreSQL / Dapper.AOT | 0 | 500.716 | 370.188 | 485.758 | 480.159 |
| PostgreSQL / Dapper.AOT | 1 | 525.844 | 431.953 | 491.721 | 489.385 |

The repeated Korda CPU reduction is causally attributable to changing that runtime setting under this short workload: approximately 1.57–1.77 ms/op for SQLite and 1.26–1.79 ms/op for PostgreSQL. SQLite latency stays in the same narrow range while CPU falls substantially. PostgreSQL latency changes direction between rounds. Thus the saved CPU is not equivalent to a proven reduction in the request's critical-path latency. Dapper SQLite supplies a useful low-scheduling negative comparison; Dapper PostgreSQL's own CPU reduction is consistent with its measured spin leaf concentration.

This result supports investigating the repeated asynchronous handoffs that feed spinning/parking workers. It does not justify adopting a global runtime switch as a Korda fix, crediting all `RhSpinWait` samples to the semaphore, subtracting sample fractions from ordinary CPU, or skipping the remaining request-stage evidence. Stage tracing must still associate native task enqueue/start, ready publication, managed scheduling/take, row materialization, EOF and retirement with the same request and batch; preserve ownership and exception ordering before changing publication or continuation policy.

## Next evidence priorities

1. Establish the exact number and ordering of native worker, callback/coordinator, and consumer continuation handoffs per query/batch, including full 32 rows and empty EOF. Compare actual waiting and CPU on the same TID.
2. For any reduced-handoff candidate, prove that root/registration/control retirement and native notification tails complete before business continuation publication, and that reentrant next-generation work cannot be modified by the previous callback's cleanup or exception boundary.
3. Then use same-machine interleaved uninstrumented A/B to test whether the specific scheduling count and corresponding CPU fall, without trading cancellation, early stop, ownership or errors for speed. Runtime defaults must be restored for product acceptance.
4. Continue native copy/allocation and per-row/per-column tracing. This profile does not yet identify exact copied byte totals, allocation call stacks, server execution costs, protocol wait times, or the full 35-business decomposition.

No final Stage 1 completion or optimization acceptance is asserted by this document alone.
