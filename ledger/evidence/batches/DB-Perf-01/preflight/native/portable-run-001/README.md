# Direct native database preflight

This Linux x64 smoke probe checks that standalone C++20 clients built with Korda's pinned Clang can bind parameters, read and materialize real SQLite/libpq results, reuse prepared queries, commit, roll back, and close their resources. It does not call Korda's C ABI or managed APIs. It is not a throughput, latency, memory, or allocation benchmark, and it does not complete a DB-Perf-01 workload or thirty-minute segment.

## Inputs and execution

Prepare the native dependencies using the repository's `eng/cpp_toolchain.py`, `eng/postgres-tools.sh`, and CMake Release preset. See `docs/guides/cpp-native.md`. The runner takes every external artifact path explicitly and verifies the compiler, locked source files, PostgreSQL build receipt, archives, patch, runtime versions, and selected SQLite compile options. It requires Python 3, `ldd`, `readelf`, normal native link prerequisites, and an account that can run a private PostgreSQL cluster.

From the repository root, after the `linux-x64-release` build:

```sh
python3 benchmarks/Database/native/run_probe.py \
  --clang artifacts/toolchain/llvm-23.1.5/bin/clang++ \
  --sqlite-source artifacts/dependencies/sqlite/sqlite-amalgamation-3510300 \
  --sqlite-archive artifacts/cmake/linux-x64-release/libnw_sqlite_engine.a \
  --sqlite-build-dir artifacts/cmake/linux-x64-release \
  --postgres-prefix artifacts/postgres-tools/install \
  --output artifacts/db-perf-native-preflight/run-001
```

`--output` must name a new directory. `--product-root` defaults to this checkout. `--llvm-root` defaults to the selected compiler distribution. `--port 0` selects an unused ephemeral loopback port; an explicit port can be supplied. `--postgres-user` defaults to the current user and names only the newly created private cluster's database superuser.

The PostgreSQL server listens on `127.0.0.1`, uses no Unix socket, and is stopped before the runner finishes. Its local trust/plaintext configuration is limited to this temporary connectivity test. The runner does not connect to an external service or alter an existing database.

## Evidence

The output includes:

- `manifest.json`: all input paths/hashes, product commit, exact compile/run arguments, start/end times, command exits, result receipts, native runtime dependencies, and server cleanup status;
- one raw log per command, plus `postgres-server.log`;
- snapshots of this runner, the C++ source, and this README;
- separate direct SQLite and PostgreSQL ELF clients and their hashes;
- the temporary SQLite file and stopped PostgreSQL data directory.

The runner reuses an existing Release SQLite archive. It records its hash and existing CMake compile command, verifies the corresponding amalgamation source hashes, then checks the actual runtime source ID and fourteen selected production compile options. This establishes the recorded input and runtime identity, not an independent rebuild proof. PostgreSQL archives and tools are verified against the source build's `korda-postgresql-build.json`, including the compiler and explicit-configuration patch.

For a Git evidence checkpoint preserve the manifest, source/runner/README snapshots, and raw logs. Keep executable/database files outside Git while retaining their hashes and reproducible inputs. Do not edit a historical attempt in place.

## Scope limits

The smoke query checks Unicode, NULL, a JSON field, an exact monetary value, parameter binding, complete result consumption, a reused prepared statement, commit, and state after rollback. PostgreSQL uses nonblocking libpq with binary single-row results. Its numeric column is explicitly cast to text and checked against `12.34`; this does not prove the final benchmark's typed binary numeric decoder. SQLite uses scaled integer money, and its JSON field extraction is expert SQL rather than proof of a Fluent JSON-path API.

SQLite memory counters cover SQLite only. They are not process-wide native allocation counters, RSS/PSS, or a steady-state result. This program does not measure managed allocation, throughput, percentiles, CPU per operation, concurrency, or sustained load. Keep these preflight receipts separate from the four-column business workload and eight long-run acceptance records.
