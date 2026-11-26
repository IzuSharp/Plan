using System.Buffers.Binary;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using Korda.Data;
using Korda.Database;
using Korda.Database.Internal;
using Korda.Database.PostgreSql;
using Korda.Database.Sqlite;
using Korda.Interop;
using Korda.Interop.Abi;
using Korda.Query.Internal;

internal static class BatchResultTests
{
    private static NativePullBatch _next;
    private static uint _status;
    private static int _takes, _views, _releases, _checks;
    private static nint _channel;
    private static ulong _generation;
    private static readonly string[] Exports = [
        "nw_db_cursor_pull_create_v1", "nw_db_cursor_pull_mutation_create_v1", "nw_db_cursor_pull_relation_create_v1",
        "nw_db_cursor_pull_request_v1", "nw_db_cursor_pull_take_v1", "nw_db_cursor_pull_take_error_v1",
        "nw_db_cursor_pull_check_read_v1", "nw_db_cursor_pull_stop_v1"];

    [UnmanagedCallersOnly(CallConvs = [typeof(CallConvCdecl)])]
    private static unsafe uint Take(nint channel, ulong generation, NativePullBatch* result, NwErrorInfoV1* error)
    { _takes++; _channel = channel; _generation = generation; *result = _next; return _status; }

    [UnmanagedCallersOnly(CallConvs = [typeof(CallConvCdecl)])]
    private static void Release(nint owner) => _releases++;

    [UnmanagedCallersOnly(CallConvs = [typeof(CallConvCdecl)])]
    private static unsafe uint View(nint owner, NwBytesViewV1* result, NwErrorInfoV1* error)
    { _views++; return NativeStatus.ContractViolation; }

    [UnmanagedCallersOnly(CallConvs = [typeof(CallConvCdecl)])]
    private static unsafe uint CheckRead(nint owner, NwErrorInfoV1* error) => NativeStatus.Ok;
    [UnmanagedCallersOnly(CallConvs = [typeof(CallConvCdecl)])]
    private static uint Stop(nint owner) => NativeStatus.Ok;
    [UnmanagedCallersOnly(CallConvs = [typeof(CallConvCdecl)])]
    private static unsafe uint Create(nint session, nint plan, NwBytesViewV1 values, nint* owner, NwErrorInfoV1* error) => NativeStatus.InvalidState;
    [UnmanagedCallersOnly(CallConvs = [typeof(CallConvCdecl)])]
    private static unsafe uint CreateMutation(nint session, nint model, uint kind, NwBytesViewV1 values, nint* owner, NwErrorInfoV1* error) => NativeStatus.InvalidState;
    [UnmanagedCallersOnly(CallConvs = [typeof(CallConvCdecl)])]
    private static unsafe uint CreateRelation(nint session, nint relation, NwBytesViewV1 values, uint kind, nint* owner, NwErrorInfoV1* error) => NativeStatus.InvalidState;
    [UnmanagedCallersOnly(CallConvs = [typeof(CallConvCdecl)])]
    private static unsafe uint Request(nint channel, ulong generation, uint rows, ulong bytes, NativePullCallbacks* callbacks, NwErrorInfoV1* error) => NativeStatus.InvalidState;
    [UnmanagedCallersOnly(CallConvs = [typeof(CallConvCdecl)])]
    private static unsafe uint TakeError(nint channel, ulong generation, nint* owner, NwErrorInfoV1* error)
    { *owner = 0; return NativeStatus.InvalidState; }

