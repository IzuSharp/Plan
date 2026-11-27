# Continuation06 — mixed35 cost and the remaining completion hypothesis

**Twelve zero-refusal cells are complete: 180,000 successful businesses, 4,392,804 consumed rows, zero errors, refusals and retries. Final 30-minute acceptance remains 0/4.** The integrated05 candidate improves process CPU and managed bytes in both providers and both reversed rounds, while PostgreSQL scheduled p99 and released RSS regress. These are short-screen observations, not parity or final adoption.

## Current source and durable evidence

- Product PR40: `2ea67ce1902f330679c3ebff4d6d5733be20f69c`, tree `4e3989f2ce9e0c554585aab5a8bbb656e689b18d`. Actual integrated05 consumers were built from local `867c869a7e51949122b3dd13e4c7c6df2a914ec7` with the same tree; preserve that actual build identity.
- Design PR21: `9092013a549f5c1f2b9078a574797d364b259728`. All three latest task branches are `task/DB-Exec-Parity-01-linux`; main inputs and the Go drafts remain unchanged.
- Product existing CI run45955784723 and both Design checks succeeded. Plan run45961676096 succeeded after the existing job timeout alone changed from10 to30minutes; its full historical gates were retained. No benchmark, profile, calibration or load task is in CI. See [verified CI receipt](ci-verified-heads-05.json).
- Archive01 is reachable at Plan `b54054bd1f3befe94e1817cc29f494bd782854b9`; archive02 at `27e0f35709036b0737ed101ba6472ce1461c0538`. Root read back all189 and103 payload paths/modes/blob SHAs respectively. [Archive02 receipt](archives-02-publication.json) includes its exact subtree.
- The [local recovery note](archive-local-recovery-05.md) supersedes historical statements that compressed parts remain local: verified duplicate parts/canonical/roundtrip files were removed after remote readback, releasing1,202,978,816B; original raw, ELF/debug/native/package/source artifacts remain. Restore compressed parts from the fixed commits when needed.

## Conditions and meaning

Same local Linux x64 host and default runtime; real PackageReference Release Native AOT consumers; unchanged mixed35 workload SHA256 `76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2`; fresh fixtures, persistent sessions, rows32/batch32, queue64, SQLite4/PG8workers. Every cell offers500businesses/s for30seconds, plus each worker’s35-case verification and64warmup outside measurement. Five seconds idle follows owner/session/source retirement without forced GC. Client CPU0–3, PG4–7, observer8. Candidate/before/Dapper order is reversed for the second round; all cells are serial under explicit peer quietness.

The dedicated `db-perf-arrivals` producer spins when at most2ms remain before the next due request (`OfferedLoad.WaitUntil`). It and the harness are included in process CPU/allocation. Do not subtract a theoretical producer budget or use the mixed process ratios to erase the separately measured6–10× thousand-row execution gap. At500/s, successful throughput near500/s is an arrival-rate result, not capacity. Latency numbers are histogram-bin upper bounds; service and scheduled-to-completion are distinct.

## Measured cells

