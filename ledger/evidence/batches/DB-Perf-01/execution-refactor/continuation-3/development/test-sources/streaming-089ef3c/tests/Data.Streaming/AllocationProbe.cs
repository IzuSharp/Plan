using System.Buffers.Binary;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Korda.Data;
using Korda.Database.Internal;

// This is an isolated internal-transport diagnostic, not a provider/package
// acceptance test. Driver controls are reported separately, never subtracted
// or rounded down to manufacture a zero-allocation result.
internal static class AllocationProbe
{
    private const uint Profile = 2, ProjectionId = 71;
    private static long s_sink;
    private readonly record struct NumberRow(long Id, long Amount);
    private readonly record struct Counts(long Operations, long Rows, long Fetches, long SuspendedMoves, long Checksum);
    private readonly record struct Counter(long Bytes, int Gen0, int Gen1, int Gen2, long Timestamp);
    private readonly record struct Window(Counter Before, Counter After, Counts Counts);
    private static readonly Projection<NumberRow> Shape = Projection<NumberRow>.Create(
        [ResultField.Create("id", Codecs.Int64), ResultField.Create("amount", Codecs.Int64)],
        static row => new(row.Read(0, Codecs.Int64), row.Read(1, Codecs.Int64)));

    internal static async Task RunAsync(string output, string[] args)
    {
        string lane = Option(args, "--probe-lane=", "sync-inbatch");
        int rounds = Integer(args, "--probe-rounds=", 64, 1, 512);
        int rows = Integer(args, "--probe-rows=", lane is "sync-inbatch" or "inbatch-control" ? 4096 : 256, 2, 4096);
        int batches = Integer(args, "--probe-batches=", 8, 1, 256);
        const int warmupOperations = 32;
        bool asynchronous = lane is "stream-async" or "driver-async";
        bool scalar = lane is "utf8-validation" or "decimal-validation" or "scalar-control";
        if (lane is not ("sync-inbatch" or "inbatch-control" or "stream-sync" or "stream-async" or
            "driver-sync" or "driver-async" or "utf8-validation" or "decimal-validation" or "scalar-control"))
            throw new ArgumentException("Unknown allocation-probe lane.");

        var expected = new WireExpectation(PayloadKind.Rows, Profile, Convert.FromHexString(Shape.ShapeHash), 0,
            ProjectionId, [new(0, Codecs.Int64.Descriptor, 3), new(1, Codecs.Int64.Descriptor, 3)]);
        byte[] data = Batch(expected, rows);
        byte[] end = DbWire.Encode(expected, 0, Array.Empty<ReadOnlyMemory<byte>?>());
        using var transport = new Transport(data, end, batches, asynchronous);
        var windows = new Window[lane is "sync-inbatch" or "inbatch-control" ? rounds : 1];
        byte[] scalarBytes = lane == "decimal-validation"
            ? Codecs.Decimal(24, 7).Encode(12345678901234567.1234567m)!
            : Encoding.UTF8.GetBytes("A bounded UTF-8 field: 订单数据库 — Καλημέρα — 😀 — repeated owned value.");
        CodecDescriptor scalarCodec = lane == "decimal-validation" ? Codecs.Decimal(24, 7).Descriptor : Codecs.String.Descriptor;

        // All immutable payloads, thread/event owners, static mappings and the
        // result array exist before warm-up and the measured boundaries.
        if (scalar) _ = ScalarLoop(lane, scalarCodec, scalarBytes, warmupOperations * rows);
        else if (lane is "sync-inbatch" or "inbatch-control")
        {
            for (int i = 0; i < warmupOperations; i++) _ = InBatch(transport, rows, lane == "inbatch-control", measure: false);
        }
        else _ = await Queries(transport, rows, batches, warmupOperations, lane.StartsWith("driver-", StringComparison.Ordinal));
        _ = GC.GetTotalAllocatedBytes(true);
        _ = GC.CollectionCount(0); _ = GC.CollectionCount(1); _ = GC.CollectionCount(2);
        _ = Stopwatch.GetTimestamp();

        if (scalar)
        {
            var before = Begin();
            long checksum = ScalarLoop(lane, scalarCodec, scalarBytes, checked(rounds * rows));
            var after = End();
            windows[0] = new(before, after, new(rounds * (long)rows, 0, 0, 0, checksum));
        }
        else if (lane is "sync-inbatch" or "inbatch-control")
        {
            for (int i = 0; i < rounds; i++) windows[i] = InBatch(transport, rows, lane == "inbatch-control", measure: true);
        }
        else
        {
            var before = Begin();
            Counts counts = await Queries(transport, rows, batches, rounds, lane.StartsWith("driver-", StringComparison.Ordinal));
            var after = End();
            windows[0] = new(before, after, counts);
        }

        long allocated = 0, completedRows = 0, operations = 0, fetches = 0, suspended = 0;
        foreach (var window in windows)
        {
            allocated = checked(allocated + window.After.Bytes - window.Before.Bytes);
            completedRows += window.Counts.Rows; operations += window.Counts.Operations;
            fetches += window.Counts.Fetches; suspended += window.Counts.SuspendedMoves;
        }
        transport.AssertDrained();
        if (asynchronous && suspended != fetches) throw new InvalidOperationException("Every synthetic async fetch must cause an observed incomplete await.");

        string path = Path.Combine(output, "allocation-probe-" + lane + ".json");
        using (var file = File.Create(path))
        using (var json = new Utf8JsonWriter(file, new JsonWriterOptions { Indented = true }))
        {
            json.WriteStartObject();
            json.WriteNumber("schema", 2);
            json.WriteString("kind", "isolated-scoped-native-stream-transport-diagnostic");
            json.WriteString("lane", lane);
            json.WriteBoolean("publicProviderAcceptance", false);
            json.WriteString("sourceCommitDeclaredByRunner", Option(args, "--probe-source-commit=", "unspecified"));
            json.WriteString("label", Option(args, "--probe-label=", "unspecified"));
            json.WriteString("runtime", RuntimeInformation.FrameworkDescription);
            json.WriteString("architecture", RuntimeInformation.ProcessArchitecture.ToString());
            json.WriteString("os", RuntimeInformation.OSDescription);
            json.WriteNumber("processorCount", Environment.ProcessorCount);
            json.WriteNumber("processId", Environment.ProcessId);
            json.WriteString("recordedAtUtc", DateTimeOffset.UtcNow);
            json.WriteBoolean("dynamicCodeSupported", System.Runtime.CompilerServices.RuntimeFeature.IsDynamicCodeSupported);
            json.WriteString("executable", Environment.ProcessPath);
            if (Environment.ProcessPath is { } executable)
            {
                using var binary = File.OpenRead(executable);
                json.WriteString("executableSha256", Convert.ToHexStringLower(SHA256.HashData(binary)));
            }
            json.WriteString("batchSha256", Convert.ToHexStringLower(SHA256.HashData(data)));
            json.WriteString("scalarInputSha256", Convert.ToHexStringLower(SHA256.HashData(scalarBytes)));
            json.WriteNumber("rowsPerBatch", rows); json.WriteNumber("batchesPerQuery", batches);
            json.WriteNumber("warmupOperations", warmupOperations); json.WriteNumber("rounds", rounds);
            json.WriteNumber("immutableDriverPayloadBytes", data.Length + end.Length);
            json.WriteNumber("driverMaximumConcurrentBatches", 1);
            json.WriteNumber("driverWorkerThreads", asynchronous ? 1 : 0);
            json.WriteNumber("driverLiveBatchesAfterDrain", transport.LiveBatches);
            json.WriteNumber("driverPendingCompletionsAfterDrain", transport.PendingCompletions);
            json.WriteNumber("managedAllocatedBytesRaw", allocated);
            json.WriteNumber("completedOperations", operations); json.WriteNumber("completedRows", completedRows);
            json.WriteNumber("fetchesInMeasuredBoundary", fetches); json.WriteNumber("observedIncompleteMovesOrFetches", suspended);
            json.WriteNumber("businessOutputAllocatedBytes", 0);
            json.WriteString("attribution", "No reference DTO/string/list output is materialized. Numeric DTO is a value type. Raw totals include framework, runtime, and measured driver/harness work. No control subtraction or per-path zero assertion.");
            json.WriteString("boundary", lane == "sync-inbatch"
                ? "Each window starts after the first row of an acquired batch and ends after its last row; stream creation, fetch, batch parsing and disposal are excluded."
                : lane == "inbatch-control" ? "Independent synchronous arithmetic loop control, without TypedStream; no zero result is transferred to another lane."
                : scalar ? "Repeated scalar validation only; immutable input and codec construction are excluded."
                : "Every query's TypedStream construction (except driver controls), enumeration, all batch fetches, completion and cleanup are included. Synthetic payload/thread construction is excluded.");
            json.WriteString("driver", "Bounded reusable scoped-native owner transport. Each fetch copies setup bytes into a fresh NativeMemory buffer and roots only its release counter; that fixture work is inside whole-query/driver windows and outside in-batch windows. Sync uses precreated completed tasks. Async allocates its own TCS/Task per fetch and publishes from one worker only after the consumer observes an incomplete await. Driver totals remain separate and are not subtracted.");
            json.WriteStartArray("windows");
            foreach (var window in windows)
            {
                json.WriteStartObject();
                WriteCounter(json, "before", window.Before); WriteCounter(json, "after", window.After);
                json.WriteNumber("allocatedBytes", window.After.Bytes - window.Before.Bytes);
                json.WriteNumber("operations", window.Counts.Operations); json.WriteNumber("rows", window.Counts.Rows);
                json.WriteNumber("fetches", window.Counts.Fetches); json.WriteNumber("observedIncomplete", window.Counts.SuspendedMoves);
                json.WriteNumber("checksum", window.Counts.Checksum);
                json.WriteEndObject();
            }
            json.WriteEndArray(); json.WriteEndObject();
        }
        Console.WriteLine($"ALLOCATION-PROBE {lane}: rawBytes={allocated}, operations={operations}, rows={completedRows}, fetches={fetches}, incomplete={suspended}; {path}");
    }

