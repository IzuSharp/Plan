// Shared by both ordinary PackageReference consumers. Successful reads retain
// exactly one disposal; exceptional reads record contract failures before
// retirement and preserve both exceptions if retirement also fails.
internal static class ReadStream
{
    internal static async ValueTask<OperationResult> Consume<T>(IAsyncEnumerable<T> stream, RowDigest<T> hash, int stopAfter = int.MaxValue)
    {
        var digest = Digest.Create(); long rows = 0, suspensions = 0;
        var reader = stream.GetAsyncEnumerator();
        try
        {
            while (rows < stopAfter)
            {
                var move = reader.MoveNextAsync();
                if (!move.IsCompleted) suspensions++;
                if (!await move.ConfigureAwait(false)) break;
                hash(ref digest, reader.Current); rows++;
            }
        }
        catch (Exception primary)
        {
            CorrectnessOracle.ObserveContractFailure(primary);
            await RetireFailedReader(reader, primary).ConfigureAwait(false);
            throw new InvalidOperationException("Failed reader retirement unexpectedly returned.");
        }
        try
        {
            var close = reader.DisposeAsync();
            if (!close.IsCompleted) suspensions++;
            await close.ConfigureAwait(false);
        }
        catch (Exception cleanup)
        {
            CorrectnessOracle.ObserveCleanupFailure(cleanup);
            throw;
        }
        return new(rows, digest.Value, suspensions);
    }

    private static async ValueTask RetireFailedReader(IAsyncDisposable reader, Exception primary)
    {
        try { await reader.DisposeAsync().ConfigureAwait(false); }
        catch (Exception cleanup)
        {
            CorrectnessOracle.ObserveCleanupFailure(cleanup);
            throw new AggregateException("Workload read and reader retirement failed.", primary, cleanup);
        }
        System.Runtime.ExceptionServices.ExceptionDispatchInfo.Throw(primary);
    }
}
