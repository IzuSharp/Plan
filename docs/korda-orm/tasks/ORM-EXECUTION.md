# ORM-EXECUTION — mature runtime adapter and exact invocation lifecycle

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Fixed decision, inputs and dependencies

Implement the graph-pinned Design `implementation-spec.md` section 7 and contracts
ORM-C01/C03/C04/C06, using Dapper.AOT **1.1.0** runtime unchanged. Read
`mature-execution.md` and `generation-integration.md`. Do not implement a Korda
command execution loop, row iteration loop, worker pool, connection pool, retry
policy or reflection mapper. Original DynamicParameters interception is a proved
control/optional compatibility route; the default consumes typed layout cells.

Start after ORM-FOUNDATION supplies the declarations and deterministic fakes below.
Acceptance requires ORM-TYPES, ORM-RENDER and ORM-SCHEMA, with the actual frozen
descriptor/value, template/binding and neutral schema contracts. Foundation's
declaration scaffolding permits parallel implementation; it does not replace
those behavioral acceptance dependencies.
Providers and generators develop independently against this packet; a real
provider is not required to run this module's fault/lifetime tests. Integration
later composes all real leaves. Shared signature changes return to Foundation's
contract owner before editing consumers.

## Owned files and exact responsibilities

| File under `src/Orm/Execution/` | Required content |
| --- | --- |
| `Korda.Orm.Execution.csproj` | net11.0/C#15; references Contracts, Types, Language, Rendering, SchemaModel and Dapper.AOT 1.1.0; no provider, Java/C++/Rust or Roslyn reference |
| `CommandOptions.cs` | Immutable timeout record from implementation-spec; validation helper |
| `ProviderServices.cs` | Infrastructure declarations below, provider capability and codec validation boundary |
| `BoundArguments.cs` | The immutable runtime argument carrier below; no SQL parser or untyped required object[] |
| `LayoutCommandFactory.cs` | One derived Dapper CommandFactory; typed value visitor, exact occurrence binding and defensive local-command cleanup |
| `OrmSession.cs` | Owned/borrowed connection context, immutable provider/profile/options, session lease and disposal |
| `InvocationLease.cs` | Atomic Idle/Active/Disposed state machine; no queue, semaphore wait or scheduler |
| `QueryExecutionExtensions.cs` | Query/BoundCommand/ReturningMutation typed result terminals and explicit mapping overloads below |
| `MutationExecutionExtensions.cs` | Nonquery Mutation/BoundMutation Execute and ExecuteAsync, using the same lease/consumption protocol |
| `MappingAttributes.cs` | Exact DbRow/DbColumn/DbConstructor/DbIgnore/DbCompileRow/CompiledRow/DbNested declarations from generator/nested packets |
| `ScalarCompiledMapping.cs`, `BuiltInMapping.cs`, `RowMappings.cs`, `DynamicRecordCompiledMapping.cs` | Closed scalar, explicit dynamic-record and Row1–8 registration below |
| `SingleUseStream.cs` | Lazy forwarding wrapper, one enumerator, no overlapping MoveNextAsync, exactly-once forwarded disposal |
| `Mapping.cs` | Generic static registration slot, immutable CompiledMapping and RowMember contracts |
| `Metadata/ISchemaCatalogReader.cs`, `Metadata/SchemaReadOptions.cs` | The schema acquisition interface agreed with ORM-SCHEMA; reference the neutral Schema types without allowing discovery inside the generator |

Own corresponding `tests/Orm/Execution/**`. The foundation/CI owner maintains root
projects and registration files. Do not edit providers, generator emitters,
renderers or historical native engines. The metadata interface adds a real SchemaModel
project dependency; the shared module registry must record it before acceptance.

## Exact infrastructure declarations

These names and signatures are fixed. Constructors that admit executable arguments
are internal where indicated; public infrastructure is exposed for generated and
advanced handwritten static mappings, not required in ordinary application code.

