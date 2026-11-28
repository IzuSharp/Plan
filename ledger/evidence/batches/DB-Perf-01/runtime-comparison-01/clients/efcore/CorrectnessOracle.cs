using System.Diagnostics;
using System.Text.Json;
using System.Text.Json.Serialization;

// Sticky for the lifetime of this independently launched consumer. A failed
// result/state check is recorded at its discovery point, before cleanup can
// replace the exception. It is never reset between recovery phases or diluted
// into the permitted rate of operational database failures.
internal static class CorrectnessOracle
{
    private static long s_failures;
    private static int s_firstClaimed;
    private static string s_phase = "setup";
    private static OracleFailure? s_first;
    internal static long Failures => Volatile.Read(ref s_failures);
    internal static OracleFailure? FirstFailure => Volatile.Read(ref s_first);
    internal static void SetPhase(string phase) => Volatile.Write(ref s_phase, phase);

    internal static OracleViolationException Failure(string message, string? caseId = null, Exception? inner = null)
    {
        Record(message, caseId, inner);
        return new(message, inner);
    }

    private static void Record(string message, string? caseId, Exception? inner)
    {
        long sequence = Interlocked.Increment(ref s_failures);
        if (Interlocked.CompareExchange(ref s_firstClaimed, 1, 0) == 0)
            Volatile.Write(ref s_first, new(sequence, Volatile.Read(ref s_phase), caseId, message,
                inner?.ToString(), Environment.StackTrace, Stopwatch.GetTimestamp(), Stopwatch.Frequency));
    }

    // Record typed materialization/hash failures before a later Dispose can
    // replace their exception. Ordinary cancellation/provider I/O remains in
    // the operational error ledger; it is not inferred to be data corruption.
    internal static void ObserveContractFailure(Exception error, string? caseId = null)
    {
        if (error is OracleViolationException) return;
        if (error is AggregateException aggregate)
        {
            foreach (var inner in aggregate.InnerExceptions) ObserveContractFailure(inner, caseId);
            return;
        }
        if (error is InvalidOperationException or InvalidDataException or InvalidCastException
            or FormatException or OverflowException or ArgumentException or NullReferenceException
            or System.Data.DataException or JsonException)
            Record("The fixed workload's materialization or execution contract failed.", caseId, error);
    }

    internal static void ObserveCleanupFailure(Exception error, string? caseId = null)
        => Record("A workload owner did not retire cleanly; no correctness or timing credit.", caseId, error);

    internal static void RequireClean()
    {
        if (Failures != 0) throw new InvalidOperationException("A prior workload oracle violation invalidates this command.");
    }

    // This sidecar also preserves setup/warmup failures when no normal receipt
    // can be returned, and never overwrites a complete receipt or prior attempt.
    internal static void WriteFailure(string? output)
    {
        if (Failures == 0) return;
        var receipt = new OracleCommandFailure("DB-Perf-01.oracle-failure.v1", Failures, FirstFailure,
            "Process-lifetime sticky oracle violations; no SLO, timing, long-segment or correctness credit.");
        string json = JsonSerializer.Serialize(receipt, OracleJson.Default.OracleCommandFailure);
        Console.Error.WriteLine("DB_PERF_ORACLE_FAILURE " + json);
        if (output is not null)
        {
            using var file = new FileStream(output + ".oracle-failure.json", FileMode.CreateNew, FileAccess.Write, FileShare.Read);
            using var writer = new StreamWriter(file);
            writer.WriteLine(json);
        }
    }
}

internal sealed class OracleViolationException(string message, Exception? inner = null) : Exception(message, inner);
internal sealed record OracleFailure(long Sequence, string Phase, string? CaseId, string Message,
    string? InnerError, string ObservedStack, long ObservedTicks, long TimerFrequency);
internal sealed record OracleCommandFailure(string Schema, long OracleFailures, OracleFailure? FirstOracleFailure, string Scope);

[JsonSerializable(typeof(OracleCommandFailure))]
internal partial class OracleJson : JsonSerializerContext;
