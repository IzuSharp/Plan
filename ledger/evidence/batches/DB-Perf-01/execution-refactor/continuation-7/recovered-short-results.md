# Recovered command-completion short observations

These are recovered executions from 2026-11-26, independently reread during the
DB-Exec-10 continuation. They predate the current development work. The nine
serial groups completed before the previous conversation stopped; the older
continuation-6 header had not yet recorded them. This record gives them their
actual input identities. It does not rerun or relabel them as a new candidate.
Current final 1800-second credit remains **0/4**.

## Source and consumer identities

| Role | Source commit | Tree | Consumer folders below the original workspace |
| --- | --- | --- | --- |
| Previous row-scope candidate | `31693e3883f1192a34fcb9e9c49acdcca4ad321c` | `21625a56598f3811008b8e5fcb71cb5758917056` | `consumers/row-{sqlite,postgresql}-{workload,phases}` |
| Command-completion candidate | `8789a45a52cc0cc0a0b62737542d9c120b753c9b` | `c8f398ae4db2d39302335a51a6378b737409f2fb` | `consumers/command-{sqlite,postgresql}-{workload,phases}-01` |
| Separate PostgreSQL commit-proof experiment | `d2c137bf44eb0b8490c8c4f59f12f34d2df75ac2` | `9dfcb6d6b0f1c0f36c5706110ed83fb3e580a2c1` | `consumers/commit-proof-postgresql-workload-01` |
| Matched transaction reference | Actual build/generated receipts preserved | Dapper.AOT 1.1.0, Dapper 2.1.100, Npgsql 11.0.0 or Microsoft.Data.Sqlite.Core 11.0.0 | `consumers/dapper-matched-{sqlite,postgresql}-01` |

The original workspace is `/workspace/scratch/4a65d70f0fe1`. Package source comes
from its actual release receipt and nuspec, not the runner checkout. Exact nupkg,
ELF, loaded native, ordinary/diagnostic source and generated factory hashes are
in [the strict analysis](recovered-short-evidence/analysis/command-paired-03.json)
and the raw archive manifest. PostgreSQL is 18.0; the SQLite image is 3.51.3.

The published formatting follow-up `47fe650dfed5d7bba1c4d74c4a127c5d08b66082`
was not the producer of these packages. Its subsequent CI outcome is a separate
root observation. No measurement here is reassigned to that commit, a new Find
cache, or the combined next candidate. The experiment remains separately labeled;
its measurements do not by themselves select its product integration.

## Recovered executions and analysis

The retained outer series contains nine groups and 63 commands, including nine
independent fixture initializers. All commands recorded exit 0, no timeout and
no observer errors. Commands and groups were serial; their original monotonic
start/end intervals are retained. The series finished at
`2026-11-26T05:35:21.901476+00:00` (13:35:21 Asia/Shanghai).

| Group, below `measurements/` | Commands including fixture | Strict reading |
| --- | ---: | --- |
| `single-row-matched-sqlite-01` | 7 | Previous candidate and matched Dapper, valid |
| `single-row-matched-postgresql-01` | 7 | Previous candidate and matched Dapper, valid |
| `single-command-sqlite-01` | 7 | Command candidate and matched Dapper, valid |
| `single-command-postgresql-01` | 7 | Command candidate and matched Dapper, valid |
| `single-commit-proof-postgresql-01` | 7 | Separate experiment and matched Dapper, valid |
| `ffi-single-command-sqlite-01` | 4 | Instrumented ABI counts, valid after the documented analyzer correction |
| `ffi-single-command-postgresql-01` | 4 | Instrumented ABI counts, valid after the documented analyzer correction |
| `phases-command-sqlite-01` | 10 | Three routes × 1/100/1000 DTOs plus Dapper and fixture; all nine ordinary receipts valid |
| `phases-command-postgresql-01` | 10 | Same coverage; all nine ordinary receipts valid |

The normal and diagnostic groups use C1, 15 seconds, persistent sessions and
64 warmup operations per worker. They are closed-loop observations with no
external arrival rate. `numeric` requests **32 rows**, despite the historical
`single-row-*` directory name. It is not a one-row primary-key measurement.
The separate phase application binds the complete composite primary key for its
one-row case and fully checks the ordered DTO result for every row count.

