# Recovery 03 — matched ordinary screens and targeted risks

This supersedes the earlier recovery checkpoint's unfinished-test status. Stage 1
is complete and is not repeated. The main Korda task worktree is still at unchanged
main `7ff7b57`; the four isolated candidate sources remain reviewable experiments.
**Final mixed35 campaign: 0/4.** No final alignment or release acceptance is claimed.

## Exact comparison scope

Six groups ran serially on the same local Linux x64 environment, in two reversed
orders, 2,048 measured operations and 64 warmups per process, concurrency 1 and
batch size 32. Client CPUs 0–3, PostgreSQL 4–7, observer 8. Peers suspended builds,
SQL, sampling and compression during the window. This establishes local task
exclusivity, not control over an unknown hypervisor or unrelated host workload.
Every measured operation uses the unchanged row-count/digest oracle.

The Worker-D, decimal and SQLite prepare groups use the new unchanged-main native
baseline and candidates with matching `-O3 -DNDEBUG -g`, provider presets and
`NW_BUILD_TESTS=OFF`. Independent review verifies generated C#, input sources,
packages, actual loaded native SHA, command ELF identity and CPU arithmetic.
The two relation groups instead intentionally use **the same old native ELF on
both sides**, isolating a managed-only change. Their absolute CPU numbers must not
be added to the new native groups or presented as combined-candidate performance.

The first attempted window is preserved in the workspace under
`experiments/ordinary-ab-recovery-03` and receives no comparative credit. Its Dapper
numeric1 process failed the optional **all-35-case** `--verify` preflight because
the related32 preflight is fixed to 32 parents. The runner now requests that extra
preflight for rows=32 only. Warmup and measurement still unconditionally validate
the selected operation at every row count, as confirmed by both consumer sources
and independent review. Final mixed35 retains the original rows32 `--verify`.

## Ordinary outcomes

Percentages below are candidate relative to its own group baseline, by reversed
round. They are observed ranges, not statistical confidence intervals. Histogram
latencies are bucket upper bounds. Native allocation profiles were disabled.

| Isolated change / business | CPU per success | Service p50 | Supported conclusion |
| --- | --- | --- | --- |
| Worker-D SQLite text1000 | −21.20%, −14.58% | −30.06%, −32.58% | Useful repeated gain; still 6.91× / 6.74× Dapper CPU |
| Worker-D PG text1000 | −26.29%, −27.22% | −26.99%, −30.67% | Useful repeated gain; still 7.96× / 8.35× Dapper CPU |
| Decimal PG money1000 | −35.61%, −39.02% | −48.71%, −44.98% | Large selected-path gain; no universal improvement |
| Decimal PG money1 | +17.93%, +15.45% | −0.69%, +5.93% | Concrete small-query CPU risk requiring follow-up |
| SQLite prepare text1000 | +20.03%, +2.66% | +15.92%, +12.35% | Initial endpoint regression; allocation benefit alone does not dismiss it |
| Relation SQLite related32 | −3.33%, −2.67% | about −3.9%, −3.4% | Stable managed allocation reduction, small CPU change |
| Relation PG related32 | −0.34%, −5.10% | about −2.9%, −3.7% | Stable managed allocation reduction; no precise CPU improvement claim |

All six groups pass full per-operation accounting, expected results and native
owner return checks. There are 172 measured process records. Full numeric values,
including Dapper references and all eight Worker-D businesses, are in `ordinary/`.

## Concrete risk follow-up

Four reversed rounds were run for each risk, with 256 warmups, 8,192 operations per
process, except the public PG union-all control with 16,384 operations. All pass
the same accounting/oracles and owner return checks.

| Risk | Four CPU changes | Interpretation |
| --- | --- | --- |
| Worker-D SQLite early-stop32 | −5.66%, +10.62%, +4.49%, −3.29% | No stable CPU direction; p50 slightly lower in all rounds, p99 mixed |
| Decimal PG money1 | +5.90%, +3.09%, +5.59%, +8.24% | Smaller CPU cost remains repeatable; keep explicit in combined selection |
| Decimal PG numeric32 control | −1.66%, +10.92%, −6.15%, +9.79% | Control variability; cannot erase money1's repeated direction |
| SQLite prepare text1000 | +0.34%, −2.83%, −10.65%, +0.01% | Initial sustained regression did not repeat; resource benefit is supported, CPU benefit is not stable |
| Relation PG public union-all32 | +0.75%, −9.77%, +0.92%, +14.43% | No stable CPU or p99 direction; tail uncertainty remains for final mixed tests |

