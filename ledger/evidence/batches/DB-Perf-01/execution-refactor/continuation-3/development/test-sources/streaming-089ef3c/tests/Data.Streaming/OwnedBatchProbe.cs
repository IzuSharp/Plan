using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using Korda.Data;
using Korda.Database.Internal;

// The former owned/unmarked managed transfer routes were removed from the
// product. Schema 2 measures only the actual scoped native boundary. Old schema
// 1 receipts remain historical and are not relabeled as this implementation.
internal static class OwnedBatchProbe
{
    private const int Rows = 128, Operations = 64, Rounds = 3, Warmup = 1024;
    private const long NewLeaseBytesLimitPerBatch = 512;
    private static long s_sink;
    private static int s_assertions;
    private static readonly Projection<long> Shape = Projection<long>.Create(
        [ResultField.Create("id", Codecs.Int64)], static row => row.Read(0, Codecs.Int64));
    private static readonly WireExpectation Expected = new(PayloadKind.Rows, 2,
        Convert.FromHexString(Shape.ShapeHash), 0, 71, [new(0, Codecs.Int64.Descriptor, 3)]);
    private static readonly StreamLimits Limits = new(Rows, 8192, Rows * 2, 16 * 1024);
    private readonly record struct Counter(long Bytes, long ThreadBytes, int Gen0, int Gen1, int Gen2);
    private readonly record struct Window(string Lane, int Round, Counter Before, Counter After,
        long Operations, long Rows, long Checksum);

    internal static void RunCorrectness()
    {
        s_assertions = 0;
        var payload = Encode(Rows);
        Correctness(payload);
        var batches = Prepare(payload, 2);
        long rows = 0, checksum = 0;
        foreach (var owner in batches)
        {
            using var lease = new RowBatchLease(owner.Batch, Expected, Shape.Fields, Limits);
            for (uint row = 0; row < lease.Rows; row++)
            {
                var value = lease.Materialize(row, Shape);
                Check(value == row + 1, "Complete scoped batch consumption changed a numeric value.");
                rows++; checksum += value;
            }
        }
        Check(rows == 2 * Rows && checksum == (long)Rows * (Rows + 1),
            "Scoped batches changed their complete row count or checksum.");
        AssertReleased(batches);
        Console.WriteLine($"PASS scoped batch correctness: {s_assertions} assertions; complete consumption, independent input, ownership and malformed-batch compensation");
    }

