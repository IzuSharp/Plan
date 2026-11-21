# Perf-01 epoch-002 reporting map

Source-only reporting notes; no new measurement, estimator, acceptance rule, or execution. Read against canonical measurement index `a71deb1272c3b29dd1573e5dacfccc0c53db01d72807dd091b4b78e18456728b` and common driver `2e3995df8d86583ee9443348276ca8d918056bfc`. Actual before/final identities come from the admitted bindings and loaded-module records, not from directory names or the common driver's Git label.

The authoritative entrypoints are [measure.py](../../diagnostics/recovery-measure-002/measure.py), [the adapted DB reader](../../diagnostics/recovery-measure-002/readers/database_compare.py), [protocol_compare.py](../../protocol_compare.py), [codec_compare.py](../../codec_compare.py), and the common NativeWeave `tests/Perf01/verify_long.py`. The historical [B23 report](../../../../B23/finite-final-b593/report-linux.md) and [weak-cache report](../epoch-001/weak-comparison-001/README.md) inform presentation only: their samples, binaries, noise bands, role meanings, and duration credit are not this baseline/final comparison.

## Common table contract

Each final row needs domain/provider, full scenario key, offered rate, concurrency/workers, process count, before/after/direct identities, successful throughput, arrival p99, CPU and RSS scope, errors, absolute/percentage changes, Rust gap, and the original eligibility/noise conclusion. Add managed observations only where the existing caller supplies that comparator. DB supplies four roles; protocol supplies before/after/direct; codec supplies four roles with restricted managed semantics.

| Report column | Existing output and interpretation |
|---|---|
| DB throughput / p99 | `comparison.json.cohorts[role].scopes[scope].successful_per_second.mean` / `p99_ns.mean`; `scope` is `whole`, or conditional `cycle`/`page` for mixed runs. Retain `.values`, `.minimum`, `.maximum`. These are equal-weight means of process metrics. |
| Protocol throughput / p99 | `ordinary_scenarios[token].routes[role].metrics.successful_calls_per_second.mean` / `arrival_p99_ns.mean`; retain `.process_values` and ranges. These are equal-weight means of three process metrics. Preserve the complete `scenario|protocol|payload|messages` token. |
| Codec throughput / p99 | `rows[].observed[role].successes_per_second` / `.latency.arrival_ns.p99`. The original codec reader **pools each row's raw samples across three processes**, unlike DB/protocol. Per-process metrics remain in `cohorts[role].cells[].groups[key]`. |
| Error count | DB: sum process `scopes[scope].errors`, with `outcomes_total`. Protocol: route `unexpected_errors` is already summed. Codec: accepted comparison cells require all successful outcomes; rejected/incomplete cells stay in their original result/phase ledgers and must not become a synthesized zero-error comparison. |
| Change / Rust gap | Use emitted `absolute` and `percent`: `(candidate-reference)` and `100*(candidate-reference)/reference`. Rust is the denominator for `before_minus_direct` / `after_minus_direct`; DB identifies the same pairs through `baseline_role`/`candidate_role`. Zero or missing denominator means N/A. Negative latency change means lower latency; positive throughput change means higher throughput. |
| Noise conclusion | DB: `comparisons[].noise_on_process_means`; protocol: `ordinary_scenarios[token].noise`; codec: `rows[].noise.after_vs_before[call_ns|arrival_ns|operation_ns]`. Preserve `effect_ns`, `bootstrap_95_percent_interval_ns`, `noise_band_ns`, `decision`, and original eligibility/reasons. |

The unchanged A21 inference uses independent **process means**, never p99 or throughput confidence intervals. Its decisions are `improvement`, `regression`, `within_band`, or `inconclusive`; within-band/inconclusive does not establish equality. DB `c16` is the repeated inferential anchor; the caller explicitly labels its other one-process strata descriptive. Fresh before-only publication/readback evidence remains attached to the actual bands. Do not recalibrate bands from candidate data. Missing percentiles remain N/A under A21's sample-count rule; p99 needs at least 100 relevant successes.

## Database / ORM

