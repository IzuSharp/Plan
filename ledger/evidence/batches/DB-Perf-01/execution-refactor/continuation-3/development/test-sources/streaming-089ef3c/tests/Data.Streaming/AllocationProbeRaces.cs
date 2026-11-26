using System.Buffers.Binary;
using Korda.Data;
using Korda.Database.Internal;

// Deterministic lifecycle tests for the lazy active-move join. Every transport
// completion is explicitly released, so a passing test cannot depend on a
// conveniently synchronous provider or a timing delay.
internal static class AllocationProbeRaces
{
    private static readonly TimeSpan Bound = TimeSpan.FromSeconds(10);
    private static int s_checks;
    private static bool s_borrowNative;

    internal static async Task RunAsync()
    {
        s_checks = 0;
        foreach (var borrowed in new[] { false, true })
        {
            s_borrowNative = borrowed;
            await DisposeDuringStart();
            await DisposeDuringFetch();
            await DisposeDuringMapping(failMapping: false, failCleanup: false);
            await DisposeDuringMapping(failMapping: true, failCleanup: false);
            await DisposeDuringMapping(failMapping: true, failCleanup: true);
            await CancellationDuringFetch();
            await DelayedMoveConsumption();
        }
        BorrowedBatchChecks.Run();
        Console.WriteLine($"PASS lazy stream join races: {s_checks} assertions; scoped native batches with and without forced-GC pending start/fetch, shared disposers, active mapper, primary/cleanup failures and cancellation");
    }

    private static async Task DisposeDuringStart()
    {
        var projection = Projection<long>.Create([ResultField.Create("id", Codecs.Int64)], static row => row.Read(0, Codecs.Int64));
        var transport = new ControlledTransport(projection, pendingFetch: false);
        var started = new TaskCompletionSource<IStreamTransport>(TaskCreationOptions.RunContinuationsAsynchronously);
        var sequence = Stream(projection, (_, _) => new(started.Task));
        var reader = sequence.GetAsyncEnumerator();
        var move = reader.MoveNextAsync().AsTask();
        Task first = reader.DisposeAsync().AsTask(), second = reader.DisposeAsync().AsTask();
        Check(!move.IsCompleted && !first.IsCompleted && !second.IsCompleted, "start admission and both disposers remain pending");
        try
        {
            started.SetResult(transport);
            await transport.JoinEntered.Task.WaitAsync(Bound);
            Check(!first.IsCompleted && !second.IsCompleted, "disposers wait for actual transport retirement after delayed start");
            Check(transport.Fetches == 0 && transport.Batch.Disposals == 0, "disposal before start completion cannot fetch or dispose an untransferred batch");
            transport.ReleaseJoin();
            await Failure<ObjectDisposedException>(move);
            await Task.WhenAll(first, second).WaitAsync(Bound);
            Check(transport.Joins == 1 && transport.Stops > 0, "delayed start cleanup joins once");
            await reader.DisposeAsync();
            Check(transport.Joins == 1, "repeated disposal observes the same retirement");
        }
        finally { started.TrySetResult(transport); transport.ReleaseJoin(); }
    }

    private static async Task DisposeDuringFetch()
    {
        int mapped = 0;
        var projection = Projection<long>.Create([ResultField.Create("id", Codecs.Int64)], row => { mapped++; return row.Read(0, Codecs.Int64); });
        var transport = new ControlledTransport(projection, pendingFetch: true);
        var reader = Stream(projection, transport.Start).GetAsyncEnumerator();
        var move = reader.MoveNextAsync().AsTask();
        await transport.FetchEntered.Task.WaitAsync(Bound);
        try
        {
            try { _ = reader.MoveNextAsync(); throw new InvalidOperationException("Expected concurrent-use rejection."); }
            catch (DatabaseException error) when (error.Kind == DatabaseErrorKind.ConcurrentUse) { s_checks++; }
            Task first = reader.DisposeAsync().AsTask(), second = reader.DisposeAsync().AsTask();
            Check(!first.IsCompleted && !second.IsCompleted && transport.Batch.Disposals == 0, "both disposers wait without releasing an outstanding fetch batch");
            transport.CompleteFetch();
            await transport.JoinEntered.Task.WaitAsync(Bound);
            Check(!first.IsCompleted && !second.IsCompleted, "fetch completion does not substitute for the retirement join");
            Check(mapped == 0 && transport.Batch.Disposals == 1, "batch is compensated once and never mapped after closure");
            transport.ReleaseJoin();
            await Failure<ObjectDisposedException>(move);
            await Task.WhenAll(first, second).WaitAsync(Bound);
            Check(transport.Joins == 1 && transport.Batch.Disposals == 1, "concurrent cleanup has one batch release and one join");
            try { _ = reader.MoveNextAsync(); throw new InvalidOperationException("Expected disposed rejection."); }
            catch (ObjectDisposedException) { s_checks++; }
        }
        finally { transport.CompleteFetch(); transport.ReleaseJoin(); }
    }