```csharp
namespace Korda.Orm.Execution;

public sealed record ProviderCapabilities(
    bool AsyncIo, bool InFlightCancellation, bool Savepoints);

public sealed record BoundArguments(
    TemplateId TemplateId,
    ImmutableArray<ParameterOccurrence> Occurrences,
    ParameterValues Values);

public sealed record RowMember(int Index, string Alias, Type ClrType,
    bool IsNullable, string? ConversionId = null);

public abstract class ProviderServices
{
    public abstract SqlProfile Profile { get; }
    public abstract ProviderCapabilities Capabilities { get; }
    public abstract void ValidateConnection(DbConnection connection,
        DbTransaction? transaction);
    public abstract Dapper.CommandFactory<BoundArguments> Commands { get; }
    public abstract void ValidateParameter(SqlTypeDescriptor type);
    public abstract void ValidateValue<T>(SqlType<T> type, T value,
        ParameterOccurrence occurrence);
    public abstract void ValidateResult(ResultColumn column, RowMember member);
    public abstract Func<DbDataReader, int, T> BindReader<T>(
        SqlTypeDescriptor sourceType, string? conversionId = null);
    public abstract Func<DbDataReader, int, DynamicCell> BindDynamicReader(
        SqlTypeDescriptor sourceType, string? conversionId = null);
    public abstract void ValidateReaderColumn(DbDataReader reader, int ordinal,
        ResultColumn expected, RowMember member);
}

public abstract class ParameterEncoder
{
    public abstract DbParameter Create<T>(DbCommand command, SqlType<T> type,
        T value, ParameterOccurrence occurrence);
}

public sealed class LayoutCommandFactory : Dapper.CommandFactory<BoundArguments>
{
    public LayoutCommandFactory(ParameterEncoder encoder);
    public override DbCommand GetCommand(DbConnection connection, string sql,
        CommandType commandType, BoundArguments args);
    public override void AddParameters(in Dapper.UnifiedCommand command,
        BoundArguments args);
    public override void UpdateParameters(in Dapper.UnifiedCommand command,
        BoundArguments args);
    public override bool CanPrepare { get; }
    public override bool TryRecycle(DbCommand command);
}

public abstract class CompiledMapping<T>
{
    protected CompiledMapping(ImmutableArray<RowMember> members);
    public ImmutableArray<RowMember> Members { get; }
    public abstract Dapper.RowFactory<T> Bind(
        ResultShape shape, ProviderServices services);
}

public static class Mapping<T>
{
    public static void Register(CompiledMapping<T> mapping);
    public static CompiledMapping<T> Get();
}
```

The project imports System, System.Data, System.Data.Common,
System.Collections.Generic, System.Collections.Immutable, System.Threading,
System.Threading.Tasks and Korda.Orm. BoundArguments
is constructed internally by the terminal from an already validated BoundCommand.
It is not an alternative public API for bypassing validation. The generic value
visitor is the Contracts-owned `IParameterValueVisitor.Visit<T>(SqlType<T>, T,
ParameterOccurrence)` seam; ParameterValues dispatches a validated occurrence to
its concrete typed cell. Scalar occurrences use ElementIndex=-1; expanded lists use
their zero-based frozen element index. The encoder returns a fully configured,
not-yet-added DbParameter. LayoutCommandFactory adds it once to the command.

Fix the internal Contracts seam as `internal interface IParameterValueVisitor`
with `void Visit<T>(SqlType<T> type, T value, ParameterOccurrence occurrence)`.
ParameterValues exposes `internal void Accept(ParameterOccurrence occurrence,
IParameterValueVisitor visitor)` to the declared friend assemblies. It resolves
SlotId through the frozen lookup, selects the scalar cell or frozen list element,
checks the occurrence's exact descriptor/index, and calls that cell's generic
Accept. Missing/type/index failures retain BIND-001/002/003. This method neither
creates a command nor boxes the stored T into a required object protocol.

