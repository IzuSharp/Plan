using System.Runtime.CompilerServices;
using System.Security.Cryptography;
using System.Text.Json;

// Copied into an external diagnostic consumer by build.py. This source is not
// compiled by a product project, default correctness gate or timed consumer.
internal static class BusinessAllocation
{
    private static long _mapperBytes, _mapperCalls, _listBytes, _listCalls, _addBytes, _addCalls;
    private static readonly List<Window> Windows = new();
    private static string? _receiptPath, _route;
    private static int _rows;
    private static Pending? _pending;
    private static bool _written;

    private readonly record struct Counters(long MapperBytes, long MapperCalls,
        long ListBytes, long ListCalls, long AddBytes, long AddCalls)
    {
        internal static Counters Read() => new(Interlocked.Read(ref _mapperBytes), Interlocked.Read(ref _mapperCalls),
            Interlocked.Read(ref _listBytes), Interlocked.Read(ref _listCalls), Interlocked.Read(ref _addBytes), Interlocked.Read(ref _addCalls));
    }
    private sealed record Pending(string Route, int Index, int Operations, int Rows, Counters Before);
    private sealed record Window(Pending Input, Counters After, long AllocatedBefore, long AllocatedAfter, int Gen0, int Gen1, int Gen2);

    internal static void Configure(string receiptPath, int rows, string route)
    {
        if (_receiptPath is not null) throw new InvalidOperationException("Allocation observer is configured once per process.");
        _receiptPath = Path.GetFullPath(receiptPath); _rows = rows; _route = route;
        // Initialize the counters and scope helper before first/warmup/windows.
        using (Mapper()) { }
        AppDomain.CurrentDomain.UnhandledException += static (_, error) =>
        {
            if (_written) return;
            try { WriteFailure(error.ExceptionObject as Exception); }
            catch (Exception reporting) { Console.Error.WriteLine("Allocation failure receipt could not be written: " + reporting.Message); }
        };
    }

