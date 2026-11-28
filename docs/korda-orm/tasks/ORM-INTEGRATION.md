# ORM-INTEGRATION — compose and verify the selected mature runtime

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Frozen decision and input contract

Compose the graph-pinned Design `implementation-spec.md`, `contracts.md` ORM-C01–C06,
`mature-execution.md`, `generation-integration.md` and the accepted leaf modules.
The selected executor is Dapper.AOT's existing Command/RowFactory runtime. Do not
substitute a Korda reader loop, reflection mapper, JDBC bridge or a new scheduler.
The original Dapper.AOT controlled-bag route and direct providers are independent
controls. The integration task consumes the exact generated Korda adapters, not the
small research probe's permissive UserRows implementation.

Start after ORM-FOUNDATION supplies the frozen source signatures and fixture types.
The fixture runner and profile routing can be authored immediately against its test
doubles. Acceptance requires the real mandatory modules listed in the graph:
language/types, renderers and four dialect profiles, schema/generator, execution and
three provider leaves, advanced/nested, oracle, CI and exact package outputs. Parser
remains optional. No provider waits for another provider's implementation to start.

## Files owned by this task

| Path | Required implementation |
| --- | --- |
| `tests/Orm/Integration/Korda.Orm.Integration.csproj` | Executable net11.0 consumer with conditional references for exactly the requested provider; Native AOT publish enabled by the native command |
| `tests/Orm/Integration/Program.cs` | Parse `--profile`, `--cases`, `--connection-env`; dispatch the selected profile; nonzero exit on any failed required case |
| `tests/Orm/Integration/Fixture.cs` | Create/reset only the named disposable fixture; construct independent expected rows without querying through Korda |
| `tests/Orm/Integration/QueryCases.cs` | INT-Q01–Q12 below through the real Fluent/render/bind/generated/execution pipeline |
| `tests/Orm/Integration/LifetimeCases.cs` | INT-L01–L10 below; state/disposal/cancellation assertions |
| `tests/Orm/Integration/MutationCases.cs` | INT-D01–D04 through actual mutation render/bind/Execute/returning paths |
| `tests/Orm/Integration/AdvancedCases.cs` | INT-A01–A07, with exact provider applicability and negative cells |
| `tests/Orm/Integration/PackageCases.cs` | Independently restored consumer checks and managed/native dependency closure |
| `tests/Orm/Integration/check.py` | Local/CI entry; select a profile, publish once, run the exact produced binary, summarize assertions and fail closed |
| `tests/Orm/Integration/README.md` | Maintained commands, expected fixture results and supported test environment; no raw samples/log archive |

The CI owner registers these paths and real dependencies in the shared module
registry. This task submits the exact registration change to that owner; it does
not edit shared workflow/registry files concurrently. Leaf implementation defects
return to the owning task. Do not modify historical product tests or old engines.

## Exact common fixture

Use a separately created disposable database (or SQLite file). Never infer a
permission to drop arbitrary tables in a user database. Within that fixture create:

```sql
CREATE TABLE departments(id BIGINT PRIMARY KEY, name VARCHAR(100) NOT NULL);
CREATE TABLE users(
  id BIGINT PRIMARY KEY, name VARCHAR(100) NOT NULL, age BIGINT NULL,
  active BIGINT NOT NULL, department_id BIGINT NULL
);
INSERT INTO departments VALUES (1,'Engineering'),(2,'Operations');
INSERT INTO users VALUES
  (1,'Alice',32,1,1),(2,'Bob',18,1,1),(3,'Carol',NULL,0,2),
  (4,'Dana',44,1,2),(5,'Eve',18,1,NULL);
```

Generate the table model from its offline schema input. Define known result types
User `(long Id, string Name, long? Age)`, JoinedUser `(long Id, string Name, string?
Department)`, and DepartmentTotal `(string Department, long Total, long? MaxAge)`.
Use the final generation attributes and factory registration from implementation-spec;
do not write a test-only reflection mapper or bypass the generated factory.

Build a query from typed users.Id/Name/Age/Active fields. All projection labels and
physical parameter placeholders must come from the real renderer. Compare SQL and
layout with ORM-ORACLE, then compare each returned cell with a separately authored
direct-provider command using identical SQL, parameter types/values and transaction.
Never call the Korda binder to prepare the control command.

## Query cases and exact expectations

