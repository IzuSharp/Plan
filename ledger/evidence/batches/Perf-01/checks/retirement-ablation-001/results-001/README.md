# Perf-01: retirement retry ablation

## Decision and scope

Remove the extra post-result retirement retry; retain the lazy `TypedStream`
waiter. In this isolated probe, all three processes without the extra retry had
lower public-call mean, public-call p99, and process CPU than every process with
it. This supports removing the additional scheduling complexity. It does not
establish final application throughput or an A21 significance decision. The
owner must build, bind, and verify the revised final product, and measure its
affected application results under that new identity.

The six independent processes ran on 2026-11-20 from
**06:40:12.922114 UTC to 06:40:41.183159 UTC**, in the predeclared order
**A/B, B/A, A/B**. All six exited 0. Each executed 20 warmup calls followed by
1,000 serial SQLite scalar calls, with 4,000 complete native-operation
observations. Every scalar result and retirement invariant passed, and all six
data sources reported their resources released. The loaded SQLite native hash
matched in every process. These are instrumented profiles: **zero formal
comparison credit and zero long-duration credit**.

## Actual results

Times are milliseconds. CPU and allocation cover the measured call loop in each
process. The retirement column counts `BeforeTake` to the managed `Retired`
observation intervals of at least 9 ms, out of 4,000 observations per process.

| Order | Variant | Call mean | Call p99 | Process CPU | Managed bytes, including observer | Retirement intervals ≥9 ms |
|---:|:---:|---:|---:|---:|---:|---:|
| 1 | A | 6.365491 | 30.6289 | 681.571 | 17,391,544 | 335 |
| 2 | B | 0.616979 | 10.1731 | 410.019 | 17,358,640 | 14 |
| 3 | B | 2.017880 | 18.4209 | 581.443 | 17,359,968 | 68 |
| 4 | A | 10.313278 | 33.0000 | 808.250 | 17,388,480 | 548 |
| 5 | A | 6.782715 | 31.1258 | 630.166 | 17,372,744 | 356 |
| 6 | B | 1.061859 | 20.3341 | 372.977 | 17,357,200 | 40 |

The following latency and resource aggregates are arithmetic means of the
three process statistics. A mean of process p99 values is **not a pooled p99**.
The final row is a count over 12,000 observations per variant.

| Metric | A: extra retry | B: extra retry removed | Absolute change, B−A | Change |
|---|---:|---:|---:|---:|
| Mean public-call latency, ms | 7.820495 | 1.232239 | −6.588255 | −84.243% |
| Mean of process call p99, ms | 31.584900 | 16.309367 | −15.275533 | −48.363% |
| Mean observed retirement interval, ms | 1.824401 | 0.215653 | −1.608749 | −88.180% |
| Mean of process retirement p99, ms | 13.264053 | 6.244658 | −7.019394 | −52.920% |
| Mean process CPU, ms | 706.662333 | 454.813000 | −251.849333 | −35.639% |
| Mean managed bytes, including observer | 17,384,256.000 | 17,358,602.667 | −25,653.333 | −0.148% |
| Retirement observations ≥9 ms | 1,239 | 122 | −1,117 | −90.153% |

All processes recorded eight generation-0 collections and no generation-1 or
generation-2 collections. RSS was not sampled by this probe and is unavailable.
The allocation figure uses process-wide `GC.GetTotalAllocatedBytes` over the
call loop; its preallocated trace arrays, warmup, startup, result serialization,
and final source disposal fall outside that bracket. Observer work during the
loop remains included.

## Exact source and artifact identities

