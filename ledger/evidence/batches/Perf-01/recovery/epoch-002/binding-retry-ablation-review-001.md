# Perf-01 — independent retry-interval TLS report review

**Disposition: accepted as diagnostic reporting, with the separately labeled CPU observation below.** No blocking numerical or scope discrepancy was found in the `binding-retry-ablation-001` README and projection committed at `00709dc79762fa00b0577d24f5d9984e42ff1dd6`. This review grants no product selection, formal A21 comparison, capacity, long-duration or GitHub approval.

The [review checklist](binding-retry-ablation-review-001.json) pins both reviewed files, all original inputs used and the exact source explaining the additional observation. The reviewer ran no build, fixture, application or load. Bounded completed metadata was read on CPU 8. The largest original cell result was 99,806 bytes. The original `verify_long.py` selected-object reader retained only requested fields; request records, resource time series and histogram bins were not reprocessed.

## Verified reporting

Checks matched **3,224 literal values and 90 arithmetic values**, twelve original result hashes, twelve cell-plan hashes, and all **37 finite-command receipt hashes**. All commands exited zero and retired, with no live owned process or owner child. Thirty case/process observations produced the reported fifteen paired p99 comparisons. All twelve cells were valid and met their original service, recovery and drain predicates; each offered, dispatched and successfully completed 323 calls, totaling **3,876 measured successes**.

The source/package and actual loaded-module identities are consistent: current managed source is `ea006711`, candidate is `a5748ad4`, and both use the same `2f40348c` native source and Server SHA-256 `8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0`. The EA5-produced executable serves only as the independent client. It does not create an EA5 server comparison. The actual supplied-native B18 result agrees with 1,036 JIT and 1,037 AOT assertions; that separate functional evidence does not supply timing credit.

The two-source diagnostic keeps 16 calls/s, 20 requested seconds, concurrency four, service CPUs 2–3, generator CPUs 0–1, original warmup/recovery, error and resource limits. Each result records 20.125 scheduled seconds. The exact source diff versus ea006 contains only the two existing Data and Server coordinator interval arguments. The earlier buffer implementation and native/shared implementations remain unchanged in this comparison.

The numerical conclusion is preserved: **13/15 p99 pairs are lower**, while server-stream replicate 1 is **16.91% higher** and replicate 2 is **9.56% higher**. All six active server CPU pairs increase. Allocation, active/after-idle RSS and GC rows agree with original metadata. All scenario wire statuses are GrpcOK; ordinary-case correctness failures and intentional cancellation/deadline counts are zero. The report correctly separates these ordinary timing cases from B18's cancellation/deadline semantics.

No mean or latency sum is present in the selected original scenario metadata. Keeping mean latency unavailable is correct; histogram `maximum_ns` is the configured ceiling. No original EA5/direct-Rust server gap, database outcome or negotiated network-compression gain can be inferred. The reported percentages remain descriptive and preserve the two adverse tails.

## Additional observation: CPU between post-recovery and post-idle samples

The report accurately says the original summaries have no **separately computed idle CPU**. However, each original retirement record contains CPU ticks and monotonic sample times in both `recovery_resources_after` and `after_idle_resources`. These existing endpoints permit the following narrowly defined derived observation, without reopening raw series or running another workload.

In the exact common `tests/Perf01.Protocols/adapter.py`, the first sample follows recovery/client exit. The adapter then sends the idle phase notification, records the idle start, sleeps for five seconds, records the idle end and takes the second sample before sending stop. The sample interval therefore brackets idle **plus phase-notification and sampling boundary work**. It is not an original pure-idle CPU field, a steady-state idle benchmark or timer-only attribution.

The formula is `100 × (CPU tick delta / ticks per second) / (sample interval ns / 1e9)`. A value of 100% means one core. Both samples identify the same server process and `SC_CLK_TCK=100` in every cell. Actual sample intervals range from **5.002030 to 5.005800 seconds**. CPU ticks have 10 ms granularity, and procfs sampling is not atomic.

| Profile / replicate | Current derived CPU, % of one core | Candidate derived CPU, % of one core | Absolute change, percentage points |
| --- | ---: | ---: | ---: |
| unary / 0 | 2.197 | 3.998 | +1.801 |
| unary / 1 | 2.199 | 4.596 | +2.397 |
| unary / 2 | 1.399 | 4.398 | +2.999 |
| streams / 0 | 1.799 | 4.198 | +2.399 |
| streams / 1 | 2.199 | 4.398 | +2.199 |
| streams / 2 | 1.998 | 4.597 | +2.599 |

The original tick endpoints, interval durations, source hash and derived values are preserved in the review JSON. Every pair is higher with the candidate in this approximately five-second bracket. This supports retaining the full-array retry scan's CPU cost as an unresolved tradeoff; it does not prove that the timer caused all observed CPU or justify transferring the values to a later scan-bound candidate. No noise test or new acceptance criterion is introduced.

## Publication and limits

The original report can be published together with this review and its additive endpoint observation. Its means-unavailable statement and original result bytes should remain unchanged. Final product retention still requires the actual selected-source application/HTTP/database checks, equivalent formal before/after measurements, capacity and all ten matching 30-minute segments. Original failed samples remain in place.

Public review data uses filename/hash provenance and aggregate numeric endpoints only. Local operational paths, process identifiers, TLS material and raw events are excluded. The original evidence remains identified by `epoch-002` relative names; this review does not assert new binary or raw-archive retention/readback.
