# Perf-01 final-002 database comparison checkpoint

This is the actual database-only numerical projection of final candidate `0715ffb6376b1ae08259ad7e2cb30ff0320d83e7` against frozen baseline `ea5fa528035d025bd7a28698ee7c71194432236c`, direct Rust, and managed controls. The candidate tree is `cd0a6022e0115c22f133aedf6c801d9244640523`. Exact execution-binding, report, reader, projection-source, input and receipt hashes are in `checklist.json`; actual artifact and loaded-library hashes remain in each process record in `database.json`.

The projection ran successfully from **2026-11-20 08:38:50.516796 UTC to 08:39:05.487485 UTC** on CPU 8 under the existing timing lock. All **48** database processes, including C1/C4/C8, passed the original correctness and evidence checks. All **24** scope rows and all controls are retained. **45** processes meet the frozen service standard; **3** PostgreSQL C16 controls miss it: direct repetition 2, managed repetitions 0 and 2. These are correct but ineligible measurements, not missing or invalid records. All before/after processes meet the service standard. A cohort or pair containing an ineligible control cannot support an eligible performance ranking.

The 48 processes contain **177,648 successful measured operations**, **88,848 measured durable commits**, zero operation errors and zero business retries. SQLite lifetime BUSY and LOCKED counters are measured zero for all 12 before/after processes. Direct and managed provider counters are unavailable. SQLite internal engine retry counts, database-service CPU/RSS and GC/allocation values that were not collected remain unavailable.

This checkpoint does **not** complete Perf-01 or contribute new workload duration. The complete inventory in `coverage.json` explicitly retains 54 missing protocol process slots, 24 missing codec process slots, and 10 missing after/direct capacity role groups; the 5 previously validated before-capacity groups remain present. Final long runs and remaining comparisons are separate obligations.

## Interpretation

PostgreSQL C16 before-to-after whole-load mean changes from **34.535357 ms to 31.331079 ms**, and mean process p99 from **214.366439 ms to 188.279126 ms** (**−12.169495%**). Whole/cycle/page A21 decisions are all **inconclusive**. This descriptive reduction does not establish a repeatable improvement. The direct Rust cohort has a service-standard miss, so it cannot establish an eligible Rust gap at this load.

SQLite C16 whole-load mean changes from **33.076711 ms to 32.928024 ms** (**−0.449522%**, A21 **within_band**), while mean process p99 rises from **162.153094 ms to 179.764195 ms** (**+10.860786%**). Cycle/page p99 rise **13.986404% / 7.489327%**. Cycle mean is within the frozen noise band and page mean is inconclusive. A21 tests process means; those decisions do not dismiss tail-latency regression risk. Final SQLite whole-load mean is **5.471690×** direct Rust, with A21 classifying the positive mean gap as regression; p99 is **13.645949×** direct Rust, a descriptive percentile comparison.

C1/C4/C8 have one process per role and remain descriptive. C16 has three processes per role. DB p50/p95/p99 aggregates are means of process percentiles, not pooled quantiles. The `whole` scope is the combined cycle/page business workload, not an isolated scalar binding microbenchmark. Conditional cycle/page success rates use the whole-load observation denominator. CPU/RSS describes the whole process and is not attributed to a slice.

## Database


Conditional cycle/page latency shares the whole-load denominator. Whole-process CPU/RSS and lifetime SQLite BUSY/LOCKED counts are separate in the JSON. C1/C4/C8 are descriptive single-process points; C16 has three processes per role.