The union-all p99 changes are +3.16%, −39.57%, −6.79%, +23.72%. The source keeps the
public Combine snapshot path unchanged; these observations do not prove an exact
zero effect on compiled layout, scheduling, GC or tails. Do not claim no regression
from source reasoning alone.

## Mechanisms and resource boundaries

The actual native allocator measurements already retained in `current-evidence/`
repeat the decimal money1000 saving of **47,396 public allocator calls and
1,141,735 requested B/business**; SQLite text32 and text1000 each save **112 calls
and 15,136 B/business**. Their instrumentation/build-overlap identities grant no
ordinary timing credit.

The relation diagnostic now confirms both providers: temporary Combine allocation
181,760 → 60,984 B, clones 31 → 0 and clone-copy bytes 54,932 → 0. The exact
120,776 B scoped saving explains about 99.5% of ordinary related32's roughly
121,323–121,354 B whole-process managed saving. The remaining delta is not forcibly
attributed. Other import/growth/copy counts, 53 result rows/digest, one SQL and PG's
four submissions are unchanged; owners return to zero. Public Combine is retained.

Less allocation did not mean universally lower resources: the related32 process
RSS high water rises about 0.10–0.54 MiB in these four pairs, Gen0 counts decrease
while Gen1 counts increase. These are process observations, not framework-only
metrics. No idle observation was requested in these short screens, so post-release
RSS remains unknown here. The final mixed helper includes a separate idle interval.

The corrected bit30 Worker-D image now passes the complete Native AOT native-host
suite as well as both new groups (ready scheduling: 82 assertions/provider; worker
execution: 21/provider). Command completion passes SQLite 452 and PG 456 assertions;
the final full-suite owner-retirement receipt reports zero owners. The earlier
old-mask failure remains a distinct failed identity. No test or validator was
weakened to admit the corrected build.

## Current-ELF sampling of the small decimal risk

Eight diagnostic processes reuse the exact ordinary baseline/codec ELFs, preload
the previously verified self-thread perf sampler, and retain the original raw
results. The actual consumer's `SteadyStartMonotonicNs`/`SteadyEndMonotonicNs` define
the selected window. An explicit schema adapter lets the archived analyzer check
matching ELF/.dbg identities, actual clock machine code, raw-record decoding,
thread registration and loss channels. All eight pass. One numeric-control sample
is sensitive to the start/end clock-offset envelope; the money1 windows have none.

In money1 the `RhSpinWait` leaf holds about 54–69% of selected user-mode samples.
The exact matched AOT machine code contains the `pause` loop. Native-library leaf
samples decrease 232 → 167 and 214 → 174, while spin samples are 1,535 → 1,537 and
815 → 918. These are sample counts, not exclusive per-call CPU or native total
CPU: C++ work inside libc/libcrypto is outside the native-library leaf category.
The profile contains no call chain, kernel CPU or global runqueue causality.
It therefore **does not fully explain the ordinary money1 regression**. It shows
why lower native allocations cannot by itself predict whole-client CPU.

All sampled runs are diagnostic even though the unmodified consumer's own JSON
does not detect this sampler and retains its original timing flag. The wrapper,
schema adapter and report explicitly deny ordinary timing/allocation/RSS credit.

## Resume and publication boundary

1. Finish Worker-D's independent baseline/candidate boundary markers and actual
   post/run/take counts. If justified, reserve a quiet current-path sample window;
   do not infer all RhSpinWait calls exclusively belong to one scheduler.
2. The relation agent is measuring the remaining SelectParent and final ToList
   construction scopes before proposing another change. No new strategy is selected.
3. Archive the newly matched foundation and experiment raw artifacts. The finite
   summaries and source patches are persistent; the named exact raw workspace
   paths in `inventory.json` are not yet a substitute for published binary archives.
4. Build an integrated candidate only after mechanism/selection gates, inspect the
   committed impact plan, and run the required correctness/API/real NuGet AOT gates.
5. Establish both-zero-refusal mixed cost, then pressure including historical
   SQLite 3000/s, C4 and PG 3600/s, C8, queue64. Client CPU is process scope and
   includes the existing offered-load producer; prior empty-driver controls are
   contextual bounds, never exact subtraction of framework cost.
6. Supplement the matched before long evidence, freeze, then execute the four
   serial 1800-second candidate/Dapper mixed35 cells with warmup separate. Report
   GC process scope, native/managed allocation attribution limits and PG server
   cost separately. Review/normal merges/existing CI/rule-selected publication and
   public NuGet AOT verification remain authorized and outstanding.

No benchmark, profiler, calibration or load invocation is added to CI. Go drafts
Plan #35 and Korda #39 remain untouched. Stop claims still require measured noise
or contract limits; the remaining thousand-row CPU gap is not described as parity.
