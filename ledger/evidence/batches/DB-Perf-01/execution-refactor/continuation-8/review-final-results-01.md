# Independent final-results review — frozen 17da campaign

Reviewed at 2026-11-26T10:43:25.252424+00:00 by `plan_freeze_audit` on CPU 8.

**Conclusion:** the four required continuous 1,800-second final observations are supported by complete, serial, source-bound raw evidence. No blocking count, duration, ownership or selected-file identity discrepancy was found. This review accepts the final measurement evidence as recorded; it does not claim Dapper performance parity, framework-only zero allocation, exclusive hardware, or completed merge/release delivery.

## Scope and evidence identities

This is an independent read-only review of completed reports and the four raw JSON/command receipts. I recalculated their counter relationships and time boundaries in memory and hashed selected reports, receipts, pinned analyzer/auditor sources and actual Dapper generated SQL source. I did not rerun the analyzer, identity auditor, benchmark, correctness suite, build, resource JSONL scan or full 373-file binary/source sweep. Existing gates and raw evidence were not modified.

| Evidence | SHA-256 |
| --- | --- |
| `final-analysis-01.json` | `aefeda74c71bd55710a727823ab0ce916580dca7b4a4a79bfa306510f73d3de9` |
| `final-identity-audit-01.json` | `71d30a985665ae57aceda35c033abee60633f33bacb9c74433145fa09b0e5b93` |
| `final-metrics-01.json` | `543075b2d39d12ebe48cd01cd2fc9badd98f8f2c225487bb22d9f426a6c86aac` |
| Original `final-freeze-01.json` | `fc1dae9be0a76b0de38c4f94c3836e47b398e10b5ff23f3c8f82313a3cb4bc1a` |

The final identity audit reports `status=passed`, `inputsUnchanged=true`, four segments and 394 observed input identities. I compared its complete bindings with the original freeze: they are equal, and every one of the original 373 path/hash pairs appears unchanged in the final audit. The full input rehash is the completed unchanged auditor's result; this reviewer did not relabel a partial selected-file hash check as a second full rehash. Product, runner and candidate harness remain `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`, tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc`. Reused Dapper harness remains `05fdd6b507bbfa9e971caa739784cf42dfb7199c`.

## Duration, business progress and serial execution

| Observation | Actual steady seconds | Start through drain seconds | Recorded idle seconds (requested 15) | Minimum successful operations in any steady second | Raw second records |
| --- | ---: | ---: | ---: | ---: | ---: |
| sqlite-final-01/candidate-c4 | 1800.026109772 | 1800.027754542 | 15.000038471 | 320 | 1802 |
| sqlite-final-01/dapper-c4 | 1800.001906858 | 1800.002836842 | 15.002442593 | 2,337 | 1802 |
| postgresql-final-01/candidate-c8 | 1800.013908184 | 1800.014960741 | 15.003852230 | 2,633 | 1802 |
| postgresql-final-01/dapper-c8 | 1800.006016273 | 1800.008237597 | 14.999423321 | 1,030 | 1802 |

All four actual steady intervals exceed 1,800 seconds. Each second 0–1,799 has successful operations and consumed rows, and all 35 cases have successful executions. Both enclosing and offered per-second sequences are consecutive and reconcile with totals; per-case successes/failures/rows also reconcile. The extra records cover drain/padding and do not replace any required steady second. No time series was truncated.

All four commands exited 0 without timeout or observer errors. Their full command monotonic intervals are strictly sequential, independently matching all six no-overlap relationships in the original analysis, including actual idle. The supervisor completed both provider runners. The PostgreSQL owner ended cleanly with exit 0 and no shutdown/accounting-error fields.

Idle duration is reported exactly: the PostgreSQL Dapper observation is 14.999423321 seconds after a request for 15 seconds. This is an actual roughly 15-second observation, not an assertion that all idle intervals are exactly or at least 15 seconds. No forced GC was used.

## Exact counts and retained refusals