| Provider / C / slice | Role | Status | Success/s | p99 ms | CPU % one core | Peak RSS MiB (mean) | Errors (mean) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| postgresql / 1 / whole | before | descriptive | 5.015 | 68.65 | 6.455 | 30.95 | 0 |
| postgresql / 1 / whole | after | descriptive | 5.005 | 135.6 | 6.193 | 30.77 | 0 |
| postgresql / 1 / whole | direct | descriptive | 5.016 | 27.16 | 0.4001 | 7.664 | 0 |
| postgresql / 1 / whole | managed | descriptive | 5.016 | 26.89 | 1.151 | 38.8 | 0 |
| postgresql / 1 / cycle | before | descriptive | 2.516 | 70.85 | N/A | N/A | 0 |
| postgresql / 1 / cycle | after | descriptive | 2.511 | 142.9 | N/A | N/A | 0 |
| postgresql / 1 / cycle | direct | descriptive | 2.516 | 28.39 | N/A | N/A | 0 |
| postgresql / 1 / cycle | managed | descriptive | 2.516 | 27.58 | N/A | N/A | 0 |
| postgresql / 1 / page | before | descriptive | 2.499 | 39.16 | N/A | N/A | 0 |
| postgresql / 1 / page | after | descriptive | 2.494 | 46.45 | N/A | N/A | 0 |
| postgresql / 1 / page | direct | descriptive | 2.5 | 11.53 | N/A | N/A | 0 |
| postgresql / 1 / page | managed | descriptive | 2.5 | 12.16 | N/A | N/A | 0 |
| postgresql / 4 / whole | before | descriptive | 20.01 | 87.83 | 16.07 | 31.11 | 0 |
| postgresql / 4 / whole | after | descriptive | 20 | 72.26 | 15.61 | 32 | 0 |
| postgresql / 4 / whole | direct | descriptive | 20.04 | 27.9 | 1.653 | 7.906 | 0 |
| postgresql / 4 / whole | managed | descriptive | 20.01 | 26.96 | 4.007 | 39.2 | 0 |
| postgresql / 4 / cycle | before | descriptive | 10.03 | 96.19 | N/A | N/A | 0 |
| postgresql / 4 / cycle | after | descriptive | 10.02 | 90.14 | N/A | N/A | 0 |
| postgresql / 4 / cycle | direct | descriptive | 10.05 | 31.49 | N/A | N/A | 0 |
| postgresql / 4 / cycle | managed | descriptive | 10.03 | 35.14 | N/A | N/A | 0 |
| postgresql / 4 / page | before | descriptive | 9.98 | 33.62 | N/A | N/A | 0 |
| postgresql / 4 / page | after | descriptive | 9.974 | 40.17 | N/A | N/A | 0 |
| postgresql / 4 / page | direct | descriptive | 9.996 | 8.83 | N/A | N/A | 0 |
| postgresql / 4 / page | managed | descriptive | 9.981 | 8.79 | N/A | N/A | 0 |
| postgresql / 8 / whole | before | descriptive | 40.01 | 77.38 | 26.19 | 35.89 | 0 |
| postgresql / 8 / whole | after | descriptive | 39.99 | 68.55 | 25.3 | 33.99 | 0 |
| postgresql / 8 / whole | direct | descriptive | 40.02 | 22.76 | 3.403 | 8.105 | 0 |
| postgresql / 8 / whole | managed | descriptive | 40.03 | 29.52 | 8.111 | 41.4 | 0 |
| postgresql / 8 / cycle | before | descriptive | 20.03 | 83.48 | N/A | N/A | 0 |
| postgresql / 8 / cycle | after | descriptive | 20.02 | 70.57 | N/A | N/A | 0 |
| postgresql / 8 / cycle | direct | descriptive | 20.03 | 24.29 | N/A | N/A | 0 |
| postgresql / 8 / cycle | managed | descriptive | 20.04 | 32.02 | N/A | N/A | 0 |
| postgresql / 8 / page | before | descriptive | 19.98 | 31.86 | N/A | N/A | 0 |
| postgresql / 8 / page | after | descriptive | 19.97 | 33.66 | N/A | N/A | 0 |
| postgresql / 8 / page | direct | descriptive | 19.98 | 21.62 | N/A | N/A | 0 |
| postgresql / 8 / page | managed | descriptive | 19.99 | 11.74 | N/A | N/A | 0 |
| postgresql / 16 / whole | before | validated | 179.8 | 214.4 | 84.12 | 47.23 | 0 |
| postgresql / 16 / whole | after | validated | 179.6 | 188.3 | 83.35 | 45.27 | 0 |
| postgresql / 16 / whole | direct | ineligible | 179.8 | 439.4 | 10.99 | 9.232 | 0 |
| postgresql / 16 / whole | managed | ineligible | 179.3 | 677 | 26.5 | 45.17 | 0 |
| postgresql / 16 / cycle | before | validated | 89.89 | 247.1 | N/A | N/A | 0 |
| postgresql / 16 / cycle | after | validated | 89.82 | 221.5 | N/A | N/A | 0 |
| postgresql / 16 / cycle | direct | ineligible | 89.93 | 491 | N/A | N/A | 0 |
| postgresql / 16 / cycle | managed | ineligible | 89.66 | 708.1 | N/A | N/A | 0 |
| postgresql / 16 / page | before | validated | 89.87 | 157 | N/A | N/A | 0 |
| postgresql / 16 / page | after | validated | 89.8 | 129.8 | N/A | N/A | 0 |
| postgresql / 16 / page | direct | ineligible | 89.91 | 402.4 | N/A | N/A | 0 |
| postgresql / 16 / page | managed | ineligible | 89.65 | 628.1 | N/A | N/A | 0 |
| sqlite / 1 / whole | before | descriptive | 5.013 | 139 | 8.021 | 27.43 | 0 |
| sqlite / 1 / whole | after | descriptive | 5.013 | 127.5 | 8.173 | 27.69 | 0 |
| sqlite / 1 / whole | direct | descriptive | 5.015 | 16.87 | 0.8502 | 8.004 | 0 |
| sqlite / 1 / whole | managed | descriptive | 5.016 | 55.59 | 1.151 | 37.69 | 0 |
| sqlite / 1 / cycle | before | descriptive | 2.515 | 144.1 | N/A | N/A | 0 |
| sqlite / 1 / cycle | after | descriptive | 2.515 | 146.5 | N/A | N/A | 0 |
| sqlite / 1 / cycle | direct | descriptive | 2.516 | 16.87 | N/A | N/A | 0 |
| sqlite / 1 / cycle | managed | descriptive | 2.516 | 88.68 | N/A | N/A | 0 |
| sqlite / 1 / page | before | descriptive | 2.498 | 47.67 | N/A | N/A | 0 |
| sqlite / 1 / page | after | descriptive | 2.498 | 64.93 | N/A | N/A | 0 |
| sqlite / 1 / page | direct | descriptive | 2.499 | 21.84 | N/A | N/A | 0 |
| sqlite / 1 / page | managed | descriptive | 2.5 | 39.74 | N/A | N/A | 0 |
| sqlite / 4 / whole | before | descriptive | 20.02 | 93.84 | 18.22 | 28.48 | 0 |
| sqlite / 4 / whole | after | descriptive | 20 | 117.5 | 18.86 | 28.26 | 0 |
| sqlite / 4 / whole | direct | descriptive | 20.04 | 43.3 | 3.458 | 8.758 | 0 |
| sqlite / 4 / whole | managed | descriptive | 20.04 | 14.07 | 3.558 | 38.16 | 0 |
| sqlite / 4 / cycle | before | descriptive | 10.03 | 103.3 | N/A | N/A | 0 |
| sqlite / 4 / cycle | after | descriptive | 10.02 | 117.6 | N/A | N/A | 0 |
| sqlite / 4 / cycle | direct | descriptive | 10.05 | 55.5 | N/A | N/A | 0 |
| sqlite / 4 / cycle | managed | descriptive | 10.05 | 14.73 | N/A | N/A | 0 |
| sqlite / 4 / page | before | descriptive | 9.984 | 34.71 | N/A | N/A | 0 |
| sqlite / 4 / page | after | descriptive | 9.974 | 62.95 | N/A | N/A | 0 |
| sqlite / 4 / page | direct | descriptive | 9.997 | 15.78 | N/A | N/A | 0 |
| sqlite / 4 / page | managed | descriptive | 9.997 | 10.7 | N/A | N/A | 0 |
| sqlite / 8 / whole | before | descriptive | 39.97 | 99.56 | 31.31 | 29.69 | 0 |
| sqlite / 8 / whole | after | descriptive | 39.91 | 129 | 30.51 | 29.35 | 0 |
| sqlite / 8 / whole | direct | descriptive | 40.03 | 32.9 | 6.856 | 10.04 | 0 |
| sqlite / 8 / whole | managed | descriptive | 40.04 | 15.36 | 6.51 | 39.23 | 0 |
| sqlite / 8 / cycle | before | descriptive | 20.01 | 107.5 | N/A | N/A | 0 |
| sqlite / 8 / cycle | after | descriptive | 19.98 | 140.4 | N/A | N/A | 0 |
| sqlite / 8 / cycle | direct | descriptive | 20.04 | 36.13 | N/A | N/A | 0 |
| sqlite / 8 / cycle | managed | descriptive | 20.04 | 17.04 | N/A | N/A | 0 |
| sqlite / 8 / page | before | descriptive | 19.96 | 34.35 | N/A | N/A | 0 |
| sqlite / 8 / page | after | descriptive | 19.93 | 36.17 | N/A | N/A | 0 |
| sqlite / 8 / page | direct | descriptive | 19.99 | 14.4 | N/A | N/A | 0 |
| sqlite / 8 / page | managed | descriptive | 19.99 | 8.435 | N/A | N/A | 0 |
| sqlite / 16 / whole | before | validated | 49.94 | 162.2 | 37.53 | 37.4 | 0 |
| sqlite / 16 / whole | after | validated | 49.96 | 179.8 | 37.71 | 37.7 | 0 |
| sqlite / 16 / whole | direct | validated | 50.01 | 13.17 | 7.531 | 12.56 | 0 |
| sqlite / 16 / whole | managed | validated | 50.01 | 16.28 | 7.909 | 41.82 | 0 |
| sqlite / 16 / cycle | before | validated | 24.98 | 213.6 | N/A | N/A | 0 |
| sqlite / 16 / cycle | after | validated | 24.99 | 243.5 | N/A | N/A | 0 |
| sqlite / 16 / cycle | direct | validated | 25.01 | 15.53 | N/A | N/A | 0 |
| sqlite / 16 / cycle | managed | validated | 25.01 | 19.25 | N/A | N/A | 0 |
| sqlite / 16 / page | before | validated | 24.96 | 34.68 | N/A | N/A | 0 |
| sqlite / 16 / page | after | validated | 24.97 | 37.28 | N/A | N/A | 0 |
| sqlite / 16 / page | direct | validated | 25 | 8.066 | N/A | N/A | 0 |
| sqlite / 16 / page | managed | validated | 25 | 7.965 | N/A | N/A | 0 |

