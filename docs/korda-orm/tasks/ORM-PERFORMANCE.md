# ORM-PERFORMANCE — finite, attributable public-path measurements

Status: `planned_candidate`; product implementation is **not authorized**.

## Fixed question, inputs and dependencies

Measure the accepted C# implementation's additional construction, rendering,
binding, strict mapping and invocation-policy costs relative to the mature
execution controls. The default architecture is already fixed: Dapper.AOT 1.1.0
runtime + typed-layout factory + generated mappings. This task verifies its budget;
it does not choose a new executor or restart historical C++ optimization work.

Read the graph-pinned Design implementation-spec, mature-execution, validation,
execution-aot and ORM-C03/C04/C06. Pin the product revision, .NET SDK/runtime,
Dapper/Dapper.AOT, three drivers, four actual server versions and release options
before the campaign. Research figures in mature-execution are mechanism evidence:
the small prototypes did not include the full public session lease, frozen values,
strict generated mapping or final one-occurrence-per-parameter policy. Do not paste
those figures into a product performance acceptance report.

Start after ORM-FOUNDATION to build fixtures and harness. Final acceptance requires
ORM-INTEGRATION's real implementation and every corresponding correctness lane.
Harness readiness does not accept performance. jOOQ/GraalVM is a separately labeled
language/runtime reference; it is not the .NET execution baseline.

## Files and exact harness roles

Own `benchmarks/Orm/` and its maintained README only. Do not edit product providers,
DSL, generator or shared contracts to hide a result; return fixes to their owners.
Foundation/CI own project registration. Required files:

| File | Fixed responsibility |
| --- | --- |
| `Korda.Orm.Benchmarks.csproj` | net11.0 Native AOT executable, pinned product/driver/control references, Release and warning policy |
| `Program.cs`, `Options.cs` | Closed CLI parser, explicit profile/mode/workload/campaign/connection-env/output options |
| `Fixture.cs` | Deterministic data and expected checksums; setup/reset outside measured intervals |
| `Workloads.cs` | The fixed workload table below; creates one logical scenario consumed by every comparable path |
| `Paths/DirectDriver.cs` | Direct typed parameter/reader lower-bound control |
| `Paths/OriginalStatic.cs` | Concrete DTO original Dapper.AOT calls and generated-coverage assertion |
| `Paths/OriginalBag.cs`, `RuntimeBag.cs` | Fresh explicit-entry bags, no object template; same actual generated row factory body for attribution |
| `Paths/RuntimeLayout.cs` | Infrastructure-only known-layout control, deliberately separate from public product endpoints |
| `Paths/PublicPreRendered.cs` | Template.Bind(values).ToList(session), fresh BoundCommand each iteration, full validation/lease/strict mapping |
| `Paths/PublicFluent.cs` | Actual Query construction + public ToList/ToListAsync; same SQL/result as its controls |
| `Measurements.cs` | Warmup, rotation, counters, timer, result sink and immutable sample output |
| `Summary.cs` | Round-level paired ratios, median/min/max, confidence interval and budget classification |
| `manifest.json` | Fixed workload/sample/budget definitions, schema version1 and source/toolchain pins |
| `run.py` | Builds explicit native consumer, runs bounded campaigns, validates sample schema and emits summary |
| `README.md` | Commands, interpretation, environmental limitations and accepted concise conclusions |

The manifest is version-controlled before implementation measurement. Temporary
samples, full logs, databases, profiler traces and binaries stay out of Design/Plan;
maintain only meaningful summaries and reproduction instructions. Source-derived
control factory bodies retain attribution and the upstream pin.

## Comparable paths and what is inside the timer

Every execution path uses the same already-open connection, SQL text, physical
parameter count/order/types/values, DTO shape, row count, buffer mode, preparation
state and fixture. Initial campaign disables pooling/auto-prepare/command recycling;
there is no template or mapping-shape cache in the product baseline. A separate
pool-open lane reports connection acquisition and is not mixed into query costs.

