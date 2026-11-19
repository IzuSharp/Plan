# A21 database generator retention diagnostic

These are three actual, completed profiling-only diagnostics using the same
unmodified NativeWeave product and loaded binaries. They support changing the measurement
harness before final calibration. It is **not a NativeWeave product improvement,
a formal before/after cohort, or a 30-minute result**. All runs have
`formal_timing_eligible=false`; this record grants zero long-duration credit.

The [receipt](receipt.json) preserves the exact commands, Python identity,
source-file hashes, producer identities, numerical observations and hashes of
the small original receipts that were read. The three `*-profile-driver.json`
files are verbatim copies of the original command/source receipts.

## Equivalent application load, different retention

All runs used PostgreSQL 18.0, the same actual Native AOT package consumer and
exception observer, real HTTP/1, mixed cycle/page operations at 171 logical
operations/s for a planned 120 seconds, 16 external client slots, seed 20261119,
16 warmups, 16 same-process recovery operations and five seconds idle. Service
and database CPUs were 2,3; generator CPUs were 0,1. The declared criteria remained
500 ms p99, 256 MiB application RSS, zero unexpected errors and 100 ms maximum
generator dispatch lag. GC remained enabled with unchanged thresholds.

| Actual observation | Original retained payloads | Compact, full replay | Compact, streamed finalization |
| --- | ---: | ---: | ---: |
| Driver UTC start | 2026-11-19 10:14:30.045013 | 2026-11-19 10:44:45.755625 | 2026-11-19 11:38:00.985422 |
| Driver UTC finish | 2026-11-19 10:16:53.469170 | 2026-11-19 10:47:13.539686 | 2026-11-19 11:40:27.302193 |
| Successful / offered logical operations | 20,522 / 20,522 | 20,522 / 20,522 | 20,522 / 20,522 |
| Independently observed measurement commits | 10,261 | 10,261 | 10,261 |
| A21 valid / service-qualified | false / false | true / true | true / true |
| Invalid reason | generator saturation: dispatch lag | none | none |
| Scheduled-arrival p50 | 24.539996 ms | 21.466764 ms | 21.119094 ms |
| Scheduled-arrival p95 | 265.849730 ms | 57.314663 ms | 57.973577 ms |
| Scheduled-arrival p99 | 635.988469 ms | 89.080751 ms | 101.755224 ms |
| Actual dispatch span | 120.006007186 s | 120.006505820 s | 120.007444966 s |
| Observation duration | 120.047111819 s | 120.039988745 s | 120.027818004 s |
| Measurement-phase GC events | 750 | 107 | 106 |
| Measurement-phase generation-2 events | 4 | 0 | 1 |
| Largest measurement-phase GC interval | 189.579873 ms | 0.988382 ms | 25.573027 ms |
| Scheduler sampled measurement RSS maximum | 453,251,072 B | 146,100,224 B | 78,794,752 B |
| HTTP target sampled measurement RSS maximum | 152,784,896 B | 152,170,496 B | 152,498,176 B |
| Parent controller sampled measurement RSS maximum | 61,423,616 B | 60,551,168 B | 41,119,744 B |
| Application sampled measurement RSS maximum | 66,945,024 B | 46,907,392 B | 49,156,096 B |
| Application observed measurement CPU | 98.64 CPU-s | 98.41 CPU-s | 96.22 CPU-s |
| Worker lifetime RSS high water including finalization | unavailable | unavailable | 90,337,280 B |

The original generation-2 intervals were 68.557009, 189.579873, 127.447295 and
175.429638 ms; each reported zero collected and zero uncollectable objects.
Three exceeded the unchanged 100 ms dispatch-lag criterion. These are recorded
callback wall intervals, including callback overhead and possible descheduling;
they are not CPU stack samples or proof that every latency difference has one
cause. The original invalid verdict remains invalid. All logical responses and
the independent durable oracle passed in all runs; consumer/database resources
were released and the server reached Disposed.

The first compact run shared one equal page-expected graph across its 10,261 page
oracle entries before timing. During measurement, accepted result values and
nested counter dictionaries stayed in the exact raw log, with scalar identities
retained for replay. No response validation, cancellation, persistence, retry or
arrival policy changed. The post-run census records 20,522 entries and 10,262
distinct expected-object identities. The original profiler did not collect this
census, so no measured original identity count is fabricated.

## Exact product identity