### DB changes and direct Rust gaps

Negative latency deltas mean lower latency. Percentages use the explicitly named baseline; a zero or missing denominator is N/A.

| Provider / slice | Baseline → candidate | Status | p99 Δ ms | p99 Δ % | Success/s Δ | Mean-noise decision |
| --- | --- | --- | ---: | ---: | ---: | --- |
| postgresql / whole | before → after | validated | -26.09 | -12.17 | -0.1469 | inconclusive |
| postgresql / whole | direct → before | ineligible | -225.1 | -51.22 | -0.06946 | inconclusive |
| postgresql / whole | direct → after | ineligible | -251.2 | -57.15 | -0.2163 | inconclusive |
| postgresql / whole | direct → managed | ineligible | 237.6 | 54.06 | -0.5229 | inconclusive |
| postgresql / cycle | before → after | validated | -25.58 | -10.35 | -0.07344 | inconclusive |
| postgresql / cycle | direct → before | ineligible | -243.9 | -49.68 | -0.03473 | inconclusive |
| postgresql / cycle | direct → after | ineligible | -269.5 | -54.89 | -0.1082 | inconclusive |
| postgresql / cycle | direct → managed | ineligible | 217.1 | 44.21 | -0.2615 | inconclusive |
| postgresql / page | before → after | validated | -27.23 | -17.34 | -0.07342 | inconclusive |
| postgresql / page | direct → before | ineligible | -245.3 | -60.97 | -0.03473 | inconclusive |
| postgresql / page | direct → after | ineligible | -272.6 | -67.74 | -0.1081 | inconclusive |
| postgresql / page | direct → managed | ineligible | 225.7 | 56.08 | -0.2614 | inconclusive |
| sqlite / whole | before → after | validated | 17.61 | 10.86 | 0.01526 | within_band |
| sqlite / whole | direct → before | validated | 149 | 1131 | -0.06815 | regression |
| sqlite / whole | direct → after | validated | 166.6 | 1265 | -0.05289 | regression |
| sqlite / whole | direct → managed | validated | 3.107 | 23.58 | -0.001743 | within_band |
| sqlite / cycle | before → after | validated | 29.88 | 13.99 | 0.007631 | within_band |
| sqlite / cycle | direct → before | validated | 198.1 | 1276 | -0.03409 | regression |
| sqlite / cycle | direct → after | validated | 228 | 1469 | -0.02646 | regression |
| sqlite / cycle | direct → managed | validated | 3.723 | 23.98 | -0.0008718 | within_band |
| sqlite / page | before → after | validated | 2.597 | 7.489 | 0.007626 | inconclusive |
| sqlite / page | direct → before | validated | 26.61 | 329.9 | -0.03406 | regression |
| sqlite / page | direct → after | validated | 29.21 | 362.1 | -0.02644 | regression |
| sqlite / page | direct → managed | validated | -0.1008 | -1.249 | -0.0008712 | inconclusive |
