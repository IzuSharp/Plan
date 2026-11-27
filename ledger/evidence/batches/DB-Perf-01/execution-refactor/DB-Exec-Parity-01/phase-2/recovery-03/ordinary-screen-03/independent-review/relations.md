# Relation ordinary A/B independent review · recovery 03

**Provisional retention is supported by a repeatable managed allocation reduction and the ownership/correctness gates.** The selected clone work disappears in both databases. This does not establish a fixed CPU improvement, Dapper parity, zero framework allocation, or absence of every regression. The PostgreSQL public union-all control has an unresolved p99 signal; root is running a larger independent risk-control before final selection.

## Matched inputs and experiment scope

Root executed the prebuilt ordinary external package consumers serially in its quiet window. Main is `7ff7b57b907b689defb880b8af62d83679608603`; candidate is `8acca4acbc341b09d9d76e4362b4d88964cadec2` (implementation `e8e07c9`, then test-only follow-up). Within each provider, harness source files, project and SDK inputs and native bytes match exactly. These are the original native identities, distinct from root's matched `-g` integration build. The baseline/candidate source and ELF/package/native hashes are in `ordinary/input-identity.json`.

Each case has 64 warmup operations and 2,048 measured operations per process. Round 1 runs baseline before candidate; round 2 reverses that order. The main case is related32; the public union-all32 path is a control. Mode is named prepared in the unchanged harness, but related32 explicitly rebuilds LoadRelatedAsync on every business operation and has no prepared overload. Concurrency is one, persistent session, 32-row batches, 8 tenants × 1,024 orders. CPU affinity isolates client CPUs 0–3 and PG CPUs 4–7; the sampler runs on CPU 8. The runner marks this host unqualified for final long-run credit and exposes unavailable cgroup accounting. The result is an isolated causal screen.

All 16 processes complete all 2,048 operations, with zero business/oracle errors and zero final native owners. related32 returns 53 rows and the expected digest; union-all32 returns 32 rows and its expected digest. This is closed-loop one-query-at-a-time cost measurement: no independent arrival process or external admission queue was exercised. It does not locate refusal thresholds or provide a separate external-queue latency distribution.

## Main case: related32

CPU units are microseconds of total client process CPU per successful business operation. Allocation is whole-process managed GC allocation, in bytes/success. Latencies are the unchanged histogram's upper bounds (less than 0.782% bin-width error).

| Provider | Round | Client CPU µs, baseline → candidate | CPU change | Managed B/success, baseline → candidate | p50 / p95 / p99 change |
|---|---:|---:|---:|---:|---:|
| sqlite | 1 | 3371.473 → 3259.104 | -3.33% | 686412.293 → 565088.980 | -3.93% / -3.73% / -13.96% |
| sqlite | 2 | 3383.512 → 3293.334 | -2.67% | 686439.031 → 565095.336 | -3.41% / -2.04% / +0.60% |
| postgresql | 1 | 2717.166 → 2707.887 | -0.34% | 686437.375 → 565096.473 | -2.89% / -3.57% / +0.43% |
| postgresql | 2 | 2918.050 → 2769.237 | -5.10% | 686450.527 → 565097.008 | -3.66% / -10.89% / -5.37% |

The allocation reduction is 121,323.313–121,353.520 B/success in all four related pairs, approximately 17.68%. The separate same-thread diagnostic directly proves 120,776 B from 31 removed Clone calls and 54,932 bytes of removed clone tape copy. That explains approximately 99.5% of the ordinary process allocation delta. The remaining 547.313–577.520 B is unassigned; differing instrumentation, async/runtime/harness allocation and compilation can affect the surrounding process total. It must not be declared another located hotspot.

The corresponding ordinary CPU differences are modest and vary by provider/round. SQLite is directionally lower twice; PostgreSQL ranges from near-no-change to a larger reduction. There are only two paired rounds, and unrelated control CPU varies more, so no confidence interval, guaranteed gain or “CPU aligned” claim is justified. related p99 is not uniformly improved: one SQLite and one PG round have small increases while their other rounds improve.

## Public union-all control and remaining tail risk

| Provider | Round | Client CPU µs, baseline → candidate | CPU change | Managed B/success, baseline → candidate | p50 / p95 / p99 change |
|---|---:|---:|---:|---:|---:|
| sqlite | 1 | 553.199 → 625.276 | +13.03% | 2581.969 → 2548.445 | +4.40% / -8.33% / -17.65% |
| sqlite | 2 | 637.990 → 591.707 | -7.25% | 2545.656 → 2547.898 | -7.02% / -2.11% / +18.89% |
| postgresql | 1 | 509.364 → 537.939 | +5.61% | 2545.312 → 2570.906 | -0.41% / -0.49% / +7.47% |
| postgresql | 2 | 554.742 → 554.005 | -0.13% | 2575.676 → 2577.820 | +1.67% / +5.67% / +44.37% |

