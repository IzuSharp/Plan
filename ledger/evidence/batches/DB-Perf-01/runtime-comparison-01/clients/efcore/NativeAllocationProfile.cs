using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json.Serialization;

// Diagnostic only. Create(false) does not read environment variables, load a
// library, construct a profiler, or allocate per-measurement state. The enabled
// path belongs in a separate process launched with the reviewed LD_PRELOAD shim;
// its timings must never be used as the ordinary performance comparison.
internal sealed class NativeAllocationProfile : IDisposable
{
    private const int SnapshotBytes = 27 * sizeof(ulong);
    private nint _module;
    private readonly SnapshotFunction _snapshot;
    private readonly string _path, _sha256;
    private NativeAllocationSnapshot _before, _after, _drained;
    private int _stage;

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    private delegate int SnapshotFunction(ref NativeAllocationSnapshot value, ulong bytes, int resetPeak);

    // This is intentionally an explicit option, not implicit activation merely
    // because another process/environment happens to define the library path.
    internal static NativeAllocationProfile? Create(bool enabled) => enabled ? new() : null;

    private NativeAllocationProfile()
    {
        if (!OperatingSystem.IsLinux() || RuntimeInformation.ProcessArchitecture != Architecture.X64)
            throw new PlatformNotSupportedException("The reviewed allocation profiler requires Linux x64 glibc.");
        if (Marshal.SizeOf<NativeAllocationSnapshot>() != SnapshotBytes)
            throw new InvalidOperationException("The allocation snapshot does not match the 27-uint64 C ABI.");
        var configured = Environment.GetEnvironmentVariable("DB_PERF_ALLOC_PROFILE_LIBRARY");
        if (string.IsNullOrWhiteSpace(configured) || !Path.IsPathFullyQualified(configured))
            throw new InvalidOperationException("Allocation profiling requires an absolute DB_PERF_ALLOC_PROFILE_LIBRARY path.");
        _path = CanonicalPath(configured);
        var preload = Environment.GetEnvironmentVariable("LD_PRELOAD");
        var declared = false;
        foreach (var entry in (preload ?? "").Split([':', ' ', '\t', '\r', '\n'], StringSplitOptions.RemoveEmptyEntries))
        {
            // The campaign uses absolute filenames. Loader search names or
            // $ORIGIN expansion are not an auditable identity for this lane.
            if (Path.IsPathFullyQualified(entry) && CanonicalPath(entry) == _path) declared = true;
        }
        if (!declared) throw new InvalidOperationException("The configured allocation profiler was not declared in LD_PRELOAD.");

        // Resolve before NativeLibrary.Load: dlopen success alone cannot prove
        // interposition. Check the actual global allocator symbols as well as
        // the snapshot endpoint, rejecting a later/competing allocator wrapper.
        var address = GlobalSymbol("db_perf_alloc_snapshot");
        if (SymbolPath(address) != _path || !IsMapped(_path))
            throw new InvalidOperationException("The configured profiler is not the already loaded global snapshot provider.");
        _sha256 = HashFile(_path);
        var module = NativeLibrary.Load(_path);
        try
        {
            if (NativeLibrary.GetExport(module, "db_perf_alloc_snapshot") != address)
                throw new InvalidOperationException("The loaded profiler handle differs from the preloaded snapshot provider.");
            foreach (var name in new[] { "malloc", "calloc", "realloc", "free", "memalign", "aligned_alloc",
                         "posix_memalign", "valloc", "pvalloc", "cfree", "free_sized", "free_aligned_sized" })
            {
                var actual = GlobalSymbol(name);
                if (actual != NativeLibrary.GetExport(module, name) || SymbolPath(actual) != _path)
                    throw new InvalidOperationException("The configured profiler does not interpose the global allocator symbol " + name + ".");
            }
            _snapshot = Marshal.GetDelegateForFunctionPointer<SnapshotFunction>(address);
            _module = module;
            // Bind/marshal once outside the measurement boundary. Coverage
            // errors are retained in subsequent cumulative raw snapshots.
            NativeAllocationSnapshot initial = default;
            Take(ref initial, false);
            if (!ValidLayout(initial)) throw new InvalidOperationException("The preloaded profiler returned an invalid ABI/capacity.");
        }
        catch
        {
            _module = 0;
            NativeLibrary.Free(module);
            throw;
        }
    }

