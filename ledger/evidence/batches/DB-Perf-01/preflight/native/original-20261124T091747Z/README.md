# DB-Perf-01 direct native probe

This scratch experiment establishes that direct C++20 clients built with the product's locked Clang 23.1.5 can execute real SQLite 3.51.3 and PostgreSQL/libpq 18.0 queries in the current environment. It is **not** a benchmark, campaign workload, candidate-package validation, or zero-allocation acceptance result.

Run `python3 run_probe.py` from any directory. It verifies the compiler hash and locked dependency source/patch inputs, reuses the existing Release SQLite archive and source-built libpq archives, builds two separate direct-driver executables, starts an isolated PostgreSQL TCP cluster on an ephemeral loopback port with Unix sockets disabled, executes the probes, and stops that cluster. It never calls the Korda C ABI.

The run at `attempt-20261124T091747Z` passed both providers. `manifest.json` records all command arguments, working directories, UTC times, exit codes, logs and log hashes, executable/archive/source hashes, linked runtime-library hashes, and cleanup status. Each compile/run has its own raw log. The exact C++ and Python inputs were copied into the attempt directory. `sqlite-provenance-check.json` additionally binds the runtime source ID to the locked header and checks fourteen selected production compile options; the run log records the full reported option list.

Checks cover bound writes, committed data, a prepared query reused with different keys, owned Unicode strings, SQL NULL, an exact money representation, a JSON field, fully consumed results, and state after rollback. SQLite statement and connection disposal are checked. PostgreSQL uses nonblocking libpq and binary single-row results and drains the final result. The private server process exited after a normal fast shutdown.

Limits of this evidence:

- PostgreSQL numeric is explicitly cast to text before binary delivery, then checked for the exact string `12.34`. This does not prove the final benchmark's binary numeric decoder or typed JSON materializer matches Korda.
- SQLite uses exact scaled integer money. Its JSON field extraction is an expert SQL operation, not a claim about Korda's Fluent JSON-path surface.
- The reused SQLite archive was not rebuilt by this probe. Its hash, locked source hashes, runtime version/source ID, compiler configuration provenance, and selected runtime compile options are recorded.
- SQLite's reported memory high-water and after-close values cover SQLite allocations only. They are not process-native allocation totals, RSS/PSS, or a steady-state allocation measurement.
- No throughput, latency, CPU-per-operation, managed allocation, concurrency ramp, or thirty-minute load result is asserted.
- The temporary cluster uses explicitly permitted loopback plaintext and trust authentication for this isolated local smoke test. It is not a deployment configuration or an external database.

Preserve the source files, runner, manifest, raw logs, and source-ID/compile-option check when moving the evidence into Plan. Binaries and database cluster files can remain outside Git if their SHA-256 and reproduction inputs are retained.
