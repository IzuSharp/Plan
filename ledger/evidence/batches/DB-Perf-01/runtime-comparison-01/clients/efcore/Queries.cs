using Microsoft.EntityFrameworkCore;

internal sealed partial class Workload
{
    internal static string ModeContract(string name, string mode)
    {
        var reuse = mode == "prepared"
            ? "Reuse IQueryable graph per worker; ordinary EF compiled query cache"
            : "Rebuild IQueryable graph per operation; ordinary EF query cache remains enabled";
        return name switch
        {
            "window" or "running-total" => "Explicit EF Database.SqlQuery SQL exception for a window expression; typed EF materialization; " + reuse,
            "raw-sql" => "Contract deliberately requests parameterized raw SQL through EF Database.SqlQuery; " + reuse,
            "cte" => "Equivalent Fluent filtered derived query; SQL need not retain the original CTE spelling; " + reuse,
            "related" => "Fluent fixed contiguous parent-key range; one ordered child query; buffered DTO grouping retains empty parents; " + reuse,
            "empty-sum" => "Fluent grouped SUM plus a nullable scalar default for no group; preserves SQL empty-SUM NULL; " + reuse,
            "early-stop" => "Full typed Order query limited to OrdersPerTenant; consumer disposes after three rows; " + reuse,
            _ => "Fluent IQueryable with no tracking and typed DTO/scalar projection; " + reuse
        };
    }

    private abstract class QueryPlan
    {
        internal abstract string Sql { get; }
        internal abstract ValueTask<OperationResult> Execute();
    }

    private sealed class StreamPlan<T>(IQueryable<T> query, RowDigest<T> hash, int stopAfter = int.MaxValue) : QueryPlan
    {
        internal override string Sql => query.ToQueryString();
        internal override ValueTask<OperationResult> Execute()
            => Read(query.AsAsyncEnumerable(), hash, stopAfter);
    }

    private sealed class EmptySumPlan(IQueryable<decimal?> query) : QueryPlan
    {
        internal override string Sql => query.ToQueryString();
        internal override async ValueTask<OperationResult> Execute()
        {
            // EF SumAsync normally coalesces empty input to zero. Grouping emits
            // no group for empty input; the nullable scalar default is SQL NULL.
            var pending = query.SingleOrDefaultAsync();
            var suspensions = pending.IsCompleted ? 0 : 1;
            var value = await pending.ConfigureAwait(false);
            var digest = Digest.Create();
            HashNullableMoney(ref digest, value);
            return new(1, digest.Value, suspensions);
        }
    }

    private sealed class RelatedPlan(IQueryable<OrderLine> query, int parentCount) : QueryPlan
    {
        internal override string Sql => query.ToQueryString();
        internal override async ValueTask<OperationResult> Execute()
        {
            var pending = query.ToArrayAsync();
            var suspensions = pending.IsCompleted ? 0 : 1;
            var children = await pending.ConfigureAwait(false);
            var groups = new List<OrderLine>[parentCount];
            foreach (var child in children)
            {
                var index = checked((int)child.OrderId - 1);
                if ((uint)index >= (uint)parentCount || child.TenantId != 1)
                    throw CorrectnessOracle.Failure("Related query returned an unrequested parent.", "related");
                (groups[index] ??= []).Add(child);
            }
            var digest = Digest.Create();
            for (var i = 0; i < parentCount; i++)
            {
                digest.Integer(i + 1);
                digest.Integer(groups[i]?.Count ?? 0);
                if (groups[i] is { } group)
                {
                    long previous = 0;
                    foreach (var child in group)
                    {
                        if (child.Id <= previous)
                            throw CorrectnessOracle.Failure("Related child order was not increasing.", "related");
                        previous = child.Id;
                        HashLine(ref digest, child);
                    }
                }
            }
            return new(children.LongLength, digest.Value, suspensions);
        }
    }

