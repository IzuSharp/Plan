using System.Runtime.InteropServices;
using System.Runtime.CompilerServices;
using Microsoft.Win32.SafeHandles;
using Korda.Data;
using Korda.Database.Internal;

// Test-only ABI bridge. Blocking harness entrypoints run on test workers while
// real B02/B03 and B06 futures execute on the explicitly created test runtime.
// This is not the B04 callback host, released operation ABI, or package loader.
internal sealed class NativeFixtureTransport : IStreamTransport
{
    private readonly FixtureHandle _handle;
    private readonly CancellationToken _token;
    private readonly object _gate = new();
    private Task<StreamRetirement>? _join;
    private ulong[]? _final;
    private int _calls;
    internal int ActiveCalls => Volatile.Read(ref _calls);
    internal int Fetches { get; private set; }
    internal int DuplicateTakeRejections { get; private set; }
    private NativeFixtureTransport(FixtureHandle handle, CancellationToken token) { _handle = handle; _token = token; }
    internal static Task<NativeFixtureTransport> OpenAsync(uint provider, uint scenario, byte[] projection, int maxRows, int maxBytes, CancellationToken token)
        => Task.Run(() =>
        {
            token.ThrowIfCancellationRequested();
            var handle = new FixtureHandle();
            try
            {
                uint status; nint pointer;
                unsafe { fixed (byte* bytes = projection) status = Native.Open(provider, scenario, bytes, (nuint)projection.Length, (nuint)maxRows, (nuint)maxBytes, out pointer); }
                handle.Initialize(pointer);
                Throw(status, token);
                return new NativeFixtureTransport(handle, token);
            }
            catch { handle.Dispose(); throw; }
        }, CancellationToken.None);
    public ValueTask<ScopedStreamBatch> FetchAsync() => new(Run<ScopedStreamBatch>(() =>
    {
        Fetches++;
        Throw(Native.Fetch(_handle), _token);
        Throw(Native.Take(_handle, out var pointer), _token);
        var owner = new BatchHandle(); owner.Initialize(pointer);
        try
        {
            var duplicate = Native.Take(_handle, out var forbidden);
            if (duplicate != 1 || forbidden != 0) throw new InvalidOperationException("Native transfer was not once-only.");
            DuplicateTakeRejections++;
            return new NativeBatch(owner).Batch;
        }
        catch { owner.Dispose(); throw; }
    }));
    public void RequestStop() { lock (_gate) { if (!_handle.IsClosed) Native.Stop(_handle); } }
    public Task<StreamRetirement> JoinAsync() { lock (_gate) return _join ??= JoinCoreAsync(); }
    private async Task<StreamRetirement> JoinCoreAsync()
    {
        await Run(() => { Throw(Native.Join(_handle), _token); return 0; }).ConfigureAwait(false);
        lock (_gate)
        {
            _final = ReadStats();
            _handle.Dispose();
            return new(_final[8] != 0, _final[9] != 0, checked((long)_final[7]));
        }
    }
    internal ulong[] Stats() { lock (_gate) return _final?.ToArray() ?? ReadStats(); }
    private unsafe ulong[] ReadStats()
    {
        var values = new ulong[20];
        fixed (ulong* output = values) Throw(Native.Stats(_handle, output), _token);
        return values;
    }
    private Task<T> Run<T>(Func<T> work)
    {
        Interlocked.Increment(ref _calls);
        return Task.Run(() => { try { return work(); } finally { Interlocked.Decrement(ref _calls); } });
    }
    internal static void Throw(uint status, CancellationToken token = default)
    {
        if (status == 0) return;
        throw status switch
        {
            4 => new OperationCanceledException("The native provider confirmed stream stop.", token),
            2 => new DatabaseException("The result shape differs from its exact projection.", DatabaseErrorKind.ShapeMismatch),
            3 => new DatabaseException("LargeValueRequiresStreaming: the inline field or row cannot fit.", DatabaseErrorKind.ResourceLimit, "LargeValueRequiresStreaming"),
            6 => new DatabaseException("Native stream capacity is exhausted.", DatabaseErrorKind.ResourceLimit),
            7 => new DatabaseException("Native cleanup is pending.", DatabaseErrorKind.InvalidState, "CleanupPending"),
            9 => new DatabaseException("A scalar conversion failed.", DatabaseErrorKind.Conversion),
            1 => new DatabaseException("Native stream operation state is invalid.", DatabaseErrorKind.InvalidState),
            _ => new DatabaseException("Native provider fixture operation failed: " + status, DatabaseErrorKind.Provider),
        };
    }
}
// The retained native fixture ABI exposes a copy operation, not a borrowed
// view. Copy directly into test-owned native storage and retain the original
// byte permit until scoped release. This fixture cost is not product timing.
internal sealed class NativeBatch
{
    internal ScopedStreamBatch Batch { get; }
    internal static long LiveBytes;
    internal static long PeakBytes;
    internal static long CopiedBytes;
    internal unsafe NativeBatch(BatchHandle handle)
    {
        ulong* info = stackalloc ulong[3]; Native.BatchInfo(handle, info);
        if (info[0] > DbWire.MaxEncodedBytes) throw new InvalidOperationException("Fixture returned an oversized batch.");
        var length = checked((int)info[0]);
        var bytes = (byte*)NativeMemory.Alloc((nuint)Math.Max(1, length));
        if (bytes == null) throw new OutOfMemoryException();
        GCHandle root = default;
        try
        {
            NativeFixtureTransport.Throw(Native.BatchCopy(handle, bytes, (nuint)length));
            root = GCHandle.Alloc(new Storage(handle, (nint)bytes, length));
            Batch = new(&Release, typeof(NativeBatch));
            Batch.Attach(GCHandle.ToIntPtr(root), (nint)bytes, length, info[2] != 0);
        }
        catch
        {
            if (root.IsAllocated) root.Free();
            NativeMemory.Free(bytes);
            throw;
        }
        var live = Interlocked.Add(ref LiveBytes, length);
        Interlocked.Add(ref CopiedBytes, length);
        long peak;
        do { peak = Interlocked.Read(ref PeakBytes); if (live <= peak) break; }
        while (Interlocked.CompareExchange(ref PeakBytes, live, peak) != peak);
    }
    [UnmanagedCallersOnly(CallConvs = [typeof(CallConvCdecl)])]
    private static unsafe void Release(nint owner)
    {
        var root = GCHandle.FromIntPtr(owner); var storage = (Storage)root.Target!;
        NativeMemory.Free((void*)storage.Bytes); storage.Original.Dispose(); root.Free();
        Interlocked.Add(ref LiveBytes, -storage.Length);
    }
    private sealed record Storage(BatchHandle Original, nint Bytes, int Length);
}
internal sealed class FixtureHandle : SafeHandleZeroOrMinusOneIsInvalid
{
    internal FixtureHandle() : base(true) { }
    internal void Initialize(nint value) => SetHandle(value);
    protected override bool ReleaseHandle() { Native.Free(handle); return true; }
}
internal sealed class BatchHandle : SafeHandleZeroOrMinusOneIsInvalid
{
    internal BatchHandle() : base(true) { }
    internal void Initialize(nint value) => SetHandle(value);
    protected override bool ReleaseHandle() { Native.BatchFree(handle); return true; }
}
internal static partial class Native
{
    private const string Library = "korda_streaming_fixture";
    [LibraryImport(Library, EntryPoint = "nw_stream_fixture_open")]
    internal static unsafe partial uint Open(uint provider, uint scenario, byte* projection, nuint length, nuint rows, nuint bytes, out nint output);
    [LibraryImport(Library, EntryPoint = "nw_stream_fixture_fetch")]
    internal static partial uint Fetch(FixtureHandle owner);
    [LibraryImport(Library, EntryPoint = "nw_stream_fixture_take")]
    internal static partial uint Take(FixtureHandle owner, out nint batch);
    [LibraryImport(Library, EntryPoint = "nw_stream_fixture_stop")]
    internal static partial void Stop(FixtureHandle owner);
    [LibraryImport(Library, EntryPoint = "nw_stream_fixture_join")]
    internal static partial uint Join(FixtureHandle owner);
    [LibraryImport(Library, EntryPoint = "nw_stream_fixture_stats")]
    internal static unsafe partial uint Stats(FixtureHandle owner, ulong* values);
    [LibraryImport(Library, EntryPoint = "nw_stream_fixture_batch_info")]
    internal static unsafe partial void BatchInfo(BatchHandle owner, ulong* values);
    [LibraryImport(Library, EntryPoint = "nw_stream_fixture_batch_copy")]
    internal static unsafe partial uint BatchCopy(BatchHandle owner, byte* destination, nuint capacity);
    [LibraryImport(Library, EntryPoint = "nw_stream_fixture_batch_release")]
    internal static partial void BatchFree(nint owner);
    [LibraryImport(Library, EntryPoint = "nw_stream_fixture_release")]
    internal static partial void Free(nint owner);
    [LibraryImport(Library, EntryPoint = "nw_stream_fixture_owners")]
    internal static partial nuint Owners();
}