    private static Window InBatch(Transport transport, int rows, bool control, bool measure)
    {
        transport.Reset();
        var reader = Stream(transport, rows).GetAsyncEnumerator();
        try
        {
            if (!Completed(reader.MoveNextAsync())) throw new InvalidOperationException("Probe needs its initial row.");
            var before = measure ? Begin() : default;
            long checksum = 0;
            for (int i = 2; i <= rows; i++)
            {
                if (control) checksum += i * 4L;
                else
                {
                    if (!Completed(reader.MoveNextAsync())) throw new InvalidOperationException("The in-batch window ended early.");
                    var row = reader.Current;
                    if (row.Id != i || row.Amount != i * 3L) throw new InvalidOperationException("Numeric mapping differs.");
                    checksum += row.Id + row.Amount;
                }
            }
            var after = measure ? End() : default;
            Volatile.Write(ref s_sink, checksum);
            if (checksum != 2L * rows * (rows + 1) - 4) throw new InvalidOperationException("Incorrect in-batch checksum.");
            return new(before, after, new(1, rows - 1, 0, 0, checksum));
        }
        finally
        {
            var disposal = reader.DisposeAsync();
            if (!disposal.IsCompleted) throw new InvalidOperationException("Synchronous probe cleanup unexpectedly suspended.");
            disposal.GetAwaiter().GetResult();
            transport.AssertDrained();
        }
    }