This public path does not call the new private transfer helper. CPU direction changes between rounds; managed allocation differences are only tens of bytes, with no clone-size change. These controls show that short CPU/latency differences cannot automatically be credited to the product change.

PostgreSQL control p99 nevertheless increases in both current rounds (about 7.47% and 44.37%). With only 2,048 operations, roughly 20 observations define the last percentile. p50 is nearly unchanged and CPU is inconsistent; there is not enough evidence to assign the cause to the candidate or dismiss it as noise. Root accepted a targeted larger-sample PG union-all AB/BA risk-control. Until its receipt is reviewed, “no regression” remains unproven. No additional product changes are proposed from this signal.

## Resource accounting limits

The ordinary number `BytesPerSuccessfulOperation` is **process-wide managed allocation**, derived from the managed GC counter. It is not native malloc, not current live managed bytes, and not a framework-only number. It includes result objects, strings/JSON, async work and test harness work. The diagnostic number is a same-thread scoped delta without crossing await; nested scopes are not summed twice. These two scopes corroborate the selected cause but remain different measurements.

All ordinary receipts have `NativeAllocationProfile=null`: native malloc counts/bytes and their call sites were not measured in this screen. The retained JSONL resource streams separate the client and PostgreSQL process trees and preserve PID/start-time identity and sample intervals. They are sampled process-tree observations, not exact server CPU attribution for the measured business interval. Server execution cost is not claimed unchanged solely because SQL/protocol counts match. The process snapshots include RSS and high-water RSS; `Idle=null`, so post-release RSS and GC pause duration are not available here. Native owner counters returning to zero prove the checked ownership contract, not an RSS release amount. Gen0/1/2 counts remain process scope and are retained per raw receipt.

### Observed process memory/GC tradeoff on related32

| Provider | Round | Peak RSS MiB, baseline → candidate | Difference MiB | Gen0 | Gen1 | Gen2 |
|---|---:|---:|---:|---:|---:|---:|
| sqlite | 1 | 32.418 → 32.953 | +0.535 | 562 → 346 | 99 → 121 | 1 → 1 |
| sqlite | 2 | 32.281 → 32.500 | +0.219 | 573 → 348 | 97 → 121 | 1 → 1 |
| postgresql | 1 | 30.340 → 30.742 | +0.402 | 571 → 345 | 100 → 119 | 1 → 1 |
| postgresql | 2 | 30.043 → 30.145 | +0.102 | 575 → 348 | 97 → 122 | 1 → 1 |

The candidate's process high-water RSS is slightly higher in all four pairs, despite lower cumulative allocation. Gen0 counts fall while Gen1 counts rise. These values include the process lifetime/high-water behavior and process-wide collection counts; they do not establish object retention by one call site or GC pause improvement. Report this small observed peak-memory cost with the allocation benefit. Post-release RSS remains unobserved in these receipts. Keeping an original command's spare array capacity when removing a trim-to-exact-size clone is a plausible contribution, but no RSS attribution is asserted from source reasoning alone.

## Retention and next boundary

The narrow transfer is supported by unchanged public snapshot behavior, 223-assertion Query.Binding AOT and 1,162-assertion real dual-provider Relations AOT, exact clone/copy elimination and repeatable process allocation reduction. Retain provisionally for integrated validation, with CPU described only by observed values. Resolve the targeted control tail question before asserting absence of regression. The final mixed workload, saturation/refusal, exact matched-native integrated packages, affected API/packed API gates and merge/CI/public NuGet checks remain separate acceptance work.

The remaining allocation is about 565 KB/business. The diagnostic median SelectParent cost remains 331,264 B, From construction 51,712 B and ToList synchronous prefix 95,640 B. These are measured residual costs, not new optimization claims; no further path was changed in this candidate.

## Evidence

- `experiments/ordinary-ab-recovery-03-attempt-02/relations-sqlite/summary.json` — SHA-256 `ad717053663fee1eac7f56e2ff1dcf3da58f943629b91741e002446365aa564c`
- `experiments/ordinary-ab-recovery-03-attempt-02/relations-postgresql/summary.json` — SHA-256 `13d86c0ae2d98f17d30b2b4c2f68cf05fafcbf1e34cd5b7f799655b34048dafe`
- Derived detail: `review-ordinary-ab.json` — SHA-256 `0189e9d31667307667c158a43c1d06d179a5ff76d36cfafe9b3eba886753cf57`.