| ID | Input | Required result |
| --- | --- | --- |
| INT-Q01 | No WHERE, zero arguments; order by id | IDs 1,2,3,4,5; Carol.Age is null |
| INT-Q02 | Active=1; optionally Age>=20; optionally Name=Alice | No options: 1,2,4,5; age only: 1,4; name only or both: 1; bind exactly 1/2/2/3 entries |
| INT-Q03 | Reuse one Id slot in `Id>=p AND Id=p`, p=2 | ID 2; two physical occurrences in textual order; PG uses $1/$2 with empty names, others @p0/@p1 |
| INT-Q04 | Two distinct slots both labelled `id`, values 1/2, joined with OR | IDs 1,2; slots remain distinct and no dictionary overwrite occurs |
| INT-Q05 | `Age = typed-null` and separate `Age IS NULL` | First empty; second ID 3; no rewrite of equality into IS NULL |
| INT-Q06 | Id IN [], [2], [1,3,5] | Empty, ID 2, IDs 1,3,5; binding rejects an invocation arity different from the rendered template |
| INT-Q07 | Name parameter `Alice' OR 1=1 --` | No rows; parameter content absent from SQL and default diagnostics |
| INT-Q08 | LEFT JOIN departments into JoinedUser | Five rows; Eve.Department=null; Alice.Department=Engineering |
| INT-Q09 | Inner join/group by department, COUNT and MAX(age) | Engineering=(2,32), Operations=(2,44) |
| INT-Q10 | Distinct valid WHERE shapes to User; same shape to another known projection | Correct rows for both mappings; each uses its generated factory |
| INT-Q11 | Required slot missing, conflicting logical type, wrong provider/profile; separate unused-superset case | BIND-001/BIND-002/EXEC-001 before command creation; unused captured/explicit slots remain allowed and produce no DbParameter |
| INT-Q12 | Nonempty result with wrong width/order/alias/type/required NULL; empty result | Strict generated mapping fails before producing a wrong row; empty result returns empty and does not promise runtime schema-drift detection; direct-reader oracle checks its schema |

For INT-Q12 induce schema differences through the public SqlTemplates.Declare<T>
caller-declared SQL boundary with explicit result metadata. Do not corrupt a supposedly immutable rendered template. Required NULL
is a row-conversion failure; nullability metadata alone is not a substitute for
checking actual cells.

## Lifetime and failure cases

| ID | Procedure | Required observation |
| --- | --- | --- |
| INT-L01 | Execute with already-open borrowed connection | Connection remains open; command/reader disposed once |
| INT-L02 | Execute with initially closed borrowed connection | Runtime opens it and restores closed state; connection object itself is not disposed |
| INT-L03 | Execute via owned data-source connection | Reader/command disposed after buffered completion; connection stays owned by the session until its DisposeAsync, then is disposed |
| INT-L04 | Stream all rows, then repeat with `break` after row 1 | Full stream gives 1–5; early exit gives 1; resources released and a subsequent query succeeds |
| INT-L05 | Dispose before first MoveNext, duplicate enumeration, overlapping MoveNext, repeated BoundCommand | No command for the first; EXEC-004/005/006 for the corresponding invalid reuse; pre-cancel does not consume the command; no hidden Task.Run |
| INT-L06 | Pass a pre-cancelled token | No provider command sent; OperationCanceledException carries the caller token |
| INT-L07 | Network query waits 10 seconds; cancel after 250ms | Cancellation observed within the five-second test bound, then same connection can execute SELECT 1; never apply this promise to SQLite native interruption |
| INT-L08 | Set explicit command timeout 1 second without caller cancellation | Provider timeout evidence retained and distinguishable from caller cancellation; subsequent usable connection or explicit broken state recorded |
| INT-L09 | Insert id=6 inside explicit transaction; read within it; rollback; then update Alice age=33 and commit | Six rows only before rollback; five afterward; committed age becomes 33; reset fixture before unrelated comparisons |
| INT-L10 | Inject CreateParameter/bind, ExecuteReader, Tokenize, Read and Dispose failures | Every acquired resource has an accountable owner; initialization catch disposes its local command; binding+Dispose double fault retains the binding failure with KordaCleanupException; post-handoff dual-fault behavior is recorded without claiming the initialization patch covers it; no retry after ambiguous commit |

INT-L02 uses the low-level OrmSession.Borrow with already verified immutable
provider services and a connection subsequently closed by the test. The public
provider BorrowAsync convenience intentionally requires an open connection to
verify its profile. This distinguishes mature operation state restoration from
network/profile acquisition.

For PostgreSQL INT-L07/L08 use `SELECT CAST(1 AS BIGINT) FROM pg_sleep(10)`.
For MySQL/MariaDB use `SELECT id FROM users WHERE SLEEP(10)=0 ORDER BY id`.
Do not use a standalone MySQL SLEEP expression as an error oracle: its documented
interrupt result may be 1 without an error. SQLite tests pre-cancel, explicit
between-read boundaries and busy timeout separately; they do not manufacture
in-flight interruption with a worker pool.