    internal static void Run(string output)
    {
        s_assertions = 0;
        var payload = Encode(Rows);
        Correctness(payload);
        var initial = Prepare(payload, 1)[0];
        using var reusable = new RowBatchLease(initial.Batch, Expected, Shape.Fields, Limits);
        reusable.Dispose();
        var warmNew = Prepare(payload, Warmup); var warmReuse = Prepare(payload, Warmup);
        _ = Consume(warmNew, null, -1); _ = Consume(warmReuse, reusable, -1);
        AssertReleased(warmNew); AssertReleased(warmReuse);
        _ = Capture();
        var windows = new Window[Rounds * 2];
        var passed = true;
        for (var round = 0; round < Rounds; round++)
        {
            var fresh = Prepare(payload, Operations); var reused = Prepare(payload, Operations);
            Window first, second;
            if ((round & 1) == 0)
            { first = Consume(fresh, null, round); second = Consume(reused, reusable, round); }
            else
            { second = Consume(reused, reusable, round); first = Consume(fresh, null, round); }
            windows[round * 2] = first; windows[round * 2 + 1] = second;
            AssertReleased(fresh); AssertReleased(reused);
            passed &= first.After.Bytes - first.Before.Bytes <= NewLeaseBytesLimitPerBatch * Operations
                && second.After.Bytes - second.Before.Bytes == 0
                && second.After.ThreadBytes - second.Before.ThreadBytes == 0
                && first.Rows == Operations * Rows && second.Rows == first.Rows
                && first.Checksum == second.Checksum
                && first.Checksum == Operations * (long)Rows * (Rows + 1) / 2;
        }
        var path = Path.Combine(output, "owned-batch-probe.json");
        using (var file = File.Create(path))
        using (var json = new Utf8JsonWriter(file, new() { Indented = true }))
        {
            json.WriteStartObject(); json.WriteNumber("schema_version", 2);
            json.WriteString("task", "DB-Exec-02"); json.WriteString("kind", "isolated-scoped-native-row-lease");
            json.WriteBoolean("passed", passed); json.WriteBoolean("public_provider_acceptance", false);
            json.WriteBoolean("native_aot", !RuntimeFeature.IsDynamicCodeSupported);
            json.WriteString("runtime", RuntimeInformation.FrameworkDescription); json.WriteNumber("process_id", Environment.ProcessId);
            json.WriteString("executable", Environment.ProcessPath);
            if (Environment.ProcessPath is { } executable)
            {
                using var binary = File.OpenRead(executable);
                json.WriteString("executable_sha256", Convert.ToHexStringLower(SHA256.HashData(binary)));
            }
            json.WriteNumber("warmup_operations_per_lane", Warmup); json.WriteNumber("rounds", Rounds);
            json.WriteNumber("operations_per_window", Operations); json.WriteNumber("rows_per_batch", Rows);
            json.WriteNumber("encoded_batch_bytes", payload.Length);
            json.WriteNumber("new_lease_raw_bytes_limit_per_batch", NewLeaseBytesLimitPerBatch);
            json.WriteString("batch_sha256", Convert.ToHexStringLower(SHA256.HashData(payload)));
            json.WriteNumber("correctness_assertions", s_assertions);
            json.WriteString("boundary", "NativeMemory, GCHandle-backed release counters and scoped owners are prepared before each window. New or reused RowBatchLease validation, all 128 typed row reads, disposal and native release are measured. Provider fetch and controller scheduling are excluded. Raw all-thread totals are not adjusted.");
            json.WriteString("history", "Schema 1 compared deleted managed-owned and unmarked transport implementations. Schema 2 contains only the production scoped native representation; it makes no copy-savings comparison with schema 1.");
            json.WriteString("ownership", "Every native buffer attaches and releases once; no fixture roots its ScopedStreamBatch. New lease and warmed reuse costs are separate. A zero reuse window never implies a zero-byte public query.");
            json.WriteStartArray("windows");
            foreach (var window in windows)
            {
                json.WriteStartObject(); json.WriteString("lane", window.Lane); json.WriteNumber("round", window.Round);
                WriteCounter(json, "before", window.Before); WriteCounter(json, "after", window.After);
                var bytes = window.After.Bytes - window.Before.Bytes;
                json.WriteNumber("allocated_bytes_total", bytes); json.WriteNumber("operations", window.Operations);
                json.WriteNumber("rows", window.Rows); json.WriteNumber("checksum", window.Checksum);
                json.WriteNumber("bytes_per_operation", bytes / (double)window.Operations); json.WriteEndObject();
            }
            json.WriteEndArray(); json.WriteEndObject();
        }
        if (!passed) throw new InvalidOperationException("Scoped row-lease construction or warmed reuse exceeded its explicit raw allocation boundary; inspect every original window.");
        Console.WriteLine($"PASS scoped row lease: {s_assertions} ownership/validation assertions; {Rounds} raw allocation windows per lane; no public-query zero claim; {path}");
    }