    private static async Task<Counts> Queries(Transport transport, int rows, int batches, int operations, bool driver)
    {
        long completedRows = 0, fetchesBefore = transport.Fetches, suspended = 0, checksum = 0;
        for (int operation = 0; operation < operations; operation++)
        {
            transport.Reset();
            if (driver)
            {
                while (true)
                {
                    var pending = transport.FetchAsync();
                    if (!pending.IsCompleted) { suspended++; transport.ReleasePending(); }
                    using var batch = await pending.ConfigureAwait(false);
                    if (batch.End) break;
                    for (int i = 1; i <= rows; i++) { checksum += i * 4L; completedRows++; }
                }
                transport.RequestStop();
                _ = await transport.JoinAsync().ConfigureAwait(false);
            }
            else
            {
                await using var reader = Stream(transport, rows).GetAsyncEnumerator();
                while (true)
                {
                    var pending = reader.MoveNextAsync();
                    if (!pending.IsCompleted) { suspended++; transport.ReleasePending(); }
                    if (!await pending.ConfigureAwait(false)) break;
                    var row = reader.Current;
                    long expectedId = completedRows % rows + 1;
                    if (row.Id != expectedId || row.Amount != expectedId * 3) throw new InvalidOperationException("Numeric mapping differs.");
                    checksum += row.Id + row.Amount; completedRows++;
                }
            }
            transport.AssertDrained();
        }
        if (completedRows != operations * (long)batches * rows || checksum != operations * (long)batches * 2 * rows * (rows + 1))
            throw new InvalidOperationException("Full query output differs.");
        Volatile.Write(ref s_sink, checksum);
        return new(operations, completedRows, transport.Fetches - fetchesBefore, suspended, checksum);
    }

