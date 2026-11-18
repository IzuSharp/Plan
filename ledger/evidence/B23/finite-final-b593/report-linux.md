# B23 Linux x64 finite performance and memory report

## Decision and scope

The declared finite B23 measurement and report scope is complete and independently accepted. All 72 search processes, 198 calibration processes and 198 separate confirmation processes were valid. All 30 declared cases have valid calibration and confirmation cohorts. The launcher completed all four phases with exit code 0, without an automatic retry or skipped eligible confirmation. The exclusive timing window ran from 2026-11-18 14:01:25 UTC to 15:00:35 UTC. Exact values and evidence bindings are in `conclusions.json`; all raw numeric observations remain available in the accompanying datasets. [1–4]

This acceptance establishes a reproducible measurement result, including adverse performance. It does not establish the near-Rust performance goal: NativeWeave was slower than the direct-Rust route under the declared measured-noise rule in 13 of 18 comparable cases; four comparisons were inconclusive and one was within the measured band. The retained A21 label `regression` denotes route overhead relative to direct Rust. No previous-release performance comparison was performed. [1,3]

B22 supplies the accepted scoped SQLite and PostgreSQL 30-minute stages and final idle periods. The user deferred 24-hour and 72-hour runs; these remain unexecuted. Windows and other platforms are outside this run. Earlier SQLite 200/s busy failures and generator-saturation observations remain adverse evidence under `calibration-001/` and `adverse-diagnosis-6b7401/`; this selected operating-point run does not relabel them. B24 package/release acceptance is a separate subsequent gate.

## Frozen design and validity

The request SHA-256 is `d11abdbc8e01bd0180e9a9bb556db227c9599706eba56b5a89bc663f145f67ff`. The reviewed controller is commit `94060930b06d1da8978c0b71e1b8caa94abd7ec0`; 169 frozen input hashes bound the launch. The two predeclared rates per family were each evaluated once with two fresh processes per supported route/case. Selection used complete functional validity, not favorable latency. The largest fully valid candidate was frozen before final calibration. [2,5]

| Family | Declared candidates (logical operations/s) | Selected | Scope |
| --- | ---: | ---: | --- |
| Cycle | 20, 30 | 30 | Low-concurrency cycle remains capped at 20/s |
| Large create | 50, 75 | 75 | Original payload, durable settings and concurrency retained |
| Keyset / minimal / advanced DI | 50, 100 | 100 | Original schema, results and concurrency retained |
| 1 MiB stream | 2, 5 | 5 | Same stream payload, authentication and protocol |

The selected profile SHA-256 is `baae204fa8dd662b7bcd3584427b68d175712493d77798443d917b8b4125dd1b`. Ordinary adjusted profiles use a six-second scheduled span. Cold create (1 at 1/s), 8 MiB streaming (20 at 2/s), overload (80 at 20/s) and all nine diagnostic profiles, including the 2,300-event saturation case, retain their original finite definitions. These rates are sampled operating points; no maximum sustainable throughput was estimated. [2,5]

Each case has three fresh calibration processes per supported route and three independent confirmation processes, with recorded shuffled order and independent confirmation seed offset. Calibration-derived noise bands remain frozen for confirmation. A21 applies 2,000 seeded independent-process bootstrap resamples to process means. It withholds percentiles when fewer than one sample represents the requested tail: p99 requires 100 samples and p99.9 requires 1,000. Pooled request percentiles and process-mean confidence intervals answer different questions. Three processes limit statistical precision, and this is one shared-host configuration rather than a hardware population. [1–3]

Durable data/oracle checks, recorded generator-lag/in-flight/timeout bounds, request semantics and input fingerprints all passed. Direct Rust and the managed AOT/Kestrel application implement the comparable ordinary workloads; they do not implement equivalent global byte-credit overload, enabled diagnostics, DI or B22 fault/retirement/retention behavior. Those 12 product-only cases are reported without invented comparator scores. Cold startup includes different migration-ledger and runtime/pool architectures. Host power policy and unrelated infrastructure activity are not controlled. [1–3]

## All 18 ordinary route comparisons

Times are the mean of three independent process mean scheduled-arrival latencies, in milliseconds. The confidence interval and frozen band are NativeWeave minus direct Rust; positive values indicate greater latency. The full dataset also retains every managed-route comparison, request-stage histogram, percentile and invalid/unavailable marker. [1,3]

