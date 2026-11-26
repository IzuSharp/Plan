using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Text.Json;
using Korda.Data;
using Korda.Database.Internal;

if (args.Length == 0) throw new ArgumentException("Usage: Data.Streaming.Tests <report-directory> [--require-aot]");
if (args.Contains("--require-aot", StringComparer.Ordinal) && RuntimeFeature.IsDynamicCodeSupported) throw new InvalidOperationException("Actual NativeAOT execution required.");
Directory.CreateDirectory(args[0]);
if (args.Contains("--allocation-probe", StringComparer.Ordinal))
{
    await AllocationProbe.RunAsync(args[0], args);
    return;
}
if (args.Contains("--allocation-probe-races", StringComparer.Ordinal))
{
    await AllocationProbeRaces.RunAsync();
    return;
}
if (args.Contains("--owned-batch-probe-only", StringComparer.Ordinal))
{
    OwnedBatchProbe.Run(args[0]);
    return;
}
if (args.Contains("--stable-batch-only", StringComparer.Ordinal))
{
    StableBatchTests.Run();
    return;
}
if (args.Contains("--row-lease-reuse-probe-only", StringComparer.Ordinal))
{
    RowLeaseReuseProbe.Run(args[0]);
    return;
}
if (args.Contains("--row-lease-reuse-checks-only", StringComparer.Ordinal))
{
    await RowLeaseReuseChecks.RunAsync();
    return;
}
if (args.Contains("--allocation-gate-only", StringComparer.Ordinal))
{
    await AllocationProbeGate.RunAsync(args[0]);
    return;
}
// The default and --correctness-only paths execute the same behavior checks.
// Allocation probes remain explicit local diagnostic entry points above.
await AllocationProbeRaces.RunAsync();
OwnedBatchProbe.RunCorrectness();
StableBatchTests.Run();
await RowLeaseReuseChecks.RunAsync();
var cases = new List<Observation>();
var assertions = 0;
var ordinary = Projection<Item>.Create([ResultField.Create("id", Codecs.Int64), ResultField.Create("label", Codecs.NullableReference(Codecs.String))], row => new(row.Read(0, Codecs.Int64), row.Read(1, Codecs.NullableReference(Codecs.String))));
var limits = new StreamLimits(3, 256, 100, 64 * 1024);

void Check(bool condition, string message) { assertions++; if (!condition) throw new InvalidOperationException(message); }
async Task Expect<T>(Func<Task> action, Func<T, bool>? predicate = null) where T : Exception
{
    try { await action(); }
    catch (T error) when (predicate?.Invoke(error) ?? true) { assertions++; return; }
    throw new InvalidOperationException("Expected " + typeof(T).Name);
}
async Task WaitFor(Func<bool> condition)
{
    var start = Stopwatch.StartNew();
    while (!condition()) { if (start.Elapsed > TimeSpan.FromSeconds(5)) throw new TimeoutException("Controlled fixture condition was not reached."); await Task.Delay(2); }
}
TypedStream<T> Make<T>(uint provider, uint scenario, Projection<T> projection, Action<NativeFixtureTransport> opened,
    StreamLimits? custom = null, CancellationToken methodToken = default, Func<IStreamTransport, IStreamTransport>? decorate = null)
{
    var settings = custom ?? limits;
    return new(async (rows, token) =>
    {
        var native = await NativeFixtureTransport.OpenAsync(provider, scenario, projection.CanonicalBytes, rows, settings.MaxBatchBytes, token);
        opened(native);
        return decorate?.Invoke(native) ?? native;
    }, projection, provider, 7, projection.Fields.Select(f => f.CodecId).ToArray(), settings, methodToken);
}
void Clean(string name, uint provider, NativeFixtureTransport? transport, int rows = 0)
{
    if (transport is null) throw new InvalidOperationException("Expected an actual provider transport.");
    var values = transport.Stats();
    Check(values[0] == 0 && values[1] == 0 && values[3] == 0 && values[4] == 0, name + ": native owned budgets returned");
    Check(values[8] == 1 && values[11] == 1 && values[12] == 1, name + ": real native operation/session/lease retirement");
    Check(values[9] == 0 || values[14] == 1, name + ": reusable connection actually runs another row query");
    Check(values[7] <= 2UL, name + ": provider channel plus delivery handoff bounded separately; observed=" + values[7]);
    Check(values[5] <= 256 && values[2] <= 64 * 1024, name + ": wire and conservative reserved byte bounds");
    Check(values[17] == 0, name + ": provider active operations returned");
    if (provider == 1) Check(values[15] == 1 && values[16] == 0, name + ": worker shutdown acknowledged; OS thread join not claimed");
    Check(transport.ActiveCalls == 0 && NativeBatch.LiveBytes == 0 && Native.Owners() == 0, name + ": managed calls/fixture native scratch/native wrapper owners retired");
    cases.Add(new(name, provider, rows, transport.Fetches, transport.DuplicateTakeRejections, values));
    Console.WriteLine($"PASS {name} provider={provider} rows={rows} fetches={transport.Fetches} native-retired={values[8]} lease-released={values[12]} reusable-probe={values[14]}");
}

