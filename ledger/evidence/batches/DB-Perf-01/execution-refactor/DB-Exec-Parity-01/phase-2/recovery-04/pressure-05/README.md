# Pressure-05: finite-load summary and independent review

**The candidate reaches continuing admission rejection and a bounded completion plateau at the high offered rates. Dapper still largely follows the highest offered rates tested, so this series does not locate its sustained saturation. The first observed refusals are not a monotonic capacity threshold.**

All16 cells passed 587 independent raw/validation/controller checks. There are 1,320,000 attempted businesses, 1,140,143 successes, 179,857 admission rejections, 27,819,949 consumed rows, and zero business errors, retries or oracle failures. Every cell covers all35 cases. This is analysis of existing evidence; no measurement, build, profile or archive ran.

## Conditions and accounting

Each cell ran30 seconds with queue64,32 rows/batch, prepared/persistent mode,8 tenants,1,024 orders/tenant,64 warmups per worker outside measurement, and5 idle seconds after owner release. SQLite uses4 workers; PostgreSQL8. Rates increase by provider, and candidate/Dapper order alternates. Historical offered rates SQLite3000 and PG3600 remain present. There is one observation per rate/variant, not replicated confidence intervals or30-minute acceptance.

Whole-cell throughput includes the actual drain interval. The final10-second subsection means completion timestamps in `[20,30)` and excludes drain completions; it is a fixed descriptive window, not automatic proof of stationarity. Planned events use scheduled time, whereas sent/rejected/completed events use their actual time. Some individual buckets consequently do not satisfy planned=sent+rejected, although the full ledgers reconcile.

## Per-cell outcome

| Cell | Attempted | Success | Rejected | Rejected % | Business errors | Success/s through drain |
|---|---:|---:|---:|---:|---:|---:|
| sqlite-rate-1000-candidate | 30000 | 30000 | 0 | 0.000 | 0 | 999.931 |
| sqlite-rate-1000-dapper | 30000 | 30000 | 0 | 0.000 | 0 | 999.965 |
| sqlite-rate-2000-dapper | 60000 | 59899 | 101 | 0.168 | 0 | 1996.570 |
| sqlite-rate-2000-candidate | 60000 | 59399 | 601 | 1.002 | 0 | 1977.336 |
| sqlite-rate-3000-candidate | 90000 | 69477 | 20523 | 22.803 | 0 | 2312.976 |
| sqlite-rate-3000-dapper | 90000 | 89421 | 579 | 0.643 | 0 | 2980.589 |
| sqlite-rate-4000-dapper | 120000 | 119446 | 554 | 0.462 | 0 | 3981.018 |
| sqlite-rate-4000-candidate | 120000 | 65843 | 54157 | 45.131 | 0 | 2192.076 |
| postgresql-rate-1200-candidate | 36000 | 35950 | 50 | 0.139 | 0 | 1198.252 |
| postgresql-rate-1200-dapper | 36000 | 35823 | 177 | 0.492 | 0 | 1194.051 |
| postgresql-rate-2400-dapper | 72000 | 72000 | 0 | 0.000 | 0 | 2399.887 |
| postgresql-rate-2400-candidate | 72000 | 71259 | 741 | 1.029 | 0 | 2373.376 |
| postgresql-rate-3600-candidate | 108000 | 71756 | 36244 | 33.559 | 0 | 2389.918 |
| postgresql-rate-3600-dapper | 108000 | 107884 | 116 | 0.107 | 0 | 3595.944 |
| postgresql-rate-4800-dapper | 144000 | 141833 | 2167 | 1.505 | 0 | 4726.883 |
| postgresql-rate-4800-candidate | 144000 | 80153 | 63847 | 44.338 | 0 | 2668.757 |

## Latency of accepted successful work

All values below are histogram-bin upper bounds in milliseconds. Rejected work is reported separately and is not assigned a successful-request latency. Raw service, scheduled and start-delay p50/p95/p99 values and complete histograms were reconciled.