| Case | Direct Rust ms | Managed AOT ms | NativeWeave ms | Difference ms [95% CI] | Noise band ms | A21 decision |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| cold-create-small-sqlite-http1 | 28.095 | 31.978 | 38.247 | 10.152 [5.534, 14.769] | 8.708 | inconclusive |
| stream-eight-mib-sqlite-http1 | 85.142 | 68.410 | 113.368 | 28.225 [13.971, 41.746] | 16.390 | inconclusive |
| stream-one-mib-postgresql-http1 | 33.522 | 29.154 | 60.673 | 27.150 [20.734, 34.415] | 7.723 | regression |
| stream-one-mib-postgresql-http1-tls | 26.536 | 35.775 | 54.591 | 28.054 [21.744, 37.243] | 3.023 | regression |
| stream-one-mib-postgresql-http2-tls | 70.971 | 48.436 | 73.633 | 2.662 [-4.682, 10.370] | 7.690 | inconclusive |
| stream-one-mib-sqlite-http1 | 34.973 | 30.711 | 65.902 | 30.929 [28.827, 32.877] | 11.391 | regression |
| stream-one-mib-sqlite-http1-tls | 28.501 | 28.470 | 58.004 | 29.503 [21.706, 37.718] | 13.129 | regression |
| stream-one-mib-sqlite-http2-tls | 75.820 | 48.011 | 76.609 | 0.789 [-6.491, 8.359] | 14.836 | within_band |
| warm-create-large-sqlite-http1 | 6.717 | 7.941 | 58.529 | 51.812 [21.402, 103.166] | 26.614 | inconclusive |
| warm-cycle-high-postgresql-http1 | 9.995 | 12.198 | 37.448 | 27.453 [25.569, 30.048] | 2.990 | regression |
| warm-cycle-high-postgresql-http1-tls | 11.133 | 16.189 | 42.152 | 31.019 [26.068, 37.657] | 5.127 | regression |
| warm-cycle-high-postgresql-http2-tls | 11.276 | 15.305 | 43.562 | 32.286 [29.661, 35.542] | 2.855 | regression |
| warm-cycle-high-sqlite-http1 | 10.706 | 11.448 | 59.650 | 48.943 [29.529, 65.620] | 5.418 | regression |
| warm-cycle-high-sqlite-http1-tls | 11.379 | 11.852 | 57.358 | 45.978 [36.713, 55.268] | 10.222 | regression |
| warm-cycle-high-sqlite-http2-tls | 12.109 | 12.120 | 52.291 | 40.181 [36.260, 43.999] | 31.121 | regression |
| warm-cycle-low-sqlite-http1 | 10.550 | 11.919 | 41.974 | 31.424 [28.159, 35.641] | 4.999 | regression |
| warm-keyset-page-postgresql-http1 | 3.756 | 4.441 | 10.761 | 7.004 [6.701, 7.312] | 2.314 | regression |
| warm-keyset-page-sqlite-http1 | 4.752 | 3.981 | 10.556 | 5.803 [4.841, 6.569] | 2.742 | regression |

For example, SQLite high-cycle HTTP/1.1 averages 59.650 ms on NativeWeave and 10.706 ms on direct Rust; its extra 48.943 ms has a 95% interval of 29.529–65.620 ms. PostgreSQL keyset averages 10.761 ms versus 3.756 ms, with a 7.004 ms difference. SQLite 1 MiB HTTP/2 TLS is within band, but this single result cannot generalize across database, payload or protocol. The large-create and 8 MiB inconclusive cases retain their larger observed means; inconclusive does not mean equal performance. [1,3]

## CPU, working memory and startup

NativeWeave has lower mean application RSS after measurement than managed AOT in all 18 comparable cases and higher RSS than direct Rust in all 18. These are descriptive process observations, without a separate memory-confidence claim. They exclude the separate PostgreSQL process and benchmark adapter, whose resources are separately retained. RSS is not native allocator usage; private working set, peak RSS, time-series samples, thread counts, file descriptors, sockets and startup-to-ready time retain their own meanings. [1,3,6]

| Case / route | RSS after MiB | App CPU ms/offered operation | Threads after (mean) | Startup-to-ready ms |
| --- | ---: | ---: | ---: | ---: |
| stream-one-mib-sqlite-http2-tls / direct-rust | 9.310 | 12.778 | 10.000 | 15.485 |
| stream-one-mib-sqlite-http2-tls / managed-aot | 43.241 | 22.889 | 14.000 | 95.989 |
| stream-one-mib-sqlite-http2-tls / nativeweave-aot-rust | 30.001 | 45.556 | 18.000 | 51.509 |
| warm-cycle-high-sqlite-http1 / direct-rust | 8.258 | 2.407 | 7.333 | 15.246 |
| warm-cycle-high-sqlite-http1 / managed-aot | 37.586 | 2.852 | 14.000 | 56.212 |
| warm-cycle-high-sqlite-http1 / nativeweave-aot-rust | 29.035 | 16.593 | 21.667 | 51.749 |
| warm-keyset-page-postgresql-http1 / direct-rust | 8.561 | 0.333 | 5.000 | 22.309 |
| warm-keyset-page-postgresql-http1 / managed-aot | 42.776 | 0.861 | 15.333 | 56.128 |
| warm-keyset-page-postgresql-http1 / nativeweave-aot-rust | 36.319 | 3.856 | 18.333 | 70.986 |

