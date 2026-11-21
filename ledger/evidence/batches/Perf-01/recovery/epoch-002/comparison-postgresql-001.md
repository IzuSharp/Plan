# Perf-01: interim completed PostgreSQL comparison

Public numeric projection of the four completed current-epoch PostgreSQL fixed-load comparisons. This is an interim domain result, not final Perf-01 acceptance. An independent bounded review checked the private projection against all four completed execution/comparison pairs on CPU 8. No active-domain output, raw workload file, payload binary, target import, build or workload was read or run. No new statistical test or acceptance gate was introduced.

## Interim finding

The completed PostgreSQL evidence supports continuing the selected candidate while the remaining domains and acceptance stages proceed. The original C16 reader reports **page mean improvement**; mixed and cycle means remain **inconclusive**. No before-to-after formal regression decision appears in these PostgreSQL results. Retain adverse descriptive observations at lower concurrency; they are not converted into significance claims. These combined-version comparisons do not identify the contribution of any individual retained change. The remaining direct-Rust gap is substantial and is separate from an optimization regression.

C16 page mean is 10.346890 → 9.544302 ms, an original reader delta of −0.802588 ms (−7.756804%). Its existing 95% process-mean interval is [−1.183930, −0.306549] ms against the frozen 0.295059 ms noise band. Mixed mean is 23.365416 → 22.274810 ms (−4.667607%); the existing interval [−1.887100, −0.154409] ms does not clear the complete 0.228314 ms noise band, and the reader retains **inconclusive**. Cycle mean is 36.381532 → 35.002962 ms (−3.789204%), also **inconclusive**.

## Reading the tables

- `whole` is the real alternating cycle/page workload with a nominal 50:50 mix; odd request budgets contain one extra cycle. Cycle and page rows are conditional slices of that same workload, not separate pure-load measurements.
- Values are the original equal-weight means of independent process metrics. C16 uses three processes per role; C1/C4/C8 use one. C16 p99 is a **mean of process p99 values**, not a pooled p99 or a confidence interval. The existing bootstrap tests process means only.
- CPU seconds, CPU percentage of one core, and RSS are whole mixed-load application observations. C16 RSS here is the mean of process peak RSS values. The final report adapter instead reports the maximum of those process peaks; these two statistics must not be substituted for one another. Both the mean and maximum remain available in the companion JSON. PostgreSQL service resources and exact SQL/pool/lock waits are unavailable. No resource values are assigned to conditional cycle/page rows.
- Counts are shown per process using the original reader means; individual process counts remain integers. The companion JSON retains original arrays, availability, minima/maxima, per-process scope/resource/correctness observations and receipt hashes. It also retains the original p50/p95 values; it does not recompute percentiles. Byte/ns values are unchanged in JSON; Markdown converts to MiB/ms.
- C1/C4/C8 are descriptive and ineligible for the declared comparison. Their reader retains all six reasons: frozen-band dataset, timing and settings mismatch; rate and concurrency mismatch; fewer than three processes per cohort. C16 is the only eligible formal stratum.

## Whole mixed-load metrics

