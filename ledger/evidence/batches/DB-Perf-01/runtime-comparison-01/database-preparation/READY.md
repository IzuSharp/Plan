# Local database environment ready

This directory restores SQLite3.51.3 and PostgreSQL18.0 for DB-Runtime-Compare-01. No benchmark or pressure run was executed. No system package was installed, no sudo was used, and no system service or access policy was changed.

## Usable artifacts

| Artifact | Relative path |
| --- | --- |
| SQLite shared image | `sqlite/lib/libsqlite3.so` |
| SQLite verified seed | `fixtures/seed.sqlite` |
| PostgreSQL binaries | `postgres/bin/` |
| PostgreSQL verified stopped cluster | `fixtures/pgdata/` |
| SQLite exact seed SQL | `fixtures/sqlite.sql` |
| PostgreSQL exact seed SQL | `fixtures/postgresql.sql` |
| Deterministic generator/full verifier | `fixture.py` |
| Finite PG initialization procedure | `prepare_postgres_fixture.py` |

SQLite library SHA256: `ad64754d771625bc16b482962d453341f95e4619c3c42e501c5c93b38318e738`.
Initial SQLite seed SHA256: `384c185015624e35579b95b49f03bd101af5d4936def6b611b0a588bd71da0bd`.

Copy the SQLite seed before each consumer run. Avoid mutating the common seed. For PG, start one owner with the `startCommand` argv in `fixtures/postgresql-setup-receipt.json`; the preserved tested connection is `postgresql://korda@127.0.0.1:48277/db_perf_01`. Check port availability when reusing it. Separate framework correctness checks should use separate cloned databases or fresh databases initialized with `fixtures/postgresql.sql`.

The original shared fixture cluster was stopped normally after initialization and verification. `serverStopped=true` in the setup receipt is an actual observation. No database server is intentionally left running by this task.

## Exact source and new binary identities

Both official source archive hashes match `native/dependencies.lock.json` at Korda `36bd5ba169b628ba4d61dd9fe260eaef5ff15599`. The PostgreSQL source has the exact repository libpq explicit-configuration patch, SHA256 `a6c33133d9900b5bd6460245331ad7d9a8b256786dcd1bd927b5491b52921ddd`.

The historical compiler was Clang23.1.5. The actual available compiler used here is GCC14.2.0. Engine versions, source bytes, SQLite feature macros and PG configure options are preserved; these are NEW binaries, not the original historical binaries. `historicalCompilerMatched=false` remains explicit. Every new framework must use the recorded current environment when making a same-machine comparison.

SQLite was built with `-O3 -DNDEBUG -fPIC -shared`, all product SQLite feature definitions and the Linux definitions preserved in `sqlite-build-receipt.json`. Actual `PRAGMA compile_options` includes `COMPILER=gcc-14.2.0`, and the actual loaded version/source ID are recorded. Native allocation/threading/compiler/linkage differences from historical builds are not hidden.

PG uses `--without-icu --without-readline --with-ssl=openssl`, normal configure-selected `-O2`, and exactly two make jobs. Configure attempt1 failed because bison was missing and is preserved. Bison3.8.2, Flex2.6.4 and m4 were then downloaded from official Debian metadata, hash verified and extracted only into `build-deps/`. Configure attempt2, make and local-prefix install succeeded. Raw logs, phase receipts, installed binary SHA256 identities and `pg_config --configure` are retained.

Actual OpenSSL development dependency:3.5.9; zlib:1.3.1. There is no claim of bit-identical historical ELF output.

## Verified data and configuration

Both fixtures have exactly256 customers,8192 orders,13120 order_lines and1 metadata row. Every actual stored row was compared with the original Korda Dataset.cs formulas. All columns, declared types, order, nullability, primary keys and four named index column lists were checked. SQLite integrity_check returnedok. PG and SQLite produce the same normalized full-order SHA256:

`ea625936eca3ebca21150852021fa25ef2d89065b289ca37e69c1ec30b231510`

SQLite:3.51.3, WAL, synchronousFULL, foreign_keysON, busy_timeout5000.

PG actual observed settings:18.0, UTF8 server/client encoding, C collation/ctype, fsyncON, synchronous_commitON, full_page_writesON, UTC, READ COMMITTED, max_connections64, shared_buffers128MB, jitON(default), plan_cache_modeAUTO(default). Server affinity was actually CPUs4-7.

The128MB server shared_buffers setting is the historical DB configuration. It is not a total database-process limit and is not the user's C# client memory cap. No new database memory cap was imposed.

## Evidence

- `sqlite-build-receipt.json`, `sqlite-ready-files.json`
- `fixtures/sqlite-seed-receipt.json`, `fixtures/sqlite-schema-verified.json`
- `postgres-configure-receipt.json` (retained failed first configure)
- `postgres-configure-02-receipt.json`, `postgres-build-receipt.json`, `postgres-install-receipt.json`
- `postgres-build-identity.json`
- `build-deps/download-receipt.json`
- `fixtures/postgresql-seed-receipt.json`, `fixtures/postgresql-setup-receipt.json`

The initial fixture-script version remains saved under its SHA256 filename because schema verification was strengthened after the first SQLite seed creation. Original receipts are not rewritten. The subsequent explicit schema receipt binds the strengthened script; PG uses that same strengthened version.

These are source/build/setup/correctness receipts only. No duration, throughput, latency, GC, memory-cap or pressure-test acceptance is granted by them.