Both producer receipts identify clean product commit
`ea5fa528035d025bd7a28698ee7c71194432236c`; every package repository commit in the
recorded closure agrees. The package probe receipt SHA-256 is
`36991e0498764aff50c62e259f3a8fb5a403e8d07b4bb7d89a128b643476b327`;
the observer manifest SHA-256 is
`0aeb5121fa7cc4f9ff4b86b4c24bdc4ce80991f83d1a07b45a849b68de271f62`.
The application executable was read through its actual procfs executable mapping,
and the native library mappings were hashed. All three runs match exactly:

| Actual loaded file | SHA-256 |
| --- | --- |
| NativeWeave.Reference.TaskService | `6f2bd3e2b31422393d0e9543388f238226df2e3ab8f7e67c7f6b613a00e650d3` |
| libnativeweave_server.so | `4827a6ecc76f871e0b4828f4ff6fe23a0d0a4ca1c57c5fc89a10a8e4d83ffe69` |
| libnw_database_postgresql.so | `b0510d35c2b7b633a9aade7a5d3ad9a74498b54fbe23863c770881e38442a6f3` |
| libnw_database_sqlite.so | `7254f8e490f19637701d92523c2ba08e0cbdfdbe4c5f28173d4215b5f303da8d` |

The package list and every archive hash are in the receipt. Python was exactly
3.12.14, executable SHA-256
`fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7`.
The A21 and wrapper source hashes differ as declared in the verbatim command
receipts. Existing product code was not rebuilt or substituted between these runs.

## Post-window memory and streamed readback

This first compact version still restored all result/counter graphs after the
load and serialized the complete observation with a full `json.dumps`; the DB
parent then parsed the entire file. The compact post-window phase recorded four
generation-2 collections, with a maximum interval of 416.057461 ms. That phase
label covers replay **and subsequent result construction/serialization until
`run_cell` returned**, so it does not isolate the replay helper alone.

The existing resource sampler ended before that finalization and parent parse.
Their peak RSS is **unavailable** in the first two records. A 146,889,586-byte compact
observation from only 20,522 operations exposed a source-defined long-run memory
risk: preparation also used a full generated dataset plus a complete Oracle
parse. Linear estimates are not measured peak RSS and are not used to lower the
representative application load.

The subsequent test-only change
`bf646d59c219bd1249624f752711121819b99d29` streams dataset generation and Oracle
canonicalization, validates/indexes the exact raw bytes, emits complete evidence
one bounded row at a time, and streams the parent's scalar projection. It retains
finite O(N) scalar/oracle/index/resource state. Its
[actual finite gates](../../checks/database-streaming-002/README.md) passed.
The third, fresh exclusive profile used this streamed implementation. Its actual
whole-worker lifetime high-water value was 90,337,280 bytes, read through Linux
`getrusage(RUSAGE_SELF).ru_maxrss × 1024` after finalization and before diagnostic
graph introspection. It includes preparation/load/finalization and is not a
per-phase value or the application RSS. Parent postprocessing high water remains
unavailable. The streamed measurement phase had one generation-2 event of
25.573027 ms, collecting 33 objects; it must not be described as having no
generation-2 collections. Its post-window streamed phase had 860 recorded GC
events, maximum 1.435366 ms and no generation-2 event.

The bounded reader subsequently scanned the entire completed streamed observation
and counted all 20,522 successful records with a normalized result and
`target_counters`, totaling 389,918 counter entries. No payloads were retained by
this count-only scan. The file stamp was unchanged across the scan, and the reader
source SHA matched the frozen dependency. This confirms that the scalar returned
state did not remove complete on-disk values/counters; it does not rerun the
application oracle or replace the preserved raw-log integrity checks.

The streamed worker profile SHA-256 is
`fdcf55607514e759058a04da2b78874a126b24b8dc1360b18dfdbc83a6dd5d70`.
These observations cannot reconstruct the missing old postprocessing peaks or
prove a 30-minute memory bound from a 120-second run. Fresh final compact
calibration and representative long cells remain separate acceptance gates.

Original complete directories remain at
`ROOT/perf01-evidence/profiling/before/db-generator-001` and
`ROOT/perf01-evidence/profiling/before/db-generator-compact-001`, plus the streamed
run at `ROOT/perf01-evidence/profiling/before/db-generator-streamed-001`. This repository
record persists the compact numerical/provenance receipt and verbatim command
receipts. It does not claim that the large raw files have already been published
or independently rehashed here. Only the streamed observation was reread for the
payload count check; raw-file sizes and previously recorded dataset hashes are
explicitly labeled in the receipt.