| Provider / round / route | Success/s | Client CPU µs/success | Managed B/success | Service p50 / p95 / p99 ms | Scheduled p50 / p95 / p99 ms | Peak / released RSS MiB | GC0/1/2 | GC pause ms |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | ---: |
| sqlite / 1 / candidate | 499.958 | 2948.235 | 20738.313 | 0.436 / 4.030 / 9.830 | 0.500 / 4.424 / 10.027 | 42.172 / 40.336 | 98/16/2 | 108.343 |
| sqlite / 1 / before | 499.982 | 3258.737 | 25627.278 | 0.594 / 5.767 / 16.056 | 0.680 / 8.782 / 22.413 | 42.023 / 37.773 | 139/21/2 | 151.635 |
| sqlite / 1 / dapper | 499.569 | 2382.410 | 7569.430 | 0.144 / 1.270 / 2.163 | 0.214 / 1.458 / 3.342 | 29.379 / 29.250 | 53/3/1 | 53.510 |
| postgresql / 1 / candidate | 499.960 | 3015.192 | 21162.107 | 0.799 / 6.193 / 12.059 | 0.877 / 6.816 / 16.712 | 47.949 / 44.500 | 95/8/2 | 124.793 |
| postgresql / 1 / before | 499.968 | 3100.712 | 26057.125 | 0.860 / 6.816 / 12.190 | 0.938 / 7.176 / 13.238 | 47.609 / 41.469 | 141/16/2 | 149.937 |
| postgresql / 1 / dapper | 499.985 | 2354.366 | 7468.667 | 0.502 / 2.146 / 4.227 | 0.569 / 2.392 / 5.177 | 37.160 / 37.168 | 33/4/2 | 59.324 |
| postgresql / 2 / dapper | 499.978 | 2352.630 | 7475.151 | 0.430 / 1.982 / 4.112 | 0.492 / 2.130 / 5.931 | 37.555 / 37.562 | 35/4/2 | 70.077 |
| postgresql / 2 / before | 499.967 | 3247.526 | 26044.292 | 0.918 / 6.980 / 12.714 | 1.008 / 7.274 / 14.156 | 46.004 / 39.500 | 139/25/2 | 200.164 |
| postgresql / 2 / candidate | 499.969 | 2981.220 | 21145.303 | 0.795 / 6.619 / 13.763 | 0.868 / 7.143 / 16.646 | 45.797 / 43.398 | 98/10/2 | 133.091 |
| sqlite / 2 / dapper | 499.978 | 2376.806 | 7566.520 | 0.157 / 1.327 / 2.621 | 0.246 / 1.589 / 4.555 | 29.520 / 29.352 | 53/3/1 | 62.301 |
| sqlite / 2 / before | 499.984 | 3106.337 | 25653.394 | 0.561 / 4.424 / 10.158 | 0.627 / 4.882 / 11.338 | 43.113 / 38.109 | 131/23/2 | 117.672 |
| sqlite / 2 / candidate | 499.984 | 2928.883 | 20756.678 | 0.420 / 3.703 / 9.699 | 0.498 / 4.145 / 10.486 | 41.977 / 39.543 | 98/13/2 | 111.367 |

Each cell has15,000 successes,366,067 rows and full35-case oracle/ledger coverage. [Machine-readable summary](zero-cost-05/summary.json), [serial plan](zero-cost-05/series-01.plan.json) and [completed controller receipt](zero-cost-05/series-01.plan.resume.json) preserve exact values, pairwise comparisons, validation SHAs and order.

## Repeated benefits and retained regressions

| Provider | CPU change vs before, rounds1 /2 | Managed change, rounds1 /2 | Scheduled p99 change, rounds1 /2 | Released RSS change, rounds1 /2 |
| --- | --- | --- | --- | --- |
| sqlite | -9.53% / -5.71% | -4889.0 B / -4896.7 B | -55.26% / -7.51% | +6.78% / +3.76% |
| postgresql | -2.76% / -8.20% | -4895.0 B / -4899.0 B | +26.24% / +17.59% | +7.31% / +9.87% |

PG service p99 is−1.08% in round1 and+8.25% in round2. PG scheduled p99 is worse in both rounds (+26.24%,+17.59%); retain this risk when deciding final adoption. SQLite service/scheduled quantiles improve in both rounds, with substantial round-to-round tail variation. Peak RSS is nearly flat, while released RSS increases in all four pairs. Fewer allocated bytes do not prove smaller retained heap/RSS. GC counts and pauses remain process scope; ordinary native allocation and framework-only managed allocation are null/unknown. No0B claim is made.

## PostgreSQL server cost

