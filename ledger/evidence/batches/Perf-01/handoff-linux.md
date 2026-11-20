# Perf-01 Linux x64 handoff

## Current state — 2026-11-20 03:21 UTC

**All five before long groups passed. Five of ten required long groups are
accepted, totaling 9,010.718473445 seconds of credited effective load.** The first
runtime candidate is now committed; no performance improvement is claimed yet.
All five final after groups, equivalent-load comparisons and final acceptance
remain pending.

R1 is published as `da95b81282b25152e82c9aa7877cd872ea9e03a0`: reuse successfully
validated default descriptor metadata and give each import resolver callback its
own OS reference. The first runtime edit began at02:57:01.121921 UTC, after the
fixed-anchor noise reports were published and read back. The complete A02 JIT,
Native AOT and package-consumer gate passed at02:59:13.306021 UTC:30 cases
and508 assertions in each mode, with actual package-consumer execution. The
[functional checklist][r1] binds its actual receipts. R2 is published as
`f914d6a3c6a57d211ca9d530472281b4af5b8246`; A07 and B06 both passed. R3 is
published as `bf0755977b16d049ee35a192f456779ce74c3767`; B15 and the fresh B18
attempt002 both passed, including compiled API and independent package
consumption. The [direct regression report][runtime] preserves exact receipts
and the initial missing-launcher failure. All runtime candidates match their
independently reviewed source. A08 also passed. The first A20 attempt completed its managed JIT/AOT and API
checks, then failed while linking the fuzzer because the matching Clang19
sanitizer/fuzzer archives were absent. The exact compiler-version test runtime
is being restored from the retained package index; no sanitizer check has been
disabled. Remaining gates, actual after builds and measurements are pending.

| Before group | Credited effective seconds | Ordinary successes | Expected cancellation/deadline probes | Arrival p99 (ms) |
| --- | ---: | ---: | ---: | ---: |
| http | 1,802.091185499 | 856,000 | 45,051 | 260.565040 |
| grpc | 1,802.101046909 | 196,880 | 10,363 | 152.456566 |
| codec | 1,802.104068505 | 346,005 | 0 | 105.719745 |
| postgresql | 1,802.212239616 | 259,526 | 0 | 207.259125 |
| sqlite | 1,802.209932916 | 72,091 | 0 | 115.857606 |

Each accepted group passed complete correctness, recovery, idle and retirement
checks. Warmup, calibration, verification and idle time are excluded from credited
load. Failed or interrupted earlier attempts remain preserved with zero credit;
partial durations were not joined. The [five-group checklist][five] contains the
actual verification hashes and the latest SQLite numerical details.

SQLite completed 72,091 operations at the frozen 40/s, concurrency16. Independent
queries found 36,182 rows per table before recovery and36,214 afterward; all32
recovery operations passed. The final idle observation lasted60.000160322s and
normal consumer/database/server cleanup passed. Sampled application CPU was544s,
30.183734% of one core, and sampled peak RSS43,560,960B. Surfaced BUSY/LOCKED and
business retries were0. Internal busy-handler retry counts remain unavailable.

The PostgreSQL wrapper initially compared the CLI duration with the driver's
existing guarded, rounded schedule span. The exact correction preserves the
original count, period, thresholds and raw files. Its54 finite checks,17 negative
cases and full original-plus-observer re-verification passed. The original failed
wrapper receipt is unchanged. See the [correction checklist][correction].

## Fixed identities and next work

The before product is main commit
`ea5fa528035d025bd7a28698ee7c71194432236c`. The locked Design is
`c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`; repository toolchain and dependency
versions remain fixed. Measurement and regression tooling was frozen at
`d859b79eedb87dfc372be6c07e516d173c96124b` before the R1 product candidate.
The accepted database observer driver is separately published at
`a3ce0f6295c535b0a81de95fc0f98aa19deb259c`. These tooling commits do not change the
before product binaries. Preserve actual package and loaded-library identities
when pairing any subsequent result.

1. Both database numerical/resource projections are complete and published at
   `6ff89dc22d2d2649a19db9e1b04be6aa618471b8`; all11 files were fetched back
   exactly and associated CI44659077895 passed. Their two reports preserve61
   resource buckets per observed role. Both raw archives were restored and all
   18 PostgreSQL/17 SQLite archived files compared byte-for-byte successfully.
   Only verified duplicate large files are selected for cold retention; original
   acceptance, extra observer metadata and actual binaries remain retained.
