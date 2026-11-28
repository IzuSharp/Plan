using System.Data.Common;
using System.Text;
using Microsoft.EntityFrameworkCore;

internal sealed partial class Workload : IDisposable
{
    internal static readonly string[] Names = ["numeric", "text", "money", "json", "wide", "optional-filter", "range", "left-join", "inner-join", "null-notes", "literal-note", "customer-totals", "product-totals", "empty-sum", "cursor", "offset", "exists", "in-subquery", "cte", "window", "union-all", "union", "intersect", "except", "running-total", "three-join", "anti-association", "nullable-order", "raw-sql", "related", "tx-commit", "tx-rollback", "partial-update", "stale-conflict", "early-stop"];
    private readonly Options _options;
    private readonly string[] _names;
    internal string[] ActiveNames => _names;
    private readonly DbConnection _session;
    private readonly string[] _sql = new string[Names.Length];
    private readonly OperationResult[] _expected = new OperationResult[Names.Length];
    private readonly DatabaseDriver _source;
    private readonly PerfContext _context;
    private readonly QueryPlan?[] _plans = new QueryPlan?[Names.Length];
    internal Dictionary<string,string> Sql => Names.Select((name,i) => (name, sql:_sql[i])).ToDictionary(pair=>pair.name,pair=>pair.sql);
    internal Dictionary<string,OperationResult> ExpectedResults => Names.Select((name,i)=>(name,result:_expected[i])).ToDictionary(pair=>pair.name,pair=>pair.result);
    internal Workload(DatabaseDriver source, DbConnection session, Options options)
    {
        _session=session; _options=options; _source=source; _context=source.CreateContext(session);
        _names=options.Cases??(options.Case=="mixed"?Names:[options.Case]);
        if (_names.Any(name=>!Names.Contains(name,StringComparer.Ordinal))) throw new ArgumentException("Unknown EF Core comparison contract.");
        if (options.Initialize) throw new ArgumentException("Initialize the common dataset through the Korda initializer first.");
        for (var index=0;index<5;index++)
        {
            var name=Names[index]; var digest=Digest.Create(); var count=Math.Min(options.Rows,options.OrdersPerTenant);
            for (long id=1;id<=count;id++)
            {
                if (name=="wide") digest.Integer(1);
                digest.Integer(id);
                if (name=="wide") { digest.Integer(1700000000+id/4); NullableInteger(ref digest, Customer(id)); }
                if (name is "money" or "wide") digest.Integer(100+(1009+id*37)%100000);
                if (name is "text" or "wide") digest.Text(id%5==0?null:"note-"+id%16);
                if (name=="wide") digest.Integer(1);
                if (name is "json" or "wide") { digest.Text(id%2==0?"web":"store"); digest.Boolean(id%11==0); }
                if (name=="wide") digest.Text(new string('m',id%17==0?2048:32));
            }
            _expected[index]=new(count,digest.Value,0);
        }
        InitializeAdvanced();
        InitializeLifecycle();
        for (var i = 0; i < Names.Length; i++)
        {
            if (i is >= 30 and <= 33) continue;
            _plans[i] = BuildPlan(_context, i);
            _sql[i] = _plans[i]!.Sql;
        }
    }
    private static long? Customer(long id) => id%7==0?null:id%10<7?1+id%8:9+id%248;
    internal int Index(long iteration) => Array.IndexOf(Names,_names[(int)(iteration%_names.Length)]);
    internal OperationResult Expected(int index) => _expected[index];
    internal OperationResult Expected(string name) => _expected[Array.IndexOf(Names,name)];
    internal string Name(long index) => Names[Index(index)];
    internal IReadOnlyDictionary<string,OperationResult> Expectations => ExpectedResults;
    internal ValueTask<OperationResult> Execute(string name, DbConnection? connection=null) => Execute(connection??_session,Array.IndexOf(Names,name));
    public void Dispose() => _context.Dispose();
    internal async ValueTask<OperationResult> Execute(DbConnection connection, int index)
    {
        if (_options.EmptyDriver) return _expected[index];
        if (ReferenceEquals(connection, _session))
        {
            if (index is >= 30 and <= 33) return await TransactionCase(_context, Names[index]);
            return await (_options.Mode == "prepared" ? _plans[index]! : BuildPlan(_context, index)).Execute();
        }
        await using var context = _source.CreateContext(connection);
        if (index is >= 30 and <= 33) return await TransactionCase(context, Names[index]);
        return await BuildPlan(context, index).Execute();
    }
    private static ValueTask<OperationResult> Read<T>(IAsyncEnumerable<T> stream, RowDigest<T> hash, int stopAfter = int.MaxValue)
        => ReadStream.Consume(stream, hash, stopAfter);

    private static void HashInteger(ref Digest digest,long value)=>digest.Integer(value);
    private static void HashText(ref Digest digest,TextRow value){digest.Integer(value.Id);digest.Text(value.Note);}
    private static void HashMoney(ref Digest digest,MoneyRow value){digest.Integer(value.Id);digest.Money(value.Total);}
    private static void HashJson(ref Digest digest,JsonRow value){digest.Integer(value.Id);digest.Text(value.Settings.Channel);digest.Boolean(value.Settings.Gift);}
    private static void NullableInteger(ref Digest digest,long? value){digest.Boolean(value.HasValue);if(value.HasValue)digest.Integer(value.Value);}
    private static void HashOrder(ref Digest digest,Order value)
    {
        digest.Integer(value.TenantId);digest.Integer(value.Id);digest.Integer(value.CreatedAt);NullableInteger(ref digest,value.CustomerId);
        digest.Money(value.Total);digest.Text(value.Note);digest.Integer(value.Version);digest.Text(value.Settings.Channel);digest.Boolean(value.Settings.Gift);digest.Text(value.InternalMemo);
    }
}