| ID | Timed path | Construction boundary |
| --- | --- | --- |
| P0 | Direct driver command, typed parameters, reader and DTO materialization | Create/dispose command/reader each operation; known SQL, same parameter values and DTO constructor |
| P1 | Original Dapper.AOT concrete Query<User> with static argument object | Create the tiny anonymous/static argument object per call; generated call must be intercepted |
| P2 | Original Dapper.AOT concrete Query<User> with explicit bag | Create/add a fresh bag per call, then execute |
| P3 | Explicit mature Runtime + same explicit bag | Same bag creation and same emitted User row-factory body as P2 |
| P4 | Explicit mature Runtime + prebound layout | Known layout/value cells; full command creation/binding/reader cleanup, but no public session/consumption wrapper |
| P5 | Public pre-rendered Korda path | Frozen template/ParameterValues are outside timer; Bind creates a fresh single-use BoundCommand inside timer; ToList runs the actual session/strict mapping path |
| P6 | Public full Fluent Korda path | Construct the fixed AST and captured/frozen values, render, bind and execute inside timer |

P4 helps attribute the policy adapter; it must never be labeled the public product
result or used to pass P5's budget. P5 includes every declared Korda preflight and
lease cost. A BoundCommand is never illegally reused to improve a number. P1 has
finite statically known shapes; dynamic-cardinality workloads use P2/P3 as their
original-library controls, not an invented infinitely generated static baseline.

For original paths, inspect generated code and fail setup if the expected call
was not intercepted. Elevate the reviewed DAP non-generation diagnostics as
ORM-EXECUTION specifies. Do not benchmark a vanilla Dapper fallback by accident.
Use a dedicated generated factory shared by P2–P4 to isolate binding-path costs;
P5/P6 use the actual generated strict product mapping and are labeled accordingly.

## Fixed datasets and workloads

SQLite uses a unique file, not an in-memory replacement, one already-open
connection and no timed setup. Create users with IDs1..1000, name
`user-` plus invariant five-digit ID, age NULL for multiples of5 and otherwise
`18 + (id % 50)`, active=1 except multiples of3, and department_id=1+(id%8).
Create departments1..8 with invariant `department-<id>`. Server lanes use the same
logical values and equivalent profile SQL. The small canonical five-user fixture
is retained separately for contract regression tests, not mixed with these samples.

| Workload ID | Exact operation / expected output | Applicable paths |
| --- | --- | --- |
| W00/W01/W02/W10/W100 | `id >= first AND id < last ORDER BY id`, first=1, last=1/2/3/11/101; return0/1/2/10/100 User rows, two parameters | P0–P6; original static P1 is the primary budget control |
| W-PRED | Four predicate masks: active=1 always, optionally age>=20 and name=user-00001; rotate mask by operation index modulo4 | P0–P6, with four inspected concrete P1 shapes |
| W-IN0/1/16/256 | `id IN (frozen list)` using IDs1..n; n=0/1/16/256, empty=false; sorted IDs exactly1..n | P0/P2/P3/P4/P5/P6; one physical parameter per list element |
| W-REPEAT | `(id=@p0 OR id=@p1)` with one logical slot1 emitted twice | Two physical parameters in every compared path, one returned row |
| W-JOIN | Users1..100 left join their departments, ordered by id |100 known JoinedUser DTOs; same aliases/getters and null policy |
| W-AGG | GROUP BY department_id, count and max(age), ordered by department_id |8 known aggregate DTOs, exact direct-driver expected values |
| W-NESTED | Eight department envelopes with fixed ordered child tuples and the accepted nested decoder | P0/P5/P6 only; each profile's approved SQL and byte budget, never compare unordered versus ordered SQL |
| W-SHAPE | Alternate the four W-PRED shapes with no cache; new template each operation | P6 and a separately labeled render-only lane |
| W-PAYLOAD | Two pre-captured text values of1 byte and1,048,576 bytes with otherwise identical AST/SQL type | Render-only: values must not enter SQL, template fingerprint or template-owned allocation |
| W-STREAM | Read100 rows completely, then a separate early-break-after-one scenario | Public StreamAsync and same mature/direct async streaming semantics; each enumeration disposed |