| Observation | Planned / attempted | Succeeded | Failed | Rejected | Rejected / attempted | Consumed rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| sqlite-final-01/candidate-c4 | 5,400,000 / 5,400,000 | 4,872,560 | 0 | 527,440 | 9.76741% | 119,018,074 |
| sqlite-final-01/dapper-c4 | 5,400,000 / 5,400,000 | 5,389,886 | 0 | 10,114 | 0.18730% | 131,513,488 |
| postgresql-final-01/candidate-c8 | 6,480,000 / 6,480,000 | 6,120,073 | 0 | 359,927 | 5.55443% | 149,540,544 |
| postgresql-final-01/dapper-c8 | 6,480,000 / 6,480,000 | 6,465,624 | 0 | 14,376 | 0.22185% | 157,761,545 |

For each observation, attempted = sent + rejected; sent = started = completed; completed = succeeded + failed. Retries, business failures and sticky-oracle failures are all zero; error arrays and error-class maps are empty. Rejections are real bounded-queue refusals, not successes or zero-latency completions. No new refusal-rate SLO is invented. Different accepted populations are retained under the same offered workload; rejected arrivals naturally make completed case counts differ.

## Result metrics and practical gaps

| Observation | Successful op/s through drain | Client CPU µs/success | Total managed B/success | Process-wide steady/drain GC0/1/2 | Complete-command wait4 peak RSS B | Actual idle RSS B |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| sqlite-final-01/candidate-c4 | 2,706.936 | 997.290 | 24,790.092 | 42245/12822/20 | 45,772,800 | 38,989,824 |
| sqlite-final-01/dapper-c4 | 2,994.376 | 582.990 | 7,431.767 | 19390/180/18 | 35,479,552 | 31,293,440 |
| postgresql-final-01/candidate-c8 | 3,400.012 | 840.060 | 25,490.045 | 51230/17717/19 | 52,674,560 | 43,261,952 |
| postgresql-final-01/dapper-c8 | 3,591.997 | 463.269 | 7,316.433 | 10949/6996/122 | 43,024,384 | 34,226,176 |

| Observation | Successful scheduled-to-completion p50 / p95 / p99 upper (µs) | Successful service p50 / p95 / p99 upper (µs) |
| --- | ---: | ---: |
| sqlite-final-01/candidate-c4 | 20,185.088 / 33,423.360 / 49,545.216 | 544.768 / 4,882.432 / 12,976.128 |
| sqlite-final-01/dapper-c4 | 207.872 / 3,031.040 / 8,585.216 | 110.592 / 1,597.440 / 4,325.376 |
| postgresql-final-01/candidate-c8 | 14,876.672 / 27,131.904 / 38,273.024 | 888.832 / 10,551.296 / 16,580.608 |
| postgresql-final-01/dapper-c8 | 370.688 / 3,325.952 / 8,519.680 | 342.016 / 2,752.512 / 4,587.520 |

These are observed outcomes at fixed offered rates (SQLite 3,000/s, PostgreSQL 3,600/s), not each implementation's unconstrained maximum throughput. Korda retains substantial client CPU, latency and managed-allocation differences from Dapper.AOT; a successful final gate does not erase them. The separate same-condition 120-second before/current comparison remains the correct direct refactor-improvement evidence. Its shorter duration is not silently equated with a 30-minute before run.

## Ownership and source-bound SQL

Both Korda raw `Drained` objects contain all eight required integer-zero owners: `Sources`, `Sessions`, `Operations`, `Cursors`, `Buffers`, `Owners`, `PullChannels`, `CommandCompletions`. I compared them with the final audit segment counters. Dapper records integer-zero `ApplicationConnections`; it does not instrument or claim Korda-style internal driver ownership. Activity counts such as SQL executions remain positive by design and are not owner leaks.

Within each provider pair, source-bound settings, actual selected case order and expected business results match. The original report records 35 diagnostic SQL-text differences in each pair: parameter marker differences and lifecycle description/statement differences remain visible. I read and hashed each matched Dapper static SQL contract, generated-factory contract and actual emitted generated source against its frozen receipt; the matched policy and generated-factory proof are present. I did not rerun those validators. Both contracts explicitly retain `runtimeSqlTraceVerified=false`. Therefore the justified claim is equivalent source-bound business SQL/parameter/results, not universal raw-byte identity or an observed server wire trace.