INT-L10's deterministic fakes count creation/disposal and ensure failure occurs at
the requested phase. A finalizer or connection-wide implicit cleanup does not count
as exactly-once explicit command ownership. Commit-failure injection classifies an
unknown outcome without asserting a real server committed or rolled back.

## Mutation composition

Add INT-D01–D04 in `MutationCases.cs`. D01 inserts ID6 through Mutation.Execute,
checks affected count1 and a direct SELECT, then rolls back the caller transaction.
D02 updates Alice age33 through ExecuteAsync, checks affected count under the
profile's declared driver setting and commits explicitly. D03 executes supported
INSERT/DELETE RETURNING as ReturningMutation<User> with the ordinary generated
query mapper; unsupported MySQL/SQLite contexts fail the dialect diagnostic before
command creation. D04 reuses a BoundMutation and gets EXEC-006; a new template Bind
works. No lane appends an implicit generated-key query or auto-retries an unknown
commit outcome.

## Advanced and nested cases

| ID | Profile | Required live test |
| --- | --- | --- |
| INT-A01 | PostgreSQL | `SqlArray<int>` [2,4,8], JsonbText containing n=17 and O'Reilly, and SqlRange<int> [1,5); closed provider conversions and neutral typed results; non-1 PG lower bounds normalize to sequence order |
| INT-A02 | MySQL and MariaDB separately | Explicit JSON parameter; JSON_EXTRACT/JSON_UNQUOTE yields number 17 and unchanged text; profile-specific JSON storage semantics remain recorded |
| INT-A03 | All four | Department with Nested.Collect returning ImmutableArray<User> through positional row-array JSON and generated readers; Engineering is Alice/Bob in declared total order, retaining duplicates |
| INT-A04 | All declared JSON profiles | Distinguish SQL NULL, JSON null, empty object and empty child collection; test missing/extra JSON cells, wrong row arity and invalid scalar token type |
| INT-A05 | Profile applicability matrix | Every declared advanced codec's boundary values and round trip; unsupported array/range/composite/storage cells fail explicitly before send |
| INT-A06 | Native consumer | Known JsonCodec<T> uses supplied JsonTypeInfo<T>; nested uses generated typed cell readers; Dapper factories/provider codec closures are rooted; reflection JSON and dynamic IL are absent |
| INT-A07 | All four | Optional nested presence0 returns None without reading required child cells; present all-null nullable payload remains Some; presence1 required NULL fails; physical/logical degree and collection-width distinction are enforced |

The research's nested smoke case proves known-type transport/decoding feasibility,
not all INT-A03–A07 semantics. This task must run the stronger production corpus.

## Local commands and CI routing

`check.py` has this fixed CLI contract:

```sh
python3 tests/Orm/Integration/check.py --profile sqlite --mode native --cases all
python3 tests/Orm/Integration/check.py --profile postgres --mode native --cases all --connection-env KORDA_TEST_POSTGRES
python3 tests/Orm/Integration/check.py --profile mysql --mode native --cases all --connection-env KORDA_TEST_MYSQL
python3 tests/Orm/Integration/check.py --profile mariadb --mode native --cases all --connection-env KORDA_TEST_MARIADB
```

The runner first executes its fixture preflight, then uses `dotnet publish -c Release
-r linux-x64 -p:PublishAot=true -p:TreatWarningsAsErrors=true` for the selected
consumer, executes that exact native file, and verifies RuntimeFeature.IsDynamicCodeSupported
is false. Generator/fallback diagnostic policy is part of the consumer project.
Use the configured local package feed for package acceptance; do not fall back to
an older installed package if the exact candidate package is absent.

CI module IDs are `orm-integration-sqlite`, `orm-integration-postgres`,
`orm-integration-mysql`, and `orm-integration-mariadb`. Each depends on actual common
source modules and its provider/profile only. An isolated provider change selects
its integration leaf, while a shared contract/runtime/generator change selects all
actual consumers. Local commands remain usable without GitHub. Long benchmarks and
raw experiment archives are excluded from routine integration and document CI.

## Acceptance and stop

Deliver per-profile case IDs with actual results, exact native/package/server inputs,
remaining unsupported cells and a source-pinned candidate for ORM-PERFORMANCE and
ORM-ACCEPTANCE. Inspect generated code, required fallback diagnostics and package
closure. A zero exit from an empty case selection is an error. Final acceptance
requires all four mandatory profiles and the declared advanced/nested corpus;
PostgreSQL/SQLite being the first validation wave grants no partial-release waiver.

Stop after the reviewed integration scope. Do not publish, cut over, merge or delete
historical code. Any failed mandatory case returns to its actual owner and remains
failed until its real implementation passes.
