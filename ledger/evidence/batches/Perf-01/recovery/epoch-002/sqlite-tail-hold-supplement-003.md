# Perf-01 — SQLite managed transaction-span supplement 003

This additive analysis locates time within the two already retired, corrected SQLite diagnostic loads. It does not replace the original formal C16 failure or claim a performance improvement. Each role contributes one instrumented process, not independent repetitions. Performance, capacity and long-duration credit remain **zero**.

The [earlier complete-lifecycle analysis](sqlite-tail-diagnostic-analysis-002.md) remains unchanged. Its source, loaded native hashes, executable identities, recorder completeness and preserved startup-witness failure are carried forward in [the numeric supplement](sqlite-tail-hold-supplement-003.json). This follow-up reads exactly the same two traces once, with a 64 MiB per-file limit and a 90-second analysis deadline. No application, fixture or benchmark was executed.

## Window and interval definitions

The managed write-transaction span proxy begins at the exit of the `BeginImmediate` public phase and ends at the exit of the `Commit` public phase, for a create request that inserted an item. It starts after managed observation of Begin retirement and ends after managed observation of Commit retirement. It is **not an exact measurement of physical SQLite lock ownership**. In particular, the native commit may release a lock before the managed Commit phase exits.

Every operation interval is clipped to this same per-create span. Overlapping intervals are merged within each segment and again across all three segments. The analysis reports the remaining uncovered part and cross-segment overlap explicitly. All observed cross-segment overlaps are zero. Percentiles below describe per-create sums of clipped intervals; they are not sums of operation percentiles.

The original driver records its load window with Python `time.monotonic_ns()`. The actual interpreter reports `clock_gettime(CLOCK_MONOTONIC)`. The locked .NET 11.0.0 / SDK 11.0.100 metadata identifies `dotnet/dotnet@297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`. At that source revision, Native AOT CoreLib imports the shared Unix Stopwatch implementation: `Stopwatch.GetTimestamp` → `SystemNative_GetTimestamp` → `minipal_hires_ticks` → Linux `CLOCK_MONOTONIC`, in nanoseconds. Both traces report a Stopwatch frequency of 1,000,000,000. The original driver launches the application directly as a child process without changing the time namespace. The source chain and immutable Git blob identities are recorded in the accompanying source index.

That common clock supports time-window selection. It does not supply an external business-cycle identifier. A cycle contains create, replay and recovery HTTP calls; no specific client cycle percentile is identity-joined to a trace request here.

| Window observation | Before | After |
| --- | ---: | ---: |
| Original first-dispatch → last-completion span | 60.009771357 s | 60.153755403 s |
| Create proxies wholly within that window | 1,501 | 1,501 |
| Create proxies before the window | 136 | 136 |
| Create proxies after the window | 16 | 16 |
| Proxies crossing either boundary | 0 | 0 |
| All lifecycle creates | 1,653 | 1,653 |

Both traces remain complete: 49,982 operations, 34,508 frames, no recorder overflow, missing expected boundary, active frame/operation or retirement invariant failure. Their original load summaries report 3,001 successes, zero recorded BUSY/LOCKED/business retries and a passing independent persisted-state oracle. The original diagnostic whole-load p99 is 185.795629 ms before and 167.403169 ms after; **cycle-only p99 is 207.031034 ms before and 227.100834 ms after**. Those original observations remain distinct from the managed intervals below.

## Time inside the managed transaction proxy

Values below use the 1,501 creates selected inside each original load window. Quantiles use nearest rank. The share denominator is the sum of all selected per-create proxy durations.

| Segment | Before mean ms | After mean ms | Before p99 ms | After p99 ms | Before share | After share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Whole Begin-exit → Commit-exit proxy | 11.659984 | 10.764558 | 41.414899 | 40.059117 | 100% | 100% |
| Start entry → terminal fields copied | 1.819568 | 1.613889 | 6.031674 | 4.720785 | 15.61% | 14.99% |
| Terminal fields copied → before take | 0.217684 | 0.202445 | 1.322976 | 0.991522 | 1.87% | 1.88% |
| Before take → retirement observed | 7.606590 | 7.108656 | 35.963464 | 36.370535 | 65.24% | 66.04% |
| Uncovered remainder of the proxy | 2.016142 | 1.839569 | 5.546774 | 4.529069 | 17.29% | 17.09% |

The last observed interval includes result taking/materialization, waiting for native quiescence and retirement, and the managed continuation that observes retirement. The trace does not record each timer tick or the count and duration of each native `TryRetire(Pending)` response. It therefore cannot attribute the entire 65–66% share to the coordinator timer.

The source executes these public phases sequentially after Begin. Their exact per-create interval totals identify where a smaller experiment can be focused:

| Public phase | Operations per create | Before phase mean ms | After phase mean ms | Before take→retired mean ms | After take→retired mean ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| ClaimQuery | 4 | 5.345221 | 4.451374 | 4.449113 | 3.639551 |
| InsertItem | 1 | 1.645648 | 1.714943 | 1.240514 | 1.360489 |
| InsertOutbox | 1 | 1.700184 | 1.830507 | 1.286522 | 1.462890 |
| Commit | 1 | 1.296812 | 1.238866 | 0.630442 | 0.645726 |

ClaimQuery is the largest recorded phase inside the proxy. The two insert phases have take-to-retirement p99s of 11.74/11.90 ms before and 11.83/11.69 ms after. This is consistent with a possible contribution from the existing nominal 10 ms retirement retry, but is not causal proof. A source-limited timer experiment must still measure the application, CPU, idle cost and drain behavior.

## Waiting to enter the transaction

Within the same load window, create-request scope p99 is 107.147279 ms before and 105.591463 ms after; Begin Start→Terminal p99 is 79.352781 ms before and 79.064299 ms after. In the slowest 1% of create request scopes (16 per role), Begin pending averages 199.990847 ms before and 146.443222 ms after. Its average fraction of each request scope is 84.14% and 86.29%, respectively. The corresponding managed transaction proxy averages 16.721818 ms and 13.773464 ms.

This separates time spent before Begin completes from time the application spends progressing through an admitted transaction. It does not separate SQLite physical lock waits, SQLx scheduling, native runtime work and callback delivery within Begin pending. No singular cause of the original 567 ms formal failure is established.

The earlier full-lifecycle create p99s (541.727586/649.450113 ms) include activity outside the measured load window. They must not be presented as measured-window or client-cycle p99s. The numeric supplement retains both scopes, every observed boundary group and the original identities.

## Provenance and retained limits

The before diagnostic source is `e494c9890de5af684c4222722fd471379cb5910d`, based on `ea5fa528035d025bd7a28698ee7c71194432236c`; the after diagnostic source is `38b1abac07bcb947291941a6c504fe3fbd40dfd9`, based on `2f40348c3db80a4fbee7a99e721b374a597b16df`. Both reuse the common business/driver revision `2e3995df8d86583ee9443348276ca8d918056bfc` and their previously recorded precompiled native assets. This supplement does not use a later experimental product binary.

Trace SHA-256 values are `9d5a3152958d925d6d2feefca8aba0a3191e9fdc80b358c7941a914e5f569821` before and `0c1757cf561dd175d624b5815d254e6c86c6a650c8522b4a3cd67852421a1d5c` after. The public JSON contains filename/hash provenance and aggregate numeric observations only. A private condensed per-create table retains timestamps and ticket correlations so no additional raw pass is needed for later window questions. Original traces and failed attempts were not rewritten.
