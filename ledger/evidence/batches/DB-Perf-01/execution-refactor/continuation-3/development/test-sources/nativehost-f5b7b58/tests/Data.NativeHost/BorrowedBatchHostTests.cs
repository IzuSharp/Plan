using System.Text.Json.Serialization;
using Korda.Data;
using Korda.Database;
using Korda.Database.PostgreSql;
using Korda.Database.Sqlite;
using Korda.Interop;

// Real provider integration for the borrowed native batch path. The separate
// Streaming fixture checks scoped native ownership under forced release; these
// tests keep the complete public StreamAsync -> synchronous mapper boundary.
internal static class BorrowedBatchHostTests
{
    private static readonly TimeSpan Bound = TimeSpan.FromSeconds(10);
    private static readonly ValueCodec<BorrowedHostPayload> Json = Codecs.Json(BorrowedHostJson.Default.BorrowedHostPayload);
    private static int _checks;
    private enum Stop { Dispose, Cancel, SourceClose, SessionClose }

    internal static async Task Run(DatabaseProvider provider, string connection)
    {
        var before = _checks;
        foreach (var batchRows in new[] { 1, 2 })
            foreach (var stop in new[] { Stop.Dispose, Stop.Cancel, Stop.SourceClose, Stop.SessionClose })
                foreach (var failMapping in new[] { false, true })
                    await DuringMapping(provider, connection, stop, failMapping, batchRows);
        Console.WriteLine($"BORROWED_HOST_PASS provider={provider} scenarios=16 assertions={_checks - before}; unknown/known EOF buffers survive complete mapper scopes and decoded values own their data");
    }

