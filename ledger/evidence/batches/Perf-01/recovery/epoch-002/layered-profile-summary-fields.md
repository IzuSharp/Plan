# Perf-01 recovery-002 layered profile summary fields

This is a source-only extraction specification for the 13 before and 13 after
profiles. It is not a new reader, runner, measurement, statistical procedure, or
performance acceptance result. No target module was imported, built, or run.
Only the completed before Inspect and SQLite page small JSON outputs were read;
no active PostgreSQL or formal measurement payload was read. The eventual table
must wait for the actual completed receipts, preserve failures and missing fields,
and retain zero formal timing and long-duration credit for every profile.

## Bound inputs

| Input | SHA-256 or commit |
| --- | --- |
| Original common driver | `2e3995df8d86583ee9443348276ca8d918056bfc` |
| Before product | `ea5fa528035d025bd7a28698ee7c71194432236c` |
| Selected after product | `2f40348c3db80a4fbee7a99e721b374a597b16df` |
| `recovery-profile-002/sources.json` | `6e0a16a6b4f84afc811b559dcdb1d62bfb32032c59bd3bd6aa030a0e778a4b42` |
| `recovery-profile-002/plan.json` | `45c1a8faa86fdfa17fe9c6912a2e3cb523db42d4db241a1dd6e67c9f9817c37f` |
| `recovery-measure-002/measurement-sources.json` | `6b1d1e8ec6ee80271fdbbeb1c6d13909b92ca13c7a28cbc4fd4085f98f6a4c2c` |
| Immutable before admission | `56725c0a0167e04bb021210d879b6616f85523705bc19bd04bc11e2cbb42d380` |
| `final-binding-004.json` | `8f8616f2932dd1c033309e177efa63429829f9ffa2b728a182406d943efdfa8d` |
| `final-profile-queue-004.json` | `9d2289f8557fd638c42e7f830141cfc0e3b39aae83e0f4c978c1e53276488e16` |

The current source index deliberately has no selected after commit: the explicit
final binding supplies it without changing the immutable before admission. The
queue is command data, not execution evidence. For every future row use the actual
`execution.json` role, scene, source indices, build proofs, final binding, status,
owned command exit/retirement results, and retained cell file hashes. An after row
must bind the selected final receipt; an older ccff result cannot fill that row.

## Row layout and arithmetic

Use `role`, `profile`, `process_index`, and, where present, the original scenario
key as row keys. Preserve the three Inspect processes separately. Preserve each
HTTP protocol and gRPC scenario separately while reporting shared resources in a
distinct whole-profile row. Do not pool profiles or infer statistical significance.
The accompanying JSON maps exact producer field names. Only unit conversion,
addition of explicitly measured batch counters, and division by the matching
completed-operation count are proposed; no new percentile calculation is needed.
An absent value or zero denominator remains N/A.

| Profiles | Completed operation and timing fields | Allocation / CPU / GC | Interpretation |
| --- | --- | --- | --- |
| `inspect` | Each `cell/inspect-{0,1,2}.json`: `completed_measured_calls`, `samples[].calls`, `samples[].wall_stopwatch_ticks`, `stopwatch_frequency` | `samples[].calling_thread_allocated_bytes`, `process_cpu_time_span_ticks`, and `gen0_collections` / `gen1_collections` / `gen2_collections` | Per process: sum measured batches only; wall ns/call = summed wall ticks × 1e9 / frequency / calls; allocation B/call = summed calling-thread bytes / calls; CPU seconds = summed TimeSpan ticks / 1e7. Keep `first_inspect` and `warmup` separate. CPU includes a wider observation bracket than allocation/wall. |
| `page-sqlite`, `page-postgresql` | `cell/result.json`: `CompletedPages`, `RowsPerPage`, `ElapsedTicks`, `StopwatchFrequency`, `FullPageTicks[]` | `ProcessManagedAllocatedBytes`, existing `ManagedBytesPerCompletedPage`, `ProcessCpuMilliseconds`, `GcCollections[0..2]` | Wall ns/page = `ElapsedTicks` × 1e9 / frequency / completed pages. **Both page timings include exact row validation.** CPU/allocation include the full public query, DTO/list materialization, cleanup and runtime work. Keep original per-page vector; do not invent a percentile. |
| `retirement-sqlite`, `retirement-postgresql` | `cell/result.json`: `Calls`, `PublicCallMilliseconds[]`, `NativeOperations[]`, `StopwatchFrequency` | `ManagedAllocatedBytesIncludingObserver`, `ProcessCpuMilliseconds`, `GcCollections[0..2]` | Sum public-call milliseconds / Calls is the mean of instrumented serial public calls, **not a measured outer wall window**. Allocation B/call includes the observer. Count `NativeOperations` as observed native operations, not all FFI crossings. Retain `Start`, `StartReturned`, `Terminal`, `BeforeTake`, `Retired` timestamps; any later interval display must retain these names and require observed, ordered endpoints. Pending retirement count remains unavailable. |
| `postgresql-cycle`, `postgresql-page` | `cell/summary.json`: `offered`, `dispatched`, `successful`, `observation_seconds`, `successful_per_second`, `p50_ns`, `p95_ns`, `p99_ns`, `outcomes`, `by_kind` | `resources.measurement`: `cpu_seconds`, `cpu_percent_one_core`, `cpu_span_seconds`, `rss_peak_bytes`, `fd_peak_count`, `socket_peak_count`; retain `generator_resources` separately | Existing application arrival latency and success rate, with logging/wait observers enabled. Window divided by success count is not request latency. CPU uses its own sampled endpoint span. Managed allocation/GC are unavailable from this summary. Preserve other phases for drain/idle context. |
| `http-tiny`, `http-json` | `cell/diagnostic-reader.json`: each `scenarios[key]` and its `metrics`; retain H1TLS/H2TLS separately | `resources.processes`, `managed_gc`, `managed_gc_observation`, `native_gauges_maximum`, `after_idle_gauges` | Use the existing reader's per-process scenario counts, arrival percentiles and rates. CPU/RSS/GC cover the whole profile, never one protocol or request. |
| `grpc-unary`, `grpc-server`, `grpc-client`, `grpc-duplex` | Same original protocol reader; calls, logical checks, request/response messages, payload bytes and protobuf-encoded bytes remain distinct | Same whole-profile resources | Preserve identity-only compression. Byte rates exclude gRPC envelope/framing/TLS. Expected deadline/cancellation probes are separate from successful business rates; submitted messages need not equal server-received messages after cancellation. |

