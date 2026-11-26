# SQLite A — isolated prepare flag and measured lookaside mechanism

## Status

The single-factor product candidate is built, its selected native correctness
checks pass, and the independent engine control proves that the prepare flag
causes substantial small-object allocator traffic for the matched narrow SQL.
Ordinary Host/AOT A/B, public-allocator endpoint deltas and final acceptance are
separate pending receipts. This document gives **no CPU, latency or parity credit**
to the engine control.

The product edit began only after the measured Plan Stage 1 gate: local commit
`da20dc395ca44a0430f933aeb7a45a3ee13aa447`, with the same gate tree subsequently
recorded remotely at `d463730`, and the adopted Design strategy. No product/CI
benchmark or diagnostic path was introduced.

## Independent candidate and build identity

Candidate source is `101837c91b96473dd6e4ba44d2be449e68cd7885` on
`task/DB-Exec-Parity-01-sqlite-a`, worktree `worktrees/Korda-sqlite-a`, directly based
on clean main `7ff7b57b907b689defb880b8af62d83679608603`. Its only product diff is
the fourth argument of `sqlite3_prepare_v3` in `ProviderConnection::prepare`:
`SQLITE_PREPARE_PERSISTENT` becomes `0`. SQL bytes and length, tail pointer,
metadata validation, parameter binding, cancellation, statement lifetime and
finalization remain unchanged. No common managed scheduling or PostgreSQL change
is included in this identity.

The existing locked SQLite implementation applies PERSISTENT by disabling
lookaside during prepare. Both v2 and v3 retain saved SQL for automatic reprepare;
v2 is equivalent to v3 with public flags zero. The library source does not give
PERSISTENT a second behavior in this pinned version. The actual baseline
diagnostic machine code's flag load and engine lookaside branch are retained in
the [SQLite measured report](sqlite-measured-01.md).

| Artifact | SHA-256 / identity |
| --- | --- |
| Candidate standalone package `Korda.Database.Sqlite.0.1.0-db-exec-parity-sqlite-a.1.nupkg` | `c630ec24ac66d1cce5fac9212e63eee3f8bec7ada602369fded1886ad61b82e1` |
| Candidate native image, built/packaged/consumer-output bytes | `2add0801cb29230fd9cadfb9b9efe07159dc8fdb0922c1855045d7bf851e8237` |
| Ordinary workload AOT `consumers/sqlite-a-sqlite/korda-workload/out/DbPerf.Korda` | `031a7d2a768d6675721ec0b86fa163d1101a3c125e38d1c2af85be00c03fb5a5` |
| Ordinary phase AOT `consumers/sqlite-a-sqlite/korda-query-phases/out/DbPerf.QueryPhases` | `63a51e7bebdf6875657aff3958cd8ab0f927d5e89dbe84184897ff69c6ab685d` |
| Source/package/generated code/ELF/debug/machine inventory | [identities.json](../builds/sqlite-a/identity-01/identities.json), SHA `3d8323d644e5f6caf6c862a018b4ce635e8011f432c553d2a585748f2367eeb6` |
| Independent direct-engine control ELF | `builds/sqlite-lookaside-01/sqlite_lookaside`, SHA `574dca0293f6f0674078dd80fd8cdf433592afc8b06383ba4cbe21dc9eec3d52` |
| Resource-control runner and raw per-operation phases | [sqlite-lookaside-01/runner.json](../measurements/sqlite-lookaside-01/runner.json), SHA `047878ccf80d510ce57e5bf8085d671f6fd44aa569301ffc9e6965d2ad6392ab` |

The two ordinary consumers were built through their unchanged external
PackageReference-only builders, with the canonical standalone package and locked
toolchain. Their actual generated C#, source/assets/commands, native image and
split `.dbg` hashes remain preserved. Both debug companions match their ELF
BuildIDs. The inventory also retains bounded disassembly of actual baseline and
candidate `ProviderConnection::prepare`; it does not infer hotness from static
machine code.

After committing the one-line diff, the required
`python3 eng/ci/impact.py origin/main --output artifacts/plan.json` selected
`linux`, `postgresql` and `sqlite`. The sole reason is the shared physical file
`native/cpp/src/provider.cpp` in `database-native`; both top-level packages retain
their separate build/pack/API/test/AOT/validation routes. No routing was narrowed
to conceal the shared-source effect. The local package plan changes only the
SQLite experiment version; the exact original impact plan/hash and that
derivation are retained under `builds/sqlite-a`.

The locked native build and CMake File API graph verification succeeded. The
SQLite preset's two existing CTest entries passed: `native.sqlite14` and
`native.selected.abi`. The fourteen-scenario fixture covers provider profile and
memory behavior, codecs, savepoints, cancellation/old tokens, early close,
pool retirement, lost commit, admission, concurrency, migrations and streaming
ownership cases. This is not a claim to have rerun the combined-provider
`native.streaming` or every managed race suite. Full selected verification and
actual ordinary business oracles remain required for the combined chosen code.
The retained log is [native-correctness.log](../builds/sqlite-a/native-correctness.log).

