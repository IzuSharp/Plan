# Independent Design, source and CI review — DB-Exec-11 recovery

## Scope and conclusion

This is an independent, read-only review performed during recovery of the
DB-Exec-02 complete database execution-path refactor on 2026-11-26. It reviewed
the current Design, the recorded upstream and generated-consumer evidence,
historical experiment correspondence, the actual existing CI selection, and
normal publication requirements. It did not execute a build, test, benchmark,
profile, compression operation, or broad hash sweep, and it did not modify a
repository or remote state.

**No Design or CI issue was found that prevents starting the frozen four-cell
local campaign.** This conclusion is not final performance acceptance or merge
authorization independent of the owner's already stated conditions. The current
candidate still needs its own four continuous 1,800-second observations,
validated final evidence, final review, normal merges, and observed main CI and
rule-selected publication. Historical long runs cannot satisfy those conditions.

This review is an actual subordinate-agent technical review. It is not a GitHub
approval submitted under a different account and does not bypass repository
protection or required checks.

## Reviewed source identities

| Repository | Public candidate | Local reviewed commit | Tree |
| --- | --- | --- | --- |
| Korda | `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` | `040911c5abdee740c0cd9fbf8295bf511c9cc69d` | `bc9087d843d8d741d83d44f53d0b2c5af26dcffc` |
| Korda-Design | `ca1933e93678039b492f10a8b47045b11827f1a4` | `734e5103c2acd7315532f19a10001f57ddd58bdf` | `4c29c7b0af358dafe7343ffe10c52b445d8c4b93` |
| Plan | `9e4aad4c04c68dd30ab3bcad68a977000b4717e2` | `e66ae1025e098fe487d86b1590cda11d7a166413` | `ea0fa9e359a44d9aefd163d2db976c2784b5ef9f` |

The public product commit exists in the local object database; its tree was
directly compared with the local product HEAD. Public Design and Plan commit
objects were absent from the inspected local object databases. Their published
tree associations come from the existing
`/workspace/scratch/fd78534029f7/publication/design-04/receipt.json` and
`/workspace/scratch/fd78534029f7/publication/checkpoint-04/receipt.json`, and the
recorded trees match the local reviewed HEAD trees. The current GitHub PR HEADs
queried during recovery match the public SHAs above. This distinction is retained
rather than describing all three comparisons as new remote object verification.

Local reviewed worktrees:

- `/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-korda`
- `/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-design`
- `/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan`

All three root `AGENTS.md` files were read. Their current continuation permits
normal reviewed merges after complete verification and supersedes the preserved
historical stop instructions. The public Fluent behavior, Native AOT, C++
execution, independent provider packages, and local-only performance execution
remain binding.

## Existing CI observed during this review

