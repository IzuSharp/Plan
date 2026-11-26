# Go comparator environment audit

Audited 2026-11-26 UTC. This report covers only the additional Go comparator. No old Korda/Dapper performance cohort has been rerun, and no benchmark has been started by the environment audit.

## Findings and scope

No `.go`, `go.mod`, or `go.sum` files were found in the three existing task roots before the new comparator work. There is no reusable Go harness there. `/usr/bin/go` is a non-toolchain program: `go version` returns `Go: Unknown option: version`; `whereis` reports no `gofmt` or `gccgo`; `dpkg-query -S /usr/bin/go` finds no package owner. No Go compiler/module cache was found in `/usr/local/go`, `/home/agent/go`, the task `tools` trees, or the inspected `/opt/codex` and primary-runtime caches.

Ordinary HTTPS access was checked with HEAD requests, without bypassing access controls. The official Go archive URL returned HTTP 200, redirected to `dl.google.com/go`, with Content-Length 70,680,823 bytes. Both pinned module `.mod` URLs on `proxy.golang.org` returned HTTP 200. This removes the initial compiler/network blocker. Root authorized an initial 600 MB budget for the task-local toolchain, modules, and build cache.

## Version pins and primary sources

| Input | Pin | Source |
| --- | --- | --- |
| Go compiler | Go 1.27.4, Linux amd64 | <https://go.dev/dl/> |
| Go archive | `go1.27.4.linux-amd64.tar.gz`, SHA-256 `7226736c2339719cda28fbf3a54d71aa63bcefe376e98cef00034268dab24840` | <https://go.dev/dl/go1.27.4.linux-amd64.tar.gz> |
| PostgreSQL Go driver | `github.com/jackc/pgx/v5 v5.11.0`, commit `5e583fa7aabfa88b796292f849fc9d7d75ac159d` | <https://github.com/jackc/pgx/tree/5e583fa7aabfa88b796292f849fc9d7d75ac159d> |
| SQLite Go driver | `github.com/mattn/go-sqlite3 v1.14.53`, commit `93c7e0a2ec6762a38ab371755d49a2b3f4a12e67` | <https://github.com/mattn/go-sqlite3/tree/93c7e0a2ec6762a38ab371755d49a2b3f4a12e67> |
| C compiler | `/usr/bin/gcc`, Debian 14.2.0-19, GCC 14.2.0 | Local `gcc --version` |
| SQLite native image | 3.51.3, same existing binary as frozen direct/Dapper comparator | Local image verified below |
| PostgreSQL service toolchain | PostgreSQL 18.0, same existing task install | Local `pg_config --version` |

Both driver tags and full commit IDs were resolved using the official repositories' Git tag-ref endpoints. GitHub `releases/latest` returned these exact versions during the audit. Pgx's pinned `go.mod` requires Go 1.25.0; go-sqlite3's pinned `go.mod` requires Go 1.21. The installed Go 1.27.4 satisfies both. Pgx stdlib explicitly exposes `database/sql`; its source documents standard PostgreSQL `$1`, `$2` positional parameters and `sql.Conn.Raw` for optional driver inspection. Sources: [pgx go.mod](https://github.com/jackc/pgx/blob/5e583fa7aabfa88b796292f849fc9d7d75ac159d/go.mod), [pgx stdlib](https://github.com/jackc/pgx/blob/5e583fa7aabfa88b796292f849fc9d7d75ac159d/stdlib/sql.go), [go-sqlite3 go.mod](https://github.com/mattn/go-sqlite3/blob/93c7e0a2ec6762a38ab371755d49a2b3f4a12e67/go.mod).

## Reusing the exact SQLite native image

Use the `libsqlite3` build tag. The pinned driver's `sqlite3_libsqlite3.go` adds `USE_LIBSQLITE3` and Linux `-lsqlite3`; its main source then includes external `<sqlite3.h>` instead of the bundled amalgamation. This preserves the engine version of the frozen campaign. The newer SQLite bundled inside the Go package is not the measurement engine. Source: [external library build selector](https://github.com/mattn/go-sqlite3/blob/93c7e0a2ec6762a38ab371755d49a2b3f4a12e67/sqlite3_libsqlite3.go), [driver C includes](https://github.com/mattn/go-sqlite3/blob/93c7e0a2ec6762a38ab371755d49a2b3f4a12e67/sqlite3.go).

- Shared image: `/workspace/scratch/4a65d70f0fe1/consumers/direct-native/libsqlite3.so`
- SHA-256: `2f693e43707c8174c862283185610abca5c671bbf17b6b1af7866bfbcd290282`
- Size: 1,917,264 bytes.
- Header: `/workspace/scratch/4a65d70f0fe1/tools/native-dependencies/sqlite/sqlite-amalgamation-3510300/sqlite3.h`
- `sqlite3_libversion()`: `3.51.3`.
- `sqlite3_sourceid()`: `2026-03-13 10:38:09 737ae4a34738ffa0c3ff7f9bb18df914dd1cad163f28fd6b6e114a344fe6d618`.
- ELF SONAME: `libsqlite3.so`; required shared objects: `libm.so.6`, `libc.so.6`.

The environment script selects that header with `CGO_CFLAGS`, that library directory with `CGO_LDFLAGS`, and that same directory as ELF runtime search path. Before any long run, verify the compiled consumer's loaded mapping and driver version in addition to the link metadata. SQLite connection pragmas, busy timeout, persistent connection ownership, SQL text, parameter types, result materialization, and transaction behavior must match the frozen workload; avoid relying on differences between driver defaults.