CompiledMapping stores immutable member metadata, not a live reader or session.
Register uses Interlocked.CompareExchange against null; a duplicate or missing
registration is KORM-MAP-001. Bind compares the DTO's logical degree/member names
against ResultShape.Members, not the physical Columns length. Match exact aliases,
CLR/nullability and explicit conversion metadata, calling ValidateResult on scalar
leaves. Acquire each known member T's closed BindReader<T> delegate once and store
it in the immutable bound factory. Tokenize validates the entire physical column
count/order/aliases and invokes ValidateReaderColumn once per physical ordinal.
Read calls the stored typed delegates and performs no catalog lookup. Provider
codec entries implement statically closed IProviderReadCodec<T> interfaces indexed
by SQL identity/explicit conversion, with safe generic-interface checks; no runtime
generic type creation is involved. The factory is bound to this projection's
order/provider policy.
No global Type dictionary, assembly scan, MakeGenericType or unbounded shape cache
is allowed. Generated mappings are singletons; bound factories are invocation-local.

Resolve the effective read ConversionId before calling BindReader. If
RowMember.ConversionId is null, use ResultColumn.ConversionId; if the column ID is
null, use the member ID; if both are non-null and Ordinal-equal, use that one ID
once. Two different non-null IDs fail KORM-MAP-002 in Bind before command creation.
There is no implicit composition, override or second execution of equal IDs.
ValidateResult applies this exact rule, and generated/manual scalar, Row, DTO and
dynamic-record factories pass the effective ID to BindReader/BindDynamicReader.
A custom composed codec may be registered under one explicit ID; two independent
metadata IDs never imply such a composition. An expression's built-in aggregate
or cast ID therefore works with an ordinary DTO member that has no attribute ID.
For nested scalar leaves use the logical column assembled by ORM-NESTED while
retaining that leaf's explicit conversion metadata; outer physical validation
continues to inspect the actual column representation.

The built-in result IDs `cast.int16.checked` and `cast.int32.checked` are fixed
for explicit Cast expressions targeting logical int16/short or int32/int, including
their nullable variants. They are copied from the final CastNode into result
metadata and selected through the rule above. They are not parameter codecs and
do not authorize implicit narrowing of an ordinary column or arithmetic result.
MySQL/MariaDB/SQLite read their declared signed Int64/INTEGER representation and
perform checked Int16/Int32 conversion; PostgreSQL reads the native Smallint/Integer
produced by its SQL cast. A wrong declared ID/T/storage fails MAP-002, a required
DBNull fails MAP-003, and an executed checked overflow fails TYPE-005 with the
original OverflowException. Native server cast errors propagate unchanged.
Promoted arithmetic returns logical Int64/Double/Decimal with null ConversionId
and its ordinary strict reader; it does not acquire a cast narrowing exemption.

Add these overloads to the implementation-spec terminals for a deliberate manual
mapping without modifying Mapping<T>'s registered default:

```csharp
public static List<T> ToList<T>(this BoundCommand<T> command, OrmSession session);
public static List<T> ToList<T>(this BoundCommand<T> command,
    OrmSession session, CompiledMapping<T> mapping);
public static Task<List<T>> ToListAsync<T>(this BoundCommand<T> command,
    OrmSession session, CompiledMapping<T> mapping,
    CancellationToken cancellationToken = default);
public static IAsyncEnumerable<T> StreamAsync<T>(this BoundCommand<T> command,
    OrmSession session, CompiledMapping<T> mapping,
    CancellationToken cancellationToken = default);
```

Diagnostic classification is exact: an unavailable parameter codec is BIND-005;
an unavailable result codec, unknown read ConversionId or wrong closed result T
is MAP-002. A known conversion that executes and fails (including checked result
overflow) is TYPE-005. A required DBNull is MAP-003. Unsupported pure advanced SQL
operations are TYPE-004. Do not select whichever error code is convenient.

The reader delegate is the sole DBNull/null-conversion owner. It checks IsDBNull,
uses the validated logical nullability and explicit conversion policy, returns the
closed nullable T or fails MAP-003 for a required value. Generated Read does not
repeat a second IsDBNull/default-value policy. For optional nested rows, physical
payload columns are nullable but the logical child need not be: presence0 skips
its getters entirely; presence1 invokes the child's strict logical delegates.
Only the outer factory Tokenize checks the full physical reader. Nested group
relative offsets, width and collection JSON-cell arity follow ORM-NESTED's exact
ResultMember/NestedShapeDescriptor declarations; no child standalone factory
retokenizes that reader.