    // Call after worker/scheduler warmup, immediately before releasing work.
    // These three captures only marshal a fixed-size blittable value. Report
    // construction, file hashing, and JSON serialization happen after drain.
    internal void CaptureBefore()
    {
        Enter(0);
        Take(ref _before, true);
        Volatile.Write(ref _stage, 1);
    }

    // Call immediately after every accepted operation/worker has completed,
    // before process-resource reads, result aggregation, and owner disposal.
    internal void CaptureAfter()
    {
        Enter(1);
        Take(ref _after, false);
        Volatile.Write(ref _stage, 2);
    }

    // Call after application worker/session/source disposal completes, before
    // idle observation or serialization. Owner visibility remains route-specific;
    // hidden provider retirement is not inferred from a completed disposal call.
    // Retained runtime/harness/report aggregation storage is included.
    internal void CaptureAfterDrain()
    {
        Enter(2);
        Take(ref _drained, false);
        Volatile.Write(ref _stage, 3);
    }

    internal NativeAllocationProfileReceipt CreateReceipt()
    {
        if (Volatile.Read(ref _stage) != 3 || _module == 0)
            throw new InvalidOperationException("All allocation boundaries must be captured before creating the receipt.");
        var unchanged = HashFile(_path) == _sha256;
        var monotonic = Monotonic(_before, _after) && Monotonic(_after, _drained);
        var layout = ValidLayout(_before) && ValidLayout(_after) && ValidLayout(_drained)
            && _before.TableCapacity == _after.TableCapacity && _after.TableCapacity == _drained.TableCapacity;
        var requested = ConservesRequested(_before, _after) && ConservesRequested(_after, _drained);
        var usable = ConservesUsable(_before, _after) && ConservesUsable(_after, _drained);
        var counts = ConservesCount(_before, _after) && ConservesCount(_after, _drained);
        return new(_path, _sha256, _before, _after, _drained,
            Delta(_after.SuccessfulAllocations, _before.SuccessfulAllocations), Delta(_after.Deallocations, _before.Deallocations),
            Delta(_after.AllocatedRequestedBytes, _before.AllocatedRequestedBytes), Delta(_after.ReleasedRequestedBytes, _before.ReleasedRequestedBytes),
            Delta(_after.AllocatedUsableBytes, _before.AllocatedUsableBytes), Delta(_after.ReleasedUsableBytes, _before.ReleasedUsableBytes),
            _after.PeakRequestedBytes, _after.PeakUsableBytes,
            unchanged && layout && monotonic && Complete(_before) && Complete(_after) && Complete(_drained),
            requested, usable, counts, monotonic, unchanged);
    }

    private void Enter(int expected)
    {
        if (_module == 0 || Interlocked.CompareExchange(ref _stage, -1, expected) != expected)
            throw new InvalidOperationException("Allocation snapshots must be captured once, in order, without concurrent disposal.");
    }

    private void Take(ref NativeAllocationSnapshot value, bool resetPeak)
    {
        var status = _snapshot(ref value, SnapshotBytes, resetPeak ? 1 : 0);
        if (status != 0 || value.Version != 1)
            throw new InvalidOperationException($"Allocation snapshot failed: status={status}, version={value.Version}, initializationFailures={value.InitializationFailures}.");
    }

    public void Dispose()
    {
        var module = Interlocked.Exchange(ref _module, 0);
        if (module != 0) NativeLibrary.Free(module);
        // This drops only our dlopen reference. The loader's LD_PRELOAD owner
        // and the process-global interposition remain until process exit.
    }

