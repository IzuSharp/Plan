# ORM-ACCEPTANCE — independently verify the concrete product candidate

Status: `planned_candidate`; product implementation, release and migration remain
unauthorized by this research plan.

## Entry gate and ownership

Start after actual Integration, Performance and Docs acceptance, including their
pinned transitive package/provider/generator inputs. The reviewer must be independent
of the implementation being accepted; an author cannot approve their own work as
the only review. Optional Parser is excluded unless explicitly included in the
candidate feature manifest. Read current product/user authorization separately.

Own `docs/orm/acceptance/candidate.md`, `features.json` and `findings.md` in the
product repository once authorized. Read all source/tests/packages but send fixes
to their owning tasks. No release, cutover, deletion or merge follows automatically.
Use graph-pinned Design contracts0.2.0, implementation-spec, provenance and the final
source/package commits. Do not accept against mutable branch names alone.

## Fixed report structure and decision algorithm

candidate.md records Candidate source commit, Design commit, Plan commit, SDK/runtime,
platform/architecture, exact seven package IDs/versions/input fingerprints, upstream
pins, database versions/settings, mandatory feature matrix, evidence summary,
performance budgets/results, independent findings, remaining exclusions and decision.
features.json entries have operationId/profile/context/status/sourceSymbol/testIds;
status is supported, rejected-with-diagnostic or excluded-optional. No 'supported'
entry may lack its actual positive and negative evidence.

findings.md uses IDs ACCEPT-001 onward, severity(blocker/major/minor), exact
contract/implementation location, reproducible input, expected/actual result,
owner, fix commit and verification. Correctness/lifetime/AOT/license/packaging/
unsupported-behavior failures are blockers. A performance budget miss is major and
blocks a claim that the declared budget is met. Cosmetic wording is minor unless
it overstates safety, supported semantics or actual evidence.

Decision is one of: `accepted-for-cutover-review`, `changes-required`, or
`measurement-unresolved`. Accept only when every mandatory matrix cell passes,
all blockers/majors are resolved, exact package consumers pass and the preregistered
performance campaign is valid and meets its budgets. A noisy/incomplete campaign
is unresolved; do not turn it into pass by editing the threshold after measuring.
The output is a recommendation for a separate authorized action, not permission.

## Independent review sequence

1. Reconcile source diff against packet ownership. Identify any replacement reader
   loop, connection pool, scheduler, retry or reflected mapper that contradicts the
   selected mature-runtime route. Verify Dapper.AOT remains the pinned runtime and
   the only initialization override is the documented defensive factory adapter.
2. Inspect compiled public surface/XML/defaults/nullability/exception/lifetime
   contract and actual generated source. Check consumer registration roots, DTO
   constructors/init, scalar/closed Row mapping, nested logical/physical ranges and
   no runtime Roslyn dependency. Do not infer interception from a clean build alone.
3. Inspect seven exact nupkgs and their input fingerprints/native/license closure.
   Core has no Dapper/driver; Execution is shipped once; provider leaves do not
   install unrelated drivers. Analyzer host dependencies load from its private
   closure and do not become application runtime references.
4. Reproduce the targeted cases below from exact packages in isolated caches and
   disposable databases. Use native executables with IsDynamicCodeSupported=false.
   Retain concise outcomes in the report; logs/builds remain temporary.
5. Verify comparable benchmark SQL, row counts, types, connection/transaction/
   preparation strategy, complete public terminals, warmup/order and process-level
   repeats. Separate rendering, binding, mapping and end-to-end results. Apply the
   fixed Performance budget, including its allocation and invalid-measurement rules.
6. Reconcile actual module selection and package checks after any fix. Rerun only
   affected tests plus concrete remaining risks; do not replay unrelated historical
   campaigns or claim a documentation CI check accepted the product.

## Required independent cases

| ID | Reproduction | Pass condition |
| --- | --- | --- |
| ACCEPT-API | Positive natural Fluent + incompatible field/parameter type | Positive compile and intended compile diagnostic |
| ACCEPT-PURE | Core-only render/native consumer | No execution/driver/Roslyn dependency; deterministic layout |
| ACCEPT-PARAM | Optional0–3 parameters, repeated slot/name, mutable list input | Exact typed values/occurrences; no retained caller mutation |
| ACCEPT-NULL | Age=NULL vs IS NULL, nullable DTO and integer/decimal overflow | Correct SQL truth, actual null, preserved/typed failure |
| ACCEPT-MAP | Declared reorder then unexpected actual reorder | Valid declared layout; strict actual mismatch before first materialized row |
| ACCEPT-EMPTY | Wrong schema with no result row | Documented empty return; separate direct-reader oracle checks metadata |
| ACCEPT-RESOURCE | Early stream break, precancel, timeout, command-init+cleanup faults | Correct lifetime/primary error; next session operation usable |
| ACCEPT-ONCE | Concurrent session, overlapping MoveNext, reused BoundCommand | Exact KORM-EXEC diagnostics; no queued work/double execution |
| ACCEPT-GEN | Cross-assembly DTO/closed Row through generic facade, no user Dapper call | Final-consumer roots static registrations and native query succeeds |
| ACCEPT-FOUR | PG/SQLite/MySQL/Maria actual declared matrix | Every mandatory lane passes with actual server/profile identity |
| ACCEPT-NESTED | Absent vs present-null child; ordered/duplicate/empty collections; Maria truncation | Correct objects/order/count; explicit budget failure |
| ACCEPT-PACK | Seven exact nupkg consumers, private analyzer dependencies | Correct closure and native/host behavior |
| ACCEPT-CI | Provider leaf, shared contract and Markdown-only diffs | Only genuine impact/resources selected |
| ACCEPT-PERF | Fixed public-path benchmark protocol | Valid repeats meet frozen budgets; no unsupported parity/zero-GC claim |

The reviewer also inspects translation provenance against actual inherited files,
including jOOQ Apache notices, Dapper runtime distribution and driver/native assets.
Do not replace that evidence with a general statement that 'open source is allowed'.

## Failure handling and stop

Return each failed case to its module owner with exact inputs and required outcome.
After a fix, record the new candidate commit and invalidate only evidence whose
inputs changed; package fingerprints must still match the candidate. Do not mark
unexecuted OS/architecture/server-version cells supported. Stop at the recorded
independent decision. A pass permits consideration of ORM-CUTOVER after its own
concrete manifest/authorization, and never starts ORM-RETIRE automatically.

The cancellation/timeout reproduction is provider-specific: PostgreSQL/MySQL/
MariaDB exercise actual in-flight cancellation and one-second execution timeout.
SQLite exercises pre-cancel and its declared busy-timeout behavior; it does not
claim an interrupt of an already-running sqlite3_step. Unsupported cancellation
capability is an explicit recorded outcome, not a fake Task.Run timeout test.
