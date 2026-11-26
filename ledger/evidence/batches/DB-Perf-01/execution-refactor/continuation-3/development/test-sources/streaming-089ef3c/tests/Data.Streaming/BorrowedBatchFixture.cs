using System.Buffers;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Text.Json.Serialization;
using Korda.Data;
using Korda.Database.Internal;

internal interface ITrackedBatch : IDisposable
{
    ScopedStreamBatch Batch { get; }
    int Disposals { get; }
    int NativeReleases { get; }
    bool Active { get; }
    void Acquire();
}

// Test-only producer of real native storage. The GCHandle roots a release
// counter, never this fixture or its ScopedStreamBatch; abandoned idle owners
// therefore remain finalizable. Every acquisition owns a separate native buffer.
internal class ScopedBatchFixture : ITrackedBatch
{
    private readonly byte[] _input;
    private readonly bool _end;
    private readonly BorrowedReleaseCounter _counter;
    internal int Acquisitions { get; private set; }
    public ScopedStreamBatch Batch { get; }
    public int Disposals => Volatile.Read(ref _counter.Releases);
    public int NativeReleases => Volatile.Read(ref _counter.Releases);
    public bool Active => Batch.IsActive;
    public bool End => _end;
    internal unsafe ScopedBatchFixture(byte[] input, bool end = false,
        BorrowedReleaseCounter? counter = null, Action? afterRelease = null)
    {
        _input = input; _end = end; _counter = counter ?? new();
        _counter.AfterRelease = afterRelease;
        Batch = new(&Release, _counter);
    }
    public unsafe void Acquire()
    {
        if (!Batch.CanAttach) throw new InvalidOperationException("A prior generation is still active or retained.");
        var storage = (Storage*)NativeMemory.AllocZeroed((nuint)sizeof(Storage));
        if (storage == null) throw new OutOfMemoryException();
        try
        {
            storage->Bytes = (byte*)NativeMemory.Alloc((nuint)Math.Max(1, _input.Length));
            if (storage->Bytes == null) throw new OutOfMemoryException();
            _input.CopyTo(new Span<byte>(storage->Bytes, _input.Length));
            storage->Counter = GCHandle.ToIntPtr(GCHandle.Alloc(_counter));
            Batch.Attach((nint)storage, (nint)storage->Bytes, _input.Length, _end);
            Acquisitions++;
        }
        catch
        {
            if (storage->Counter != 0) GCHandle.FromIntPtr(storage->Counter).Free();
            NativeMemory.Free(storage->Bytes); NativeMemory.Free(storage);
            throw;
        }
    }
    public void Dispose() => Batch.Dispose();
    [UnmanagedCallersOnly(CallConvs = [typeof(CallConvCdecl)])]
    private static unsafe void Release(nint owner)
    {
        var storage = (Storage*)owner;
        var root = GCHandle.FromIntPtr(storage->Counter);
        var counter = (BorrowedReleaseCounter)root.Target!;
        NativeMemory.Free(storage->Bytes); NativeMemory.Free(storage);
        root.Free();
        Interlocked.Increment(ref counter.Releases);
        counter.AfterRelease?.Invoke();
    }
    private unsafe struct Storage { internal byte* Bytes; internal nint Counter; }
}

internal sealed class BorrowedBatchFixture(byte[] input, bool end = false, BorrowedReleaseCounter? counter = null)
    : ScopedBatchFixture(input, end, counter);

internal sealed class BorrowedReleaseCounter
{
    internal int Releases;
    internal Action? AfterRelease;
}