### Scalar and typed-row registration

The initial built-in scalar family is bool, short, int, long, ulong, float, double, decimal,
string, byte[], Guid, DateOnly, TimeOnly, DateTime and DateTimeOffset, plus Nullable<T>
for those value types. Recognition alone does not assert provider support: the
chosen SQL descriptor/codec must still validate. Unsupported CLR T has no implicit
scalar mapper. ScalarCompiledMapping<T>.Members is Empty as the one explicit
exception to DTO degree matching. Its Bind requires exactly one logical Scalar
member with physical width1, takes that invocation's actual alias, creates a
RowMember(0,alias,typeof(T),canAcceptNull) and follows ValidateResult/BindReader.
Value-type nullability is fixed by closed T; string/byte[] nullable annotations are
runtime-erased, so their scalar nullability follows the declared Field/ResultMember
SQL nullability. No fixed alias named Value is invented.

Mapping<T>.Get first returns an already registered mapping. Otherwise it accesses
BuiltInMapping<T>.Instance through an explicit static constructor, testing T only
against the fixed typeof(...) whitelist and DynamicRecord. The known scalar branch
constructs ScalarCompiledMapping<T>; the DynamicRecord branch selects the fixed
DynamicRecordCompiledMapping. Publish the default with Interlocked.CompareExchange,
retaining an already manually registered mapping rather than overwriting it.
Unknown T remains MAP-001. This is a statically reachable generic path for a
no-generator consumer, not an Execution-assembly module initializer or runtime
member/type discovery. Explicit Register still rejects a duplicate registration.

DynamicRecord is the deliberate runtime-selected-field output from Contracts.
DynamicRecordCompiledMapping.Bind admits only scalar logical members, each width1,
with contiguous complete physical coverage and exact declared aliases. It creates
one RowMember per descriptor and prebinds BindDynamicReader for each column. Each
provider implements that method by a closed scalar codec entry producing a typed
DynamicCell<T>; an unsupported result SQL/CLR cell fails MAP-002 before execution.
No runtime-created CLR record type or required object[] protocol appears. Tokenize
uses the same physical shape/storage validation. Read invokes the cached delegates,
constructs one owned DynamicCell array and freezes it into DynamicRecord with its
immutable shape. Nested dynamic members are outside this initial entry and fail
explicitly. The same mature Dapper row loop executes it.

Known Row arities1–8 have `RowMappings<T1,...,TN>.EnsureRegistered()`. A single
static constructor for each closed helper calls Mapping<Row<...>>.Register once;
EnsureRegistered triggers it and is otherwise empty. Consumer generated module
initializers call these helpers, allowing the same Row closure in several consumer
assemblies without competing duplicate registrations. A handwritten no-generator
consumer can call the same helper. Ordinary DTO registration remains strict and a
duplicate still fails MAP-001. The generator discovers closed Row shapes or the
explicit assembly DbCompileRow hint; it never scans assemblies at runtime. The
final consumer generator emits direct EnsureRegistered calls for required Row
closures and for known DTO registrar symbols from referenced CompiledRow metadata.
A library module initializer alone is not sufficient Native AOT rooting; the
consumer's explicit static call path must survive trimming. Do not use
RuntimeHelpers.RunModuleConstructor as a substitute. Follow the generator packet's
exact input-hint/output-marker/registrar declarations.

### Schema acquisition interface

`Metadata/ISchemaCatalogReader.cs` and `Metadata/SchemaReadOptions.cs` contain the
following exact declarations. They import Korda.Orm.Schema's portable model types;
selection/override application is SchemaSnapshotTransform.Apply once, not a second
provider-specific interpretation.