| Cell | Service p50 / p95 / p99 ms | Scheduled p50 / p95 / p99 ms | Start-delay p99 ms |
|---|---|---|---:|
| sqlite-rate-1000-candidate | 0.510 / 6.062 / 14.025 | 0.623 / 7.700 / 20.447 | 5.472 |
| sqlite-rate-1000-dapper | 0.127 / 1.450 / 3.768 | 0.207 / 2.048 / 4.719 | 1.958 |
| sqlite-rate-2000-dapper | 0.138 / 2.294 / 6.914 | 0.268 / 4.178 / 12.452 | 8.585 |
| sqlite-rate-2000-candidate | 0.545 / 6.095 / 20.972 | 4.555 / 28.312 / 45.089 | 39.846 |
| sqlite-rate-3000-candidate | 0.512 / 5.603 / 19.661 | 26.870 / 39.584 / 54.264 | 44.040 |
| sqlite-rate-3000-dapper | 0.132 / 2.818 / 8.651 | 0.406 / 5.079 / 13.828 | 10.093 |
| sqlite-rate-4000-dapper | 0.122 / 2.277 / 6.816 | 0.557 / 4.588 / 12.845 | 7.733 |
| sqlite-rate-4000-candidate | 0.569 / 5.964 / 21.234 | 29.491 / 44.564 / 60.293 | 52.429 |
| postgresql-rate-1200-candidate | 0.795 / 9.306 / 13.304 | 0.881 / 10.027 / 17.039 | 6.259 |
| postgresql-rate-1200-dapper | 0.469 / 3.310 / 7.635 | 0.549 / 4.620 / 35.652 | 29.229 |
| postgresql-rate-2400-dapper | 0.457 / 3.506 / 5.636 | 0.506 / 3.867 / 6.652 | 2.720 |
| postgresql-rate-2400-candidate | 1.139 / 11.272 / 18.350 | 3.031 / 21.365 / 36.176 | 30.278 |
| postgresql-rate-3600-candidate | 1.270 / 14.352 / 25.297 | 26.345 / 50.332 / 75.497 | 63.439 |
| postgresql-rate-3600-dapper | 0.473 / 3.785 / 6.390 | 0.557 / 5.079 / 11.207 | 8.454 |
| postgresql-rate-4800-dapper | 0.516 / 4.391 / 8.094 | 0.766 / 9.568 / 21.365 | 18.612 |
| postgresql-rate-4800-candidate | 1.237 / 13.107 / 20.054 | 25.559 / 39.059 / 49.021 | 40.632 |

## Last10 seconds and continuing rejection

| Cell | Completion/s in0–10 /10–20 /20–30 | Last10 rejections | Rejecting seconds /10 | Last10 success min–max/s | Last10 CV % |
|---|---|---:|---:|---|---:|
| sqlite-rate-1000-candidate | 999.9 / 1000.1 / 999.9 | 0 | 0 | 993–1006 | 0.375 |
| sqlite-rate-1000-dapper | 1000.0 / 1000.0 / 1000.0 | 0 | 0 | 999–1001 | 0.077 |
| sqlite-rate-2000-dapper | 1989.9 / 1999.9 / 2000.1 | 0 | 0 | 1996–2003 | 0.106 |
| sqlite-rate-2000-candidate | 1977.5 / 1989.3 / 1967.7 | 281 | 4 | 1851–2024 | 3.042 |
| sqlite-rate-3000-candidate | 2236.6 / 2359.2 / 2345.2 | 6549 | 10 | 2090–2522 | 6.148 |
| sqlite-rate-3000-dapper | 2963.9 / 2981.6 / 2996.6 | 39 | 1 | 2962–3009 | 0.413 |
| sqlite-rate-4000-dapper | 3999.9 / 3952.0 / 3992.4 | 89 | 2 | 3920–4015 | 0.647 |
| sqlite-rate-4000-candidate | 2121.7 / 2190.5 / 2265.3 | 17349 | 10 | 1966–2492 | 6.820 |
| postgresql-rate-1200-candidate | 1194.9 / 1200.1 / 1199.9 | 0 | 0 | 1191–1206 | 0.392 |
| postgresql-rate-1200-dapper | 1186.3 / 1196.0 / 1199.9 | 0 | 0 | 1195–1204 | 0.206 |
| postgresql-rate-2400-dapper | 2400.0 / 2399.9 / 2400.0 | 0 | 0 | 2396–2404 | 0.115 |
| postgresql-rate-2400-candidate | 2399.7 / 2375.4 / 2346.9 | 497 | 5 | 2114–2413 | 4.001 |
| postgresql-rate-3600-candidate | 2216.3 / 2213.5 / 2738.8 | 8603 | 10 | 2570–2891 | 3.548 |
| postgresql-rate-3600-dapper | 3599.9 / 3588.7 / 3599.7 | 7 | 1 | 3595–3605 | 0.065 |
| postgresql-rate-4800-dapper | 4749.4 / 4663.0 / 4770.4 | 294 | 3 | 4537–4811 | 1.640 |
| postgresql-rate-4800-candidate | 2647.0 / 2663.7 / 2697.4 | 21026 | 10 | 2456–2881 | 4.708 |