    private static long ScalarLoop(string lane, CodecDescriptor codec, byte[] bytes, int count)
    {
        long checksum = 0;
        for (int i = 0; i < count; i++)
        {
            if (lane != "scalar-control") DbWire.ValidateScalar(codec, bytes);
            checksum += bytes[i % bytes.Length];
        }
        Volatile.Write(ref s_sink, checksum);
        return checksum;
    }
    private static TypedStream<NumberRow> Stream(Transport transport, int rows) => new(transport.Start, Shape, Profile,
        ProjectionId, [3, 3], new(rows, 1024 * 1024, rows, 16 * 1024 * 1024));
    private static bool Completed(ValueTask<bool> value)
    {
        if (!value.IsCompleted) throw new InvalidOperationException("The in-batch probe must complete synchronously.");
        return value.GetAwaiter().GetResult();
    }
    private static byte[] Batch(WireExpectation expected, int rows)
    {
        var cells = new ReadOnlyMemory<byte>?[rows * 2];
        for (int i = 0; i < rows; i++)
        {
            var id = new byte[8]; var amount = new byte[8];
            BinaryPrimitives.WriteInt64LittleEndian(id, i + 1); BinaryPrimitives.WriteInt64LittleEndian(amount, (i + 1) * 3L);
            cells[i * 2] = id; cells[i * 2 + 1] = amount;
        }
        return DbWire.Encode(expected, checked((uint)rows), cells);
    }
    private static Counter Begin()
    {
        int gen0 = GC.CollectionCount(0), gen1 = GC.CollectionCount(1), gen2 = GC.CollectionCount(2);
        long timestamp = Stopwatch.GetTimestamp();
        return new(GC.GetTotalAllocatedBytes(true), gen0, gen1, gen2, timestamp);
    }
    private static Counter End()
    {
        long bytes = GC.GetTotalAllocatedBytes(true);
        return new(bytes, GC.CollectionCount(0), GC.CollectionCount(1), GC.CollectionCount(2), Stopwatch.GetTimestamp());
    }
    private static void WriteCounter(Utf8JsonWriter json, string name, Counter counter)
    {
        json.WriteStartObject(name); json.WriteNumber("totalAllocatedBytes", counter.Bytes);
        json.WriteNumber("gen0", counter.Gen0); json.WriteNumber("gen1", counter.Gen1); json.WriteNumber("gen2", counter.Gen2);
        json.WriteNumber("stopwatchTimestamp", counter.Timestamp); json.WriteEndObject();
    }
    private static string Option(string[] args, string prefix, string fallback) => args.FirstOrDefault(value => value.StartsWith(prefix, StringComparison.Ordinal)) is { } value ? value[prefix.Length..] : fallback;
    private static int Integer(string[] args, string prefix, int fallback, int minimum, int maximum)
    {
        int value = int.Parse(Option(args, prefix, fallback.ToString(System.Globalization.CultureInfo.InvariantCulture)), System.Globalization.CultureInfo.InvariantCulture);
        if (value < minimum || value > maximum) throw new ArgumentOutOfRangeException(prefix);
        return value;
    }

