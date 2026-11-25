# Independent micro-ORM preflight: two real Native AOT consumers passed

This packet establishes minimum execution and mapping support for the independent
C# micro-ORM comparison candidate. It contains **no performance, zero-allocation,
concurrency, capacity, or long-duration acceptance**.

## Observed executions

| Attempt | Result | Boundary |
| --- | --- | --- |
| [Original](original/evidence/result.json) | Passed; all nine commands exited 0 | Actual first consumer source, registry downloads, compiled native library, AOT executables and database execution |
| [Portable 001](portable-001/evidence/failure.json) | Failed before build | Caller supplied a nonexistent SQLite source path; no successful query or compiler result is claimed |
| [Portable 002](portable-002/evidence/result.json) | Passed; all eleven commands exited 0 | Repository probe entry point, locked restore, seven generated Dapper call sites per provider, real AOT execution |

The portable command is implemented in Korda
`benchmarks/Database/independent-orm/run.py`. It accepts tool/source paths, rejects
incorrect pinned versions or SQLite bytes, and copies ordinary consumers into a
new directory outside the source tree. It uses no Korda project reference or Korda
package. The application-source and runner SHA-256 values are bound by the result.

The [original command records](original/evidence/commands.json) and
[portable command records](portable-002/evidence/commands.json) preserve actual
arguments, absolute paths, start/end UTC, exit codes and raw log hashes. The
`files.json` in each successful packet records exact copied evidence bytes.
Historical paths and failure records have not been rewritten to look portable.
Executables, native libraries and NuGet archives are omitted from Git; their hashes
and reproduction inputs remain in the receipts.

## Fixed candidate and successful minimum coverage

Dapper 2.1.79 with Dapper.AOT 1.1.0 runs with Npgsql 11.0.0 against PostgreSQL 18.0
and Microsoft.Data.Sqlite.Core 11.0.0 against SQLite 3.51.3. The SQLite adapter is
SQLitePCLRaw.provider.sqlite3 2.1.11 with resolved core 3.0.5. Both consumers were
published by SDK 11.0.100 for `linux-x64`; the program rejects a dynamic-code-capable
runtime. Both publish logs show native code generation.

Public generic Dapper calls perform parameterized insertion, transactional commit,
async single-row DTO materialization, complete async result enumeration, partial
update followed by rollback, and synchronous reread of the original persisted
state. Returned `long`, Unicode text, nullable text and decimal `12.25` are checked.
The table is dropped and the disposable PostgreSQL cluster is stopped. Each
provider has seven generated interceptors, retained and hashed in
[the generated-code receipt](portable-002/evidence/generated-code.json).

The SQLite C source exactly matches Korda's pinned 3.51.3 hash. Its separately
compiled shared library uses Clang 23.1.5, `-O3 -DNDEBUG`, `SQLITE_THREADSAFE=1` and
`SQLITE_ENABLE_COLUMN_METADATA`. The complete native compiler option set has
**not** been aligned with Korda's statically bundled engine; resolve that before
comparative timing. The native-library hash in these receipts identifies the
produced probe library; this probe does not claim a separately inspected live
process library map.

## Unproved capabilities and comparison rules

- `async_*` in the raw result means the corresponding API was invoked. It does not
  establish a real suspension. Microsoft.Data.Sqlite implements its async ADO.NET
  methods synchronously.
- JSON codecs, cancellation, early enumeration termination, connection pooling,
  high concurrency and the full business query set are not covered here.
- Dapper.AOT provides generated object mapping and is a micro-ORM. Npgsql or
  Microsoft.Data.Sqlite alone would be SQL-driver comparisons, not this ORM column.
- Dapper.AOT has no LINQ/Fluent SQL translator. Dynamic SQL construction must be
  charged explicitly and separated from reused-query cells.
- Do not substitute unsupported `CommandDefinition`, multi-mapping or
  `QueryMultiple` calls and assume AOT safety. This packet proves only its observed
  generic call shapes. The probe promotes known unsupported-call diagnostics to
  errors and inspects its generated source.

## Runner capability observation

The [read-only GitHub observation](runner-capabilities.json) identifies current
repository permission metadata and its active ruleset, and shows that existing
baseline jobs use GitHub-hosted `ubuntu-24.04`. It does not establish an available
self-hosted/dedicated machine. The GitHub connector rejected runner-list and
workflow-list endpoints as unsupported; no `workflow_dispatch` tool was exposed.
The [CLI observation](runner-cli-observation.json) found no authenticated `gh`
session. No workflow was dispatched, rerun, changed or labeled by this probe.

A task-specific `pull_request` label event is a documented normal Actions trigger
and could be considered separately if deliberately configured and authorized. It
has not been implemented or executed by this preflight. GitHub-hosted jobs have a
six-hour limit; a single job can therefore accommodate the requested four hours
of effective workload plus bounded setup/drain time, subject to actual availability,
resource observation and successful execution. A virtual machine is not evidence
of physically exclusive hardware.

## Primary sources

- https://github.com/DapperLib/DapperAOT/releases/tag/1.1.0
- https://github.com/DapperLib/DapperAOT/blob/1.1.0/test/Dapper.AOT.Test/ApiSurface.expected.txt
- https://www.npgsql.org/doc/compatibility.html
- https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/custom-versions
- https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/async
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request
- https://docs.github.com/en/actions/reference/limits
