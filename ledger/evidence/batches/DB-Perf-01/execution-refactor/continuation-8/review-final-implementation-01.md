# Independent final-result scope review — four frozen 17da observations

Review date: 2026-11-26. Reviewer: `implementation_review`, separate from the product author and final campaign owner.

## Disposition

**The four final observations are suitable for reporting with the scope qualifications below. No new product-correctness or result-accounting blocker was found in this review.** All four original commands succeeded, all admitted operations completed successfully, the sticky correctness oracle remained clear, and the two Korda observations ended with all eight native owner counters zero. Explicit arrival rejection remains a material performance result and must be reported alongside zero business failures.

The independent reading supports the selected validated candidate. It does not turn the campaign into proof of global optimality, framework-only zero allocation, a complete PostgreSQL server CPU measurement or unrecorded FFI/protocol-reply totals. The detailed stopping limitations in `final-stopping-review-01.md` remain applicable after the long runs.

This review read the four original raw result JSON files, their command records through the arithmetic report, the final arithmetic/identity/metric reports, the original freeze receipt, and the actual frozen measurement source. It compared raw endpoints and integer accounting and inspected the earlier current-candidate FFI extraction. It did not run a gate, test, build, profile or benchmark, change product code, recompute hashes, or modify raw evidence. Only this intermediate Markdown review was written.

## Stable identities and campaign completion

The report inputs are:

- `/workspace/scratch/166b48a091b9/recovery/final-analysis-01.json`
- `/workspace/scratch/166b48a091b9/recovery/final-identity-audit-01.json`
- `/workspace/scratch/166b48a091b9/recovery/final-metrics-01.json`
- `/workspace/scratch/fd78534029f7/measurements/final-freeze-01.json`
- `/workspace/scratch/fd78534029f7/measurements/final-freeze-spec-01.json`

The final identity audit records `status=passed`, `inputsUnchanged=true`, `ownersAndProducerImagesVerified=true`, and 394 input entries. Comparing its stored input map with the original freeze receipt finds all 373 original entries present with the same recorded values. This is a review of the completed audit and its recorded bindings, not a second byte-hash verification by this reviewer.

