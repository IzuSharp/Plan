using System.Globalization;
using System.Security.Cryptography;
using System.Text.Json;

internal sealed record Options(string Connection, string Output, string KordaReceipt, string? NativeLibrary,
    int Rows, int Iterations, int Windows, bool Initialize)
{
    internal static Options Parse(string[] args)
    {
        string? connection = null, output = null, receipt = null, native = null;
        var rows = 100; var iterations = 256; var windows = 3; var initialize = false;
        for (var i = 0; i < args.Length; i++)
        {
            string Value() => ++i < args.Length ? args[i] : throw new ArgumentException("Missing value for " + args[i - 1]);
            switch (args[i])
            {
                case "--connection": connection = Value(); break;
                case "--output": output = Path.GetFullPath(Value()); break;
                case "--korda-receipt": receipt = Path.GetFullPath(Value()); break;
                case "--native-library": native = Path.GetFullPath(Value()); break;
                case "--rows": rows = int.Parse(Value(), CultureInfo.InvariantCulture); break;
                case "--iterations": iterations = int.Parse(Value(), CultureInfo.InvariantCulture); break;
                case "--windows": windows = int.Parse(Value(), CultureInfo.InvariantCulture); break;
                case "--initialize": initialize = true; break;
                default: throw new ArgumentException("Unknown option: " + args[i]);
            }
        }
        if (string.IsNullOrEmpty(connection) || output is null || receipt is null)
            throw new ArgumentException("--connection, --output and --korda-receipt are required.");
        if (rows is not (1 or 100 or 1000) || iterations is < 1 or > 100000 || windows is < 1 or > 30)
            throw new ArgumentOutOfRangeException(nameof(args));
        if (File.Exists(output) || File.Exists(output + ".failure.json"))
            throw new ArgumentException("Use a new output path; prior evidence must remain intact.");
        return new(connection, output, receipt, native, rows, iterations, windows, initialize);
    }

    internal QueryContract ReadContract()
    {
        var bytes = File.ReadAllBytes(KordaReceipt);
        using var json = JsonDocument.Parse(bytes);
        var root = json.RootElement;
        var template = Rows == 1 ? PhaseSql.PrimaryKey : PhaseSql.Many;
        if (!root.GetProperty("NativeAot").GetBoolean() || root.GetProperty("SchemaVersion").GetInt32() != 3
            || root.GetProperty("Provider").GetString() != PhaseDriver.KordaProvider
            || root.GetProperty("ResultRows").GetInt32() != Rows
            || root.GetProperty("RawTemplate").GetString() != template)
            throw new InvalidOperationException("The actual Korda phase receipt does not match this provider, SQL or result shape.");
        return new(KordaReceipt, Convert.ToHexStringLower(SHA256.HashData(bytes)),
            root.GetProperty("ExecutableSha256").GetString()!, root.GetProperty("Sql").GetString()!, template);
    }
}

internal static class PhaseSql
{
    // Exact RawTemplate from both providers' actual query-phases receipts.
    // Keep these compile-time constants so Dapper.AOT generates fixed factories.
    internal const string PrimaryKey = """SELECT "query_phases"."Id" AS "Id", "query_phases"."Note" AS "Note" FROM "query_phases" WHERE "query_phases"."TenantId" = @tenant AND "query_phases"."Id" = @id ORDER BY "query_phases"."Id" ASC NULLS LAST""";
    internal const string Many = """SELECT "query_phases"."Id" AS "Id", "query_phases"."Note" AS "Note" FROM "query_phases" WHERE "query_phases"."TenantId" = @tenant AND "query_phases"."Id" <= @id ORDER BY "query_phases"."Id" ASC NULLS LAST""";
}