    private QueryPlan BuildPlan(PerfContext context, int index)
    {
        var tenant = 1L;
        var take = _options.Rows;
        var orders = context.Orders.AsNoTracking().Where(row => row.TenantId == tenant);
        switch (Names[index])
        {
            case "numeric":
                return new StreamPlan<long>(orders.OrderBy(row => row.Id).Take(take).Select(row => row.Id), HashInteger);
            case "text":
                return new StreamPlan<TextRow>(orders.OrderBy(row => row.Id).Take(take)
                    .Select(row => new TextRow(row.Id, row.Note)), HashText);
            case "money":
                return new StreamPlan<MoneyRow>(orders.OrderBy(row => row.Id).Take(take)
                    .Select(row => new MoneyRow(row.Id, PerfContext.Money(row.Total))), HashMoney);
            case "json":
                return new StreamPlan<JsonRow>(orders.OrderBy(row => row.Id).Take(take)
                    .Select(row => new JsonRow(row.Id, row.Settings)), HashJson);
            case "wide":
                return new StreamPlan<Order>(orders.OrderBy(row => row.Id).Take(take).Select(PerfContext.FullOrder), HashOrder);
            case "optional-filter":
                var customer = 2L;
                return new StreamPlan<long>(orders.Where(row => row.CustomerId == customer)
                    .OrderBy(row => row.Id).Take(take).Select(row => row.Id), HashInteger);
            case "range":
                var start = 1_700_000_100L;
                var end = 1_700_000_200L;
                return new StreamPlan<long>(orders.Where(row => row.CreatedAt >= start && row.CreatedAt < end)
                    .OrderBy(row => row.Id).Take(take).Select(row => row.Id), HashInteger);
            case "left-join":
                return new StreamPlan<JoinRow>(orders
                    .GroupJoin(context.Customers.AsNoTracking(), row => row.CustomerId, row => (long?)row.Id,
                        (order, customers) => new { Order = order, Customers = customers })
                    .SelectMany(pair => pair.Customers.DefaultIfEmpty(),
                        (pair, customerRow) => new { pair.Order.Id, Name = customerRow == null ? null : customerRow.Name })
                    .OrderBy(row => row.Id).Take(take).Select(row => new JoinRow(row.Id, row.Name)), HashJoin);
            case "inner-join":
                return new StreamPlan<JoinRow>(orders
                    .Join(context.Customers.AsNoTracking(), row => row.CustomerId, row => (long?)row.Id,
                        (order, customerRow) => new { order.Id, customerRow.Name })
                    .OrderBy(row => row.Id).Take(take).Select(row => new JoinRow(row.Id, row.Name)), HashJoin);
            case "null-notes":
                return new StreamPlan<long>(orders.Where(row => row.Note == null)
                    .OrderBy(row => row.Id).Take(take).Select(row => row.Id), HashInteger);
            case "literal-note":
                var pattern = "%note-1%";
                return new StreamPlan<long>(orders.Where(row => EF.Functions.Like(row.Note!, pattern, "\\"))
                    .OrderBy(row => row.Id).Take(take).Select(row => row.Id), HashInteger);
            case "customer-totals":
                return new StreamPlan<CustomerTotal>(orders.GroupBy(row => row.CustomerId)
                    .Select(group => new { CustomerId = group.Key, Count = group.LongCount(), Total = group.Sum(row => row.Total) })
                    .Where(group => group.Count > 3)
                    .OrderBy(group => group.CustomerId == null).ThenBy(group => group.CustomerId)
                    .Select(group => new CustomerTotal(group.CustomerId, group.Count, PerfContext.Money(group.Total))), HashCustomerTotal);
            case "product-totals":
                return new StreamPlan<ProductTotal>(context.Lines.AsNoTracking().Where(row => row.TenantId == tenant)
                    .GroupBy(row => row.Product)
                    .Select(group => new { Product = group.Key, Quantity = group.Sum(row => row.Quantity) })
                    .Where(group => group.Quantity > 10).OrderBy(group => group.Product)
                    .Select(group => new ProductTotal(group.Product, group.Quantity)), HashProductTotal);
            case "empty-sum":
                var absentTenant = -1L;
                return new EmptySumPlan(context.Orders.AsNoTracking().Where(row => row.TenantId == absentTenant)
                    .GroupBy(row => row.TenantId)
                    .Select(group => (decimal?)PerfContext.Money(group.Sum(row => row.Total))));
            case "cursor":
                var afterId = (long)(_options.OrdersPerTenant / 2);
                var afterCreated = Dataset.CreatedAt(afterId);
                return new StreamPlan<long>(orders.Where(row => row.CreatedAt > afterCreated
                        || (row.CreatedAt == afterCreated && (row.TenantId > tenant
                            || (row.TenantId == tenant && row.Id > afterId))))
                    .OrderBy(row => row.CreatedAt).ThenBy(row => row.TenantId).ThenBy(row => row.Id)
                    .Take(take).Select(row => row.Id), HashInteger);
            case "offset":
                return new StreamPlan<long>(orders.OrderBy(row => row.CreatedAt).ThenBy(row => row.TenantId)
                    .ThenBy(row => row.Id).Skip(_options.OrdersPerTenant * 3 / 4).Take(take).Select(row => row.Id), HashInteger);
            case "exists":
                return new StreamPlan<long>(context.Customers.AsNoTracking()
                    .Where(_ => context.Orders.Any(row => row.TenantId == tenant && row.Id >= 32))
                    .OrderBy(row => row.Id).Take(1).Select(row => row.Id), HashInteger);
            case "in-subquery":
                return new StreamPlan<long>(context.Customers.AsNoTracking()
                    .Where(customerRow => orders.Where(row => row.Id > 128).Select(row => row.CustomerId).Contains(customerRow.Id))
                    .OrderBy(row => row.Id).Take(take).Select(row => row.Id), HashInteger);
            case "cte":
                // SQL-equivalent filtered derived query. No recursive CTE or
                // materialization boundary exists in the original contract.
                return new StreamPlan<long>(orders.Where(row => row.Id > 16).Select(row => row.Id)
                    .OrderBy(id => id).Take(take), HashInteger);
            case "window":
                return new StreamPlan<RankRow>(context.Database.SqlQuery<RankRow>($"""
                    SELECT "Id", ROW_NUMBER() OVER (
                        PARTITION BY "CustomerId" ORDER BY "CreatedAt" ASC NULLS LAST, "Id" ASC NULLS LAST) AS "Rank"
                    FROM orders WHERE "TenantId"={tenant} ORDER BY "Id" ASC NULLS LAST LIMIT {take}
                    """), HashRank);
            case "union-all":
                return new StreamPlan<long>(orders.Where(row => row.Id <= 16).Select(row => row.Id)
                    .Concat(orders.Where(row => row.Id >= 9 && row.Id <= 24).Select(row => row.Id)).OrderBy(id => id), HashInteger);
            case "union":
                return new StreamPlan<long>(orders.Where(row => row.Id <= 16).Select(row => row.Id)
                    .Union(orders.Where(row => row.Id >= 9 && row.Id <= 24).Select(row => row.Id)).OrderBy(id => id), HashInteger);
            case "intersect":
                return new StreamPlan<long>(orders.Where(row => row.Id <= 16).Select(row => row.Id)
                    .Intersect(orders.Where(row => row.Id >= 9 && row.Id <= 24).Select(row => row.Id)).OrderBy(id => id), HashInteger);
            case "except":
                return new StreamPlan<long>(orders.Where(row => row.Id <= 16).Select(row => row.Id)
                    .Except(orders.Where(row => row.Id >= 9 && row.Id <= 24).Select(row => row.Id)).OrderBy(id => id), HashInteger);
            case "running-total":
                return new StreamPlan<RunningRow>(context.Database.SqlQuery<RunningRow>($"""
                    SELECT "Id", SUM("Quantity") OVER (
                        ORDER BY "Id" ASC NULLS LAST ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS "Quantity"
                    FROM order_lines WHERE "TenantId"={tenant} ORDER BY "Id" ASC NULLS LAST LIMIT {take}
                    """), HashRunning);
            case "three-join":
                return new StreamPlan<DetailRow>(orders
                    .Join(context.Customers.AsNoTracking(), row => row.CustomerId, row => (long?)row.Id,
                        (order, customerRow) => new { Order = order, Customer = customerRow })
                    .Join(context.Lines.AsNoTracking(), row => new { row.Order.TenantId, OrderId = row.Order.Id },
                        row => new { row.TenantId, row.OrderId }, (pair, line) => new { pair.Order.Id, pair.Customer.Name, Line = line })
                    .OrderBy(row => row.Id).ThenBy(row => row.Line.Id).Take(take)
                    .Select(row => new DetailRow(row.Id, row.Name, row.Line.Product, row.Line.Quantity)), HashDetail);
            case "anti-association":
                return new StreamPlan<long>(orders.Where(row => !context.Lines
                        .Where(line => line.TenantId == tenant && line.Quantity >= 5)
                        .Select(line => line.OrderId).Contains(row.Id))
                    .OrderBy(row => row.Id).Take(take).Select(row => row.Id), HashInteger);
            case "nullable-order":
                // This case explicitly specifies NULLS FIRST, unlike customer-totals.
                return new StreamPlan<long>(orders.OrderBy(row => row.CustomerId != null)
                    .ThenBy(row => row.CustomerId).ThenBy(row => row.Id).Take(take).Select(row => row.Id), HashInteger);
            case "raw-sql":
                return new StreamPlan<TextRow>(context.Database.SqlQuery<TextRow>($"""
                    SELECT "Id", "Note" FROM orders WHERE "TenantId"={tenant} ORDER BY "Id" LIMIT {take}
                    """), HashText);
            case "related":
                var parentCount = Math.Min(Math.Min(take, _options.BatchRows), _options.OrdersPerTenant);
                return new RelatedPlan(context.Lines.AsNoTracking()
                    .Where(row => row.TenantId == tenant && row.OrderId >= 1 && row.OrderId <= parentCount)
                    .OrderBy(row => row.OrderId).ThenBy(row => row.Id)
                    .Select(row => new OrderLine(row.Id, row.TenantId, row.OrderId, row.Product, row.Quantity)), parentCount);
            case "early-stop":
                return new StreamPlan<Order>(orders.OrderBy(row => row.Id).Take(_options.OrdersPerTenant)
                    .Select(PerfContext.FullOrder), HashOrder, stopAfter: 3);
            default:
                throw new ArgumentOutOfRangeException(nameof(index), Names[index]);
        }
    }
}