2. The six fresh independent60-second before noise processes at PostgreSQL180/s
   and SQLite50/s, concurrency16, completed between02:28:50.920151 and
   02:36:44.487826 UTC. All41,406 offered operations succeeded and all six driver
   exits were zero. Full-row extraction completed at02:39:07.767248 UTC, with
   both exits zero. The [numerical results][anchor] and [verified raw retention
   checklist][retention] are published at
   `2681f8c28a7f3d7e3249100236e466812c6729bf`; all six files were read back exactly
   before the first product edit. Mixed/cycle/page mean-noise bands are
   0.965361/1.202557/0.728120ms for PostgreSQL and
   4.364952/7.874522/0.853042ms for SQLite. These are mean ranges, not p99 noise,
   capacity or long-test results. They do not replace the48 formal DB comparison
   processes. The existing220/60 capacity noise and144/40 long rates remain
   separate. The portable source/contract commit900adc6 and its passed
   CI44658571298 remain unchanged.
3. Finish the final affected shared-adopter and canonical gates for the committed
   R1–R3 candidates. The reviewed changes comprise lazy stream-disposal
   waiting and one bounded post-result retirement retry; bounded initial JSON
   storage and scoped weak gRPC writer reuse. Run affected ownership/concurrency,
   package, JIT and Native AOT regressions and compare the measured layered costs.
   Retain only changes supported by equivalent-load evidence.
4. Build the final after package closure, keep the frozen application/client and
   direct Rust controls, execute interleaved comparisons and capacity sweeps,
   then run all five after long groups at the unchanged accepted rates:
   PostgreSQL144/s, SQLite40/s, HTTP500 logical operations/s, gRPC115 calls/s,
   codec192 operations/s. All retain their original mixtures and resource/SLO
   limits.
5. Publish the before/after/direct-Rust table, retained/reverted decisions,
   remaining bottlenecks and exact ten long-run intervals. Complete required
   checks and independent review, merge both PRs under repository rules, and
   verify post-merge CI and the existing normally triggered preview.

## Evidence and boundaries

- [HTTP before long numerical report][http]
- [gRPC before long numerical report][grpc]
- [Codec before long report,32 partitions and resource series][codec]
- [Database calibration:24 points and matched capacity-noise checks][database]
- [PostgreSQL accepted before long and resource series][pg-long]
- [SQLite accepted before long and resource series][sqlite-long]
- [Per-mode gRPC profiling][grpc-profile]
- [Five-before acceptance checklist and SQLite results][five]

The current source studies map public C# through native bindings to the actual
Rust engines. The [Wasmtime study](source-binding-wasmtime.md) and
[csbindgen comparison](source-binding-csbindgen.md) distinguish read source from
executed tests and record licensing; no third-party implementation is imported.
gRPC remains identity-compression only. Independent codec results are not
negotiated network-compression gains. Sampled resources are not allocation/CPU
stack traces; unobservable counters are marked unavailable.

Public synthetic numerical/checklist evidence is retained in Git while repository
history is retained. The complete raw measurement records and operational
controls remain in the measurement workspace; no remote full-raw archive is
claimed. Broader operational/source publication bundles were rejected by automatic review;
they remain local and are not claimed published.
This portable progress record omits those private control details and references
only published project sources and numerical evidence.

[NativeWeave#19][native-pr] and [Plan#23][plan-pr] remain draft. Public domain
package release and24h/72h tests remain separate deferred tasks. The user's
current performance-implementation authorization supersedes historical
research-only phase text; no repository protections or required checks are waived.

[five]: checks/before-long-five-001/public-checklist.json
[correction]: checks/database-observer-long-correction-002/public-checklist.json
[http]: checks/before-http-long-001
[grpc]: checks/before-grpc-long-002
[codec]: checks/before-codec-long-002
[database]: checks/database-observer-calibration-001/results-001
[grpc-profile]: checks/grpc-modes-before-001
[native-pr]: https://github.com/IzuSharp/NativeWeave/pull/19
[plan-pr]: https://github.com/IzuSharp/Plan/pull/23

[pg-long]: checks/before-postgresql-observer-long-002/results-001/README.md
[sqlite-long]: checks/before-sqlite-observer-long-001/results-001/README.md
[anchor]: checks/database-anchor-before-noise-001/results-001/README.md
[retention]: checks/before-database-accepted-retention-001/README.md

[r1]: checks/R1-A02-001/public-checklist.json

[runtime]: checks/runtime-functional-001/public-summary.json