| Scene | Offered/s | Seconds/process | Role | Processes | Success/s | Mean ms | Mean process p99 ms | App CPU s | App CPU % of one core | Mean peak RSS MiB | Errors/process | Durable commits/process | Retries/process |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| c1 | 5 | 60 | before | 1 | 5.015329 | 28.623946 | 130.856826 | 4.400000 | 7.334479 | 32.171875 | 0 | 151 | 0 |
| c1 | 5 | 60 | after | 1 | 5.013972 | 27.285867 | 84.950672 | 4.660000 | 7.768532 | 32.167969 | 0 | 151 | 0 |
| c1 | 5 | 60 | direct | 1 | 5.016036 | 6.346675 | 17.644478 | 0.270000 | 0.450364 | 7.781250 | 0 | 151 | 0 |
| c1 | 5 | 60 | managed | 1 | 5.015755 | 6.897690 | 14.672961 | 0.640000 | 1.067952 | 40.261719 | 0 | 151 | 0 |
| c4 | 20 | 20 | before | 1 | 20.025951 | 22.909185 | 78.236874 | 3.170000 | 15.855506 | 33.746094 | 0 | 201 | 0 |
| c4 | 20 | 20 | after | 1 | 20.033738 | 24.822611 | 78.894790 | 3.060000 | 15.331218 | 32.554688 | 0 | 201 | 0 |
| c4 | 20 | 20 | direct | 1 | 20.042728 | 6.037746 | 14.788107 | 0.320000 | 1.600575 | 7.863281 | 0 | 201 | 0 |
| c4 | 20 | 20 | managed | 1 | 20.039423 | 6.848925 | 16.302919 | 0.790000 | 3.955286 | 40.304688 | 0 | 201 | 0 |
| c8 | 40 | 20 | before | 1 | 39.775658 | 24.174091 | 78.971562 | 5.370000 | 26.759114 | 37.238281 | 0 | 401 | 0 |
| c8 | 40 | 20 | after | 1 | 39.966777 | 25.569403 | 85.457115 | 5.180000 | 25.954767 | 33.527344 | 0 | 401 | 0 |
| c8 | 40 | 20 | direct | 1 | 40.036000 | 5.621166 | 18.929691 | 0.600000 | 3.003763 | 8.160156 | 0 | 401 | 0 |
| c8 | 40 | 20 | managed | 1 | 40.029206 | 6.796431 | 16.934886 | 1.540000 | 7.717748 | 43.093750 | 0 | 401 | 0 |
| c16 | 180 | 60 | before | 3 | 179.902331 | 23.365416 | 69.257592 | 49.630000 | 82.721849 | 44.217448 | 0 | 5401 | 0 |
| c16 | 180 | 60 | after | 3 | 179.875931 | 22.274810 | 66.407971 | 47.206667 | 78.661500 | 42.861979 | 0 | 5401 | 0 |
| c16 | 180 | 60 | direct | 3 | 179.995099 | 5.341373 | 26.945529 | 6.010000 | 10.021118 | 8.888021 | 0 | 5401 | 0 |
| c16 | 180 | 60 | managed | 3 | 179.897685 | 7.600257 | 41.485649 | 15.846667 | 26.418123 | 46.273438 | 0 | 5401 | 0 |

## Conditional cycle/page metrics

| Scene | Slice | Role | Success/s | Mean ms | Mean process p99 ms | Success/process | Errors/process |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| c1 | cycle | before | 2.515995 | 45.453157 | 141.716413 | 151 | 0 |
| c1 | cycle | after | 2.515315 | 43.154643 | 89.525443 | 151 | 0 |
| c1 | cycle | direct | 2.516350 | 9.058823 | 27.235567 | 151 | 0 |
| c1 | cycle | managed | 2.516209 | 9.756910 | 16.255773 | 151 | 0 |
| c1 | page | before | 2.499333 | 11.682540 | 35.743987 | 150 | 0 |
| c1 | page | after | 2.498657 | 11.311300 | 41.979067 | 150 | 0 |
| c1 | page | direct | 2.499686 | 3.616446 | 14.232653 | 150 | 0 |
| c1 | page | managed | 2.499546 | 4.019409 | 6.589661 | 150 | 0 |
| c4 | cycle | before | 10.037945 | 33.844804 | 81.473995 | 201 | 0 |
| c4 | cycle | after | 10.041849 | 39.222716 | 87.855581 | 201 | 0 |
| c4 | cycle | direct | 10.046355 | 8.692347 | 18.706690 | 201 | 0 |
| c4 | cycle | managed | 10.044698 | 9.867637 | 16.754540 | 201 | 0 |
| c4 | page | before | 9.988005 | 11.918887 | 37.046922 | 200 | 0 |
| c4 | page | after | 9.991889 | 10.350506 | 38.804738 | 200 | 0 |
| c4 | page | direct | 9.996373 | 3.369873 | 6.177073 | 200 | 0 |
| c4 | page | managed | 9.994725 | 3.815119 | 6.996704 | 200 | 0 |
| c8 | cycle | before | 19.912658 | 36.139127 | 87.351831 | 401 | 0 |
| c8 | cycle | after | 20.008336 | 39.366667 | 87.279006 | 401 | 0 |
| c8 | cycle | direct | 20.042991 | 7.991017 | 19.471452 | 401 | 0 |
| c8 | cycle | managed | 20.039590 | 10.015426 | 17.585009 | 401 | 0 |
| c8 | page | before | 19.863000 | 12.179144 | 41.345151 | 400 | 0 |
| c8 | page | after | 19.958440 | 11.737646 | 34.867907 | 400 | 0 |
| c8 | page | direct | 19.993009 | 3.245390 | 7.248819 | 400 | 0 |
| c8 | page | managed | 19.989616 | 3.569389 | 6.694610 | 400 | 0 |
| c16 | cycle | before | 89.959494 | 36.381532 | 80.441649 | 5401 | 0 |
| c16 | cycle | after | 89.946292 | 35.002962 | 79.255988 | 5401 | 0 |
| c16 | cycle | direct | 90.005882 | 7.656153 | 37.247755 | 5401 | 0 |
| c16 | cycle | managed | 89.957170 | 10.502860 | 59.075161 | 5401 | 0 |
| c16 | page | before | 89.942838 | 10.346890 | 31.709349 | 5400 | 0 |
| c16 | page | after | 89.929639 | 9.544302 | 29.936774 | 5400 | 0 |
| c16 | page | direct | 89.989217 | 3.026165 | 16.388734 | 5400 | 0 |
| c16 | page | managed | 89.940515 | 4.697115 | 26.279795 | 5400 | 0 |