foreach (var provider in new uint[] { 1, 2 })
{
    NativeFixtureTransport? transport = null;
    var empty = Make(provider, 0, ordinary, value => transport = value);
    Check((await empty.ToListAsync()).Count == 0, "empty list"); Clean("empty", provider, transport);
    await Expect<InvalidOperationException>(async () => { await empty.ToListAsync(); });

    transport = null;
    var one = await Make(provider, 1, ordinary, value => transport = value).SingleAsync();
    Check(one == new Item(1, "row-1"), "one exact row"); Clean("one", provider, transport, 1);

    transport = null;
    var many = await Make(provider, 2, ordinary, value => transport = value).ToArrayAsync();
    Check(many.Length == 17 && many.Sum(item => item.Id) == 153 && many[16].Label == "row-17", "multiple bounded batches");
    Check(transport!.Fetches >= 9 && transport.Fetches == transport.DuplicateTakeRejections, "byte split and one transfer per fetch");
    Clean("multibatch", provider, transport, 17);
    Check(many[0].Label == "row-1", "owned DTO survives native and managed retirement");

    transport = null; var read = 0;
    await foreach (var item in Make(provider, 2, ordinary, value => transport = value))
    {
        read++; var fetches = transport!.Fetches;
        var before = transport.Stats();
        await Task.Delay(4);
        Check(transport.Fetches == fetches && before[3] == 1 && before[4] <= 256, "slow consumer does not start another fetch");
        Check(item.Id == read, "ordered stream row");
    }
    Clean("slow-consumer", provider, transport, read);

    transport = null; read = 0;
    await foreach (var item in Make(provider, 2, ordinary, value => transport = value)) { read++; if (read == 3) break; }
    Clean("early-break", provider, transport, read);

    transport = null; var maps = 0;
    var throwing = Projection<Item>.Create(ordinary.Fields, row => { maps++; if (maps == 2) throw new InvalidDataException("application constructor failure"); return new(row.Read(0, Codecs.Int64), row.Read(1, Codecs.NullableReference(Codecs.String))); });
    await Expect<InvalidDataException>(async () => { await foreach (var item in Make(provider, 2, throwing, value => transport = value)) { _ = item; } });
    Check(maps == 2, "mapper exception stops materialization"); Clean("mapper-throw", provider, transport, 1);

    transport = null; maps = 0;
    var counted = Projection<Item>.Create(ordinary.Fields, row => { maps++; return new(row.Read(0, Codecs.Int64), row.Read(1, Codecs.NullableReference(Codecs.String))); });
    await Expect<DatabaseException>(async () => { await Make(provider, 3, counted, value => transport = value).ToListAsync(); }, e => e.ProviderCode == "LargeValueRequiresStreaming");
    Check(maps == 0, "oversized row fails before constructor"); Clean("huge-field", provider, transport);

    transport = null; maps = 0;
    await Expect<DatabaseException>(async () => { await Make(provider, 2, counted, value => transport = value, limits with { MaxBufferedRows = 5 }).ToListAsync(); }, e => e.Kind == DatabaseErrorKind.ResourceLimit);
    Check(maps == 5, "buffered row cap checked before the next mapper"); Clean("buffered-row-limit", provider, transport, maps);

    transport = null; maps = 0;
    await Expect<DatabaseException>(async () => { await Make(provider, 2, counted, value => transport = value, limits with { MaxBufferedBytes = 200 }).ToListAsync(); }, e => e.Kind == DatabaseErrorKind.ResourceLimit);
    Check(maps == 1, "buffered bytes include header, descriptors, cells and payload"); Clean("buffered-byte-limit", provider, transport, maps);

    transport = null;
    var first = await Make(provider, 2, ordinary, value => transport = value).FirstAsync();
    Check(first.Id == 1 && transport!.Fetches == 1, "First takes one business row"); Clean("first", provider, transport, 1);
    transport = null;
    await Expect<InvalidOperationException>(async () => { await Make(provider, 2, ordinary, value => transport = value).SingleAsync(); });
    Check(transport!.Fetches == 1, "Single reads at most two business rows"); Clean("single-excess", provider, transport, 2);
    transport = null;
    await Expect<InvalidOperationException>(async () => { await Make(provider, 0, ordinary, value => transport = value).FirstAsync(); });
    Clean("first-empty", provider, transport);
    transport = null;
    Check(await Make(provider, 0, ordinary, value => transport = value).SingleOrDefaultAsync() is null, "reference absence default"); Clean("single-or-default-empty", provider, transport);
    transport = null;
    var numeric = Projection<long>.Create(ordinary.Fields, row => row.Read(0, Codecs.Int64));
    Check(await Make(provider, 0, numeric, value => transport = value).FirstOrDefaultAsync() == 0L, "unconstrained generic value-type default"); Clean("value-type-default", provider, transport);

    var scalar = Projection<long>.Scalar(Codecs.Int64);
    transport = null;
    Check(await Make(provider, 21, scalar, value => transport = value).SingleAsync() == 1L, "exact scalar one column and row"); Clean("scalar-one", provider, transport, 1);
    transport = null;
    await Expect<InvalidOperationException>(async () => { await Make(provider, 20, scalar, value => transport = value).SingleAsync(); });
    Clean("scalar-empty", provider, transport);
    transport = null;
    await Expect<InvalidOperationException>(async () => { await Make(provider, 22, scalar, value => transport = value).SingleAsync(); });
    Clean("scalar-excess", provider, transport, 2);

    // Actual provider bytes are borrowed only through the live owned batch lease.
    transport = await NativeFixtureTransport.OpenAsync(provider, 1, ordinary.CanonicalBytes, 3, 256, default);
    var raw = await transport.FetchAsync();
    var expected = new WireExpectation(PayloadKind.Rows, provider, Convert.FromHexString(ordinary.ShapeHash), 0, 7,
        [new(0, Codecs.Int64.Descriptor, 3), new(1, Codecs.NullableReference(Codecs.String).Descriptor, 5)]);
    var lease = new RowBatchLease(raw, expected, ordinary.Fields, limits);
    var copied = lease.Materialize(0, ordinary);
    lease.Dispose(); lease.Dispose();
    await Expect<ObjectDisposedException>(() => { ((IRowLifetime)lease).AssertAlive(); return Task.CompletedTask; });
    await transport.JoinAsync(); Check(copied.Label == "row-1", "DTO owns its data after lease disposal"); Clean("lease-dispose", provider, transport, 1);

    foreach (var scenario in new uint[] { 4, 5, 6 })
    {
        transport = null;
        await Expect<DatabaseException>(async () => { await Make(provider, scenario, ordinary, value => transport = value).ToListAsync(); }, e => e.Kind == DatabaseErrorKind.ShapeMismatch);
        Check(transport is null && Native.Owners() == 0, "bad complete shape rejects before publishing a managed transport");
        Console.WriteLine($"PASS shape-preflight provider={provider} scenario={scenario} no-managed-transport");
    }
    transport = null;
    var nullable = await Make(provider, 7, ordinary, value => transport = value).SingleAsync();
    Check(nullable.Label is null, "declared NULL is distinct from missing column"); Clean("nullable", provider, transport, 1);
    transport = null;
    var required = Projection<Item>.Create([ResultField.Create("id", Codecs.Int64), ResultField.Create("label", Codecs.String)], row => new(row.Read(0, Codecs.Int64), row.Read(1, Codecs.String)));
    await Expect<DatabaseException>(async () => { await Make(provider, 7, required, value => transport = value).SingleAsync(); }, e => e.Kind == DatabaseErrorKind.Conversion);
    Clean("null-nonnullable", provider, transport);

    // The worker can be preempted after scheduling a fetch but before entering the provider.
    transport = await NativeFixtureTransport.OpenAsync(provider, 8, ordinary.CanonicalBytes, limits.MaxBatchRows, limits.MaxBatchBytes, CancellationToken.None);
    transport.RequestStop();
    await Expect<OperationCanceledException>(async () => { using var batch = await transport.FetchAsync(); });
    await transport.JoinAsync();
    Clean("stop-before-native-fetch", provider, transport);

    foreach (var enumerationToken in new[] { false, true })
    {
        transport = null;
        using var cancellation = new CancellationTokenSource();
        var sequence = Make(provider, 8, ordinary, value => transport = value, methodToken: enumerationToken ? default : cancellation.Token);
        await using var enumerator = sequence.GetAsyncEnumerator(enumerationToken ? cancellation.Token : default);
        var moving = enumerator.MoveNextAsync().AsTask();
        await WaitFor(() => transport is { Fetches: > 0 });
        cancellation.Cancel();
        await Expect<OperationCanceledException>(async () => { await moving; });
        await enumerator.DisposeAsync();
        Clean(enumerationToken ? "enumerator-cancel" : "method-cancel", provider, transport);
    }
    transport = null;
    var concurrent = Make(provider, 8, ordinary, value => transport = value).GetAsyncEnumerator();
    var pending = concurrent.MoveNextAsync().AsTask();
    await WaitFor(() => transport is { Fetches: > 0 });
    await Expect<DatabaseException>(async () => { await concurrent.MoveNextAsync(); }, e => e.Kind == DatabaseErrorKind.ConcurrentUse);
    var disposal = concurrent.DisposeAsync().AsTask();
    try { await pending; }
    catch (Exception e) when (e is OperationCanceledException or ObjectDisposedException) { assertions++; }
    await disposal; await concurrent.DisposeAsync(); Clean("concurrent-dispose", provider, transport);

    transport = null;
    using (var method = new CancellationTokenSource())
    using (var enumeration = new CancellationTokenSource())
    {
        CancellationToken linked = default;
        var failing = new TypedStream<Item>(async (rows, token) =>
        {
            linked = token;
            transport = await NativeFixtureTransport.OpenAsync(provider, 1, ordinary.CanonicalBytes, rows, limits.MaxBatchBytes, token);
            return new FailingCleanupTransport(transport);
        }, ordinary, provider, 7, [3, 5], limits, method.Token);
        await Expect<InvalidDataException>(async () => { await failing.ToListAsync(enumeration.Token); });
        Check(linked.CanBeCanceled && !linked.IsCancellationRequested, "linked token reached the accepted provider factory");
        method.Cancel(); enumeration.Cancel();
        Check(!linked.IsCancellationRequested, "failed cleanup still releases linked parent-token registrations");
        Clean("cleanup-failure-registrations", provider, transport, 1);
    }

    foreach (var mutation in new[] { 0, 1, 2, 3, 4 })
    {
        transport = null;
        await Expect<DatabaseException>(async () => { await Make(provider, 1, ordinary, value => transport = value, decorate: original => new CorruptTransport(original, mutation)).ToListAsync(); }, e => e.Kind == DatabaseErrorKind.ShapeMismatch);
        Clean("malformed-wire-" + mutation, provider, transport);
    }
}