- SQLite candidate rejects during all30 seconds at both3000/s and4000/s. Final10 completion rates are **2345.2/s and2265.3/s**, with21.83% and43.37% final-window admission rejection. This is an observed overloaded plateau around2.3k/s under these conditions, not a maximum loss-free sustainable capacity.
- PG candidate also rejects during every second at3600/s and4800/s. Final10 completion rates are **2738.8/s and2697.4/s**, with23.90% and43.80% final-window rejection. At3600/s, however, the first two10-second blocks are only2216.3/s and2213.5/s. The whole-window2389.9/s obscures that transition; its cause is not established by these counters.
- SQLite Dapper still completes3992.4/s in the final10 seconds at4000/s, with rejections in only2 of those seconds. PG Dapper completes4770.4/s at4800/s with3 rejecting seconds. No sustained flat Dapper plateau has been located. A nonzero rejection count alone does not establish saturation.

## Non-monotonic observations and complete rejection distribution

PG Dapper1200/s rejects177 requests only in seconds8,10 and17; its final10 seconds reject none. The subsequent2400/s cell has zero rejections throughout. SQLite Dapper2000/s rejects101 only in second9, then its final10 seconds follow2000/s without rejection. At3000/s it rejects579, and at4000/s554, while completion follows the raised offer. These original counts are preserved; no smoothing or forced monotonic fit was applied.

Below are all nonzero `second:rejected` bins; all omitted offered-second bins are zero. `per-second.json` retains every bin, including zeros and drain bins, with planned/sent/started/success/error/row counters. The fixed final10 interval and nonzero rejection bins are also embedded in `summary.json`.

- **sqlite-rate-1000-candidate**: none.
- **sqlite-rate-1000-dapper**: none.
- **sqlite-rate-2000-dapper**: 9:101.
- **sqlite-rate-2000-candidate**: 2:1, 3:7, 8:79, 9:111, 12:116, 13:6, 21:14, 22:44, 24:131, 29:92.
- **sqlite-rate-3000-candidate**: 0:711, 1:904, 2:898, 3:691, 4:824, 5:734, 6:754, 7:543, 8:809, 9:699, 10:814, 11:690, 12:538, 13:648, 14:752, 15:891, 16:534, 17:500, 18:575, 19:465, 20:571, 21:755, 22:501, 23:645, 24:802, 25:562, 26:786, 27:477, 28:547, 29:903.
- **sqlite-rate-3000-dapper**: 0:94, 8:195, 9:70, 18:181, 29:39.
- **sqlite-rate-4000-dapper**: 15:12, 19:453, 23:80, 24:9.
- **sqlite-rate-4000-candidate**: 0:2286, 1:1960, 2:1816, 3:1864, 4:1715, 5:1832, 6:1803, 7:1848, 8:1809, 9:1783, 10:1714, 11:1734, 12:1752, 13:1907, 14:1736, 15:1991, 16:1846, 17:1894, 18:1794, 19:1724, 20:2036, 21:1813, 22:1839, 23:1612, 24:1506, 25:1865, 26:1587, 27:1569, 28:1782, 29:1740.
- **postgresql-rate-1200-candidate**: 6:50.
- **postgresql-rate-1200-dapper**: 8:96, 10:55, 17:26.
- **postgresql-rate-2400-dapper**: none.
- **postgresql-rate-2400-candidate**: 13:24, 14:33, 15:115, 16:7, 18:65, 20:24, 23:8, 24:184, 28:22, 29:259.
- **postgresql-rate-3600-candidate**: 0:844, 1:1022, 2:976, 3:1037, 4:945, 5:1120, 6:1396, 7:2263, 8:2006, 9:2156, 10:1739, 11:1712, 12:1850, 13:1780, 14:2032, 15:1137, 16:1074, 17:901, 18:891, 19:760, 20:1023, 21:810, 22:889, 23:715, 24:976, 25:783, 26:932, 27:813, 28:906, 29:756.
- **postgresql-rate-3600-dapper**: 11:109, 28:7.
- **postgresql-rate-4800-dapper**: 0:30, 3:398, 5:42, 6:27, 9:5, 13:777, 14:22, 15:7, 16:512, 17:53, 20:260, 21:12, 29:22.
- **postgresql-rate-4800-candidate**: 0:2294, 1:2443, 2:2409, 3:1908, 4:2114, 5:2200, 6:2096, 7:1790, 8:2043, 9:2162, 10:2274, 11:2423, 12:2105, 13:2003, 14:2212, 15:2064, 16:2138, 17:1949, 18:2044, 19:2150, 20:2303, 21:2346, 22:1993, 23:1918, 24:2134, 25:2110, 26:2110, 27:2067, 28:1994, 29:2051.

