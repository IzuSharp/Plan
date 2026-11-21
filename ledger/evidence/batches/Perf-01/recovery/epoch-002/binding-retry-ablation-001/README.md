# Perf-01: completed callback retry-interval ablation

**Result: the 1 ms candidate lowered p99 in 13 of 15 paired case observations, with higher active CPU in all six profile pairs and two worse server-stream p99 observations.** Keep it as a promising scheduling experiment, with those costs explicit. It is not yet a retained final product or a formal performance acceptance. All twelve short TLS cells passed the unchanged correctness, service-standard, recovery and drain predicates.

## Actual execution and identity

The run started **2026-11-21T10:27:03.113522+00:00** and ended **2026-11-21T10:34:19.856176+00:00**. All **37 finite commands exited 0 and retired**, with zero live owned processes/owner children in their receipts. Two profiles each used three fresh process pairs in order current/candidate, candidate/current, current/candidate. Every cell offered, dispatched and successfully completed **323 calls**: **3,876** measured successful calls in total. Warmup (24 calls), recovery (32 calls) and idle (5 seconds) were separate.

Current managed code was `ea0067114346af4f13383f24df165456bcabe344`; candidate was `a5748ad4e03825e3da7706d074887952da6c2d43`. Both used native source `2f40348c3db80a4fbee7a99e721b374a597b16df` and actually loaded Server SHA-256 `8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0`. Common application/client/driver remained `2e3995df8d86583ee9443348276ca8d918056bfc`. The same existing independent client SHA-256 was `ae59038f6d83b0cdc60677f5d65f50f06298b53a168bee65f73a6599d7832f8e`. The separate reused component-test native (`83b57ab5…`) was not the supplied/loaded Server.

The exact product diff changes only the existing `CallbackCoordinator` constructor arguments in `Data.NativeHost/NativeHost.cs` and `Server.Native/NativeHost.cs` from the unchanged 10 ms default to an explicit 1 ms. Native and shared coordinator/async implementations, buffer writer, application, DTO and protobuf remain unchanged. This protocol application exercises the Server change; it provides no database result for the other argument. Both roles retain the same ea006 buffer implementation.

The actual a5748 supplied-native B18 prerequisite passed **1036 JIT assertions / 598 retirements** and **1037 AOT assertions / 595 retirements**. The candidate then used actual B24 packages and a Release Native AOT protocol application built with locked .NET 11.0.100 and x86-64-v2. The metadata truthfully records managed a5748/native 2f; this mixed-source diagnostic does not meet the unchanged formal reader's same-commit-native rule.

Workload settings stayed at 16 calls/s, 20 requested seconds, concurrency 4, four reusable HTTP/2 client connections, identical TLS inputs and identity compression. The original controller recorded 20.125 scheduled seconds per cell. Service CPUs stayed 2–3; generator CPUs 0–1. Limits stayed at 500 ms arrival p99, zero unexpected errors, 256 MiB RSS and 64 MiB managed/native payload budgets. No rate, timeout, error or resource criterion was relaxed.

[projection.json](projection.json) preserves exact per-process observations, all original result/receipt/build hashes, selected package/server/client identities and the actual source delta. The report reads only completed original metadata. No raw request/resource series, binary payloads or new statistical reader were used. Values below are rounded; JSON retains original integer nanoseconds/bytes and recorded percentages.

## Tail latency: every process pair

Each triplet is replicate **0 / 1 / 2**; percentages compare the corresponding current/candidate processes. Latency includes scheduled-arrival queue/IPC through completion. **Mean latency remains unavailable for every case/process** because the unchanged completed metadata has exact percentiles and counts but no mean or latency sum. No histogram-midpoint estimate is used. `arrival_success_histogram_maximum_ns` means only the configured 60 s histogram ceiling, not an observed maximum.

| Case | Current p99, ms (0 / 1 / 2) | Candidate p99, ms (0 / 1 / 2) | Paired p99 change (0 / 1 / 2) |
| --- | --- | --- | --- |
| Unary, 64 B | 33.031 / 41.818 / 41.573 | 18.136 / 16.517 / 13.980 | -45.09% / -60.50% / -66.37% |
| Unary, 65536 B | 32.515 / 39.467 / 36.922 | 20.407 / 19.152 / 10.205 | -37.24% / -51.47% / -72.36% |
| Client stream, 32 × 4 KiB | 161.901 / 115.815 / 139.697 | 81.760 / 57.051 / 71.933 | -49.50% / -50.74% / -48.51% |
| Duplex, 32 × 4 KiB | 289.784 / 256.792 / 271.724 | 88.267 / 52.933 / 177.234 | -69.54% / -79.39% / -34.77% |
| Server stream, 32 × 4 KiB | 267.573 / 164.731 / 178.615 | 174.548 / 192.589 / 195.698 | -34.77% / +16.91% / +9.56% |

All unary, client-stream and duplex p99 pairs improved descriptively. Server-stream p99 improved in replicate 0 but increased by **16.91%** and **9.56%** in replicates 1 and 2. Its p50/p95 were lower in all three pairs, so those better central/95th-percentile values do not erase the two adverse p99 observations. All case p99 values remained below 500 ms. No A21 noise/significance classification is claimed, and process quantiles are not pooled. Exact p50/p95/p99 and per-case rates remain in JSON.

## CPU, allocation and memory

Each resource row is **current → candidate**. CPU is the original sampled percentage of one core (100% = one core); the absolute increase and relative change are both shown. These are active-window observations, not idle CPU. Managed allocation/GC deltas cover the first to last managed measurement samples; they do not count all startup/shutdown allocation.

