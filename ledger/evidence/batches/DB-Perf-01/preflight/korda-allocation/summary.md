# Korda public-package allocation baseline

This short preflight uses original candidate packages from fixed main `771bc77cbd68d3f932b99ed2497c0697bbba5f02`. It measures unoptimized behavior; there are no production changes or before/after performance claims in these results.

All figures below are process-wide managed allocation totals. Exact framework attribution remains **unproved**; no control value is subtracted. Each process warms each query/advance scenario 64 times before its 128 measured repetitions; the idle control is one separate 100 ms interval. The generated entity contains one `long`; queries return scalar values consumed into checked numeric sums without business DTO/string/list/array output inside the intervals.

Configured limits are one connection, four waiters, 128 rows / 65536 encoded bytes per batch, 1024 field bytes, 512 buffered rows and 512 query nodes. Other limits retain the fixed package's defaults. The same session is reused for the query measurements; session-open/return allocation is not inside those query numbers.

## Complete queries

Every measured query consumes 256 rows, the terminating `false`, enumerator cleanup, and dynamic-query disposal where applicable. A prepared parameterless plan is created before its measurement. The result count and checksum are checked on every query.

| Provider / independent process | Path | Raw allocated bytes | Queries | Rows | Total B/query | Total B/row | GC0 / GC1 / GC2 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [postgresql / 1](postgresql-run-1.json) | dynamic_complete | 8903792 | 128 | 32768 | 69560.875 | 271.72216796875 | 2 / 0 / 0 |
| [postgresql / 1](postgresql-run-1.json) | prepared_parameterless_complete | 7208048 | 128 | 32768 | 56312.875 | 219.97216796875 | 2 / 0 / 0 |
| [sqlite / 1](sqlite-run-1.json) | dynamic_complete | 8905064 | 128 | 32768 | 69570.8125 | 271.760986328125 | 2 / 0 / 0 |
| [sqlite / 1](sqlite-run-1.json) | prepared_parameterless_complete | 7208048 | 128 | 32768 | 56312.875 | 219.97216796875 | 2 / 0 / 0 |
| [sqlite / 2](sqlite-run-2.json) | dynamic_complete | 8903792 | 128 | 32768 | 69560.875 | 271.72216796875 | 2 / 0 / 0 |
| [sqlite / 2](sqlite-run-2.json) | prepared_parameterless_complete | 7207856 | 128 | 32768 | 56311.375 | 219.96630859375 | 2 / 0 / 0 |
| [postgresql / 2](postgresql-run-2.json) | dynamic_complete | 8903976 | 128 | 32768 | 69562.3125 | 271.727783203125 | 2 / 0 / 0 |
| [postgresql / 2](postgresql-run-2.json) | prepared_parameterless_complete | 7208048 | 128 | 32768 | 56312.875 | 219.97216796875 | 2 / 0 / 0 |
| [postgresql / 3](postgresql-run-3.json) | dynamic_complete | 8903320 | 128 | 32768 | 69557.1875 | 271.707763671875 | 2 / 0 / 0 |
| [postgresql / 3](postgresql-run-3.json) | prepared_parameterless_complete | 7208048 | 128 | 32768 | 56312.875 | 219.97216796875 | 2 / 0 / 0 |
| [sqlite / 3](sqlite-run-3.json) | dynamic_complete | 8903704 | 128 | 32768 | 69560.1875 | 271.719482421875 | 2 / 0 / 0 |
| [sqlite / 3](sqlite-run-3.json) | prepared_parameterless_complete | 7208048 | 128 | 32768 | 56312.875 | 219.97216796875 | 2 / 0 / 0 |

## Narrow windows and controls

The within-batch interval starts after the first row has arrived. Each of its 127 subsequent moves must be synchronously completed; the probe fails if that claim is false. The supplemental-fetch interval includes one fetch and the first mapped row of the next batch. Its final row count is therefore one, not 128.

| Provider / process | Interval | Windows | Sum of raw interval deltas | Min / max B per window | Rows in windows | Incomplete observations / actual thread changes |
| --- | --- | ---: | ---: | --- | ---: | --- |
| postgresql / 1 | within_first_batch | 128 | 1430528 | 11176 / 11176 | 16256 | 0 / 0 |
| postgresql / 1 | supplemental_fetch_including_first_row | 128 | 1562736 | 12128 / 17304 | 128 | 128 / 73 |
| postgresql / 1 | empty_sync_control | 128 | 0 | 0 / 0 | 16256 | 0 / 0 |
| sqlite / 1 | within_first_batch | 128 | 1430528 | 11176 / 11176 | 16256 | 0 / 0 |
| sqlite / 1 | supplemental_fetch_including_first_row | 128 | 1552384 | 12128 / 12128 | 128 | 128 / 73 |
| sqlite / 1 | empty_sync_control | 128 | 0 | 0 / 0 | 16256 | 0 / 0 |
| sqlite / 2 | within_first_batch | 128 | 1430528 | 11176 / 11176 | 16256 | 0 / 0 |
| sqlite / 2 | supplemental_fetch_including_first_row | 128 | 1551736 | 11872 / 12248 | 128 | 125 / 65 |
| sqlite / 2 | empty_sync_control | 128 | 0 | 0 / 0 | 16256 | 0 / 0 |
| postgresql / 2 | within_first_batch | 128 | 1430528 | 11176 / 11176 | 16256 | 0 / 0 |
| postgresql / 2 | supplemental_fetch_including_first_row | 128 | 1557560 | 12128 / 17304 | 128 | 128 / 52 |
| postgresql / 2 | empty_sync_control | 128 | 0 | 0 / 0 | 16256 | 0 / 0 |
| postgresql / 3 | within_first_batch | 128 | 1430528 | 11176 / 11176 | 16256 | 0 / 0 |
| postgresql / 3 | supplemental_fetch_including_first_row | 128 | 1557560 | 12128 / 17304 | 128 | 128 / 77 |
| postgresql / 3 | empty_sync_control | 128 | 0 | 0 / 0 | 16256 | 0 / 0 |
| sqlite / 3 | within_first_batch | 128 | 1430528 | 11176 / 11176 | 16256 | 0 / 0 |
| sqlite / 3 | supplemental_fetch_including_first_row | 128 | 1552384 | 12128 / 12128 | 128 | 128 / 68 |
| sqlite / 3 | empty_sync_control | 128 | 0 | 0 / 0 | 16256 | 0 / 0 |