Do not execute unsupported profile/workload combinations by silently changing their
semantics. Report the already-approved capability rejection; required integration
coverage must separately confirm it. Arrays/nested/JSON are not compared against
a scalar-only baseline while claiming the same work.

## Isolated measurements and state boundaries

Use separate explicit operations rather than subtracting unrelated full-query
means. The isolated lanes are:

1. Construct immutable AST/captured values, without render or driver.
2. Render a prebuilt AST with a fixed RenderShape, without values or driver.
3. Bind frozen ParameterValues to a pre-rendered template and create its invocation.
4. Convert a known layout to an original explicit DynamicParameters bag.
5. Create/bind/dispose a driver command without executing it, separately for bag
   and typed layout. Include fresh bag creation in its named lane and provide the
   conversion-only lane above, so totals are interpretable.
6. Tokenize a real reader's first valid row and then map subsequent rows through
   the actual factory, measured only in a dedicated fixture with correct reader
   lifetime. Label the row-only fixture separately; never claim subtraction of
   full-driver time isolates mapping perfectly.

No prevalidation, snapshot, strict factory creation or disposal is moved outside
P5/P6's specified timer merely to improve its result. Pre-captured values in
render-only lanes are intentionally outside; that is a different question.

## Bounded measurement algorithm

1. Validate result count, every DTO field and a deterministic checksum for every
   scenario/path before any timing. Run integration negatives first; do not time
   an incorrect or fallback path. Reset any mutation fixture outside timed loops.
2. Build native Release once per exact campaign revision. Assert dynamic code is
   unsupported and record publish options, executable byte count, CPU, affinity,
   OS/kernel, memory limit, SDK/driver/server versions and relevant connection
   options. Redact credentials/connection strings. Record preparation/pooling and
   whether the host is shared; do not describe a shared host as dedicated.
3. Run two independent process campaigns. Each execution path warms for1000
   operations; isolated lanes warm for2000. Each campaign has seven rounds.
   Synchronous SQLite batches contain20,000 operations per path/workload. Network
   async batches contain200 operations; nested/stream batches contain200. These
   counts are fixed before measurement and bounded by a per-process30-minute cap.
4. In round r visit path `(p+r) mod pathCount`. Use Stopwatch.GetTimestamp around
   only its loop. Consume count and a field checksum through a live sink; assert
   final sink consistency. Run full forced collections only between measured
   batches, outside their timers. Do not force a collection per query.
5. Synchronous SQLite records GetAllocatedBytesForCurrentThread before/after and
   divides by operations. Async/network lanes use process-wide
   GetTotalAllocatedBytes(precise:true) and report that scope; thread-local counters
   across awaits are invalid. Record GC.CollectionCount deltas separately. No
   unrelated application work runs inside the benchmark process.
6. Samples contain campaign, round, workload, path, operations, elapsed ticks,
   allocated bytes, GC deltas, result checksum and setup fingerprint. Preserve
   every valid sample. Do not discard a slow round because it changes the median.
7. Report median/min/max ns/op and B/op over seven rounds. For relative results,
   pair equal campaign/round/workload values, compute seven ratios, then their
   median. Use deterministic bootstrap seed1729,2000 resamples of whole paired
   rounds for a95% interval; never treat20,000 operations inside one interval as
  20,000 independent statistical samples.
8. If the direct-driver control's round coefficient of variation exceeds15%, or
   throttling/competing work invalidates the setup, mark the campaign
   `measurement-invalid`. Permit exactly one fresh process replacement with the
   same inputs; retain the invalid record and explanation. If still invalid, stop
   with unresolved measurement. Do not lower iteration counts, change budgets or
   select a favorable subset. Run correctness independently of this timing result.