The input/hash checks, successful business counts, full per-case and per-second
counters, error/row/transaction oracles and owner drain remain strict. Read the
[previous candidate analysis](recovered-short-evidence/analysis/row-before-paired-02.json),
[command ordinary/ABI analysis](recovered-short-evidence/analysis/command-paired-03.json),
[isolated PostgreSQL analysis](recovered-short-evidence/analysis/pg-experiment-02.json)
and [18-receipt phase analysis](recovered-short-evidence/analysis/phases-01.json).

## Transaction observations

Each cell is one approximately 15-second observation, with the exact effective
interval in the raw receipt. No business failures, sticky oracle failures or
retries occurred. All Korda sources, sessions, operations, cursors, buffers,
owners, pull channels and supported command-completion counters returned to zero.
Dapper reports its own application connections returned to zero, without
invented Korda-internal counters.

| Provider / case | Previous Korda completed | Command Korda completed | Command-group Dapper completed | Command Korda service p50 / p95 / p99, μs |
| --- | ---: | ---: | ---: | --- |
| SQLite, numeric 32 rows | 82,473 | 79,225 | 790,386 | 178.176 / 292.864 / 432.128 |
| SQLite, rollback | 2,260 | 11,695 | 204,857 | 1,212.416 / 1,671.168 / 3,080.192 |
| SQLite, commit | 1,893 | 8,130 | 48,923 | 1,761.280 / 2,408.448 / 4,046.848 |
| PostgreSQL, numeric 32 rows | 47,762 | 45,858 | 125,302 | 307.200 / 471.040 / 700.416 |
| PostgreSQL, rollback | 2,947 | 6,784 | 23,727 | 2,146.304 / 2,818.048 / 4,259.840 |
| PostgreSQL, commit | 2,197 | 5,252 | 13,189 | 2,768.896 / 3,604.480 / 5,341.184 |

These data support a short-observation improvement in transaction completion,
with substantial remaining Dapper gaps. Numeric throughput did not improve in
these pairs. The phase results below are mixed, so no universal query speedup is
claimed. Tail values are raw histogram upper bounds; no trimming was applied.

Command-group total managed bytes per successful operation were 2,747.31,
61,794.78 and 65,306.95 on SQLite (numeric, rollback, commit), and 2,755.73,
62,099.84 and 65,492.86 on PostgreSQL. These are process-wide business,
framework/provider and harness totals. Their raw allocated endpoints and
process-wide GC deltas are retained. They are not framework-only bytes, and
neither a zero-allocation nor a zero-GC claim follows.

The separate PostgreSQL commit-proof sample completed 44,431 numeric, 7,223
rollback and 5,478 commit operations. Commit p50/p95/p99 were
2,686.976 / 3,375.104 / 4,554.752 μs. Its approximately 4.3% higher commit count
than the preceding command sample is not isolated causal evidence: the rollback
and numeric observations also changed. Its source review and any final combined
candidate measurements remain separate.

## One-row and DTO phase observations

Each route retains three windows of 256 successful fully consumed queries.
The following values are median sums of construction, submit-to-first-row,
remaining read and release. They exclude verification outside those four phase
boundaries; they are not a mixed-load throughput or service-latency result.

| Provider / rows | Fluent previous → command, μs | Prepared previous → command, μs | Host SQL previous → command, μs | Dapper reference, μs |
| --- | ---: | ---: | ---: | ---: |
| SQLite / 1 | 221.519 → 235.305 | 129.673 → 147.049 | 155.341 → 185.696 | 6.871 |
| SQLite / 100 | 453.995 → 435.969 | 330.661 → 322.425 | 391.758 → 366.185 | 47.080 |
| SQLite / 1000 | 1,927.682 → 1,861.566 | 1,669.014 → 1,730.609 | 1,778.296 → 1,728.072 | 372.454 |
| PostgreSQL / 1 | 392.784 → 356.390 | 250.969 → 235.887 | 312.150 → 269.651 | 96.404 |
| PostgreSQL / 100 | 550.470 → 663.986 | 505.542 → 528.103 | 550.419 → 582.302 | 185.025 |
| PostgreSQL / 1000 | 2,598.164 → 2,527.873 | 2,466.880 → 2,481.193 | 2,632.937 → 2,495.228 | 463.630 |

The phase report also preserves actual first executions, preparation, individual
phase p50/p95/p99, per-window CPU/RSS/allocation/GC, SQL execution counts and
protocol submissions. Protocol submissions are not physical round trips.
Ordinary query phases are unchanged by a transaction-only completion boundary;
the mixed direction of these short samples is retained as observed variation,
not explained away or replaced by a best trial.