### PostgreSQL observations

Keep `cell/postgres-profile-summary.json` beside the application row:

- `statement_observations[]`: original `phase`, `protocol_step`, `sql_first_line`,
  `observations`, `total_server_elapsed_ms`, `mean_server_elapsed_ms`, `p50_ms`,
  `p95_ms`, `p99_ms`. Preserve the producer's grouping; Parse/Bind/Execute are not
  additional business operations. Server elapsed time already includes waits.
- `activity_snapshots` and `backend_wait_samples[]` are sampled backend states,
  not measured wait durations. Preserve `phase`, `state`, `wait_event_type`,
  `wait_event`, and `samples` rather than multiplying by the requested interval.
- **Concurrent statement durations and wait samples cannot be subtracted from
  application wall time to estimate C#/Rust or connection-pool overhead.** Exact
  per-request lock time, pool wait and pure database CPU remain unavailable.
- Carry `wait_observer_passed`, `load_statement_logging_observed`,
  `unparsed_duration_lines`, `missing_files`, and the application's `valid`,
  `supervision`, `invalid_reasons`, `durable_oracle`, `provider_errors`, and
  `business_retry_attempts`; failed observations must remain visible.

### Protocol observations

For each `scenarios[key]`, copy original offered/dispatched/client call counts,
successful calls/checks, outcome/status maps, correctness failures, unexpected
errors, intentional cancellations/deadlines, `successful_totals`, and
`raw_observed_totals`.
Use existing `metrics.arrival_mean_ns`, `arrival_p50_ns`, `arrival_p95_ns`,
`arrival_p99_ns`, `successful_calls_per_second`, `logical_checks_per_second`, and
the six request/response message, payload and encoded-byte rates. Their common
denominator is `measurement_window.elapsed_ns`, not scenario-only time. These are
single-process percentiles; do not relabel them pooled or mean-process values.

For each whole-profile process, copy original `cpu_seconds`,
`cpu_percent_one_core`, `rss_bytes_maximum`, `threads_maximum`, `fd_count_maximum`,
and `socket_count_maximum`. GC deltas and heap/committed maxima remain whole-server
observations. `managed_gc_observation` records an approximate partial snapshot
bracket using `GC.GetTotalAllocatedBytes(false)`; retain its `seconds`,
`sample_count`, `allocated_bytes_delta` and `allocated_mib_per_second`. It cannot
yield exact allocation per call/message. Missing native allocation measurements
remain unavailable. A valid diagnostic reader intentionally retains
`eligible: false` and the issue
`Profiling-only cell cannot establish a timing comparison`.

## Identity, publication and completed schema checks

Inspect already reports product/driver commits, executable/manifest hashes and
`loaded_native_sha256`. Page reports executable/build-manifest hashes and
`LoadedNativeModules`; retirement reports the latter and is executable-bound by
the owned command and build receipt. PostgreSQL application uses `loaded_files`
plus its owned build proof. The protocol reader carries `build` with manifest,
server/client executable and actual loaded native hashes. Keep these bindings in
the local extraction. Public output should contain source commits and
filename-plus-hash provenance, not local operational path maps or TLS material.

Completed small files used to confirm the schema, without recalculating results:

| Profile / file | SHA-256 |
| --- | --- |
| before Inspect `execution.json` | `bfdd60225591425b78839eba74201c85fcd88a7f690f6750821cfe361945f277` |
| before Inspect `inspect-0.json` | `ece841c157814035ec957d6c4177994cadcea69c28c2ee78c24f3f8d4ce4169e` |
| before Inspect `inspect-1.json` | `38d6c9e20241159cc8d8dfcafecaea9fba42aac9fb448d237c9177dbbec563d2` |
| before Inspect `inspect-2.json` | `67901224d41b5191b050ec870b555f0796f490029d8dbd703a93f139aa7ee832` |
| before SQLite page `execution.json` | `76e8ad158546d0699cc7f85102036d3e1617a28766543b031ea1780a9c6424ee` |
| before SQLite page `result.json` | `09fb550a2b3f05de36c2edab35e765c49819d90d10980c60c2460f0710a35418` |

These checks establish field names and denominators only. No after value, speedup,
direct-Rust gap, significance verdict, or long-test credit is filled here.