| Field family | Read and report |
|---|---|
| Denominator / actual generation | A process rate uses `observation.measurement_window_ns.elapsed / 1e9`, exposed as `observation_seconds`. Conditional cycle/page rates use this **same whole-run window**. Retain `offered`, `dispatched`, `dispatch_attempts`, `maximum_dispatch_lag_ns`, raw outcome counts, and the configured rate/concurrency; attempts are not committed transactions. |
| Application CPU/RSS | `cohorts[role].resources.app_cpu_percent_one_core.mean`, `rss_peak_bytes.mean`; retain each process and the maximum of its sampled peaks separately. `fd_peak_count`/`socket_peak_count` and generator resources are available where observed. No CPU/RSS allocation to conditional cycle/page rows. |
| Durable business volume | Process `durable_measurement_commits` comes from `summary.persisted_before_recovery.committed_operations_by_phase.measurement` only when availability is `measured`. Preserve `durable_oracle`, independent persisted counts, and recovery oracle outcomes. This is distinct from logical read/write calls and excludes seed/warmup/recovery mutations. |
| SQLite BUSY / retries | Process `sqlite_busy`, `sqlite_locked`, `provider_errors`, `business_retry_attempts`, `classified_error_counts`. BUSY/LOCKED and explicit retries cover the **complete application lifetime**. Internal busy-handler attempts are unavailable; explicit retries of zero does not mean SQLite performed no internal waits/retries. |
| Limits | PostgreSQL service CPU/RSS, exact SQL execution/lock/pool wait times, ordinary DB FFI/copy counts, native allocator bytes and internal SQLite retry counts are N/A in these formal receipts. Do not fill them from unrelated diagnostic timings. Scheduler-GC policy is a generator configuration, not managed application GC allocation evidence. |
| Final state | Preserve `closed.databaseResourcesReleased`, `consumerResourcesReleased`, and raw `serverState`: NativeWeave `Disposed`, direct/managed `Stopped` in the adapted short reader. The long verifier accepts only actual product roles. |

DB latency covers real HTTP, authentication, typed application/ORM/DTO work, binding, SQL, and I/O. Label it end-to-end business latency, not isolated database execution.

## HTTP and gRPC

Ordinary scenario rates use `measurement_window.elapsed_ns / 1e9`, including the final observed completion. `http-cancel`, `grpc-cancel`, and `grpc-deadline` remain in `expected_probes`; successful probes are logical checks, not ordinary business calls or successful payload throughput. Capacity/whole-cell arrival p99 includes successful probes. Keep `raw_observed_totals` separate from `successful_totals`: canceled streams can expose only a prefix.

| Field family | Read and report |
|---|---|
| Calls / messages / bytes | Reader scenario `successful_calls`, `successful_logical_checks`, `successful_totals.{request_messages,response_messages,request_payload_bytes,response_payload_bytes,request_encoded_bytes,response_encoded_bytes}` and corresponding `metrics.*_per_second`. Raw result equivalents are `independent_client.business_success_per_second`, `scenarios[token].business_successful_calls`, `successful_business_totals`, and `successful_business_rates`. Counts and rates answer different questions. |
| Cardinality | For configured payload `B` and message count `M`: unary request/response messages `1/1`; server stream `1/M`; client stream `M/1`; duplex `M/M`. The client-stream aggregate response has zero application Data payload in this fixture. Encoded bytes are protobuf message bytes, excluding gRPC framing, HTTP/2 and TLS overhead. HTTP encoded-protobuf counters are zero, not wire-byte measurements. |
| Status / correctness | Per-process reader scenarios retain `client_outcomes`, `controller_outcomes`, `wire_statuses`, `correctness_failures`, `intentional_cancellations`, and `intentional_deadlines`; independent client rows retain the original outcome/failure. Trailer correctness is an existing client assertion, not a separate exported trailer-value/count metric. Preserve its pass/failure evidence; a generic integrity label alone does not prove payload corruption. |
| Concurrency | Report configured `plan.schedule.concurrency`, profile `client.http2_connections`, and `server.max_http2_streams_per_connection` separately from observed `result.independent_client.maximum_in_progress_calls`. In-progress calls and socket-descriptor counts are not exact active HTTP/2 stream counts. |
| Resources | `whole_profile_resources.metrics.server_cpu_percent_one_core.routes[role]`, `server_rss_bytes_maximum.routes[role]`, plus client/adapter/controller counterparts. `.mean` is mean process observation; `.maximum` retains the largest process peak. Scenario CPU/RSS/GC is N/A. Preserve native-gauge maxima and `after_idle_gauges` from each cell. |
| GC / allocation | `server_gc_observed_allocated_mib_per_second` derives from the first/last measurement snapshots of `GC.GetTotalAllocatedBytes(false)`; it is a partial sampled interval, not exact B/call. Keep GC deltas, heap/committed maxima, sample count and interval. Direct Rust managed GC is N/A; native allocation and total copies remain unavailable. |

