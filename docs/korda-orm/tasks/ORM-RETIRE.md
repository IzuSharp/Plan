# ORM-RETIRE — remove only enumerated and proven-unused legacy components

Status: `planned_candidate`; deletion is not authorized by this research plan.

## Entry gate and current ownership

Start after the actual accepted/authorized CUTOVER report. Require current source
commit, switched/retained-old consumer inventory, exact new package closure and a
concrete authorized removal manifest. A documentation PR, new product build or
historical optimization approval does not satisfy this gate.

The graph initially grants only `docs/orm/migration/retirement.md`. Prepare the
maintained manifest before asking for any missing deletion authorization; the
user must be able to review real paths and impact. After authorization, update
reviewed graph write scopes to those paths. Do not infer authority from 'legacy'
or from a file being written in C++/Rust. No history rewrite, release deletion or
unrelated task cleanup is allowed.

## Fixed inventory and classification procedure

Use the read-only research baseline 36bd5ba169b628ba4d61dd9fe260eaef5ff15599 as the
starting map, then reconcile actual current files. Candidate **inspection roots**
are the following; they are not preapproved deletion globs:

| Candidate family | Roots to inspect | Retention rule |
| --- | --- | --- |
| Old Fluent/query bindings | src/Query.Fluent, Query.Native, Query.Binding, Orm.Relations | Retain any remaining consumer/API required by a supported old product |
| Old materialization/streaming/transactions | src/Data.Materialization, Data.Streaming, Data.Transactions, Data.NativeHost | Shared or retained-old callers prevent removal |
| Old driver transports | src/Data.Postgres, Data.Sqlite, Data.NativeHost/Providers | Remove only after loader/protocol/package consumers are zero |
| Native database execution/compiler | native/cpp database-specific code, native/database, native/compiler where present | Enumerate files and target/reference closure; shared interop must remain |
| Shared infrastructure | src/Korda.Core, native/interop, common CI/package utilities | Presume retained until every independent consumer is examined |
| Packaging/tests | old provider package scripts/manifests and tests exclusive to removed modules | Preserve current release/history guidance; remove only now-orphaned execution assets |
| Licenses/notices | per-component notices and THIRD_PARTY_NOTICES entries | Retain obligations for any translated/shared code or shipped native driver |

For each file, record path, current blob ID, component, incoming source/project/
runtime/package references, disposition(remove/retain/split), reason and affected
check IDs. 'No text match' alone is insufficient: inspect generated imports,
P/Invoke/native exports, build globs, package assets, reflection/configuration names
and runtime-loaded modules. Resolve references transitively until every incoming
edge originates in a removed component or an explicitly retired consumer.

A shared file needing split is a separate small reviewed refactor: extract only the
retained behavior, prove its callers, update dependencies, then remove the obsolete
portion. Do not delete the whole directory because most of it is obsolete. Include
path renames and deleted inputs in the same ownership/module impact review.

## Required maintained record

retirement.md contains candidate/cutover/acceptance pins, authorized file manifest,
retained components and reasons, exact removals, registry/package adjustments,
validation outcomes and remaining old consumers. For large manifests use an
adjacent reviewed retirement-manifest.json after adding that exact path to scope.
Its entries use the fields above and a stable `RETIRE-<number>` identity. Do not
commit raw rg output, native binaries, profiling data or source archives.

## Ordered removal algorithm

1. Verify every intended removal against current blob IDs. If the file changed
   since the reviewed manifest, recompute its impact and review the changed scope.
2. In an isolated authorized worktree, remove the enumerated obsolete sources and
   exclusively associated tests/assets using ordinary Git changes. Leave retained
   files and all published old releases accessible.
3. Remove their exact project/package/native target references and obsolete loader
   entries. Coordinate shared registry/root edits with ORM-CI; do not delete an
   existing check while a retained consumer still needs it.
4. Update the seven new packages' actual input/asset closure and notices. The new
   product must remain independent of the old compiler/executor; preserve
   Microsoft.Data.Sqlite's required SQLitePCLRaw/e_sqlite3 driver-native assets.
5. Update current documentation/entry points so they do not link deleted live files.
   Historical acceptance/design documents keep their historical commit references
   and scope; do not rewrite them to imply they described the new implementation.
6. Run affected module checks and exact package consumers selected by the existing
   runner. Run the specific database/native lanes whose closure changed. No reason
   exists to rerun unrelated long performance or frozen historical campaigns.
7. Review the removal diff against the authorized manifest and retained-reference
   inventory. Submit the authorized retirement PR and stop at its review boundary.

## Exact verification matrix

| ID | Input/check | Pass condition |
| --- | --- | --- |
| RET-01 | Current source/project/build/package reference inventory | No surviving required reference to any removed path/symbol/asset |
| RET-02 | Removed path and rename impact selection | Owning checks/dependents selected or intentionally retired with no consumers |
| RET-03 | Pure Korda.Orm exact nupkg Native AOT consumer | Runs without old native loader/query compiler/executor |
| RET-04 | PostgreSQL/MySQL exact native consumers | Use their selected mature drivers and intended native dependency closure only |
| RET-05 | SQLite exact native consumer in clean package cache | Required driver-native SQLite still loads and query/transaction cases pass |
| RET-06 | Seven package file lists and notices | No obsolete payload/duplicate Execution DLL; all remaining obligations retained |
| RET-07 | Existing retained-old/shared module checks | Still build/run, or their absence is explicitly part of the accepted cutover scope |
| RET-08 | Current Markdown/source/build links | No unintended broken reference; historical commit links remain valid |
| RET-09 | Removal manifest versus Git diff | Every deleted/edited legacy path accounted for; no unapproved broad cleanup |
| RET-10 | Prior supported release availability and rollback instructions | Historical release remains obtainable; no rewritten/deleted Git history |

If an incoming consumer or unexplained native import remains, retain that component
and return a precise blocker to CUTOVER. Completion is the reviewed bounded removal
and its verification, not deletion of every old-looking file in the repository.
