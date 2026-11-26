# DB-Exec-Parity-01 — Go as an attribution control

This is source analysis of the already measured Go comparator. It neither changes
the Go drafts nor reruns their completed long measurements. The primary benchmark
reference remains Dapper.AOT. No new Go runtime count is claimed here.

## Bound inputs

- The recorded consumer is [Korda draft #39 at d5f4f9d](https://github.com/IzuSharp/Korda/tree/d5f4f9d6616bad54a08aebb7d1aca7937b18eb93/benchmarks/db-perf/go).
- The original 35-case manifest is SHA-256 `76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2`.
- The actual `go.mod` pins Go 1.27.4, go-sqlite3 v1.14.53 and pgx v5.11.0. GitHub's tag refs resolve Go to `7b2881024c95a11ddb86663a616340aa3a88b67f` and go-sqlite3 to `93c7e0a2ec6762a38ab371755d49a2b3f4a12e67`. The files were read directly at these commits; copies are under `analysis/go-upstream/` in the task workspace.
- [Pinned go-sqlite3 implementation](https://github.com/mattn/go-sqlite3/blob/93c7e0a2ec6762a38ab371755d49a2b3f4a12e67/sqlite3.go), [pinned database/sql](https://github.com/golang/go/blob/7b2881024c95a11ddb86663a616340aa3a88b67f/src/database/sql/sql.go), and the already read [pgx implementation](https://github.com/jackc/pgx/tree/5e583fa7aabfa88b796292f849fc9d7d75ac159d) bind this analysis to the recorded dependency versions. A source-derived call count is still not a newly executed counter.
- The historical long-run result is [Plan draft #35](https://github.com/IzuSharp/Plan/pull/35): SQLite 222,218,466 steady cgo calls, 131,430,355 consumed business rows and 2,992.478 successful businesses/s. These are mixed-workload totals. They cannot be divided into a matched narrow-query FFI cost or compared directly with Korda's differently scoped FFI totals.

## Match a business query, not the aggregate crossing count

The original `text` business in the frozen manifest selects ordered `Id` and
nullable `Note` with Int64 tenant/take parameters and 32 consumed rows. The Go
worker's case 1 uses that exact provider-specific manifest SQL and argument list.
It calls `Rows.Scan(&row.Id, &row.Note)` into its handwritten `TextRow`, then feeds
the same fields to the digest. The Korda and Dapper workload consumers use their
actual generated readers and the same result oracle. This business is a useful
mapping/driver comparison. It is distinct from the phase probe's `query_phases`
table, composite-primary-key predicate, materialized List and 1/100/1000 rows;
numbers from the two fixtures are not silently combined.

| Boundary | Recorded Go SQLite source | Korda / Dapper comparison and implication |
| --- | --- | --- |
| Statement lifetime | `NewWorker` retains a public `sql.Stmt` for each read case. `SQLiteRows.Close` normally resets it; worker disposal eventually closes/finalizes it. Transaction cases use their own commands. | Korda logical Prepare is not physical statement retention. The measured Dapper generated command recycle detaches `Connection`, causing Microsoft.Data.Sqlite to finalize its statement. This is a query-fixed difference to count, not an explanation for all thousand-row growth. |
| Bind and first row | The pinned driver has `_sqlite3_bind_step_columns`: reset, clear bindings, positional bind, first step and post-step metadata/reprepare state share one cgo entry. | Do not model this driver as the older per-bind/per-column crossing implementation. Korda and Dapper must be compared at semantic stages because their first-step placement differs. |
| Subsequent rows | `_sqlite3_step_values` combines `sqlite3_step` and extraction of all current columns in one cgo entry. The Go code then reads the returned C column records. | A cgo entry is useful work on the calling goroutine's native path. There is no application-level native task, ready callback and separate managed continuation for every Go row. Runtime cgo scheduling still exists and is not measured as zero. |
| Reused native scratch | The statement owns reusable `cargs`, argument bytes and `colvals`. Capacity increases allocate explicitly; ordinary reuse does not allocate a new native column buffer for each row. | Compare Korda's actual task/Cancel/worker and buffer allocation counts and copying with this lifetime, rather than inferring them from the total crossing count. |
| Text and BLOB ownership | Native column records temporarily contain SQLite-owned pointers. `readStepResult` makes the Go-owned values before the next step/reset invalidates those pointers. | Neither Go nor Korda can expose a dangling SQLite value. Korda's canonical batch representation and later owned CLR values may incur different copies/scans; count actual bytes. |
| Cancellation | When the context has no Done channel, the pinned driver takes its direct step path. Cancellable readers install an AfterFunc observer and guard which active reader may be interrupted. | A cancellation check is not necessarily a newly allocated registration per row. Korda's actual per-advance hook and per-batch control counts need their own proof. |
| Schema change | The eager first step inspects SQLite's reprepare counter and invalidates cached column metadata. A Query-issued data modification can therefore execute before Next is called. | This cannot be copied into Korda without preserving Korda's no-execution-before-metadata/error contract. Automatic reprepare alone does not prove equivalent error order or effect timing. |
| DTO mapping | Go uses handwritten typed Scan targets and runtime placement chosen by the compiler; Dapper and Korda use actual generated readers. | No artificial Go allocation is introduced to imitate CLR objects. The historical Go heap total is not a measurement of equivalent managed DTO object counts or pure framework overhead. |

## PostgreSQL control

The recorded Go worker uses pgx through database/sql in `QueryExecModeExec`, with
statement and description caches disabled. That is the appropriate contrast for
Npgsql's phase path with MaxAutoPrepare=0, but the codecs are not identical: the
pinned pgx exec path builds text parameters and default text results; Korda uses
text parameter values and requests binary result fields. The protocol frame
grouping and read-buffer path can be compared independently of those conversions.
Go's zero cgo count in this provider says only that this is the Go protocol path;
it says nothing about kernel calls, SQL executions, server work or required
replies. Existing PG source audit and new wire/poll evidence own those counts.

## What the new evidence does and does not establish

DB-Exec-Parity-01's four current Native AOT profiles have measured leaf CPU IPs
inside exact warm windows. Korda's thousand-row user-space samples include a large
`RhSpinWait` fraction; Dapper SQLite's warm samples stay on one thread and do not
show that hot leaf. Both the source and this observation make total FFI count an
inadequate explanation. The new default/spin0 experiment changes only the
thread-pool semaphore spin limit, on identical current ELF files for both
implementations; it is a causal sensitivity diagnostic, not a production tuning
decision. Request/batch timelines and counts are still required to tie that
sensitivity to Korda's repeated handoffs.

No new Go run is needed merely to reproduce the already retained 222 million
crossings. A new matched Go query should be added only if these measured Korda /
Dapper stages leave a specific mechanism unresolved. Keep both Go PRs open drafts
with their original heads and auto-merge disabled.
