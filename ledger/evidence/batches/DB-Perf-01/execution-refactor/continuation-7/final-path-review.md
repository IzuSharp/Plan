# Final-path source and package reading — 17da

Reviewed on 2026-11-26 by the `find_path` worker. Formal source is
[`17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`][product], tree
`bc9087d843d8d741d83d44f53d0b2c5af26dcffc`. The implemented path, fixed upstream
references, actual generated-consumer distinctions and contract-to-test map are
recorded in [Design execution-path-17da.md][design].

This is a separate **source and existing-receipt reading audit**. No product
build, test, workload, archive or evidence-hash sweep was run for this review.
It creates no new correctness, AOT or performance execution credit. The worker
authored the Find implementation; this document is not independent approval of
that worker's own change. [The independent native/Find review](find-path-review.md)
and [Find validation receipts](find-validation/README.md) retain their actual
reviewers, executed sources and failure records.

At this checkpoint, final continuous1800-second credit remains **0/4**.
[Campaign selection](local-load-tools/current-campaign-selection.md) owns the
remaining same-host before supplement, offered-load validation and four serial
final cells. The later campaign record must supply its own exact execution
results; this reading does not predict them.

## Entry-path check

| Public entry | Source observed at 17da | Conclusion |
| --- | --- | --- |
| Ordinary Fluent | `SessionQueries.cs -> QueryBinding.CreateBuffered -> QueryCommand -> native compile/seal -> QueryContext.Stream` | Formal entry submits the complete command; `CommandOnlyTests` separately covers absence of per-node composition exports |
| Prepared | `Terminals.cs`: `Owner.Seal(8)` once; exact-Source checks and parameter capture in `PreparedQuery.Stream` | Fixed native plan/layout is reused; values and execution owners remain independent |
| Find | `Crud.cs -> AcquireFindPlan -> FindPlan.Execute` | Exact-Table Source cache and private key slots bypass repeated Fluent/NWQC construction and the second general ShapeCache lookup |
| Parameterized SQL | `DataSession.QueryAsync/StreamAsync -> SqlSubmission.Create` | Uses the explicit SQL and captured argument input, without routing through Fluent composition |

All four row paths reach `DataSession.OpenPlanStreamAsync -> NativeHost.CreatePull
-> HostStreamTransport -> TypedStream -> generated/static DTO reader`.
`BatchResultTests` checks public pull counts and known EOF, one SQL execution,
one final close and zero generic per-fetch retirement. No source fallback to the
old row execution path was found. Source routing is not a substitute for actual
consumer execution; the package builds and ordinary phase/workload receipts keep
those different claims separate.

## Retained/deleted work check

- Reuse libpq18 and sqlite3 3.51.3. PostgreSQL Parse/Describe share one pipeline
  group/Sync, while complete metadata still precedes Execute. SQLite describes
  and binds the same prepared statement, with no step at open. EOF and healthy
  pre-COMMIT proof remove only the specifically verified extra confirmations.
- Dynamic NWQC record traversal and native semantic compilation remain. The
  deleted work is clause/field rewrapping, token patching, duplicate schema
  parsing, whole-frame value retention and private arena cloning/re-encoding.
  Ordinary Fluent and public Prepare still use the general ShapeCache; private
  Find directly reuses its owned compiled shape.
- Native typed values move into the execution plan; batches are written directly
  into their bounded arena and borrowed through scoped owners. Header/descriptor
  work, extent and data-dependent validation, independent parameter bytes,
  SQL/Expectation ownership and per-batch scheduling still have actual callers.
- Typed command completion replaces generic polling for the selected scalar,
  CRUD and transaction/control entries. Source/admin/unknown-acceptance generic
  work, old direct ABI compatibility and independent cleanup/notification fences
  remain necessary callers rather than deletion candidates.
- Arbitrary fixed Fluent method bodies are not source-generated SQL templates.
  Actual generation supplies model/projection/DTO readers; runtime Prepare and
  private Find provide the implemented fixed execution shapes. Cross-execution
  physical statement caches remain unselected because their equivalence is not
  established under the retained schema/error/lifetime contract.

The historical `remaining-hot-path-costs.md` and early native review bind their
original 47fe650 source. Their Find/general-ShapeCache wording does not describe
17da; the history has not been rewritten. Design's new current-path record
likewise identifies older implementation-pending tables as historical.

## Independent provider package reading

Read the original release JSON and the existing
[completed-public-builds-17da-02 audit](current-ci-review-evidence/completed-public-builds-17da-02.json).
Both clean producers bind exact source17da/treebc9087d, and both record all eight
stages passing: impact, native build, native correctness, bundle, public AOT
consumption, public validation and the two ordinary consumer builds.

| Independent top-level package | Dependency map | Sole provider image | Package SHA256 already recorded by the audit |
| --- | --- | --- | --- |
| `Korda.Database.Sqlite` | `{}` | `runtimes/linux-x64/native/libnw_database_sqlite.so` | `059a0df6b2ed428788b2bf5a7212dd4d73d43cd642eee0de152b975efaf03d6a` |
| `Korda.Database.PostgreSql` | `{}` | `runtimes/linux-x64/native/libnw_database_postgresql.so` | `46d5757c6dc48c721167476e2975f025b6884dc0c54b6956b9677a8eb4b29dec` |

Those identifiers were read, not recomputed here. The prior missing-bit29
inventory failure remains evidence; 17da closes the exact export inventory
without weakening its audit. No cross-provider package dependency or implicit
old-asset execution fallback was found. The associated CI/build evidence lives
in [current-ci-review.md](current-ci-review.md), not in this source reading.

## Rejected experiment and material remaining claims

The [prospective close rule and observed rejection](close-quiet-experiment.md)
retain public92b separately. It passed correctness/package validation but failed
the selected ordinary-performance rule: PostgreSQL single-row read-complete was
directionally inconsistent across the two rounds, and SQLite1,000 pooled total
p50 regressed6.78%, above5%. Formal17da therefore retains queued final close.
This review credits neither public92b nor its superseded untimed predecessor
as the final path. Rejecting this experiment does not prove all remaining
optimization opportunities are exhausted.

The following remain material limits on completion claims:

1. [Current allocation evidence](current-measurements/allocation/README.md)
   explicitly reports `FrameworkOnlyBytes=null`. It separates actual mapper/List
   scopes without subtraction, has no current before-allocation overlay and
   grants no standalone Find-allocation result. Whole-framework0B is unproven.
2. Submit/read-complete timing does not isolate every surviving hash, copy,
   validation or dispatch cost. The source inventory identifies those costs,
   but no per-component CPU/latency attribution is invented.
3. Window process-GC counts are not the entire process lifetime including
   setup/warmup/gaps. Final metrics must retain the actual runner scope.
4. Final same-host long-run comparison, normal reviewed merges and observed
   existing CI/rule-selected publication are separate delivery obligations.
   Current source/receipt reading grants none of their uncompleted credit.

No new product-entry or package-closure blocker was found. The stopping rationale
must preserve measured gaps, unproven claims and failed experiments; it cannot
claim zero overhead or that every possible measurable gain has disappeared.
Only these documentation paths were changed. Documentation gates are deferred
to the coordinator's measurement gap; no test was hidden in this writing step.

[product]: https://github.com/IzuSharp/Korda/commit/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa
[design]: https://github.com/IzuSharp/Korda-Design/pull/20
