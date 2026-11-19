using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

internal static partial class Program
{
    private static readonly object ResolverGate = new();
    private static nint _module;
    private static nint _probe;
    private static int _resolutions;

    private static int Main(string[] args)
    {
        if (args.Length < 2) throw new ArgumentException("mode fixture required");
        string mode = args[0];
        bool aot = !RuntimeFeature.IsDynamicCodeSupported;
        if (args.Contains("--require-aot") && !aot) throw new InvalidOperationException("AOT required");
        _module = NativeLibrary.Load(Path.GetFullPath(args[1]));
        _probe = NativeLibrary.GetExport(_module, "nw_a02_alpha_probe");
        NativeLibrary.SetDllImportResolver(typeof(Program).Assembly, (name, _, _) =>
        {
            lock (ResolverGate)
            {
                Interlocked.Increment(ref _resolutions);
                return name == "nw_a02_alpha" ? _module : 0;
            }
        });
        Console.WriteLine($"BEGIN mode={mode} aot={aot}; plain NativeLibrary resolver installed");
        if (mode is "serial" or "warm") Check(123, Native.Alpha(123));
        if (mode == "serial")
        {
            Console.WriteLine($"PASS serial resolutions={_resolutions} bootstrap={Native.AlphaCalls()}");
            return 0;
        }
        if (mode is not ("cold" or "warm" or "pointer")) throw new ArgumentException("unknown mode");
        using var ready = new CountdownEvent(8);
        using var start = new ManualResetEventSlim();
        Task[] workers = Enumerable.Range(0, 8).Select(worker => Task.Factory.StartNew(() =>
        {
            ready.Signal();
            start.Wait();
            for (int i = worker; i < 64; i += 8)
            {
                ulong input = (ulong)i;
                Check(input, mode == "pointer" ? Pointer(input) : Native.Alpha(input));
            }
        }, CancellationToken.None, TaskCreationOptions.LongRunning, TaskScheduler.Default)).ToArray();
        bool allReady = ready.Wait(TimeSpan.FromSeconds(10));
        Console.WriteLine($"GATE ready={allReady}; resolutions={_resolutions}");
        start.Set();
        bool allCompleted = Task.WaitAll(workers, TimeSpan.FromSeconds(10));
        if (!allReady || !allCompleted) throw new InvalidOperationException("Workers did not complete");
        uint calls = Native.AlphaCalls();
        if (calls != 0) throw new InvalidOperationException("This plain-runtime control did not call bootstrap");
        Console.WriteLine($"PASS {mode} calls=64 resolutions={_resolutions} bootstrap={calls}");
        return 0;
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
