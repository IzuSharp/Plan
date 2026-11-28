# Korda-Orm-01 Linux handoff

Status: **mature-runtime route selected; substantive specifications complete;
final cross-file corrections and paired PR checks in progress**. Research stop
condition A is met: the verified route merits implementation. Product implementation,
merge, package publication, cutover and deletion remain unauthorized. This is the
single maintained continuation and result record for Korda-Orm-01.

## Scope and formal entries

- [Research and specification plan](plan.md).
- Existing review PRs: [Korda-Design #23](https://github.com/IzuSharp/Korda-Design/pull/23) and [Plan #39](https://github.com/IzuSharp/Plan/pull/39); both remain open and unmerged.
- [Implementation entry](../../../../docs/korda-orm/README.md), [independent graph](../../../../docs/korda-orm/implementation-graph.json) and 30 detailed task packets.
- [Published Design checkpoint](https://github.com/IzuSharp/Korda-Design/tree/b67317b2a89245fe82337b9b69e2748626ac67cb/docs/korda-orm), with contracts ORM-C01–C06 version0.2.0 and implementation-spec.md.
- [Execution selection and alternatives](https://github.com/IzuSharp/Korda-Design/blob/b67317b2a89245fe82337b9b69e2748626ac67cb/docs/korda-orm/execution-aot.md), [mature-runtime analysis](https://github.com/IzuSharp/Korda-Design/blob/b67317b2a89245fe82337b9b69e2748626ac67cb/docs/korda-orm/mature-execution.md) and [bounded validation](https://github.com/IzuSharp/Korda-Design/blob/b67317b2a89245fe82337b9b69e2748626ac67cb/docs/korda-orm/validation.md).

Only IzuSharp/Korda-Design and IzuSharp/Plan are writable, on the existing
`task/Korda-Orm-01-linux` branches in separate worktrees. IzuSharp/Korda was inspected
read-only at `36bd5ba169b628ba4d61dd9fe260eaef5ff15599`; no product source, remote
branch, PR, workflow or setting was changed. All raw experiments, checkouts,
generated source, logs, archives, binaries and benchmark outputs remain outside
the document repositories and were not uploaded elsewhere.

## Fixed decision and what the implementer receives

The default is a driver-free C# DSL and renderer translated from reviewed jOOQ
semantics, **unmodified Dapper.AOT1.1.0 Runtime**, a small typed-layout
CommandFactory adapter, ordinary incremental generation of RowFactory subclasses,
and Npgsql/Microsoft.Data.Sqlite/MySqlConnector transport. jOOQ binding/conversion,
constructor/presence and nested-result rules inform the explicit C# adaptation.
There is no new Korda reader loop, pool, scheduler or retry engine.

The earlier independent Korda binder/projector default is superseded. Original
Dapper.AOT with explicit DynamicParameters remains a demonstrated compatibility
route and performance control; it is not rejected merely because SQL is dynamic.
A stable prebuild/interceptor route and a native Java/JDBC route are feasible
alternatives. Their additional integration or ownership cost is unnecessary for
the supported selected path. The comparison and unsuccessful alternatives retain
precise limitations rather than claims of universal impossibility.

All 30 packets are execution specifications. They fix file/module ownership,
shared/public/internal signatures, node fields, source/symbol inheritance, ordered
algorithms, state transitions, error codes, fixtures/expected results, commands,
acceptance inputs and stop gates. This includes otherwise easy-to-miss details:

- Typed captured cells and generic visitation; value-free templates; per-textual-
  occurrence parameters; structural list arity; canonical fingerprints.
- Exact normal SG output, public registrars, final-consumer rooting, closed row
  registrations and schema/physical-output duplicate diagnostics.
- Session admission and single-consumption rules; lazy single-use streams;
  command initialization cleanup limited to the actual factory-owned window.
- Logical versus physical result layouts, optional-child presence, strict NULL
  handling, checked conversion provenance and bounded nested JSON decoding.
- Pure profile-rule dispatch, scope/precedence/CTE/window/DML rules, explicit
  unsupported semantics, SQLite scalar proofs/RETURNING and MariaDB JSON budgets.
- Seven public packages, eleven pure-core assemblies, exact dependency closure,
  isolated consumers and the necessary narrow existing-runner extension.

The final Design pin and graph are the authority; an implementer returns a real
contradiction to the contract owner rather than designing a second protocol.
No throw-only declaration sample or research adapter is a production implementation.

## Actual continuation evidence

The principal environment was Debian13 Linuxx64, .NET SDK11.0.100 / C#15 / GCC14,
using isolated official toolchains and fixed sources. Individual suites overlap;
the following counts must not be added into an invented total.

| Experiment | Observed result and boundary |
| --- | --- |
| Original Dapper.AOT and runtime reuse | Explicit typed DynamicParameters and a known DTO completed a runtime small-DSL SQLite path; the fault-focused suite ended at96 assertions. Object-template bag construction published but failed in Reflection.Emit natively. An open generic vanilla call was not intercepted and produced DAP016 Info, requiring the planned elevated diagnostic gate. |
| Four-profile mature runtime | SQLite3.53.4:92; PostgreSQL18.7:99; MySQL8.4.11:97; MariaDB11.8.10:97 assertions. These include representative scalar, advanced and nested paths, not every proposed public operation. |
| Typed-cell visitor closure | A separate13-check suite covered SQLite3/PostgreSQL4/MySQL3/MariaDB3, exercising the closed generic visitor/provider seam without runtime generic construction. |
| Cancellation and timeout | Network-provider cancellation completed at about252/268/255ms, one-second command timeouts and subsequent connection reuse passed. A MySQL SLEEP-based first fixture had the wrong expectation and was replaced with the recorded row-scan query. |
| Normal SG and final-consumer roots | Core/Runtime/Models/Consumer with actual generated Dapper factories passed21 Native AOT checks, rerun after the rooting correction with the same21 checks; a separate7-check closed-row registration suite passed. Native publishes had zero warnings. Library-only initialization failed natively despite managed success, which directly caused the final-consumer registrar design. |
| Analyzer and schema host | netstandard2.0/Roslyn4.14/Immutable9 generator compiled and loaded in SDK11/Roslyn5.12 with zero warnings. Portable schema declarations compiled against net11 and netstandard references with zero warnings. This is not final NuGet/IDE consumer acceptance. |
| Staged interceptor alternative | Ordinary SG output yielded zero Dapper interceptors, experimental pre-compilation output and physical source each yielded one; a stable physical prebuild route passed3 native checks. The experimental compiler facility is not required by the default. |
| Native Java/JDBC bridge | C# Native AOT → GraalVM shared library → SQLite JDBC → typed DTO passed27 assertions, without a JVM/JIT process. The shared library was16.38MiB plus about1.1MiB SQLite native library; build1m26s/peakRSS1.32GiB, Java heap128MiB. One Xerial deprecated-argument warning remains explicitly recorded. |
| Java boundary-only timing | About22.78–24.32ns per bridge ping versus3.27ns C# noinline control. This measures a boundary, not database throughput or Java heap allocation. |
| Additional real SQL cases | Ordered nested SQL was exercised on PostgreSQL/MySQL/MariaDB. MariaDB46-byte budget succeeded at46 and rejected45; a UTF-8/quote/NUL case succeeded at88 and rejected87. SQLite multirow scalar returned its first row, and qualified RETURNING failed while unqualified target columns worked. |
| Common signature checks | Split Contracts/Types/Language/Rendering/Nested/dialect declarations and extended positive consumers compiled with zero warnings; incompatible operands failed CS1503. Throw-only declarations check accessibility/type shape, not behavior. Final added surfaces retain Foundation's full compile gate. |
| Actual runtime signature checks | Dapper.AOT CommandFactory/RowFactory and selected sync/async/stream/nonquery methods compiled. Contracts/metadata had zero warnings; bare csc with net11 references plus Dapper's net10 reference emitted two visible CS1701 framework-unification warnings, made nonfatal only in this signature experiment. It is not new native proof or a zero-warning overall claim. |
| LINQ alternatives | EF's runtime QueryCompiler path has an explicit native compilation gate. Three LinqToDB6.4.0 attempts respectively failed strict trim/AOT diagnostics, trimmed SqliteTransaction reflection, then trimmed SqlExt/AsyncFactory initialization after an explicit SQLite assembly root. Later diagnostic builds retained254 IL2026 and106 IL3050 warnings each. No successful LinqToDB native query is claimed and no universal impossibility is inferred. |

Database and native build processes used by these experiments have stopped. The
selected implementation route does not depend on running research services.

### Controlled cost comparison and its limits

The SQLite comparison used the same two parameters/two rows,1,000 warmups,
20,000 operations per round, seven rotated rounds and CPU affinity. First-campaign
median microseconds / allocated bytes per operation were: direct14.024/1832,
original static15.259/2104, original explicit bag15.982/2664, runtime bag15.893/2664,
object layout14.864/2024 and small full DSL15.935/4208.

A follow-up included typed cells: median15.015us/2072B, versus original explicit
bag17.210us/2664B; typed bind-only317.03ns/480B versus bag739.89ns/960B. Allocation
savings were592B per complete operation and480B per bind in those probes. Timing
variance was too wide for a strict speed ranking or parity claim. The final full
public wrappers, strict mapping and ownership guards were not all in those probes.
ORM-PERFORMANCE fixes future public-path comparisons, budgets and noisy-run rules;
those prospective gates have not passed merely because the research is promising.

## Source pins and inheritance

| Upstream | Pinned revision |
| --- | --- |
| jOOQ3.21.10 | `3c58109e7ab69772de75e640852935ee7e284177` |
| Dapper.AOT1.1.0 | `0e071bf05e54caecfa98c885b075fa3e247f3ecc` |
| Dapper2.1.100, original-bag control | `188094784256da61d7a37c43ea54c64213c2ce7c` |
| Npgsql11.0.0 | `4d174200ed48e3e3ab16419dbf84dd655da59de6` |
| EF/Microsoft.Data.Sqlite11.0.0 | `9e685c7a52d1a344d133a3d370e458db97417b3f` |
| MySqlConnector3.0.0 | `95875a195369f0dd804f63ded2f95da3fed59ec2` |
| LinqToDB6.4.0, diagnostic alternative | `82fbf0f91399cc8c9cea22d09dcae20e4d7568c6` |

Design source maps distinguish unchanged dependency reuse, algorithm adaptation,
C# representation changes and Korda-owned composition. Dapper.AOT's selected net10
runtime dependency group does not require Dapper; Dapper is a control dependency,
not a hidden default Execution dependency. Compiler/linker build tools and analyzer
private dependencies are not misrepresented as application runtime requirements.

## Independent review and repaired seams

Independent execution, generation and Java/SQL owners reviewed other owners'
authored specifications; the coordinator reconciled shared decisions and inspected
existing product CI read-only. Findings repaired during this continuation include:

1. Ordinary SG output is not automatically input to Dapper's generator. The default
   emits direct runtime subclasses; public registrars and final-consumer roots fix
   the observed Native AOT library-initializer gap.
2. Invocation identity, lazy stream admission, scalar/row/dynamic registration,
   typed parameter visitation and projection-specific prebound readers are explicit.
   Empty-result runtime behavior is preserved rather than claiming unexecuted
   physical reader validation.
3. The command cleanup override covers failures before its factory return. It does
   not claim to intercept later upstream connection/transaction/timeout setters;
   supported providers prevalidate and require no concurrent caller resource mutation.
4. Physical/logical nested layouts, optional presence, child access, shared JSON
   budgets and whole-reader validation are consistent. Ordered collections require
   order terms, with ties explicitly unspecified; there is no hidden key-proof rule.
5. Rendering uses Contracts rules/visitor seams; concrete dialects depend inward
   on pure language/advanced/nested modules. Contracts and Nested friend-assembly
   access are explicit. Scalar degree/cardinality, returning scope and integer
   arithmetic/cast conversion representations are fixed.
6. SchemaModel is portable where source-linked; the analyzer and CLI have separate
   host/dependency boundaries. Generated table keys/registrars and physical versus
   AdditionalFiles modes have deterministic names and duplication behavior.
7. Existing product package validation originally expected one target archive and
   no NuGet dependencies. The plan now fixes candidate dependency staging,
   NW_DEPENDENCY_FEED/MANIFEST, exact owned/external pins, hashes, whole closure
   validation and dependency-first publication, preserving the old product branch.
8. The graph separates start from acceptance, adds actual rendering/schema/nested/
   provider/package inputs, and leaves all four mandatory profiles independently
   startable after Foundation. Packet commands and scopes are reconciled with it.

This is scoped independent research/specification review, not independent product
acceptance or exhaustive coverage of the entire jOOQ implementation.

## Revisions and document checks

| Repository/milestone | Confirmed revision and observation |
| --- | --- |
| Design main | `80746769f11874ae917e17a0f02f5ee47a3e250d` |
| Plan main | `911c9764d0bfe10e78862251b43fcf108a8696e8` |
| Historical first Design delivery | `0c5f2c20cca4e386ac8f18c7a3d4c777f7f985d5`; superseded execution choice, valid bounded first-phase observations retained |
| Historical first Plan handoff | `e74b80af1df5377f1af473925b2e1dfd5abae5f2` |
| Continuation opening/progress | Plan `fb0079f649611927ac48ecab6486e35f69cdea91` and `74ccb558cb533b3ea6ab88d07eb66fa4b1922562` |
| Published mature-reuse Design checkpoint | `b67317b2a89245fe82337b9b69e2748626ac67cb`; twelve formal Markdown files, no product code |
| Checkpoint Design local PR selection | Passed; zero checks selected for registered prose |
| Checkpoint Design GitHub CI | [Run46179904662](https://github.com/IzuSharp/Korda-Design/actions/runs/46179904662) succeeded at the b67317b2 checkpoint |
| Current final-delivery checks | Pending final cross-file edits, exact final Design pin and the resulting Plan/Design heads; do not reuse checkpoint results as new-head evidence |

The first delivery's Plan full/PR checks passed five registered checks, including
48 CI self-tests,114 historical task IDs and30 ORM IDs. Historical GitHub runs
[Design46168738533](https://github.com/IzuSharp/Korda-Design/actions/runs/46168738533)
and [Plan46168697427](https://github.com/IzuSharp/Plan/actions/runs/46168697427)
remain historical evidence, not the current continuation's checks.

A file cannot contain the hash of the commit that first contains that exact file.
Recorded substantive revisions plus the current branch/PR head identify subsequent
handoff-only commits. Consult the existing PR Checks tabs for the exact current
head instead of treating any older recorded milestone as the latest revision.

## Historical first-phase observations

Retained earlier work includes the selected-source jOOQ semantic mapping; Java
SQL-only oracle with two34-assertion branches; five actual SQLite SQL assertions;
two11-assertion pure C# native runs plus negative generic compilation; eight native
offline schema-generation assertions and negative schema/typed-comparison cases;
and a bounded Dapper dynamic SQL/known DTO native check. These were not rerun merely
to increase counts. The first own-binder/projector architectural default is
superseded by the current mature-runtime decision.

## Next action and stop boundary

Finish the final shared-surface corrections and independent consistency review,
publish Design, pin its exact head from Plan, run normal local and GitHub document
checks on both heads, update the existing PR descriptions and this handoff, then
stop for the user's paired review. No further equivalent Native AOT experiment is
needed to choose a route. No hidden product implementation should be started.

After later explicit product authorization, read the then-current Korda rules and
begin ORM-FOUNDATION from the accepted immutable Design/Plan revisions. Complete
its actual shared contract/API/native data tests, then start the independent
module owners against that surface. Real four-profile integration, exact package
consumers, full public-path performance, supported-platform gates and independent
product acceptance remain future work. Only a separately accepted concrete cutover
and retirement scope can migrate or delete the old implementation.
