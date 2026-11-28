using System.Data;
using Microsoft.EntityFrameworkCore;

internal sealed partial class Workload
{
    private static Order SeedOrder(long id) => new(1, id, Dataset.CreatedAt(id), Dataset.CustomerId(id), Dataset.Cents(1, id) / 100m,
        Dataset.Note(id), 1, new(Dataset.Channel(id), Dataset.Gift(id)), new string('m', id % 17 == 0 ? 2048 : 32));

    private void InitializeLifecycle()
    {
        foreach (var name in _options.Verify ? Names : _names)
        {
            if (name is not ("tx-commit" or "tx-rollback" or "partial-update" or "stale-conflict" or "early-stop")) continue;
            var index = Array.IndexOf(Names, name);
            var digest = Digest.Create();
            if (name == "early-stop")
            {
                for (long id = 1; id <= 3; id++) HashOrder(ref digest, SeedOrder(id));
                _expected[index] = new(3, digest.Value, 0);
                continue;
            }
            _sql[index] = "EF BeginTransaction; full no-tracking DTO read; ExecuteUpdateAsync; affected-row checks; restore/rollback; final full DTO read. See case contract.";
            var original = SeedOrder(_options.OrdersPerTenant);
            HashOrder(ref digest, original);
            if (name == "stale-conflict")
            {
                digest.Boolean(true);
                HashOrder(ref digest, original);
                _expected[index] = new(2, digest.Value, 0);
            }
            else
            {
                var changed = name == "partial-update" ? original with { Note = null } : original with { Note = "perf-mutated", Version = 2 };
                HashOrder(ref digest, changed);
                HashOrder(ref digest, original);
                _expected[index] = new(3, digest.Value, 0);
            }
        }
    }

    private IQueryable<OrderEntity> Target(PerfContext context)
    {
        var id = (long)_options.OrdersPerTenant;
        return context.Orders.AsNoTracking().Where(row => row.TenantId == 1 && row.Id == id);
    }

    private async ValueTask<OperationResult> TransactionCase(PerfContext context, string name)
    {
        var digest = Digest.Create();
        long suspensions = 0;
        var target = Target(context);
#if POSTGRES
        var begin = context.Database.BeginTransactionAsync(IsolationLevel.ReadCommitted);
#else
        var begin = context.Database.BeginTransactionAsync(IsolationLevel.Serializable);
#endif
        if (!begin.IsCompleted) suspensions++;
        var transaction = await begin.ConfigureAwait(false);
        Order original;
        try
        {
            var find = target.Select(PerfContext.FullOrder).SingleAsync();
            if (!find.IsCompleted) suspensions++;
            original = await find.ConfigureAwait(false);
            if (original != SeedOrder(_options.OrdersPerTenant))
                throw CorrectnessOracle.Failure("Write target differs from fixed initial state.", name);
            HashOrder(ref digest, original);

            Task<int> update;
            if (name == "stale-conflict")
                update = target.Where(row => row.Version == 1)
                    .ExecuteUpdateAsync(setters => setters.SetProperty(row => row.Note, "perf-mutated").SetProperty(row => row.Version, 2L));
            else if (name == "partial-update")
                update = target.ExecuteUpdateAsync(setters => setters.SetProperty(row => row.Note, (string?)null));
            else
                update = target.ExecuteUpdateAsync(setters => setters.SetProperty(row => row.Note, "perf-mutated").SetProperty(row => row.Version, 2L));
            if (!update.IsCompleted) suspensions++;
            if (await update.ConfigureAwait(false) != 1)
                throw CorrectnessOracle.Failure("Mutation did not affect exactly one order.", name);

            if (name == "stale-conflict")
            {
                var caught = false;
                try
                {
                    var stale = target.Where(row => row.Version == 1)
                        .ExecuteUpdateAsync(setters => setters.SetProperty(row => row.Note, "stale-write"));
                    if (!stale.IsCompleted) suspensions++;
                    if (await stale.ConfigureAwait(false) == 0) throw new DbUpdateConcurrencyException("The fixed stale version was rejected.");
                }
                catch (DbUpdateConcurrencyException) { caught = true; }
                if (!caught) throw CorrectnessOracle.Failure("A stale optimistic write was accepted.", name);
                digest.Boolean(true);
                var rollback = transaction.RollbackAsync();
                if (!rollback.IsCompleted) suspensions++;
                await rollback.ConfigureAwait(false);
            }
            else
            {
                var check = target.Select(PerfContext.FullOrder).SingleAsync();
                if (!check.IsCompleted) suspensions++;
                var changed = await check.ConfigureAwait(false);
                var expected = name == "partial-update" ? original with { Note = null } : original with { Note = "perf-mutated", Version = 2 };
                if (changed != expected)
                    throw CorrectnessOracle.Failure("Partial mutation changed omitted fields or lost NULL.", name);
                HashOrder(ref digest, changed);
                if (name == "tx-rollback")
                {
                    var rollback = transaction.RollbackAsync();
                    if (!rollback.IsCompleted) suspensions++;
                    await rollback.ConfigureAwait(false);
                }
                else
                {
                    var restore = name == "partial-update"
                        ? target.ExecuteUpdateAsync(setters => setters.SetProperty(row => row.Note, original.Note))
                        : target.ExecuteUpdateAsync(setters => setters.SetProperty(row => row.Note, original.Note)
                            .SetProperty(row => row.Version, original.Version));
                    if (!restore.IsCompleted) suspensions++;
                    if (await restore.ConfigureAwait(false) != 1)
                        throw CorrectnessOracle.Failure("Restore did not affect exactly one order.", name);
                    var commit = transaction.CommitAsync();
                    if (!commit.IsCompleted) suspensions++;
                    await commit.ConfigureAwait(false);
                }
            }
        }
        catch (Exception error) { CorrectnessOracle.ObserveContractFailure(error, name); throw; }
        finally
        {
            try
            {
                var retire = transaction.DisposeAsync();
                if (!retire.IsCompleted) suspensions++;
                await retire.ConfigureAwait(false);
            }
            catch (Exception cleanup) { CorrectnessOracle.ObserveCleanupFailure(cleanup, name); throw; }
        }
        // Match the historical operation count: this final read uses the retained
        // connection after the transaction was fully disposed. Independent-connection
        // checks run only during explicit --verify, outside the steady timing boundary.
        var final = target.Select(PerfContext.FullOrder).SingleAsync();
        if (!final.IsCompleted) suspensions++;
        var persisted = await final.ConfigureAwait(false);
        if (persisted != original) throw CorrectnessOracle.Failure("Durable state was not restored after transaction.", name);
        HashOrder(ref digest, persisted);
        return new(name == "stale-conflict" ? 2 : 3, digest.Value, suspensions);
    }

    internal async Task VerifyIndependentStateAsync(string name)
    {
        var independentConnection = await _source.OpenSessionAsync();
        try
        {
            await using var independent = _source.CreateContext(independentConnection);
            var persisted = await Target(independent).Select(PerfContext.FullOrder).SingleAsync();
            if (persisted != SeedOrder(_options.OrdersPerTenant))
                throw CorrectnessOracle.Failure("Independent connection did not see the restored durable order.", name);
            _source.RecordIndependentStateCheck();
        }
        finally { await _source.CloseSessionAsync(independentConnection); }
    }
}