    private static byte[] Encode(int rows)
    {
        var cells = new ReadOnlyMemory<byte>?[rows];
        for (var i = 0; i < rows; i++) cells[i] = Codecs.Int64.Encode(i + 1L);
        return DbWire.Encode(Expected, checked((uint)rows), cells);
    }
    private static ScopedBatchFixture[] Prepare(byte[] payload, int count)
    {
        var batches = new ScopedBatchFixture[count];
        for (var i = 0; i < count; i++) { batches[i] = new(payload); batches[i].Acquire(); }
        return batches;
    }
    private static Window Consume(ScopedBatchFixture[] batches, RowBatchLease? reusable, int round)
    {
        long rows = 0, checksum = 0;
        var before = Capture();
        foreach (var owner in batches)
        {
            var lease = reusable;
            if (lease is null) lease = new(owner.Batch, Expected, Shape.Fields, Limits);
            else lease.Attach(owner.Batch, Expected, Limits);
            try
            { for (uint row = 0; row < lease.Rows; row++) { checksum += lease.Materialize(row, Shape); rows++; } }
            finally { lease.Dispose(); }
        }
        Volatile.Write(ref s_sink, checksum);
        var after = Capture();
        return new(reusable is null ? "new-scoped-row-lease" : "reused-scoped-row-lease", round, before, after, batches.Length, rows, checksum);
    }
    private static Counter Capture() => new(GC.GetTotalAllocatedBytes(true), GC.GetAllocatedBytesForCurrentThread(),
        GC.CollectionCount(0), GC.CollectionCount(1), GC.CollectionCount(2));
    private static void WriteCounter(Utf8JsonWriter json, string name, Counter counter)
    {
        json.WriteStartObject(name); json.WriteNumber("allocated_bytes", counter.Bytes);
        json.WriteNumber("current_thread_allocated_bytes", counter.ThreadBytes);
        json.WriteNumber("gc0", counter.Gen0); json.WriteNumber("gc1", counter.Gen1); json.WriteNumber("gc2", counter.Gen2); json.WriteEndObject();
    }
    private static void Correctness(byte[] payload)
    {
        var input = (byte[])payload.Clone();
        var captured = new ScopedBatchFixture(input); captured.Acquire();
        using (var lease = new RowBatchLease(captured.Batch, Expected, Shape.Fields, Limits))
        {
            Array.Clear(input);
            Check(lease.Materialize(0, Shape) == 1 && lease.Materialize(Rows - 1, Shape) == Rows,
                "Fixture native payload no longer owns a snapshot of its mutable setup input.");
        }
        Check(captured.NativeReleases == 1, "Captured native owner release count differs.");
        var retainedOwner = new ScopedBatchFixture(payload); retainedOwner.Acquire();
        var retained = new RowBatchLease(retainedOwner.Batch, Expected, Shape.Fields, Limits);
        Check(retainedOwner.Acquisitions == 1 && retainedOwner.NativeReleases == 0,
            "Scoped attachment released its owner before disposal.");
        Check(retained.Materialize(0, Shape) == 1, "Scoped row decode changed.");
        retained.Dispose(); retained.Dispose();
        Check(retainedOwner.NativeReleases == 1, "Idempotent lease disposal released its native owner twice.");
        Reject<ObjectDisposedException>(retained.AssertAlive);
        Reject<ObjectDisposedException>(() => retained.Materialize(0, Shape));
        foreach (var failure in new[] { "header", "bytes", "rows", "empty-not-end" })
        {
            var bytes = (byte[])payload.Clone(); var limits = Limits;
            if (failure == "header") bytes[0] = 0;
            if (failure == "bytes") limits = limits with { MaxBatchBytes = payload.Length - 1 };
            if (failure == "rows") limits = limits with { MaxBatchRows = Rows - 1 };
            if (failure == "empty-not-end") bytes = Encode(0);
            var invalid = new ScopedBatchFixture(bytes); invalid.Acquire();
            Reject<DatabaseException>(() => { using var lease = new RowBatchLease(invalid.Batch, Expected, Shape.Fields, limits); });
            Check(invalid.NativeReleases == 1 && !invalid.Active, "Invalid scoped batch did not compensate its owner once: " + failure);
        }
        var end = new ScopedBatchFixture(Encode(0), end: true); end.Acquire();
        using (var lease = new RowBatchLease(end.Batch, Expected, Shape.Fields, Limits))
            Check(lease.End && lease.Rows == 0, "Canonical scoped end batch changed.");
        Check(end.NativeReleases == 1, "End batch owner did not retire.");
    }
    private static void AssertReleased(ScopedBatchFixture[] batches)
    {
        foreach (var batch in batches)
            Check(batch.Acquisitions == 1 && batch.NativeReleases == 1 && !batch.Active,
                "Measured native owner attachment/release count differs.");
    }
    private static void Check(bool condition, string message)
    { s_assertions++; if (!condition) throw new InvalidOperationException(message); }
    private static void Reject<T>(Action action) where T : Exception
    {
        try { action(); } catch (T) { s_assertions++; return; }
        throw new InvalidOperationException("Expected " + typeof(T).Name);
    }
}