| Repository and exact head | Existing workflow run | Observed result |
| --- | --- | --- |
| Korda `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` | [CI 45772470391](https://github.com/IzuSharp/Korda/actions/runs/45772470391) | completed / success |
| Design `ca1933e93678039b492f10a8b47045b11827f1a4` | [Current database API design 45783451407](https://github.com/IzuSharp/Korda-Design/actions/runs/45783451407) | completed / success |
| Design `ca1933e93678039b492f10a8b47045b11827f1a4` | [Historical English and contract acceptance 45783451381](https://github.com/IzuSharp/Korda-Design/actions/runs/45783451381) | completed / success |
| Plan `9e4aad4c04c68dd30ab3bcad68a977000b4717e2` | [Design-owned native research assets 45783337420](https://github.com/IzuSharp/Plan/actions/runs/45783337420) | completed / success |

For the product run, `plan`, interop, Linux, PostgreSQL, SQLite, Secret scan,
Dependency review, C# CodeQL, Python CodeQL and `Verify` succeeded. `modules` and
`publish` were skipped as expected for this PR plan. Each of the three PRs
returned an empty reviews list and an empty inline review-thread list. This does
not establish that repository protection requires no further approval; normal
merge processing must continue to enforce whatever protection actually applies.

## Actual diff and module selection

The review read:

- `eng/ci/modules/README.md`
- `.github/workflows/ci.yml`
- `.github/workflows/build.yml`
- `.github/workflows/release.yml`
- `eng/ci/impact.py`
- `eng/ci/plan_run.py`
- `eng/ci/registry.py`
- `eng/ci/modules/database-perf.json`
- `eng/ci/modules/db-perf.json`

The current saved plan is
`/workspace/scratch/fd78534029f7/ci-review-17da-01/plan.json`. The independent
17da package build also retained its actual plan at
`/workspace/scratch/fd78534029f7/builds/candidate-sqlite-02/ci-plan.json`.
Both select the following four scopes:

| Scope | Actual selected actions | Why the scope is affected |
| --- | --- | --- |
| `interop` | `interop.async`, `interop.callbacks` | Shared async and callback lifetime changes affect their conformance checks. |
| `linux` | `database.native`, `database.build`, `database.api`, `database.dependencies`, `database.regressions`, `fluent.api`, `api.tool`, `migrations.api`, `relations.api` | Shared database/native execution, result, Fluent, CRUD, ABI and dependent consumer changes require the existing correctness and API checks. |
| `postgresql` | `postgresql.build`, `postgresql.dependencies`, `public.pack`, `postgresql.packed-api`, `postgresql.test`, `public.consume-aot`, `public.validate` | The PostgreSQL top-level package independently builds, validates shipped content and executes its AOT consumer. |
| `sqlite` | `sqlite.build`, `public.pack`, `public.consume-aot`, `public.validate`, `sqlite.dependencies`, `sqlite.packed-api`, `sqlite.test` | The SQLite top-level package independently builds, validates shipped content and executes its AOT consumer. |

The plans have `modules=[]`, `module_packages=[]`, `deferred=[]`, and
`releases=[]`. Both PR package versions are `0.1.0-ci.1`; they are validation
versions, not evidence of public NuGet publication.

The product diff against `origin/main` preserves the requested performance/CI
separation:

- `ci.yml` has no diff.
- The two benchmark module registrations contain only `tests` path ownership.
  They have no `run`, `checks`, or `package` action and select no benchmark job.
- The added planner regression verifies that benchmark-only paths select no
  build/package jobs, while SQLite leaf and shared product changes still select
  the correct independent package validation.
- `build.yml` only expands failure-log retention to provider command, result,
  summary, stdout/stderr and PostgreSQL logs.
- `worker.py` only adds `--encoding=UTF8` to the existing initdb command.

No added performance workflow, job, manual button, scheduled performance run, or
hidden benchmark action was found. The existing weekly/manual general-check
mechanism is not a new performance workflow.

The root continuation should still save its own exact invocation of
`python3 eng/ci/impact.py origin/main --output artifacts/plan.json` from the
recovered product worktree. This reviewer read the already executed plan and did
not rerun the planner or tests during the local measurement recovery.

## Normal main publication and required delivery observations

`impact.py` uses main reconciliation to compare each registered top-level
package's current inputs fingerprint with the latest published NuGet package's
`korda/public.json.inputs`. A missing or changed package gets its own next
`0.1.0-preview.N`; the two provider versions must not be assumed equal.

The reviewed 17da PR plan records these package input fingerprints:

| Package | Input fingerprint |
| --- | --- |
| `Korda.Database.PostgreSql` | `f1727c1a6fd91c691fd35559b6314764d05f611de5907b1cf62e6e3f4b5cbff3` |
| `Korda.Database.Sqlite` | `41ca933c2990a2184613e459c21440486549884634ef4678ad80e45bc6b50941` |

Existing `ci.yml` publishes only when the event is `push` on `main` in
`IzuSharp/Korda`, `Verify` succeeded, the reconciled releases list is nonempty,
and the existing `NUGET_PUBLISH_ENABLED` variable is `true`.

The release workflow downloads each already verified candidate artifact,
validates its tested tree, allowed package set and bytes, and checks whether a
newer main has superseded that package's inputs. It must not publish stale
content over a newer package. After a permitted NuGet push, the same workflow
waits for indexing, downloads the signed registry package, checks its actual
content against the candidate, and builds/runs the public Native AOT consumer.
The `public-consumption-<module>-<version>` artifact preserves the release and
plan records, registry readback and public-consumption receipts.

Final delivery therefore needs the actual merged main SHA and main CI result,
plus each provider's actual release selection, version, publication outcome and
public Native AOT consumption. Successful PR CI is not publication evidence.
Do not create another publication path or alter release permissions to make
these observations appear successful.

## Current driver-to-Fluent decision and implementation correspondence

The current primary Design entry is
[execution-path-17da.md](https://github.com/IzuSharp/Korda-Design/blob/ca1933e93678039b492f10a8b47045b11827f1a4/docs/database/execution-path-17da.md).
It separates implemented 17da behavior from older proposal tables and identifies
actual reuse, rewrite, deletion, retained costs and contract tests. Its product
links are pinned to 17da and its current Plan links to 9e4aad4.

| Boundary | Reviewed current decision and correspondence |
| --- | --- |
| Ordinary Fluent | Keep bounded NWQC semantic composition and typed owner sidecar, with C++ as the authoritative compiler. Record traversal and semantic compilation remain real work; one submission is not described as zero replay cost. |
| `.Prepare()` | Reuse compiled SQL, ordered parameter metadata and projection layout; independently snapshot changing values for each execution. |
| `FindAsync` | Reuse a Source-owned bounded fixed-key shape keyed by the exact Table identity, NativePlan/key slots and the exact managed mapper. The former per-call Fluent builder is replaced; its retained test oracle still has a real differential-testing caller. |
| Complete SQL | Keep raw SQL's own captured submission contract rather than treating it as a prepared execution or borrowing mutable caller data across await. |
| Shared row-producing route | `OpenPlanStreamAsync -> CreatePull -> HostStreamTransport -> TypedStream -> RowReader -> DTO` is the stated actual route for all four public entry forms. |
| Native arguments | Remove the second render-time NWDB encoding and Host re-decoding; transfer validated typed scalar ownership to provider binding. |
| Native result construction | Write directly into a bounded BatchWriter arena; remove per-cell owning vectors and row staging. Keep extent, type, NULL, numeric, UTF-8 and generation/lifetime validation. |
| Count and controls | Typed command completion covers Count/Any, nonreturning mutations, transactions/savepoints and child close. Source/admin/uncertain-admission generic paths retain actual responsibilities. |
| PostgreSQL | Fresh unnamed Parse and Describe share one preparation Sync. Proven successful preparation and natural EOF remove redundant confirmations; skipping pre-COMMIT SELECT 1 requires the narrow healthy exact-INTRANS proof. |
| SQLite | Prepare, inspect metadata and bind one statement. Opening does not step; completion and failure still finalize. Cross-execution statement reuse is not claimed. |
| Final retirement | 17da retains queued final close and independent ownership/notification fences. The rejected close experiment is not silently adopted. |

The public-route tests named in the Design are substantive correspondences:
`CommandOnlyTests` removes direct composition exports from its resolver while
the complete-command entry still succeeds; `BatchResultTests` covers public
1/32/64/100/1000-row streams with exact pull, SQL and final-close counts. The
Design does not treat compiling a consumer alone as proof that a timed route
executed.

The Design explains why copying Npgsql or Microsoft.Data.Sqlite reader-open
timing directly would violate Korda's existing side-effect timing, and why a
successful libpq send count is not an observed network RTT count. PostgreSQL
physical statement/description caches and SQLite reset/clear-bindings reuse
remain unselected because their DDL, transaction, error-order and ownership
equivalence has not been established.

## Fixed upstream and actual generated-consumer evidence

| Reference | Pinned version/commit and reviewed evidence category |
| --- | --- |
| PostgreSQL/libpq | 18.0; `3d6a828938a5fa0444275d3d2f67b64ec3199eb7`; server Parse/Bind/Execute/Describe, libpq send/result/Sync, plan revalidation. |
| Npgsql | 11.0.0; `4d174200ed48e3e3ab16419dbf84dd655da59de6`; command, reader, physical prepared-statement ownership and transaction controls. |
| Dapper.AOT | 1.1.0; `0e071bf05e54caecfa98c885b075fa3e247f3ecc`; `CommandT.Query.cs`, fixtures, and separately retained actual consumer-generated sources. |
| .NET | 11; `deae2e32bf0e018e09d64597b7c59b62b73bb3ce`; DbCommand base contract versus provider implementation. |
| Microsoft.Data.Sqlite | 11.0.0; `9e685c7a52d1a344d133a3d370e458db97417b3f`; command, reader and record behavior. |
| SQLite | 3.51.3; `a5333afb9ad1aa473f8963b92caeaa955f47dc74`; prepare and VDBE API boundaries. |
| SqlSugar | `06789315fcea02f17901506b0cbf670a25192083`; complete SQL/parameters before provider execution. |

The reviewed native lock and actual consumer project agree on libpq 18.0,
SQLite 3.51.3, Dapper.AOT 1.1.0, Npgsql 11.0.0 and Microsoft.Data.Sqlite.Core
11.0.0. The user requested the versions actually locked by the consumer and
native build; this review does not replace those inputs with unrelated latest
versions.

The Design correctly distinguishes three actual generated-consumer identities:

1. The original nine-column Order mixed-workload reader.
2. The later matched-SQL lifecycle Find with `tenant`, `id`, and `take` as three
   Int64 parameters; it is not the earlier two-parameter PK command.
3. The current two-column Id/Note phase consumer. The preserved generated source
   has two command-factory instances, two ordinal Int64 parameter updates,
   `RowFactory0.Tokenize` matching names/types once, and typed reads/IsDBNull
   followed by direct `PhaseRow` construction.

This reviewer directly read the preserved actual generated phase source and the
matched-SQL audit. Upstream generated fixtures were not substituted for emitted
consumer code, nor was the nine-column RowFactory3 substituted for the
two-column phase reader. The audit also distinguishes PostgreSQL provider name
rewriting and SQLite's allowed placeholder differences from a claim that every
raw SQL byte and driver control command is identical.

## Historical experiment guarantees and current C++ tests

The original function names were read from Design commit `3db2d69` in the two
experiment paths explicitly requested by the owner. Their guarantees were
compared with current `native/cpp/tests/ported-tests.md` and the maintained C++
fixtures/protocol tests.

| Historical guarantee | Maintained C++ correspondence |
| --- | --- |
| Dropped transaction rolls back before the same connection is reused | SQLite savepoint and transaction lifecycle families, including final-owner cleanup. |
| Early stream drop unblocks the bounded row queue and permits safe reuse | SQLite `early_stream`, B06 streaming ownership cases and provider tests. |
| Cancelled pool acquire does not lose its permit | SQLite admission and PostgreSQL `stream_and_admission`. |
| Dropping an already dispatched commit before acknowledgement can still commit | SQLite `lost_commit` and B05 response-loss/Unknown cases. |
| Progress-cancellation state is removed before the next operation | SQLite cancellation/stale-token and provider checks. |
| Pool close waits for the checked-out parent and rejects new acquisition | `pool_retirement`, `last_parent`, and the actual SQLite collation-destructor retirement gate. |
| PostgreSQL statement timeout requires rollback before same-connection reuse | `timeout_rollback`, retaining 57014, 25P02, explicit rollback and reuse. |
| PostgreSQL early stream drop drains before the next query | `stream_and_admission`, provider and protocol tests. |
| Codec roundtrip and lossy refusal | PostgreSQL `codecs`, native scalar/codec gates and the retained 120-vector comparison. |
| Lost COMMIT reply can coexist with durable effects | `lost_commit` with a real proxy and independent SQL, plus protocol `commit_fault` cases. |
| Conflict CTE snapshot requires a separate recovery statement | `conflict_snapshot`. |
| Migration error leaves an advisory lock until dedicated connection retirement | `migration_lock`, retaining the contaminated-lease negative control. |

Current PostgreSQL protocol tests additionally assert exact commit-readiness
exclusions: IDLE, live described statement, active reader, statement still live
after EOF, INERROR, completed rollback and closed physical connection. Fallback
cases retain savepoint and 25P02 priority, post-COMMIT missing/held confirmation,
Unknown outcome and connection safety.

These are source/test correspondences, not new executions. Old Rust experiment
counts and previous C++ run counts must retain their actual source/run
identities and cannot be relabelled as independently built 17da package tests.

## Current navigation that must be refreshed before final delivery

The following do not block the frozen run, but should be updated with a new
current record before claiming delivery. Preserve the old records as history.

1. Design and Plan PR bodies still point to `b748d89` / continuation-5 and
   describe older implementation-pending state. The product PR body also does
   not yet reflect the completed current 120-second comparisons.
2. `execution-refactor/current-checkpoint.md` still leads with the 15:16 record,
   saying PostgreSQL phases are running and naming older Design `da8c314`.
   The frozen continuation-7 and current Design record already contain the
   later evidence, but the shared entry point is stale.
3. `docs/generators/query-generation.md` still contains an older statement that
   final integrated package gates are pending. Its current entry should point
   to the successful exact-17da package evidence and the eventual final campaign
   result without rewriting historical claims.
4. Keep the exact frozen historical verifiers and inputs unchanged. Plan's
   existing workflow intentionally runs the old DB-Perf gate at
   `38f8ce8a01f88e6e4c4459926f197c5438c2f6fc`; running it directly against current
   changed evidence has the wrong scope. The preserved scope failure is not a
   reason to relax that gate.

## Honest final stopping rationale

The current Design already states the limits correctly. The final summary must
continue to distinguish the completed refactor and measured gains from these
remaining measured or unproven costs:

- Additional managed framework allocation of 0 B remains unproven. The current
  allocation audit records `FrameworkOnlyBytes=null`.
- Separately measured mapper/List allocation must not be subtracted from total
  process allocation to manufacture a framework-only number.
- The exact latency/CPU cost of every retained hash, copy, validation and queue
  has not been independently isolated. Phase timing alone does not identify
  each component's causal cost.
- Rejecting the narrower final-close experiment under its prospective rule
  does not prove that every possible measurable improvement has disappeared.
- Arbitrary fixed Fluent method-body SQL/template generation and physical
  statement caches are not implemented/selected by this candidate.
- GC scope must be reported as actually measured: process-wide deltas for
  specific windows are not the whole process lifetime including setup/warmup.
- Final throughput, p50/p95/p99, errors/rejections, CPU, peak/idle RSS,
  allocations, GC and remaining Dapper gaps must come from the final validated
  evidence and keep historical observations separate.

The final stopping statement should identify what was completed, the observed
before/after gains, the rejected experiments, the remaining costs and the
practical reason for ending this round. It must not claim whole-path zero
allocation or exhaustion of all possible optimization merely because the
required long observations completed.
