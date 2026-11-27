// LOCAL DIAGNOSTIC OVERLAY ONLY. Never merge or treat this image as ordinary timing.
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks.Sources;

namespace Korda.Interop.Callbacks;

internal sealed record CallbackDiagnosticRequest(long Controller, ulong Generation, short Version);

internal sealed class CallbackDiagnosticContinuation(CallbackDiagnosticRequest request, long registration,
    Action<object?> continuation, object? state)
{
    internal void Invoke()
    {
        CallbackDispatchDiagnostics.Activity("continuation", request, enter: true, registration);
        try { continuation(state); }
        finally { CallbackDispatchDiagnostics.Activity("continuation", request, enter: false, registration); }
    }
}

internal sealed class CallbackDiagnosticSetter(long id, CallbackDiagnosticRequest request, CallbackDiagnosticSetter? previous)
{
    internal readonly long Id = id;
    internal readonly CallbackDiagnosticRequest Request = request;
    internal readonly CallbackDiagnosticSetter? Previous = previous;
}

internal static partial class CallbackDispatchDiagnostics
{
    private const long MaximumRecords = 1_000_000;
    private static readonly object Gate = new();
    private static readonly string? Path = Environment.GetEnvironmentVariable("KORDA_TAIL_DIAGNOSTIC_PATH");
    private static long _controllers, _offers, _registrations, _setters, _records, _dropped, _clockErrors;
    private static long _clockCalls, _tidCalls;
    private static int _activeSetters, _activeContinuations, _activeRegistrations, _activeResults;
    private static int _activeExecutions, _activeOffers, _pendingOffers, _recorders;
    private static bool _closed;
    [ThreadStatic] private static int _nativeTid;
    [ThreadStatic] private static CallbackDiagnosticSetter? _setter;
    private static readonly StreamWriter? Writer = Open();

    [StructLayout(LayoutKind.Sequential)]
    private struct Timespec { internal long Seconds; internal long Nanoseconds; }

    [LibraryImport("libc", EntryPoint = "clock_gettime", SetLastError = true)]
    private static partial int ClockGetTime(int clock, out Timespec value);

    [LibraryImport("libc", EntryPoint = "gettid")]
    private static partial int GetTid();

    internal static bool Enabled => Writer is not null;
    internal static long NewController() => Interlocked.Increment(ref _controllers);
    internal static long NewOffer() => Interlocked.Increment(ref _offers);
    internal static long NewRegistration() => Interlocked.Increment(ref _registrations);
    internal static CallbackDiagnosticRequest? NewRequest(long controller, ulong generation, short version) =>
        Enabled ? new(controller, generation, version) : null;

    private static StreamWriter? Open()
    {
        if (string.IsNullOrEmpty(Path)) return null;
        var writer = new StreamWriter(new FileStream(Path, FileMode.CreateNew, FileAccess.Write, FileShare.Read),
            new UTF8Encoding(false), 65536);
        writer.WriteLine(FormattableString.Invariant($"#header\t1\t{Environment.ProcessId}\t{Stopwatch.Frequency}\t{MaximumRecords}"));
        writer.WriteLine("#columns\tseq\tkind\tcontroller\tgeneration\tversion\tmanaged_tid\tnative_tid\tmono_ticks\tthread_cpu_ns\tsetter\tsetter_controller\tsetter_generation\tsetter_version\targ0\targ1\targ2");
        writer.Flush();
        AppDomain.CurrentDomain.ProcessExit += static (_, _) => Close();
        return writer;
    }

    internal static int SchedulerKind(ValueTaskSourceOnCompletedFlags flags)
    {
        if ((flags & ValueTaskSourceOnCompletedFlags.UseSchedulingContext) == 0) return 0;
        if (SynchronizationContext.Current is { } context && context.GetType() != typeof(SynchronizationContext)) return 1;
        return TaskScheduler.Current != TaskScheduler.Default ? 2 : 0;
    }

