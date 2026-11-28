using System.Data.Common;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using Microsoft.EntityFrameworkCore;
#if POSTGRES
using ProviderConnection = Npgsql.NpgsqlConnection;
#else
using ProviderConnection = Microsoft.Data.Sqlite.SqliteConnection;
#endif

internal sealed class DatabaseDriver : IAsyncDisposable
{
    private readonly string _connectionString;
    private int _connections;
    private int _independentStateChecks;
    internal int IndependentStateChecks => Volatile.Read(ref _independentStateChecks);
    internal void RecordIndependentStateCheck() => Interlocked.Increment(ref _independentStateChecks);
    internal RuntimeIdentity RuntimeIdentity { get; } = RuntimeIdentity.ReadAndValidate();
    internal string? NativePath { get; }
    internal string? NativeHash { get; }
    internal string DatabaseVersion { get; private set; } = "unknown";
    internal string[] CompileOptions { get; private set; } = [];
#if POSTGRES
    internal string Provider => "Npgsql";
#else
    internal string Provider => "Microsoft.Data.Sqlite.Core";
#endif

    internal DatabaseDriver(Options options)
    {
#if POSTGRES
        Npgsql.NpgsqlConnectionStringBuilder builder;
        if (options.Connection.StartsWith("postgresql://", StringComparison.Ordinal))
        {
            var uri = new Uri(options.Connection);
            var credentials = uri.UserInfo.Split(':', 2);
            builder = new()
            {
                Host = uri.Host, Port = uri.Port < 0 ? 5432 : uri.Port,
                Username = Uri.UnescapeDataString(credentials[0]),
                Password = credentials.Length == 2 ? Uri.UnescapeDataString(credentials[1]) : "",
                Database = Uri.UnescapeDataString(uri.AbsolutePath.Trim('/')),
                SslMode = Npgsql.SslMode.Disable
            };
        }
        else builder = new(options.Connection);
        builder.MaxPoolSize = options.Concurrency + 1;
        builder.MinPoolSize = 0;
        builder.Pooling = true;
        builder.MaxAutoPrepare = 0;
        _connectionString = builder.ConnectionString;
#else
        if (options.NativeLibrary is null)
            throw new ArgumentException("--native-library must select the exact baseline SQLite build.");
        var path = Path.GetFullPath(options.NativeLibrary);
        path = File.ResolveLinkTarget(path, returnFinalTarget: true)?.FullName ?? path;
        var handle = NativeLibrary.Load(path);
        NativeLibrary.SetDllImportResolver(typeof(SQLitePCL.SQLite3Provider_sqlite3).Assembly,
            (name, _, _) => name == "sqlite3" ? handle : nint.Zero);
        SQLitePCL.raw.SetProvider(new SQLitePCL.SQLite3Provider_sqlite3());
        var mapped = File.ReadLines("/proc/self/maps")
            .Select(line => line.Split(' ', 6, StringSplitOptions.RemoveEmptyEntries))
            .Where(parts => parts.Length == 6 && Path.GetFileName(parts[5]).StartsWith("libsqlite3.so", StringComparison.Ordinal))
            .Select(parts => parts[5]).Distinct(StringComparer.Ordinal).ToArray();
        if (mapped.Length != 1 || Path.GetFullPath(mapped[0]) != path)
            throw new InvalidOperationException("Selected SQLite library is not the sole actually mapped SQLite image.");
        NativePath = mapped[0];
        using (var file = File.OpenRead(NativePath)) NativeHash = Convert.ToHexStringLower(SHA256.HashData(file));
        var builder = new Microsoft.Data.Sqlite.SqliteConnectionStringBuilder
        {
            DataSource = options.Connection, Pooling = true, ForeignKeys = true, DefaultTimeout = 5
        };
        _connectionString = builder.ConnectionString;
#endif
    }

    internal PerfContext CreateContext(DbConnection connection)
    {
        var builder = new DbContextOptionsBuilder<PerfContext>();
#if POSTGRES
        builder.UseNpgsql(connection);
#else
        builder.UseSqlite(connection);
#endif
        builder.UseQueryTrackingBehavior(QueryTrackingBehavior.NoTracking);
        return new(builder.Options);
    }

    internal async Task<DbConnection> OpenSessionAsync()
    {
        var connection = new ProviderConnection(_connectionString);
        try
        {
            await connection.OpenAsync().ConfigureAwait(false);
#if !POSTGRES
            await using var command = connection.CreateCommand();
            command.CommandText = "PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=5000;";
            await command.ExecuteNonQueryAsync().ConfigureAwait(false);
#endif
            Interlocked.Increment(ref _connections);
            return connection;
        }
        catch { await connection.DisposeAsync(); throw; }
    }

    internal async ValueTask CloseSessionAsync(DbConnection connection)
    {
        await connection.DisposeAsync().ConfigureAwait(false);
        if (connection.State != System.Data.ConnectionState.Closed)
            throw new InvalidOperationException("Disposed provider connection remained open.");
        Interlocked.Decrement(ref _connections);
    }

    internal async Task VerifyDataset(Options options)
    {
        var connection = await OpenSessionAsync();
        try
        {
            DatabaseVersion = connection.ServerVersion;
            await using var command = connection.CreateCommand();
            command.CommandText = "SELECT tenants, orders_per_tenant FROM db_perf_metadata";
            await using (var reader = await command.ExecuteReaderAsync())
            {
                if (!await reader.ReadAsync() || reader.GetInt64(0) != options.Tenants
                    || reader.GetInt64(1) != options.OrdersPerTenant || await reader.ReadAsync())
                    throw CorrectnessOracle.Failure("Dataset metadata differs from requested oracle inputs.", "dataset");
            }
#if !POSTGRES
            command.CommandText = "PRAGMA compile_options";
            var compileOptions = new List<string>();
            await using var compileReader = await command.ExecuteReaderAsync();
            while (await compileReader.ReadAsync()) compileOptions.Add(compileReader.GetString(0));
            CompileOptions = compileOptions.Order(StringComparer.Ordinal).ToArray();
#endif
        }
        finally { await CloseSessionAsync(connection); }
    }

    internal OwnershipCounts Read() => new(Volatile.Read(ref _connections),
        "Application-owned logical provider connections; EF/driver internal ownership is unobservable.");

    public ValueTask DisposeAsync()
    {
#if POSTGRES
        Npgsql.NpgsqlConnection.ClearAllPools();
#else
        Microsoft.Data.Sqlite.SqliteConnection.ClearAllPools();
#endif
        return ValueTask.CompletedTask;
    }
}

internal sealed record OwnershipCounts(int ApplicationConnections, string Scope);
