using System.Data;
using System.Data.Common;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using Dapper;
#if POSTGRES
using ProviderConnection = Npgsql.NpgsqlConnection;
#else
using ProviderConnection = Microsoft.Data.Sqlite.SqliteConnection;
#endif

internal sealed class PhaseDriver : IAsyncDisposable
{
    internal DbConnection Connection { get; }
    internal string? NativePath { get; }
    internal string? NativeSha256 { get; }
    internal string[] CompileOptions { get; private set; } = [];
    internal string DatabaseVersion { get; private set; } = "unknown";
    internal bool ConnectionClosed => Connection.State == ConnectionState.Closed;
#if POSTGRES
    internal const string KordaProvider = "PostgreSql";
    internal const string Provider = "Npgsql";
#else
    internal const string KordaProvider = "Sqlite";
    internal const string Provider = "Microsoft.Data.Sqlite.Core";
#endif

    internal PhaseDriver(Options options)
    {
#if POSTGRES
        Npgsql.NpgsqlConnectionStringBuilder builder;
        if (options.Connection.StartsWith("postgresql://", StringComparison.Ordinal)
            || options.Connection.StartsWith("postgres://", StringComparison.Ordinal))
        {
            var uri = new Uri(options.Connection);
            var user = uri.UserInfo.Split(':', 2);
            builder = new() { Host = uri.Host, Port = uri.Port < 0 ? 5432 : uri.Port,
                Username = Uri.UnescapeDataString(user[0]), Database = Uri.UnescapeDataString(uri.AbsolutePath.Trim('/')),
                SslMode = Npgsql.SslMode.Disable };
            if (user.Length == 2) builder.Password = Uri.UnescapeDataString(user[1]);
        }
        else builder = new(options.Connection);
        builder.Pooling = true; builder.MaxPoolSize = 1; builder.MinPoolSize = 0; builder.MaxAutoPrepare = 0;
        Connection = new ProviderConnection(builder.ConnectionString);
#else
        if (options.NativeLibrary is null)
            throw new ArgumentException("SQLite requires --native-library with the exact matching libsqlite3.so.");
        var path = Path.GetFullPath(options.NativeLibrary);
        var handle = NativeLibrary.Load(path);
        NativeLibrary.SetDllImportResolver(typeof(SQLitePCL.SQLite3Provider_sqlite3).Assembly,
            (name, _, _) => name == "sqlite3" ? handle : nint.Zero);
        SQLitePCL.raw.SetProvider(new SQLitePCL.SQLite3Provider_sqlite3());
        var mapped = File.ReadLines("/proc/self/maps").Select(line => line.Split(' ', 6, StringSplitOptions.RemoveEmptyEntries))
            .Where(parts => parts.Length == 6 && Path.GetFileName(parts[5]) == "libsqlite3.so")
            .Select(parts => parts[5]).Distinct().ToArray();
        if (mapped.Length != 1 || Path.GetFullPath(mapped[0]) != path)
            throw new InvalidOperationException("The selected SQLite library is not the sole actually mapped sqlite3 image.");
        NativePath = mapped[0]; NativeSha256 = Hash(NativePath);
        var builder = new Microsoft.Data.Sqlite.SqliteConnectionStringBuilder
        { DataSource = options.Connection, Pooling = true, ForeignKeys = true, DefaultTimeout = 5 };
        Connection = new ProviderConnection(builder.ConnectionString);
#endif
    }

    internal async Task Open()
    {
        await Connection.OpenAsync();
#if POSTGRES
        await Connection.ExecuteAsync("SET timezone TO 'UTC'");
        DatabaseVersion = await Connection.QuerySingleAsync<string>("SELECT version()") ?? throw new InvalidOperationException("Missing server version.");
#else
        await Connection.ExecuteAsync("PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=5000;");
        DatabaseVersion = await Connection.QuerySingleAsync<string>("SELECT sqlite_version()") ?? throw new InvalidOperationException("Missing SQLite version.");
        CompileOptions = Connection.Query<string>("PRAGMA compile_options").Order(StringComparer.Ordinal).ToArray();
#endif
    }

    internal async Task Initialize()
    {
        await Connection.ExecuteAsync("CREATE TABLE query_phases (\"TenantId\" BIGINT NOT NULL, \"Id\" BIGINT NOT NULL, \"Note\" TEXT NULL, PRIMARY KEY(\"TenantId\",\"Id\"))");
        await using var transaction = await Connection.BeginTransactionAsync();
        for (var tenant = 1; tenant <= 2; tenant++)
        {
            var sql = new StringBuilder("INSERT INTO query_phases VALUES ");
            for (var id = 1; id <= 1000; id++)
            {
                if (id > 1) sql.Append(',');
                sql.Append('(').Append(tenant).Append(',').Append(id).Append(',');
                if (id % 5 == 0) sql.Append("NULL");
                else sql.Append("'note-").Append(tenant).Append('-').Append(id).Append('\'');
                sql.Append(')');
            }
            await Connection.ExecuteAsync(sql.ToString(), transaction: transaction);
        }
        await transaction.CommitAsync();
        await transaction.DisposeAsync();
        await Connection.ExecuteAsync("ANALYZE query_phases");
    }

    internal static string Hash(string path)
    { using var file = File.OpenRead(path); return Convert.ToHexStringLower(SHA256.HashData(file)); }

    internal static DependencyVersion[] Versions =>
        [Version("Dapper", typeof(SqlMapper).Assembly), Version("Dapper.AOT", typeof(CommandFactory).Assembly),
         Version(Provider, typeof(ProviderConnection).Assembly)];
    private static DependencyVersion Version(string name, Assembly assembly) => new(name,
        assembly.GetName().Version?.ToString() ?? "unknown",
        assembly.GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion ?? "unknown");

    public async ValueTask DisposeAsync()
    {
        await Connection.DisposeAsync();
        ProviderConnection.ClearAllPools();
    }
}