## Client CPU, allocations, memory and GC

| Cell | Client CPU µs/success | Managed B/success | Peak / idle RSS MiB | GC0 /1 /2 | Process GC pause ms |
|---|---:|---:|---|---|---:|
| sqlite-rate-1000-candidate | 1998.393 | 20701.575 | 43.727 / 38.906 | 199 / 39 / 2 | 214.999 |
| sqlite-rate-1000-dapper | 1317.569 | 7536.279 | 29.949 / 29.820 | 107 / 3 / 1 | 93.051 |
| sqlite-rate-2000-dapper | 849.704 | 7451.341 | 30.508 / 30.105 | 214 / 3 / 1 | 203.804 |
| sqlite-rate-2000-candidate | 1283.328 | 20483.105 | 45.570 / 41.773 | 410 / 79 / 2 | 408.795 |
| sqlite-rate-3000-candidate | 1126.301 | 20353.045 | 47.188 / 40.293 | 520 / 100 / 2 | 456.889 |
| sqlite-rate-3000-dapper | 639.186 | 7376.354 | 30.031 / 29.895 | 317 / 3 / 1 | 301.887 |
| sqlite-rate-4000-dapper | 535.019 | 7329.164 | 31.613 / 31.055 | 421 / 3 / 1 | 403.866 |
| sqlite-rate-4000-candidate | 1213.144 | 20453.318 | 45.125 / 41.156 | 470 / 102 / 2 | 493.736 |
| postgresql-rate-1200-candidate | 1606.211 | 21037.062 | 48.609 / 45.340 | 247 / 58 / 2 | 255.616 |
| postgresql-rate-1200-dapper | 1177.855 | 7397.414 | 38.281 / 37.012 | 73 / 20 / 2 | 125.084 |
| postgresql-rate-2400-dapper | 654.493 | 7342.890 | 38.656 / 35.945 | 116 / 69 / 2 | 175.856 |
| postgresql-rate-2400-candidate | 1095.548 | 20700.485 | 51.527 / 46.422 | 466 / 120 / 1 | 519.142 |
| postgresql-rate-3600-candidate | 1069.990 | 20790.897 | 53.195 / 47.039 | 475 / 149 / 2 | 622.646 |
| postgresql-rate-3600-dapper | 506.562 | 7192.820 | 38.391 / 37.320 | 164 / 107 / 2 | 255.298 |
| postgresql-rate-4800-dapper | 397.728 | 7026.253 | 37.789 / 36.402 | 230 / 131 / 2 | 365.839 |
| postgresql-rate-4800-candidate | 1010.010 | 20696.252 | 51.504 / 46.344 | 510 / 161 / 2 | 648.140 |

These CPU totals include the spinning arrival producer, unsuccessful admission work, harness, drivers/framework and business materialization. A changed rate or rejection share changes how those common costs amortize per successful operation. Do not label the ratios as isolated execution efficiency or subtract a theoretical producer budget. Managed allocations include DTO/string/JSON and harness work. Native allocation and framework-only managed allocation are unknown in every ordinary cell.
Peak RSS is lifetime-through-measurement-snapshot, while idle RSS is later, after tracked-owner release and five idle seconds without forced GC. GC counts and pause remain process totals. Exact bytes, total CPU/allocation and idle PSS are in summary.json. A drop in process B/op across rates does not by itself prove a new allocation optimization.

## Successful business mix under rejection

The offered business contract is the same35 cases, but accepted successful subsets differ after rejection. Each cell's35 success shares, deviations from the uniform1/35 reference and candidate/Dapper share differences are retained in summary.json. The reference is a descriptive normalization, not an inferred per-class rejection ledger.

| Cell | Min–max successful cases per class | Min–max count deviation from uniform % |
|---|---|---|
| sqlite-rate-1000-candidate | 857–858 | -0.017 to +0.100 |
| sqlite-rate-1000-dapper | 857–858 | -0.017 to +0.100 |
| sqlite-rate-2000-dapper | 1710–1712 | -0.082 to +0.035 |
| sqlite-rate-2000-candidate | 1688–1701 | -0.537 to +0.229 |
| sqlite-rate-3000-candidate | 1941–2087 | -2.219 to +5.136 |
| sqlite-rate-3000-dapper | 2553–2557 | -0.074 to +0.083 |
| sqlite-rate-4000-dapper | 3408–3415 | -0.139 to +0.066 |
| sqlite-rate-4000-candidate | 1814–1925 | -3.574 to +2.327 |
| postgresql-rate-1200-candidate | 1026–1028 | -0.111 to +0.083 |
| postgresql-rate-1200-dapper | 1022–1025 | -0.148 to +0.145 |
| postgresql-rate-2400-dapper | 2057–2058 | -0.007 to +0.042 |
| postgresql-rate-2400-candidate | 2032–2041 | -0.195 to +0.247 |
| postgresql-rate-3600-candidate | 2004–2100 | -2.252 to +2.430 |
| postgresql-rate-3600-dapper | 3080–3084 | -0.078 to +0.052 |
| postgresql-rate-4800-dapper | 4046–4062 | -0.157 to +0.238 |
| postgresql-rate-4800-candidate | 2215–2357 | -3.279 to +2.922 |

