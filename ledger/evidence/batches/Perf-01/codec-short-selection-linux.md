# Perf-01 codec fixed short-load selection

## Recorded before candidate observation

The prospective [short-cohort recipe](codec-short-cohorts-linux.md) remains the
command and acceptance authority. Root's before-only W1 smoke completed on
2026-11-19 at 11:00:34.957897 UTC. Its [actual receipt and audit](observations-before/codec-w1-smoke-003/README.md)
passed every declared smoke bound, so the fixed short selections are:

| Stratum | Workers | Planned rate | Full measurement duration | Selection basis |
| --- | ---: | ---: | ---: | --- |
| W1 | 1 | 134 operations/s | 120 seconds | Passing actual before-only 10-second smoke, without a new capacity ladder |
| W2 | 2 | 268 operations/s | 60 seconds | Existing root-selected fixed rate; this W1 smoke does not alter it |

Use the exact new `ROOT/perf01-codec-checks/package-before-003/manifest.json`
(SHA-256 `f7a766eb277d09a6f5d64fd3ecac2e83bf6dcbac41ab384c0b75affc234c775d`)
with the unchanged corpus and final driver/A21 source binding. The plan of the
actual smoke records its loaded native library. Keep the corpus, driver/A21
hashes and workload configuration fixed across fresh before and after cohorts.
Bind the after version to its own fresh producer and actual native hashes; keep
historical manifests unchanged.

Everything else stays as specified by the recipe: complete mixed 160-operation
cycle, both interfaces and actions, target CPUs 2,3 and generator CPUs 0,1,
queue 64, in-flight bound 256, warmup 20 seconds, recovery 10 seconds at 1/s,
short idle five seconds, deadline 1,000 ms, generator lag bound 100 ms,
whole-cell arrival p99 at most 500 ms, sampled target RSS at most 256 MiB and
zero unexpected outcomes. The rounded-period duration calculation yields at
least 16,000 scheduled operations without relying on dispatch-guard additions.
Every completed full process must actually have at least 16,000 successes and
at least 100 in each of its 32 rows; planned counts are insufficient.

The smoke has only 1,355 measurement successes and a minimum of eight successes
per row. It is selection evidence only, excluded from noise and confirmation.
Collect separate three-process before-only noise receipts for W1 and W2, freeze
their hashes before candidate observations, and collect fresh interleaved
before/after/direct processes. Managed ZLibStream remains a valid-corpus
observation with its documented semantic and ownership limitations.

The fresh post-A21 baseline capacity confirmation near 336/s remains a separate
root-owned step. These fixed-load selections neither declare capacity nor
replace the five paired 30-minute groups. No new workload was run to author
this decision record, and it awards no long-duration credit.