var starts = 0;
var never = new TypedStream<Item>((_, _) => { starts++; throw new InvalidOperationException("must not dispatch"); }, ordinary, 1, 7, [3, 5], limits);
var unused = never.GetAsyncEnumerator();
await Expect<InvalidOperationException>(() => { _ = never.GetAsyncEnumerator(); return Task.CompletedTask; });
await unused.DisposeAsync(); await unused.DisposeAsync(); Check(starts == 0, "unused one-shot sequence does not execute");
using (var canceled = new CancellationTokenSource())
{
    canceled.Cancel();
    var sequence = new TypedStream<Item>((_, _) => { starts++; throw new InvalidOperationException("must not dispatch"); }, ordinary, 1, 7, [3, 5], limits, canceled.Token);
    await Expect<OperationCanceledException>(async () => { await sequence.ToListAsync(); });
    Check(starts == 0, "pre-canceled method performs no native admission");
}
Check(NativeBatch.LiveBytes == 0 && Native.Owners() == 0, "all component owners returned");

using (var output = File.Create(Path.Combine(args[0], "results.json")))
using (var json = new Utf8JsonWriter(output, new JsonWriterOptions { Indented = true }))
{
    json.WriteStartObject(); json.WriteString("task", "B06"); json.WriteString("status", "passed"); json.WriteString("platform", "linux-x64");
    json.WriteBoolean("dynamicCodeSupported", RuntimeFeature.IsDynamicCodeSupported); json.WriteNumber("assertions", assertions);
    json.WriteNumber("fixtureNativeCopyBytes", NativeBatch.CopiedBytes); json.WriteNumber("peakFixtureNativeBytes", NativeBatch.PeakBytes);
    json.WriteNumber("schemaVersion", 2);
    json.WriteString("memoryScope", "Correctness records owned reservation and the retained fixture ABI copy into test-owned native storage. The product scoped path has no fixture copy. Process allocation, GC and RSS sampling belong to explicit local diagnostics.");
    json.WriteStartArray("cases");
    foreach (var item in cases)
    {
        json.WriteStartObject(); json.WriteString("name", item.Name); json.WriteNumber("provider", item.Provider); json.WriteNumber("rows", item.Rows); json.WriteNumber("fetches", item.Fetches); json.WriteNumber("duplicateTakeRejections", item.DuplicateTakes);
        json.WriteStartArray("nativeSnapshot"); foreach (var value in item.Stats) json.WriteNumberValue(value); json.WriteEndArray(); json.WriteEndObject();
    }
    json.WriteEndArray(); json.WriteEndObject();
}
Console.WriteLine($"PASS B06 assertions={assertions} cases={cases.Count} jit={RuntimeFeature.IsDynamicCodeSupported} fixture-native-live-bytes={NativeBatch.LiveBytes} native-wrappers={Native.Owners()}");

