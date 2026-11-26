# One-shot command completion implemented; final package measurements pending

This checkpoint continues [continuation 5](../continuation-5/README.md). Public
[Korda 8789a45](https://github.com/IzuSharp/Korda/commit/8789a45a52cc0cc0a0b62737542d9c120b753c9b)
has tree `c8f398ae4db2d39302335a51a6378b737409f2fb`, identical to integrated local
`d8beff6dc31f6190caaed333a28847511b7adbc5`. The selected command-completion
implementation and development correctness are complete. Root is building the
two formal provider profiles/packages and external ordinary consumers from this
fetched public source. Those builds, package consumption, new measurements and
their exact input identities require their own subsequent records.

The existing [CI run 45759068704](https://github.com/IzuSharp/Korda/actions/runs/45759068704)
is **pending at this checkpoint**. No successful result is predicted. Final
candidate/Dapper.AOT long-test credit remains **0/4**. Source publication, this
archive, development tests and AOT compilation do not establish performance,
whole-framework 0 B, normal merge or release acceptance. Earlier four-cell and
eight-cell records retain their historical identities and original bytes.
The [intermediate exact-head observation](ci-45759068704-observation-01.json.gz)
at 05:16:10Z records completed provider/interop/security jobs and an in-progress
Linux job; it does not establish overall CI success. Its original bytes are
[retained without normalization](ci-45759068704-observation-01.retention.json)
in deterministic gzip after the raw extra EOF blank line failed git whitespace
validation; that document failure is retained separately.

## Fixed identities and evidence roles

| Input | Identity | Credit at this checkpoint |
| --- | --- | --- |
| Public implementation | `8789a45a52cc0cc0a0b62737542d9c120b753c9b` | Published source, same tree as reviewed local `d8beff6` |
| Integrated local source | `d8beff6dc31f6190caaed333a28847511b7adbc5` | Contains final test corrections and matched Dapper lifecycle SQL |
| Independent development native producers | `374a253f09f47d0b42f9d18491677158287ba18b` | Two real Release provider assets without test hooks; product bytes match the integrated source |
| Final NativeHost AOT test source | `21fd325cc528eab720f06e681c1f5cd9aee64da2` | Actual paired provider command matrix and complete NativeHost suite passed |
| Final original Fluent/Relations suite source | `8736d93da65f1d7ae19508afb28f68de224e19de` | Original public API suites and seven compile-negative cases passed |
| Matched Dapper AOT build source | `4532354b4a316285b21b463f6ca6eda670dd7a49` | Both AOT builds and actual emitted factory contracts verified; no runtime/timing credit |
| Previous Plan checkpoint | public `b748d89ed0173843b182703d6affa534d6c43aa0`, local `0b85e76bc42d2173594cbcafdd4205b290659cc4` | Same tree `9f2e73e27c005db623e08a9391ffd260f1af0e8e`; previous evidence is unchanged |

Read [the public source parity](source-parity-public-8789a45.json),
[publication intent](one-shot-publication-intent-01.json),
[publication receipt](one-shot-publication-receipt-01.json), and
[previous Plan publication receipt](command-plan-publication-receipt.json).
The public tree was checked directly from the fetched git objects. The matched
Dapper source and tool inputs are byte-identical between their build commit and
public 8789a45. Development product/test parity is preserved inside the command
archive; these comparisons are not new executions at the public commit.

## Implemented path and preserved contracts

Normal Count/Any, nonreturning mutation/CRUD, transaction begin/finish,
savepoint controls and session/transaction/savepoint close now use
`db.command.completion.v1`. The four typed exports are request, take,
take-error and cancel. The result-ready notification follows release of the
worker's action, command admission, cancel hook, Source pending reservation and
business accessors. A separate notification-tail fence preserves parent join
safety. The managed controller retains the root, callback slot, setup and
cancel controls until the corresponding obligations drain before publishing.

Normal terminals prove one actual request/ready/typed take and zero generic
retirements. Source open/close, administration, frozen ABI and cold proof keep
their genuine generic callers. Untaken new transaction/savepoint owners require
real cleanup; an existing transaction's early `Unknown` result cannot imply
retirement. Tests preserve primary error fields and secondary cleanup detail.

Count has a direct scalar read path. It succeeds at legal `MaxBatchRows=1`
without constructing a result batch. Native tests retain width/type/NULL,
zero/one/multiple row, late-error and transaction-state behavior. The public
Count/Any cases exercise the formal Fluent terminal at that configuration.
The frozen compatibility entry remains separate; its old batch-dependent Count
implementation does not describe the new public path.

## Actual development results and retained failures

| Evidence | Observed result | Scope |
| --- | --- | --- |
| Native `command-completion-11` | Six gates passed: query, command completion, transactions, streaming, host review and frozen C ABI | Query capability bit28 positive and bit29/63 negative controls included |
| Final native `command-completion-12` | 377 default checks plus eight real PostgreSQL queued-cancellation checks passed | Native before-work barrier proves zero provider dispatch; actual SQL verifies no side effect |
| NativeHost AOT `command-managed-05` | Locked restore, Release Native AOT publish, command-only and full suite all exit0 | Same source, executable and independent provider hashes before/after |
| New command-only matrix | 451 assertions per provider in the final standalone run | All seven public command kinds, setup/ready/control drains, rejected scheduling, cold ownership cleanup and zero final owner counts |
| Complete NativeHost suite | Main suite438 assertions/36 genuine generic retirements; every nested suite passed | Normal command/pull/close generic counts remain zero; cold/source paths retain their distinct counts |
| Original Query.Fluent AOT03 | 343 assertions, 28 cases, 14 actual generic retirements; both databases passed | Product bytes match producer374; not final public NuGet package credit |
| Original Orm.Relations AOT03 | 768 assertions, 56 actual generic retirements; both databases passed; seven compile-negative cases passed | Physical input ResourceLimit and zero SQL assertions preserved with the new real command observer |

NativeHost also retains all held-mapper/buffered, pull/close count and scheduling
matrices. Native diagnostics0..5/8/9 end at zero. Detailed counts remain in the
archive README and actual logs; assertion totals are observations, not fixed
business-operation counts.

All original product, fixture and tool failures remain classified in the
archives. These include missing secondary cleanup, rejected capability bit28,
compile/runner mistakes, incorrect scalar expectations, the stopped compile,
formatting and obsolete generic observers. Their later passes retain separate
source identities; no failed attempt is relabeled.

PostgreSQL pre-dispatch cancellation is proved by a native work barrier and
zero SQL. Dispatched cancellation is separately proved using an independently
held row lock and `pg_stat_activity`: the task stays pending after cancel intent
and confirms the actual write after lock release. Managed03's incorrect
`pg_sleep(10)` expectation is retained as a failure; its unused branch was deleted.

Managed04's SessionClose observer now requires actual kind7/result101 ready,
taken, published and drained state plus real DisposeAsync/LocalResourcesReleased.
The held mapper still owns exactly one native buffer, independent of parent
provider join; normal child close has zero generic retirement. SourceClose keeps
its genuine generic observer. The full call-site audit is archived.

## Dapper.AOT matched lifecycle SQL and actual generated code

The previous independent ORM consumers remain historical. New matched mode
matches Korda's business Find SQL and parameter sequence, including Int64
tenant/id/take=2. PostgreSQL SQL bytes match after Npgsql rewrites named
parameters to `$N` in SQL occurrence order. SQLite adapts only `?` versus named
placeholders; the remaining bytes match, so raw SQLite SQL strings are not
claimed byte-identical. Checked mutation values/types and SQL order also match.
Seventeen static checks retain wrong-SQL, missing-limit, Int32-limit,
parameter-position, mutation-value, verification-SQL, cache-policy and frozen-
manifest negative controls. Historical source/receipt/generated bytes remain
unchanged and cannot be relabeled as matched mode.

Both new consumers actually compiled to Release Native AOT. Each provider's
emitted Dapper interceptor source verifies twelve lifecycle call sites,
command factories, parameter DbTypes/value members and row factories. The
complete actual generated C# is archived, together with source, project,
global settings, asset graph, package hashes and publish logs. Their contracts
explicitly keep `runtimeSqlTraceVerified=false`; no consumer execution, timing
or allocation result is inferred from these builds.

Actual consumer versions are Dapper2.1.100, Dapper.AOT1.1.0, Npgsql11.0.0,
Microsoft.Data.Sqlite.Core11.0.0 and SQLitePCLRaw3.0.5. Package hashes and asset
graphs are preserved.

Read [the paired build record](dapper-matched-builds-01.json) and the
`dapper/` section of the public-suite archive for the original static/generated
receipts. The independently proposed PostgreSQL conditional commit-status probe
in DB-Exec-08 is **not included in public8789a45** and has no measured performance
credit here; it must not be mixed into candidate evidence.

The [SQL and driver audit](sql-and-probe-audit.md) preserves pinned Npgsql,
Microsoft.Data.Sqlite, PostgreSQL18 and SQLite source, including parameter
rewriting and transaction-control responsibilities. Matching business SQL does
not equate each driver's BEGIN/COMMIT control text or send/wait sequence; Korda's
SELECT1/Sync/query-only controls were not copied into Dapper. The separate
[fixed-shape Find proposal](find-fixed-shape-proposal.md) remains unimplemented
and unmeasured. Its source observations are not candidate behavior or gains.

## Recoverable archives

| Archive | SHA256 | Verified contents |
| --- | --- | --- |
| [command-completion-development-01.tar.gz](command-completion-development-01.tar.gz) | `ccdb3af63f640cad8b4df34a4b1674bc3b6e560d5cce1664f8c3e70dfbf6a6db` | 228 members, native01–12 and managed01–05, all failures, final tests/patches, producer identities, source audit and impact |
| [public-suite-and-matched-inputs-01.tar.gz](public-suite-and-matched-inputs-01.tar.gz) | `624244da2a13b7f523904e58b3d73e4474c84cd415c0428cbe6997563ece6c4d` | 349 members, original Fluent/Relations01–03, source/build inputs and actual provider identities, matched Dapper sources/factories and historical negative controls |
| [sql-parity-and-find-audit-01.tar.gz](sql-parity-and-find-audit-01.tar.gz) | `ca53adf8a2b53eebc47e0a590094ca2b3913bc50b3401931f8603e0e4ea49a5c` | 43 members, original read-only audit, fixed upstream source, actual generated inputs, unselected proposals and four retained source-extraction selector failures |

Each archive has an external `.manifest.json`, its scope/readme or original audit,
assembly script, member hashes and complete extraction verification. Deterministic gzip
was produced twice and compared byte-for-byte. All retained ELF paths/hashes are
bound without storing binaries, bin/obj, database data or private certificates.

The command archive audits 6706 recorded source entries. Native attempts07/08/09
include 6/6/9 then-uncommitted managed test draft hashes, which were not compiled
or executed by those native attempts. All native executed inputs match their
recorded commits; recoverable exact draft bytes are included and unrecovered
unused formatting drafts are explicitly limited to their original hashes.
Final native10–12 and managed01–05 match their recorded commits in full. This
qualification is retained instead of claiming that every historical worktree
was clean.

## CI routing, document gates and next action

The actual command-managed impact05 plan retains the existing interop/linux and
independent PostgreSQL/SQLite scopes. Its actions are compilation, correctness,
API/dependency checks, separate package production and AOT consumption. No
benchmark, profile, calibration or pressure action is added. Diff reasons may
include locally used measurement sources without scheduling their execution in
CI. The original planner/log and earlier attempts are preserved in the archives.

The unchanged Plan record gate is run at frozen
`38f8ce8a01f88e6e4c4459926f197c5438c2f6fc`, with its historical rename/API gates.
The previous current-tree rejection of eight already committed repository-rename
paths remains historical; it is not reused as the current gate and no verifier
or threshold is changed. These are document/history checks only.
The [frozen gate receipt](documentation-gates-01/frozen-record-receipt.json),
[schema receipt](documentation-gates-01/schema-receipt.json) and
[current document preservation check](documentation-gates-01/current-documents-receipt.json)
record the actual local checks. The schema receipt distinguishes local
jsonschema4.26.0 from the unchanged hosted workflow's4.23.0 dependency.

Continue from the fetched public source and matching formal package receipts.
Run actual public-package correctness and short calibration before selecting
measurement inputs. Preserve failed attempts. Compare ordinary uninstrumented
results separately from FFI/allocation diagnostics, then run the four required
serial 1800-second cells only after their complete source/package/workload/
environment identity is fixed. Record actual CI, review, normal merge and
rule-selected release results separately. Current final long credit is **0/4**.