## Analyzer failure and correction

The first actual recovery analysis exited 1. It correctly accepted the two
ordinary groups, but rejected the transaction ABI structures because its source
assumed a mandatory child-close command after every completed transaction.
[Original analyzer/result bytes](recovered-short-evidence/failed-analysis-01/receipt.json)
are retained. This was a read-only analysis failure, not a new product failure.

At the measured `8789a45` source, `CloseController.Request` first reads
`NativeHost.Snapshot(owner).Cleanup`. If `LocalResourcesReleased` is already true,
it releases the owner without calling `CloseOwner`. Otherwise it issues and
awaits one child close. The valid direct-completion structure is therefore:

- rollback: begin + mutation + finish = 3 mandatory commands, plus 0..1 close;
- commit: begin + two mutations + finish = 4 mandatory commands, plus 0..1 close;
- numeric: no command-completion request;
- command requests and typed takes must be equal, with every return OK;
- command error-take/cancel and **all** generic-operation calls must be zero;
- ordinary business, error, identity and final-owner predicates remain unchanged.

The extra count is inferred from aggregate ABI counters. Those counters do not
identify individual command kinds; they cannot independently prove that each
extra request was a close. The source branch and retained command-boundary tests
supply the distinct semantic evidence. The report names the inference explicitly.

The first finite negative-control execution exposed a second analyzer issue:
one generic retirement Pending-only attempt with zero starts satisfied the old
return-conservation equation. That exact failed control and analyzer bytes are
[retained](recovered-short-evidence/failed-controls-01/receipt.json). The corrected
direct path now requires zero calls for every `nw_db_operation_*` entry.
All 146 finite offline controls then passed, including absent/partial/all close,
missing mandatory work, extra close, mismatched take, non-OK status, unexpected
error/cancel/generic calls, every owner leak, business error and sticky oracle
failure. They mutate only in-memory copies of real JSON; no workload runs and
no raw evidence changes. See [the control receipt](recovered-short-evidence/analysis/analyzer-controls-03.json).

An independent reviewer reran those 146 controls and supplied another 186
controls, covering request/take skew, Pending replacing OK, unexplained status
returns, the complete generic-operation inventory and malformed counter vectors.
All passed on final analyzer SHA-256
`0cec15c40be5a8c1db900d884daf2bc83f9f84fc5ff930c30d9ebac38d5a5730`.
Read the [independent review and its exact input/output hashes](recovered-short-evidence/review/analyzer-review.md).
The review also corrected the displayed expected range for a rejected direct
transaction close; rejection logic and successful observations did not change.
The preceding analyzer bytes remain in `tools/versions/`, and preceding analysis
outputs remain unchanged; fresh numbered analyses bind the final analyzer.

## Recovery and remaining work

The deterministic archive stores original raw JSON/JSONL/stdout, plans and outer
logs; exact source/build/generated-factory and asset identities; the isolated
experiment delta; successful and failed analyses; and the analysis tools. It
omits ELF/NuGet/tool binary bytes and database files while retaining their
verified hashes and package metadata. Its manifest explicitly limits later
reproduction: recovering the original inputs is different from creating a new
build with a new identity.

The [raw recovery archive](recovered-short-evidence/recovered-short-01.tar.gz)
contains 1,272 members and is 3,071,416 bytes. Its SHA-256 is
`f7bda31ba88bc275df91cfd4c5f50109278e24a430f451e235f05f6cf4c57bcd`.
Two deterministic encodings were byte-identical, every member passed readback,
and all source hashes were rechecked after collection. The
[external manifest](recovered-short-evidence/recovered-short-01.manifest.json)
records every member hash, bound binary exclusion, original source path and all
63 nonoverlapping command intervals. No original observation was overwritten.

Matched Dapper business SQL and parameter types are bound to actual generated
factories, including the Find limit. Driver transaction controls retain their
own semantics. A generated source match is not a captured runtime wire trace.
Host affinity/noise/cgroup observations retain their original limitations; no
exclusive physical host or invisible quota is invented. Ordinary timings and
instrumented ABI-only observations remain separate.

Next work is the selected Find/driver refactor and public-package validation,
followed by final-source concurrency/rate calibration, same-condition before
comparison, and four serial candidate/Dapper 1800-second intervals. None of
those obligations is satisfied by this recovered C1 single-case record.