    private static unsafe nint Resolve(string symbol) => symbol switch
    {
        "nw_db_cursor_pull_create_v1" => (nint)(delegate* unmanaged[Cdecl]<nint, nint, NwBytesViewV1, nint*, NwErrorInfoV1*, uint>)&Create,
        "nw_db_cursor_pull_mutation_create_v1" => (nint)(delegate* unmanaged[Cdecl]<nint, nint, uint, NwBytesViewV1, nint*, NwErrorInfoV1*, uint>)&CreateMutation,
        "nw_db_cursor_pull_relation_create_v1" => (nint)(delegate* unmanaged[Cdecl]<nint, nint, NwBytesViewV1, uint, nint*, NwErrorInfoV1*, uint>)&CreateRelation,
        "nw_db_cursor_pull_request_v1" => (nint)(delegate* unmanaged[Cdecl]<nint, ulong, uint, ulong, NativePullCallbacks*, NwErrorInfoV1*, uint>)&Request,
        "nw_db_cursor_pull_take_v1" => (nint)(delegate* unmanaged[Cdecl]<nint, ulong, NativePullBatch*, NwErrorInfoV1*, uint>)&Take,
        "nw_db_cursor_pull_take_error_v1" => (nint)(delegate* unmanaged[Cdecl]<nint, ulong, nint*, NwErrorInfoV1*, uint>)&TakeError,
        "nw_db_cursor_pull_check_read_v1" => (nint)(delegate* unmanaged[Cdecl]<nint, NwErrorInfoV1*, uint>)&CheckRead,
        "nw_db_cursor_pull_stop_v1" => (nint)(delegate* unmanaged[Cdecl]<nint, uint>)&Stop,
        _ => 0
    };

    internal static unsafe void VerifyRecord()
    {
        NativePullBatch layout = default;
        Check(sizeof(NativePullBatch) == 32 && (byte*)&layout.Owner - (byte*)&layout == 0
            && (byte*)&layout.Bytes - (byte*)&layout == 8 && (byte*)&layout.KnownEnd - (byte*)&layout == 24
            && (byte*)&layout.Reserved - (byte*)&layout == 28, "C# pull result x64 layout differs from the additive C record");
        NativePullCallbacks callbacks = default;
        Check(sizeof(NativePullCallbacks) == 24 && (byte*)&callbacks.StructSize - (byte*)&callbacks == 0
            && (byte*)&callbacks.Reserved - (byte*)&callbacks == 4 && (byte*)&callbacks.Context - (byte*)&callbacks == 8
            && (byte*)&callbacks.Ready - (byte*)&callbacks == 16, "C# pull callback x64 layout differs from the additive C record");
        var calls = new NativeCalls("pull-result-test", symbol => symbol switch
        {
            "nw_db_buffer_release_v1" => (nint)(delegate* unmanaged[Cdecl]<nint, void>)&Release,
            "nw_db_buffer_view_v1" => (nint)(delegate* unmanaged[Cdecl]<nint, NwBytesViewV1*, NwErrorInfoV1*, uint>)&View,
            _ => 0
        });
        var binding = new SourceBinding(calls, 2) { Pulls = new(Resolve) };
        binding.Pulls.Require();
        byte* bytes = stackalloc byte[96]; new Span<byte>(bytes, 96).Clear();
        BinaryPrimitives.WriteUInt32LittleEndian(new Span<byte>(bytes + 56, 4), 1);
        foreach (var end in new uint[] { 0, 1 })
        {
            Reset(bytes); _next.KnownEnd = end;
            var batch = new ScopedStreamBatch(&Release, binding);
            NativeHost.TakePullBatch(binding, 19, 23, batch, 96);
            var read = batch.AcquireRead();
            Check(read.Bytes.Length == 96 && batch.End == (end == 1), "The pull result lost its borrowed view or known EOF");
            batch.Dispose(); batch.Dispose();
            Check(_takes == 1 && _channel == 19 && _generation == 23 && _views == 0 && _releases == 0,
                "A pull uses one generation-specific take, no buffer_view and retains bytes for an admitted reader");
            Check(BinaryPrimitives.ReadUInt32LittleEndian(read.Bytes[56..]) == 1, "The admitted native span remains valid after disposal");
            read.Dispose(); read.Dispose(); batch.Close();
            Check(_releases == 1, "The final reader releases the transferred native owner exactly once");
        }
        foreach (var fault in new[] { "null-view", "oversized", "short-header", "end-flag", "reserved", "failed-owner" })
        {
            Reset(bytes);
            switch (fault)
            {
                case "null-view": _next.Bytes.Data = null; break;
                case "oversized": _next.Bytes.Length = 97; break;
                case "short-header": _next.Bytes.Length = 95; break;
                case "end-flag": _next.KnownEnd = 2; break;
                case "reserved": _next.Reserved = 1; break;
                case "failed-owner": _status = NativeStatus.InvalidState; break;
            }
            var batch = new ScopedStreamBatch(&Release, binding);
            if (fault == "failed-owner") Reject<InvalidOperationException>(() => NativeHost.TakePullBatch(binding, 19, 23, batch, 96));
            else Reject<DatabaseException>(() => NativeHost.TakePullBatch(binding, 19, 23, batch, 96));
            Check(_takes == 1 && _views == 0 && _releases == 1 && batch.CanAttach,
                "Malformed pull result did not compensate its owned reference: " + fault);
            batch.Close(); Check(_releases == 1, "A rejected result must not transfer ownership into the reusable batch");
        }
        Reset(bytes); _next.Owner = 0;
        var empty = new ScopedStreamBatch(&Release, binding);
        Reject<InvalidOperationException>(() => NativeHost.TakePullBatch(binding, 19, 23, empty, 96));
        empty.Close(); Check(_releases == 0, "A null output must not be released as an owned reference");
        Reset(bytes);
        var occupied = new ScopedStreamBatch(&Release, binding);
        NativeHost.TakePullBatch(binding, 19, 23, occupied, 96);
        Reject<InvalidOperationException>(() => NativeHost.TakePullBatch(binding, 19, 24, occupied, 96));
        Check(_takes == 2 && _releases == 1 && occupied.IsActive,
            "Failed attachment releases only the rejected result and preserves the preceding active generation");
        occupied.Close(); Check(_releases == 2, "Both independently transferred native references release once");
        foreach (var missing in Exports)
        {
            binding.Pulls = new(symbol => symbol == missing ? 0 : Resolve(symbol));
            Reject<NotSupportedException>(() => binding.Pulls.Require());
        }
        binding.Pulls = new(_ => 0);
        Reject<NotSupportedException>(() => binding.Pulls.Require());
        Console.WriteLine($"PULL_RESULT_RECORD_PASS assertions={_checks}; x64 layouts, generation-specific take, held reads, malformed ownership and every missing export");
    }

