# Perf-01: actual observer equivalence diagnostic 001

Both fixed-before PostgreSQL cells passed their full functional/resource audits and their original validity and service gates. Each completed 17,282 measured operations. The synchronous control did **not** reproduce a dispatch-timing failure in this 120-second pair. Threaded observation had a lower single maximum dispatch lag, but higher arrival p99, dispatch-lag p99 and sampled CPU usage. These are descriptive observations from one process per policy; there is no product-performance, noise or long-run acceptance claim. **Formal duration credit remains zero.**

All numerical tables below derive from [public-summary.json](public-summary.json). The [projection source](project_public_summary.py) reads only the already completed, hash-bound small audits/control summaries, validates a typed publication allowlist and emits [its execution receipt](projection-execution.json). It does not replay full raw observations or run a new workload.

## Fixed identities and load

- Actual measured driver: `a3ce0f6295c535b0a81de95fc0f98aa19deb259c`, full tree `eb6b61e7c159c343513f7a50359f1a6c09f8df77`.
- Before product/runtime: `ea5fa528035d025bd7a28698ee7c71194432236c`; the same precompiled package/application/native assets were loaded in both cells.
- PostgreSQL, real HTTP/1.1, typed page/business-cycle mix, 144 scheduled operations/s, concurrency 16, nominal 120 s, warmup 16, recovery 32 and idle 60 s; fresh equivalent databases. Service/database and generator each use the same declared two-CPU allocation.
- Both scheduler processes use deferred cyclic GC. Only the explicit resource-sampling policy changes from synchronous to threaded; the original driver gates remain unchanged.
- Original gates: no unexpected business errors, arrival p99 <=500 ms, dispatch lag <=100 ms and conservative application RSS <=256 MiB. Both sides met them; the prospectively permitted timing-only continuation exception was unused.

Actual loaded identities, equal on both sides:

| Artifact | SHA-256 |
|---|---|
| Native AOT TaskService application | `6f2bd3e2b31422393d0e9543388f238226df2e3ab8f7e67c7f6b613a00e650d3` |
| Server native library | `4827a6ecc76f871e0b4828f4ff6fe23a0d0a4ca1c57c5fc89a10a8e4d83ffe69` |
| PostgreSQL native library | `b0510d35c2b7b633a9aade7a5d3ad9a74498b54fbe23863c770881e38442a6f3` |
| SQLite native library present in the same application | `7254f8e490f19637701d92523c2ba08e0cbdfdbe4c5f28173d4215b5f303da8d` |

## Actual time and workload

| Policy | Driver start UTC | Driver end UTC | Driver elapsed seconds |
|---|---|---|---:|
| synchronous | 2026-11-19T22:54:00.103579+00:00 | 2026-11-19T22:57:27.450184+00:00 | 207.346649171 |
| threaded | 2026-11-19T22:57:43.363528+00:00 | 2026-11-19T23:01:11.882808+00:00 | 208.519471489 |

| Policy | Target first measured dispatch UTC | Target last measured completion UTC | A21 effective load seconds |
|---|---|---|---:|
| synchronous | 2026-11-19T22:54:06.751717+00:00 | 2026-11-19T22:56:06.808834+00:00 | 120.059631475 |
| threaded | 2026-11-19T22:57:49.908238+00:00 | 2026-11-19T22:59:49.982826+00:00 | 120.077474309 |

The UTC load columns are the target-side observed load endpoints. Effective duration is the independent A21 monotonic measurement window; the clocks have distinct observation points and are not presented as identical brackets. Driver elapsed time includes setup, warmup, recovery, idle and finalization. The whole serial supervisor ran from 2026-11-19T22:54:00.025163+00:00 to 2026-11-19T23:01:28.735570+00:00.

| Metric | Synchronous | Threaded | Threaded minus synchronous |
|---|---:|---:|---:|
| Successful operations/s | 143.945136 | 143.923747 | -0.021389 (-0.015%) |
| Arrival p50, ms | 18.558256 | 19.600267 | +1.042011 (+5.615%) |
| Arrival p95, ms | 51.693998 | 54.051182 | +2.357184 (+4.560%) |
| Arrival p99, ms | 68.575553 | 73.439022 | +4.863469 (+7.092%) |
| Maximum dispatch lag, ms | 21.823064 | 15.139320 | -6.683744 (-30.627%) |
| Dispatch-lag p99, ms | 1.641967 | 2.406749 | +0.764782 (+46.577%) |
| Mean dispatch lag, ms | 0.624895 | 0.643539 | +0.018645 (+2.984%) |
| Planned / completed / successful operations | 17,282 / 17,282 / 17,282 | 17,282 / 17,282 / 17,282 | 0 |
| Durable cycles / typed pages | 8,641 / 8,641 | 8,641 / 8,641 | 0 |
| Dispatch lags above 50 ms / above 100 ms | 0 / 0 | 0 / 0 | 0 |
| Errors / timeouts / cancellations / rejections | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 |

