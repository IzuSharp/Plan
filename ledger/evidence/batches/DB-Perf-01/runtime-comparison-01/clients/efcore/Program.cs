using System.Text.Json;

var options = Options.Parse(args);
try
{
    await using var source = new DatabaseDriver(options);
    Console.WriteLine("DB_PERF_RUNTIME " + JsonSerializer.Serialize(source.RuntimeIdentity, PerfJson.Default.RuntimeIdentity));
    await source.VerifyDataset(options);
    var result = await Measurement.Run(source, options);
    var json = JsonSerializer.Serialize(result, PerfJson.Default.RunReceipt);
    if (options.Output is not null) File.WriteAllText(options.Output, json + "\n");
    Console.WriteLine("DB_PERF_RESULT " + json);
    return result.Failed == 0 && result.OracleFailures == 0
        && result.ApplicationConnectionsReturnedToZero && result.NativeAllocationProfile?.Passed != false ? 0 : 1;
}
finally { CorrectnessOracle.WriteFailure(options.Output); }
