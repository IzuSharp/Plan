using System.Data.Common;
using System.Diagnostics;
using Dapper;

internal sealed class PhaseProbe(DbConnection connection, int resultRows, Progress progress)
{
    private readonly Arguments _arguments = new();
    private readonly string?[][] _notes = CreateNotes();

    private static string?[][] CreateNotes()
    {
        string?[][] values = [new string?[1000], new string?[1000]];
        for (var tenant = 1; tenant <= 2; tenant++)
            for (var id = 1; id <= 1000; id++)
                values[tenant - 1][id - 1] = id % 5 == 0 ? null : $"note-{tenant}-{id}";
        return values;
    }

    [CacheCommand]
    private IAsyncEnumerable<PhaseRow> Query(long tenant)
    {
        // Serial enumeration owns these values until EOF and Dispose complete.
        // Reuse the argument object just as the fixed command factory updates
        // its two cached DbParameter values by ordinal on every execution.
        _arguments.tenant = tenant; _arguments.id = resultRows;
        return resultRows == 1
            ? connection.QueryUnbufferedAsync<PhaseRow>(PhaseSql.PrimaryKey, _arguments)
            : connection.QueryUnbufferedAsync<PhaseRow>(PhaseSql.Many, _arguments);
    }

    internal async ValueTask<Sample> Run(long tenant)
    {
        List<PhaseRow>? rows = null;
        try
        {
            progress.Stage = "construct";
            IAsyncEnumerator<PhaseRow>? reader = null;
            var started = Stopwatch.GetTimestamp();
            rows = BusinessAllocation.CreateList<PhaseRow>(resultRows);
            var stream = Query(tenant);
            var constructed = Stopwatch.GetTimestamp();
            long first = constructed, complete = constructed, released;
            try
            {
                progress.Stage = "first";
                reader = stream.GetAsyncEnumerator();
                if (!await reader.MoveNextAsync()) throw new InvalidOperationException("Expected the first row.");
                BusinessAllocation.Add(rows, reader.Current);
                first = Stopwatch.GetTimestamp();
                progress.Stage = "read";
                while (await reader.MoveNextAsync()) BusinessAllocation.Add(rows, reader.Current);
                complete = Stopwatch.GetTimestamp();
            }
            catch (Exception failure)
            {
                progress.Capture(failure, rows.Count);
                throw;
            }
            finally
            {
                progress.Stage = "release";
                if (reader is not null) await reader.DisposeAsync();
                released = Stopwatch.GetTimestamp();
            }
            progress.Stage = "verify";
            if (rows.Count != resultRows) throw new InvalidOperationException("Incomplete result.");
            for (var i = 0; i < rows.Count; i++)
                if (rows[i].Id != i + 1 || rows[i].Note != _notes[tenant - 1][i])
                    throw new InvalidOperationException("Result field, ordering or null differs.");
            GC.KeepAlive(rows);
            return new(constructed - started, first - constructed, complete - first, released - complete, rows.Count);
        }
        catch (Exception failure)
        {
            progress.Capture(failure, rows?.Count);
            throw;
        }
    }

    internal sealed class Arguments
    {
        public long tenant { get; set; }
        public long id { get; set; }
    }
}

internal sealed record PhaseRow(long Id, string? Note);