## Metric boundary qualifications

- CPU is client process cumulative CPU over actual steady-through-drain endpoints; PostgreSQL server CPU is separate. The server-owner lifetime covers fixture and both provider cohorts, so it is not assigned wholesale to one cohort. No missing per-cohort complete server CPU is invented.
- Managed bytes include business DTO/string/JSON, harness, framework and driver work. `framework_only_bytes` remains null. Raw cumulative allocation endpoints and actual offered-end allocation are preserved; RSS is not treated as native heap allocation.
- GC counts are process-wide differences over the steady/drain interval, not thread-local counters and not full process-lifetime collections including setup, warmup, disposal and idle. The raw receipt has an offered-end cumulative snapshot but lacks complete lifetime GC endpoints; no lifetime total is fabricated.
- Histogram quantiles are upper bounds. Scheduled-to-completion includes scheduling/queue delay; `start_delay` is planned-arrival-to-worker-start, not pure queue residence. Refused arrivals have no fabricated completion quantile.
- The final table uses complete-command `wait4` peak RSS. SQLite Dapper's value is 35,479,552 B; the consumer's after-steady high-water is 33,923,072 B. Both original values remain preserved and have different observation boundaries. Non-atomic sampled tree RSS is another distinct metric.
- Recorded host identity and affinity are unchanged. Cgroup visibility is unavailable and exclusive physical hardware is unproven. The comparison is a source-bound local-host observation under the recorded conditions.
- Ordinary long-run receipts do not serialize runtime FFI-call or physical protocol-reply counts. Existing separate diagnostics remain separate; SQL/protocol submission activity is not relabeled as network RTT.

## Review disposition

The observed four-cell duration, correctness, owner/drain, identity and serial requirements are satisfied without modifying a gate or rerunning a load. Retain all refusal counts, exact metrics and scope limits in the delivery report. This review finds no measurement-evidence blocker to proceeding with evidence retention and the separately required normal reviewed merge/CI/release workflow. It does not claim that every possible optimization has been exhausted.

## Selected files independently hashed during this review

The table below records actual selected read-only hashes. Resource JSONL and the full package/binary closure were not reread by this review; their verification remains attributed to the completed original analyzer and identity auditor.