Variant A is product commit
`ada13b865ec5d19876745498f6f51d8ad2367399`, tree
`0d1b1ca390b582b1f2ebf004f7778c8f084a68a4`.
Variant B is the retained local experimental commit
`5ac6620015f5096bc3c800b1d95f60af898a097b`, tree
`d06e25143d883252e4bdbd988dad2bed5ad3429e`.
The complete source diff changes only
[`src/Interop.Async/AsyncOperation.cs`](https://github.com/IzuSharp/NativeWeave/blob/ada13b865ec5d19876745498f6f51d8ad2367399/src/Interop.Async/AsyncOperation.cs):
it removes `_postResultRetryRequested` and the extra `Signal()` on a
post-result `Pending` retirement attempt. `RequestRetry()` and the original
timer, ownership, cancellation, and scheduler-failure paths remain. The lazy
waiter is identical in both variants, with source SHA-256
`5c917739cb57a42240ae6f708a2410c5c0f2d89d36e8bbc49ffc1aaa070c9091`.

Both use the unchanged
[`RetirementProbe`](https://github.com/IzuSharp/NativeWeave/blob/ada13b865ec5d19876745498f6f51d8ad2367399/tests/Perf01.Shared/RetirementProbe/Program.cs),
source SHA-256
`d642d024ced08a2c5a6392e797b6de6ca904f59c7141e57ad0e5cf33a3fb3774`,
and actually loaded SQLite native SHA-256
`7254f8e490f19637701d92523c2ba08e0cbdfdbe4c5f28173d4215b5f303da8d`.
Both consumers use Release Native AOT and the same `x86-64-v2` setting.
Their recorded executable hashes are respectively
`b8b64cf0c68543c1059f5aaa8e8697f65813479217f31f6bf08aa30cb99c7645`
and
`331dd2aa240e040c5db07d4dafc7d83b539b382d8de8ac6a0dbe185b4ff12f13`.
Package versions and provenance metadata differ; the claim is an isolated
runtime source change, not a byte-identical build except for one instruction.
The three reused native packages retain A's native source identity.

## Interpretation and independent audit

The `Retired` timestamp is taken by the managed test observer after
[`DataSource.Complete`](https://github.com/IzuSharp/NativeWeave/blob/ada13b865ec5d19876745498f6f51d8ad2367399/src/Data.NativeHost/DataSource.cs)
awaits `operation.Retirement`. Its interval includes continuation scheduling
and observation work. It is not a direct native-quiescence timestamp. The
probe does not count `Pending` returns or extra-retry triggers; the results do
not prove that a particular timer or wake-up mechanism caused the difference.
No new A21 noise band was established. This experiment is separate from the
earlier historical single-process retirement profile and from database
application comparisons.

The independent numeric audit recomputed all 6,000 call durations and 24,000
operation intervals from the six original result arrays. Percentiles use the
same nearest-rank method as the existing profile projection:
`sorted(values)[max(0, ceil(count * p) - 1)]`. All owner-reported numeric rows
were reproduced; 455 audit checks passed. The audit rehashed consumed small
sources, manifests, results, receipts, and logs. It verified recorded package
and consumer identities against the actual measurement binding; it did not
rehash large binaries or execute the workloads. The original measurement
runner performed the binary/package checks and preserved their binding.

The first offline projection exited 1 because its metadata assertion
incorrectly assigned B's managed source commit to the three reused native
packages. Its source and failure receipt remain retained. After correcting
that assertion to the manifests' actual native source commit, the second
projection completed. No measurement input, threshold, result, or failed
attempt was changed.

[`public-summary.json`](public-summary.json) contains the six complete numeric
rows, aggregate changes, fixed artifact-role hashes, and the consumed-input
hash checklist. [`projection-execution.json`](projection-execution.json)
records the actual offline extraction and the preserved first failure. The
measurement execution SHA-256 is
`82f0e63f4dfe8d6989c2e53dd6619e0f99c5dc180b33ee472c700e2c2476b2d7`;
the actual binding SHA-256 is
`40eedf5b6177c60c96927384266afcac66cf8da340e864259036996cc77ee39e`.
Full local inputs and the private projection source remain local; this report
does not claim that their operational contents have been publicly published.