    private sealed class Transport : IStreamTransport, IDisposable
    {
        private readonly object _gate = new();
        private readonly BatchOwner _data, _end;
        private readonly Task<ScopedStreamBatch> _dataTask, _endTask;
        private readonly Task<IStreamTransport> _start;
        private readonly Task<StreamRetirement> _join = Task.FromResult(new StreamRetirement(true, true, 0));
        private readonly int _batches;
        private readonly AutoResetEvent? _signal;
        private readonly Thread? _worker;
        private TaskCompletionSource<ScopedStreamBatch>? _pending;
        private ScopedStreamBatch? _pendingBatch;
        private int _fetch, _stopped, _exit;
        internal long Fetches { get; private set; }
        internal int LiveBatches => _data.Active + _end.Active;
        internal int PendingCompletions { get { lock (_gate) return _pending is null ? 0 : 1; } }
        internal Transport(byte[] data, byte[] end, int batches, bool asynchronous)
        {
            _data = new(data, false); _end = new(end, true); _batches = batches;
            _dataTask = Task.FromResult(_data.Batch); _endTask = Task.FromResult(_end.Batch);
            _start = Task.FromResult<IStreamTransport>(this);
            if (asynchronous)
            {
                _signal = new(false); _worker = new(CompleteLoop) { IsBackground = true, Name = "allocation-probe-fetch" }; _worker.Start();
            }
        }
        internal ValueTask<IStreamTransport> Start(int rows, CancellationToken token) { token.ThrowIfCancellationRequested(); return new(_start); }
        internal void Reset() { AssertDrained(); _fetch = 0; _stopped = 0; }
        public ValueTask<ScopedStreamBatch> FetchAsync()
        {
            if (_stopped != 0 || LiveBatches != 0 || _fetch > _batches) throw new InvalidOperationException("Invalid bounded probe fetch.");
            var batch = _fetch++ == _batches ? _end : _data;
            batch.Acquire(); Fetches++;
            if (_worker is null) return new(batch.End ? _endTask : _dataTask);
            lock (_gate)
            {
                if (_pending is not null) throw new InvalidOperationException("A probe fetch is already pending.");
                _pendingBatch = batch.Batch; _pending = new(TaskCreationOptions.RunContinuationsAsynchronously);
                return new(_pending.Task);
            }
        }
        internal void ReleasePending()
        {
            lock (_gate) if (_pending is null) throw new InvalidOperationException("An incomplete probe move has no pending fetch.");
            _signal!.Set();
        }
        private void CompleteLoop()
        {
            while (true)
            {
                _signal!.WaitOne();
                if (Volatile.Read(ref _exit) != 0) return;
                TaskCompletionSource<ScopedStreamBatch> pending; ScopedStreamBatch batch;
                lock (_gate)
                {
                    pending = _pending ?? throw new InvalidOperationException("Missing pending fetch.");
                    batch = _pendingBatch!; _pending = null; _pendingBatch = null;
                }
                pending.SetResult(batch);
            }
        }
        public void RequestStop() => _stopped = 1;
        public Task<StreamRetirement> JoinAsync() { AssertDrained(); return _join; }
        internal void AssertDrained()
        {
            if (LiveBatches != 0 || PendingCompletions != 0) throw new InvalidOperationException("Probe driver has an unretired batch or completion.");
        }
        public void Dispose()
        {
            AssertDrained(); Volatile.Write(ref _exit, 1); _signal?.Set(); _worker?.Join(); _signal?.Dispose();
        }
    }
    private sealed class BatchOwner(byte[] bytes, bool end) : ScopedBatchFixture(bytes, end)
    {
        internal new int Active => base.Active ? 1 : 0;
    }
}