The candidate and runner remain public Korda `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`, tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc`. The audit binds the ordinary candidate-02 PackageReference consumers, their package repository source, generated source, AOT executables and loaded native images. The reused Dapper consumer harness remains bound to its actual `05fdd6b507bbfa9e971caa739784cf42dfb7199c` source; it is not relabelled as newly built from 17da. Its actual emitted factories and SQL-contract receipts remain linked.

The unchanged arithmetic report identifies all four cells as `complete-raw-evidence`, with 1,800 seconds of offered arrivals, all 35 cases observed, no missing per-second business progress, reconciled raw counters, and no overlap between any pair of commands' steady/drain/recorded-idle intervals. Same recorded host is established by that report. The identity audit does not silently change its role into an arithmetic or performance-threshold gate. The arithmetic report explicitly leaves `taskAcceptance` undecided; its successful completion is evidence for the final decision, not a new performance SLO.

The four original raw paths are:

| Provider / cohort | Raw result |
| --- | --- |
| SQLite / candidate | `/workspace/scratch/fd78534029f7/measurements/sqlite-final-01/candidate-c4.json` |
| SQLite / Dapper | `/workspace/scratch/fd78534029f7/measurements/sqlite-final-01/dapper-c4.json` |
| PostgreSQL / candidate | `/workspace/scratch/fd78534029f7/measurements/postgresql-final-01/candidate-c8.json` |
| PostgreSQL / Dapper | `/workspace/scratch/fd78534029f7/measurements/postgresql-final-01/dapper-c8.json` |

No before-candidate 30-minute cell is part of this four-cell index. The earlier matched short baseline must retain its actual duration and source when used for before/after comparisons. Missing phase rows in this final-only index are not evidence that the separately archived phase campaign failed or never ran.

## Business outcomes, rejection and throughput

Direct reading of each raw `OfferedLoad` record gives the following totals. Rejection percentage uses attempted arrivals as its denominator. Error percentage among admitted/started operations is zero in all four observations.

| Provider / cohort | Attempted | Sent = started = successful = completed | Failed | Rejected | Rejected / attempted | Successful ops/s through drain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SQLite / candidate | 5,400,000 | 4,872,560 | 0 | 527,440 | 9.767407% | 2,706.936039 |
| SQLite / Dapper | 5,400,000 | 5,389,886 | 0 | 10,114 | 0.187296% | 2,994.376392 |
| PostgreSQL / candidate | 6,480,000 | 6,120,073 | 0 | 359,927 | 5.554429% | 3,400.012296 |
| PostgreSQL / Dapper | 6,480,000 | 6,465,624 | 0 | 14,376 | 0.221852% | 3,591.996895 |

For every record, `attempted = sent + rejected` and `started = succeeded + failed`. The sum of per-case started/succeeded/failed counts matches the offered totals. Top-level Errors and offered Errors are empty; retries and oracle failures are zero. A rejected arrival was not admitted as a business operation and is not included in Failed. Thus “zero business failures” is accurate, while “all offered requests succeeded” would be false.

The rate settings are 3,000 arrivals/s for SQLite and 3,600 for PostgreSQL; both use queue capacity 64, concurrency 4 or 8 respectively, and the same recorded settings within each provider pair. The offered schedule and the admission outcome must remain part of the interpretation. Dapper's near-arrival-rate completion is not a measurement of its maximum sustainable capacity. The measured throughput difference alone understates the larger service-time/queueing gap and cannot be advertised as a general capacity ratio.

The summary's throughput uses `OfferedLoad.DrainedTicks - StartedTicks`, including the source-ordered snapshot boundary after admitted work completes. The raw top-level `EffectiveSeconds` is sampled slightly earlier, immediately after the workload task completes. Both are retained; they differ by about 0.9–2.2 milliseconds here. The corresponding denominator must be named consistently rather than mixing one table's throughput with another endpoint definition.

All 35 cases are present, but rejected job indices make the executed case mixture slightly different between products. For example, SQLite candidate case shares range from about 2.7675% to 2.9602%, while SQLite Dapper is near the nominal 1/35 share. The offered mix is shared; an exactly identical admitted mix is not claimed. This is an aggregate mixed-load comparison, not a per-case equal-count microbenchmark.

## Latency populations

The offered/service/all-terminal/start-delay histograms each contain exactly the admitted completed count shown above. Rejected arrivals have no completed service latency and are excluded from those histograms. The final report should present rejection separately, not imply that successful-response p99 describes every attempted arrival.

`SuccessScheduledHistogram` measures scheduled arrival to successful completion, including producer scheduling delay and admission-queue delay. `SuccessServiceHistogram` begins when a worker starts the admitted job. `AllCompletedScheduledHistogram` includes successful and failed admitted outcomes; it equals the successful population here because there were no failures. Its name does not include rejected arrivals.

| Provider / cohort | Successful scheduled-to-complete p50 / p95 / p99, ms | Successful service p50 / p95 / p99, ms |
| --- | --- | --- |
| SQLite / candidate | 20.185088 / 33.423360 / 49.545216 | 0.544768 / 4.882432 / 12.976128 |
| SQLite / Dapper | 0.207872 / 3.031040 / 8.585216 | 0.110592 / 1.597440 / 4.325376 |
| PostgreSQL / candidate | 14.876672 / 27.131904 / 38.273024 | 0.888832 / 10.551296 / 16.580608 |
| PostgreSQL / Dapper | 0.370688 / 3.325952 / 8.519680 | 0.342016 / 2.752512 / 4.587520 |

These percentiles are the recorded histogram-bin upper bounds, not exact order statistics from individual stored latency samples. The consumer declares 128 subdivisions per base-2 exponent and less than 0.782% relative bin width. The large Korda scheduled latency should not be described as only database execution time.

Source: actual frozen `OfferedLoad.cs:103,132,174,182` and the histogram fields in the original raw results; Korda `Measurement.cs:362` and Dapper `Measurement.cs:302` describe the quantile representation.

## CPU and RSS scope

CPU uses the client's `ProcessReading` cumulative user and privileged CPU endpoints, taken before releasing the workload start and after all admitted jobs finish. It includes all client threads, native code executing in the client, the shared arrival generator, framework/driver work and harness overhead. The producer's spin/sleep scheduling work is part of this CPU. The endpoints bracket the operation interval but are not sampled atomically with the timer, allocation or native counters.

| Provider / cohort | Client user + system CPU seconds | Client CPU microseconds / success | Complete-command wait4 peak RSS, bytes | After-idle client RSS, bytes |
| --- | ---: | ---: | ---: | ---: |
| SQLite / candidate | 4,859.353638 | 997.289646 | 45,772,800 | 38,989,824 |
| SQLite / Dapper | 3,142.247549 | 582.989612 | 35,479,552 | 31,293,440 |
| PostgreSQL / candidate | 5,141.226175 | 840.059616 | 52,674,560 | 43,261,952 |
| PostgreSQL / Dapper | 2,995.324906 | 463.269269 | 43,024,384 | 34,226,176 |

These CPU values are not total client-plus-PostgreSQL-server CPU. SQLite executes in the client process, whereas PostgreSQL has a separate server. The resource report retains PID/start-tick observations, but a complete server CPU group is unavailable and no complete server total is inferred. cgroup-v2 visibility is unavailable in both endpoint observations. Same recorded host and serial commands do not turn this into a measurement of every source of host noise or a fully observed CPU quota.

The RSS table deliberately uses the complete-command `processLifetimeMaxRssBytes` supplied by the runner's wait4 accounting. This differs from the raw endpoint `Process.PeakWorkingSet64` in at least one record: SQLite Dapper records endpoint peak 33,923,072 bytes and complete-command wait4 peak 35,479,552 bytes. Both must remain in the evidence. Sampled non-atomic process-tree RSS maxima are a third scope, not interchangeable with either high-water value.

The requested idle was 15 seconds after workers and Source were disposed. Actual recorded idle intervals are 15.000038471, 15.002442593, 15.003852230 and 14.999423321 seconds in table order. The report should say “requested 15 seconds” or show the actual values; it should not assert four measured idle intervals of at least 15 seconds. No forced GC occurs in this idle observation. After-idle RSS is not a proof that all allocator pages were returned to the operating system or that no leak could appear over a longer interval.

Source: Korda `Measurement.cs:206` uses `Process.UserProcessorTime`, `PrivilegedProcessorTime`, `WorkingSet64` and `PeakWorkingSet64`; `:277,294` read the CPU endpoints and `:315` begins source/worker drain; `:325` records idle. Dapper has the corresponding ordering at `Measurement.cs:216,233,254,263`.

## Managed allocation and both GC scopes

The final managed B/op uses `GC.GetTotalAllocatedBytes(precise: true)` after minus before, divided by successful admitted business operations. It is a process-wide allocation total spanning all threads and admitted work through completion. It includes business DTO/string/JSON objects and harness/framework/driver work. It excludes the later worker/Source disposal, idle observation and serialization work. It is not the live heap size, peak heap size, native allocation total or exclusive framework allocation.

| Provider / cohort | Process allocated bytes / success | Measurement-to-workload-completion GC delta, Gen0 / Gen1 / Gen2 | Absolute process GC through actual offered end, Gen0 / Gen1 / Gen2 |
| --- | ---: | --- | --- |
| SQLite / candidate | 24,790.092441 | 42,245 / 12,822 / 20 | 42,248 / 12,823 / 20 |
| SQLite / Dapper | 7,431.766588 | 19,390 / 180 / 18 | 19,391 / 180 / 18 |
| PostgreSQL / candidate | 25,490.045165 | 51,230 / 17,717 / 19 | 51,235 / 17,717 / 19 |
| PostgreSQL / Dapper | 7,316.433420 | 10,949 / 6,996 / 122 | 10,951 / 6,997 / 122 |

The middle column is the original top-level `Gen0/Gen1/Gen2 = after-before` recorded after admitted job completion and before worker/Source disposal. It is process-wide, not a sum of thread-local measurements. The last column is the absolute `GC.CollectionCount` result read by the producer at its actual offered-end boundary. It includes setup and warmup from process start. Those boundaries are distinct; subtracting the columns does not yield a reliable per-phase GC attribution or an absolute count at process exit.

The generic inherited `gc_scope` text says cumulative endpoints were not serialized. Read narrowly, there is no serialized absolute start/after pair for the main delta. Read as a statement that no absolute process GC is available anywhere, it would be misleading: the separate offered-end cumulative fields are present and the final metric extraction retains them. The human report should use the two explicit labels above. No after-idle or process-exit absolute GC counters were recorded.

The Dapper PostgreSQL Gen2 delta of 122 is an actual observation and should not be “corrected” to match the lower allocation total or the other runs. It does not by itself identify a GC cause, generation-specific memory cost or regression.

`framework_only_bytes` remains null. The instrumented allocation overlay belongs to a separate diagnostic scope and cannot be subtracted from the mixed workload total to prove 0 B. The earlier source review identified surviving framework allocations independently of this missing exclusive numerical attribution. Lower B/op and lower total GC counts also cannot be combined into a synthetic per-component GC measure.

Source: Korda actual consumer `Measurement.cs:280,282,289,291,354`; Dapper `:219,221,228,230,294`; common frozen `OfferedLoad.cs:118` reads the actual offered-end allocation and absolute collection counts before closing the producer queue.

## Owners, SQL dispatch, FFI and protocol counts

The two Korda Drained records each have strict zero values for Sources, Sessions, Operations, Cursors, Buffers, Owners, PullChannels and CommandCompletions. Operations/cursors/buffers/pull/completion counts are also zero at the normal before/after workload endpoints while Source, Sessions and retained owners remain live by design. This is a stronger native ownership observation than Dapper supplies. Dapper records application-owned logical connections returning to zero; it does not instrument the provider's internal native/reader/command owners. Reporting “all eight native counters zero for all four runs” would be incorrect.

For the actual Korda operation interval, `After - Before` yields:

| Provider | SQL dispatches | Successful libpq send/Sync submissions | Later Drained-minus-After submissions |
| --- | ---: | ---: | ---: |
| SQLite | 8,380,640 | 0 | 0 |
| PostgreSQL | 9,903,990 | 42,366,008 | 16 |

The later 16 PostgreSQL submissions belong to disposal/retirement and should not be folded silently into the operation-only numerator. SQL dispatch counts include control SQL and count dispatch at the provider's specified increment point, not server-confirmed successful business statements. A repeated batch fetch is not another SQL dispatch. Successful libpq submissions are not message counts, mandatory reply counts, packet counts or RTT. SQLite's zero network-submission count does not imply zero database/lock/storage waits.

Ordinary final records contain no runtime FFI arrays and no protocol-reply totals. Dapper provides neither internal SQL dispatch nor FFI/reply counters in this ordinary consumer. Those fields correctly remain null/unavailable rather than zero.

The earlier `final-ffi-diagnostics-01.md/.json` extraction supplies actual 17da calls for six separate instrumented, 15-second, C1 observations, numeric 32 rows plus transaction commit/rollback. Its endpoint deltas and exact source/build receipt binding remain suitable for that scope. It gives 13 wrapped managed-to-native calls per numeric operation, including two pull request/take pairs at the exact 32-row batch boundary and only one SQL dispatch per operation. The paired-column table means each named function has the shown count; request and take are separate calls. It does not measure a 13-call single-row path or the 30-minute mixed workload, and it carries no latency/allocation comparison credit.

The current source's 60-symbol inventory is not a per-query FFI count. The separate protocol proxy's actual narrow-window reply observations and `BatchResultTests` assertions likewise cannot be multiplied into unobserved final-workload replies. The stopping review correctly leaves those metric boundaries open.

## SQL and comparison limits

Both final provider comparisons have `sameBusinessContract=true`, `settingDifferences={}` and `comparableBusinessWorkload=true`. Both also retain `rawSqlByteEqual=false`. All 35 `ActualDiagnosticSql` descriptions retain textual differences, including provider parameter spelling and transaction-description details. The identity audit links Dapper's actual generated-factory and source SQL contracts while explicitly retaining `runtimeSqlTraceVerified=false`.

It is defensible to report the matched declared SQL/ordered parameter and business contract, with documented driver syntax/control differences. It is not defensible to describe these JSON descriptions as an observed byte-identical server wire trace. Korda-specific controls are not inserted into Dapper to manufacture identical internal traffic. The raw differences and generated-source receipts remain reviewable instead of being erased by equal result assertions.

The four runs demonstrate completion of the frozen campaign with materially lower Korda performance than Dapper under these offered rates, despite zero admitted business errors and successful ownership drain. They do not establish a statistical distribution over repeated 30-minute trials. Earlier before/after and phase evidence should be reported with its actual duration, source and measurement mode, not reassigned to the final campaign.

## Final stopping language

The selected implementation is the retained candidate among evaluated alternatives, with four completed serial long observations and no new correctness/accounting defect identified here. The original rejected experiments and failures remain relevant evidence for why those alternatives were not selected.

The final report should explicitly retain the remaining Dapper gap, arrival rejections, framework-only allocation uncertainty and surviving framework allocations, incomplete server CPU scope, and missing ordinary FFI/reply counts. These are not resolved by the successful 4/4 campaign. A statement of global optimality, universal 0 B, no further measurable gain or complete per-layer cost attribution would still exceed the evidence.

This review accepts accurate publication of the selected candidate's results within those boundaries. Product review, existing CI, normal merge and expected publication checks remain the campaign owner's separate delivery steps.

## Readback of the human final-report draft

The reviewer subsequently read `/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/final-report.md` as it stood before the archive freeze. Its final business, rejection, latency, client CPU, whole-command wait4 RSS, actual idle, allocation, two GC scopes, SQL/submission and separate FFI tables match the source/raw scope reviewed here. Its stopping language correctly limits the decision to evaluated alternatives. No concrete numerical discrepancy was found in those portions.

Two terminology improvements were sent to the report owner: explicitly call the GC delta endpoint admitted-work completion before worker/Source disposal, so it cannot be confused with the later native `Drained` owner snapshot; and say plainly that `runtimeSqlTraceVerified` remains false rather than using the confusing construction “false remains true as a statement.” They are presentation clarifications, not a request to alter original analysis or evidence.

The draft's historical short/phase tables and CI/delivery statements remain attributed to their linked original validations. This final-raw review does not claim to have re-executed or independently reconstructed those other gates. No more recovery-file writes are planned after this addendum; the campaign owner may archive the completed review artifacts.
