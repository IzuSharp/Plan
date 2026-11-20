# Perf-01 Linux x64 handoff

## Current state — 2026-11-20 01:59 UTC

**All five before long groups passed. Five of ten required long groups are
accepted, totaling 9,010.718473445 seconds of credited effective load.** No product
runtime optimization has been applied and no performance improvement is claimed.
All five final after groups, equivalent-load comparisons and final acceptance
remain pending.

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
versions remain fixed. The main implementation PR currently contains measurement
and regression tooling at `d859b79eedb87dfc372be6c07e516d173c96124b`.
The accepted database observer driver is separately published at
`a3ce0f6295c535b0a81de95fc0f98aa19deb259c`. These tooling commits do not change the
before product binaries. Preserve actual package and loaded-library identities
when pairing any subsequent result.

1. Finish the two database numerical/resource projections. Retain complete raw
   records; remove an uncompressed duplicate only after verified lossless archive
   restoration and byte-for-byte comparison.
2. Before the first runtime edit, freeze three fresh independent60-second noise
   processes at each existing database comparison anchor: PostgreSQL180/s and
   SQLite50/s, concurrency16, with the adopted deferred scheduler GC and threaded
   observer. Existing capacity noise at220/s and60/s does not apply to these
   different configuration fingerprints. Formal before/after comparisons still
   require their own fresh processes.
3. Root integrates the independently source-reviewed R1–R3 candidates: successful
   default metadata reuse and resolver reference ownership; lazy stream-disposal
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
claimed. A broader operational publication was rejected by automatic review.
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