## Direct-engine control: what was measured

The root explicitly authorized a **counts-only** control while other candidate
builds continued. This concurrency is recorded in the runner. No CPU or elapsed
time result from that run is used. The source, build command and boundaries are
in [diagnostics/sqlite-lookaside](../diagnostics/sqlite-lookaside/README.md).

The executable links the actual ordinary baseline `libnw_sqlite_engine.a`, not a
system or newly configured engine. It opens the copied, fully closed phase
fixture and executes the exact narrow phase SQL with Int64 tenant/id parameters.
The only variable is v3 prepare flags 1 versus 0. It checks metadata before
binding, performs the complete ordered read, verifies every Id/Note/NULL, and
finalizes once. Each process warms 64 operations and records eight. Two rounds
reverse flags order for each of 1/32/100/1,000 rows: sixteen processes, 128 recorded
operations. All passed and the fixture's bytes remained unchanged.

Before engine initialization the observer copies the original
`sqlite3_mem_methods`, forwards xMalloc/xFree/xRealloc through counters, and leaves
the other functions/application data unchanged. This is the SQLite allocator's
request layer, including its own rounding; it is neither public glibc allocator
traffic nor a framework-only measurement. Connection status counters are read
with resetFlag=0. HIT/MISS counters are taken from their API high-water output;
USED records current slots and a separately labeled connection-lifetime high
water. Counter snapshots stop before JSON output.

### Repeated result

Each cell below is per operation and identical in both rounds. Full reads retain
one prepare, two binds, one finalize, RUN=1, and identical VM_STEP/REPREPARE for
both flags settings.

| Result size | PERSISTENT xMalloc calls / bytes | Flags=0 xMalloc calls / bytes | PERSISTENT xRealloc calls / bytes | Flags=0 xRealloc calls / bytes | Lookaside HIT, PERSISTENT → 0 | VM_STEP | REPREPARE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1, complete PK | 51 / 6,024 B | 0 / 0 B | 1 / 32 B | 0 / 0 B | 3 → 54 | 17 | 0 |
| 32, range | 117 / 13,016 B | 0 / 0 B | 0 / 0 B | 0 / 0 B | 3 → 120 | 207 | 1 |
| 100, range | 117 / 13,016 B | 0 / 0 B | 0 / 0 B | 0 / 0 B | 3 → 120 | 615 | 1 |
| 1,000, range | 117 / 13,016 B | 0 / 0 B | 0 / 0 B | 0 / 0 B | 3 → 120 | 6,014.5 | 1 |

MISS_SIZE and MISS_FULL deltas are zero in every recorded operation. Current
lookaside slots return to their pre-prepare value after every finalize. No
allocator failure was observed. The observed zero xMalloc/xRealloc counts with
flags zero mean requests were satisfied from already allocated lookaside slots;
they do not mean zero logical allocations, zero engine memory use, or zero Korda
framework allocation.

### Initial prepare and automatic reprepare are distinct

For every range size, PERSISTENT causes 57 xMalloc requests/6,416 B through the
initial prepare and metadata boundary. Binding introduces no additional requests.
Between binding and first row, a further 60 requests/6,600 B appear while the
statement records REPREPARE=1. There are no further xMalloc requests while reading
the remaining rows or finalizing. The phase attribution is exact; this is not an
exclusive allocation-callstack attribution of each internal recompile function.

With flags zero, initial prepare instead records 57 lookaside hits and holds 17
slots. The first-row boundary reaches 120 hits and 20 current slots. EOF returns
to 17 slots, then finalize returns to zero. The one-row PK has no automatic
reprepare: its 51 initial heap requests and one realloc become 51 initial
lookaside hits, then three execution hits. This explains why the flag's cost in
these controls is mainly query-fixed and reprepare-related, even when the result
contains 1,000 rows.

## Interpretation and limits

The controlled evidence confirms the proposed allocation mechanism: for this
locked engine and matched SQL, the single prepare flag redirects small
allocations between the engine allocator and its existing lookaside arena.
Neither SQL work, result bytes, parameter types, row order nor automatic
reprepare changes. The candidate is therefore supported as a resource
experiment, independently of the much larger batch/scheduling CPU investigation.

The 117 direct-engine requests must **not** be subtracted from the original
mixed 32-row text case's 185.039 public allocator calls: those are different SQL,
DTO/column and observation scopes. Likewise, unchanged logical work in this
control does not establish ordinary endpoint CPU improvement. The next accepted
evidence must be the root-coordinated interleaved ordinary baseline/candidate/
Dapper runs and separately instrumented public-allocator runs from the actual
standalone AOT consumers.

Wider or more concurrent statements can exhaust lookaside and fall back to the
allocator. This is an engine fallback, not a reason to assume these zero-call
numbers apply to all 35 businesses. Flags zero do not create a statement cache;
the per-query prepare/finalize lifetime remains intact. This report neither
changes the default batch size nor weakens cancellation, dynamic type, DDL,
transaction-unknown, ownership or safe-return contracts.