| Profile / replicate | CPU % of one core | Absolute CPU increase, percentage points | Relative CPU change | Allocated MiB | Allocation change |
| --- | ---: | ---: | ---: | ---: | ---: |
| unary / 0 | 3.560 → 5.487 | +1.926 | +54.10% | 188.16 → 188.19 | +0.02% |
| unary / 1 | 3.562 → 5.502 | +1.939 | +54.44% | 185.83 → 188.17 | +1.26% |
| unary / 2 | 3.453 → 5.294 | +1.841 | +53.33% | 188.12 → 188.17 | +0.03% |
| streams / 0 | 6.967 → 9.067 | +2.100 | +30.14% | 193.04 → 188.22 | -2.50% |
| streams / 1 | 6.811 → 9.115 | +2.304 | +33.83% | 192.26 → 186.36 | -3.07% |
| streams / 2 | 7.665 → 9.063 | +1.398 | +18.24% | 193.05 → 187.05 | -3.11% |

Active server CPU increased in all six pairs by approximately **1.40–2.30 percentage points of one core**. Allocation remained in the same range as ea006: this is not another buffer-allocation reduction. More frequent retry ticks still scan the fixed coordinator array, but these measurements do not isolate timer/scan CPU or exact wakeup frequency. No separately computed idle-phase CPU value is available in these original summaries.

| Profile / replicate | Active RSS maximum, MiB | Last active RSS, MiB | After-idle RSS, MiB | GC gen0/gen1/gen2 |
| --- | ---: | ---: | ---: | --- |
| unary / 0 | 71.30 → 71.43 | 36.11 → 36.29 | 36.21 → 36.38 | 30/18/16 → 28/16/14 |
| unary / 1 | 71.07 → 71.41 | 35.89 → 35.92 | 35.11 → 35.99 | 29/17/16 → 30/17/16 |
| unary / 2 | 71.12 → 71.59 | 35.89 → 36.25 | 35.52 → 35.86 | 30/17/16 → 30/17/16 |
| streams / 0 | 68.93 → 68.79 | 52.36 → 52.31 | 52.37 → 52.33 | 101/2/1 → 97/2/1 |
| streams / 1 | 68.99 → 68.73 | 52.51 → 52.16 | 52.23 → 52.17 | 100/2/1 → 96/1/1 |
| streams / 2 | 69.04 → 68.94 | 52.38 → 52.43 | 52.39 → 52.45 | 100/2/1 → 96/1/1 |

After-idle RSS was slightly higher for the candidate in all three unary pairs and mixed for streams. Its active RSS maxima were also higher in all unary pairs and lower in all streaming pairs. All values stayed within the original RSS cap. Exact managed heap/committed maxima, process CPU seconds, descriptor/socket/thread counts and sampled native gauges are retained in JSON. Sampled maxima can miss brief peaks and a sampled zero does not prove zero transient allocation.

The after-idle procfs observation is distinct from the final active sample and occurs before final disposal. All cells returned native payload/request/retiring/queue gauges to zero; every close reported `Completed` / `Disposed`, zero pending requests and zero retained managed/native bytes. All 32 recovery calls passed per cell. These checks establish finite-cell drain, not return of process RSS to its pre-load level.

## Successful work and scope

Every measured outcome was `ok`, every wire status was `GrpcOK`, and each scenario had zero correctness failures, unexpected errors, timeouts and intentional cancel/deadline probes. The unchanged independent client checked protobuf/content acknowledgements. Successful calls/messages/payload counts were identical across the six processes for each profile. Payload bytes below exclude protobuf/envelope/HTTP2/TLS overhead; encoded protobuf-byte totals are separately retained in JSON.

| Case | Successful calls per process | Request / response messages | Request / response payload bytes |
| --- | ---: | ---: | ---: |
| grpc-unary 64 B | 162 | 162 / 162 | 10,368 / 10,368 |
| grpc-unary 65536 B | 161 | 161 / 161 | 10,551,296 / 10,551,296 |
| grpc-client | 107 | 3,424 / 107 | 14,024,704 / 0 |
| grpc-duplex | 108 | 3,456 / 3,456 | 14,155,776 / 14,155,776 |
| grpc-server | 108 | 108 / 3,456 | 442,368 / 14,155,776 |

Recorded successful throughput ranged from **16.009 to 16.048 calls/s** at the fixed offered rate. This is not a capacity measurement. Actual client calls in progress are recorded separately; configured HTTP/2 stream/connection limits are not observations of transport stream occupancy. The ordinary short mixes contain no new cancel/deadline probes; B18 supplies separate functional evidence.

## Decision and limits

The consistent unary/client-stream/duplex tail improvement supports continued evaluation of the scheduling change. The higher active CPU and two adverse server-stream p99 observations remain costs to resolve or accept explicitly. A smaller scan bound, if pursued, would be a separate implementation and controlled experiment: no such change is present in these results. The inherited buffer grant/reap/growth costs are unchanged in both roles.

Keep this as diagnostic evidence until any selected revision passes the original formal comparison on actual same-commit native/full producers, followed by capacity and 30-minute acceptance. This comparison includes neither the original EA5 server nor direct Rust, and its values cannot be combined arithmetically with the earlier 2f→ea006 run to manufacture a 2f/EA5→a5748 improvement. The earlier buffer ablation and all its unfavorable observations remain intact. No database, formal A21, capacity, long-run or public-release credit is awarded here.

Original completed metadata is identified by project-relative evidence names and SHA-256 in the JSON. Names are relative to execution evidence root `epoch-002`; explicit repository prefixes identify source files. Raw files are not asserted to be committed beside this projection; durable archival/publication is mapped by the owning Perf-01 handoff. No environment maps, machine paths, PIDs, TLS credentials, binaries or raw request records are included here.
