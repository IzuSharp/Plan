# PG codec B — independent review of completed ordinary02

**Conclusion:** retain commit `23845016b707a2876e6777cf935667dc546ca6d5` for integration as a targeted PostgreSQL decimal-configuration optimization. The source-bound resource mechanism and ordinary two-round money32/money1000/wide32 CPU/service-p50 changes support that scope. It has not aligned Korda with Dapper.AOT, established a mixed35 benefit, or established absence of small control-path regressions.

## Verified comparison boundary

`analysis/pg-codec-b-ordinary-review.json` and `diagnostics/pg-codec-b/review_ordinary.py` contain the independent raw-result checks. All 48 actual process receipts match their recorded SHA-256 and executable identity. Each executed exactly 256 planned/started/completed operations, with zero failed/retried/oracle-violating operations, histogram count 256 and successful supported owner drain. They are ordinary Release Native AOT, no allocation shim, no empty-driver substitution, prepared/persistent, one worker, warmup 64, batch 32, 8 tenants and 1,024 orders per tenant. Monotonic durations, CPU/managed-byte division and before/after allocation accounting agree with the raw receipts.

For all 16 same-provider/case/size/round groups, baseline Korda, codec-B Korda and Dapper report identical expected result rows and digest. Selected SQL matches after normalizing parameter spelling and verifying positional order: PostgreSQL Korda `$N`, Dapper `@pN`, SQLite Korda anonymous `?`. This is a source/reported-command check, not a new protocol capture. Korda baseline/candidate SQL execution and protocol-submission deltas also match. Dapper owner drain observes application logical connections only; it must not be equated to Korda native owner visibility.

The initial offline normalizer handled only PostgreSQL named/positional spelling and failed on SQLite anonymous placeholders. The corrected verifier explicitly checks all three spellings and ordered ordinals; no raw result was edited.

## Ordinary observations, both repetitions retained

CPU is client process CPU microseconds per successful operation. p50 is the retained service histogram upper bound. Each cell below is round 0 / round 1; positive percentages indicate improvement against the Korda baseline in the same round.

| Provider/case | Baseline CPU μs | Candidate CPU μs | Dapper CPU μs | Candidate CPU reduction | Service p50 reduction |
| --- | ---: | ---: | ---: | ---: | ---: |
| postgresql money1 | 405.21 / 355.98 | 271.64 / 356.46 | 127.65 / 129.22 | +32.96% / -0.13% | +14.94% / +4.12% |
| postgresql money32 | 600.61 / 585.96 | 481.46 / 499.75 | 126.84 / 138.78 | +19.84% / +14.71% | +21.33% / +19.26% |
| postgresql money1000 | 7,875.38 / 7,888.62 | 5,347.80 / 5,097.65 | 628.46 / 601.03 | +32.09% / +35.38% | +45.00% / +45.50% |
| postgresql wide32 | 877.11 / 680.23 | 637.66 / 592.41 | 186.84 / 238.08 | +27.30% / +12.91% | +16.13% / +6.67% |
| postgresql customer-totals32 | 389.41 / 424.67 | 385.70 / 489.30 | 157.25 / 158.73 | +0.95% / -15.22% | +0.59% / -2.23% |
| postgresql numeric32 | 444.64 / 463.45 | 444.86 / 466.14 | 110.60 / 110.25 | -0.05% / -0.58% | -7.89% / -4.59% |
| sqlite money32 | 509.48 / 459.64 | 411.74 / 471.68 | 33.69 / 31.30 | +19.19% / -2.62% | +10.07% / -5.14% |
| sqlite wide32 | 618.67 / 617.44 | 638.80 / 589.48 | 114.27 / 115.73 | -3.25% / +4.53% | -3.92% / -5.94% |

PG money1000 CPU is 7,875.38 / 7,888.62 μs before and 5,347.80 / 5,097.65 μs after: reductions of 32.09% / 35.38%. Its p50 moves from 6,553.60 μs to 3,604.48 / 3,571.71 μs, reductions of 45.00% / 45.50%. This is consistent with removing 47,000 configuration-related allocation calls and 1,132,000 requested native bytes per 1,000-decimal business in the independent resource controls. This consistency does not assign all CPU improvement exclusively to allocator calls; JSON parsing, destruction, canonical-string reconstruction and the changed valid-path instructions are removed together.

