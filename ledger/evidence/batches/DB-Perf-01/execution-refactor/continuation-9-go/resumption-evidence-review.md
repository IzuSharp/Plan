# Go comparison: evidence review after resumption

Reviewed at 2026-11-26 14:37:42 UTC. Result: **PASS**.

This review reread the completed SQLite and PostgreSQL Go measurements after the
conversation resumed. It did not run a database, a benchmark, a build, a unit test,
or either existing result-verification script. Independent Python calculations
read the raw JSON, counters, histograms, input files, Git blobs and archive
members. The original measurements and source files were not modified.

## Evidence checked

The original evidence root was
`/workspace/scratch/166b48a091b9/go-comparison-01`.

- Raw results: `measurements/sqlite-final-01/go-c4.json` and
  `measurements/postgresql-final-01/go-c8.json`, with their command receipts.
- All **38 frozen files** matched their recorded lengths and SHA-256 hashes.
- All **31 analysis input references** matched their SHA-256 hashes: 13 SQLite
  references and 18 PostgreSQL references. References are counted per analysis;
  shared input files are not represented as 31 distinct physical files.
- All **11 runtime/module/assembly source blobs** matched measured build commit
  `94eb3a7675a44e30c6f9ed6c7a7edda987fe36db`.
- The local final source tree matched recorded published tree
  `f8744d7735e47552c657d3b18ad5cd9e39946db9` for Korda record commit
  `d5f4f9d6616bad54a08aebb7d1aca7937b18eb93`.
- Both providers' **35 ordered cases** reconciled their success, row and
  business SQL/control counts with the frozen workload, including the aggregate
  expected digest XOR.
- Planned, attempted, admitted, started, completed, successful and rejected
  counters reconciled. Every one of the **1,800 offered seconds** had the exact
  planned arrival count and successful business progress. The complete 1,802
  element second arrays reconciled with aggregate counts.
- All four histogram sample counts reconciled with completed successes. p50,
  p95 and p99 were recalculated directly from cumulative histogram bins.
- Monotonic deadlines and drain times, throughput, TotalAlloc and GC deltas,
  client user/system CPU deltas, and absence of forced GC during work and idle
  were checked against raw boundaries.
- Both commands exited 0 without timeout or observer error. Actual post-close
  application connection arrays were four zeroes and eight zeroes respectively.

## Recalculated outcomes

| Observation | SQLite | PostgreSQL |
| --- | ---: | ---: |
| Offered seconds | 1,800 | 1,800 |
| Through-drain seconds | 1,800.000112125 | 1,800.001636491 |
| Planned arrivals | 5,400,000 | 6,480,000 |
| Successful operations | 5,386,460 | 6,468,551 |
| Rejected arrivals | 13,540 | 11,449 |
| Successful operations/s | 2,992.477591371 | 3,593.636177248 |
| Business / oracle failures / retries | 0 / 0 / 0 | 0 / 0 / 0 |
| Scheduled p50 / p95 / p99, ms upper | 0.252928 / 2.146304 / 6.586368 | 0.407552 / 2.867200 / 5.898240 |
| Service p50 / p95 / p99, ms upper | 0.104448 / 1.425408 / 3.440640 | 0.305152 / 2.457600 / 4.063232 |
| Client steady CPU seconds | 2,998.755182 | 2,515.403490 |
| Consumed business rows | 131,430,355 | 157,833,343 |
| Business SQL/control calls | 8,771,576 | 10,533,858 |
| Expected / observed digest XOR | `755849b7578d6975` | `9bb99dba0f17ed2a` |
| Go TotalAlloc delta, bytes | 16,912,450,224 | 26,729,703,808 |
| Go GC cycle delta | 9,186 | 10,112 |

## Archive readback

The local Go archive at
`/workspace/scratch/166b48a091b9/go-final-evidence-01/evidence.tar.gz` was completely
read back. All **186 retained original files**, totaling **31,309,236 bytes**,
matched both the archive manifest and original source files. The archive and
manifest matched their receipt hashes:

- Archive SHA-256:
  `eac700a195dce834006a56a50df1f2934a095e15f6a2b1f66fc21a0931d9ce3d`.
- Manifest SHA-256:
  `58bfad9d3090103b803018345b2f02145db9c632d3dc97c4dac726823c3f6aa7`.

This is a local byte-integrity review. Remote publication/readback and actual
filesystem cleanup require their own receipts. The archive excludes reproducible
binaries, caches and database files and makes no binary recovery claim.

## Scope and delivery limits

The measurements remain two Go-only runs using `database/sql` and manually typed
DTO readers. Existing Korda/Dapper.AOT measurements are historical reused inputs;
none were rerun. Fixed offered-rate completion throughput is not maximum
capacity. Histogram upper bounds are not exact sampled quantiles. Go heap/GC and
CLR heap/generation counters have different semantics, and no framework-only
zero-allocation conclusion follows. PostgreSQL server lifetime CPU includes
fixture/startup/cleanup and is separate from steady client CPU. Required protocol
reply counts and framework-specific FFI counts remain uninstrumented.

The archived `RESUME.md` describes the earlier running state and is historical;
it does not authorize restarting completed cells. The current record is
**2/2 measurements complete, 0 new measurements during resumption**. Korda #39
and Plan #35 are record-only Draft PRs and must not be merged. This review does
not claim cleanup has already occurred.
