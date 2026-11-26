using System.Buffers.Binary;
using Korda.Data;
using Korda.Database.Internal;

// Test-only access to internal leases does not grant a public reader any
// lifetime beyond its synchronous materializer. No fixture owner is reused.
internal static class RowLeaseReuseChecks
{
    private static int s_checks;
    private static readonly ValueCodec<long?> NullableLong = Codecs.Nullable(Codecs.Int64);
    private static readonly Projection<long?> Shape = Projection<long?>.Create(
        [ResultField.Create("id", NullableLong)], static row => row.Read(0, NullableLong));
    private static readonly WireExpectation Expected = new(PayloadKind.Rows, 2,
        Convert.FromHexString(Shape.ShapeHash), 0, 71, [new(0, NullableLong.Descriptor, 3)]);
    private static readonly StreamLimits Limits = new(8, 4096, 32, 16 * 1024);

    internal static async Task RunAsync()
    {
        s_checks = 0;
        foreach (var storage in new[] { "native", "snapshot-input" })
        {
            ReattachAndCompensate(storage);
            await IndependentEnumerators(storage);
            await MalformedLaterBatch(storage);
            await ReentrantMapping(storage);
            ValidatedLayout(storage);
        }
        Console.WriteLine($"PASS row lease reuse: {s_checks} assertions; inactive checks, ownership compensation, later malformed batches, independent enumerators and reentrant mapper rejection across native storage and independently captured input");
    }

    private static byte[] Encode(params long?[] values)
    {
        var cells = new ReadOnlyMemory<byte>?[values.Length];
        for (var i = 0; i < values.Length; i++)
        {
            var bytes = NullableLong.Encode(values[i]);
            if (bytes is null) cells[i] = null;
            else cells[i] = new ReadOnlyMemory<byte>(bytes);
            if (values[i].HasValue != cells[i].HasValue || cells[i] is { } cell && cell.Length != 8)
                throw new InvalidOperationException("Fixture lost SQL NULL or Int64 width before wire encoding.");
        }
        return DbWire.Encode(Expected, (uint)values.Length, cells);
    }

    private static ITrackedBatch Owner(string storage, byte[] bytes, bool end = false)
    {
        ITrackedBatch result = new ScopedBatchFixture(bytes, end);
        result.Acquire();
        return result;
    }

    private static void ReattachAndCompensate(string storage)
    {
        var first = Owner(storage, Encode(1, 2));
        var lease = new RowBatchLease(first.Batch, Expected, Shape.Fields, Limits);
        Check(lease.IsActive && lease.Rows == 2 && lease.Materialize(1, Shape) == 2, "initial row lease failed");
        var unaccepted = Owner(storage, Encode(99));
        Throws<InvalidOperationException>(() => lease.Attach(unaccepted.Batch, Expected, Limits));
        Check(first.Disposals == 0 && unaccepted.Disposals == 0 && first.Active && unaccepted.Active,
            "active-lease rejection transferred or released an owner");
        Check(lease.Materialize(0, Shape) == 1, "active-lease rejection changed the previous row");
        unaccepted.Dispose(); Released(unaccepted);
        lease.Dispose(); lease.Dispose(); Released(first); Inactive(lease);

        var second = Owner(storage, Encode(null, 301, 302));
        lease.Attach(second.Batch, Expected, Limits);
        Check(lease.IsActive && lease.Rows == 3 && lease.Materialize(0, Shape) is null && !lease.End,
            "attachment did not reset row zero or nullable state");
        Check(lease.Materialize(0, Shape) is null && lease.Materialize(2, Shape) == 302,
            "different-sized attachment materialized stale cells");
        lease.Dispose(); Released(second); Inactive(lease);
        var empty = Owner(storage, Encode(), end: true);
        lease.Attach(empty.Batch, Expected, Limits);
        Check(lease.Rows == 0 && lease.End, "terminal empty attachment changed");
        lease.Dispose(); Released(empty); Inactive(lease);

        foreach (var failure in new[] { "header", "range", "shape", "byte-budget", "row-budget", "empty-not-end" })
        {
            var bytes = Encode(41, 42); var limits = Limits;
            if (failure == "header") bytes = bytes[..95];
            if (failure == "range") BinaryPrimitives.WriteUInt64LittleEndian(
                bytes.AsSpan(WireSchema.HeaderBytes + WireSchema.DescriptorBytes + 8), ulong.MaxValue);
            if (failure == "shape") BinaryPrimitives.WriteUInt32LittleEndian(bytes.AsSpan(72), 72);
            if (failure == "byte-budget") limits = limits with { MaxBatchBytes = bytes.Length - 1 };
            if (failure == "row-budget") limits = limits with { MaxBatchRows = 1 };
            if (failure == "empty-not-end") bytes = Encode();
            var incoming = Owner(storage, bytes);
            var error = Throws<DatabaseException>(() => lease.Attach(incoming.Batch, Expected, limits));
            Check(error.Kind == (failure == "byte-budget" ? DatabaseErrorKind.ResourceLimit : DatabaseErrorKind.ShapeMismatch),
                "attachment changed failure classification: " + failure);
            if (failure is "header" or "range" or "shape")
                Check(error.InnerException is ArgumentException, "wire parser failure lost its original wrapper");
            Released(incoming); Inactive(lease);
            lease.Dispose(); Released(incoming);
        }

        var bytesAfterFailure = Encode(611);
        var afterFailure = Owner(storage, bytesAfterFailure);
        lease.Attach(afterFailure.Batch, Expected, Limits);
        if (storage == "snapshot-input") Array.Clear(bytesAfterFailure);
        Check(!lease.End && lease.Rows == 1 && lease.Materialize(0, Shape) == 611,
            "failed attachments left stale state or fixture input mutation reached the captured native payload");
        lease.Dispose(); Released(afterFailure); Inactive(lease);
    }

