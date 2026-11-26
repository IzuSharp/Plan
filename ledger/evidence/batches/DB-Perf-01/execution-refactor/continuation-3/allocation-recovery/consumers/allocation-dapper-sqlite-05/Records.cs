using System.Diagnostics;
using System.Text.Json.Serialization;

internal readonly record struct Sample(long ConstructTicks, long SubmitToFirstRowTicks, long ReadCompleteTicks, long ReleaseTicks, int Rows);
internal sealed record Window(string Route, int Index, int Operations, long AllocatedBefore, long AllocatedAfter,
    int Gen0, int Gen1, int Gen2, long CpuBeforeTicks, long CpuAfterTicks, long ResidentBytes, long PeakResidentBytes,
    long StartedTicks, long FinishedTicks, Sample[] Samples);
internal sealed record DependencyVersion(string Name, string AssemblyVersion, string InformationalVersion);
internal sealed record QueryContract(string KordaReceiptPath, string KordaReceiptSha256, string KordaExecutableSha256,
    string KordaSql, string RawTemplate);
internal sealed record Receipt(int SchemaVersion, string Provider, string Driver, bool NativeAot,
    string DatabaseVersion, DependencyVersion[] Versions, string RuntimeVersion, string ExecutableSha256,
    string? NativePath, string? NativeSha256, string[] SqliteCompileOptions, QueryContract Contract,
    string Sql, string RawTemplate, string ParametersAndResults, int ResultRows, long StopwatchFrequency,
    int WarmupPerRoute, Sample[] FirstExecutions, Window[] Windows, long TeardownTicks, bool ConnectionClosed,
    bool CacheCommand, int PhysicalConnectionsOpened, int PostgreSqlMaxAutoPrepare, string Scope);
internal sealed record FailureObservation(string Area, int Window, int Iteration, string Stage, int? Rows,
    long ObservedTicks, string Type, string Message, string? StackTrace);
internal sealed record FailureReceipt(int SchemaVersion, string Provider, bool NativeAot, bool TimingCredit,
    string ExecutableSha256, QueryContract? Contract, FailureObservation[] Observations, string Scope);

internal sealed class Progress
{
    internal string Area = "setup", Stage = "setup";
    internal int Window = -1, Iteration = -1;
    private readonly List<Exception> _seen = [];
    internal readonly List<FailureObservation> Failures = [];
    internal void Locate(string area, int window, int iteration)
    { Area = area; Window = window; Iteration = iteration; }
    internal void Capture(Exception error, int? rows = null)
    {
        if (_seen.Any(value => ReferenceEquals(value, error))) return;
        _seen.Add(error);
        Failures.Add(new(Area, Window, Iteration, Stage, rows, Stopwatch.GetTimestamp(),
            error.GetType().FullName ?? error.GetType().Name, error.Message, error.StackTrace));
    }
}

[JsonSerializable(typeof(Receipt))]
[JsonSerializable(typeof(FailureReceipt))]
internal partial class ProbeJson : JsonSerializerContext;