    private static async Task DisposeDuringMapping(bool failMapping, bool failCleanup)
    {
        using var releaseMapper = new ManualResetEventSlim();
        var enteredMapper = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var mappingFailure = new InvalidDataException("Controlled business mapper failure.");
        var cleanupFailure = new InvalidOperationException("Controlled cleanup failure after batch release.");
        var projection = Projection<long>.Create([ResultField.Create("id", Codecs.Int64)], row =>
        {
            enteredMapper.TrySetResult();
            if (!releaseMapper.Wait(Bound)) throw new TimeoutException("Mapper release was not delivered.");
            if (failMapping) throw mappingFailure;
            return row.Read(0, Codecs.Int64);
        });
        var transport = new ControlledTransport(projection, pendingFetch: false);
        var reader = Stream(projection, transport.Start).GetAsyncEnumerator();
        Task<bool> move = Task.Run(() => reader.MoveNextAsync().AsTask());
        try
        {
            await enteredMapper.Task.WaitAsync(Bound);
            Task first = reader.DisposeAsync().AsTask(), second = reader.DisposeAsync().AsTask();
            Check(!first.IsCompleted && !second.IsCompleted, "disposal joins a synchronously executing mapper");
            Check(transport.Batch.Disposals == 0 && transport.Joins == 0, "the mapper retains its batch until it exits");
            if (s_borrowNative)
            {
                GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();
                Check(transport.Batch.NativeReleases == 0, "active mapper retains native memory across forced GC");
            }
            releaseMapper.Set();
            await transport.JoinEntered.Task.WaitAsync(Bound);
            Check(transport.Batch.Disposals == 1 && !first.IsCompleted && !second.IsCompleted, "mapper exit releases the batch and still awaits retirement");
            transport.ReleaseJoin(failCleanup ? cleanupFailure : null);
            if (failMapping)
            {
                var failure = await Failure<InvalidDataException>(move);
                Check(ReferenceEquals(failure, mappingFailure), "cleanup preserves the original mapper exception instance");
                if (failCleanup)
                {
                    Check(ReferenceEquals(failure.Data["Korda.Database.StreamCleanup.v1"], cleanupFailure), "cleanup failure remains attached to the primary mapper failure");
                    Check(ReferenceEquals(await Failure<InvalidOperationException>(first), cleanupFailure), "first disposer observes the cleanup failure");
                    Check(ReferenceEquals(await Failure<InvalidOperationException>(second), cleanupFailure), "second disposer observes the same cleanup failure");
                }
                else await Task.WhenAll(first, second).WaitAsync(Bound);
            }
            else
            {
                Check(await move.WaitAsync(Bound), "an already admitted synchronous mapper retains its successful row");
                await Task.WhenAll(first, second).WaitAsync(Bound);
            }
            Check(transport.Joins == 1 && transport.Batch.Disposals == 1, "mapper race retirement is once-only");
            if (s_borrowNative) Check(transport.Batch.NativeReleases == 1, "native mapper buffer releases exactly once after the full synchronous read");
        }
        finally { releaseMapper.Set(); transport.ReleaseJoin(); }
    }

    private static async Task CancellationDuringFetch()
    {
        using var cancellation = new CancellationTokenSource();
        var projection = Projection<long>.Create([ResultField.Create("id", Codecs.Int64)], static row => row.Read(0, Codecs.Int64));
        var transport = new ControlledTransport(projection, pendingFetch: true);
        var reader = Stream(projection, transport.Start, cancellation.Token).GetAsyncEnumerator();
        var move = reader.MoveNextAsync().AsTask();
        try
        {
            await transport.FetchEntered.Task.WaitAsync(Bound);
            cancellation.Cancel();
            Check(transport.Stops > 0 && !move.IsCompleted, "cancellation requests stop without inventing a terminal fetch result");
            var disposing = reader.DisposeAsync().AsTask();
            transport.CancelFetch(cancellation.Token);
            await transport.JoinEntered.Task.WaitAsync(Bound);
            Check(!disposing.IsCompleted && !move.IsCompleted, "confirmed fetch cancellation still joins native-equivalent retirement");
            transport.ReleaseJoin();
            var failure = await Failure<OperationCanceledException>(move);
            Check(failure.CancellationToken == cancellation.Token, "cancellation retains its admitted token");
            await disposing.WaitAsync(Bound);
            Check(transport.Joins == 1 && transport.Batch.Disposals == 1, "canceled untransferred batch is compensated once");
        }
        finally { transport.CancelFetch(cancellation.Token); transport.ReleaseJoin(); }
    }

