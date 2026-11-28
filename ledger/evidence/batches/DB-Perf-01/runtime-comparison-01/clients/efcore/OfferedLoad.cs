using System.Diagnostics;
using System.Numerics;
using System.Threading.Channels;

// Shared unchanged by the public Korda and independent ORM consumers. All queue
// storage, worker state and histogram arrays are bounded and prepared before the
// measurement starts. Async scheduling allocations remain in the raw E2E total;
// an empty-driver run measures this harness separately, without blind subtraction.
internal sealed class OfferedLoad : IDisposable
{
    private readonly record struct Job(long Index, long PlannedTicks);
    private sealed class WorkerState
    {
        internal long Started, Succeeded, Failed, Rows, Suspensions;
        internal ulong Digest;
        internal string? FirstError;
        internal readonly long[] Service = new long[8192], Response = new long[8192],
            AllResponse = new long[8192], Queue = new long[8192];
        internal readonly string?[] ErrorNames = new string?[16];
        internal readonly long[] ErrorCounts = new long[16];
    }

    private readonly double _seconds, _rate;
    private readonly Channel<Job> _queue;
    private readonly Func<long, ValueTask<OperationResult>>[] _operations;
    private readonly WorkerState[] _workers;
    private readonly ManualResetEventSlim _producerStart = new(false), _producerReady = new(false);
    private readonly TaskCompletionSource _producerDone = new(TaskCreationOptions.RunContinuationsAsynchronously);
    private readonly Thread _producer;
    private readonly long[] _plannedBySecond, _sentBySecond, _startedBySecond, _succeededBySecond,
        _failedBySecond, _rejectedBySecond, _rowsBySecond;
    private long _attempted, _sent, _rejected, _offeredEndTicks, _offeredEndAllocated, _oracleFailuresBefore;
    private int _offeredEndGen0, _offeredEndGen1, _offeredEndGen2, _truncated, _started;
    internal long Planned { get; }
    internal int QueueCapacity { get; }
    internal long StartedTicks { get; private set; }
    internal long DeadlineTicks { get; private set; }
    internal Task Completion { get; }

    internal OfferedLoad(double seconds, double rate, int queueCapacity,
        Func<long, ValueTask<OperationResult>>[] operations)
    {
        if (!double.IsFinite(seconds) || seconds is <= 0 or > 86400 || !double.IsFinite(rate)
            || rate is <= 0 or > 1_000_000 || queueCapacity is < 1 or > 65536
            || operations.Length is < 1 or > 256)
            throw new ArgumentOutOfRangeException(nameof(seconds), "Offered load must be finite and bounded.");
        _seconds = seconds; _rate = rate; QueueCapacity = queueCapacity;
        Planned = checked((long)Math.Ceiling(seconds * rate));
        _operations = operations;
        _queue = Channel.CreateBounded<Job>(new BoundedChannelOptions(queueCapacity)
        {
            SingleWriter = true, SingleReader = operations.Length == 1,
            AllowSynchronousContinuations = false, FullMode = BoundedChannelFullMode.Wait
        });
        // Grow the bounded channel's internal deque outside the allocation boundary.
        for (var i = 0; i < queueCapacity; i++)
            if (!_queue.Writer.TryWrite(new(-1, 0))) throw new InvalidOperationException("Queue preallocation failed.");
        while (_queue.Reader.TryRead(out _)) { }
        var size = checked((int)Math.Ceiling(seconds) + 301);
        _plannedBySecond = new long[size]; _sentBySecond = new long[size]; _startedBySecond = new long[size];
        _succeededBySecond = new long[size]; _failedBySecond = new long[size];
        _rejectedBySecond = new long[size]; _rowsBySecond = new long[size];
        for (var second = 0; second < Math.Ceiling(seconds); second++)
            _plannedBySecond[second] = Math.Min(Planned, checked((long)Math.Ceiling((second + 1) * rate)))
                - Math.Min(Planned, checked((long)Math.Ceiling(second * rate)));
        _workers = new WorkerState[operations.Length];
        var tasks = new Task[operations.Length + 1];
        for (var i = 0; i < _workers.Length; i++)
        {
            _workers[i] = new();
            tasks[i] = Consume(i);
        }
        tasks[^1] = _producerDone.Task;
        Completion = Task.WhenAll(tasks);
        _ = _producerStart.WaitHandle; _ = _producerReady.WaitHandle;
        _producer = new Thread(Produce) { IsBackground = true, Name = "db-perf-arrivals" };
        _producer.Start();
        _producerReady.Wait();
    }