Whole-process costs do not isolate FFI, ORM materialization, DTO conversion, copying, native allocations or pinned bytes. The accepted ordinary application has no public per-operation observer for those categories, so they remain unavailable. Ordinary-route managed allocation deltas likewise remain unavailable where no managed probe exists. Instrumented diagnostic/DI cohorts retain measured allocation and GC snapshots, with the observer present. No missing value is converted to zero. Virtual image mappings identify loaded modules, not resident code pages or allocator bytes. [1,6]

## Twelve product-only cases

Two keyset cases compare the minimal typed path with the advanced DI path. The advanced-minus-minimal process-mean difference is -0.441 ms, 95% CI [-1.982, 0.787] ms, against a 4.102 ms measured band: within band. This measured precision does not establish zero DI cost. Both paths exercise the same accepted instrumented application and retain their managed allocation, CPU, GC and resource observations. [1,3,6]

Nine diagnostic cases cover disabled Release, default Debug, explicit local Debug, sampled/full tracing, configured logging, configured Meter, exporter saturation and exporter failure. Comparisons below use disabled Release as the baseline. Saturation has a different 2,300-event workload and is intentionally not assigned a comparable latency effect. [1,3,6]

| Diagnostic mode | Difference ms [95% CI] | Measured band ms | Decision |
| --- | --- | ---: | --- |
| debug-default | -1.026 [-2.435, 0.787] | 4.563 | within_band |
| debug-local | 1.868 [-1.657, 7.672] | 3.416 | inconclusive |
| exporter-failure | 0.059 [-1.295, 1.904] | 2.688 | within_band |
| exporter-saturation | unavailable: distinct workload | unavailable | not_comparable |
| full | 0.472 [-0.782, 1.500] | 2.343 | within_band |
| log-only | 0.197 [-1.249, 1.794] | 4.242 | within_band |
| meter-only | 1.688 [0.815, 2.556] | 2.343 | inconclusive |
| sampled | 0.415 [-2.122, 2.440] | 2.343 | inconclusive |

In all three saturation confirmations, the sampled exporter queue peak is 2,048 entries and 311,296 bytes; each process records 268 diagnostic drops. Exporter-failure confirmations preserve 300, 301 and 301 failed exports and the same drop deltas. Sampled callback maximums, callback-retirement/request durations, probe boundaries and counter deltas remain in the numeric projection. Peaks include setup and can miss short excursions. Expected diagnostic HTTP 500 responses are intentional workload observations, distinct from logical validity and exporter failures. Passing the functional oracle does not erase export loss. [6]

The twelfth product-only case is bounded upload overload. The confirmation cohort records 19 successful and 221 rejected logical operations out of 240 offered. Rejection is the expected capacity response and remains explicit; neither unsupported comparator is represented as a passing overload result. All HTTP status and hashed error-code counts, including setup, are retained separately from measured logical-operation outcomes. [1,6]

## Deployment and developer cost

| Route | Runtime deployment bytes | MiB |
| --- | ---: | ---: |
| direct-rust | 9,412,936 | 8.977 |
| managed-aot | 21,729,120 | 20.723 |
| nativeweave-aot-rust | 29,294,349 | 27.937 |

The runtime totals exclude debug symbols and XML documentation. NativeWeave separately has 14,528,616 debug-symbol bytes and 11,303 XML-documentation bytes. Its runtime includes 23,260,040 native-module bytes, a 6,033,336-byte managed AOT executable and 973 metadata bytes. The full consumer ships both database provider assets. The Server module includes HTTP/TLS/Tonic/rmcp code; omitting a managed protocol facade from configuration does not remove that native code. Physical archive/file hashes and lock/toolchain identities accompany the inventory. No claim of smallest deployment follows. [1,3]

