# Perf-01 final candidate: completed layered profiles

This is a descriptive, data-only projection of completed profiling evidence for product commit `ada13b865ec5d19876745498f6f51d8ad2367399`, tree `0d1b1ca390b582b1f2ebf004f7778c8f084a68a4`. The before product is `ea5fa528035d025bd7a28698ee7c71194432236c`. The current candidate includes R1, R2, R3 and the separately documented native shutdown correctness correction. The profiles do not isolate every change from every other change.

**Formal comparison credit: 0. Long-stage credit: 0 seconds. No additional runtime change was made for this report.** Independent formal comparisons, capacity tests and accepted long runs determine retention and application-level benefit. A single historical before process versus a single after process does not establish a latency improvement or regression.

`public-summary.json` contains fixed role labels, numbers, booleans, UTC timestamps and content hashes. It preserves the exact start/end/exit of all 22 queue commands, the six Inspect process results, all page and retirement aggregates, both HTTP protocols, all four gRPC modes, resource observations and descriptive absolute/percentage changes. The underlying scripts, commands, host paths, process identifiers, environment values and raw records are not copied into this public projection. Full evidence remains local and hash-bound; this report does not claim that it or the private extractor has been remotely archived.

## Execution and identity

The recorded layered queue ran from **2026-11-20 04:55:54.660538 UTC to 04:59:53.951191 UTC**. Its 22 commands completed with actual exit code 0: six interleaved Inspect processes; SQLite and PostgreSQL page probes; one SQLite retirement probe; prepare/run pairs for HTTP JSON, HTTP tiny and four gRPC modes; and the existing protocol-reader extraction. The exact per-command times, output hashes and result-validation flags are retained in the JSON. This interval is the queue's own receipt, not an inferred effective-load interval.

The final nine-step build receipt was completed before the queue and is bound by SHA-256 `800560f7674b0a4b5eecdcbf357577c862daf92470768b6fdf10854edc972c43`. Thirteen application inputs were already checked equal by that producer. This projection verifies the common package hashes recorded by the page, retirement and protocol manifests and the reused application source hashes. It records consumer executable and actually loaded native hashes from the existing results/producer records; **it does not rehash executables, native libraries or package archives**.

The six Inspect processes use the same committed profile source `6bf7f6c4a8152cad2882f3d9f504f095b9627973`. Page and retirement application source hashes are equal before/after. Protocols reuse the same before client executable, SHA-256 `acb1c163cd51e291f58dbe51ae12c04f82c2b51538aa36e446a05890e06aadd0`; all four gRPC comparison identities and reader signatures match before/after. The HTTP comparison identities and exact successful byte/message totals also match. The protocol timing source view remains the immutable `d859b79eedb87dfc372be6c07e516d173c96124b` view, with A21 SHA-256 `dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53`. Producer source commits in the JSON are explicitly producer identities, not a substitute for the timing source view.

## Inspect: repeat-call allocation removed

Each process completed 10,000 warmup calls followed by ten batches of 100,000 calls. The actual order was before/after, after/before, before/after. All returned metadata was checked by the existing probe.

| Process | Before steady allocation | After steady allocation | Before wall ns/call | After wall ns/call |
|---|---:|---:|---:|---:|
| 1 | 2,624 B/call | 0 B/call | 611.551 | 1.483 |
| 2 | 2,624 B/call | 0 B/call | 624.471 | 1.657 |
| 3 | 2,624 B/call | 0 B/call | 600.699 | 1.452 |

All three before steady phases recorded 1,255 Gen0 collections; all after steady phases recorded zero collections. The first Inspect call remains separate: before allocated 21,224 bytes and after 21,216 bytes. First-call times were mixed; there is no first-call speed claim. Allocation is measured on the calling thread; wall is the exact probe bracket. Process CPU readings are a wider observation and do not turn the reported nanoseconds into isolated method CPU cost. The measured change demonstrates the repeated default-inspection path, not the same multiplier for a full application.

## Pages: lower allocation, mixed latency

Each probe performed 20 warmup pages and 1,000 measured pages of 100 ordered rows, with a 128-row batch limit and a 65,536-byte limit. The fixture hash, query, full value validation, committed seed, fresh-session checks and actual cleanup are unchanged. Both provider probes completed all checks. Before pages are historical single processes; after pages are single processes from this queue.

| Provider | Allocated B/page before → after | Mean ms before → after | p99 ms before → after | Process CPU ms before → after |
|---|---:|---:|---:|---:|
| SQLite | 72,780.608 → 63,894.952 (−12.209%) | 6.173 → 7.052 | 25.077 → 22.767 | 1,914.149 → 2,064.641 |
| PostgreSQL | 72,775.152 → 63,894.000 (−12.204%) | 5.985 → 4.994 | 25.862 → 22.924 | 1,147.890 → 976.244 |