    private static async Task DuringMapping(DatabaseProvider provider, string connection, Stop stop, bool failMapping, int batchRows)
    {
        Console.WriteLine($"BORROWED_HOST_CASE provider={provider} stop={stop} mapperFailure={failMapping} batchRows={batchRows}");
        var engine = provider == DatabaseProvider.Sqlite ? SqliteDataSource.Engine : PostgreSqlDataSource.Engine;
        await WaitZero(engine);
        var builder = new DataSourceBuilder().WithName($"borrowed-{provider}-{stop}-{failMapping}")
            .ConfigureLimits(new DatabaseLimits { MaxConnections = 1, MaxBatchRows = batchRows, MaxBatchBytes = 4096, MaxFieldBytes = 1024 });
        if (provider == DatabaseProvider.Sqlite) builder.UseSqlite(connection);
        else builder.UsePostgreSql(connection, options => options.TlsMode = PostgreSqlTlsMode.DisableForLocalDevelopment);
        var source = builder.Build();
        var retired = 0; var stopped = 0;
        source.TestPullBoundary = boundary =>
        {
            if (boundary == HostPullBoundary.StopReturned) Interlocked.Increment(ref stopped);
        };
        source.TestRetirement = snapshot =>
        {
            Check(snapshot.Released && !snapshot.RootLive && snapshot.Controls == 0 && snapshot.CallbackEntries == 0 && snapshot.RetainedInputBytes == 0,
                "a real provider operation retires its managed bridge owners");
            Interlocked.Increment(ref retired);
        };
        var session = await source.OpenSessionAsync();
        using var cancellation = new CancellationTokenSource();
        using var releaseMapper = new ManualResetEventSlim();
        var enteredMapper = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var mappingFailure = new InvalidDataException("Borrowed native mapper fixture failure.");
        const string inputName = "owned row 🦀";
        byte[] inputBytes = [0, 1, 127, 255];
        var inputJson = new BorrowedHostPayload(42, "owned JSON 🦀");
        BorrowedHostValues? observed = null;
        var projection = Projection<BorrowedHostValues>.Create(
            [ResultField.Create("name", Codecs.String), ResultField.Create("bytes", Codecs.Bytes), ResultField.Create("json", Json)], row =>
            {
                // Read both before and after the barrier, inside one synchronous
                // materializer. A GetSpan-only pin would not protect this scope.
                var name = row.Read(0, Codecs.String);
                enteredMapper.TrySetResult();
                if (!releaseMapper.Wait(Bound)) throw new TimeoutException("The real provider mapper barrier was not released.");
                var result = new BorrowedHostValues(name, row.Read(1, Codecs.Bytes), row.Read(2, Json));
                observed = result;
                if (failMapping) throw mappingFailure;
                return result;
            });
        var sql = provider == DatabaseProvider.Sqlite
            ? "SELECT CAST(@name AS TEXT) AS name, CAST(@bytes AS BLOB) AS bytes, CAST(@json AS TEXT) AS json"
            : "SELECT CAST(@name AS TEXT) AS name, CAST(@bytes AS BYTEA) AS bytes, CAST(@json AS JSONB) AS json";
        var command = SqlCommand.Create(sql, new SqlParameters().Add("name", inputName, Codecs.String)
            .Add("bytes", inputBytes, Codecs.Bytes).Add("json", inputJson, Json));
        var reader = session.StreamAsync(command, projection, cancellation.Token).GetAsyncEnumerator();
        var move = Task.Run(() => reader.MoveNextAsync().AsTask());
        Task? disposing = null, closingSource = null, closingSession = null;
        try
        {
            var entered = await Task.WhenAny(enteredMapper.Task, move).WaitAsync(Bound);
            if (ReferenceEquals(entered, move))
            {
                // Query/conversion failures before mapping must retain their
                // original error, rather than appear as a barrier timeout.
                _ = await move;
                throw new InvalidOperationException("The result move completed without entering its synchronous mapper.");
            }
            await enteredMapper.Task;
            Console.WriteLine($"BORROWED_HOST_PHASE provider={provider} stop={stop} mapperFailure={failMapping} phase=mapper-entered");
            Check(Counts(engine)[4] == 1, "the paused public mapper owns one real native result buffer");
            var beforeClose = Volatile.Read(ref retired);
            var beforeStop = Volatile.Read(ref stopped);
            switch (stop)
            {
                case Stop.Dispose:
                    disposing = reader.DisposeAsync().AsTask();
                    Check(!disposing.IsCompleted, "DisposeAsync waits for the admitted synchronous mapper");
                    break;
                case Stop.Cancel:
                    cancellation.Cancel();
                    break;
                case Stop.SourceClose:
                    closingSource = source.DisposeAsync().AsTask();
                    break;
                case Stop.SessionClose:
                    closingSession = session.DisposeAsync().AsTask();
                    break;
            }
            // Pull stop is a synchronous channel control. Its returned boundary
            // proves the stop reached native code while this mapper holds its
            // span. Parent close retains its separate generic close retirement.
            if (stop is Stop.Dispose or Stop.Cancel)
                await Until(() => Volatile.Read(ref stopped) > beforeStop,
                    "The native pull stop did not return while its result batch was held.");
            else
                await Until(() => Volatile.Read(ref retired) > beforeClose,
                    "The real parent close operation did not retire while its result batch was held.");
            Console.WriteLine($"BORROWED_HOST_PHASE provider={provider} stop={stop} mapperFailure={failMapping} phase=stop-or-close-observed");
            if (closingSource is not null)
            {
                await closingSource.WaitAsync(Bound);
                Check(source.Cleanup.LocalResourcesReleased, "source shutdown joins native safety independently of a held result buffer");
            }
            if (closingSession is not null)
            {
                await closingSession.WaitAsync(Bound);
                Check(session.Cleanup.LocalResourcesReleased, "session shutdown joins native safety independently of a held result buffer");
            }
            Check(!move.IsCompleted, "control completion cannot finish an executing synchronous mapper");
            Check(Counts(engine)[4] == 1, "the real native result buffer survives completed stop/close control while the mapper is paused");
            if (disposing is not null) Check(!disposing.IsCompleted, "concurrent enumerator disposal still joins the mapper after native stop");
            releaseMapper.Set();
            if (failMapping)
            {
                var failure = await Failure<InvalidDataException>(move);
                Check(ReferenceEquals(failure, mappingFailure), "the original mapper exception survives stop/close and cleanup");
            }
            else
            {
                Check(await move.WaitAsync(Bound), "an already admitted mapper completes its owned row after stop/close");
                Check(ReferenceEquals(reader.Current, observed), "the observed row is the public current value");
                if (stop == Stop.Cancel)
                {
                    var failure = await Failure<OperationCanceledException>(reader.MoveNextAsync().AsTask());
                    Check(failure.CancellationToken == cancellation.Token, "the next move preserves the admitted cancellation token");
                }
                else if (stop == Stop.SourceClose)
                    await Failure<ObjectDisposedException>(reader.MoveNextAsync().AsTask());
                else if (stop == Stop.SessionClose)
                {
                    var failure = await Failure<InvalidOperationException>(reader.MoveNextAsync().AsTask());
                    Check(failure.GetType() == typeof(InvalidOperationException)
                        && failure.Message == "The native operation is not legal in the current state.",
                        "parent session closure keeps native cursor InvalidState mapping at both EOF boundaries");
                }
            }
            await reader.DisposeAsync().AsTask().WaitAsync(Bound);
            if (disposing is not null) await disposing.WaitAsync(Bound);
            await session.DisposeAsync().AsTask().WaitAsync(Bound);
            await source.DisposeAsync().AsTask().WaitAsync(Bound);
            Check(session.Cleanup.LocalResourcesReleased && source.Cleanup.LocalResourcesReleased,
                "the real public session and source report local retirement");
            await WaitZero(engine);
            var materialized = observed ?? throw new InvalidOperationException("The paused mapper did not read the held native result.");
            Check(materialized.Name == inputName && materialized.Json == inputJson
                && materialized.Bytes.AsSpan().SequenceEqual(inputBytes), "string, bytes and typed JSON remain valid after every native owner retires");
            Check(!ReferenceEquals(materialized.Bytes, inputBytes) && !ReferenceEquals(materialized.Json, inputJson),
                "decoded bytes and typed JSON are independent application-owned values");
            inputBytes[1] = 99;
            Check(materialized.Bytes[1] == 1 && materialized.Name == "owned row 🦀" && materialized.Json.Label == "owned JSON 🦀",
                "retired native/input storage cannot mutate already materialized application values");
            Console.WriteLine($"BORROWED_HOST_CASE_PASS provider={provider} stop={stop} mapperFailure={failMapping}; native-buffer-held=1; final-owners=0");
        }
        finally
        {
            releaseMapper.Set();
            await reader.DisposeAsync().AsTask().WaitAsync(Bound);
            await session.DisposeAsync().AsTask().WaitAsync(Bound);
            await source.DisposeAsync().AsTask().WaitAsync(Bound);
        }
    }