internal sealed record Item(long Id, string? Label);
internal sealed record Observation(string Name, uint Provider, int Rows, int Fetches, int DuplicateTakes, ulong[] Stats);
internal sealed class FailingCleanupTransport(IStreamTransport inner) : IStreamTransport
{
    public ValueTask<ScopedStreamBatch> FetchAsync() => inner.FetchAsync();
    public void RequestStop() => inner.RequestStop();
    public async Task<StreamRetirement> JoinAsync()
    {
        await inner.JoinAsync();
        throw new InvalidDataException("Injected cleanup failure after the actual native provider receipt.");
    }
}
internal sealed class CorruptTransport(IStreamTransport inner, int mutation) : IStreamTransport
{
    public async ValueTask<ScopedStreamBatch> FetchAsync()
    {
        var owner = await inner.FetchAsync();
        byte[] bytes;
        using (var read = owner.AcquireRead()) bytes = read.Bytes.ToArray();
        switch (mutation)
        {
            case 0: bytes[24] ^= 1; break;
            case 1: DbWire.U16(bytes, 100, ushort.MaxValue); break;
            case 2: DbWire.U16(bytes, 130, 1); DbWire.U64(bytes, 136, 0); DbWire.U64(bytes, 144, 0); break;
            case 3: bytes[checked((int)DbWire.R64(bytes, 160))] = 0xff; break;
            case 4: DbWire.U64(bytes, 160, DbWire.R64(bytes, 136)); break;
        }
        var corrupt = new ScopedBatchFixture(bytes, owner.End, afterRelease: owner.Dispose);
        corrupt.Acquire();
        return corrupt.Batch;
    }
    public void RequestStop() => inner.RequestStop();
    public Task<StreamRetirement> JoinAsync() => inner.JoinAsync();
}