These are full public-query costs including DTO/list materialization and stream cleanup, not database execution time. There is no SQL-only attribution, direct-Rust comparison or database wait counter in these probes. The allocation direction agrees with the lazy move waiter. SQLite mean increased while PostgreSQL mean decreased; the formal multi-process comparison remains necessary. Quantiles are nearest-rank values from the actual 1,000 per-page durations; percentile values are not averaged across processes.

## Retirement: a remaining post-result tail

Both SQLite scalar profiles completed 1,000 public calls and 4,000 complete native-operation observations with actual retirement invariants satisfied. The before probe's original outer process-exit receipt is unavailable; the JSON keeps that field null. The complete before probe data and `SourceReleased=true` are available. After has both the complete probe result and queue exit 0.

| Observed interval | Before mean / p99 ms | After mean / p99 ms |
|---|---:|---:|
| Public scalar call | 1.196 / 20.768 | 3.209 / 20.851 |
| Start → terminal fields copied | 0.11984 / 0.40484 | 0.08369 / 0.28016 |
| Terminal fields copied → before take | 0.00998 / 0.05664 | 0.01199 / 0.07114 |
| Before take → actual retired observation | 0.15414 / 8.03645 | 0.69001 / 11.74452 |

After, every Start→Terminal interval was below 1.716 ms, while 152 of 4,000 BeforeTake→Retired intervals were at least 9 ms (before: 30). The sum of that latter interval across four operations averages about 2.760 ms per public call, compared with the 3.209 ms public-call mean. Allocation including the diagnostic observer was 17,543,728 → 17,391,120 bytes; process CPU was 615.216 → 594.303 ms; Gen0 was 8 on both sides.

This localizes the observed long segment after result notification. It does **not** prove that every long segment is a timer wait or that R2 causes a regression. BeforeTake→Retired also includes result mapping and other retirement obligations. This probe does not record native Pending counts, individual retry triggers, exact source-lease release times or a scheduler rejection count.

### Source analysis, separate from measurement

The exact candidate sources are bound by role and SHA-256 in `source_analysis_inputs`:

- [`DataSource.Complete`](https://github.com/IzuSharp/NativeWeave/blob/ada13b865ec5d19876745498f6f51d8ad2367399/src/Data.NativeHost/DataSource.cs) awaits operation retirement in `finally` before the public operation is fully complete.
- [`AsyncOperation`](https://github.com/IzuSharp/NativeWeave/blob/ada13b865ec5d19876745498f6f51d8ad2367399/src/Interop.Async/AsyncOperation.cs) adds one bounded immediate retry after a post-result Pending verdict.
- [`CallbackCoordinator`](https://github.com/IzuSharp/NativeWeave/blob/ada13b865ec5d19876745498f6f51d8ad2367399/src/Interop.Callbacks/CallbackCoordinator.cs) still supplies a 10 ms periodic retry; requesting retry only sets a retry flag.
- The [`database native operation`](https://github.com/IzuSharp/NativeWeave/blob/ada13b865ec5d19876745498f6f51d8ad2367399/native/database/host/src/operation.rs) notifies completion before dropping its worker lease. The [`native async core`](https://github.com/IzuSharp/NativeWeave/blob/ada13b865ec5d19876745498f6f51d8ad2367399/native/interop/async/src/lib.rs) must return Pending while callback/source leases remain; lease release does not send another managed terminal notification.

A second poll can therefore still precede native quiet and fall back to the timer. That is a source-supported possible path, not a measured causal attribution for these samples. No timer, poll budget or ownership rule was changed. If formal results justify further investigation, a separate diagnostic must bind actual Pending/status sequences and retry origin to the observed tail before any additional scheduling change. Such a change would also need bounded-work, scheduler-rejection, cancellation, retained-input and exactly-once retirement regressions.

## HTTP and gRPC: allocation gains with explicit resource costs

HTTP JSON and tiny profiles each completed 645 successful calls, alternating HTTP/1.1+TLS and HTTP/2+TLS, at scheduled 32 calls/s and concurrency 4. Each gRPC mode completed 323 calls at scheduled 16 calls/s and concurrency 4 through the independent common HTTP/2+TLS client. Unary uses 64-byte Data and one message; each streaming mode uses 4,096-byte Data and 32 messages. Client-stream acknowledgments have zero Data payload but nonzero encoded protobuf bytes. All protocol profiles reported valid/service-standard-met with zero content failures or unexpected errors. Recorded idle payload/queue/active/retiring gauges returned to zero.

| Profile | Sampled allocation before → after | Server CPU seconds before → after | Server RSS peak bytes before → after | p99 ms before → after |
|---|---:|---:|---:|---:|
| HTTP JSON | 674,465,840 → 18,493,272 B | 0.83 → 0.63 | 58,347,520 → 67,878,912 | 8.370 → 7.200 |
| HTTP tiny | 8,363,968 → 8,386,760 B | 0.68 → 0.63 | 67,891,200 → 67,837,952 | 5.055 → 4.671 |
| gRPC unary | 16.307 → 16.310 MiB/s | 0.75 → 0.60 | 59,748,352 → 49,934,336 | 35.475 → 26.268 |
| gRPC server stream | 512.446 → 18.818 MiB/s | 2.94 → 1.77 | 44,863,488 → 99,655,680 | 146.004 → 105.348 |
| gRPC client stream | 21.053 → 21.095 MiB/s | 1.22 → 1.15 | 70,578,176 → 70,938,624 | 180.214 → 74.004 |
| gRPC duplex | 518.345 → 24.103 MiB/s | 3.76 → 2.35 | 43,745,280 → 105,410,560 | 182.601 → 158.403 |

The JSON allocation delta decreased descriptively by 97.258%; tiny changed by +0.273%. The consumed historical HTTP summaries do not expose the exact allocation-sampling duration, so no before HTTP MiB/s is invented. The actual after HTTP allocation brackets are retained, but are not substituted for missing historical brackets.

For gRPC, the existing reader provides actual sampled durations. Server-stream allocation rate decreased 96.328%, duplex 95.350%, while unary and client-stream rates changed +0.016% and +0.197%. Client-stream allocation *bytes* fell about 4.1%, but its sampling interval shortened; its normalized rate did not improve. Server-stream Gen2 collections fell 895→36, and duplex 932→37.

The memory tradeoff is material: sampled server-stream RSS peak increased **54,792,192 bytes (52.254 MiB)** and duplex **61,665,280 bytes (58.809 MiB)**. Weak references permit collection; they do not establish a memory-neutral implementation or immediate RSS return. Zero idle owner/request gauges are preserved, but they do not prove that RSS returned to baseline.

Protocol GC/allocation observations are `GC.GetTotalAllocatedBytes(false)` deltas over a partial sampled whole-process interval. CPU and RSS use their existing process sampling brackets. No resource value is attributed to one HTTP scenario, no exact allocation-per-call is derived, and no p99 change here establishes formal timing or capacity benefit. Every consumed gRPC observation and every after protocol observation carries the existing reader's explicit rejection of profiling-only cells as timing-comparison evidence.

### Remaining encoded-limit constraint

The current [`gRPC writer`](https://github.com/IzuSharp/NativeWeave/blob/ada13b865ec5d19876745498f6f51d8ad2367399/src/Protocols.Grpc/NativeTransport.cs) retains the exact 1 MiB encoded limit and its original managed credit. A unary transport has only one outgoing write, so its per-transport weak writer has no later write to reuse; the residual approximately one MiB per call is consistent with this source path, not an exact per-call allocation measurement. Adaptive growth retaining old and new arrays under only E credit has not been proven safe. Reducing E would change the fixed contract, and a cross-request cache would add ownership/concurrency obligations. Neither was introduced. The current fixed-E candidate proceeds to formal comparison and resource acceptance.

## Projection and reproducibility boundary

The local fixed-input extractor consumed **82 existing small files, 2,021,084 bytes total**, each at most 1 MiB, plus **12 exact Git source objects, 158,134 bytes total**. It reused stored protocol-reader outputs and reported histograms; page and retirement summaries use direct subtraction, nearest-rank quantiles and elementary arithmetic on the explicitly requested small records. It did not import a driver, replay protocol JSONL, acquire the timing lock, rebuild, rerun a workload, or hash a binary/package. There was no new test framework or performance experiment.

The actual projection exited 0 at 2026-11-20 05:10:39 UTC. Private extractor SHA-256: `cb88c8cfe8fedcb17743cf4cbec57f5bc73b85832bb17db0e17c241ab1fe7322`. Its source remains local. `projection-execution.json` records actual dates, output hash, input hashes and counts; its checked-condition count is input/format validation, not a claim of newly executed product tests. The public summary SHA-256 is `d065a46ccc434213d1104ff81576a6f382766c3c59d655fe0f1431a541eda674`.

Original failures and prior evidence remain unchanged. The local invocation memo (SHA-256 `be1fd5e59e271f32cb631d871e7ca29b82103550da36597195a52b3e1fefa367`) binds historical source locations and limits; this report does not imply that the operational memo is publicly available. The full private producer/measurement records are required to replay the workload; the numerical public projection alone is not an executable runbook.
