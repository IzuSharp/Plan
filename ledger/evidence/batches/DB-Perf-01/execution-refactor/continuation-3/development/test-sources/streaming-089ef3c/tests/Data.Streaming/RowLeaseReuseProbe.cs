using System.Runtime.CompilerServices;
using System.Security.Cryptography;
using System.Text.Json;
using Korda.Data;
using Korda.Database.Internal;

// This fresh-process zero gate excludes first lease construction and provider
// fetch. Owners and exclusive buffers are bounded, precreated and used once.
// OwnedBatchProbe retains its separate new-lease-per-batch raw boundary.
internal static class RowLeaseReuseProbe
{
    private const int Rows = 128, Operations = 64, Windows = 3, Warmup = 1024;
    private static long s_sink;
    private static readonly Projection<long> Shape = Projection<long>.Create(
        [ResultField.Create("id", Codecs.Int64)], static row => row.Read(0, Codecs.Int64));
    private static readonly WireExpectation Expected = new(PayloadKind.Rows, 2,
        Convert.FromHexString(Shape.ShapeHash), 0, 71, [new(0, Codecs.Int64.Descriptor, 3)]);
    private static readonly StreamLimits Limits = new(Rows, 8192, Rows * 2, 16 * 1024);
    private readonly record struct Counter(long Bytes, long ThreadBytes, int Gen0, int Gen1, int Gen2);
    private readonly record struct Window(int Index, Counter Before, Counter After, long Operations, long Rows, long Checksum);

    internal static void Run(string output)
    {
        var cells = new ReadOnlyMemory<byte>?[Rows];
        for (var i = 0; i < Rows; i++) cells[i] = Codecs.Int64.Encode(i + 1L);
        var payload = DbWire.Encode(Expected, Rows, cells);
        var initialOwner = new Owner((byte[])payload.Clone());
        using var lease = new RowBatchLease(initialOwner.Batch, Expected, Shape.Fields, Limits);
        lease.Dispose();
        var warm = Prepare(payload, Warmup);
        _ = Consume(lease, warm, -1);
        AssertReleased(warm);
        var owners = new Owner[Windows][];
        for (var i = 0; i < Windows; i++) owners[i] = Prepare(payload, Operations);
        var windows = new Window[Windows];
        _ = Capture();
        for (var i = 0; i < Windows; i++) windows[i] = Consume(lease, owners[i], i);
        foreach (var batches in owners) AssertReleased(batches);
        if (initialOwner.Acquisitions != 1 || initialOwner.NativeReleases != 1 || lease.IsActive)
            throw new InvalidOperationException("Reusable lease retained an owner outside its attachment window.");
        var passed = windows.All(window => window.After.Bytes - window.Before.Bytes == 0
            && window.After.ThreadBytes - window.Before.ThreadBytes == 0
            && window.Operations == Operations && window.Rows == Operations * Rows
            && window.Checksum == Operations * (long)Rows * (Rows + 1) / 2);
        var path = Path.Combine(output, "row-lease-reuse-probe.json");
        using (var file = File.Create(path))
        using (var json = new Utf8JsonWriter(file, new() { Indented = true }))
        {
            json.WriteStartObject(); json.WriteNumber("schema_version", 2);
            json.WriteString("task", "DB-Exec-02"); json.WriteBoolean("passed", passed);
            json.WriteBoolean("native_aot", !RuntimeFeature.IsDynamicCodeSupported);
            json.WriteBoolean("public_provider_acceptance", false);
            json.WriteNumber("process_id", Environment.ProcessId);
            json.WriteString("executable", Environment.ProcessPath);
            if (Environment.ProcessPath is { } executable)
            {
                using var binary = File.OpenRead(executable);
                json.WriteString("executable_sha256", Convert.ToHexStringLower(SHA256.HashData(binary)));
            }
            json.WriteNumber("warmup_operations", Warmup); json.WriteNumber("rows_per_batch", Rows);
            json.WriteNumber("encoded_batch_bytes", payload.Length);
            json.WriteString("batch_sha256", Convert.ToHexStringLower(SHA256.HashData(payload)));
            json.WriteString("boundary", "One lease and all single-use native batches and scoped owners are precreated. Attach, complete wire validation, all numeric row reads and Dispose are inside each all-thread cumulative allocation boundary. First lease construction, owner/input construction, provider fetch and output serialization are excluded and never declared zero by this gate.");
            json.WriteString("ownership", "One private lease; no global pool, no reused batch owner, no retained prior payload. Every native owner attaches and releases exactly once; NativeMemory and GCHandle preparation occur before the window. Original per-batch constructor gate remains separate.");
            json.WriteStartArray("windows");
            foreach (var window in windows)
            {
                json.WriteStartObject(); json.WriteNumber("index", window.Index);
                WriteCounter(json, "before", window.Before); WriteCounter(json, "after", window.After);
                json.WriteNumber("allocated_bytes_total", window.After.Bytes - window.Before.Bytes);
                json.WriteNumber("operations", window.Operations); json.WriteNumber("rows", window.Rows);
                json.WriteNumber("checksum", window.Checksum); json.WriteEndObject();
            }
            json.WriteEndArray(); json.WriteEndObject();
        }
        if (!passed) throw new InvalidOperationException("Warmed row lease Attach/read/Dispose boundary allocated; inspect raw counters without rounding or control subtraction.");
        Console.WriteLine($"PASS reused row lease allocation: {Windows} windows, {Operations * Windows} attachments, {Operations * Windows * Rows} rows, raw all-thread bytes=0; initial lease and provider fetch excluded; {path}");
    }

    private static Owner[] Prepare(byte[] payload, int count)
    {
        var owners = new Owner[count];
        for (var i = 0; i < count; i++) owners[i] = new((byte[])payload.Clone());
        return owners;
    }
    private static Window Consume(RowBatchLease lease, Owner[] owners, int index)
    {
        long rows = 0, sum = 0;
        var before = Capture();
        foreach (var owner in owners)
        {
            lease.Attach(owner.Batch, Expected, Limits);
            try
            {
                for (uint row = 0; row < lease.Rows; row++) { sum += lease.Materialize(row, Shape); rows++; }
            }
            finally { lease.Dispose(); }
        }
        Volatile.Write(ref s_sink, sum);
        var after = Capture();
        return new(index, before, after, owners.Length, rows, sum);
    }
    private static Counter Capture() => new(GC.GetTotalAllocatedBytes(true), GC.GetAllocatedBytesForCurrentThread(),
        GC.CollectionCount(0), GC.CollectionCount(1), GC.CollectionCount(2));
    private static void WriteCounter(Utf8JsonWriter json, string name, Counter value)
    {
        json.WriteStartObject(name); json.WriteNumber("allocated_bytes", value.Bytes);
        json.WriteNumber("current_thread_bytes", value.ThreadBytes); json.WriteNumber("gen0", value.Gen0);
        json.WriteNumber("gen1", value.Gen1); json.WriteNumber("gen2", value.Gen2); json.WriteEndObject();
    }
    private static void AssertReleased(Owner[] owners)
    {
        foreach (var owner in owners)
            if (owner.Acquisitions != 1 || owner.NativeReleases != 1) throw new InvalidOperationException("Attachment owner was not consumed/released exactly once.");
    }
    private sealed class Owner : ScopedBatchFixture
    {
        internal Owner(byte[] bytes) : base(bytes) => Acquire();
    }
}
