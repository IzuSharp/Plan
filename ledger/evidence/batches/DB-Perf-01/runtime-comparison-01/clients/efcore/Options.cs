using System.Globalization;

internal sealed record Options
{
    internal string Connection { get; init; } = "";
    internal string Case { get; init; } = "numeric";
    internal string[]? Cases { get; init; }
    internal double Rate { get; init; }
    internal double IdleSeconds { get; init; }
    internal int QueueCapacity { get; init; } = 64;
    internal string Mode { get; init; } = "prepared";
    internal string SessionMode { get; init; } = "persistent";
    internal int Concurrency { get; init; } = 1;
    internal int Warmup { get; init; } = 64;
    internal int Rows { get; init; } = 32;
    internal int BatchRows { get; init; } = 32;
    internal int Tenants { get; init; } = 8;
    internal int OrdersPerTenant { get; init; } = 1024;
    internal long Operations { get; init; } = 1000;
    internal double Seconds { get; init; }
    internal bool Initialize { get; init; }
    internal bool Verify { get; init; }
    internal bool LifecycleChecks { get; init; }
    internal bool RecoveryChecks { get; init; }
    internal double RecoveryRate { get; init; } = 50;
    internal double RecoverySeconds { get; init; } = 2;
    internal double OverloadRate { get; init; } = 1000000;
    internal double OverloadSeconds { get; init; } = 2;
    internal bool EmptyDriver { get; init; }
    internal bool AllocationProfile { get; init; }
    internal string? NativeLibrary { get; init; }
    internal string? Output { get; init; }

    internal static Options Parse(string[] args)
    {
        var p = new Options();
        for (var i = 0; i < args.Length; i++)
        {
            string Value() => ++i < args.Length ? args[i] : throw new ArgumentException("Missing option value.");
            int Number() => int.Parse(Value(), CultureInfo.InvariantCulture);
            p = args[i] switch
            {
                "--connection" => p with { Connection = Value() },
                "--case" => p with { Case = Value() },
                "--cases" => p with { Cases = Value().Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries) },
                "--rate" or "--arrival-rate" => p with { Rate = double.Parse(Value(), CultureInfo.InvariantCulture) },
                "--idle-seconds" => p with { IdleSeconds = double.Parse(Value(), CultureInfo.InvariantCulture) },
                "--queue-capacity" => p with { QueueCapacity = Number() },
                "--mode" => p with { Mode = Value() },
                "--session" => p with { SessionMode = Value() },
                "--concurrency" => p with { Concurrency = Number() },
                "--warmup" => p with { Warmup = Number() },
                "--rows" => p with { Rows = Number() },
                "--batch-rows" => p with { BatchRows = Number() },
                "--tenants" => p with { Tenants = Number() },
                "--orders-per-tenant" => p with { OrdersPerTenant = Number() },
                "--operations" => p with { Operations = long.Parse(Value(), CultureInfo.InvariantCulture), Seconds = 0 },
                "--seconds" => p with { Seconds = double.Parse(Value(), CultureInfo.InvariantCulture), Operations = 0 },
                "--initialize" => p with { Initialize = true },
                "--verify" => p with { Verify = true },
                "--lifecycle-checks" => p with { LifecycleChecks = true },
                "--recovery-checks" => p with { RecoveryChecks = true },
                "--recovery-rate" => p with { RecoveryRate = double.Parse(Value(), CultureInfo.InvariantCulture) },
                "--recovery-seconds" => p with { RecoverySeconds = double.Parse(Value(), CultureInfo.InvariantCulture) },
                "--overload-rate" => p with { OverloadRate = double.Parse(Value(), CultureInfo.InvariantCulture) },
                "--overload-seconds" => p with { OverloadSeconds = double.Parse(Value(), CultureInfo.InvariantCulture) },
                "--empty-driver" => p with { EmptyDriver = true },
                "--allocation-profile" => p with { AllocationProfile = true },
                "--output" => p with { Output = Value() },
                "--native-library" => p with { NativeLibrary = Value() },
                _ => throw new ArgumentException("Unknown option " + args[i]),
            };
        }
        if (p.Connection.Length == 0) throw new ArgumentException("--connection must identify a dedicated DB-Perf-01 database.");
#if POSTGRES
        if(p.NativeLibrary is not null)throw new ArgumentException("--native-library applies only to SQLite; PostgreSQL uses managed Npgsql.");
#endif
        if (p.Mode is not ("dynamic" or "prepared")) throw new ArgumentException("--mode must be dynamic or prepared.");
        if (p.SessionMode is not ("persistent" or "per-operation")) throw new ArgumentException("--session must be persistent or per-operation.");
        if (p.Concurrency is < 1 or > 256 || p.Warmup is < 1 or > 100000 || p.Rows is < 1 or > 1000000
            || p.BatchRows is < 1 or > 4096 || p.Tenants is < 1 or > 1024 || p.OrdersPerTenant < 32
            || !double.IsFinite(p.Seconds) || p.Seconds < 0 || p.Seconds > 86400 || p.Operations < 0 || (!p.Initialize && p.Seconds == 0 && p.Operations == 0))
            throw new ArgumentOutOfRangeException(nameof(args), "Invalid or unbounded workload size.");
        if (!double.IsFinite(p.IdleSeconds) || p.IdleSeconds < 0 || p.IdleSeconds > 300
            || !double.IsFinite(p.Rate) || p.Rate < 0 || p.Rate > 1000000 || p.QueueCapacity is < 1 or > 65536
            || (p.Rate > 0 && p.Seconds <= 0) || p.Cases is { Length: 0 })
            throw new ArgumentException("Offered load needs finite --seconds and --rate; --cases must not be empty.");
        if (!double.IsFinite(p.RecoveryRate) || p.RecoveryRate is <= 0 or > 1000000
            || !double.IsFinite(p.OverloadRate) || p.OverloadRate is <= 0 or > 1000000
            || !double.IsFinite(p.RecoverySeconds) || p.RecoverySeconds is <= 0 or > 300
            || !double.IsFinite(p.OverloadSeconds) || p.OverloadSeconds is <= 0 or > 300
            || (p.RecoveryChecks && (p.SessionMode != "persistent" || p.EmptyDriver || p.LifecycleChecks || p.Initialize
                || p.Rate != 0 || p.OverloadRate <= p.RecoveryRate)))
            throw new ArgumentException("Recovery checks require real persistent sessions and dedicated bounded recovery/overload options.");
        if (p.AllocationProfile && (p.Initialize || p.LifecycleChecks || p.RecoveryChecks))
            throw new ArgumentException("Allocation profiling requires its separate steady workload process.");
        if (p.Initialize) throw new ArgumentException("Initialize the canonical dataset with its existing initializer; this comparison client never changes the schema.");
        if (p.LifecycleChecks || p.RecoveryChecks) throw new ArgumentException("This comparison client does not implement the separate historical lifecycle/recovery diagnostics.");
        return p;
    }
}