```csharp
namespace Korda.Orm.Execution.Metadata;

public sealed record SchemaReadOptions(SqlProfile Profile,
    ImmutableArray<SchemaNameFilter> Includes,
    ImmutableArray<SchemaNameFilter> Excludes,
    SchemaGenerationOptions Generation,
    ImmutableArray<SchemaOverride> Overrides,
    UnresolvedTypePolicy UnresolvedTypes = UnresolvedTypePolicy.Error);
public interface ISchemaCatalogReader
{
    Task<SchemaSnapshot> ReadAsync(DbConnection connection,
        SchemaReadOptions options, CancellationToken cancellationToken = default);
}
```

The caller supplies an open connection with no concurrent operation or caller
transaction. The adapter borrows it and reads catalogs only; it cannot Open/Close,
attach databases, issue DDL/SET, begin/commit/rollback a transaction or acquire
credentials. SchemaTool owns explicit connection opening and atomic file output.
Provider packets fix catalog SQL and ORMSCHEMA008 coherence behavior. This shared
interface is in Execution because its signature is ADO.NET, while SchemaModel
remains portable and provider/ADO-free.

Transactions are explicit provider/ADO.NET objects. The baseline introduces no
Korda transaction engine: callers begin/commit/rollback/savepoints on their driver
transaction and pass it to Borrow. Own does not infer an ambient transaction.

## Parameter adapter algorithm

Use the upstream [CommandFactory](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/CommandFactory.cs)
factory protocol and [Command<T>.GetCommand](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/CommandT.cs),
with the following exact adaptation:

1. Reject a non-Text command type before CreateCommand. The public infrastructure
   constructor is `LayoutCommandFactory(ParameterEncoder
   encoder)`. Store only that immutable encoder; do not keep a live command, visitor
   or per-command mutable state on the factory singleton.
2. GetCommand creates `connection.CreateCommand()` into a local variable. Inside
   try, assign SQL and CommandType.Text, then call `Bind(DbCommand, BoundArguments)`.
3. Bind iterates Occurrences in ascending contiguous Ordinal. Visit each logical
   typed cell (or frozen list element) and call encoder.Create<T>. Add the returned
   parameter exactly once. Repeated logical slots create repeated physical
   parameters according to the final template; never deduplicate by label or scan
   SQL. PG names are empty and positional; other provider names are p0 onward.
4. Catch an initialization exception, attempt Dispose on the locally owned
   command, retain a second cleanup exception in `primary.Data["KordaCleanupException"]`,
   and rethrow the primary with its original stack. A failing Dispose must not
   replace the binding failure. Do not include parameter values in diagnostic data.
5. AddParameters(in UnifiedCommand, args) delegates to the same Bind with
   `command.Command!`; reject an unavailable command/batch case explicitly. The
   UnifiedCommand constructor is internal and must not be called externally.
6. No command caching in this baseline: CanPrepare=false and TryRecycle=false.
   UpdateParameters clears the collection and calls Bind; do not promise an
   in-place update optimization that has not been measured and accepted.

`Bind(DbCommand command, BoundArguments args)` creates one private sealed
`BinderVisitor(command, encoder)` for this invocation and calls
`args.Values.Accept(occurrence, visitor)` for each occurrence. BinderVisitor stores
only that command/encoder; its generic Visit calls
`command.Parameters.Add(encoder.Create(command,type,value,occurrence))`.
The preflight counterpart stores only ProviderServices and calls ValidateParameter
then ValidateValue<T> with the same occurrence. Neither visitor is shared between
invocations. In the cleanup catch, attaching a second Dispose exception is
best-effort: if `primary.Data` itself rejects the attachment, keep the original
binding exception and stack rather than replacing it with that metadata failure.

The catch covers failures inside LayoutCommandFactory.GetCommand only. Upstream
Command<T>.GetCommand subsequently sets Connection, Transaction and CommandTimeout
before handing ownership to its query state; a failure in those later setters is
outside this catch. The declared drivers use fresh commands, validated association/
timeout values and no external concurrent connection mutation. Do not claim
arbitrary adversarial DbCommand setter cleanup is repaired, add a command proxy or
fork the execution loop to broaden that statement without a separate contract.