Retain protocol, TLS-enabled setting, payload hashes, actual byte counts, status/trailer/deadline assertions, and drain results. The common B18 guide specifies identity-only gRPC payload compression. Independent codec gains do not establish network compression gains; HTTP/2 header compression is a different mechanism.

## Codec

Keep worker count and all **32** `action/interface/case` partitions: eight size/entropy cases × compression/decompression × array/owned. Use recorded corpus identity, seed, zlib format, level, checksum and decode/encode bounds; do not merge compress and decompress totals into one unexplained MiB/s.

| Field family | Exact interpretation |
|---|---|
| Count / denominator | Each process uses `result.measurement_observation_seconds = (max(scheduled_end_ns,last_completion_ns)-scheduled_start_ns)/1e9`. Cohort rates divide summed row counts/bytes by the **sum** of these windows. Row rates contribute to the fixed mixed workload; they are not standalone capacity. |
| Raw throughput / ratio | Row `raw_mib_per_second_wall`, `raw_mib_per_second_summed_call`, `raw_over_encoded_ratio`. The second divides by `sum(call_ns)` and is not concurrent wall throughput. Ratio is raw/encoded, not encoded/raw. Raw single-cell summary names differ: `raw_mib_per_second_summed_codec_time` and `compression_ratio_raw_over_encoded`. |
| Timing ownership | `.latency.call_ns`, `consume_ns`, `release_ns`, `operation_ns`, `arrival_ns`, `dispatch_lag_ns`, `dispatch_to_admission_ns`. Array call includes output copy and native result retirement. Owned call excludes later Read/Dispose; include consume/release/operation to explain total cost. |
| Allocation / copies | `counter_totals` / `counter_per_success` retain `managed_allocated_bytes`, `managed_allocated_bytes_including_validation`, `copied_bytes_derived`, and `ffi_calls_derived`. Derived copies cover managed/native output copy; FFI counts cover codec and result-free calls. Neither measures total hardware traffic or all runtime/native allocation. |
| CPU / RSS | `cohorts[role].mixed_resource_summary.target_cpu_percent_one_core` uses summed CPU brackets / summed observation seconds; `target_rss_sample_peak_bytes` is the maximum sampled peak. Per-cell resource records retain target/generator intervals, endpoint RSS and trend. Resources belong to the entire mixture, not individual actions or cases. |
| Comparators | Direct array/owned labels partition the same Rust Vec implementation. Managed owned is an array-path alias; .NET compression bytes/ratios can differ and trailing/concatenated-stream rejection is not equivalent. Report managed **valid-corpus isolated call** observations only; do not rank managed arrival, full ownership operation, or NativeBuffer semantics. |

Keep per-process counts/tails and roundtrip/limit-rejection proof. Unknown counters remain null/N/A. Pooled codec p99 changes and throughput changes are descriptive; A21 decisions use the three per-process means for each existing noise metric.

## Capacity and ten long rows

Capacity uses the existing `selection.json.highest_consistently_passing_rate`, `first_failing_bracket_rate`, and every `controller.json.cells[]` phase/rate/outcome. Show the actual successful throughput/p99/resources of the three final 60-second confirmations, alongside the sampled offered-rate bracket. Preserve overload errors, invalid generator/environment cells and recovery. An unbracketed result is a measured lower bound; a generator-limited failure does not bound server capacity. The current caller has before/after/direct capacity for five groups. Its `capacity.fixed_paired_long_rate` is frozen; `original_long_rate_proposal_ignored` must not be reused to retune it.

