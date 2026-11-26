using Korda.Data;
using Korda.Database.Internal;

internal static class StableBatchTests
{
    private static int s_checks;
    internal static void Run()
    {
        s_checks = 0;
        var shape = Projection<long>.Create([ResultField.Create("id", Codecs.Int64)], row => row.Read(0, Codecs.Int64));
        var expected = new WireExpectation(PayloadKind.Rows, 2, Convert.FromHexString(shape.ShapeHash), 0, 71,
            [new(0, Codecs.Int64.Descriptor, 3)]);
        var limits = new StreamLimits(8, 4096, 8, 4096);
        byte[] Encoded() => DbWire.Encode(expected, 1, [Codecs.Int64.Encode(42)]);

        var input = Encoded();
        var fixture = new ScopedBatchFixture(input);
        var owner = fixture.Batch;
        Check(owner.CanAttach && !owner.IsActive, "An idle stable owner must accept its first generation.");
        fixture.Acquire();
        var firstGeneration = owner.Generation;
        var lease = new RowBatchLease(owner, expected, shape.Fields, limits);
        Check(lease.Materialize(0, shape) == 42, "Scoped batch mapping changed.");
        using (var first = owner.AcquireRead(firstGeneration))
        {
            var second = owner.AcquireRead(firstGeneration);
            Check(first.Bytes.SequenceEqual(input) && second.Bytes.SequenceEqual(input), "Scoped reads changed native batch bytes.");
            lease.Dispose(); lease.Dispose();
            Check(!owner.IsActive && !owner.CanAttach && fixture.NativeReleases == 0,
                "Logical disposal must invalidate reads while retaining both admitted physical read scopes.");
            RejectDisposed(() => { using var invalid = owner.AcquireRead(firstGeneration); });
            Reject<InvalidOperationException>(fixture.Acquire);
            Check(fixture.Acquisitions == 1 && fixture.NativeReleases == 0,
                "A rejected reattachment consumed or released a new owner.");
            second.Dispose();
            Check(!owner.CanAttach && fixture.NativeReleases == 0 && first.Bytes.SequenceEqual(input),
                "The first read lost native storage when a later read left its scope.");
        }
        Check(owner.CanAttach && fixture.NativeReleases == 1, "The final admitted read must release its native generation exactly once.");
        RejectDisposed(() => lease.Materialize(0, shape));
        RejectDisposed(lease.AssertAlive);

        fixture.Acquire();
        Check(ReferenceEquals(owner, fixture.Batch) && owner.Generation > firstGeneration,
            "Reattachment must reuse one stable owner with a distinct generation.");
        RejectDisposed(() => { using var stale = owner.AcquireRead(firstGeneration); });
        lease.Attach(owner, expected, limits);
        Check(lease.Materialize(0, shape) == 42, "The same row lease did not attach to the next generation.");
        lease.Dispose();
        Check(fixture.NativeReleases == 2 && owner.CanAttach, "The next generation did not release exactly once.");

        fixture.Acquire();
        using (var read = owner.AcquireRead())
        {
            owner.Close(); owner.Close();
            Check(!owner.IsActive && !owner.CanAttach && fixture.NativeReleases == 2,
                "Permanent close must retain an admitted read without allowing another generation.");
            Check(read.Bytes.SequenceEqual(input), "Permanent close invalidated an admitted span.");
            RejectDisposed(() => { using var invalid = owner.AcquireRead(); });
        }
        Check(fixture.NativeReleases == 3 && !owner.CanAttach, "The closed stable owner did not release its final native storage.");
        Reject<InvalidOperationException>(fixture.Acquire);

        var mutable = Encoded();
        var captured = new ScopedBatchFixture(mutable); captured.Acquire();
        using (var snapshot = new RowBatchLease(captured.Batch, expected, shape.Fields, limits))
        {
            Array.Clear(mutable);
            Check(snapshot.Materialize(0, shape) == 42, "Fixture input mutation reached its independently owned native payload.");
        }
        Check(captured.NativeReleases == 1, "The independently captured owner was not released once.");

        foreach (var failure in new[] { "header", "row-limit", "byte-limit", "empty-not-terminal" })
        {
            var invalid = Encoded(); var selected = limits;
            if (failure == "header") invalid[4] = 2;
            if (failure == "row-limit") selected = limits with { MaxBatchRows = 0 };
            if (failure == "byte-limit") selected = limits with { MaxBatchBytes = invalid.Length - 1 };
            if (failure == "empty-not-terminal") invalid = DbWire.Encode(expected, 0, []);
            var invalidOwner = new ScopedBatchFixture(invalid); invalidOwner.Acquire();
            Reject<DatabaseException>(() => { using var unused = new RowBatchLease(invalidOwner.Batch, expected, shape.Fields, selected); });
            Check(invalidOwner.NativeReleases == 1 && !invalidOwner.Active,
                "Invalid scoped batch lost validation or owner compensation: " + failure);
        }
        Console.WriteLine($"PASS stable scoped native owner: {s_checks} assertions; nested reads, generation rejection, reuse, permanent close, input capture and malformed-batch compensation");
    }
    private static void Check(bool value, string message)
    { s_checks++; if (!value) throw new InvalidOperationException(message); }
    private static void RejectDisposed(Action action) => Reject<ObjectDisposedException>(action);
    private static void Reject<T>(Action action) where T : Exception
    {
        try { action(); } catch (T) { s_checks++; return; }
        throw new InvalidOperationException("Expected " + typeof(T).Name);
    }
}
