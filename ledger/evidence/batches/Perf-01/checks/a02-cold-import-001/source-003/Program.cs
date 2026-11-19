using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Security.Cryptography;

internal static partial class Program
{
    private const int WorkerCount = 8;
    private static readonly CountdownEvent CallbackReady = new(WorkerCount);
    private static nint _module;
    private static nint _probe;
    private static string _copy = "";
    private static bool _owned;
    private static int _resolutions;
    private static int _completedCallbacks;

    private static nint Resolve(string name, System.Reflection.Assembly _, DllImportSearchPath? __)
    {
        if (name != "nw_a02_alpha") return 0;
        int ordinal = Interlocked.Increment(ref _resolutions);
        nint handle = _owned ? NativeLibrary.Load(_copy) : _module;
        if (handle != _module || NativeLibrary.GetExport(handle, "nw_a02_alpha_probe") != _probe)
            throw new InvalidOperationException("Callback did not resolve the originally loaded binary");
        Console.WriteLine($"CALLBACK entry={ordinal} owned={_owned} handle=0x{handle:x}");
        // Every cold importer must have observed a zero module cell before any
        // callback returns. No lock is held while the callbacks rendezvous.
        if (ordinal <= WorkerCount)
        {
            CallbackReady.Signal();
            if (!CallbackReady.Wait(TimeSpan.FromSeconds(10)))
                throw new TimeoutException("Cold importers did not overlap");
        }
        Interlocked.Increment(ref _completedCallbacks);
        return handle;
    }

    private static int Main(string[] args)
    {
        if (args.Length != 4) throw new ArgumentException("mode fixture fresh-directory --require-aot required");
        string mode = args[0];
        _owned = mode is "owned" or "owned-unlink";
        if (mode is not ("borrowed" or "owned" or "owned-unlink")) throw new ArgumentException("Unknown mode");
        if (args[3] != "--require-aot" || RuntimeFeature.IsDynamicCodeSupported)
            throw new InvalidOperationException("Actual Native AOT required");
        string fixture = Path.GetFullPath(args[1]);
        string fresh = Path.GetFullPath(args[2]);
        if (Directory.Exists(fresh) || File.Exists(fresh)) throw new InvalidOperationException("Fresh fixture directory required");
        Directory.CreateDirectory(fresh);
        _copy = Path.Combine(fresh, "libnw_a02_alpha.so");
        File.Copy(fixture, _copy, overwrite: false);
        string originalSha = Hash(fixture);
        if (Hash(_copy) != originalSha) throw new InvalidOperationException("Fixture copy hash differs");
        _module = NativeLibrary.Load(_copy); // This original reference is never transferred or freed.
        _probe = NativeLibrary.GetExport(_module, "nw_a02_alpha_probe");
        Console.WriteLine($"BEGIN mode={mode} aot=true workers={WorkerCount} fixture_sha256={originalSha} module=0x{_module:x} probe=0x{_probe:x}");
        Maps("loaded");
        if (mode == "owned-unlink")
        {
            File.Delete(_copy); // Only the new copy is unlinked; the input fixture is untouched.
            if (File.Exists(_copy)) throw new InvalidOperationException("Fixture copy still exists after unlink");
            Console.WriteLine("UNLINK original-copy-missing=true");
        }
        NativeLibrary.SetDllImportResolver(typeof(Program).Assembly, Resolve);
        using var ready = new CountdownEvent(WorkerCount);
        using var start = new ManualResetEventSlim();
        Task[] workers = Enumerable.Range(0, WorkerCount).Select(worker => Task.Factory.StartNew(() =>
        {
            ready.Signal();
            start.Wait();
            for (int i = worker; i < 64; i += WorkerCount)
                Check((ulong)i, Native.Alpha((ulong)i));
        }, CancellationToken.None, TaskCreationOptions.LongRunning, TaskScheduler.Default)).ToArray();
        bool allReady = ready.Wait(TimeSpan.FromSeconds(10));
        Console.WriteLine($"GATE ready={allReady} callbacks={_resolutions}");
        start.Set();
        bool allCompleted = Task.WaitAll(workers, TimeSpan.FromSeconds(20));
        if (!allReady || !allCompleted) throw new InvalidOperationException("Worker gate/join failed");
        if (_resolutions != WorkerCount || _completedCallbacks != WorkerCount)
            throw new InvalidOperationException("The eight cold callback resolutions were not all exercised");
        if (Native.AlphaCalls() != 0) throw new InvalidOperationException("Plain runtime control did not call NativeWeave bootstrap");
        if (NativeLibrary.GetExport(_module, "nw_a02_alpha_probe") != _probe)
            throw new InvalidOperationException("Original resident export changed");
        Check(123, Pointer(123));
        if (Hash(fixture) != originalSha) throw new InvalidOperationException("Input fixture changed");
        if (mode == "owned-unlink" && File.Exists(_copy)) throw new InvalidOperationException("Unlinked path reappeared");
        Maps("complete");
        Console.WriteLine($"PASS mode={mode} calls=64 callbacks={_resolutions} completed_callbacks={_completedCallbacks} original_reference_valid=true fixture_sha256={originalSha} unlinked={mode == "owned-unlink"}");
        return 0;
    }

    private static string Hash(string path)
    {
        using FileStream stream = File.OpenRead(path);
        return Convert.ToHexStringLower(SHA256.HashData(stream));
    }

    private static void Maps(string stage)
    {
        string[] mappings = File.ReadLines("/proc/self/maps").Where(line => line.EndsWith(_copy, StringComparison.Ordinal) || line.EndsWith(_copy + " (deleted)", StringComparison.Ordinal)).ToArray();
        if (mappings.Length == 0) throw new InvalidOperationException("Original native mapping unavailable");
        foreach (string mapping in mappings) Console.WriteLine($"MAP stage={stage} {mapping}");
        if (stage == "complete" && _copy.Length != 0 && !File.Exists(_copy) && !mappings.All(line => line.EndsWith(" (deleted)", StringComparison.Ordinal)))
            throw new InvalidOperationException("Deleted mapping identity not visible");
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    private static unsafe ulong Pointer(ulong input) => ((delegate* unmanaged[Cdecl]<ulong, ulong>)_probe)(input);
    private static void Check(ulong input, ulong result)
    {
        if (result != (input ^ 0xa102UL)) throw new InvalidOperationException("Native xor mismatch");
    }
}

internal static partial class Native
{
    [LibraryImport("nw_a02_alpha", EntryPoint = "nw_a02_alpha_probe")]
    [UnmanagedCallConv(CallConvs = [typeof(CallConvCdecl)])]
    internal static partial ulong Alpha(ulong input);

    [LibraryImport("nw_a02_alpha", EntryPoint = "nw_a02_alpha_bootstrap_calls")]
    [UnmanagedCallConv(CallConvs = [typeof(CallConvCdecl)])]
    internal static partial uint AlphaCalls();
}