The corrected artifact inventory contains no newly executed business-edit delta. The separately accepted original B21 edit proof is reused at its original receipt identity: edits to DatabaseService.cs, Models.cs, Program.cs and Protocol.cs built and ran in JIT/AOT consumers without a consumer Rust invocation and with unchanged native bytes. Its cached MSBuild reports are 4.76 s for the baseline JIT build and 3.96 s for the edited JIT build; these are not a controlled productivity comparison or cold-machine timing. AOT elapsed time was not recorded. The original source count is 1,422 C# physical lines before the edit and 1,423 afterward, plus 62 SQL lines; comments/blanks are included and these counts are not complexity scores. [7]

The current corrected baseline JIT build separately reports 4.32 s. The direct-Rust producer has a 126 s compiler-reported development build and a 35.452217 s externally timed incremental build under differing host/cache conditions. Managed AOT and NativeWeave AOT publish durations are unavailable. Time from an empty user project to a useful call and native/framework engineering effort were not independently timed. These values must not be ranked as an apples-to-apples build-speed comparison. [1,3,7]

## Interpretation and remaining limits

The measured tradeoff is a C# application workflow with precompiled native modules and lower observed RSS than the managed comparator, alongside greater route latency in many ordinary cases, more CPU in representative cases and a larger runtime file closure. The data does not attribute the latency gap to one boundary or prove that changing a particular component would recover it. Any optimization proposal needs its own source/lifetime analysis and repeatable benefit; this finite cohort made no post-result tuning change. [1,3]

Native retirement/cancellation claims continue to rely on B22 and the package/runtime contracts, rather than process exit alone. A stopped process is not evidence that individual native resources retired correctly. Comparator maintenance, overload, diagnostics and cancellation scopes remain narrower. The finite benchmark does not replace the deferred 24/72-hour resource runs, pristine B24 consumers, a release gate, additional hardware or other operating systems.

## Reproduction, storage and recovery

`measurements/` contains both matrix phases’ raw numeric timing rows and the final displayed summaries. `all-phase-observations-compact/` adds every search/calibration/confirmation process observation, all 19,152 search timing rows, per-process histograms, explicit calibration bands, null/unavailable metadata, unsupported/not-run accounting and both diagnostic probe boundaries. Application and adapter resource samples use explicit column tables with interned metadata; reconstructing those tables preserves every projected sample. Manifests bind every emitted file by size and SHA-256. `diagnostic-observations.json` retains the separately reviewed final-phase diagnostic projection. A21 request/response wire-byte fields count JSONL IPC bytes, not HTTP/TLS transport bytes. [4,6]

Only allowlisted fixed identities, hashes and numeric observations are projected. Service bodies/headers, private configurations/keys, databases, traces and free-form logs stay local, with source hashes preserving exact identity. The initial larger v1 analysis projection is retained locally; the compact v2 projection changes storage shape only. Both the original frozen measurement controller and the reviewed diagnostic exporter are unchanged. No executed measurement was repeated to create these reports.

`continuation-semantics.md` records why a missing terminal session handle does not prove process termination, how to follow the existing atomic launch guard and sealed cohort files, and the narrow conditions for continuing only unstarted work. The successful run now needs no resume. `exec-completion.json` seals observed exit 0 while the original launch-session receipt remains intact.

### Evidence bindings

| Reference | Evidence | SHA-256 |
| --- | --- | --- |
| [1] | report.json (raw_final_report) | `e1b0c55dfa0ea80a8153f2f2abfe8c60bdb2fa79dbc1a0965729613dc3dc57ce` |
| [2] | cohorts.json (cohorts) | `d92580d30f96d70e2e9e99ebf36064629853689cf71b63a6ee0e9ff0e1a582ec` |
| [3] | b23-final-report-review.json (independent_report_review) | `82bce5bd1120ce17141800fee142329a6f870241e6874498490907ad7a8889d1` |
| [4] | b23-final-execution-readback.json (independent_execution_review) | `11d5c2010fc04cb82eb81af655a139d5d69327da6838596f0cca45ec715ef69c` |
| [5] | root-launch-request.json (frozen_request) | `d11abdbc8e01bd0180e9a9bb556db227c9599706eba56b5a89bc663f145f67ff` |
| [6] | manifest.json (all_phase_numeric_manifest) | `ebd118bc3fd09d92a0e83c6a2a2cd1275beb77ed1fbb1771c758ebb38ff9cd67` |
| [7] | accepted-edit-cost-summary.json (accepted_original_B21_edit_summary) | `b037520ac3db04cb6c0caf246c41df33f98d3409aa08115dbb81cc03962e02b4` |

Additional file hashes and full precision values are in `conclusions.json`; independent numeric-projection review verified all 468 processes, 109,950 timing rows and exact reconstruction of all 191,033 application/adapter resource samples. Its identity is recorded in conclusions.json.
