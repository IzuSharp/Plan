internal sealed partial class Workload
{
    private void InitializeAdvanced()
    {
        foreach (var name in _options.Verify ? Names : _names)
        {
            if (name is "numeric" or "text" or "money" or "json" or "wide") continue;
            switch (name)
            {
                case "optional-filter": SetExpected(name, HashInteger, Ids().Where(id => Dataset.CustomerId(id) == 2).Take(_options.Rows)); break;
                case "range": SetExpected(name, HashInteger, Ids().Where(id => Dataset.CreatedAt(id) >= 1700000100 && Dataset.CreatedAt(id) < 1700000200).Take(_options.Rows)); break;
                case "null-notes": SetExpected(name, HashInteger, Ids().Where(id => Dataset.Note(id) is null).Take(_options.Rows)); break;
                case "literal-note": SetExpected(name, HashInteger, Ids().Where(id => Dataset.Note(id)?.Contains("note-1", StringComparison.Ordinal) == true).Take(_options.Rows)); break;
                case "left-join": SetExpected(name, HashJoin, Ids().Take(_options.Rows).Select(id => new JoinRow(id, Dataset.CustomerId(id) is { } customer ? Dataset.CustomerName(customer) : null))); break;
                case "inner-join": SetExpected(name, HashJoin, Ids().Where(id => Dataset.CustomerId(id).HasValue).Take(_options.Rows).Select(id => new JoinRow(id, Dataset.CustomerName(Dataset.CustomerId(id)!.Value)))); break;
                case "customer-totals":
                    var groups = Ids().GroupBy(Dataset.CustomerId).Where(group => group.Count() > 3)
                        .OrderBy(group => group.Key is null).ThenBy(group => group.Key)
                        .Select(group => new CustomerTotal(group.Key, group.LongCount(), group.Sum(id => Dataset.Cents(1, id)) / 100m));
                    SetExpected(name, HashCustomerTotal, groups); break;
                case "product-totals":
                    var products = Ids().SelectMany(id => Enumerable.Range(0, Dataset.Lines(id)).Select(line => (Product: Dataset.Product(id, line), Quantity: Dataset.Quantity(id, line))))
                        .GroupBy(item => item.Product, StringComparer.Ordinal).Where(group => group.Sum(item => item.Quantity) > 10)
                        .OrderBy(group => group.Key, StringComparer.Ordinal).Select(group => new ProductTotal(group.Key, group.Sum(item => item.Quantity)));
                    SetExpected(name, HashProductTotal, products); break;
                case "empty-sum": SetExpected<decimal?>(name, HashNullableMoney, [null]); break;
                case "cursor": SetExpected(name, HashInteger, Ids().Skip(_options.OrdersPerTenant / 2).Take(_options.Rows)); break;
                case "offset": SetExpected(name, HashInteger, Ids().Skip(_options.OrdersPerTenant * 3 / 4).Take(_options.Rows)); break;
                case "exists": SetExpected(name, HashInteger, new long[] { 1 }); break;
                case "in-subquery": SetExpected(name, HashInteger, Ids().Where(id => id > 128).Select(Dataset.CustomerId).Where(id => id.HasValue).Select(id => id!.Value).Distinct().Order().Take(_options.Rows)); break;
                case "cte": SetExpected(name, HashInteger, Ids().Where(id => id > 16).Take(_options.Rows)); break;
                case "window":
                    var ranks = new Dictionary<long, long>();
                    SetExpected(name, HashRank, Ids().Take(_options.Rows).Select(id =>
                    {
                        var key = Dataset.CustomerId(id) ?? -1; ranks.TryGetValue(key, out var rank); ranks[key] = ++rank;
                        return new RankRow(id, rank);
                    })); break;
                case "union-all": SetExpected(name, HashInteger,
                    Enumerable.Range(1, 16).Select(i => (long)i).Concat(Enumerable.Range(9, 16).Select(i => (long)i)).Order()); break;
                case "union": SetExpected(name, HashInteger, Enumerable.Range(1, 24).Select(i => (long)i)); break;
                case "intersect": SetExpected(name, HashInteger, Enumerable.Range(9, 8).Select(i => (long)i)); break;
                case "except": SetExpected(name, HashInteger, Enumerable.Range(1, 8).Select(i => (long)i)); break;
                case "running-total":
                    long lineId = 0, sum = 0;
                    SetExpected(name, HashRunning, Ids().SelectMany(id => Enumerable.Range(0, Dataset.Lines(id)).Select(line => new RunningRow(++lineId, sum += Dataset.Quantity(id, line)))).Take(_options.Rows)); break;
                case "three-join":
                    SetExpected(name, HashDetail, Ids().Where(id => Dataset.CustomerId(id).HasValue)
                        .SelectMany(id => Enumerable.Range(0, Dataset.Lines(id)).Select(line => new DetailRow(id, Dataset.CustomerName(Dataset.CustomerId(id)!.Value), Dataset.Product(id, line), Dataset.Quantity(id, line))))
                        .Take(_options.Rows)); break;
                case "anti-association": SetExpected(name, HashInteger, Ids().Where(id => Enumerable.Range(0, Dataset.Lines(id)).All(line => Dataset.Quantity(id, line) < 5)).Take(_options.Rows)); break;
                case "nullable-order": SetExpected(name, HashInteger, Ids().OrderBy(id => Dataset.CustomerId(id).HasValue).ThenBy(Dataset.CustomerId).ThenBy(id => id).Take(_options.Rows)); break;
                case "raw-sql":
                    
                    var textDigest = Digest.Create(); long textRows = 0;
                    foreach (var id in Ids().Take(_options.Rows)) { HashText(ref textDigest, new TextRow(id, Dataset.Note(id))); textRows++; }
                    _expected[Array.IndexOf(Names,name)] = new(textRows, textDigest.Value, 0); break;
                case "related":
                    var relationDigest = Digest.Create(); long relationRows = 0, relationLineId = 0;
                    for (long id = 1; id <= Math.Min(Math.Min(_options.Rows, _options.BatchRows), _options.OrdersPerTenant); id++)
                    {
                        relationDigest.Integer(id); relationDigest.Integer(Dataset.Lines(id));
                        for (var line = 0; line < Dataset.Lines(id); line++)
                        {
                            HashLine(ref relationDigest, new OrderLine(++relationLineId, 1, id, Dataset.Product(id, line), Dataset.Quantity(id, line)));
                            relationRows++;
                        }
                    }
                    _expected[Array.IndexOf(Names,name)] = new(relationRows, relationDigest.Value, 0); break;
            }
        }
    }

    private IEnumerable<long> Ids() => Enumerable.Range(1,_options.OrdersPerTenant).Select(i=>(long)i);
    private void SetExpected<T>(string name,RowDigest<T> hash,IEnumerable<T> rows)
    {
        var digest=Digest.Create();long count=0;foreach(var row in rows){hash(ref digest,row);count++;}
        _expected[Array.IndexOf(Names,name)]=new(count,digest.Value,0);
    }
    private static void HashJoin(ref Digest digest, JoinRow row) { digest.Integer(row.Id); digest.Text(row.Name); }
    private static void HashNullableMoney(ref Digest digest, decimal? value) { digest.Boolean(value.HasValue); if (value.HasValue) digest.Money(value.Value); }
    private static void HashCustomerTotal(ref Digest digest, CustomerTotal row) { NullableInteger(ref digest, row.CustomerId); digest.Integer(row.Count); HashNullableMoney(ref digest, row.Total); }
    private static void HashProductTotal(ref Digest digest, ProductTotal row) { digest.Text(row.Product); NullableInteger(ref digest, row.Quantity); }
    private static void HashRank(ref Digest digest, RankRow row) { digest.Integer(row.Id); digest.Integer(row.Rank); }
    private static void HashRunning(ref Digest digest, RunningRow row) { digest.Integer(row.Id); NullableInteger(ref digest, row.Quantity); }
    private static void HashDetail(ref Digest digest, DetailRow row) { digest.Integer(row.OrderId); digest.Text(row.Name); digest.Text(row.Product); digest.Integer(row.Quantity); }
    private static void HashLine(ref Digest digest, OrderLine row) { digest.Integer(row.Id); digest.Integer(row.TenantId); digest.Integer(row.OrderId); digest.Text(row.Product); digest.Integer(row.Quantity); }
}