StaticConversion and codec validation/conversion callbacks must be pure,
deterministic and side-effect-free. Mutable custom values are snapshotted before
this phase. ValidateValue and defensive Create validation may call the same pure
helper more than once; no mutable pre-encoding cache or guessed effectful callback
protocol is introduced.

The selected typed-cell → generic-visitor → provider-encoder seam is statically
reachable. Provider leaf implementations create typed NpgsqlParameter<T> or normal
ADO.NET parameters; normal Value assignment may box T. Do not introduce dynamic
IL or runtime generic construction to avoid boxing.

## Terminal and session state machine

OrmSession stores the borrowed/owned connection, optional caller transaction,
profile, provider services and validated CommandOptions. Own/Borrow call
services.ValidateConnection(connection,transaction) during construction; terminal
preflight calls it again to detect a completed/reassociated transaction. Each leaf
uses a static `is` check for its driver connection/transaction and same-instance
Transaction.Connection; no driver reference is added to Execution. A wrong driver,
completed transaction (Connection=null) or association fails EXEC-001 before a
DbCommand is created. Its state is one integer:
0=Idle, 1=Active, 2=Disposed. `TryEnter` uses CompareExchange(0→1); state 1 fails
KORM-EXEC-002 and state 2 fails ObjectDisposedException. Release changes 1→0.
DisposeAsync changes 0→2; state 1 fails KORM-EXEC-003 without changing it. On a
successful 0→2 transition dispose the connection only when owned. Never dispose
a caller transaction.

Each BoundCommand and BoundMutation has one private, shared InvocationState with atomic unused=0,
consumed=1; it is a class, not a publicly cloneable record. A template can Bind
again to create a fresh invocation. Profile compatibility compares family, version interval and placeholder style,
then Settings sorted by StringComparer.Ordinal and compared key/value by Ordinal.
Never use record/default ImmutableDictionary reference equality for profiles.
Semantically identical independently constructed profiles must match. The terminal
sequence is fixed:

1. Validate non-null public arguments and session not disposed; throw on a
   pre-cancelled caller token without consuming the invocation.
2. For Query<T> or ReturningMutation<T>, RenderAndBind using the session profile
   and captured/explicit values. For BoundCommand<T>, use its existing immutable template unchanged.
3. Validate profile/version/settings, contiguous physical layout, slots/types,
   list arities, nullable/facet policies, codecs and the connection/transaction
   association. A typed visitor walks the validated occurrence layout and calls
   services.ValidateParameter(type.Descriptor), then ValidateValue<T>(type,value,
   occurrence) before admission/CreateCommand. Each provider shares its closed
   codec validation helper with Create<T>; this adds no SQL scan or command. Bind the explicit/default CompiledMapping to the result descriptor.
4. Acquire the session lease. TryConsume the BoundCommand once. If consumption
   fails, release the session lease and throw KORM-EXEC-006; never retry or silently
   recreate the invocation. Errors before admission leave an unused command usable.
5. Create BoundArguments and call
   `DapperAotExtensions.Command(connection, transaction, sql, CommandType.Text,
   timeout, services.Commands)`. Map null timeout to -1, explicit 0 to unlimited,
   positive values unchanged; negative public values are KORM-EXEC-001.
6. Buffered sync invokes QueryBuffered(args, boundFactory); async invokes
   QueryBufferedAsync(args, boundFactory, cancellationToken: token). Await the
   upstream operation without replacing its loop. Release the session lease in
   finally after the runtime has cleaned up its operation.

Passing a transaction associated with another connection is KORM-EXEC-001 before
command creation. Provider exceptions propagate unchanged unless a specified
Korda shape/conversion failure adds safe context with the original InnerException.
A timeout is not caller cancellation; a successful command after a cancellation
race remains a successful provider outcome, not proof that the request had no effect.

### Lazy streaming wrapper

Constructing StreamAsync acquires no connection/command/session lease. Its first
GetAsyncEnumerator atomically claims the wrapper (another claim fails KORM-EXEC-004)
and retains the method token plus enumerator token. If both are cancellable and
different, create one linked CancellationTokenSource owned by this enumerator;
otherwise forward the effective token without a linked source.