    private static unsafe void Reset(byte* bytes)
    {
        _next = new() { Owner = 17, Bytes = new() { Data = bytes, Length = 96 } };
        _status = NativeStatus.Ok; _takes = _views = _releases = 0; _channel = 0; _generation = 0;
    }

    internal static async Task VerifyFetches(DatabaseProvider provider, string connection)
    {
        var beforeChecks = _checks;
        var builder = new DataSourceBuilder().ConfigureLimits(new DatabaseLimits { MaxConnections = 1, MaxBatchRows = 32, MaxBatchBytes = 65536 });
        if (provider == DatabaseProvider.Sqlite) builder.UseSqlite(connection);
        else builder.UsePostgreSql(connection, options => options.TlsMode = PostgreSqlTlsMode.DisableForLocalDevelopment);
        await using var source = builder.Build();
        await using var session = await source.OpenSessionAsync();
        var retirements = 0; var requests = 0; var takes = 0; var publications = 0;
        ulong lastGeneration = 0;
        source.TestRetirement = snapshot =>
        {
            Check(snapshot.Released && snapshot.NativeQuiet, "A counted query operation returned before native retirement");
            Interlocked.Increment(ref retirements);
        };
        source.TestPullBoundary = boundary =>
        {
            if (boundary == HostPullBoundary.RequestReturned) Interlocked.Increment(ref requests);
            if (boundary == HostPullBoundary.ResultTaken) Interlocked.Increment(ref takes);
        };
        source.TestPullSnapshot = snapshot =>
        {
            if (!snapshot.Published || snapshot.Consumed) return; // Stop may also report the completed generation.
            Check(snapshot.Active && snapshot.SetupReturned && snapshot.Accepted && snapshot.Ready && snapshot.ResultTaken
                && !snapshot.Rooted && !snapshot.SlotReserved && snapshot.Controls == 0 && snapshot.CallbackEntries == 0
                && snapshot.RegistrationDrained,
                "A public pull must drain setup, registration, callback and control obligations before publishing its taken batch");
            Check(snapshot.Generation == lastGeneration + 1, "A public stream publishes each sequential pull generation once");
            lastGeneration = snapshot.Generation;
            Interlocked.Increment(ref publications);
        };
        var projection = Projection<Item>.Create([ResultField.Create("id", Codecs.Int64)], row => new(row.Read(0, Codecs.Int64)));
        foreach (var count in new[] { 0, 1, 32, 64, 100, 1000 })
        {
            var command = SqlCommand.Create("WITH RECURSIVE items(id) AS (SELECT CAST(1 AS BIGINT) WHERE @count > 0 UNION ALL SELECT id + 1 FROM items WHERE id < @count) SELECT id FROM items ORDER BY id",
                new SqlParameters().Add("count", (long)count, Codecs.Int64));
            var before = Volatile.Read(ref retirements);
            var requestsBefore = Volatile.Read(ref requests); var takesBefore = Volatile.Read(ref takes);
            var publishedBefore = Volatile.Read(ref publications); var sqlBefore = SqlExecutions(provider);
            lastGeneration = 0; var rows = 0; long sum = 0;
            await foreach (var item in session.StreamAsync(command, projection))
            {
                rows++; sum += item.Id;
                Check(Volatile.Read(ref retirements) == before, "Opening and consuming pull batches creates no generic operation retirement");
            }
            var expectedFetches = count / 32 + 1;
            Check(rows == count && sum == (long)count * (count + 1) / 2, "The public batch stream changed its business result");
            Check(Volatile.Read(ref requests) - requestsBefore == expectedFetches
                && Volatile.Read(ref takes) - takesBefore == expectedFetches
                && Volatile.Read(ref publications) - publishedBefore == expectedFetches,
                "The public stream uses exactly one request, take and publication per required batch; known EOF must not fetch again");
            var finalCloses = Volatile.Read(ref retirements) - before;
            // Native snapshot reports local safety only after both the channel
            // worker fence and cursor completion are quiet. Stop can reach that
            // state before CloseController observes it, requiring no operation;
            // otherwise one final generic close joins those same obligations.
            Check(finalCloses is 0 or 1,
                "A public stream needs at most one final generic close; observed=" + finalCloses);
            Check(SqlExecutions(provider) - sqlBefore == 1, "The complete public stream executes its SQL exactly once");
            Console.WriteLine($"PULL_RESULT_FETCH_PASS provider={provider} rows={count} requests={expectedFetches} takes={expectedFetches} publications={expectedFetches} retiredOperations={Volatile.Read(ref retirements) - before} sqlExecutions=1");
        }
        Console.WriteLine($"PULL_RESULT_FETCH_PASS provider={provider} assertions={_checks - beforeChecks}; public entry, single SQL execution, partial EOF and exact row boundaries");
    }