    internal void Start()
    {
        if (Interlocked.Exchange(ref _started, 1) != 0) throw new InvalidOperationException("The schedule runs once.");
        _oracleFailuresBefore = CorrectnessOracle.Failures;
        StartedTicks = Stopwatch.GetTimestamp();
        DeadlineTicks = StartedTicks + checked((long)(_seconds * Stopwatch.Frequency));
        _producerStart.Set();
    }

    private static void WaitUntil(long due)
    {
        while (true)
        {
            var left = due - Stopwatch.GetTimestamp();
            if (left <= 0) return;
            // The same arrival clock is used by both managed routes. Its CPU and
            // scheduling delay are visible in process CPU and scheduled latency.
            if (left > Stopwatch.Frequency / 500) Thread.Sleep(1);
            else Thread.SpinWait(32);
        }
    }

    private void Produce()
    {
        _producerReady.Set();
        _producerStart.Wait();
        try
        {
            for (long i = 0; i < Planned; i++)
            {
                var due = StartedTicks + checked((long)(i * (Stopwatch.Frequency / _rate)));
                WaitUntil(due);
                _attempted++;
                var now = Stopwatch.GetTimestamp();
                if (_queue.Writer.TryWrite(new(i, due))) { _sent++; Record(_sentBySecond, now, 1); }
                else { _rejected++; Record(_rejectedBySecond, now, 1); }
            }
            WaitUntil(DeadlineTicks);
            _offeredEndTicks = Stopwatch.GetTimestamp();
            _offeredEndAllocated = GC.GetTotalAllocatedBytes(precise: true);
            _offeredEndGen0 = GC.CollectionCount(0); _offeredEndGen1 = GC.CollectionCount(1); _offeredEndGen2 = GC.CollectionCount(2);
            _queue.Writer.TryComplete();
            _producerDone.SetResult();
        }
        catch (Exception error)
        {
            _queue.Writer.TryComplete(error);
            _producerDone.SetException(error);
        }
    }

    private async Task Consume(int index)
    {
        var worker = _workers[index];
        while (await _queue.Reader.WaitToReadAsync().ConfigureAwait(false))
        {
            while (_queue.Reader.TryRead(out var job))
            {
                var began = Stopwatch.GetTimestamp();
                worker.Started++; Record(_startedBySecond, began, 1);
                Add(worker.Queue, began - job.PlannedTicks);
                try
                {
                    var result = await _operations[index](job.Index).ConfigureAwait(false);
                    var ended = Stopwatch.GetTimestamp();
                    worker.Succeeded++; worker.Rows += result.Rows; worker.Suspensions += result.Suspensions;
                    worker.Digest ^= result.Digest;
                    Add(worker.Service, ended - began); Add(worker.Response, ended - job.PlannedTicks);
                    Add(worker.AllResponse, ended - job.PlannedTicks);
                    Record(_succeededBySecond, ended, 1); Record(_rowsBySecond, ended, result.Rows);
                }
                catch (Exception error)
                {
                    var ended = Stopwatch.GetTimestamp(); worker.Failed++;
                    Add(worker.AllResponse, ended - job.PlannedTicks); Record(_failedBySecond, ended, 1);
                    worker.FirstError ??= error.ToString();
                    var name = error.GetType().FullName ?? error.GetType().Name;
                    var slot = 0;
                    while (slot < worker.ErrorNames.Length - 1 && worker.ErrorNames[slot] is { } prior && prior != name) slot++;
                    worker.ErrorNames[slot] ??= slot == worker.ErrorNames.Length - 1 ? "other-error-types" : name;
                    worker.ErrorCounts[slot]++;
                }
            }
        }
    }

    private void Record(long[] values, long now, long amount)
    {
        var second = (now - StartedTicks) / Stopwatch.Frequency;
        if ((ulong)second >= (ulong)values.Length) { Volatile.Write(ref _truncated, 1); return; }
        Interlocked.Add(ref values[second], amount);
    }

    private static void Add(long[] histogram, long ticks)
    {
        var ns = Math.Max(1UL, (ulong)(Math.Max(0, ticks) * (1_000_000_000d / Stopwatch.Frequency)));
        var exponent = BitOperations.Log2(ns); var lower = 1UL << exponent;
        histogram[exponent * 128 + (int)((ns - lower) * 128 / lower)]++;
    }