Different accepted shares can change DTO/JSON/row-allocation and driver work per success. A rate-dependent B/op decrease, or a difference affected by selective dropping of costly or cheap business, cannot be credited as a framework-allocation improvement. These counters do not identify per-class rejection causes or counterfactual costs.

## PostgreSQL server costs, separately scoped

| PG cell | Observed inner CPU s | Observed outer CPU s | Separate wait4 lifetime CPU s | Lifetime wait4 MaxRSS B |
|---|---:|---:|---:|---:|
| postgresql-rate-1200-candidate | 18.250 | 18.790 | 19.671372 | 35786752 |
| postgresql-rate-1200-dapper | 16.700 | 17.190 | 18.226284 | 35647488 |
| postgresql-rate-2400-dapper | 31.330 | 31.880 | 32.878700 | 35946496 |
| postgresql-rate-2400-candidate | 38.440 | 39.060 | 40.115568 | 35868672 |
| postgresql-rate-3600-candidate | 43.170 | 43.650 | 44.386833 | 36093952 |
| postgresql-rate-3600-dapper | 48.240 | 49.120 | 49.754612 | 35893248 |
| postgresql-rate-4800-dapper | 64.680 | 65.440 | 66.082091 | 35819520 |
| postgresql-rate-4800-candidate | 41.240 | 41.750 | 42.832137 | 35848192 |

Inner/outer values are endpoint observations of visible live/reaped processes, not exact steady CPU bounds. The separately retained wait4 lifetime includes server startup, fixture creation, warmup, idle and shutdown; its MaxRSS is that lifetime receipt field, not a summed steady PG-group RSS. These costs are not added to each other or to client CPU. Missed exited processes and non-atomic counter-transfer loss remain unknown.

## Targeted follow-ups worth doing

1. **Locate sustained Dapper overload.** A fresh bounded plan can try one higher rate per provider, for example SQLite6000/s and PG7200/s with the same queue/workers. Extend one further step only if completion still tracks offered load. Repeat the first adjacent high pair that produces dense continuing rejection and a completion plateau; the current top rates are insufficient to claim its saturation.
2. **Resolve non-monotonic transient refusal when a zero-loss envelope matters.** Reverse the PG Dapper2400/1200 pair. If the SQLite admission boundary affects a decision, similarly repeat Dapper4000/2000. Preserve per-second admission/start-delay evidence; do not treat a single burst as a precise monotonic threshold or rerun the entire16-cell grid.
3. **Check PG candidate3600's transient.** A reversed candidate4800/3600 pair with a separately identified duration such as60 seconds and the same fixed final10 summary can show whether the initial/middle slowdown recurs. Existing SQLite high cells already establish continuing rejection; broad additional repeats are unnecessary merely to show that overload.

These are suggested local follow-ups, not executed measurements. The first tested rate with any refusal is SQLite2000/s and PG1200/s for both variants, but this is only an observation in the sampled grid. It must not be presented as exact capacity. Final long cells retain their own frozen conditions, original historical rates/queue and separate acceptance credit.

## Evidence and recovery

`independent-checks.json` retains all checks and exact small-input identities. `summary.json` contains complete per-cell resources,35-case ledgers,10-second windows and comparisons. `per-second.json` retains exact event bins. `summarize_pressure.py` reproduces these reports without accessing a database or large binary.
The root's fixture retirement receipt is `experiments/recovery/fixture-retirement-review-01/actual-01.json`. No retired data directory was recreated, read as a new result, or included in this analysis. Original raw, validation, controller and configuration files remain unchanged.

Primary controller identities:

- `experiments/recovery/pressure-05/series-01.plan.json`: SHA256 `8f9046d330aa1e27320406a985665d7a5950bd151a47436f8fd5e669eaabc746` (6254 B).
- `experiments/recovery/pressure-05/series-01.plan.resume.json`: SHA256 `d3fcc1147955b0c21f2489f943bd5c50ee63f77d2d64425906279f1e7d94b957` (27627 B).
