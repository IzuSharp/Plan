using System.Data.Common;
using System.Linq.Expressions;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.EntityFrameworkCore;
#if POSTGRES
using StoredMoney = System.Decimal;
#else
using StoredMoney = System.Int64;
#endif

public sealed record OrderSettings(string Channel, bool Gift);
public sealed record TextRow(long Id, string? Note);
public sealed record MoneyRow(long Id, decimal Total);
public sealed record JsonRow(long Id, OrderSettings Settings);
public sealed record Order(long TenantId, long Id, long CreatedAt, long? CustomerId, decimal Total,
    string? Note, long Version, OrderSettings Settings, string InternalMemo);
public sealed record JoinRow(long Id, string? Name);
public sealed record CustomerTotal(long? CustomerId, long Count, decimal? Total);
public sealed record ProductTotal(string Product, long? Quantity);
public sealed record RankRow(long Id, long Rank);
public sealed record RunningRow(long Id, long? Quantity);
public sealed record DetailRow(long OrderId, string Name, string Product, long Quantity);
public sealed record OrderLine(long Id, long TenantId, long OrderId, string Product, long Quantity);

internal sealed class OrderEntity
{
    public long TenantId { get; set; }
    public long Id { get; set; }
    public long CreatedAt { get; set; }
    public long? CustomerId { get; set; }
    public StoredMoney Total { get; set; }
    public string? Note { get; set; }
    public long Version { get; set; }
    public OrderSettings Settings { get; set; } = null!;
    public string InternalMemo { get; set; } = "";
}

internal sealed class CustomerEntity
{
    public long Id { get; set; }
    public string Name { get; set; } = "";
    public string? Email { get; set; }
}

internal sealed class LineEntity
{
    public long Id { get; set; }
    public long TenantId { get; set; }
    public long OrderId { get; set; }
    public string Product { get; set; } = "";
    public long Quantity { get; set; }
}

internal sealed class PerfContext(DbContextOptions<PerfContext> options) : DbContext(options)
{
    internal DbSet<OrderEntity> Orders => Set<OrderEntity>();
    internal DbSet<CustomerEntity> Customers => Set<CustomerEntity>();
    internal DbSet<LineEntity> Lines => Set<LineEntity>();

    // The projection is shared unchanged by both runtime builds. SQLite keeps
    // integer cents through server aggregation; the final DTO conversion is exact.
    internal static readonly Expression<Func<OrderEntity, Order>> FullOrder = row => new(
        row.TenantId, row.Id, row.CreatedAt, row.CustomerId, Money(row.Total),
        row.Note, row.Version, row.Settings, row.InternalMemo);

    internal static decimal Money(StoredMoney value) =>
#if POSTGRES
        value;
#else
        value / 100m;
#endif

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        var orders = modelBuilder.Entity<OrderEntity>();
        orders.ToTable("orders").HasKey(row => new { row.TenantId, row.Id });
        orders.Property(row => row.TenantId).ValueGeneratedNever();
        orders.Property(row => row.Id).ValueGeneratedNever();
        orders.Property(row => row.Total).HasColumnType(
#if POSTGRES
            "numeric(18,2)"
#else
            "BIGINT"
#endif
        );
        orders.Property(row => row.Settings)
            .HasConversion(
                settings => JsonSerializer.Serialize(settings, PerfJson.Default.OrderSettings),
                json => JsonSerializer.Deserialize(json, PerfJson.Default.OrderSettings)!)
            .HasColumnType(
#if POSTGRES
                "jsonb"
#else
                "TEXT"
#endif
            );
        orders.Property(row => row.InternalMemo).IsRequired();
        var customers = modelBuilder.Entity<CustomerEntity>();
        customers.ToTable("customers").HasKey(row => row.Id);
        customers.Property(row => row.Id).ValueGeneratedNever();
        customers.Property(row => row.Name).IsRequired();
        var lines = modelBuilder.Entity<LineEntity>();
        lines.ToTable("order_lines").HasKey(row => row.Id);
        lines.Property(row => row.Id).ValueGeneratedNever();
        lines.Property(row => row.Product).IsRequired();
    }
}

[JsonSerializable(typeof(OrderSettings))]
[JsonSerializable(typeof(RunReceipt))]
[JsonSerializable(typeof(RuntimeIdentity))]
internal partial class PerfJson : JsonSerializerContext;