    private static TypedStream<long?> Stream(Projection<long?> shape, BatchSequence transport) =>
        new(transport.Start, shape, 2, 71, [3], Limits);

    private static async Task IndependentEnumerators(string storage)
    {
        var leftOwners = new[] { Owner(storage, Encode(11)), Owner(storage, Encode(12), end: true) };
        var rightOwners = new[] { Owner(storage, Encode(101, 102)), Owner(storage, Encode(103), end: true) };
        var leftTransport = new BatchSequence(leftOwners); var rightTransport = new BatchSequence(rightOwners);
        await using var left = Stream(Shape, leftTransport).GetAsyncEnumerator();
        await using var right = Stream(Shape, rightTransport).GetAsyncEnumerator();
        Check(await left.MoveNextAsync() && left.Current == 11, "left first batch failed");
        Check(await right.MoveNextAsync() && right.Current == 101, "right first batch failed");
        Check(await left.MoveNextAsync() && left.Current == 12, "left reattachment failed");
        Released(leftOwners[0]);
        Check(rightOwners[0].Disposals == 0 && rightOwners[0].Active,
            "reattaching one enumerator retired another enumerator's batch");
        await left.DisposeAsync();
        Check(await right.MoveNextAsync() && right.Current == 102, "disposal of the left enumerator invalidated the right lease");
        Check(await right.MoveNextAsync() && right.Current == 103 && !await right.MoveNextAsync(),
            "independent right reattachment or terminal row changed");
        await right.DisposeAsync();
        foreach (var owner in leftOwners.Concat(rightOwners)) Released(owner);
        Check(leftTransport.Joins == 1 && rightTransport.Joins == 1,
            "independent enumerators did not join exactly once");
    }

    private static async Task MalformedLaterBatch(string storage)
    {
        var malformed = Encode(2);
        BinaryPrimitives.WriteUInt32LittleEndian(malformed.AsSpan(72), 72);
        var owners = new[] { Owner(storage, Encode(1)), Owner(storage, malformed) };
        var transport = new BatchSequence(owners);
        await using var reader = Stream(Shape, transport).GetAsyncEnumerator();
        Check(await reader.MoveNextAsync() && reader.Current == 1, "valid first batch failed before later corruption");
        DatabaseException? failure = null;
        try { _ = await reader.MoveNextAsync(); }
        catch (DatabaseException error) { failure = error; }
        Check(failure is { Kind: DatabaseErrorKind.ShapeMismatch, InnerException: ArgumentException },
            "malformed later attachment did not preserve shape failure");
        Check(!await reader.MoveNextAsync() && transport.Fetches == 2 && transport.Joins == 1,
            "failed reattachment continued fetching or skipped cleanup");
        await reader.DisposeAsync();
        foreach (var owner in owners) Released(owner);
    }

    private static async Task ReentrantMapping(string storage)
    {
        IAsyncEnumerator<long?>? reader = null;
        var rejected = 0;
        var shape = Projection<long?>.Create(Shape.Fields, row =>
        {
            try { _ = reader!.MoveNextAsync(); }
            catch (DatabaseException error) when (error.Kind == DatabaseErrorKind.ConcurrentUse) { rejected++; }
            return row.Read(0, NullableLong);
        });
        var owners = new[] { Owner(storage, Encode(71)), Owner(storage, Encode(72), end: true) };
        var transport = new BatchSequence(owners);
        reader = Stream(shape, transport).GetAsyncEnumerator();
        try
        {
            Check(await reader.MoveNextAsync() && reader.Current == 71, "reentrant first mapper result changed");
            Check(await reader.MoveNextAsync() && reader.Current == 72, "reentrant reused mapper result changed");
            Check(!await reader.MoveNextAsync() && rejected == 2, "a mapper reentered an active attach/move");
        }
        finally { await reader.DisposeAsync(); }
        foreach (var owner in owners) Released(owner);
    }