## Sampled resources and coverage

CPU is the process counter delta over each phase's actual CPU-observation endpoints. One-core CPU percent may exceed 100% for a process using multiple cores. RSS is the greater peak from measurement-phase samples and reads overlapping the A21 measurement window, identically applied to all four roles and both policies. These are sampled process observations, not total host CPU or a separate PostgreSQL-process CPU measurement.

| Role | CPU seconds, sync / threaded | CPU delta | One-core CPU %, sync / threaded | RSS MiB, sync / threaded | RSS delta, MiB |
|---|---:|---:|---:|---:|---:|
| application | 83.63 / 87.34 | +3.71 (+4.436%) | 69.681295 / 72.744761 | 42.898438 / 44.718750 | +1.820312 (+4.243%) |
| target | 50.22 / 52.94 | +2.72 (+5.416%) | 42.028455 / 44.519110 | 50.878906 / 52.464844 | +1.585938 (+3.117%) |
| scheduler | 10.58 / 12.29 | +1.71 (+16.163%) | 8.854246 / 10.334578 | 110.988281 / 112.160156 | +1.171875 (+1.056%) |
| controller | 1.41 / 1.42 | +0.01 (+0.709%) | 1.180005 / 1.194054 | 37.437500 / 37.171875 | -0.265625 (-0.710%) |

The target is the independent Python client/process driver; scheduler is the A21 arrival scheduler; controller owns the finite cell. CPU deltas use slightly different observed endpoint spans, listed below. The public JSON preserves exact byte counts, CPU spans, offset/overlap coverage, descriptor/socket peaks and per-phase summaries.

| Role | Measurement samples, sync / threaded | CPU bracket seconds, sync / threaded | Bracket intersection with actual load, seconds | RSS-overlap samples, sync / threaded |
|---|---:|---:|---:|---:|
| application | 2312 / 2253 | 120.017860918 / 120.063629384 | 120.017860918 / 120.062396743 | 2312 / 2252 |
| target | 120 / 119 | 119.490474529 / 118.915225412 | 119.490474529 / 118.915225412 | 120 / 119 |
| scheduler | 120 / 119 | 119.490688952 / 118.921159540 | 119.490688952 / 118.921159540 | 120 / 119 |
| controller | 120 / 119 | 119.490998560 / 118.922594808 | 119.490998560 / 118.922594808 | 120 / 119 |

All resource error counters in the retained phases are zero. The threaded application CPU bracket ends 1.233 milliseconds after the A21 window; the conservative RSS rule intentionally retains phase-labelled observations. Its 2,253 measurement-phase samples include 2,252 whose read interval intersects the window. The other roles use the same rule. Threaded application/generator rows reported zero start/end phase-label changes; this pair did not exercise an observed live phase-change span. Finite boundary tests and the source review remain separate evidence for that boundary.

| Observer | Total samples, sync / threaded | Distinct observer worker IDs recorded, sync / threaded |
|---|---:|---:|
| a21 | 8898 / 8731 | 0 / 1 |
| application | 3649 / 3576 | 0 / 13 |
| generator | 573 / 567 | 0 / 13 |

The threaded target's application and generator observers together used 13 distinct recorded worker IDs; their union contains 13. This is a count across observations, not simultaneous thread concurrency, all process threads, retained threads or proof of a leak. Identifiers themselves are excluded from this public record. Synchronous sampling produces no observer-worker-ID records. Each sampler's own intervals were serial and all sampler completion checks passed.

## Recovery, idle, GC and correctness

| Role | Synchronous idle RSS first -> last, MiB | Threaded idle RSS first -> last, MiB |
|---|---:|---:|
| application | 34.195312 -> 33.742188 | 33.386719 -> 33.062500 |
| target | 70.175781 -> 70.289062 | 71.937500 -> 73.601562 |
| scheduler | 112.042969 -> 118.972656 | 113.332031 -> 120.878906 |
| controller | 37.437500 -> 38.355469 | 37.171875 -> 38.089844 |