## Original before-to-after deltas and decisions

| Scene | Scope | Mean delta ms | Mean delta % | p99 delta ms | p99 delta % | Success/s delta | Decision on process means |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| c1 | whole | -1.338079 | -4.674684 | -45.906154 | -35.081207 | -0.001357 | inconclusive; descriptive/ineligible |
| c1 | cycle | -2.298515 | -5.056887 | -52.190970 | -36.827753 | -0.000681 | inconclusive; descriptive/ineligible |
| c1 | page | -0.371240 | -3.177737 | 6.235080 | 17.443717 | -0.000676 | inconclusive; descriptive/ineligible |
| c4 | whole | 1.913427 | 8.352226 | 0.657916 | 0.840928 | 0.007787 | inconclusive; descriptive/ineligible |
| c4 | cycle | 5.377912 | 15.889919 | 6.381586 | 7.832666 | 0.003903 | inconclusive; descriptive/ineligible |
| c4 | page | -1.568380 | -13.158783 | 1.757816 | 4.744837 | 0.003884 | inconclusive; descriptive/ineligible |
| c8 | whole | 1.395312 | 5.771931 | 6.485553 | 8.212517 | 0.191119 | inconclusive; descriptive/ineligible |
| c8 | cycle | 3.227541 | 8.930876 | -0.072825 | -0.083370 | 0.095679 | inconclusive; descriptive/ineligible |
| c8 | page | -0.441497 | -3.625028 | -6.477244 | -15.666272 | 0.095440 | inconclusive; descriptive/ineligible |
| c16 | whole | -1.090606 | -4.667607 | -2.849621 | -4.114525 | -0.026400 | inconclusive |
| c16 | cycle | -1.378570 | -3.789204 | -1.185661 | -1.473939 | -0.013201 | inconclusive |
| c16 | page | -0.802588 | -7.756804 | -1.772575 | -5.590072 | -0.013199 | improvement |

## Remaining after-to-direct gap

| Scene | Scope | Mean excess ms | Mean excess % | p99 excess ms | p99 excess % | Original process-mean decision |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| c1 | whole | 20.939192 | 329.923785 | 67.306194 | 381.457553 | inconclusive; descriptive/ineligible |
| c1 | cycle | 34.095819 | 376.382425 | 62.289876 | 228.707836 | inconclusive; descriptive/ineligible |
| c1 | page | 7.694854 | 212.773884 | 27.746414 | 194.948995 | inconclusive; descriptive/ineligible |
| c4 | whole | 18.784865 | 311.123777 | 64.106683 | 433.501617 | inconclusive; descriptive/ineligible |
| c4 | cycle | 30.530369 | 351.232724 | 69.148891 | 369.647923 | inconclusive; descriptive/ineligible |
| c4 | page | 6.980634 | 207.148298 | 32.627665 | 528.205916 | inconclusive; descriptive/ineligible |
| c8 | whole | 19.948238 | 354.877241 | 66.527424 | 351.444849 | inconclusive; descriptive/ineligible |
| c8 | cycle | 31.375651 | 392.636536 | 67.807554 | 348.240871 | inconclusive; descriptive/ineligible |
| c8 | page | 8.492256 | 261.671344 | 27.619088 | 381.015004 | inconclusive; descriptive/ineligible |
| c16 | whole | 16.933437 | 317.024035 | 39.462442 | 146.452654 | regression |
| c16 | cycle | 27.346808 | 357.187312 | 42.008233 | 112.780578 | regression |
| c16 | page | 6.518137 | 215.392698 | 13.548040 | 82.666792 | regression |