    private static void Inactive(RowBatchLease lease)
    {
        Check(!lease.IsActive, "retired or failed lease still reports active");
        Throws<ObjectDisposedException>(lease.AssertAlive);
        Throws<ObjectDisposedException>(() => { _ = lease.Rows; });
        Throws<ObjectDisposedException>(() => lease.AssertAlive());
        Throws<ObjectDisposedException>(() => { _ = lease.RowBytes(0); });
        Throws<ObjectDisposedException>(() => { _ = lease.Materialize(0, Shape); });
    }

    private static void ValidatedLayout(string storage)
    {
        var maps = 0;
        var equivalent = Codecs.Nullable(Codecs.Int64);
        var foreign = new ResultColumn<long?>(new object(), 0, "id", NullableLong);
        var shape = Projection<long?>.Create(Shape.Fields, row =>
        {
            maps++;
            try { _ = row.Read(0, Codecs.Int32); throw new InvalidOperationException("Wrong codec accepted by a validated row."); }
            catch (DatabaseException error) when (error.Kind == DatabaseErrorKind.ShapeMismatch) { s_checks++; }
            try { _ = row.Read(1, NullableLong); throw new InvalidOperationException("Out-of-range ordinal accepted by a validated row."); }
            catch (ArgumentOutOfRangeException) { s_checks++; }
            try { _ = row.Get(foreign); throw new InvalidOperationException("Foreign token accepted by a validated row."); }
            catch (ArgumentException) { s_checks++; }
            return row.Read(0, equivalent);
        });
        var expected = Expected with { MetadataHash = shape.ShapeBytes };
        var owner = Owner(storage, Encode(81, null));
        using (var lease = new RowBatchLease(owner.Batch, expected, shape.Fields, Limits))
        {
            Check(lease.Materialize(0, shape) == 81 && lease.Materialize(1, shape) is null && maps == 2,
                "Validated layout changed equivalent codec reads or nullable values.");
            var wrong = Projection<long?>.Create([ResultField.Create("other", NullableLong)], _ => { maps++; return 0; });
            Check(Throws<DatabaseException>(() => lease.Materialize(0, wrong)).Kind == DatabaseErrorKind.ShapeMismatch && maps == 2,
                "A foreign projection reused another layout's validation proof.");
            Check(lease.Materialize(0, shape) == 81 && maps == 3, "A rejected projection corrupted the validated layout.");
        }
        Released(owner);

        RowBatchLease? retiring = null;
        var retiringShape = Projection<long?>.Create(Shape.Fields, row =>
        {
            retiring!.Dispose();
            try { return row.Read(0, NullableLong); }
            catch (ObjectDisposedException) { s_checks++; return -1; }
        });
        var retiringOwner = Owner(storage, Encode(91));
        retiring = new(retiringOwner.Batch, Expected with { MetadataHash = retiringShape.ShapeBytes }, retiringShape.Fields, Limits);
        Check(retiring.Materialize(0, retiringShape) == -1, "A validated reader outlived its retired lease.");
        Released(retiringOwner); Inactive(retiring);
    }
    private static void Released(ITrackedBatch owner) => Check(owner.Disposals == 1 && !owner.Active
        && owner.NativeReleases == 1, "batch owner was not released exactly once");
    private static void Check(bool condition, string message)
    { s_checks++; if (!condition) throw new InvalidOperationException(message); }
    private static TException Throws<TException>(Action action) where TException : Exception
    {
        try { action(); } catch (TException error) { s_checks++; return error; }
        throw new InvalidOperationException("Expected " + typeof(TException).Name);
    }

    private sealed class BatchSequence(ITrackedBatch[] owners) : IStreamTransport
    {
        internal int Fetches, Joins;
        public ValueTask<IStreamTransport> Start(int rows, CancellationToken token) => new(this);
        public ValueTask<ScopedStreamBatch> FetchAsync() => Fetches < owners.Length
            ? new(owners[Fetches++].Batch) : throw new InvalidOperationException("No fixture batch remains.");
        public void RequestStop() { }
        public Task<StreamRetirement> JoinAsync() { Joins++; return Task.FromResult(new StreamRetirement(true, true, 0)); }
    }
}
