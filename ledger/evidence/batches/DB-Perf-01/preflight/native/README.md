# Direct native preflight evidence

These two attempts passed minimal real SQLite and PostgreSQL correctness probes. They establish direct C++ driver availability in this session; they are not DB-Perf-01 performance, workload, zero-allocation, candidate-package, or long-run acceptance evidence.

| Attempt | Maintained or historical entry | Result | Server cleanup |
| --- | --- | --- | --- |
| [original-20261124T091747Z](original-20261124T091747Z/manifest.json) | Historical scratch prototype; exact original source and path-bound runner retained | SQLite and PostgreSQL passed | Private PostgreSQL process exited |
| [portable-run-001](portable-run-001/manifest.json) | `Korda/benchmarks/Database/native/run_probe.py` with explicit dependency paths | SQLite and PostgreSQL passed after recompilation through the portable entry | Private PostgreSQL process exited |

Each directory retains raw command logs, exact command arguments and UTC timestamps, input/executable/dependency SHA-256, source/runner/README snapshots, result receipts, and a `retained-files.sha256.json` inventory. No executable, archive, SQLite database, or PostgreSQL data directory is committed here. Executable identities and reproduction inputs remain in the manifests.

Both attempts use pinned Clang/libc++ 23.1.5, SQLite 3.51.3, and libpq/PostgreSQL 18.0. Compiler/source/patch and PostgreSQL archive/tool hashes were checked against the product lock and existing source-build receipt. The SQLite archive was reused from a prior Release build. Its existing CMake command, exact archive hash, locked amalgamation hashes, runtime source ID, and selected compile options are recorded; this is explicitly not an independent rebuild of that archive. The portable attempt automatically validates the runtime source ID and fourteen selected production compile options.

The direct clients check parameter binding, prepared-query reuse including an absent key, fully consumed results, owned Unicode values, SQL NULL, an exact monetary representation, a JSON field, commit, and rollback. SQLite statement and connection closure are checked. PostgreSQL uses nonblocking libpq with binary single-row results and drains the final result. Each attempt creates its own temporary loopback TCP server with Unix sockets disabled, then stops it.

PostgreSQL numeric is explicitly cast to text and compared with `12.34`. Therefore this probe does not establish equivalent typed binary numeric decoding or complete DTO/JSON materialization for the final workload. SQLite uses exact scaled integer money. Its memory counters cover SQLite only, not process-native allocations or RSS/PSS. Neither attempt measures concurrency, sustainable throughput, latency percentiles, CPU per operation, managed allocation, or thirty-minute effective load.

The maintained runner has no dependency on a particular prior scratch directory. Use its explicit `--clang`, `--sqlite-source`, `--sqlite-archive`, `--sqlite-build-dir`, `--postgres-prefix`, and `--output` arguments. The historical manifests intentionally preserve the absolute input paths actually used in these runs. See the [portable runner snapshot](portable-run-001/run_probe.py) and [its usage guide](portable-run-001/README.md).