    private static TypedStream<long> Stream(Projection<long> projection, Func<int, CancellationToken, ValueTask<IStreamTransport>> start,
        CancellationToken token = default) => new(start, projection, 2, 71, [3], new(2, 4096, 2, 4096), token);
    private static async Task DelayedMoveConsumption()
    {
        var projection = Projection<long>.Create([ResultField.Create("id", Codecs.Int64)], static row => row.Read(0, Codecs.Int64));
        var transports = Enumerable.Range(0, 3).Select(_ => new ControlledTransport(projection, pendingFetch: true)).ToArray();
        var readers = transports.Select(transport => Stream(projection, transport.Start).GetAsyncEnumerator()).ToArray();
        try
        {
            var first = readers[0].MoveNextAsync();
            await transports[0].FetchEntered.Task.WaitAsync(Bound);
            Check(!first.IsCompleted, "first move really suspends before delayed consumption");
            transports[0].CompleteFetch();
            var started = System.Diagnostics.Stopwatch.GetTimestamp();
            while (!first.IsCompleted)
            {
                if (System.Diagnostics.Stopwatch.GetElapsedTime(started) > Bound) throw new TimeoutException("Delayed move did not complete.");
                await Task.Delay(1);
            }
            // Completion alone does not consume the ValueTask. A second pending
            // move of this closed generic type cannot take its state-machine box.
            var second = readers[1].MoveNextAsync();
            await transports[1].FetchEntered.Task.WaitAsync(Bound);
            Check(!second.IsCompleted && first.IsCompletedSuccessfully, "another pending move cannot overwrite an unconsumed completed move");
            Check(first.Result && readers[0].Current == 42, "the delayed single GetResult preserves its original result");
            var retainedTask = second.AsTask();
            transports[1].CompleteFetch();
            Check(await retainedTask.WaitAsync(Bound) && readers[1].Current == 42, "a pending ValueTask converts once to an independently retained Task");
            var third = readers[2].MoveNextAsync();
            await transports[2].FetchEntered.Task.WaitAsync(Bound);
            transports[2].CompleteFetch();
            Check(await third && readers[2].Current == 42, "a later suspended move safely reuses available runtime state");
            Check(await retainedTask && await retainedTask, "the Task returned by one AsTask conversion remains reusable after later moves");
        }
        finally
        {
            for (var i = 0; i < readers.Length; i++)
            {
                transports[i].CompleteFetch();
                var close = readers[i].DisposeAsync().AsTask();
                await transports[i].JoinEntered.Task.WaitAsync(Bound);
                transports[i].ReleaseJoin();
                await close.WaitAsync(Bound);
            }
        }
        Check(transports.All(transport => transport.Batch.Disposals == 1 && transport.Joins == 1),
            "delayed consumption and retained Tasks do not leak or duplicate batch retirement");
    }
    private static void Check(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
        Interlocked.Increment(ref s_checks);
    }
    private static async Task<TException> Failure<TException>(Task task) where TException : Exception
    {
        try { await task.WaitAsync(Bound); }
        catch (TException error) { s_checks++; return error; }
        throw new InvalidOperationException("Expected " + typeof(TException).Name);
    }

    private sealed class ControlledTransport : IStreamTransport
    {
        private readonly Task<IStreamTransport> _start;
        private readonly Task<ScopedStreamBatch> _ready;
        private readonly TaskCompletionSource<ScopedStreamBatch>? _fetch;
        private readonly TaskCompletionSource<StreamRetirement> _retirement = new(TaskCreationOptions.RunContinuationsAsynchronously);
        internal readonly TaskCompletionSource FetchEntered = new(TaskCreationOptions.RunContinuationsAsynchronously);
        internal readonly TaskCompletionSource JoinEntered = new(TaskCreationOptions.RunContinuationsAsynchronously);
        internal readonly ITrackedBatch Batch;
        internal int Fetches, Stops, Joins;
        internal ControlledTransport(Projection<long> projection, bool pendingFetch)
        {
            byte[] scalar = new byte[8]; BinaryPrimitives.WriteInt64LittleEndian(scalar, 42);
            var expectation = new WireExpectation(PayloadKind.Rows, 2, Convert.FromHexString(projection.ShapeHash), 0, 71,
                [new(0, Codecs.Int64.Descriptor, 3)]);
            var bytes = DbWire.Encode(expectation, 1, [new ReadOnlyMemory<byte>(scalar)]);
            Batch = new ScopedBatchFixture(bytes);
            _start = Task.FromResult<IStreamTransport>(this); _ready = Task.FromResult(Batch.Batch);
            if (pendingFetch) _fetch = new(TaskCreationOptions.RunContinuationsAsynchronously);
        }
        internal ValueTask<IStreamTransport> Start(int rows, CancellationToken token) => new(_start);
        public ValueTask<ScopedStreamBatch> FetchAsync()
        {
            if (Interlocked.Increment(ref Fetches) != 1) throw new InvalidOperationException("Race fixture fetched twice.");
            Batch.Acquire(); FetchEntered.TrySetResult(); return new(_fetch?.Task ?? _ready);
        }
        internal void CompleteFetch() => _fetch?.TrySetResult(Batch.Batch);
        internal void CancelFetch(CancellationToken token)
        {
            if (_fetch is { Task.IsCompleted: false }) { Batch.Dispose(); _fetch.TrySetCanceled(token); }
        }
        public void RequestStop() => Interlocked.Increment(ref Stops);
        public Task<StreamRetirement> JoinAsync()
        {
            Check(!Batch.Active, "transport retirement begins after batch release");
            Interlocked.Increment(ref Joins); JoinEntered.TrySetResult(); return _retirement.Task;
        }
        internal void ReleaseJoin(Exception? failure = null)
        {
            if (failure is null) _retirement.TrySetResult(new(true, true, 0));
            else _retirement.TrySetException(failure);
        }
    }
}
