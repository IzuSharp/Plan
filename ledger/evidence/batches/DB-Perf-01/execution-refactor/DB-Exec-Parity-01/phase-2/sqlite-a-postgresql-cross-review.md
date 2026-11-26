# Independent review — SQLite-A prepare flag

Reviewer: PostgreSQL execution audit agent. Reviewed source commit
`101837c91b96473dd6e4ba44d2be449e68cd7885` independently of its implementation.
Review is read-only; no new build or workload was started.

## Result

No source-level correctness blocker found for the pinned SQLite3.51.3 engine.
The one-line diff changes only the public flags argument of the existing
`sqlite3_prepare_v3` call from `SQLITE_PREPARE_PERSISTENT` to `0`.
Ordinary A/B and full selected final gates remain separate requirements.

## Checks and reasoning

The actual pinned amalgamation was read from
`worktrees/Korda-postgresql-a/artifacts/dependencies/sqlite/sqlite-amalgamation-3510300/sqlite3.c`.
In `sqlite3Prepare` (line146405), the PERSISTENT bit disables lookaside during
statement preparation. A search for all uses of that flag confirms no second
general prepare-path behavior in this locked implementation. Extension modules
have their own internal prepare calls, which this Korda diff does not change.

`sqlite3_prepare_v3` still ORs in `SQLITE_PREPARE_SAVESQL` regardless of the public
flags argument (line146659). The adjacent v2 implementation documents and
implements the same behavior as v3 with public flags zero. `sqlite3Reprepare`
reads the retained VDBE prepare flags and uses the retained SQL; removing
PERSISTENT does not remove the saved-SQL bit or disable automatic reprepare.

The same SQL pointer, exact byte length, statement output and tail output are
passed. Korda's existing empty-statement/multiple-statement-tail rejection,
column metadata/type checks, deferred binding, cancellation hook, first step,
current statement gate and finalization are untouched. Metadata remains before
statement execution. This is an allocation-policy change, not a physical
statement cache or a change to DDL invalidation semantics.

SQLite falls back to its normal allocator when lookaside cannot serve a
request. Thus the owner's zero allocator-call counts for the matched narrow
control cannot be generalized to wide/concurrent/mixed workloads. The source
change does not establish CPU or latency improvement by itself.

## Evidence reviewed and limits

The owner's `analysis/sqlite-a-lookaside-01.md` retains candidate package/native/
ELF identities, native.sqlite14 and selected ABI results, and the separate
16-process same-engine counts control. Its claims correctly distinguish engine
allocation requests from public glibc calls, metadata prepare from automatic
reprepare, and resource counts from endpoint performance. The reported full
range controls keep RUN1/REPREPARE1 and matching VM_STEP/DTO oracles while routing
117 requests/13,016 B to existing lookaside. I did not rerun those controls and
do not claim an independent runtime pass.

CI impact correctly remains both provider package groups because provider.cpp
is a registered shared source. The existing two-NuGet/AOT architecture is not
changed, and no benchmark or profiling invocation is added to CI.