    internal OfferedReceipt Snapshot()
    {
        if (!Completion.IsCompletedSuccessfully) throw new InvalidOperationException("Drain all workers before recording the schedule.");
        var end = Stopwatch.GetTimestamp();
        var started = _workers.Sum(w => w.Started); var succeeded = _workers.Sum(w => w.Succeeded);
        var failed = _workers.Sum(w => w.Failed);
        if (_attempted != Planned || _attempted != _sent + _rejected || started != _sent || started != succeeded + failed)
            throw new InvalidOperationException("Offered-load operation accounting does not reconcile.");
        var seconds = new OfferedSecond[Math.Min(_plannedBySecond.Length, (int)Math.Ceiling((end - StartedTicks) / (double)Stopwatch.Frequency) + 1)];
        for (var i = 0; i < seconds.Length; i++) seconds[i] = new(i, _plannedBySecond[i], _sentBySecond[i], _startedBySecond[i],
            _succeededBySecond[i], _failedBySecond[i], _rejectedBySecond[i], _rowsBySecond[i]);
        var errors = new Dictionary<string, long>(StringComparer.Ordinal);
        foreach (var worker in _workers)
            for (var i = 0; i < worker.ErrorNames.Length; i++)
                if (worker.ErrorNames[i] is { } name) { errors.TryGetValue(name, out var count); errors[name] = count + worker.ErrorCounts[i]; }
        long[] Merge(Func<WorkerState, long[]> select)
        {
            var result = new long[8192];
            foreach (var worker in _workers) { var data = select(worker); for (var i = 0; i < result.Length; i++) result[i] += data[i]; }
            return result;
        }
        var oracleFailuresAfter = CorrectnessOracle.Failures;
        return new(_rate, _seconds, QueueCapacity, StartedTicks, DeadlineTicks, _offeredEndTicks, end, Stopwatch.Frequency,
            _offeredEndAllocated, _offeredEndGen0, _offeredEndGen1, _offeredEndGen2,
            Planned, _attempted, _sent, started, succeeded + failed, succeeded, failed, _rejected, 0,
            _workers.Sum(w => w.Rows), _workers.Sum(w => w.Suspensions),
            Merge(w => w.Service), Merge(w => w.Response), Merge(w => w.AllResponse), Merge(w => w.Queue),
            seconds, _truncated != 0, errors, _workers.Where(w => w.FirstError is not null).Select(w => w.FirstError!).ToArray())
        {
            OracleFailuresBefore = _oracleFailuresBefore, OracleFailuresAfter = oracleFailuresAfter,
            OracleFailures = oracleFailuresAfter, FirstOracleFailure = CorrectnessOracle.FirstFailure
        };
    }

    public void Dispose()
    {
        if (Volatile.Read(ref _started) == 0) throw new InvalidOperationException("Start and join the prepared schedule before disposal.");
        if (!Completion.IsCompleted) throw new InvalidOperationException("Join the schedule before disposal.");
        _producer.Join(); _producerStart.Dispose(); _producerReady.Dispose();
    }
}

internal sealed record OfferedSecond(int Second, long Planned, long Sent, long Started, long Succeeded,
    long Failed, long Rejected, long Rows);
internal sealed record OfferedReceipt(double RequestsPerSecond, double OfferedSeconds, int QueueCapacity,
    long StartedTicks, long DeadlineTicks, long OfferedEndTicks, long DrainedTicks, long TimerFrequency,
    long AllocatedAtOfferedEnd, int Gen0AtOfferedEnd, int Gen1AtOfferedEnd, int Gen2AtOfferedEnd,
    long Planned, long Attempted, long Sent, long Started, long Completed, long Succeeded, long Failed,
    long Rejected, long Retries, long Rows, long Suspensions,
    long[] SuccessServiceHistogram, long[] SuccessScheduledHistogram, long[] AllCompletedScheduledHistogram,
    long[] StartDelayHistogram, OfferedSecond[] Seconds, bool TimeSeriesTruncated,
    Dictionary<string, long> ErrorClasses, string[] Errors)
{
    public long OracleFailuresBefore { get; init; }
    public long OracleFailuresAfter { get; init; }
    public long OracleFailures { get; init; }
    public OracleFailure? FirstOracleFailure { get; init; }
}