Dapper money1000 remains at 628.46 / 601.03 μs CPU and 700.416 / 659.456 μs p50. Candidate Korda is still 8.51× / 8.48× Dapper client CPU and 5.15× / 5.42× p50. This candidate is a meaningful local improvement with a large remaining execution-path gap.

PG money32 CPU improves by 19.84% / 14.71% and p50 by 21.33% / 19.26%. PG wide32 CPU improves by 27.30% / 12.91% and p50 by 16.13% / 6.67%. These are the additional repeated ordinary supports for retaining the targeted change.

## Non-benefits and observed adverse controls

- PG money1 CPU is not a repeated win: one round improves 32.96%, the other is 0.13% worse. p50 improves in both, by 14.94% / 4.12%, with different magnitudes. Do not report a stable singleton CPU benefit.
- PG customer-totals has 9 decimal outputs per business, and its source allocations fall as predicted, but ordinary CPU is 0.95% better / 15.22% worse and p50 is 0.59% better / 2.23% worse. Do not report a measured aggregate endpoint benefit.
- Int64 numeric32 contains no configured decimal. CPU is nearly unchanged (0.05% / 0.58% worse), while p50 is 7.89% / 4.59% worse in both rounds. This adverse control must remain visible; two short rounds do not establish whether it is a repeatable product regression, code-layout effect or host/runtime variation.
- SQLite money32 CPU/p50 directions reverse between rounds. SQLite wide32 CPU directions also reverse, but its p50 is 3.92% / 5.94% worse in both rounds. There is no justified SQLite performance gain from this PG-only codec change, and no justified blanket claim of zero regression.

The strongest benefit is much larger than these small adverse control movements, and its direction agrees with exact source-resource changes. That supports retaining this narrow implementation for the combined candidate while carrying the adverse observations into final comparison. It does not justify erasing them or attributing them definitively without another observation. Root-owned combined-candidate/frozen mixed runs remain the appropriate next gate; this review launches no further benchmark.

## Allocation and measurement limits

For money1000, managed allocation is 42,873.09 / 42,863.66 B per business before, 42,941.25 / 42,902.38 B after, and 42,349.31 / 42,323.34 B for Dapper. It is essentially unchanged at this attribution boundary, not reduced to zero. The candidate exceeds Dapper by 591.94 / 579.03 B per business; this is whole-process measured managed allocation including required DTOs and harness/driver activity, not an exact framework-only attribution. All six money1000 processes report 4 Gen0, 1 Gen1 and 0 Gen2 collections in their measured intervals.

The screen has only 256 measured operations and two processes per variant/case. money1000 measured wall windows are about 1.70 s baseline, 0.97 s candidate and 0.17–0.19 s Dapper; the smaller cases are shorter still. Reversed ordering reduces one source of time drift but does not establish stationarity. Reported process CPU resolution, scheduling and warm-state effects still matter. Histograms provide observed quantiles, but roughly the highest few operations determine p99; these cells do not establish sustained-tail, saturation, arrival-rate/queue delay or long-run RSS/GC behavior. Server cost is not subtracted from or inferred from the client CPU number.

Ordinary01 remains an invalid comparison attempt: Dapper `money --rows1 --verify` enters the all35 warmup sweep and fails on its fixed32 related-parent contract before the gate. Ordinary02 uniformly uses selected-case warmup64 and retains unconditional row/digest validation in every operation. The original mixed35 verification remains enabled in its dedicated rows32/batch32 cells. Older all35-warmed partial cells are not pooled with ordinary02.

## Integration decision

Preserve the exact canonical parser, all original validation sites and original JSON error fallback. Preserve the 463-configuration and existing scalar/provider/ownership regressions and independent package routing. Do not bundle metadata caches, removed checks, FixedScaleMoney changes, vector rewrites or protocol/scheduling changes under this evidence. Adopt the source change as targeted allocation/CPU improvement, state its supported decimal cases, and explicitly state that Dapper parity and the mixed35/final delivery gates remain unachieved by this experiment.