An incomplete observation means the returned move was pending when checked; it can race with the subsequent await. A managed-thread change across the await demonstrates an actual suspension/resumption in those instances. Neither counter claims that every other move completed synchronously.

The raw within-batch values expose the current row cost without hiding query or batch costs. The separate source audit locates an unconditional `TaskCompletionSource` per move. The empty synchronous control has the same counter and advance-loop shape. A control reading is retained as evidence, not used as an estimated subtraction or a whole-framework zero-allocation claim.

| Provider / process | Empty async control total B | Source-open 100 ms idle total B | Native live owners after source close |
| --- | ---: | ---: | --- |
| postgresql / 1 | 0 | 0 | [0, 0, 0, 0, 0, 0] |
| sqlite / 1 | 0 | 0 | [0, 0, 0, 0, 0, 0] |
| sqlite / 2 | 0 | 0 | [0, 0, 0, 0, 0, 0] |
| postgresql / 2 | 0 | 0 | [0, 0, 0, 0, 0, 0] |
| postgresql / 3 | 0 | 0 | [0, 0, 0, 0, 0, 0] |
| sqlite / 3 | 0 | 0 | [0, 0, 0, 0, 0, 0] |

The native owner order is sources, sessions, operations, cursors, buffers and handle-table entries. All six must be zero. The raw JSON also records cumulative SQL dispatch/protocol counters over setup, warmup, measurement and cleanup. They are not per-window counts and do not establish physical network round trips.

## Identity and execution evidence

[Build manifest](build-manifest.json) preserves package and executable paths, SHA-256 values, exact resolved provider IDs, source inputs, SDK support package hashes and the isolated PostgreSQL command. Every process verifies the loaded provider file observed in `/proc/self/maps` against that receipt.

| Provider | Candidate package SHA-256 | Native AOT executable SHA-256 | Actually loaded native SHA-256 |
| --- | --- | --- | --- |
| postgresql | `458c115e12d65ca0719f542ea262aeb3347f5bc3269f99d5ba14f3e36c038e0f` | `dd762d02adebe83cdd85e6911ce3951f41c8d8d1b930a7a7e50988e677bf001b` | `73f725104fb1bee5fc86a9bc371e556ea8358ac3a2d774c4823185e6da8984c6` |
| sqlite | `584d46aa5b08b1e0af46a454ac9f41704c28fe502884017e856ad1b66ca53ef5` | `d5f3a27fe4b04fed2ba87f6d45b6d1c991158ccc5bce1f31d2d3e15d3518f229` | `970a8868290cec37c353bbd8e48bb7bf4ef18cfa1da9e495fc06d7eb08d71d40` |

Both candidate versions are `0.1.0-preview.3`. These are fixed-main candidate artifacts, not evidence of a new public NuGet download or post-merge release. [PostgreSQL release receipt](postgresql-release.json) and [SQLite release receipt](sqlite-release.json) preserve the source binding.

The actual SDK, compiler and server are recorded in [dotnet-info.log](dotnet-info.log), [clang-version.log](clang-version.log) and [postgres-version.log](postgres-version.log). PostgreSQL runs in the probe's own TCP-only cluster, with `-k ''`, `fsync=on`, `synchronous_commit=on` and `full_page_writes=on`; [shutdown](postgres-stop.log) completed with exit code zero. SQLite receives a distinct file for each process. Providers are interleaved, with only one probe consumer running at a time.

## Build recovery and limits

The first restore lacked two SDK support packages; the next attempt exhausted workspace storage while duplicating ILCompiler/runtime packages. The `.previous-*.log` files preserve these failures. Only this probe's reproducible duplicate support-package extractions were removed. The successful build uses a fallback view containing the six exact SDK support packages and isolated provider-specific Korda caches; no product source/project reference or launcher is involved.

Physical-host exclusivity is not established and other work may compile on the host. Elapsed ticks are diagnostic only. This report supplies no throughput ranking, CPU-memory comparison, four-way ORM comparison, tail-latency claim, transaction/high-concurrency allocation acceptance or 30-minute segment. The eight required long segments remain separate work.

Regenerate these totals with `python3 benchmarks/Database/allocations/summarize.py /absolute/path/to/this/evidence-directory`. The script verifies raw arithmetic, expected rows/checksums, synchronous-window conditions, package/binary/native hashes, independent process identities and native retirement before writing the summary.