    internal static void Record(string kind, CallbackDiagnosticRequest? request, long arg0 = 0, long arg1 = 0, long arg2 = 0)
    {
        if (request is null || Writer is null) return;
        Interlocked.Increment(ref _recorders);
        try
        {
            long timestamp = Stopwatch.GetTimestamp();
            Interlocked.Increment(ref _clockCalls);
            long cpu = ClockGetTime(3, out var clock) == 0 ? checked(clock.Seconds * 1_000_000_000L + clock.Nanoseconds) : -1;
            if (cpu < 0) Interlocked.Increment(ref _clockErrors);
            if (_nativeTid == 0)
            {
                Interlocked.Increment(ref _tidCalls);
                _nativeTid = GetTid();
                if (_nativeTid <= 0) Interlocked.Increment(ref _clockErrors);
            }
            var setter = _setter;
            lock (Gate)
            {
                if (_closed)
                {
                    Interlocked.Increment(ref _dropped);
                    // A footer cannot silently claim that a later event did not
                    // occur. The external validator rejects this sidecar.
                    File.AppendAllText(Path + ".late", kind + "\n");
                    return;
                }
                if (_records >= MaximumRecords) { Interlocked.Increment(ref _dropped); return; }
                Writer.WriteLine(FormattableString.Invariant($"{++_records}\t{kind}\t{request.Controller}\t{request.Generation}\t{request.Version}\t{Environment.CurrentManagedThreadId}\t{_nativeTid}\t{timestamp}\t{cpu}\t{setter?.Id ?? 0}\t{setter?.Request.Controller ?? 0}\t{setter?.Request.Generation ?? 0}\t{setter?.Request.Version ?? 0}\t{arg0}\t{arg1}\t{arg2}"));
            }
        }
        catch
        {
            // Diagnostic failures invalidate the raw ledger; they must not be
            // substituted for the business operation's first exception.
            Interlocked.Increment(ref _dropped);
        }
        finally { Interlocked.Decrement(ref _recorders); }
    }

    internal static CallbackDiagnosticSetter? EnterSetter(CallbackDiagnosticRequest? request)
    {
        if (request is null) return null;
        Interlocked.Increment(ref _activeSetters);
        var setter = new CallbackDiagnosticSetter(Interlocked.Increment(ref _setters), request, _setter);
        _setter = setter;
        Record("setter-enter", request);
        return setter;
    }

    internal static void ExitSetter(CallbackDiagnosticSetter? setter, bool failed)
    {
        if (setter is null) return;
        if (!ReferenceEquals(_setter, setter)) Interlocked.Increment(ref _dropped);
        Record("setter-exit", setter.Request, failed ? 1 : 0);
        _setter = setter.Previous;
        Interlocked.Decrement(ref _activeSetters);
    }

    internal static void Activity(string kind, CallbackDiagnosticRequest? request, bool enter,
        long arg0 = 0, long arg1 = 0, long arg2 = 0)
    {
        if (request is null) return;
        if (enter) AdjustActivity(kind, 1);
        Record(kind + (enter ? "-enter" : "-exit"), request, arg0, arg1, arg2);
        if (!enter) AdjustActivity(kind, -1);
    }

    private static void AdjustActivity(string kind, int delta)
    {
        switch (kind)
        {
            case "oncompleted": Interlocked.Add(ref _activeRegistrations, delta); break;
            case "continuation": Interlocked.Add(ref _activeContinuations, delta); break;
            case "getresult": Interlocked.Add(ref _activeResults, delta); break;
            case "execute": Interlocked.Add(ref _activeExecutions, delta); break;
            default: Interlocked.Increment(ref _dropped); break;
        }
    }

    internal static void BeginOffer(CallbackDiagnosticRequest? request, long offer)
    {
        if (request is null) return;
        Interlocked.Increment(ref _activeOffers);
        Interlocked.Increment(ref _pendingOffers);
        Record("offer-enter", request, offer);
    }

    internal static void EndOffer(CallbackDiagnosticRequest? request, long offer, bool accepted, bool threw)
    {
        if (request is null) return;
        Record("offer-exit", request, offer, accepted ? 1 : 0, threw ? 1 : 0);
        if (!accepted) Interlocked.Decrement(ref _pendingOffers);
        Interlocked.Decrement(ref _activeOffers);
    }

    internal static void ClaimOffer(long offer)
    {
        if (offer != 0 && Interlocked.Decrement(ref _pendingOffers) < 0) Interlocked.Increment(ref _dropped);
    }

    private static bool Idle() => Volatile.Read(ref _activeSetters) == 0
        && Volatile.Read(ref _activeContinuations) == 0 && Volatile.Read(ref _activeRegistrations) == 0
        && Volatile.Read(ref _activeResults) == 0 && Volatile.Read(ref _activeExecutions) == 0
        && Volatile.Read(ref _activeOffers) == 0 && Volatile.Read(ref _pendingOffers) == 0
        && Volatile.Read(ref _recorders) == 0;

    private static void Close()
    {
        // Measurement has already ended. Give retired diagnostic frames a
        // bounded chance to append their exits before writing the final ledger.
        var started = Stopwatch.GetTimestamp();
        while (!Idle() && Stopwatch.GetElapsedTime(started) < TimeSpan.FromSeconds(5)) Thread.Sleep(1);
        lock (Gate)
        {
            if (_closed || Writer is null) return;
            _closed = true;
            Writer.WriteLine(FormattableString.Invariant($"#footer\t{_records}\t{_dropped}\t{_clockErrors}\t{_activeSetters}\t{_activeContinuations}\t{_activeRegistrations}\t{_activeResults}\t{_activeExecutions}\t{_activeOffers}\t{_pendingOffers}\t{_recorders}\t{_clockCalls}\t{_tidCalls}"));
            Writer.Flush(); Writer.Dispose();
        }
    }
}
