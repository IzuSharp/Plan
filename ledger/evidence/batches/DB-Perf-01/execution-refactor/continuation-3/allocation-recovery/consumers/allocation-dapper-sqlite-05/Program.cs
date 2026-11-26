using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Text.Json;
using Dapper;

[module: DapperAot]

if (RuntimeFeature.IsDynamicCodeSupported)
    throw new InvalidOperationException("Run the published Linux Native AOT executable.");
var options = Options.Parse(args);
BusinessAllocation.Configure(options.Output, options.Rows, "dapper-aot");
Directory.CreateDirectory(Path.GetDirectoryName(options.Output)!);
var progress = new Progress();
QueryContract? contract = null;
try
{
    contract = options.ReadContract();
    await using var driver = new PhaseDriver(options);
    await driver.Open();
    if (options.Initialize) await driver.Initialize();
    var probe = new PhaseProbe(driver.Connection, options.Rows, progress);
    progress.Locate("first", -1, 0);
    var first = await probe.Run(1);
    const int warmup = 64;
    for (var i = 0; i < warmup; i++)
    {
        progress.Locate("warmup", -1, i);
        _ = await probe.Run(1 + i % 2);
    }
    var measurements = new Window[options.Windows];
    using var process = Process.GetCurrentProcess();
    for (var window = 0; window < options.Windows; window++)
    {
        var samples = new Sample[options.Iterations];
        BusinessAllocation.BeginWindow("dapper-aot", window, options.Iterations, options.Rows);
        var gc0 = GC.CollectionCount(0); var gc1 = GC.CollectionCount(1); var gc2 = GC.CollectionCount(2);
        var cpuBefore = process.TotalProcessorTime.Ticks;
        var allocatedBefore = GC.GetTotalAllocatedBytes(true);
        var started = Stopwatch.GetTimestamp();
        for (var i = 0; i < options.Iterations; i++)
        {
            progress.Locate("window", window, i);
            samples[i] = await probe.Run(1 + i % 2);
        }
        var ended = Stopwatch.GetTimestamp();
        var allocatedAfter = GC.GetTotalAllocatedBytes(true);
        var cpuAfter = process.TotalProcessorTime.Ticks;
        var end0 = GC.CollectionCount(0); var end1 = GC.CollectionCount(1); var end2 = GC.CollectionCount(2);
        process.Refresh();
        measurements[window] = new("dapper-aot", window, options.Iterations, allocatedBefore, allocatedAfter,
            end0 - gc0, end1 - gc1, end2 - gc2, cpuBefore, cpuAfter, process.WorkingSet64, process.PeakWorkingSet64,
            started, ended, samples);
        BusinessAllocation.EndWindow(allocatedBefore, allocatedAfter, end0 - gc0, end1 - gc1, end2 - gc2);
    }
    progress.Locate("teardown", -1, -1); progress.Stage = "release";
    var teardownStarted = Stopwatch.GetTimestamp();
    await driver.DisposeAsync();
    var teardownEnded = Stopwatch.GetTimestamp();
    if (!driver.ConnectionClosed) throw new InvalidOperationException("The rented provider connection remained open after disposal.");
    var receipt = new Receipt(1, PhaseDriver.KordaProvider, PhaseDriver.Provider, true, driver.DatabaseVersion,
        PhaseDriver.Versions, Environment.Version.ToString(), PhaseDriver.Hash(Environment.ProcessPath!),
        driver.NativePath, driver.NativeSha256, driver.CompileOptions, contract, contract.RawTemplate, contract.RawTemplate,
        $"Int64 tenant alternates 1 and 2; Int64 id={options.Rows}; ordered full List<PhaseRow> with {options.Rows} rows and exact Id/Note/null checks; rows=1 binds the complete composite primary key",
        options.Rows, Stopwatch.Frequency, warmup, [first], measurements, teardownEnded - teardownStarted,
        driver.ConnectionClosed, true, 1, 0,
        "ALLOCATION-INSTRUMENTED; TimingCredit=false. Local Dapper.AOT phase diagnostic, one connection rented once across first/warmup/windows, no transaction. " +
        "SQL equals the actual Korda phase receipt RawTemplate byte for byte; Korda rendered PostgreSQL markers are $1/$2 and SQLite markers are anonymous ?, while this ADO.NET command uses @tenant/@id. " +
        "Dapper.AOT CacheCommand reuses the generated command factory, two ordinal Int64 parameters and one mutable serial argument object; Npgsql automatic preparation is disabled, with no explicit Prepare. " +
        "Construction includes the result List/backing array and stream construction. Submit-to-first-row includes first MoveNext, DTO mapping and List.Add. " +
        "Read-complete includes all remaining rows and EOF, including cleanup performed by the upstream async iterator before it returns false. Release measures the subsequent DisposeAsync. " +
        "All rows are materialized and checked outside phase timestamps but inside the whole-process window. Phase durations do not partition allocations. " +
        "Allocation/GC/CPU are whole process; peak RSS is process lifetime. Setup and first execution are not independently process-cold ORM/compiler measurements. " +
        "ConnectionClosed observes the public provider connection; internal provider/native owner counts, FFI and protocol waits are not instrumented by this consumer. " +
        "This two-field query is independent of the nine-field mixed workload; no CI performance run is added.");
    progress.Stage = "receipt";
    await File.WriteAllTextAsync(options.Output, JsonSerializer.Serialize(receipt, ProbeJson.Default.Receipt) + Environment.NewLine);
    BusinessAllocation.Write();
    Console.WriteLine("DB_PERF_DAPPER_QUERY_PHASES " + options.Output);
}
catch (Exception failure)
{
    progress.Capture(failure);
    var receipt = new FailureReceipt(1, PhaseDriver.KordaProvider, true, false, PhaseDriver.Hash(Environment.ProcessPath!),
        contract, progress.Failures.ToArray(), "Failed phase run; no performance credit. Earlier query failure is retained if cleanup also failed.");
    await File.WriteAllTextAsync(options.Output + ".failure.json", JsonSerializer.Serialize(receipt, ProbeJson.Default.FailureReceipt) + Environment.NewLine);
    throw;
}
