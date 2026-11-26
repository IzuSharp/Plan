using Microsoft.Extensions.DependencyInjection;
using System.Runtime.CompilerServices;
using Korda.Data;
using Korda.Database;
using Korda.Database.Internal;
using Korda.Database.Sqlite;
using Korda.Database.PostgreSql;
using Korda.Interop;
using Korda.Interop.Async;
using Korda.Interop.Abi;
using Korda.Query.Internal;
using System.Buffers.Binary;
using System.Buffers;
using System.Runtime.InteropServices;
using NativeBuffer = Korda.Database.NativeBuffer;

if (await SnapshotProbe.RunIfRequested(args)) return;
if (await FetchProbe.RunIfRequested(args)) return;
if (await TransactionDefaultProbe.RunIfRequested(args)) return;
Console.WriteLine("snapshot parser oracle inputs=" + SnapshotProbe.Verify());
BatchResultTests.VerifyRecord();
try { await Suite.Run(); } catch (DatabaseException failure) { Console.Error.WriteLine($"kind={failure.Kind} provider={failure.ProviderCode} correlation={failure.CorrelationId}"); throw; }

internal static class Suite
{
    private static int _assertions, _retirements;
    private static void Check(bool value, string message) { Interlocked.Increment(ref _assertions); if (!value) throw new InvalidOperationException(message); }
    private static async Task<T> Throws<T>(Func<Task> action) where T : Exception
    { try { await action(); } catch (T exception) { Interlocked.Increment(ref _assertions); return exception; } throw new InvalidOperationException("Expected " + typeof(T).Name); }
    internal static async Task Run()
    {
        var pg = Environment.GetEnvironmentVariable("NW_TEST_POSTGRES");
        if (string.IsNullOrEmpty(pg)) throw new InvalidOperationException("Set NW_TEST_POSTGRES to the isolated actual PostgreSQL18 test cluster.");
        var directory = Path.Combine(Path.GetTempPath(), "korda-b04-" + Guid.NewGuid().ToString("N")); Directory.CreateDirectory(directory);
        var path = Path.Combine(directory, "host.db");
        var sqlite = new DataSourceBuilder().UseSqlite(path).WithName("b04-sqlite").ConfigureLimits(new DatabaseLimits { MaxConnections = 2, MaxBatchRows = 3 }).Build();
        Check(!File.Exists(path), "Build must not open SQLite");
        var postgres = new DataSourceBuilder().UsePostgreSql(pg, options => options.TlsMode = PostgreSqlTlsMode.DisableForLocalDevelopment).WithName("b04-postgres").ConfigureLimits(new DatabaseLimits { MaxConnections = 2, MaxBatchRows = 3 }).Build();
        WrongModule(sqlite, postgres); WrongModule(postgres, sqlite);
        foreach (var source in new[] { sqlite, postgres })
        {
            Console.WriteLine("host provider=" + source.Provider);
            source.TestRetirement = snapshot =>
            {
                Check(snapshot.Released && !snapshot.RootLive && snapshot.Controls == 0 && snapshot.CallbackEntries == 0 && snapshot.RetainedInputBytes == 0, "managed retirement released root/control/callback/input owners");
                Check(snapshot.Start is AsyncStartOutcome.Skipped or AsyncStartOutcome.Rejected or AsyncStartOutcome.NotStarted || snapshot.NativeQuiet, "accepted native operation is quiet before managed result returns");
                Interlocked.Increment(ref _retirements);
            };
            Check(source.Capabilities.Supports("db.sql.expert.v1"), "actual raw SQL capability");
            Check(!source.Capabilities.Supports("unknown"), "unknown capability false");
            using var canceled = new CancellationTokenSource(); canceled.Cancel();
            var canceledOpen = source.OpenSessionAsync(canceled.Token);
            Check(canceledOpen.IsCanceled, "already canceled Open Task");
            var ce = await Throws<OperationCanceledException>(() => canceledOpen); Check(ce.CancellationToken == canceled.Token, "token identity");
            await using (var probe = await source.Start(() => NativeHost.Open(source), operation => TakeProbe(source, operation))) { Check(probe.Cleanup.Status == CleanupStatus.NotStarted, "adopted session independent from operation retirement"); }
            var session = await source.OpenSessionAsync();
            await using (var occupied = await source.OpenSessionAsync())
            {
                using var pendingCancel = new CancellationTokenSource();
                var pending = source.OpenSessionAsync(pendingCancel.Token);
                await Task.Delay(20); Check(!pending.IsCompleted, "physical capacity bounds accepted admission");
                pendingCancel.Cancel(); var canceledAdmission = await Throws<OperationCanceledException>(() => pending);
                Check(canceledAdmission.CancellationToken == pendingCancel.Token, "accepted cancel token identity");
            }
            var table = "b04_" + Guid.NewGuid().ToString("N");
            await session.ExecuteAsync(SqlCommand.Create("CREATE TABLE " + table + " (id BIGINT PRIMARY KEY, name TEXT NOT NULL)", kind: SqlCommandKind.Mutation));
            for (var i = 1L; i <= 7; i++)
            {
                var command = SqlCommand.Create("INSERT INTO " + table + " (id,name) VALUES (@id,@name)", new SqlParameters().Add("id", i, Codecs.Int64).Add("name", "row " + i, Codecs.String), SqlCommandKind.Mutation);
                Check(await session.ExecuteAsync(command) == 1, "affected count");
            }
            Check(await session.ScalarAsync(SqlCommand.Create("SELECT COUNT(*) FROM " + table), Codecs.Int64) == 7, "exact scalar count");
            var nullable = Codecs.Nullable(Codecs.Int64);
            Check(await session.ScalarAsync(SqlCommand.Create("SELECT CAST(@empty AS BIGINT)", new SqlParameters().Add("empty", (long?)null, nullable)), nullable) is null, "typed null remains a null canonical wire cell");
            var repeated = SqlCommand.Parameterized(FormattableStringFactory.Create("SELECT CAST({0} AS BIGINT) + CAST({0} AS BIGINT)", 3L));
            Check(await session.ScalarAsync(repeated, Codecs.Int64) == 6, "repeated interpolated argument is bound twice without SQL interpolation");
            var quotedHole = SqlCommand.Parameterized(FormattableStringFactory.Create("SELECT {0}, '{0}'", 3L));
            await Throws<ArgumentException>(() => session.ScalarAsync(quotedHole, Codecs.Int64));
            var projection = Projection<Row>.Create([ResultField.Create("id", Codecs.Int64), ResultField.Create("name", Codecs.String)], row => new(row.Read(0, Codecs.Int64), row.Read(1, Codecs.String)));
            await NativeBatches(source, session, table, projection);
            await ReusablePullBatches(source, session, table, projection);
            await PrivateFetchOwnerFailures(source, session, table, projection);
            await PrivatePullStopBeforeReservation(source, session, table, projection);
            var rows = await session.QueryAsync(SqlCommand.Create("SELECT id,name FROM " + table + " ORDER BY id"), projection);
            Check(rows.Count == 7 && rows[6].Id == 7 && rows[0].Name == "row 1", "multi-batch owned materialization");
            var empty = await session.QueryAsync(SqlCommand.Create("SELECT id,name FROM " + table + " WHERE id<0"), projection); Check(empty.Count == 0, "empty canonical EOS");
            await Throws<InvalidOperationException>(() => session.ScalarAsync(SqlCommand.Create("SELECT id FROM " + table), Codecs.Int64));
            await Throws<InvalidOperationException>(() => session.ScalarAsync(SqlCommand.Create("SELECT id FROM " + table + " WHERE id<0"), Codecs.Int64));
            var shapeFailure = await Throws<DatabaseException>(() => session.QueryAsync(SqlCommand.Create("SELECT id AS wrong,name FROM " + table), projection)); Check(shapeFailure.Kind == DatabaseErrorKind.ShapeMismatch, "empty/nonempty exact shape");
            var mapper = Projection<Row>.Create([ResultField.Create("id", Codecs.Int64), ResultField.Create("name", Codecs.String)], _ => throw new MappingFailure());
            await Throws<MappingFailure>(() => session.QueryAsync(SqlCommand.Create("SELECT id,name FROM " + table), mapper));
            Check(await session.ScalarAsync(SqlCommand.Create("SELECT COUNT(*) FROM " + table), Codecs.Int64) == 7, "mapping exception drains session");
            await using (var stream = session.StreamAsync(SqlCommand.Create("SELECT id,name FROM " + table + " ORDER BY id"), projection).GetAsyncEnumerator())
            {
                Check(await stream.MoveNextAsync() && stream.Current.Id == 1, "lazy bounded stream");
                var busy = await Throws<DatabaseException>(() => session.ExecuteAsync(SqlCommand.Create("DELETE FROM " + table + " WHERE id=-1", kind: SqlCommandKind.Mutation))); Check(busy.Kind == DatabaseErrorKind.ConcurrentUse, "cursor holds session admission");
            }
            await using (var transaction = await session.BeginTransactionAsync())
            {
                await session.ExecuteAsync(SqlCommand.Create("INSERT INTO " + table + " VALUES (8,'outer')", kind: SqlCommandKind.Mutation));
                await using (var savepoint = await transaction.CreateSavepointAsync())
                { await session.ExecuteAsync(SqlCommand.Create("INSERT INTO " + table + " VALUES (9,'savepoint')", kind: SqlCommandKind.Mutation)); await savepoint.RollbackAsync(); await savepoint.ReleaseAsync(); }
                await transaction.CommitAsync(); Check(transaction.Outcome == TransactionOutcome.Committed, "confirmed commit");
            }
            Check(await session.ScalarAsync(SqlCommand.Create("SELECT COUNT(*) FROM " + table), Codecs.Int64) == 8, "savepoint rollback effect");
            await using (var transaction = await session.BeginTransactionAsync())
            { await session.ExecuteAsync(SqlCommand.Create("DELETE FROM " + table, kind: SqlCommandKind.Mutation)); await transaction.RollbackAsync(); Check(transaction.Outcome == TransactionOutcome.RolledBack, "confirmed rollback"); }
            var duplicate = await Throws<DatabaseException>(() => session.ExecuteAsync(SqlCommand.Create("INSERT INTO " + table + " VALUES (1,'duplicate')", kind: SqlCommandKind.Mutation)));
            Check(duplicate.Kind == DatabaseErrorKind.Constraint && duplicate.ProviderCode is not null, "bounded provider error identity");
            source.TestAfterErrorTake = () => throw new MappingFailure();
            await Throws<MappingFailure>(() => session.ExecuteAsync(SqlCommand.Create("INSERT INTO " + table + " VALUES (1,'duplicate')", kind: SqlCommandKind.Mutation))); source.TestAfterErrorTake = null;
            foreach (var fault in new[] { AsyncBoundary.BeforeRoot, AsyncBoundary.RootAllocated, AsyncBoundary.BeforeRegister, AsyncBoundary.Registered, AsyncBoundary.BeforeStart, AsyncBoundary.BeforeTake })
            {
                source.TestBoundary = boundary => { if (boundary == fault) throw new MappingFailure(); };
                await Throws<MappingFailure>(() => source.OpenSessionAsync()); source.TestBoundary = null;
            }
            source.TestAfterOwnerTake = () => throw new MappingFailure(); await Throws<MappingFailure>(() => source.OpenSessionAsync()); source.TestAfterOwnerTake = null;
            Check(await source.CanConnectAsync(), "fault cleanup restores physical capacity");
            await Throws<TimeoutException>(() => session.ExecuteAsync(SqlCommand.Create("DELETE FROM " + table + " WHERE id=-1", kind: SqlCommandKind.Mutation, timeout: TimeSpan.Zero)));
            await session.ExecuteAsync(SqlCommand.Create("DROP TABLE " + table, kind: SqlCommandKind.Mutation));
            await session.DisposeAsync(); Check(session.Cleanup.LocalResourcesReleased, "session physical retirement");
            Check(session.Cleanup.ConnectionDisposition == ConnectionDisposition.Usable, "normal session receipt confirms pool return");
            await using (var changing = await source.OpenSessionAsync())
            {
                var sql = source.Provider == DatabaseProvider.Sqlite ? "PRAGMA user_version = 17" : "SET application_name = 'b04-session-mutating'";
                await changing.ExecuteAsync(SqlCommand.Create(sql, kind: SqlCommandKind.SessionMutating));
                Check(changing.Cleanup.LocalResourcesReleased && changing.Cleanup.ConnectionDisposition == ConnectionDisposition.Discarded, "session-mutating command physically discards connection");
                await Throws<InvalidOperationException>(() => changing.ExecuteAsync(SqlCommand.Create("DELETE FROM imaginary", kind: SqlCommandKind.Mutation)));
            }
            var orphan = await source.OpenSessionAsync();
            var close = source.CloseAsync(TimeSpan.Zero); var snapshot = await close; Check(snapshot.Status is CleanupStatus.Pending or CleanupStatus.Succeeded, "zero close observation");
            await Throws<OperationCanceledException>(() => source.CloseAsync(TimeSpan.FromSeconds(1), canceled.Token));
            await source.DisposeAsync(); Check(source.Cleanup.LocalResourcesReleased, "engine runtime retirement");
            await Throws<ObjectDisposedException>(() => orphan.ScalarAsync(SqlCommand.Create("SELECT 1"), Codecs.Int64));
            await orphan.DisposeAsync(); Check(orphan.Cleanup.LocalResourcesReleased, "child after source retirement");
            await source.DisposeAsync();
            await WaitZero(source.Provider == DatabaseProvider.Sqlite ? SqliteDataSource.Engine : PostgreSqlDataSource.Engine);
        }
        await BorrowedBatchHostTests.Run(DatabaseProvider.Sqlite, Path.Combine(directory, "borrowed.db"));
        await BorrowedBatchHostTests.Run(DatabaseProvider.PostgreSql, pg);
        await BatchResultTests.VerifyFetches(DatabaseProvider.Sqlite, Path.Combine(directory, "batch-result.db"));
        await BatchResultTests.VerifyFetches(DatabaseProvider.PostgreSql, pg);
        await BatchResultTests.VerifyParentTransactions(DatabaseProvider.Sqlite, Path.Combine(directory, "batch-parent.db"));
        await BatchResultTests.VerifyParentTransactions(DatabaseProvider.PostgreSql, pg);
        await DependencyInjection(Path.Combine(directory, "di.db"));
        await WaitZero(SqliteDataSource.Engine);
        Directory.Delete(directory, true);
        Console.WriteLine("B04 actual Linux two-provider assertions=" + _assertions + "; separately observed managed retirements=" + _retirements + "; all source/session/operation/cursor/buffer/handle/pull counters=0");
    }
    private static unsafe void WrongModule(DataSource owner, DataSource foreign)
    {
        using var lease = owner.Owner.Borrow(DatabaseOwnerKind.Source); nint output = 123; var error = BindingChecks.Error();
        var status = foreign.Binding.Calls.nw_db_session_open_create_v1(lease.Pointer, &output, &error);
        Check(status == NativeStatus.InvalidState && output == 0, "foreign creating-module owner rejects and zeros output");
    }
    private static unsafe DataSession TakeProbe(DataSource source, nint operation)
    {
        nint pointer = 123; var error = BindingChecks.Error();
        var wrong = source.Binding.Calls.nw_db_operation_take_owner_v1(operation, 2, &pointer, &error);
        Check(wrong == NativeStatus.InvalidState && pointer == 0, "wrong typed take is nonconsuming and clears output");
        var owner = NativeHost.TakeOwner(source.Binding, operation, 1, DatabaseOwnerKind.Session);
        pointer = 123; var twice = source.Binding.Calls.nw_db_operation_take_owner_v1(operation, 1, &pointer, &error);
        Check(twice == NativeStatus.InvalidState && pointer == 0, "owner transfers exactly once");
        return new(source, owner);
    }
    private static async Task NativeBatches(DataSource source, DataSession session, string table, Projection<Row> projection)
    {
        var id = source.RegisterProjection(projection);
        using var plan = SqlSubmission.Create(session, SqlCommand.Create("SELECT id,name FROM " + table + " ORDER BY id"), 3, id);
        using var cursor = await source.Start(() => NativeHost.Execute(session.Owner, plan, ReadOnlyMemory<byte>.Empty),
            operation => NativeHost.TakeOwner(source.Binding, operation, 2, DatabaseOwnerKind.Cursor));
        var close = new CloseController(source, cursor, cursor.Dispose);
        var engine = source.Provider == DatabaseProvider.Sqlite ? SqliteDataSource.Engine : PostgreSqlDataSource.Engine;
        var buffersBefore = Counts(engine)[4];
        Task<Korda.Database.NativeBuffer> Fetch(int rows) => source.Start(() => LegacyFetch(cursor, rows, source.Limits.MaxBatchBytes), operation => LegacyTakeBuffer(source.Binding, operation));
        try
        {
            using (var first = await Fetch(1))
            {
                using var batch = LegacyBatch(first, checked((int)source.Limits.MaxBatchBytes));
                var borrowed = batch.Bytes;
                Check(!System.Runtime.InteropServices.MemoryMarshal.TryGetArray(borrowed, out _),
                    "host batch exposes native storage without an intermediate managed array");
                Check(ReferenceEquals(batch.ReadOwner, first), "the native batch exposes its creating SafeHandle read owner");
                InspectNativeBatch(batch, first, engine, buffersBefore + 1, dispose: false);
                await Throws<NotSupportedException>(() => { using var pin = borrowed.Pin(); return Task.CompletedTask; });
                await Throws<InvalidOperationException>(async () => { using var blocked = await Fetch(1); });
                Check(!first.IsClosed, "the batch retains the native byte permit before disposal");
                InspectNativeBatch(batch, first, engine, buffersBefore + 1, dispose: true);
                Check(first.IsClosed && Counts(engine)[4] == buffersBefore,
                    "the last synchronous read reference releases the disposed native batch once");
                await Throws<ObjectDisposedException>(() => { _ = batch.Bytes; return Task.CompletedTask; });
                await Throws<ObjectDisposedException>(() => { _ = borrowed.Span.Length; return Task.CompletedTask; });
            }
            using var second = await Fetch(2);
            Check(BinaryPrimitives.ReadUInt32LittleEndian(second.Copy().AsSpan(56)) == 2, "native per-fetch two-row demand after prior buffer release");
        }
        finally { close.Request(); await close.JoinAsync(); }
    }
    // The frozen independent execute/fetch/take_buffer ABI remains supported.
    // These private fixtures do not reintroduce the deleted product batch path.
    private static unsafe nint LegacyFetch(DatabaseOwner cursor, int rows, long bytes)
    {
        using var lease = cursor.Borrow(DatabaseOwnerKind.Cursor); nint result = 0; var error = BindingChecks.Error();
        HostFailure.Check(cursor.Source, cursor.Source.Calls.nw_db_cursor_fetch_create_v1(lease.Pointer,
            checked((uint)rows), checked((ulong)bytes), &result, &error), error);
        return result;
    }
    private static unsafe NativeBuffer LegacyTakeBuffer(SourceBinding binding, nint operation)
    {
        nint result = 0; var error = BindingChecks.Error();
        HostFailure.Check(binding, binding.Calls.nw_db_operation_take_buffer_v1(operation, &result, &error), error);
        try { return new(binding, result); }
        catch { if (result != 0) binding.Calls.nw_db_buffer_release_v1(result); throw; }
    }
    private static LegacyBufferView LegacyBatch(NativeBuffer owner, int maximum) => new(owner, maximum);
    private sealed class LegacyBufferView : MemoryManager<byte>
    {
        private NativeBuffer? _owner;
        private readonly nint _address;
        private readonly int _length;
        internal LegacyBufferView(NativeBuffer owner, int maximum)
        {
            var retained = false;
            try
            {
                owner.DangerousAddRef(ref retained);
                owner.ViewWhileRetained(maximum, out _address, out _length);
                if (_length < 96) throw new InvalidOperationException("Incomplete legacy batch header.");
                _owner = owner;
            }
            finally { if (retained) owner.DangerousRelease(); }
        }
        internal SafeHandle ReadOwner => Volatile.Read(ref _owner) ?? throw new ObjectDisposedException(nameof(LegacyBufferView));
        internal ReadOnlyMemory<byte> Bytes { get { _ = ReadOwner; return CreateMemory(_length); } }
        public override unsafe Span<byte> GetSpan()
        {
            ObjectDisposedException.ThrowIf(ReadOwner.IsClosed, this);
            return new Span<byte>((void*)_address, _length);
        }
        public override MemoryHandle Pin(int elementIndex = 0) => throw new NotSupportedException();
        public override void Unpin() { }
        public void Dispose() => Dispose(true);
        protected override void Dispose(bool disposing) => Interlocked.Exchange(ref _owner, null)?.Dispose();
    }
    private static async Task PrivateFetchOwnerFailures(DataSource source, DataSession session, string table, Projection<Row> projection)
    {
        var id = source.RegisterProjection(projection);
        foreach (var fault in new[] { HostPullBoundary.BeforeRoot, HostPullBoundary.RootAllocated, HostPullBoundary.BeforeRegister,
            HostPullBoundary.Registered, HostPullBoundary.BeforeRequest, HostPullBoundary.RequestReturned,
            HostPullBoundary.Ready, HostPullBoundary.BeforeTake, HostPullBoundary.ResultTaken, HostPullBoundary.Published })
        {
            using var plan = SqlSubmission.Create(session, SqlCommand.Create("SELECT id,name FROM " + table + " ORDER BY id"), 3, id);
            using var cancellation = new CancellationTokenSource();
            var channel = NativeHost.CreatePull(session, plan, ReadOnlyMemory<byte>.Empty);
            var transport = new HostStreamTransport(source, channel, 3, cancellation.Token);
            var original = new MappingFailure();
            try
            {
                source.TestPullBoundary = boundary => { if (boundary == fault) throw original; };
                var failure = await Throws<MappingFailure>(async () =>
                {
                    using var batch = await transport.FetchAsync();
                });
                Check(ReferenceEquals(failure, original), "private fetch preserves constructor/setup/take failure identity");
                var snapshot = transport.PullSnapshot;
                Check(snapshot.Generation == 1 && snapshot.SetupReturned && snapshot.Published && snapshot.Consumed
                    && !snapshot.Active && !snapshot.Rooted && !snapshot.SlotReserved
                    && snapshot.CallbackEntries == 0 && snapshot.Controls == 0 && snapshot.RegistrationDrained,
                    "a failed pull publishes only after releasing its callback root, reservation and setup/control obligations");
            }
            finally
            {
                source.TestPullBoundary = null;
                var retirement = await transport.JoinAsync().WaitAsync(TimeSpan.FromSeconds(10));
                Check(retirement.NativeRetired, "private failed fetch releases channel ownership before reuse");
            }
            Check(await session.ScalarAsync(SqlCommand.Create("SELECT COUNT(*) FROM " + table), Codecs.Int64) == 7,
                "each private fetch fault compensation leaves the same real session usable");
        }
    }
    private static async Task ReusablePullBatches(DataSource source, DataSession session, string table, Projection<Row> projection)
    {
        var id = source.RegisterProjection(projection);
        using var plan = SqlSubmission.Create(session, SqlCommand.Create("SELECT id,name FROM " + table + " ORDER BY id"), 3, id);
        var engine = source.Provider == DatabaseProvider.Sqlite ? SqliteDataSource.Engine : PostgreSqlDataSource.Engine;
        var buffersBefore = Counts(engine)[4]; var sqlBefore = Diagnostic(engine, 6);
        var channel = NativeHost.CreatePull(session, plan, ReadOnlyMemory<byte>.Empty);
        var transport = new HostStreamTransport(source, channel, 3, default);
        Check(Diagnostic(engine, 6) == sqlBefore, "constructing the pull channel preserves lazy SQL side effects");
        try
        {
            var firstRequest = transport.FetchAsync();
            var batch = await firstRequest;
            var firstGeneration = batch.Generation;
            Check(PullRows(batch) == 3 && !batch.End && transport.PullSnapshot.Generation == 1,
                "the first pull opens the command and returns its demanded first batch");
            RejectConsumed(firstRequest);
            HeldPull(transport, batch, engine, buffersBefore);
            var second = await transport.FetchAsync();
            Check(ReferenceEquals(batch, second) && second.Generation > firstGeneration
                && PullRows(second) == 3 && !second.End && transport.PullSnapshot.Generation == 2,
                "the next pull reuses the same managed batch with a new native generation");
            RejectConsumed(firstRequest);
            try { using var stale = second.AcquireRead(firstGeneration); throw new InvalidOperationException("Expected stale generation rejection."); }
            catch (ObjectDisposedException) { Check(true, "a retained generation token cannot read replacement storage"); }
            second.Dispose();
            var third = await transport.FetchAsync();
            Check(ReferenceEquals(batch, third) && PullRows(third) == 1 && third.End && transport.PullSnapshot.Generation == 3,
                "the final partial batch preserves known EOF while reusing the same owner");
            third.Dispose();
            Check(Counts(engine)[4] == buffersBefore && Diagnostic(engine, 6) == sqlBefore + 1,
                "all three pulls execute one SQL and release every transferred native buffer");
        }
        finally
        {
            var retired = await transport.JoinAsync().WaitAsync(TimeSpan.FromSeconds(10));
            Check(retired.NativeRetired, "the reusable channel joins its worker tail on final close");
        }
        Console.WriteLine($"PULL_REUSE_PASS provider={source.Provider}; same owner, one-shot ValueTasks, generation rejection and held reader admission");
    }
    private static uint PullRows(ScopedStreamBatch batch)
    { using var read = batch.AcquireRead(); return BinaryPrimitives.ReadUInt32LittleEndian(read.Bytes[56..]); }
    private static void RejectConsumed(ValueTask<ScopedStreamBatch> request)
    {
        try { _ = request.GetAwaiter().GetResult(); }
        catch (InvalidOperationException) { Check(true, "a pull ValueTask is consumed exactly once and rejects a stale version"); return; }
        throw new InvalidOperationException("A consumed pull ValueTask was accepted twice.");
    }
    private static void HeldPull(HostStreamTransport transport, ScopedStreamBatch batch, EngineDescriptor engine, ulong before)
    {
        var generation = transport.PullSnapshot.Generation;
        using (var read = batch.AcquireRead())
        {
            batch.Dispose(); batch.Dispose();
            Check(Counts(engine)[4] == before + 1 && !batch.CanAttach && !batch.IsActive,
                "an admitted reader keeps the exact native storage after logical batch disposal");
            try { _ = transport.FetchAsync(); throw new InvalidOperationException("Expected busy held batch rejection."); }
            catch (DatabaseException error) when (error.Kind == DatabaseErrorKind.ConcurrentUse)
            { Check(transport.PullSnapshot.Generation == generation, "held storage rejects another pull without consuming a generation"); }
            Check(BinaryPrimitives.ReadUInt32LittleEndian(read.Bytes[56..]) == 3,
                "the held native batch remains readable throughout the rejected next request");
        }
        Check(Counts(engine)[4] == before && batch.CanAttach, "the final reader releases the native permit and permits another generation");
    }
    private static async Task PrivatePullStopBeforeReservation(DataSource source, DataSession session, string table, Projection<Row> projection)
    {
        var id = source.RegisterProjection(projection);
        foreach (var fault in new[] { HostPullBoundary.BeforeRoot, HostPullBoundary.RootAllocated })
        {
            using var plan = SqlSubmission.Create(session, SqlCommand.Create("SELECT id,name FROM " + table + " ORDER BY id"), 3, id);
            var transport = new HostStreamTransport(source, NativeHost.CreatePull(session, plan, ReadOnlyMemory<byte>.Empty), 3, default);
            var original = new MappingFailure(); var published = 0;
            source.TestPullBoundary = boundary =>
            {
                if (boundary != fault) return;
                Task.Run(transport.RequestStop).Wait(TimeSpan.FromSeconds(10));
                if (!transport.PullSnapshot.StopObserved) throw new TimeoutException("Concurrent native stop did not return before setup failure.");
                throw original;
            };
            source.TestPullSnapshot = snapshot =>
            {
                if (snapshot.Published && !snapshot.Consumed) Interlocked.Increment(ref published);
            };
            try
            {
                var failure = await Throws<MappingFailure>(async () => { using var batch = await transport.FetchAsync(); });
                var snapshot = transport.PullSnapshot;
                Check(ReferenceEquals(failure, original) && Volatile.Read(ref published) == 1
                    && snapshot.Published && snapshot.Consumed && snapshot.StopObserved && !snapshot.Rooted && !snapshot.SlotReserved
                    && snapshot.CallbackEntries == 0 && snapshot.Controls == 0 && snapshot.RegistrationDrained,
                    "concurrent pre-reservation stop and setup failure publish once after releasing every bridge owner");
            }
            finally
            {
                source.TestPullBoundary = null; source.TestPullSnapshot = null;
                var retired = await transport.JoinAsync().WaitAsync(TimeSpan.FromSeconds(10));
                Check(retired.NativeRetired, "a stopped pre-reservation channel completes normal close");
            }
        }
        Check(await session.ScalarAsync(SqlCommand.Create("SELECT COUNT(*) FROM " + table), Codecs.Int64) == 7,
            "pre-reservation concurrent stop leaves the same real session usable");
    }
    private static void InspectNativeBatch(LegacyBufferView batch, Korda.Database.NativeBuffer owner,
        EngineDescriptor engine, ulong expectedBuffers, bool dispose)
    {
        var retained = false;
        try
        {
            owner.DangerousAddRef(ref retained);
            var span = batch.Bytes.Span;
            Check(BinaryPrimitives.ReadUInt32LittleEndian(span[56..]) == 1, "native per-fetch one-row demand within a complete read scope");
            if (dispose)
            {
                batch.Dispose(); batch.Dispose();
                Check(Counts(engine)[4] == expectedBuffers, "disposing a batch cannot free storage retained by an active read scope");
                Check(BinaryPrimitives.ReadUInt32LittleEndian(span[56..]) == 1, "an already acquired span remains valid until its read scope ends");
            }
        }
        finally { if (retained) owner.DangerousRelease(); }
    }
    private static async Task DependencyInjection(string path)
    {
        var services = new ServiceCollection(); var configurations = 0;
        services.AddKordaDatabase(builder => { configurations++; builder.UseSqlite(path); });
        services.AddKeyedKordaDatabase("audit", builder => builder.UseSqlite(path));
        Check(configurations == 0, "DI configuration waits for owner construction");
        await Throws<InvalidOperationException>(() => { services.AddKordaDatabase(_ => { }); return Task.CompletedTask; });
        await Throws<InvalidOperationException>(() => { services.AddKeyedKordaDatabase("audit", _ => { }); return Task.CompletedTask; });
        DataSource first, keyed;
        await using (var provider = services.BuildServiceProvider())
        {
            first = provider.GetRequiredService<DataSource>(); keyed = provider.GetRequiredKeyedService<DataSource>("audit");
            Check(ReferenceEquals(first, provider.GetRequiredService<DataSource>()) && configurations == 1, "DI singleton config exactly once");
            Check(!ReferenceEquals(first, keyed) && keyed.Name == "audit", "keyed sources have independent ownership");
            Check(provider.GetService<DataSession>() is null, "no implicitly shared session");
            Check(await first.CanConnectAsync() && await keyed.CanConnectAsync(), "DI sources open actual SQLite");
        }
        Check(first.Cleanup.LocalResourcesReleased && keyed.Cleanup.LocalResourcesReleased, "async container disposal joins native sources");
    }
    private static async Task WaitZero(EngineDescriptor engine)
    {
        for (var attempt = 0; attempt < 100; attempt++)
        {
            var counts = Counts(engine); if (counts.All(value => value == 0)) { Check(true, "all native resources retired"); return; }
            await Task.Delay(10);
        }
        throw new InvalidOperationException("Native resource leak: " + string.Join(',', Counts(engine)));
    }
    private static unsafe ulong[] Counts(EngineDescriptor engine)
    { var count = (delegate* unmanaged[Cdecl]<uint, ulong>)EngineModuleLoader.ResolveExport(engine, "nw_db_diagnostic_count_v1"); return new uint[] { 0, 1, 2, 3, 4, 5, 8 }.Select(index => count(index)).ToArray(); }
    private static unsafe ulong Diagnostic(EngineDescriptor engine, uint index)
    { var count = (delegate* unmanaged[Cdecl]<uint, ulong>)EngineModuleLoader.ResolveExport(engine, "nw_db_diagnostic_count_v1"); return count(index); }
    private sealed record Row(long Id, string Name);
    private sealed class MappingFailure : Exception;
}