    private static async Task Until(Func<bool> condition, string message)
    {
        var started = System.Diagnostics.Stopwatch.GetTimestamp();
        while (!condition())
        {
            if (System.Diagnostics.Stopwatch.GetElapsedTime(started) > Bound) throw new TimeoutException(message);
            await Task.Delay(1);
        }
    }
    private static async Task WaitZero(EngineDescriptor engine)
    {
        await Until(() => Counts(engine).All(value => value == 0), "Native borrowed batch fixture did not drain: " + string.Join(',', Counts(engine)));
        Check(true, "all real source/session/operation/cursor/buffer/handle/pull owners drain to zero");
    }
    private static unsafe ulong[] Counts(EngineDescriptor engine)
    {
        var count = (delegate* unmanaged[Cdecl]<uint, ulong>)EngineModuleLoader.ResolveExport(engine, "nw_db_diagnostic_count_v1");
        return new uint[] { 0, 1, 2, 3, 4, 5, 8 }.Select(index => count(index)).ToArray();
    }
    private static async Task<TException> Failure<TException>(Task task) where TException : Exception
    {
        try { await task.WaitAsync(Bound); }
        catch (TException error) { Check(true, "observed expected " + typeof(TException).Name); return error; }
        throw new InvalidOperationException("Expected " + typeof(TException).Name);
    }
    private static void Check(bool condition, string message)
    {
        Interlocked.Increment(ref _checks);
        if (!condition) throw new InvalidOperationException(message);
    }
}

internal sealed record BorrowedHostValues(string Name, byte[] Bytes, BorrowedHostPayload Json);
internal sealed record BorrowedHostPayload(int Value, string Label);
[JsonSerializable(typeof(BorrowedHostPayload))]
internal partial class BorrowedHostJson : JsonSerializerContext;
