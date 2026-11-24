using System.Data.Common;
using System.Globalization;
using System.Runtime.CompilerServices;
using Dapper;
#if POSTGRESQL
using Npgsql;
#else
using Microsoft.Data.Sqlite;
#endif

[module: DapperAot]

internal static class Program
{
    private static async Task Main(string[] args)
    {
        if (RuntimeFeature.IsDynamicCodeSupported)
            throw new InvalidOperationException("This probe must be a real Native AOT executable.");
#if POSTGRESQL
        const string provider = "postgresql";
        await using var connection = new NpgsqlConnection(args[0]);
#else
        const string provider = "sqlite";
        SQLitePCL.raw.SetProvider(new SQLitePCL.SQLite3Provider_sqlite3());
        await using var connection = new SqliteConnection("Data Source=" + args[0] + ";Pooling=False");
#endif
        await connection.OpenAsync();
        await connection.ExecuteAsync("CREATE TABLE orm_probe (id BIGINT PRIMARY KEY, customer TEXT NOT NULL, note TEXT NULL, total DECIMAL(18,2) NOT NULL)");
        await using (var transaction = await connection.BeginTransactionAsync())
        {
            var rows = await connection.ExecuteAsync(
                "INSERT INTO orm_probe (id, customer, note, total) VALUES (@Id, @Customer, @Note, @Total)",
                new { Id = 101L, Customer = "Db-Perf Ω", Note = (string?)null, Total = 12.25m }, transaction);
            if (rows != 1) throw new InvalidOperationException("Insert row count mismatch.");
            await transaction.CommitAsync();
        }
        var result = await connection.QuerySingleAsync<ProbeRow>(
            "SELECT id AS Id, customer AS Customer, note AS Note, total AS Total FROM orm_probe WHERE id = @Id",
            new { Id = 101L });
        Check(result);
        long streamedRows = 0;
        await foreach (var row in connection.QueryUnbufferedAsync<ProbeRow>(
            "SELECT id AS Id, customer AS Customer, note AS Note, total AS Total FROM orm_probe WHERE id = @Id",
            new { Id = 101L }))
        {
            Check(row);
            streamedRows++;
        }
        if (streamedRows != 1) throw new InvalidOperationException("Stream row count mismatch.");
        await using (var transaction = await connection.BeginTransactionAsync())
        {
            await connection.ExecuteAsync("UPDATE orm_probe SET customer = @Customer WHERE id = @Id",
                new { Customer = "rollback", Id = 101L }, transaction);
            await transaction.RollbackAsync();
        }
        var persisted = connection.QuerySingle<ProbeRow>(
            "SELECT id AS Id, customer AS Customer, note AS Note, total AS Total FROM orm_probe WHERE id = @Id",
            new { Id = 101L });
        Check(persisted);
        Console.WriteLine("ORM_PROBE provider=" + provider
            + " aot=" + (!RuntimeFeature.IsDynamicCodeSupported).ToString().ToLowerInvariant()
            + " driver=" + connection.GetType().Assembly.GetName().Version
            + " database=" + connection.ServerVersion
            + " rows=" + streamedRows.ToString(CultureInfo.InvariantCulture)
            + " typed_id=" + result.Id.ToString(CultureInfo.InvariantCulture)
            + " typed_decimal=" + result.Total.ToString(CultureInfo.InvariantCulture)
            + " nullable=true unicode=true async_materialization=true async_enumeration=true sync_materialization=true commit=true rollback=true");
        await connection.ExecuteAsync("DROP TABLE orm_probe");
    }

    private static void Check(ProbeRow row)
    {
        if (row.Id != 101L || row.Customer != "Db-Perf Ω" || row.Note is not null || row.Total != 12.25m)
            throw new InvalidOperationException("Actual mapped result differs from expected state.");
    }
}

public sealed class ProbeRow
{
    public long Id { get; set; }
    public string Customer { get; set; } = "";
    public string? Note { get; set; }
    public decimal Total { get; set; }
}
