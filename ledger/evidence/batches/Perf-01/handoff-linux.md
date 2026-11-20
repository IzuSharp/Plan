# Perf-01 Linux x64 handoff

## Latest recovery — 2026-11-20 07:43 UTC

The original measurement workspace and all five accepted before long groups
were recovered. The frozen kernel boot identity, CPU fingerprint, compiler bytes
and measurement environment match the recorded freeze. **Five of ten long groups
remain accepted; no final-after long group has run.**

Final retained product source remains
`0715ffb6376b1ae08259ad7e2cb30ff0320d83e7`, tree
`cd0a6022e0115c22f133aedf6c801d9244640523`. The complete nine-producer build
ran from 07:07:45.509242 to 07:17:02.217218 UTC with all exits zero, using actual
package version `0.1.0-perf01.after.3`. Final business comparisons, capacity and
after long tests must bind these new packages, not the historical ADA build.

[CI123](https://github.com/IzuSharp/NativeWeave/actions/runs/44690977311)
completed successfully at 07:14:28 UTC. Both complete downloaded artifacts were
hashed and their actual outcomes audited. The [canonical report](checks/ci123-canonical-001/README.md)
and [A20 report](checks/ci123-a20-001/README.md) bind the actual checkout tree to
0715, all seven jobs, 48 A20 outcomes and 96 command-log hashes, enabled
ASan/UBSan/leak checks and the normal package/fresh-SDK/Task04/Task07 gates.
These are functional results with zero measurement-duration credit.

All nine fresh affected component gates have
passed: A07, A08, A18, B06, B16, B17, B19, B15 and B18. The continuation completed
at 07:33:18 UTC. The first B17 attempt stopped before compilation
because its literal `clang-19` command was absent from PATH. The locked compiler
already existed and its SHA matched; adding its existing directory only to the
functional continuation resolved that launch issue. The failed attempt remains
preserved. Passed prefix gates were not rerun; the four-gate continuation has
fresh outputs and binds the exact failed-prefix receipt.
The [actual functional checklist](checks/final-functional-0715-001/README.md)
retains all ten attempts and the nine successful gate results.

The final source, four actual measured-consumer manifests and unchanged frozen
matrix are bound in the new comparison binding (SHA-256
`851a84a5351fa91a5098f4319ff20d2b225429229101bb911b6e71b535fd69f3`).
All six short comparison/capacity queues passed their describe-only checks.
The five after-long groups have a new actual build binding (SHA-256
`646bed58f9564c36bb66f2577855c8f4185fc1b3be32af47ef1ad59caab7ffd9`)
and a numerical build checklist (SHA-256
`e8e1de83307947317c3b95f726f03cc621b13c3321f368bb09d109e093f64b3a`).
The [final build binding](checks/after-long-build-002/README.md) records these
actual package/consumer/native identities and all five unchanged loads.
No formal after-002 measurement has started. The short collection amendments
passed all seven finite tests; the final result projector passed all eighteen
after correcting its missing allowlist entry for the existing numeric generator
resource subtree. The preceding failed finite attempt is retained. These are
offline preparation checks and grant no measurement-duration credit.

The [independent retained-source review](reviews/final-retained-source-0715ffb6.md)
records API/ownership applicability and the final gate scope. The latest eight-file
CI/source/retention publication was fetched back exactly at public Plan commit
`e0d2940861639effb0eae5a683074f72401d76cc`. Both PR descriptions now record the
retry removal, completed superseded matrix and final-source CI/build distinction.

[Verified numerical retention](checks/comparison-database-cold-retention-004/README.md)
preserved 208 completed historical ADA numeric files, 3,151,319,300 bytes, in
96,856,400 gzip bytes with full decoded/hash verification before original
replacement. Every original valid/ineligible/failed classification remains.
This storage operation grants no test or performance credit.

## Earlier checkpoint — 2026-11-20 06:59 UTC

The following historical state remains attached to its actual time and source.

**All five before long groups passed: five of ten required groups, totaling
9,010.718473445 seconds of credited effective load. No final-after long group
has run.** The first candidate's complete 48-process database comparison is
validated and preserved. Forty-three rows meet the frozen service standard;
five PostgreSQL control rows do not. No row is measurement-invalid. The
[historical candidate report][db-ada] distinguishes this completed experiment
from the final product identity.

The six-process [retirement ablation][retry-ablation] completed with all exits
zero and all correctness/ownership checks passing. Removing the extra
post-result retry reduced mean-of-process scalar latency from7.820495 to
1.232239ms and mean-of-process p99 from31.584900 to16.309367ms in this isolated
probe. All three means, p99 values and CPU readings without it were lower than
all three with it. This is profiling evidence with zero formal/long credit.
The decision is to remove the extra retry and retain the lazy stream waiter.

The exact final source is now public commit
`0715ffb6376b1ae08259ad7e2cb30ff0320d83e7`, tree
`cd0a6022e0115c22f133aedf6c801d9244640523`. All three changed files were fetched
and compared exactly at06:53:59.509302 UTC. Independent review verified the
runtime equals the measured ablation and the two A07 test files equal their
pre-retry versions; the original13 main tests and ownership/cancellation/timer/
scheduler-rejection coverage remain. The immutable ada checkout, packages and
measurements remain preserved. A fresh full candidate build and its affected
functional gates, final business comparisons, capacity sweeps and five after
long groups are pending. CI123 (run44690977311) is running on the new source;
its eventual result is not yet claimed.

The following sections retain the earlier candidate history and actual results.
They must not be relabeled as builds or acceptance of0715ffb6.

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
independently reviewed source. A08, A23 and B16 also passed. The
[A08/A20 numerical report][a08-a20] preserves the two local A20 failures:
missing matching Clang sanitizer archives, followed after restoration by a
LeakSanitizer fatal diagnostic explaining the unsupported ptrace environment.
The second fuzz process completed20,000 inputs but exited1; A20 remains
unaccepted locally and no sanitizer has been disabled.

The completed CI119 tree equals the R3 product tree, but actual workflow,
job logs and downloaded evidence confirm that it did not execute full A20.
The minimal CI-only commit `7b588c48e2898d93423ff278814370cdd7b49030`
adds the unchanged complete A20 harness and requires it in the existing Verify
aggregate. Its exact source was read back from GitHub. The complete A20 job in
CI120 passed with ASan, UBSan and leak detection enabled; the [actual artifact
audit][ci-a20] verifies all48 outcomes and96 command-log hashes. The whole CI120
workflow was subsequently superseded and cancelled by the next normal PR update,
so it is not a whole-workflow pass. The [CI121 archive audit][ci-canonical]
subsequently verified the complete successful canonical, fresh SDK, Task04 and
Task07 gates on the exact3db tree. That historical result does not cover the
later native shutdown correction. This functional sanitizer job does not alter
the frozen local performance toolchain.

B17's first two attempts executed its real native/JIT/AOT and example checks,
but failed while writing its legacy cost/result files: first a missing default
report directory, then an unsupported external artifact path. Both failed
receipts remain preserved. The third attempt passed using the verifier's supported
in-checkout artifact location. A17 also passed. A18 exposed an existing test
assumption: its unchanged original self-close assertion failed in two of three
fixed baseline processes and two of three candidate processes. The [diagnostic
report][a18-diagnostic] retains every outcome and the source-supported race.
The narrow test correction is published as
`3db42f3131c72be217e49e386ba61ece7cee27fb`; its complete JIT, Native AOT and
package gate passed at04:00:37.317440 UTC. At that checkpoint runtime
implementation was unchanged from R3; the subsequent native correction below
is retained in the later final candidate.

B19 then passed native, JIT and compiled-API checks but failed its AOT
managed-tail fixture's immediate native-completion assertion. Test-only commit
`178aee4750b198147f270675980692079e445e4d` establishes a bounded native-ready
precondition without weakening any original managed-tail assertion. Its next
full attempt still failed and exposed native fault state5 with zero retained
bytes. Both failed attempts remain preserved.

The native supervisor could select a normally completed acceptor when the stop
signal was also ready, then incorrectly report a host fault. A fixed64-cycle
actual-network diagnostic passed and is not claimed as a reproduction. A
separate real-Tokio ordered-outcome regression failed on the extracted original
unconditional-fault logic, observing state5 instead of4. Independently reviewed
correction `ada13b865ec5d19876745498f6f51d8ad2367399` accepts normal acceptor
completion only after stop, while retaining faults for unexpected completion
and failed tasks, including the final join. Existing fault state is preserved.
This is a correctness correction, with no claimed performance benefit.

The complete fresh B17 Host gate passed at04:28:01.137436 UTC, including all19
native tests, JIT and Native AOT. Fresh B19, B15 and B18 also passed, finishing at
04:31:15.875241,04:32:53.358305 and04:35:14.371373 UTC respectively. The
[shutdown regression report][shutdown] preserves both earlier failures, the
ordered RED result, the non-reproducing network diagnostic and all four fresh
gates. Independent B16 and A23 inputs did not change; their completed gates
remain applicable. At that historical checkpoint both product checkouts used ada13b8.

CI122 completed successfully at04:45:12 UTC. The [canonical artifact audit][ci122]
read all46,797,437 downloaded bytes and checked the actual source tree,
canonical11 checks, the two new native shutdown regressions, fresh-SDK, Task04
and Task07 results. The [separate full A20 audit][ci122-a20] read all9,642,395
artifact bytes, checked48 command outcomes and96 log hashes, and confirmed
ASan/UBSan/LSan plus20,000 completed fuzz inputs. Actual CI checkout
`34ed067343298abfb78947f750730f7efb29c101` has the same tree
`0d1b1ca390b582b1f2ebf004f7778c8f084a68a4` as ada13b8. The hosted artifacts
expire on2026-12-04 at04:43:36 and04:29:36 UTC respectively; their portable
numerical reports remain in Git. No sanitizer or required check was disabled.

The complete nine-step after build ran from04:36:00.904295 to04:44:30.117702
UTC; every command exited0. All those actual packages and consumers bind the historical
ada13b8 source. The measured Server native SHA-256 is
`7dd16c9f13c394f09e6c88b0f814110a0b1c002166257c02b66a0cb0a99d54b5`;
PostgreSQL, SQLite and codec native bytes remain identical to before. The
[after-build numerical checklist][after-build] records actual package,
application, native and manifest hashes, and the unchanged five long-load
configurations. It explicitly does not claim public availability of local
operational helper source. The revised publication proof passed51 finite checks.

The layered queue completed22 commands with all exits0 between04:55:54.660538
and04:59:53.951191 UTC. The [layered numerical report][layered-after] preserves
all15 processes and the actual input/result hashes. Three interleaved Inspect
processes per version show2,624 to0 B/call in the repeated path. Page allocation
fell about12.2%, but single-process latency was mixed. HTTP JSON sampled
allocation fell97.258%; gRPC server-stream/duplex allocation rates fell96.328%
and95.350%, while sampled RSS peaks increased by52.254 and58.809MiB. Unary and
client-stream allocation rates did not improve. These are profiling observations
with zero formal-comparison or long-duration credit. A remaining post-result
retirement tail and the fixed-E unary writer cost are explicitly documented.

The48-process database comparison started at05:03:25.791019 UTC and stopped
at05:18:10.259307 UTC after16 application processes exited0. All16 records are
correctness-valid. The last PostgreSQL C16 managed process completed10,801
operations but missed the unchanged500ms standard with p99=1,524.691236ms.
The launcher incorrectly required every collected comparison row to meet the
service standard and therefore exited1. The [partial numerical checkpoint][db-partial]
preserves every result and the failure; no sample is rerun, removed or relabeled.
The narrowly bound continuation started at05:54:37.826927 UTC for the
remaining32 processes and original readers, keeping the exact matrix, order,
thresholds and noise. It uses source SHA-256
`3a5bb35e45f98dd9c65c2f998414e2693919b567d4ce729df22e42ad9206b135`
and exact-prefix proof SHA-256
`6375e85f6e9709ce3922e9248cb0b6662b4e095832da75ae0b10cda36105703f`.
The [actual continuation checklist][db-continuation] preserves all preflight
exits and input hashes. Its eight finite checks passed, including all sixteen actual terminal control
schemas, followed by a successful real description. The first description had
failed before workload because the launcher read `max_rss_mib` instead of the
existing `max_app_rss_mib` field. That failure and the initial seven finite
model checks are preserved; only the read key changed, retaining256MiB.
Independent review covered the fixed-prefix continuation and reader correction.
A separate reader correction recognizes existing comparator `Stopped` versus
NativeWeave `Disposed` terminal enums; its89 finite checks passed. All other
validity/SLO/persistence/release gates remain, and the actual managed SLO miss
stays ineligible. The original reader and its eventual reports are retained.
The suffix and full projection subsequently completed as recorded above.
Other final comparison stages, capacity sweeps and all five after long groups
remain pending. No final improvement conclusion is inferred from ADA rows.

The retirement ablation is complete and its decision is recorded above. Its
six actual processes ran from06:40:12.922114 to06:40:41.183159 UTC with the
fixed A/B, B/A, A/B order,20 warmup calls,1,000 measured scalar calls and4,000
native-operation observations each. The B experiment source is
`5ac6620015f5096bc3c800b1d95f60af898a097b`; its managed packages retain the
actual reused-native producer identity. The separate independent projection
recomputed all6,000 call durations and24,000 operation intervals and passed455
audit checks. An initial projection metadata assertion failed and remains
preserved; no measured input changed. The final0715 source is a separate
reviewed integration, requiring fresh packages and affected application results.

The first comparison launcher description failed before starting any workload
because a logical profile name was resolved to a nonexistent file. That failed
preflight remains retained. The correction resolves the logical name to the
existing catalog sibling without changing frozen profile bytes, driver, matrix
or acceptance limits; all six corrected stage descriptions passed before any
formal workload started. A separately reviewed
lossless-storage helper passed11 finite boundary tests. Its actual execution
finished at04:54:40.469433 UTC with exit0:484 explicit completed before
numerical files,6,884,013,987 raw bytes, were preserved in200,931,346 verified
gzip bytes. Every file was fully decompressed and hashed before removal of its
original copy; all small controls remain in place. The local archive manifest
SHA-256 is `b5d703dc1edf5b6c6f6ebe7d59fd80f55bd176c25237907d79b16b82614b67b1`.
It preserves all original valid, invalid and interrupted classifications and
gives no measurement credit. Actual available disk afterward was11,614,433,280
bytes; database and application files were outside the storage selection.

The separate [PostgreSQL snapshot storage report][storage003] covers the actual
05:35:44.358063–05:37:01.847585 UTC operation:245 selected large files from79
stopped baseline calibration clusters,2,364,178,432 original bytes preserved
in447,308,972 verified gzip bytes, all records removed only after their recorded
full decoded readback and source rehash. Small files and all original controls
remain. The103,381-file inventory is descriptive; only245 files were selected.
These partially cold clusters require exact restoration before restarting.
The67 originally valid and12 invalid classifications are unchanged. The actual
ending free-space observation was11,477,278,720 bytes; it is not a promise about
space available to later loads. The15 finite checks and actual storage process
passed. This operation gives zero performance or long-duration credit.

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
3. Build and verify the new0715 final candidate. Prior ada functional gates and
   package closure retain their original identities. Keep metadata reuse, lazy
   stream-disposal waiting, bounded initial JSON storage and scoped weak gRPC
   writer reuse; remove the extra post-result retirement retry based on the
   six-process experiment. The native shutdown correction remains supported
   by correctness regressions. Bind every final-after result to actual new
   packages and loaded library hashes.
4. Keep the frozen application/client and direct Rust controls, execute
   interleaved comparisons and capacity sweeps,
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

[a08-a20]: checks/retained-runtime-functional-gates-001/data-001/README.md

[ci-a20]: checks/ci120-a20-001/README.md

[a18-diagnostic]: checks/a18-self-close-diagnostic-001/data-001/README.md

[ci-canonical]: checks/ci121-canonical-001/README.md

[ci122]: checks/ci122-canonical-001/README.md
[ci122-a20]: checks/ci122-a20-001/README.md
[shutdown]: checks/native-shutdown-functional-001/README.md
[after-build]: checks/after-long-build-001/public-checklist.json
[layered-after]: checks/final-layered-profiles-001/results-001/README.md

[db-partial]: checks/database-collection-checkpoint-001/public-summary.json

[db-continuation]: checks/database-continuation-002/public-checklist.json
[storage003]: checks/calibration-postgresql-cold-retention-003/README.md

[db-ada]: checks/database-ada-comparison-001/README.md
[retry-ablation]: checks/retirement-ablation-001/results-001/README.md