## Correctness, adverse observations and limits

Every supplied process in these four completed scenes has zero mixed/cycle/page errors, zero explicit business retries, a passing independent durable oracle, and the original service-standard pass. Actual success counts per process are 301/401/801/10801 at C1/C4/C8/C16; corresponding durable measurement commits are 151/201/401/5401. NativeWeave provider-exception observers report zero. Direct/managed provider exception-code observation is unavailable and is not rewritten as zero. PostgreSQL SQLite-specific BUSY/LOCKED fields remain N/A. All 28 finite command receipts recorded by the four execution files have exit zero and retired=true: 24 application measurements and four comparison-reader commands. Independent durable-oracle totals include other declared phases; the separate durable measurement-commit counts are the business totals used here.

C4 mixed mean rose 8.352226% and cycle mean rose 15.889919%; C8 mixed mean rose 5.771931% and cycle mean rose 8.930876%. C1 page p99 rose 17.443717%, and C4 page p99 rose 4.744837%. C1 application CPU seconds rose 5.909091%. These observations remain visible; one process per role and the mismatched frozen C16 band prevent formal attribution. They do not by themselves identify a change to revert.

C16 whole-load app CPU seconds fell 4.882799% and mean peak RSS fell 3.065461% in the original resource deltas. Resource and p99 changes have no significance test in these receipts. Equal success throughput at a fixed offered rate does not establish maximum sustainable capacity. This projection gives zero 30-minute duration credit, exactly as the four source executions do; capacity and long-run acceptance are still separate.

## Provenance

Before product commit: `ea5fa528035d025bd7a28698ee7c71194432236c`. Final selected product commit: `2f40348c3db80a4fbee7a99e721b374a597b16df`. Driver/comparator checkout: `2e3995df8d86583ee9443348276ca8d918056bfc`. Design commit: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. Final binding SHA: `8f8616f2932dd1c033309e177efa63429829f9ffa2b728a182406d943efdfa8d`. Measurement source index: `6b1d1e8ec6ee80271fdbbeb1c6d13909b92ca13c7a28cbc4fd4085f98f6a4c2c`. Producer proof hashes, source-reader filename/hash pairs, loaded executable/native filename/hash pairs and per-process summary hashes are copied into [comparison-postgresql-001.json](comparison-postgresql-001.json) from the completed receipts. Absolute paths and operational maps are excluded. No payload hashes were recomputed.

| Scene | Actual execution start UTC | Actual execution end UTC | Comparison SHA-256 already recorded by execution |
| --- | --- | --- | --- |
| c1 | 2026-11-21T06:35:24.691929+00:00 | 2026-11-21T06:40:35.258443+00:00 | `cd5d2003f9e7e51db8cee7830a73f3486acc3e97796750eb532826e99f2c609a` |
| c4 | 2026-11-21T06:40:38.479631+00:00 | 2026-11-21T06:43:01.364620+00:00 | `4952943b0a367718324060ad3a7e450f23df57e37e3374669da0aec4a8123e81` |
| c8 | 2026-11-21T06:43:04.044793+00:00 | 2026-11-21T06:45:28.134856+00:00 | `e28c876bdba9340234e7b96e8917d3f463cda309552ca8b6c32fefb4c41a2899` |
| c16 | 2026-11-21T06:45:31.106203+00:00 | 2026-11-21T07:03:11.138295+00:00 | `f688b3564abb4ce64a62359ff7b032f5b7d5728234139ed6035290fc14b67493` |

The companion JSON uses an explicit field whitelist, not a redacted copy of the operational input. It preserves the original comparison SHA-256 values above, command receipt hashes, source/binary filename hashes, original decisions and per-process numeric observations. The private source projection is identified by filename and SHA-256 in JSON; the original files remain unchanged. This publication contains summary observations and provenance, not the complete resource time series or a raw-data archive; those retention records remain separate.

See [comparison-postgresql-001-review.md](comparison-postgresql-001-review.md) for the bounded independent metadata review and publication scope.