| Round / route | Visible inner / outer interval CPU seconds |
| --- | --- |
| 1 / candidate | 7.880 / 8.160 |
| 1 / before | 7.130 / 7.340 |
| 1 / dapper | 7.060 / 7.510 |
| 2 / dapper | 6.160 / 6.710 |
| 2 / before | 7.590 / 8.020 |
| 2 / candidate | 8.090 / 8.420 |

These are endpoint differences from visible-process PPid trees tied to the actual postmaster PID/startTicks. They are non-atomic observed intervals, not mathematically exact steady-state bounds. Each cell retains acquisition times, eligible/missing observations and a separate wait4 lifetime total including startup, fixture, warmup, idle and shutdown. Never add the lifecycle total to the sampled interval. Unseen exited children and topology-transfer losses remain unknown.

## Wrapper and independent checks

The [local wrapper](local-runner-05/run_verified_mixed_cell.py) validates actual package/ELF/symbol/native/generated/source identities before and after each run, original35-case oracle/accounting, both latency boundaries, client/server identities, owner retirement, resource counters and ordinary/instrumented separation. The original repository observer and local plan helper are unchanged. The [independent review](local-runner-05/independent-review.md) covers23static controls (including6actual prepare paths),9targeted abort controls and the first real cell. The first SQLite candidate retains wrapperv1; subsequent cells use v2 with interruption/retirement lease controls and unchanged ordinary commands. The [complete independent result review](zero-cost-05/zero-cost-independent-review.md) passes373checks across all12raw/validation/controller/summary and35-case/histogram/GC ledgers. First-cell [review](zero-cost-05/first-cell-independent-review.md) remains separately attributed.

A persistent launch lease blocks subsequent cells if prior observer/owner retirement is unproven. The [serial controller](local-runner-05/run_verified_series.py) binds completed reuse to exact validation/snapshot/provider/variant identities, checks its own/plan/wrapper bytes at both cell boundaries, and stops on failure. It grants no automatic final credit. All12 complete raw result/validation pairs are included under [the cell index](zero-cost-05/cells-index.json). Full observer resources/commands/input snapshots remain at the local receipt paths; their next append-only raw archive is pending at this checkpoint.

## Active continuation — do not restart completed work

1. `experiments/recovery/pressure-05/series-01.plan.json` has completed16serial30second candidate/Dapper cells with zero business errors: SQLite1000/2000/3000/4000, PG1200/2400/3600/4800, original queue64. Include finite refusal onset and historical rates; do not infer an exact capacity from one short cell. The quiet pressure window ended after all16 clean validations; its full analysis and raw append are next.
2. Resolve the single [tail-completion06 hypothesis](tail-completion-hypothesis-06.md) before final freeze. Worker-D’s new ordering may permit removal of an additional eligible completion queue; its fraction and effect are unproven. The new independent assessment supports a bounded combined experiment, preserving the old standalone Common-A rejection. Contract proof and actual-generation mechanism counts precede ordinary A/B. The [read-only implementation design](tail-completion-design-06.md) identifies actual existing regression methods and distinguishes directly counted coordinator offers from completion-queue branches inferred through the locked runtime and actual ELF.
3. Preserve the current early-stop/money1 mixed/tail risks. Select or reject the additional candidate on repeated evidence, then freeze actual consumers. Supplement the two matched before long cells and execute the four requested1800second candidate/Dapper × provider cells serially. Native allocation diagnosis is a separate identity; final4/4 remains unearned.
4. Complete distinct author/independent review, normal PR merges, main existing CI, rule-selected releases and actual public NuGet AOT consumption. No release or public-consumer result is claimed yet.

Working root remains `/workspace/scratch/0669b59f9cae/DB-Exec-Parity-01`; source `toolchain/environment.sh`. The completed zero-cost serial receipt is `experiments/recovery/zero-cost-05/series-01.plan.resume.json`; completed pressure resume is `experiments/recovery/pressure-05/series-01.plan.resume.json`. Every attempt has its own raw/validation/resume identity. A chat interruption does not authorize restarting or overwriting a completed cell.