The actual idle intervals were 60.000252011s and 60.000242121s. The application's last idle RSS sample was below its measurement peak, while sampled generator RSS remained above startup observations. These observations do not establish long-run memory neutrality. Generator sampling ends before final A21 result replay and the scheduler-GC wrapper restoration; no continuous RSS bracket covers those final transients.

| Gate | Synchronous | Threaded |
|---|---|---|
| Actual driver / side-audit exits | 0 / 0 | 0 / 0 |
| Complete operation oracle | 17,282 / 17,282 matched | 17,282 / 17,282 matched |
| Independent persisted rows before recovery | 8,777 each: items / operations / outbox | 8,777 each: items / operations / outbox |
| Independent persisted rows before shutdown | 8,809 each: items / operations / outbox | 8,809 each: items / operations / outbox |
| Same-process recovery | 32 successful; durable oracle passed | 32 successful; durable oracle passed |
| Python scheduler GC collections in deferred scope | [0, 0, 0] | [0, 0, 0] |
| Scheduler initial / in-scope / restored automatic GC | enabled / disabled / enabled | enabled / disabled / enabled |
| Application owners, database, server and supervised cleanup | passed; no live owned process | passed; no live owned process |
| Individual side-audit checks | 84 passed | 78 passed |
| Original validity / service-standard flags | true / true | true / true |
| Formal credit | 0 seconds | 0 seconds |

The final pair audit passed all 9 checks and exited 0. Different side-audit counts reflect the actual retained phase coverage: the synchronous generator has final-phase observations; threaded shutdown does not submit a new job after stop. All present phases and sample totals were validated against their original summaries. Neither missing phases nor unobserved finalization periods are filled with invented zeroes.

The scheduler-GC scopes lasted 197.116445424s and 197.478992245s, including the complete original worker. Normal restoration passed. Managed application GC/allocation counters are unavailable in this package's recorded endpoints; they are not inferred from Python collections, CPU or RSS. This projection validates the already executed independent SQL receipts, not a new database query.

## Evidence hashes and scope

| Record | SHA-256 |
|---|---|
| Public numerical projection | `46a3d151e66fff044ea6f082a4be0a03cd6956037e1bd982b904a0491c7904f2` |
| Projection source | `f9658a3105f224c32dbcd8de2c86b731000f1b9c4d56a7a98aab5496a433da25` |
| Actual projection execution receipt | `9cf5b38b79e44700dcbfa732340cc54102eedac3992c5a40590368b652bbeb3e` |
| Actual supervisor control input | `c64debb45b30388809373695dfda3e59714571debf3db8801b4672a54c7de796` |
| Completed final audit input | `bfca614ae18a47237df7f1fdea5daed54a364cd087a12118fc3937aaedee130d` |
| Synchronous audit input | `311a8720af69a7a57e7fbf347b73e3a48fe7f7393d009104949ed56f0b8b3fca` |
| Threaded audit input | `205ec4f49539835997a1e3ec3ac732329ff6612daad4197fb0b6a1187ba2c3bb` |
| Prospective pair configuration | `2f7a7149d3f8de59a90b1cd569032bb16a203957c4807062e8a5330c6f1368e0` |
| Executed auditor source | `f8013d23a12b5e0a4acb0e2befa800a10120353729330eaad59bc7e6b76bdd43` |
| Executed supervisor source | `4a3a30d8b74c905b419ca6d71e8c059f6ea888dbbfa2b9aef58455c22e680d40` |

Only explicitly selected numbers, fixed enums, dates and hashes are published in the JSON. Full private receipts, absolute paths, process/thread identifiers, commands and raw payloads are excluded. The original evidence is unchanged. This projection does not claim that the full raw archive has been published or read back; that is a separate owner-managed evidence obligation.

This one-pair semantic/resource gate supports further investigation under a separate prospective policy freeze. It neither demonstrates a product gain nor excludes timing interference in a longer run. The 17,282-entry plan does not establish the 259,526-entry long-plan heap, prolonged allocator/GC behavior, sustained capacity, independent-process noise, direct-Rust equivalence or 30-minute acceptance. The smaller single maximum lag is insufficient to override the higher p99/CPU observations or to attribute a causal effect from one pair.