    private static unsafe ulong SqlExecutions(DatabaseProvider provider)
    {
        var engine = provider == DatabaseProvider.Sqlite ? SqliteDataSource.Engine : PostgreSqlDataSource.Engine;
        var count = (delegate* unmanaged[Cdecl]<uint, ulong>)EngineModuleLoader.ResolveExport(engine, "nw_db_diagnostic_count_v1");
        return count(6);
    }

    internal static async Task VerifyParentTransactions(DatabaseProvider provider, string connection)
    {
        var beforeChecks = _checks;
        foreach (var batchRows in new[] { 1, 2 })
        {
            var builder = new DataSourceBuilder().ConfigureLimits(new DatabaseLimits { MaxConnections = 1, MaxBatchRows = batchRows });
            if (provider == DatabaseProvider.Sqlite) builder.UseSqlite(connection);
            else builder.UsePostgreSql(connection, options => options.TlsMode = PostgreSqlTlsMode.DisableForLocalDevelopment);
            await using var source = builder.Build();
            await using var session = await source.OpenSessionAsync();
            foreach (var control in new[] { "commit", "rollback", "dispose" })
            {
                await using var transaction = await session.BeginTransactionAsync();
                var projection = Projection<Item>.Create([ResultField.Create("id", Codecs.Int64)], row => new(row.Read(0, Codecs.Int64)));
                await using var reader = session.StreamAsync(SqlCommand.Create("SELECT CAST(1 AS BIGINT) AS id"), projection).GetAsyncEnumerator();
                Check(await reader.MoveNextAsync() && reader.Current.Id == 1, "The active transaction delivered its row");
                Task? closing = null;
                if (control == "dispose")
                {
                    closing = transaction.DisposeAsync().AsTask();
                    Check(!closing.IsCompleted, "Transaction close waits for the admitted cursor's command gate");
                }
                else if (control == "commit")
                {
                    var failure = await Failure<DatabaseException>(transaction.CommitAsync());
                    Check(failure.Kind == DatabaseErrorKind.ConcurrentUse && transaction.State == TransactionState.Active,
                        "Commit while a cursor owns the gate rejects without closing that transaction");
                }
                else
                {
                    var failure = await Failure<DatabaseCleanupException>(transaction.RollbackAsync());
                    Check(failure.Data["Korda.Database.Primary.v1"] is DatabaseException { Kind: DatabaseErrorKind.ConcurrentUse }
                        && transaction.State == TransactionState.Active,
                        "Busy rollback retains its cleanup wrapper and original concurrent-use diagnostic");
                }
                Check(!await reader.MoveNextAsync(), "An existing cursor may reach EOF while transaction close waits or control admission was rejected");
                await reader.DisposeAsync();
                if (closing is not null) await closing.WaitAsync(TimeSpan.FromSeconds(10));
                else await transaction.RollbackAsync();
                await transaction.DisposeAsync();
                Check(transaction.Outcome == TransactionOutcome.RolledBack && transaction.Cleanup.LocalResourcesReleased,
                    "The parent transaction retires after the cursor, with confirmed rollback");
                Check(await session.ScalarAsync(SqlCommand.Create("SELECT CAST(7 AS BIGINT) AS id"), Codecs.Int64) == 7,
                    "The same physical session is reusable after cursor and transaction retirement");
                Console.WriteLine($"BATCH_RESULT_PARENT_PASS provider={provider} batchRows={batchRows} control={control}; cursor completed and transaction retired");
            }
        }
        Console.WriteLine($"BATCH_RESULT_PARENT_PASS provider={provider} assertions={_checks - beforeChecks}; transaction close/control preserves unknown and known EOF behavior");
    }

    private static async Task<T> Failure<T>(Task task) where T : Exception
    {
        try { await task.WaitAsync(TimeSpan.FromSeconds(10)); }
        catch (T failure) { Check(true, "Observed expected " + typeof(T).Name); return failure; }
        throw new InvalidOperationException("Expected " + typeof(T).Name);
    }

    private static void Check(bool value, string message)
    { Interlocked.Increment(ref _checks); if (!value) throw new InvalidOperationException(message); }
    private static void Reject<T>(Action action) where T : Exception
    { try { action(); } catch (T) { _checks++; return; } throw new InvalidOperationException("Expected " + typeof(T).Name); }
    private sealed record Item(long Id);
}