Use Linux taskset when a stable CPU allocation is available; affinity failure is
recorded and investigated before budget acceptance. Network latency represents
local server+protocol+query+client work; it is not attributed entirely to Korda.
Do not infer a universal ordering from overlapping noisy intervals.

## Initial implementation budgets, fixed before product measurement

These are engineering gates for the stated workloads, not a promise derived from
the temporary research prototype. The contract owner reviews this manifest before
implementation begins; implementers must not tune thresholds after observing a
failure. Both valid independent SQLite campaigns must meet the gates.

| Gate | Exact pass condition |
| --- | --- |
| PERF-CORRECT | Every compared valid scenario has equal SQL intent/parameter types/result fields/checksum; required negative behavior and native coverage pass |
| PERF-PREBOUND | P5 for W00/W01/W02/W10/W100: paired median ns/op ratio to P1 <=1.35 and median extra allocation <=1024 B/op |
| PERF-FLUENT | P6 for W02, the exact two-predicate/two-parameter/two-row case: median ns/op <=max(1.75×P1, P1+10,000 ns), median extra allocation <=8192 B/op |
| PERF-VALUE-SEPARATION | W-PAYLOAD render-only output SQL/layout/fingerprint identical; allocation difference between large/small pre-captured payload <=256 B; template retains no payload bytes/reference |
| PERF-BOUNDED | W-IN256/W-SHAPE/nesting complete within the declared process cap, without unbounded global caches; report size/allocation growth against input counts, not an invented constant-cost claim |
| PERF-NATIVE | All compared consumers are actually native; intended original calls intercepted; no broad warning suppression or runtime code generation |

Network/advanced/stream timing and native binary size are reported with the exact
samples and limitations; they do not acquire ad hoc PR latency thresholds in this
initial campaign. Their correctness/native/lifetime gates remain mandatory. A
performance failure is a task failure requiring an attributed issue returned to
its module owner; it does not authorize removing strictness, snapshotting,
cancellation, physical-parameter policy or public leases to reach a number.

## Commands, CI and stop

The runner's CLI accepts exactly the documented workload IDs or `all`, profiles
sqlite/postgres/mysql/mariadb, mode=smoke/campaign, and explicit native=true.
Connection-env is required for server profiles and forbidden from being echoed.
Output is a caller-owned scratch directory; maintained summary export is a separate
explicit step. A smoke uses100 warmup/100 measured operations and one round,
asserting correctness/schema/native wiring only, with no performance pass claim.

```sh
python3 benchmarks/Orm/run.py --profile sqlite --mode smoke --native true --workloads W01 --output artifacts/orm-perf-smoke
python3 benchmarks/Orm/run.py --profile sqlite --mode campaign --native true --workloads all --output artifacts/orm-perf-sqlite
python3 benchmarks/Orm/run.py --profile postgres --mode campaign --native true --workloads all --connection-env KORDA_TEST_POSTGRES --output artifacts/orm-perf-postgres
python3 benchmarks/Orm/run.py --profile mysql --mode campaign --native true --workloads all --connection-env KORDA_TEST_MYSQL --output artifacts/orm-perf-mysql
python3 benchmarks/Orm/run.py --profile mariadb --mode campaign --native true --workloads all --connection-env KORDA_TEST_MARIADB --output artifacts/orm-perf-mariadb
```

Register module orm-performance and its actual benchmark/product dependencies.
Routine CI selects the correctness/native smoke when relevant sources change;
finite campaigns are explicit acceptance/manual jobs with supplied services and
resource limits. Do not run long campaigns on every documentation change or start
profilers indefinitely. Stop after the finite campaign, maintained source-pinned
summary, pass/fail decisions and scoped attributable fixes. Publication, merging,
package release and product cutover are not authorized by this packet.
