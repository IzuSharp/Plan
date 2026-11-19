using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

internal static partial class Program
{
    private static readonly object ResolverGate = new();
    private static nint _module;
    private static nint _probe;
    private static int _resolutions;
    private static string _fixture = "";
    private static bool _installed;
    private static readonly System.Reflection.Assembly OwnerAssembly = typeof(Program).Assembly;
    private static readonly ConditionalWeakTable<System.Reflection.Assembly, Resolver> Resolvers = new();

    private static void Bind()
    {
        lock (ResolverGate)
        {
            if (_module == 0) _module = NativeLibrary.Load(_fixture);
            if (_installed) return;
            NativeLibrary.SetDllImportResolver(OwnerAssembly, (name, _, _) =>
            {
                lock (ResolverGate)
                {
                    Interlocked.Increment(ref _resolutions);
                    return name == "nw_a02_alpha" ? _module : 0;
                }
            });
            _installed = true;
        }
    }

    private sealed class Resolver
    {
        private readonly object _gate = new();
        private readonly Dictionary<string, nint> _modules = new(StringComparer.Ordinal);
        private bool _bound;
        internal void Bind()
        {
            lock (_gate)
            {
                if (!_bound)
                {
                    NativeLibrary.SetDllImportResolver(OwnerAssembly, Resolve);
                    _bound = true;
                }
                _modules["nw_a02_alpha"] = _module;
                _modules["libnw_a02_alpha.so"] = _module;
            }
        }
        private nint Resolve(string name, System.Reflection.Assembly _, DllImportSearchPath? __)
        {
            lock (_gate)
            {
                Interlocked.Increment(ref _resolutions);
                return _modules.GetValueOrDefault(name);
            }
        }
    }

    private static int Main(string[] args)
    {
        if (args.Length < 2) throw new ArgumentException("mode fixture required");
        string mode = args[0];
        bool aot = !RuntimeFeature.IsDynamicCodeSupported;
        if (args.Contains("--require-aot") && !aot) throw new InvalidOperationException("AOT required");
        _fixture = Path.GetFullPath(args[1]);
        if (mode != "late-load") _module = NativeLibrary.Load(_fixture);
        if (mode is not ("late" or "late-load" or "late-cwt")) Bind();
        Console.WriteLine($"BEGIN mode={mode} aot={aot}; plain NativeLibrary control");
        if (mode is "serial" or "warm") Check(123, Native.Alpha(123));
        if (mode == "serial")
        {
            Console.WriteLine($"PASS serial resolutions={_resolutions} bootstrap={Native.AlphaCalls()}");
            return 0;
        }
        if (mode is not ("cold" or "warm" or "late" or "late-load" or "late-cwt")) throw new ArgumentException("unknown mode");
        using var ready = new CountdownEvent(8);
        using var start = new ManualResetEventSlim();
        Task[] workers = Enumerable.Range(0, 8).Select(worker => Task.Factory.StartNew(() =>
        {
            ready.Signal();
            start.Wait();
            for (int i = worker; i < 64; i += 8)
            {
                ulong input = (ulong)i;
                if (mode is "late" or "late-load") Bind();
                if (mode == "late-cwt") Resolvers.GetValue(OwnerAssembly, static _ => new Resolver()).Bind();
                Check(input, Native.Alpha(input));
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