## PostgreSQL resources

Reuse `/workspace/scratch/4a65d70f0fe1/tools/postgres/install`, whose `pg_config --version` reports `PostgreSQL 18.0`. The install contains `initdb`, `postgres`, `pg_isready`, and `psql`. Pgx implements its own wire protocol and does not need to link libpq. Its server must still be launched with the same version, settings, affinity, fixture, and client/server separation as the frozen campaign. Use a new task output/data directory and preserve old evidence.

## Task-local setup and reproducibility

- Root: `/workspace/scratch/166b48a091b9/go-comparison-01/toolchain`.
- Compiler: `toolchain/go/bin/go`.
- Environment: `toolchain/task-go-env.sh` (source it for build/dependency operations).
- Download receipt: `toolchain/download-receipt.json`, including requested/resolved official URL, actual byte count, measured SHA-256, extraction size, install time, and archive deletion after verification.
- Module cache: `toolchain/modcache`; build cache: `toolchain/buildcache`; temporary build files: `toolchain/tmp`; GOPATH: `toolchain/gopath`.
- `GOTOOLCHAIN=local` prevents implicit alternate compiler downloads. `GOPROXY=https://proxy.golang.org` and `GOSUMDB=sum.golang.org` retain normal upstream module verification.
- The agreed `harness/go.mod` and `harness/go.sum` pin both drivers. They were written by the environment agent while the implementation agents own the Go source files. `toolchain/dependency-seed/go.mod` is an unused initial staging input; downloads ultimately ran from the agreed harness directory.
- Go's ordinary optimized `go build -tags libsqlite3` is the intended build path; the setup audit does not compile or run the benchmark.

After results and source are durably archived, the new toolchain root and its caches can be deleted with the other authorized task artifacts. Existing LLVM, CMake, and .NET raw archives are not needed by this Go+cgo setup.

## Driver mode verification

Pgx's pinned `conn.go` accepts `default_query_exec_mode=exec` and removes that option from the server runtime parameters. It selects `QueryExecModeExec`, whose query path calls `ExecParams`; it does not create and retain the driver's default statement-cache entries. This mode infers parameter types from Go values and uses text parameter encoding. Do not call PostgreSQL `PrepareContext` in the consumer when preserving the frozen no-persistent-server-prepare comparator behavior. Source: [pgx connection/execution modes](https://github.com/jackc/pgx/blob/5e583fa7aabfa88b796292f849fc9d7d75ac159d/conn.go).

The locked SQLite driver accepts `_txlock=immediate&_foreign_keys=on&_journal_mode=WAL&_synchronous=FULL&_busy_timeout=5000`. The transaction setting becomes `BEGIN IMMEDIATE`, foreign keys are enabled, and timeout is in milliseconds. Parsing `_journal_mode=WAL` initially sets synchronous mode to `NORMAL`; the later explicit `_synchronous=FULL` overrides it, so retaining `FULL` is necessary for the intended settings. SQLite prepared read statements may be reused on each pinned physical connection. Source: [locked SQLite DSN parsing](https://github.com/mattn/go-sqlite3/blob/93c7e0a2ec6762a38ab371755d49a2b3f4a12e67/sqlite3.go).

## Completed setup status

The official archive was downloaded, matched its published SHA-256, and was extracted safely. The verified archive was deleted afterward. `go version` returned `go version go1.27.4 linux/amd64`. `go mod download -json all` downloaded the pinned dependency graph; `go mod verify` returned `all modules verified`. These are dependency/integrity operations, not benchmarks or workload tests.

The setup's files at 2026-11-26 12:37 UTC were:

| Area | File bytes | Notes |
| --- | ---: | --- |
| Go toolchain | 244,338,457 | 15,659 files |
| Module cache | 69,958,739 | 13 modules in the resolved graph; 1,379 files |
| Build cache | 1,551 | No consumer compiled yet |
| Build temporary directory | 0 | Empty |
| GOPATH support data | 188 | Task-local only |
| Available filesystem space | 817,688,576 | Parent coordinates further cleanup before build/run |

Receipts are `toolchain/download-receipt.json`, `toolchain/go-env-verification.json`, `toolchain/module-downloads.jsonl`, `toolchain/module-downloads.normalized.json`, and `toolchain/source-pins.json`. The last file records the archive SHA-256s, module sums, and hashes of the Go executable and task setup files. Driver module sums are:

- Pgx v5.11.0: `h1:IzBBtyK9AHqf98cctWFifYSci2hgQR/cd56wB4p+ogg=`; module ZIP SHA-256 `ada62e95244336484f86c274e04a6845f0c494c93b69d24f2ac4181b7c58b11d`.
- go-sqlite3 v1.14.53: `h1:mnTM0owzUMrKuLo+0w51NUiB0ir2Fo7kFXlPt/l3BGs=`; module ZIP SHA-256 `a1a2f76a2109acba21d65ecb44c1de0f98257fe506737a7acf6959304dd8782c`.

Source files are still being assembled by other agents. Once they are complete, run `go mod tidy` as needed to record the actual imported graph, then freeze the final module files and binary hashes. No benchmark, calibration, profile, or performance CI operation has been run as part of this environment setup.