On first MoveNextAsync run the terminal preflight/admission sequence, then obtain
the upstream QueryUnbufferedAsync enumerator. Use a separate atomic move flag to
reject overlap with KORM-EXEC-005. Await/forward MoveNextAsync and Current; reset
the move flag in finally. Do not copy or prefetch rows, queue work, or implement a
replacement read loop. At EOF, failure or DisposeAsync, forward upstream disposal
once, release the session lease once, and dispose the linked token source once.
Dispose before the first move acquires no command and consumes no BoundCommand.
Concurrent Dispose while a move is outstanding fails KORM-EXEC-005; the caller must
await the move then dispose. Disposal is idempotent after successful terminal cleanup.

### Declared SQL without Fluent composition

The Rendering-owned SqlTemplates.Declare<T>(sql,profile,occurrences,result) and
DeclareMutation(sql,profile,occurrences) supply validated value-free templates to
these same endpoints. They validate structural layout/profile/result metadata;
the exact SQL text is a caller-declared escape and is not parsed or claimed to
match its placeholder/statement semantics. A declared-sql-v1 fingerprint domain
includes the exact SQL bytes. A no-Fluent/no-generator consumer can Bind such a
template and pass a deliberate handwritten CompiledMapping to ToList/ToListAsync/
StreamAsync. Do not add a competing raw SQL binder or bypass the session lease.

### Nonquery mutations

Mutation is the shared abstract handle, implemented by InsertBuilder/UpdateBuilder/
DeleteBuilder. A nonquery render produces RenderedMutationTemplate; binding returns
BoundMutation with the same private one-use state. Implement the fixed terminals
`Execute(this Mutation, OrmSession) : int`,
`ExecuteAsync(this Mutation, OrmSession, CancellationToken=default) : Task<int>`,
and the corresponding two overloads for BoundMutation. Use the exact pre-cancel,
validation, lease, consumption and finally order above, omitting result mapping.
Then call upstream `Command<BoundArguments>.Execute(args)` or
`ExecuteAsync(args, cancellationToken)`. Return its affected count unchanged; no
implicit generated-key SELECT, count reinterpretation or automatic retry.

ReturningMutation<T> is a separate typed result handle. Its renderer produces the
ordinary RenderedTemplate<T>/BoundCommand<T> and ToList/ToListAsync/StreamAsync
follow the same generated mapping path as Query<T>. A returning statement does
not also invoke Execute or confuse affected count with returned row count.

The generated RowFactory validates actual count/order/aliases/types in Tokenize
before its first materialized row. Empty results skip Tokenize in the upstream
runtime and return empty. Do not add a hidden schema-only query or alter the mature
loop to make a different empty-result promise.

## Exact execution diagnostics

Use the shared exception/data contract and these fixed messages. Replace only
quoted metadata placeholders; never insert SQL parameter values or credentials.

| Code / reason | Message |
| --- | --- |
| EXEC-001 | `Execution profile, provider, transaction, or timeout is incompatible with this invocation.` |
| EXEC-002 | `The session already has an active operation.` |
| EXEC-003 | `The session cannot be disposed while an operation is active.` |
| EXEC-004 | `This stream can be enumerated only once.` |
| EXEC-005 | `Stream operations cannot overlap.` |
| EXEC-006 | `This bound invocation has already been consumed. Bind the template again.` |
| MAP-001 missing | `No compiled mapping is registered for '{type}'.` |
| MAP-001 duplicate | `A compiled mapping is already registered for '{type}'.` |
| MAP-002 | `Result member '{alias}' at ordinal {ordinal} does not match the declared shape.` |
| MAP-003 | `Column '{alias}' at ordinal {ordinal} cannot produce required type '{type}'.` |

The full stored codes have the `KORM-` prefix. Public null/negative argument
errors remain ArgumentException/ArgumentOutOfRangeException with the corresponding
code in Data["KordaCode"]. Cancellation remains OperationCanceledException; do not
convert it into one of these generic errors. Conversion diagnostics retain their
more specific TYPE/NESTED code where their owning contract defines one.