    internal readonly struct Scope : IDisposable
    {
        private readonly long _before;
        private readonly int _thread, _kind;
        internal Scope(int kind)
        { _kind = kind; _thread = Environment.CurrentManagedThreadId; _before = GC.GetAllocatedBytesForCurrentThread(); }
        [MethodImpl(MethodImplOptions.NoInlining)]
        public void Dispose()
        {
            if (_thread != Environment.CurrentManagedThreadId)
                throw new InvalidOperationException("A synchronous allocation scope crossed a managed thread.");
            var bytes = GC.GetAllocatedBytesForCurrentThread() - _before;
            if (bytes < 0) throw new InvalidOperationException("A synchronous allocation counter moved backwards.");
            switch (_kind)
            {
                case 0: Interlocked.Add(ref _mapperBytes, bytes); Interlocked.Increment(ref _mapperCalls); break;
                case 1: Interlocked.Add(ref _listBytes, bytes); Interlocked.Increment(ref _listCalls); break;
                case 2: Interlocked.Add(ref _addBytes, bytes); Interlocked.Increment(ref _addCalls); break;
                default: throw new InvalidOperationException("Unknown allocation scope.");
            }
        }
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    internal static Scope Mapper() => new(0);
    [MethodImpl(MethodImplOptions.NoInlining)]
    internal static List<T> CreateList<T>(int capacity)
    { using var scope = new Scope(1); return new List<T>(capacity); }
    [MethodImpl(MethodImplOptions.NoInlining)]
    internal static void Add<T>(List<T> values, T value)
    { using var scope = new Scope(2); values.Add(value); }

    internal static void BeginWindow(string route, int index, int operations, int rows)
    {
        if (_receiptPath is null || _pending is not null || rows != _rows)
            throw new InvalidOperationException("Allocation windows must be configured and serial.");
        _pending = new(route, index, operations, rows, Counters.Read());
    }
    internal static void EndWindow(long allocatedBefore, long allocatedAfter, int gen0, int gen1, int gen2)
    {
        var input = _pending ?? throw new InvalidOperationException("No active allocation window.");
        var after = Counters.Read();
        var expectedRows = checked((long)input.Operations * input.Rows);
        if (after.MapperCalls - input.Before.MapperCalls != expectedRows
            || after.ListCalls - input.Before.ListCalls != input.Operations
            || after.AddCalls - input.Before.AddCalls != expectedRows)
            throw new InvalidOperationException("The actual generated mapper/List scopes did not observe exactly the fully consumed business result.");
        Windows.Add(new(input, after, allocatedBefore, allocatedAfter, gen0, gen1, gen2));
        _pending = null;
    }

    internal static void Write()
    {
        if (_receiptPath is null || _pending is not null || Windows.Count == 0)
            throw new InvalidOperationException("Only complete diagnostic windows can receive a success receipt.");
        using var file = File.Create(_receiptPath + ".allocation.json");
        using var json = new Utf8JsonWriter(file, new() { Indented = true });
        Start(json, false);
        json.WriteString("BaseReceiptSha256", Hash(_receiptPath));
        WriteWindows(json); json.WriteEndObject();
        _written = true;
    }
    private static void WriteFailure(Exception? error)
    {
        if (_receiptPath is null) return;
        using var file = File.Create(_receiptPath + ".allocation.failure.json");
        using var json = new Utf8JsonWriter(file, new() { Indented = true });
        Start(json, true);
        json.WriteString("FailureType", error?.GetType().FullName);
        json.WriteString("FailureMessage", error?.Message);
        if (_pending is { } pending)
        {
            json.WriteString("PendingRoute", pending.Route); json.WriteNumber("PendingWindow", pending.Index);
            WriteDelta(json, pending.Before, Counters.Read());
        }
        WriteWindows(json); json.WriteEndObject();
    }
    private static void Start(Utf8JsonWriter json, bool failed)
    {
        json.WriteStartObject(); json.WriteNumber("SchemaVersion", 1); json.WriteBoolean("NativeAot", !RuntimeFeature.IsDynamicCodeSupported);
        json.WriteBoolean("TimingCredit", false); json.WriteBoolean("Failed", failed);
        json.WriteString("RouteFamily", _route); json.WriteNumber("ResultRows", _rows);
        json.WriteString("ExecutableSha256", Hash(Environment.ProcessPath!));
        var provenance = Path.Combine(AppContext.BaseDirectory, "allocation-build-receipt.json");
        json.WriteString("BuildReceiptPath", provenance); json.WriteString("BuildReceiptSha256", File.Exists(provenance) ? Hash(provenance) : null);
        json.WriteString("BaseReceiptPath", _receiptPath);
        json.WriteString("Scope", "Independent instrumented query-phases consumer. Raw whole-process allocation and GC are retained from the original window. Actual generated synchronous mapper bodies and List constructor/Add use same-thread allocation deltas, including codec/driver scratch allocated inside those bodies. They are observed scopes, not pure DTO live-object estimates. FrameworkOnlyBytes remains null; no subtraction or timing credit is permitted. First/warmup scopes are excluded by counter snapshots. Counter/window-report allocations occur outside the observed mapper/List scopes; reporting and window objects are outside the original process window. The unchanged query oracle still consumes and checks every row.");
    }
    private static void WriteWindows(Utf8JsonWriter json)
    {
        json.WriteStartArray("Windows");
        foreach (var window in Windows)
        {
            json.WriteStartObject(); json.WriteString("Route", window.Input.Route); json.WriteNumber("Index", window.Input.Index);
            json.WriteNumber("Operations", window.Input.Operations); json.WriteNumber("RowsPerOperation", window.Input.Rows);
            json.WriteNumber("ProcessAllocatedBefore", window.AllocatedBefore); json.WriteNumber("ProcessAllocatedAfter", window.AllocatedAfter);
            json.WriteNumber("ProcessAllocatedBytes", window.AllocatedAfter - window.AllocatedBefore);
            json.WriteNumber("ProcessGen0", window.Gen0); json.WriteNumber("ProcessGen1", window.Gen1); json.WriteNumber("ProcessGen2", window.Gen2);
            WriteDelta(json, window.Input.Before, window.After); json.WriteEndObject();
        }
        json.WriteEndArray();
    }
    private static void WriteDelta(Utf8JsonWriter json, Counters before, Counters after)
    {
        json.WriteNumber("MapperCalls", after.MapperCalls - before.MapperCalls); json.WriteNumber("MapperBytes", after.MapperBytes - before.MapperBytes);
        json.WriteNumber("ListConstructorCalls", after.ListCalls - before.ListCalls); json.WriteNumber("ListConstructorBytes", after.ListBytes - before.ListBytes);
        json.WriteNumber("ListAddCalls", after.AddCalls - before.AddCalls); json.WriteNumber("ListAddBytes", after.AddBytes - before.AddBytes);
        json.WriteNumber("ObservedMapperAndListBytes", after.MapperBytes - before.MapperBytes + after.ListBytes - before.ListBytes + after.AddBytes - before.AddBytes);
        json.WriteNull("FrameworkOnlyBytes");
    }
    private static string Hash(string path)
    { using var file = File.OpenRead(path); return Convert.ToHexStringLower(SHA256.HashData(file)); }
}
