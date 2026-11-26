# Independent provider executable review

Scope: read-only inspection of the final provider-isolation source change. No build, test, benchmark, or database operation was performed by this reviewer.

## Source conclusion

The staged source correctly selects one registered database driver per executable:

- `driver_sqlite.go` requires the `sqlite` tag, imports only `github.com/mattn/go-sqlite3`, and declares `compiledProvider = "sqlite"`.
- `driver_postgresql.go` requires the `postgresql` tag, imports only `github.com/jackc/pgx/v5/stdlib`, and declares `compiledProvider = "postgresql"`.
- `worker.go` no longer imports both drivers.
- `parseOptions` rejects a `--provider` value different from the compiled provider before a database is opened.
- Result metadata records `CompiledProvider`, and the compilation description now says only the selected database driver is present.

Supplying both provider tags includes both constant declarations and fails compilation; supplying neither leaves the constant undefined and also fails compilation. Neither configuration silently produces another joint executable. These conclusions are source inspection, not newly executed negative-build tests.

The documented build commands select `sqlite,libsqlite3` for the SQLite executable and `postgresql` for PostgreSQL. The SQLite `libsqlite3` tag selects the frozen external native engine. Merely leaving the SQLite include/search-directory environment in scope for a PostgreSQL build does not import the SQLite Go driver; final binary build metadata and link dependencies remain the evidence of what was linked. The SQLite runtime's sole-image mapping check additionally rejects an accidental bundled-engine build.

No blocking configuration issue remains in this source change. The initial combined-driver five-second runs remain preparation evidence; they cannot establish the identity of the independent provider executables used for formal runs.

## Final readiness checks to apply to the new independent-bin evidence

1. Each final plan has only an initialization command (`--initialize --operations 0`) and its corresponding Go timed consumer; no prior measured Korda/Dapper command is selected.
2. The final executable hash equals the corresponding successful independent-bin preflight hash. `CompiledProvider`, build tags, linked libraries, and selected Go driver agree with the provider. Module and compiler pins remain unchanged.
3. The exact workload manifest hash is `76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2`; all 35 case identities, rows, digests, SQL/control totals, and whole-process counters pass the preflight analyzer. Five seconds receives no 30-minute credit.
4. SQLite is the sole mapped selected image, version 3.51.3, SHA-256 `2f693e43707c8174c862283185610abca5c671bbf17b6b1af7866bfbcd290282`, with WAL/FULL/foreign keys/5,000 ms timeout. PostgreSQL uses the same frozen 18.0 tool executables and verified server settings.
5. Formal requests remain SQLite C4/rate3000 then PostgreSQL C8/rate3600, each 1,800 seconds, queue64, warmup64 per worker after full verification, followed by15 seconds idle after closing resources. Client CPUs0–3, observer8, PostgreSQL4–7; Go runtime GOMAXPROCS4/GOGC100/no memory limit. Results, fixture directories, and service data paths are fresh.
6. Before the first formal cell, all build/profiling/calibration processes are stopped, host identity and usable CPUs are captured, and memory/disk capacity is sufficient. Source, executables, native identities, plans, and analysis tools remain frozen during both serial runs.

Readiness of these final identities is pending inspection of the new preflight/freeze artifacts supplied by root. This source review does not itself authorize accepting a long-run result.