| Original path | SHA-256 |
| --- | --- |
| `/tmp/DB-Exec-10-pack-sqlite-02/benchmarks/db-perf/workload/queries-v3.json` | `76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2` |
| `/workspace/scratch/166b48a091b9/recovery/campaign-supervisor-01.json` | `bc9b8561e49ec137ad7b4767b7b1dde0dafe5d763a7c85dc4445d8c8815a5c8c` |
| `/workspace/scratch/166b48a091b9/recovery/final-analysis-01.json` | `aefeda74c71bd55710a727823ab0ce916580dca7b4a4a79bfa306510f73d3de9` |
| `/workspace/scratch/166b48a091b9/recovery/final-identity-audit-01.json` | `71d30a985665ae57aceda35c033abee60633f33bacb9c74433145fa09b0e5b93` |
| `/workspace/scratch/166b48a091b9/recovery/final-index-01.json` | `7ddd819378e7dc3fee9b9c126f9829ce52716423996a18e93290a1a4031b79dc` |
| `/workspace/scratch/166b48a091b9/recovery/final-metrics-01.json` | `543075b2d39d12ebe48cd01cd2fc9badd98f8f2c225487bb22d9f426a6c86aac` |
| `/workspace/scratch/4a65d70f0fe1/consumers/dapper-matched-postgresql-01/build-receipt.json` | `69b569cf44b0f40777de99489b2a417690a93458b4ea7706b4e58e826bc23c57` |
| `/workspace/scratch/4a65d70f0fe1/consumers/dapper-matched-postgresql-01/generated-sql-contract.json` | `082158c321e7dcdf174a17a11c6684824c87f7fb86d83f3e0e74a7d8d69fd138` |
| `/workspace/scratch/4a65d70f0fe1/consumers/dapper-matched-postgresql-01/generated/Dapper.AOT.Analyzers/Dapper.CodeAnalysis.DapperInterceptorGenerator/DbPerf.Dapper.generated.cs` | `26efaa4adc2140e39acc23a39d659b57c37879dc37dfaa65065b598c142a151c` |
| `/workspace/scratch/4a65d70f0fe1/consumers/dapper-matched-postgresql-01/sql-contract.json` | `36a4be265e8c5a10f59a0873dc06ddec7a740119e1191a35ddd0497e59580508` |
| `/workspace/scratch/4a65d70f0fe1/consumers/dapper-matched-sqlite-01/build-receipt.json` | `c34b073ba24f3756aac3208891955e769855856ad95c3db331f5dd99a14e570b` |
| `/workspace/scratch/4a65d70f0fe1/consumers/dapper-matched-sqlite-01/generated-sql-contract.json` | `9bc521adb8da59e282b75dfcc95c81c37fa3f30db8b90f886008b2c01ab7dc65` |
| `/workspace/scratch/4a65d70f0fe1/consumers/dapper-matched-sqlite-01/generated/Dapper.AOT.Analyzers/Dapper.CodeAnalysis.DapperInterceptorGenerator/DbPerf.Dapper.generated.cs` | `daa2d91d5b4b27b133e60167c669cb117af3cadaf230238384b0db2eb1823cf1` |
| `/workspace/scratch/4a65d70f0fe1/consumers/dapper-matched-sqlite-01/sql-contract.json` | `36a4be265e8c5a10f59a0873dc06ddec7a740119e1191a35ddd0497e59580508` |
| `/workspace/scratch/fd78534029f7/measurements/final-freeze-01.json` | `fc1dae9be0a76b0de38c4f94c3836e47b398e10b5ff23f3c8f82313a3cb4bc1a` |
| `/workspace/scratch/fd78534029f7/measurements/postgresql-final-01/candidate-c8.command.json` | `e3ae22d8c8682a2fe56b420cffea9cfc29343e9b97c21537d39e33fffdc41b46` |
| `/workspace/scratch/fd78534029f7/measurements/postgresql-final-01/candidate-c8.json` | `e2e46a43807d6a332465d2b16b20d213bc2d9254abb03c249ab339ed7653af9a` |
| `/workspace/scratch/fd78534029f7/measurements/postgresql-final-01/dapper-c8.command.json` | `96ba8c2bf5469efab3a723d5ee05b8050b79c86a4ee8a2457c739dd59099f91b` |
| `/workspace/scratch/fd78534029f7/measurements/postgresql-final-01/dapper-c8.json` | `89bf8e963dec4b9f1d414cdfdab465a9451a89adc9aefc5a31107a62acef7d19` |
| `/workspace/scratch/fd78534029f7/measurements/postgresql-final-01/postgres-owner.json` | `36449313ecbfe22221a2f8418bd985929ae9d4a94a421aa9646c29b7445a8e16` |
| `/workspace/scratch/fd78534029f7/measurements/sqlite-final-01/candidate-c4.command.json` | `22a0cb0222fdecdc7bbf19add364bc5096ea2a9d9d72552ce3903dd53e43a1ef` |
| `/workspace/scratch/fd78534029f7/measurements/sqlite-final-01/candidate-c4.json` | `77bb05387cfa0f286b50a0e64c2e3fd537e698e13a17b01a5b6912fa36ffa40d` |
| `/workspace/scratch/fd78534029f7/measurements/sqlite-final-01/dapper-c4.command.json` | `776aa4c30bed0ca06261a5d37d683abd9f56d786cec691d714b2276b0f5e3c92` |
| `/workspace/scratch/fd78534029f7/measurements/sqlite-final-01/dapper-c4.json` | `0ca96974cd1aeb7357cfcf62b3354356fa455f1f260b749f19571c4a0b931c31` |
| `/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-3/analysis/analyze_execution.py` | `ac493c81eabd214295bfe3e7a59ae8887503f7408248993f48fba2245b199d37` |
| `/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/local-load-tools/audit_final_identity.py` | `99f458030b41cfe9f5740cd536a0f5d3314b0955a8a72de9abce10d3ab3c91e2` |