## Deterministic acceptance cases

Use the actual Dapper runtime with tracking ADO.NET fakes; they must exercise its
real public methods, not a fake copy of Dapper. Also publish/run the fake consumer
as Native AOT, because typed visitors and generic registration are part of the seam.

| Case | Required exact assertion |
| --- | --- |
| EX01 | Missing slot→BIND-001; conflict/type→BIND-002; arity→BIND-003; required null→BIND-004; missing codec/snapshot→BIND-005; CreateCommand count remains zero |
| EX02 | Same slot twice creates two parameters with equal typed values; distinct same-label slots preserve different values; order equals occurrence ordinal |
| EX03 | Scalar ElementIndex=-1 and list 0..n-1 visit the correct typed cells; long/string/long?/array closures compile/run natively |
| EX04 | Timeout null leaves fake default 30; 0 sets 0; 7 sets 7; negative fails before creation |
| EX05 | Base upstream binding fault reproduces its pre-handoff gap; adapted GetCommand disposes once and rethrows original; second Dispose fault is attached without replacing it |
| EX06 | Reader failure, Tokenize failure, required NULL and conversion failure invoke normal runtime cleanup; verify real provider behavior separately for any cleanup failure during that phase |
| EX07 | Borrowed open/closed and owned connection behavior matches the state machine; no caller transaction is disposed |
| EX08 | Busy session→EXEC-002, active Dispose→EXEC-003, repeated enumerator→EXEC-004, overlapping MoveNext/Dispose→EXEC-005, repeated BoundCommand→EXEC-006 |
| EX09 | Pre-cancel leaves command unused; early break consumes it and releases the session; rebinding the same template creates a new executable invocation |
| EX10 | Duplicate/missing Mapping<T>→MAP-001; reordered valid projection binds its own factory; width/alias/type mismatch→MAP-002 before wrong row; required NULL→MAP-003 |
| EX11 | Stream never enumerated/disposed before first move: zero CreateCommand; complete/early/error streams release exactly once and permit next fresh invocation |
| EX12 | Assembly references contain no provider driver, generator/Roslyn runtime, old native engine or reflection fallback |
| EX13 | Mutation/BoundMutation Execute and ExecuteAsync invoke actual mature nonquery runtime, preserve affected count/transaction and consume once; ReturningMutation uses the typed query path only |
| EX14 | Scalar alias follows ResultShape; nullable scalar NULL remains NULL; unsupported T fails; two assemblies EnsureRegistered for the same Row closure succeed once while duplicate DTO Register fails |
| EX15 | DynamicRecord with runtime-selected known scalar columns uses typed cells and strict alias/order; unsupported cell/nested shape fails; one logical nested member spans several physical columns; optional presence0 skips strict child getter, presence1 required NULL fails MAP-003; collection physical width1 differs from JSON element arity |

## Commands, routing and stop

Create `tests/Orm/Execution/Korda.Orm.Execution.Tests.csproj` as an executable
contract/fault runner and `tests/Orm/Execution/check.py` accepting `--mode managed`
and `--mode native`. Both modes run EX01–EX15; native publishes net11.0/linux-x64 with
PublishAot and warnings-as-errors, runs the produced executable and asserts dynamic
code is unsupported. `--mode managed` supports fast local development; it is not
substituted for native acceptance.

```sh
python3 tests/Orm/Execution/check.py --mode managed
python3 tests/Orm/Execution/check.py --mode native
python3 eng/ci/impact.py origin/main --output artifacts/plan.json
```

Register module `orm-execution` with its actual source/test roots and project/link
inputs. Source changes select generator/provider/integration/package consumers;
its own fake tests start no database. Packet changes in Plan select document-link
checks only. Product compilation never moves into document CI.

Stop after the specified adapter, generic mapping, lifecycle and fault gates pass.
Do not introduce an alternative execution engine, publish packages, cut over or
remove historical code. A contradiction in the shared interface is a contract
change, not permission for an implementer to redesign a parallel module.