For each before/after × PostgreSQL/SQLite/HTTP/gRPC/codec row, bind the actual source/packages/loaded native hashes, owner execution receipt, cell/result hash, and `long-verification.json` hash. Report `accepted`, `failure_reasons`, `duration_credit_seconds`, `driver_arrival_p99_ns`, sampled RSS, counts and recovery/drain status. Source preparation or an interrupted receipt earns no duration credit.

| Long evidence | Reported fields |
|---|---|
| Actual duration | `duration_proof.ordinary_operation_lower_bound_ns` is **D−C**: last successful ordinary dispatch minus earliest successful ordinary completion. Keep both endpoint records, `original_dispatch_start_span_ns`, `offered`, `successful_logical_checks`, `ordinary_successes`, `expected_probe_successes`, maximum dispatch lag and over-50-ms count. The original verifier requires both D−C and dispatch span ≥1,800 s. Requested 1,802 s, wall runtime, warmup, recovery and idle are not duration credit. |
| UTC windows | DB: `summary.phases.load.start_utc` / `last_completion_utc` describe target-observed load endpoints. Protocol: `result.measurement_window.start_utc` / `end_utc`, plus first/last dispatch UTC. Codec: `result.measurement_start_utc` / `measurement_end_utc`. Label these different observation points; keep the outer command start/end separately. Do not claim these wall-clock endpoints are exact D/C timestamps. |
| DB recovery / idle / drain | `summary.phases.recovery` operations and oracle; `phases.idle.start_ns/end_ns`, UTC and before/after resources; application `closed` release booleans/state and durable oracle. |
| Protocol recovery / idle / drain | `result.recovery`; `idle_owner_and_request_gauges_receded`; execution receipt `idle_start_utc_ns/idle_end_utc_ns`; `closed.status/state`, pending requests and retained managed/native bytes; sampled idle gauges. |
| Codec recovery / idle / drain | `result.phase_counts.recovery`, `recovery_standard_met`, `drained_at_utc`, `idle_observation_seconds`, `closed_at_utc`; `events.jsonl` drained event's errors and native `live/capacity/active` counters. |

Use the existing streaming long verifier and bounded metadata reads. The short protocol reader has a 64 MiB control-file ceiling and must not be used to parse a potentially larger long result. A long acceptance receipt alone does not establish pairing or all-five-group coverage. Missing CPU/GC/connections/handles/queues/owner counters stay N/A, with their actual availability scope; sampled RSS cannot prove an unsampled peak or exact allocator retention.

## Safe evidence projection

Retain synthetic numerical operations/resource series with phase, logical case/process label, timestamps, counts, outcomes, latencies, bytes, observed resource/gauge values and availability flags; retain original source/binary/package/corpus/receipt hashes and the exact published commit/path/blob/content SHA plus actual readback timestamp. Preserve failed/invalid cells and reason categories, linking their original receipt hashes. Do not select only favorable processes or replace a failed process with a mean from the rest.

Public projections omit absolute operational paths, process identifiers, environment maps, command argument maps, credentials, connection strings, certificate/key material and signed URLs. Synthetic payload identity can be retained as case/size/seed/hash without embedding payload buffers. Keep original evidence immutable and distinguish projected counts from archived raw bytes. Record actual storage location/retention/readback when publication occurs; this map creates no archive or publication. Profiling findings remain separately labeled diagnostic evidence, with no formal timing credit.

Source identities read: protocol reader `a8cead371ceed5b2d6a865c1e6b113110005db7880af7566d5125f46429c032f`; codec reader `6f09ac17bc60544ef97c147a47cada66344f6ea068318821f204da0a6e468663`; adapted DB reader `6ccbe1d00d75c8c84fa41e2d9ab6353a49fe476c8d0a24f7b5c767ad79d57108`; long verifier `3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82`.