    private static ulong? Delta(ulong after, ulong before) => after >= before ? after - before : null;
    private static bool Complete(NativeAllocationSnapshot value) => value.UnknownFrees == 0 && value.UnknownReallocs == 0
        && value.DroppedAllocations == 0 && value.DuplicateAddresses == 0 && value.InitializationFailures == 0;
    private static bool ValidLayout(NativeAllocationSnapshot value) => value.Version == 1
        && value.TableCapacity is >= 256 and <= 4194304 && (value.TableCapacity & (value.TableCapacity - 1)) == 0
        && value.TableBytes == value.TableCapacity * 24 && value.LiveAllocations <= value.TableCapacity
        && value.PeakLiveAllocations >= value.LiveAllocations && value.PeakRequestedBytes >= value.LiveRequestedBytes
        && value.PeakUsableBytes >= value.LiveUsableBytes;
    private static bool Monotonic(NativeAllocationSnapshot before, NativeAllocationSnapshot after) =>
        after.MallocCalls >= before.MallocCalls && after.CallocCalls >= before.CallocCalls
        && after.ReallocCalls >= before.ReallocCalls && after.AlignedCalls >= before.AlignedCalls
        && after.FreeCalls >= before.FreeCalls && after.NullFrees >= before.NullFrees
        && after.SuccessfulAllocations >= before.SuccessfulAllocations && after.FailedAllocations >= before.FailedAllocations
        && after.Deallocations >= before.Deallocations && after.AllocatedRequestedBytes >= before.AllocatedRequestedBytes
        && after.ReleasedRequestedBytes >= before.ReleasedRequestedBytes && after.AllocatedUsableBytes >= before.AllocatedUsableBytes
        && after.ReleasedUsableBytes >= before.ReleasedUsableBytes && after.UnknownFrees >= before.UnknownFrees
        && after.UnknownReallocs >= before.UnknownReallocs && after.DroppedAllocations >= before.DroppedAllocations
        && after.DuplicateAddresses >= before.DuplicateAddresses && after.InitializationFailures >= before.InitializationFailures;
    private static bool ConservesRequested(NativeAllocationSnapshot before, NativeAllocationSnapshot after) =>
        (UInt128)before.LiveRequestedBytes + after.AllocatedRequestedBytes + before.ReleasedRequestedBytes
            == (UInt128)after.LiveRequestedBytes + before.AllocatedRequestedBytes + after.ReleasedRequestedBytes;
    private static bool ConservesUsable(NativeAllocationSnapshot before, NativeAllocationSnapshot after) =>
        (UInt128)before.LiveUsableBytes + after.AllocatedUsableBytes + before.ReleasedUsableBytes
            == (UInt128)after.LiveUsableBytes + before.AllocatedUsableBytes + after.ReleasedUsableBytes;
    private static bool ConservesCount(NativeAllocationSnapshot before, NativeAllocationSnapshot after) =>
        (UInt128)before.LiveAllocations + after.SuccessfulAllocations + before.Deallocations
            == (UInt128)after.LiveAllocations + before.SuccessfulAllocations + after.Deallocations;

    private static string HashFile(string path)
    {
        using var file = File.OpenRead(path);
        return Convert.ToHexStringLower(SHA256.HashData(file));
    }

    private static string CanonicalPath(string path)
    {
        var buffer = new byte[4096]; // Linux PATH_MAX, only used during setup/identity checks.
        if (RealPath(path, buffer) == 0) throw new IOException("Cannot resolve allocation profiler path: " + path);
        var length = Array.IndexOf(buffer, (byte)0);
        if (length < 0) throw new IOException("Allocation profiler canonical path exceeds PATH_MAX.");
        return Encoding.UTF8.GetString(buffer, 0, length);
    }

    private static bool IsMapped(string path)
    {
        foreach (var line in File.ReadLines("/proc/self/maps"))
        {
            var fields = line.Split(' ', 6, StringSplitOptions.RemoveEmptyEntries);
            if (fields.Length == 6 && fields[5] == path) return true;
        }
        return false;
    }

    private static nint GlobalSymbol(string name)
    {
        var address = Dlsym(0, name); // glibc RTLD_DEFAULT.
        if (address == 0) throw new InvalidOperationException("Missing preloaded global allocator symbol " + name + ".");
        return address;
    }

