# DB-Exec-02 — complete database execution-path refactor

Status: **candidate B measured; follow-up corrections published; cursor pull-channel refactor in progress; no final acceptance**. Use the [current checkpoint](current-checkpoint.md) for executed evidence and the selected next action.
Authorization date: 2026-11-26 (Asia/Shanghai). Continue the open
[Korda #37](https://github.com/IzuSharp/Korda/pull/37),
[Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and
[Plan #34](https://github.com/IzuSharp/Plan/pull/34).
This continuation belongs to the existing DB-Perf-01 batch; DB-Exec-02 identifies
its new worktrees, input freezes and evidence. The [parent plan](../plan.md) and
[handoff](../handoff-linux.md) remain the recovery entry points.

The owner requests the complete path from the database driver to C# Fluent.
Preserve public Fluent calls and behavior, Native AOT, C++ execution and the two
independent provider packages. Host internals, ABI call granularity, command and
parameter representations, batch construction, ownership adapters and mapping
are in scope. Reusing a suitable implementation, rewriting a misplaced
responsibility and deleting a replaced path are all required options. A series
of serializer micro-optimizations does not establish completion of this task.

## Fixed starting points and historical evidence

| Input | Fixed identity | Role |
| --- | --- | --- |
| Korda #37 | [f0078da720e07031bc56464995af6791c41aaae8](https://github.com/IzuSharp/Korda/commit/f0078da720e07031bc56464995af6791c41aaae8), tree `1e56f5466fa02640dcb68389f283e5c03c2c09ec` | Immediate pre-refactor implementation; includes the complete NWQC command path |
| Korda-Design #20 | [335706d1d2c76f11d4e0eaffc4a35bf404776a19](https://github.com/IzuSharp/Korda-Design/commit/335706d1d2c76f11d4e0eaffc4a35bf404776a19) | Existing query, lifetime and public behavior contracts |
| Plan #34 | [bfe4aa3f074789dfac046412eff37fe6ba58b0f7](https://github.com/IzuSharp/Plan/commit/bfe4aa3f074789dfac046412eff37fe6ba58b0f7) | Previous final local evidence and stop record |
| Earliest product baseline | `771bc77cbd68d3f932b99ed2497c0697bbba5f02` | Historical preview.3 baseline; keep separate from the immediate before implementation |

The [previous final record](../query-optimization/final-f0078da7/README.md) reports
four completed local 1800-second cells and large remaining Dapper.AOT gaps.
Those cells retain their original identities, closed-loop C8 workload and
environment limits. They do not count toward this candidate's four cells.
Ordinary Fluent allocation was about 25.31% above the recovered intermediate
input, despite cumulative reductions from the earliest baseline. Framework-wide
zero allocation was not achieved or attributed.

The previous final full numeric archive remained local-only after an upload
rejection. The current workspace has neither that archive nor the old
`/tmp/DB-Perf-01*` tool/application directories. The public pre-long and SQLite
halfway archives and final selected summaries remain available; their hashes are
not evidence that missing executables have been recovered. Rebuild the immediate
before and new candidate with matching toolchain/dependencies and the same
consumer source for this host. Preserve both unexplained aborts: the PostgreSQL
`r1-recovered` prepared -6 and SQLite B03 AOT CI `45622268417` -6. Later passes
do not prove their causes or fixes.

The final stop at the top of the old handoff supersedes its older coordinator
61233/34628 snapshots. No current branch-writer claim follows from those retained
session numbers. Recheck remote heads before every publication; if another
writer advances the same branch, reconcile its handoff before editing/pushing.

## Source pins and responsibility evidence

The actual DB-Perf-01 consumer declares Dapper 2.1.100, Dapper.AOT 1.1.0,
Npgsql 11.0.0 or Microsoft.Data.Sqlite.Core 11.0.0, and
SQLitePCLRaw.provider.sqlite3 3.0.5 in
[DbPerf.Dapper.csproj](https://github.com/IzuSharp/Korda/blob/f0078da720e07031bc56464995af6791c41aaae8/benchmarks/db-perf/managed/Dapper/DbPerf.Dapper.csproj).
Use the actual restored consumer graph/generated source in the new freeze.
The older `benchmarks/Database/campaign` lock files describe another harness and
are not substitutes for this consumer's actual restore. Native versions come
from [native/dependencies.lock.json](https://github.com/IzuSharp/Korda/blob/f0078da720e07031bc56464995af6791c41aaae8/native/dependencies.lock.json):
PostgreSQL/libpq 18.0 and SQLite 3.51.3.

| Source | Fixed source / inspected mechanism | Evidence boundary |
| --- | --- | --- |
| PostgreSQL 18.0 | [postgres.c at 3d6a8289](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/tcop/postgres.c): `exec_parse_message`, `exec_bind_message`, `exec_execute_message`, `exec_describe_statement_message` | Source reading; no local execution credit |
| libpq 18.0 | [fe-exec.c at 3d6a8289](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/interfaces/libpq/fe-exec.c): send prepare/describe, pipeline, result separators and Sync | Parse/Describe may be queued together; drain the complete group, not just the first null result |
| PostgreSQL cache | [plancache.c at 3d6a8289](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/utils/cache/plancache.c): `CachedPlanGetTargetList` / `RevalidateCachedQuery` | A changed fixed result descriptor may raise 0A000 even when a cached statement is described again |
| Npgsql 11.0.0 | [NpgsqlCommand.cs at 4d174200](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlCommand.cs), [NpgsqlDataReader.cs](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlDataReader.cs), [PreparedStatementManager.cs](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/PreparedStatementManager.cs) | Compare send/wait/read and connector-local reuse; do not transplant a different execution or cancellation boundary |
| Microsoft.Data.Sqlite 11.0.0 | [SqliteCommand.cs at 9e685c7a](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteCommand.cs), [SqliteDataReader.cs](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteDataReader.cs), [SqliteDataRecord.cs](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteDataRecord.cs) | Reuse preparation/binding/reset concepts; ExecuteReader stepping is not Korda's cursor-open timing |
| SQLite 3.51.3 | [prepare.c at a5333afb](https://github.com/sqlite/sqlite/blob/a5333afb9ad1aa473f8963b92caeaa955f47dc74/src/prepare.c), [vdbeapi.c](https://github.com/sqlite/sqlite/blob/a5333afb9ad1aa473f8963b92caeaa955f47dc74/src/vdbeapi.c) | prepare/step/reset/finalize, bind lifetime and schema reprepare |
| Dapper.AOT 1.1.0 | [CommandT.Query.cs at 0e071bf0](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/CommandT.Query.cs); upstream Query/CacheCommand generated test fixtures | Tokenize once then typed Read; [actual generated consumers](generated-consumers/README.md) are now retained with hashes; upstream fixtures remain separate |
| .NET 11 | [DbCommand at deae2e32](https://github.com/dotnet/runtime/blob/deae2e32bf0e018e09d64597b7c59b62b73bb3ce/src/libraries/System.Data.Common/src/System/Data/Common/DbCommand.cs) | Its base async wrappers may invoke synchronous methods; inspect the actual provider overrides before attributing I/O behavior |
| SqlSugar | [QueryableHelper at 06789315](https://github.com/DotNetNext/SqlSugar/blob/06789315fcea02f17901506b0cbf670a25192083/Src/Asp.NetCore2/SqlSugar/Abstract/QueryableProvider/QueryableHelper.cs): `_ToListAsync` / `_ToSql` / ToSqlString + Parameters / GetDataReaderAsync | Complete-query construction reference; no new reflective mapper dependency |

## Selected changes and deletion obligations

| Layer | Reuse, rewrite or delete | Required proof |
| --- | --- | --- |
| Public Fluent, metadata and codecs | Reuse public shape, validation timing, capability refusals, source ownership, static DTO construction and semantic codec policies | Existing API checks, full query goldens, dynamic and generated/handwritten parity |
| Dynamic command representation | Compare direct validated flat graph/IR compilation with the current NWQC encode/parse/replay path; select one production representation | Gate E2 below decides whether tape/replay and wrappers are deleted. Do not call the task complete with this decision omitted |
| Prepared shape and parameters | Reuse immutable SQL/codec/slot expectation; resolve managed parameter identities to ordinals once and rewrite execution as one validated typed-argument owner | Preserve missing/extra/foreign parameters, nullability, conversion/limit/error order and independent per-execution snapshots |
| Native parameter transfer | Remove `NativePlan::render`'s second NWDB encoding and the subsequent parsing/decoding into provider arguments | No duplicate frame exists on the selected public path; actual changed values and provider storage-width refusals still match |
| PostgreSQL open | Fresh unnamed Parse + Describe queued in one libpq pipeline group with one Sync; no Execute at cursor open | Full results/ReadyForQuery drainage, error priority, same physical connection and no early side effect |
| PostgreSQL physical caching | Do not adopt cross-execution statement or column-description caching in this candidate | Fresh Parse preserves external-DDL behavior; cached Describe can fail 0A000 and abort a transaction where fresh Parse differs. No hidden retry/replay repairs this |
| SQLite open | One prepared statement supplies description and binding for that same execution; open does not step | Preserve SQL-error versus parameter/shape-error precedence, binding ownership and first-step timing; finalize on every failure |
| SQLite physical caching | Not selected without a separate schema/reset/clear-bindings compatibility proof | Do not infer safety from automatic schema reprepare or ignored reset errors |
| Native result construction | Replace per-cell owning `Bytes`/row staging and reparsing with direct bounded writes into the transferred batch arena | Complete shape preflight, checked extents, typed conversion, row/field/byte limits and failure-atomic publication |
| Native-to-managed batch ownership | Rewrite private per-batch wrappers as one stable scoped native owner and generation-checked Span lease | Current code already avoids a whole-batch native-to-managed copy; preserve held-reader lifetime and do not claim removal of a nonexistent copy |
| Managed row access | Match/validate layout once per accepted result/batch, then use typed offsets/readers within the retained lease | Preserve malformed-wire, missing/duplicate/type/NULL/narrowing/UTF-8 errors and constructor-failure cleanup |
| EOF and wake/retirement path | Replace per-batch generic operations with a cursor pull channel; first request opens/validates/fetches, later requests fetch; retain observed EOF and final true join | Exactly one detached callback per accepted generation, no provider/read-guard use after readiness, no permanent idle self-root, no speculative row read or late error suppression |
| Superseded adapters | Delete private unused encoders, parsers, staging objects and old entry routing after public consumers prove the replacement | Retain required ABI compatibility adapters separately; record remaining callers and costs instead of keeping silent product fallbacks |

The [Design target](https://github.com/IzuSharp/Korda-Design/blob/task/DB-Perf-01-query-optimization/docs/database/query-semantics.md)
owns semantics. The initial selections are now being implemented and reviewed; no dirty-worktree development pass is a frozen-candidate or performance acceptance. See the [development checkpoint](development-checkpoint.md). One complete command does not imply one ABI call
for model registration, execution, fetch, cancellation and retirement combined.

## Implementation and acceptance gates

| Gate | Work | Exit evidence | Current state |
| --- | --- | --- | --- |
| E0 — recovery and versions | Reconcile three heads, prior results, local missing inputs and actual dependency pins; read AGENTS/module routing | Checkout/restore/tool hashes, source map, reproducible local commands | Local SDK/toolchain/PG and both independent before packages recovered; [build recovery](build-recovery.json) binds the inputs. Final publication recheck remains pending |
| E1 — before observations | Build immediate-before and Dapper consumers; trace one PK query and 100 DTOs through actual generated code; calibrate 1/100/1000-row phase and mixed load | Same SQL/types/results/connection/transaction consumption; counted ABI calls, business SQL sends and necessary protocol waits | [Current-host short before/Dapper observations](before-local/README.md) and [actual generated sources](generated-consumers/README.md) retained. FFI diagnostics, same-SQL external phase comparison, offered-rate and long baselines pending |
| E2 — complete command decision | Direct operand compilation and private in-place edits replace the redundant replay adaptation; retain one bounded NWQC representation | Source/test-bound deletion and retained-copy inventory; construction and Prepare cost, without attributing read-complete gains to compilation | Implemented in B; current phase measurements retained. Final review of remaining record/immutable-block/literal copies is in progress |
| E3 — parameter and provider execution | Direct typed arguments, PG grouped fresh Parse/Describe and SQLite single-statement opening | Changed values, schema/DDL, empty metadata, error order, no open side effects and protocol faults | B implementation and independent package CI pass; local SQLite transaction retirement failure remains blocking |
| E4 — batch and mapper | Direct native arena, validated managed layout and observed EOF record | 1/100/1000 DTO values and costs, malformed inputs, held mapper, cancel/early stop and complete retirement | B correctness development and same-SQL public oracles pass. B large-result timing regresses; bounded retirement scheduling experiments continue |
| E5 — complete public route | Fluent/Prepare/raw SQL/complex queries/transactions/streams use the selected path; remove superseded helpers | Dependency-selected correctness/API and independent package consumers; DTO-only edits retain native bytes | B two bundles and six external AOT consumers built; CI 45684406029 passed. Local full native gate failed 1/20 on transaction closure-tail owners; preserve and fix before final acceptance |
| E6 — local candidate freeze | Paired before/candidate/Dapper and bounded scheduling comparisons, retaining all regressions | Exact source/package/AOT/native/generated freeze, calibrated concurrency/rate and quiet host observations | [B paired short data](candidate-b/README.md) complete (48 commands). C one-retry comparison complete (46 commands); four-retry comparison building. Final candidate, offered rate and long freeze pending |
| E7 — four long cells | Run candidate and Dapper.AOT for each database, serially, at least 1800 effective seconds each | Raw counters, histograms, errors/rejections, CPU/RSS/idle/GC and unchanged post-run inputs; 4 cells / at least 7200 seconds | 0/4 for this refactor |
| E8 — delivery and stop | Independent complete-path review, normal PR merges, observed existing CI and rule-selected release/public consumption | Actual merge/CI/package receipts, deletion inventory, remaining gaps and measured stopping reason | Pending |

Each additional wait, copy or intermediate representation needs a named protected
contract, the corresponding test and a measured cost. First complete the single
row and 100 DTO paths; then cover complex queries, transactions and streaming.
Do not preserve the old Host layout merely because it exists. Do not claim a
micro-optimization or passing source/project test as the complete external
provider path.

## Correctness oracles to retain

| Contract | Existing source-bound tests / required continuation |
| --- | --- |
| Cursor-open timing | `native/cpp/tests/streaming_tests.cpp::bounded_batches` requires zero reads before fetch; `fixtures/sqlite.cpp::early_stream` counts real UDF calls. Add real-provider open/no-fetch/close and volatile/write-returning observations for the changed path |
| Transaction effects separate from cancellation/cleanup | `transaction_tests.cpp` admission/deadline/Unknown families; real SQLite commit-hook and PG COMMIT-response-loss fixtures |
| Protocol-safe reuse | `postgres_sync_tests.cpp`, `fixtures/postgres.cpp::timeout_rollback`, same-backend and terminated-backend replacement probes |
| Fault injection after changing Sync count | Move injection to the actual semantic boundary; retain SQL error priority, Unknown, cleanup disposition and charged lease. Old ordinal counts are not the target contract |
| Batch budget and lifetime | `streaming_tests.cpp::batch_outlives_cursor`, `field_and_shape`, `partial_fetch_cancel`, both retirement barriers and managed borrowed-batch/mapper tests |
| Public shape/parameter behavior | Query goldens, Binding/Fluent command-only and origin/CTE tests, `host_review_tests.cpp` physical widths/error precedence, codec fallibility |
| Historical research correspondence | [ported-tests.md](https://github.com/IzuSharp/Korda/blob/f0078da720e07031bc56464995af6791c41aaae8/native/cpp/tests/ported-tests.md), [retirement experiment](https://github.com/IzuSharp/Korda-Design/blob/3db2d69/experiments/database-retirement/src/lib.rs), [PG experiment](https://github.com/IzuSharp/Korda-Design/blob/3db2d69/experiments/database-completion/tests/postgres.rs) |

Historical Rust tests and inspected upstream tests supply semantic evidence,
not new C++ or Native AOT execution credit. A timeout never authorizes freeing an
active provider, callback or batch. No write or Unknown transaction is replayed
to recover a cache, protocol or scheduling optimization.

## Local comparison and allocation reporting

Use the existing `benchmarks/db-perf` builders, workload and observer. Compare
ordinary Fluent, warmed Prepare and full parameterized SQL through the same C++
Host; Dapper.AOT plus the corresponding driver is the external end-to-end
reference. Direct libpq/Npgsql measurements are diagnostic isolation only.

Before and candidate must use the same machine, exact dependency versions,
fixture, SQL and parameter types, physical-connection/transaction policy, result
values and full consumption. Retain the historical SQLite `?`/`?1` normalization
disclosure until a new actual-byte trace proves alignment. Rebuild and remeasure
the immediate before input when its old environment/consumer is not comparable.
Do not overwrite earlier data or present a rebuilt binary as a recovered one.

Run short calibration before selecting concurrency/arrival rate. Offered-load
receipts must retain scheduled arrivals, queue rejection and accepted-work
drain; closed-loop observations remain explicitly separate. The old numeric
extractor rejects non-null OfferedLoad, so any new offered-load publication
requires a reviewed versioned extraction change. Do not turn missing rejection
counters into measured zero.

Final required cells are SQLite/candidate, SQLite/Dapper.AOT,
PostgreSQL/candidate and PostgreSQL/Dapper.AOT. Each is one uninterrupted
1800-second observation, run sequentially with warmup/setup/idle outside its
measurement boundary and accepted-work drain accounted explicitly. No parallel
benchmark, build or fault-injection load may contaminate a cell. Report actual
host/quota/noise observations and limits without claiming unobserved exclusivity.

Report throughput, p50/p95/p99, failures, retries and rejections, client CPU,
PostgreSQL server CPU where actually attributed, peak/steady/after-idle RSS,
raw all-process allocated bytes and generation 0/1/2 collections. Separate
business DTO/list/string/JSON allocations from observed framework costs.
The steady framework path targets 0 B of additional managed allocation; each
public operation, suspended/concurrent path and refill boundary needs its own
actual coverage before that target can be declared met.
Public Task and one-shot owner/lifetime allocations must be reported as explicit
residuals if they remain; never subtract an estimated business graph or empty
harness to fabricate framework-wide 0 B. A zero in-row window does not mean zero
per-query allocation, zero GC or zero native allocation.

## CI and final stopping rule

CI keeps its existing compilation, correctness and rule-based packaging duties.
Use Korda's existing diff/dependency planner and independent provider package
runners. Run and inspect:

```sh
python3 eng/ci/impact.py origin/main --output artifacts/plan.json
```

Explain each selected scope from changed modules/dependencies. If selection
cannot be explained, record the exact question and stop that change instead of
adding a job. Benchmark source ownership may remain registered without an
execution action. No performance workflow, job, manual button, scheduled run or
benchmark hidden inside a correctness/release script is permitted.

Retain existing Plan/Design document gates and frozen history. The old
`acceptance.json` and `delivery-graph.json` eight-cell snapshot keep their original
meaning; this four-cell continuation does not mark those old claims passed.
Publish fresh results and acceptance decisions here, bound to actual candidates.

The [initial document-gate record](document-gates-initial.json) preserves the
Design naming/history passes and Plan's existing frozen record gate pass at
`38f8ce8a01f88e6e4c4459926f197c5438c2f6fc`. It also retains the failed attempt to
run that legacy Plan verifier at the current head: its path guard compares with
`bc1956936ee77a997a016856c97def6aabc0bbc6` and rejects the same eight paths already
outside its scope at the starting Plan head. The existing CI deliberately runs
the unchanged verifier at its immutable input. Neither the verifier nor the old
acceptance record was weakened to make this draft pass. These are document and
historical-integrity observations, with no new product or performance execution.

Completion requires the entire chosen path, public-package correctness,
reproducible before/after evidence, four candidate/reference long cells and
normal reviewed delivery. Record every retained or deleted layer, unresolved
gap, and why another concrete change no longer has a supported measurable
benefit. If an implementation, environment, correctness or measurement gate is
blocked, record the blocker and remaining work; do not declare full refactoring
or performance acceptance.