internal static class BorrowedBatchChecks
{
    private static int s_checks;
    private static void Check(bool condition, string message)
    { if (!condition) throw new InvalidOperationException(message); s_checks++; }
    internal static void Run()
    {
        s_checks = 0;
        ScopeAndAbandonment();
        ValidationAndOwnedResults();
        TypedJsonOwnership();
        Console.WriteLine($"PASS borrowed native batch lifetime and validation: {s_checks} assertions; bounded native ownership, complete synchronous reads, finalizer fallback and independent decoded values");
    }
    private static void ScopeAndAbandonment()
    {
        var batch = new BorrowedBatchFixture([42]); batch.Acquire();
        var generation = batch.Batch.Generation;
        using (var read = batch.Batch.AcquireRead())
        {
            var bytes = read.Bytes;
            Check(bytes.Length == 1 && batch.Batch.IsActive, "Scoped fixture must expose its active native generation.");
            batch.Dispose();
            GC.Collect(); GC.WaitForPendingFinalizers();
            Check(batch.NativeReleases == 0 && bytes[0] == 42, "The complete synchronous span read lost its native owner reference.");
        }
        Check(batch.NativeReleases == 1, "The last synchronous read did not release native memory exactly once.");
        var rejected = false;
        try { using var stale = batch.Batch.AcquireRead(generation); } catch (ObjectDisposedException) { rejected = true; }
        Check(rejected, "A retired scoped generation remained readable after disposal.");
        var counter = new BorrowedReleaseCounter();
        var orphan = Abandon(counter);
        for (var i = 0; i < 10 && counter.Releases == 0; i++) { GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect(); }
        Check(!orphan.IsAlive && counter.Releases == 1, "An abandoned native batch leaked a persistent native owner reference.");
    }
    [MethodImpl(MethodImplOptions.NoInlining)]
    private static WeakReference Abandon(BorrowedReleaseCounter counter)
    {
        var batch = new BorrowedBatchFixture([1, 2, 3], counter: counter); batch.Acquire();
        using (var read = batch.Batch.AcquireRead()) Check(read.Bytes[2] == 3, "Abandonment fixture read failed.");
        return new WeakReference(batch);
    }
    private static void ValidationAndOwnedResults()
    {
        var projection = Projection<OwnedResult>.Create(
            [ResultField.Create("id", Codecs.Int64), ResultField.Create("name", Codecs.String), ResultField.Create("bytes", Codecs.Bytes)],
            static row => new(row.Read(0, Codecs.Int64), row.Read(1, Codecs.String), row.Read(2, Codecs.Bytes)));
        var fields = projection.Fields.ToArray();
        var expected = new WireExpectation(PayloadKind.Rows, 2, Convert.FromHexString(projection.ShapeHash), 0, 71,
            [new(0, Codecs.Int64.Descriptor, 3), new(1, Codecs.String.Descriptor, 5), new(2, Codecs.Bytes.Descriptor, 6)]);
        var valid = DbWire.Encode(expected, 1, [Codecs.Int64.Encode(42), Codecs.String.Encode("retained"), new byte[] { 1, 2, 255 }]);
        var batch = new BorrowedBatchFixture(valid); batch.Acquire();
        OwnedResult result;
        using (var lease = new RowBatchLease(batch.Batch, expected, fields, new(2, 4096, 2, 4096)))
        {
            Check(lease.RowBytes(0) == 3 * WireSchema.CellBytes + 8 + 8 + 3, "Borrowed row byte accounting changed.");
            result = lease.Materialize(0, projection);
            Check(batch.NativeReleases == 0 && result.Id == 42, "Materializer did not retain the native batch.");
        }
        Check(batch.Disposals == 1 && batch.NativeReleases == 1, "A successful lease did not release its owner exactly once.");
        GC.Collect(); GC.WaitForPendingFinalizers();
        Check(result.Name == "retained" && result.Bytes.AsSpan().SequenceEqual(new byte[] { 1, 2, 255 }), "Decoded application values retained borrowed storage.");
        Reject(valid[..95], expected, fields, new(2, 4096, 2, 4096), false, DatabaseErrorKind.ShapeMismatch);
        var malformed = (byte[])valid.Clone(); malformed[0] = 0;
        Reject(malformed, expected, fields, new(2, 4096, 2, 4096), false, DatabaseErrorKind.ShapeMismatch);
        Reject(valid, expected, fields, new(2, valid.Length - 1, 2, 4096), false, DatabaseErrorKind.ResourceLimit);
        var empty = DbWire.Encode(expected, 0, []);
        Reject(empty, expected, fields, new(2, 4096, 2, 4096), false, DatabaseErrorKind.ShapeMismatch);
        var tooMany = DbWire.Encode(expected, 2, [Codecs.Int64.Encode(1), Codecs.String.Encode("a"), new byte[] { 1 }, Codecs.Int64.Encode(2), Codecs.String.Encode("b"), new byte[] { 2 }]);
        Reject(tooMany, expected, fields, new(1, 4096, 2, 4096), false, DatabaseErrorKind.ShapeMismatch);
        var eos = new BorrowedBatchFixture(empty, end: true); eos.Acquire();
        using (var lease = new RowBatchLease(eos.Batch, expected, fields, new(2, 4096, 2, 4096)))
            Check(lease.End && lease.Rows == 0, "Borrowed empty EOS was rejected.");
        Check(eos.NativeReleases == 1, "EOS native owner leaked.");
    }
    private static void Reject(byte[] input, WireExpectation expected, ResultField[] fields, StreamLimits limits, bool end, DatabaseErrorKind kind)
    {
        var batch = new BorrowedBatchFixture(input, end); batch.Acquire();
        var rejected = false;
        try { using var lease = new RowBatchLease(batch.Batch, expected, fields, limits); }
        catch (DatabaseException error) when (error.Kind == kind) { rejected = true; }
        Check(rejected && batch.Disposals == 1 && batch.NativeReleases == 1, "Borrowed constructor failure did not compensate its owner exactly once.");
    }
    private static void TypedJsonOwnership()
    {
        var codec = Codecs.Json(BorrowedBatchJson.Default.BorrowedJsonValue);
        var projection = Projection<BorrowedJsonValue>.Create([ResultField.Create("json", codec)], row => row.Read(0, codec));
        var expected = new WireExpectation(PayloadKind.Rows, 2, Convert.FromHexString(projection.ShapeHash), 0, 72, [new(0, codec.Descriptor, 16)]);
        var input = DbWire.Encode(expected, 1, [codec.Encode(new(42, ["owned", "values"]))]);
        var batch = new BorrowedBatchFixture(input); batch.Acquire();
        BorrowedJsonValue value;
        using (var lease = new RowBatchLease(batch.Batch, expected, projection.Fields, new(1, 4096, 1, 4096)))
            value = lease.Materialize(0, projection);
        GC.Collect(); GC.WaitForPendingFinalizers();
        Check(batch.NativeReleases == 1 && value.Id == 42 && value.Labels.SequenceEqual(new[] { "owned", "values" }), "Typed JSON retained borrowed native storage after deserialization.");
        var wrongShape = new BorrowedBatchFixture(DbWire.Encode(expected, 1, ["[]"u8.ToArray()])); wrongShape.Acquire();
        var failed = false;
        try
        {
            using var lease = new RowBatchLease(wrongShape.Batch, expected, projection.Fields, new(1, 4096, 1, 4096));
            _ = lease.Materialize(0, projection);
        }
        catch (Exception error) when (error is JsonException or DatabaseException) { failed = true; }
        Check(failed && wrongShape.NativeReleases == 1 && wrongShape.Disposals == 1, "A typed JSON mapping failure leaked the borrowed owner.");
    }
    private sealed record OwnedResult(long Id, string Name, byte[] Bytes);
}

internal sealed record BorrowedJsonValue(long Id, string[] Labels);
[JsonSerializable(typeof(BorrowedJsonValue))]
internal partial class BorrowedBatchJson : JsonSerializerContext { }