    private static string SymbolPath(nint address)
    {
        if (Dladdr(address, out var info) == 0 || info.FileName == 0)
            throw new InvalidOperationException("Cannot resolve the loaded allocation symbol owner.");
        var path = Marshal.PtrToStringUTF8(info.FileName)
            ?? throw new InvalidOperationException("The loaded allocation symbol owner has no path.");
        return CanonicalPath(path);
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct DlInfo { internal nint FileName, BaseAddress, SymbolName, SymbolAddress; }
    [DllImport("libdl.so.2", EntryPoint = "dlsym", CallingConvention = CallingConvention.Cdecl)]
    private static extern nint Dlsym(nint handle, [MarshalAs(UnmanagedType.LPUTF8Str)] string name);
    [DllImport("libdl.so.2", EntryPoint = "dladdr", CallingConvention = CallingConvention.Cdecl)]
    private static extern int Dladdr(nint address, out DlInfo info);
    [DllImport("libc.so.6", EntryPoint = "realpath", CallingConvention = CallingConvention.Cdecl, SetLastError = true)]
    private static extern nint RealPath([MarshalAs(UnmanagedType.LPUTF8Str)] string path, [Out] byte[] resolved);
}

// Keep the explicit fields in exactly the order of allocation_profile.h. Each
// snapshot is 216 bytes; the native export rejects every other size.
[StructLayout(LayoutKind.Sequential, Pack = 8)]
internal struct NativeAllocationSnapshot
{
    [JsonInclude, JsonPropertyName("version")] public ulong Version;
    [JsonInclude, JsonPropertyName("table_capacity")] public ulong TableCapacity;
    [JsonInclude, JsonPropertyName("table_bytes")] public ulong TableBytes;
    [JsonInclude, JsonPropertyName("malloc_calls")] public ulong MallocCalls;
    [JsonInclude, JsonPropertyName("calloc_calls")] public ulong CallocCalls;
    [JsonInclude, JsonPropertyName("realloc_calls")] public ulong ReallocCalls;
    [JsonInclude, JsonPropertyName("aligned_calls")] public ulong AlignedCalls;
    [JsonInclude, JsonPropertyName("free_calls")] public ulong FreeCalls;
    [JsonInclude, JsonPropertyName("null_frees")] public ulong NullFrees;
    [JsonInclude, JsonPropertyName("successful_allocations")] public ulong SuccessfulAllocations;
    [JsonInclude, JsonPropertyName("failed_allocations")] public ulong FailedAllocations;
    [JsonInclude, JsonPropertyName("deallocations")] public ulong Deallocations;
    [JsonInclude, JsonPropertyName("allocated_requested_bytes")] public ulong AllocatedRequestedBytes;
    [JsonInclude, JsonPropertyName("released_requested_bytes")] public ulong ReleasedRequestedBytes;
    [JsonInclude, JsonPropertyName("allocated_usable_bytes")] public ulong AllocatedUsableBytes;
    [JsonInclude, JsonPropertyName("released_usable_bytes")] public ulong ReleasedUsableBytes;
    [JsonInclude, JsonPropertyName("live_allocations")] public ulong LiveAllocations;
    [JsonInclude, JsonPropertyName("live_requested_bytes")] public ulong LiveRequestedBytes;
    [JsonInclude, JsonPropertyName("live_usable_bytes")] public ulong LiveUsableBytes;
    [JsonInclude, JsonPropertyName("peak_live_allocations")] public ulong PeakLiveAllocations;
    [JsonInclude, JsonPropertyName("peak_requested_bytes")] public ulong PeakRequestedBytes;
    [JsonInclude, JsonPropertyName("peak_usable_bytes")] public ulong PeakUsableBytes;
    [JsonInclude, JsonPropertyName("unknown_frees")] public ulong UnknownFrees;
    [JsonInclude, JsonPropertyName("unknown_reallocs")] public ulong UnknownReallocs;
    [JsonInclude, JsonPropertyName("dropped_allocations")] public ulong DroppedAllocations;
    [JsonInclude, JsonPropertyName("duplicate_addresses")] public ulong DuplicateAddresses;
    [JsonInclude, JsonPropertyName("initialization_failures")] public ulong InitializationFailures;
}

internal sealed record NativeAllocationProfileReceipt(
    [property: JsonPropertyName("libraryPath")] string LibraryPath,
    [property: JsonPropertyName("librarySha256")] string LibrarySha256,
    [property: JsonPropertyName("before")] NativeAllocationSnapshot Before,
    [property: JsonPropertyName("after")] NativeAllocationSnapshot After,
    [property: JsonPropertyName("afterDrain")] NativeAllocationSnapshot AfterDrain,
    [property: JsonPropertyName("allocationCalls")] ulong? AllocationCalls,
    [property: JsonPropertyName("deallocationEvents")] ulong? DeallocationEvents,
    [property: JsonPropertyName("allocatedRequestedBytes")] ulong? AllocatedRequestedBytes,
    [property: JsonPropertyName("releasedRequestedBytes")] ulong? ReleasedRequestedBytes,
    [property: JsonPropertyName("allocatedUsableBytes")] ulong? AllocatedUsableBytes,
    [property: JsonPropertyName("releasedUsableBytes")] ulong? ReleasedUsableBytes,
    [property: JsonPropertyName("trackedRequestedHeapPeakBytes")] ulong TrackedRequestedHeapPeakBytes,
    [property: JsonPropertyName("trackedUsableHeapPeakBytes")] ulong TrackedUsableHeapPeakBytes,
    [property: JsonPropertyName("observedAllocationCoverageComplete")] bool ObservedAllocationCoverageComplete,
    [property: JsonPropertyName("requestedByteConservation")] bool RequestedByteConservation,
    [property: JsonPropertyName("usableByteConservation")] bool UsableByteConservation,
    [property: JsonPropertyName("allocationCountConservation")] bool AllocationCountConservation,
    [property: JsonPropertyName("cumulativeCountersMonotonic")] bool CumulativeCountersMonotonic,
    [property: JsonPropertyName("libraryFileUnchanged")] bool LibraryFileUnchanged)
{
    [JsonPropertyName("passed")] public bool Passed => ObservedAllocationCoverageComplete && RequestedByteConservation
        && UsableByteConservation && AllocationCountConservation && CumulativeCountersMonotonic && LibraryFileUnchanged;
    [JsonPropertyName("fullAddressSpaceHeapPeakProven")] public bool FullAddressSpaceHeapPeakProven => false;
    [JsonPropertyName("timingComparisonEligible")] public bool TimingComparisonEligible => false;
    [JsonPropertyName("preloadedGlobalAllocatorIdentityVerified")] public bool PreloadedGlobalAllocatorIdentityVerified => true;
    [JsonPropertyName("scope")] public string Scope => "Separate instrumented lane; interposed public glibc allocator calls across all threads, including observable C++/provider/.NET native calls. Excludes private mmap, managed object heap, allocator metadata and hidden internal calls. Never subtract this profile from managed allocation counters.";
    [JsonPropertyName("peakScope")] public string PeakScope => "Live tracked allocation sizes at wrapper registration boundaries; excludes transient internal realloc copy overlap and allocator metadata. Fixed profiler table mmap bytes are reported separately in each raw snapshot.";
    [JsonPropertyName("drainScope")] public string DrainScope => "After application worker/session/source disposal calls complete, before idle observation and JSON serialization. Includes retained runtime, harness and report-aggregation storage. Actual owner visibility follows each route's raw counters; this does not prove hidden provider physical retirement or attribute retained storage to a leak.";
    [JsonPropertyName("counterSemantics")] public string CounterSemantics => "Successful realloc retires the old tracked allocation and records its replacement, including in-place resize; free_calls also includes null frees. Raw cumulative counters precede every subtraction. Coverage errors invalidate the profile.";
}
