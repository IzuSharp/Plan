using Google.Protobuf;
using NativeWeave.Grpc.Sample.Messages;
using G = Grpc.Core;

internal static class ClientDemo
{
    internal static void Ensure(bool value, string message)
    { if (!value) throw new InvalidOperationException(message); Console.WriteLine("PASS " + message); }

    internal static async Task Minimal(EchoApi.EchoApiClient echo, CounterApi.CounterApiClient counter)
    {
        var request = new EchoRequest { Text = "hello from C#", Payload = ByteString.CopyFrom([0, 1, 255]) };
        using var unary = echo.EchoAsync(request, deadline: DateTime.UtcNow.AddSeconds(5));
        var result = await unary.ResponseAsync;
        Ensure(result.Text == request.Text && result.Payload.Equals(request.Payload), "typed generated protobuf unary round trip");
        Ensure(unary.GetStatus().StatusCode == G.StatusCode.OK && unary.GetTrailers().GetValue("sample-completed") == "yes", "successful terminal status and trailers");
        using var increment = counter.IncrementAsync(new() { Value = 40 }, deadline: DateTime.UtcNow.AddSeconds(5));
        Ensure((await increment.ResponseAsync).Value == 41, "second independent service and generated DTO pair");
    }

    internal static async Task Advanced(EchoApi.EchoApiClient echo)
    {
        var request = new EchoRequest { Text = "stream", Count = 3 };
        using (var server = echo.Repeat(request, deadline: DateTime.UtcNow.AddSeconds(5)))
        {
            var indices = new List<int>();
            while (await server.ResponseStream.MoveNext(default)) indices.Add(server.ResponseStream.Current.Index);
            Ensure(indices.SequenceEqual([0, 1, 2]), "server streaming preserves complete-message boundaries");
        }
        using (var client = echo.Sum(deadline: DateTime.UtcNow.AddSeconds(5)))
        {
            await client.RequestStream.WriteAsync(new() { Count = 4 });
            await client.RequestStream.WriteAsync(new() { Count = 7 });
            await client.RequestStream.CompleteAsync();
            Ensure((await client.ResponseAsync).Index == 11, "client streaming consumes explicit input half-close");
        }
        using (var duplex = echo.Duplex(deadline: DateTime.UtcNow.AddSeconds(5)))
        {
            await duplex.RequestStream.WriteAsync(new() { Text = "first", Count = 1 });
            Ensure(await duplex.ResponseStream.MoveNext(default) && duplex.ResponseStream.Current.Text == "first", "duplex response before input half-close");
            await duplex.RequestStream.WriteAsync(new() { Text = "second", Count = 2 });
            await duplex.RequestStream.CompleteAsync();
            Ensure(await duplex.ResponseStream.MoveNext(default) && duplex.ResponseStream.Current.Index == 2 && !await duplex.ResponseStream.MoveNext(default), "duplex ordering and terminal EOF");
        }
        var metadata = new G.Metadata { { "sample-bin", new byte[] { 0, 5, 255 } } };
        using (var binary = echo.EchoAsync(request, metadata, DateTime.UtcNow.AddSeconds(5)))
        {
            var headers = await binary.ResponseHeadersAsync;
            await binary.ResponseAsync;
            Ensure(headers.GetValueBytes("sample-bin")!.SequenceEqual(new byte[] { 0, 5, 255 }), "raw binary gRPC metadata is not HTTP header text");
        }
        using (var failure = echo.FailAsync(request, deadline: DateTime.UtcNow.AddSeconds(5)))
        {
            try { await failure.ResponseAsync; throw new InvalidOperationException("Expected the explicit protocol failure."); }
            catch (G.RpcException error)
            { Ensure(error.StatusCode == G.StatusCode.NotFound && error.Trailers.GetValue("sample-error") == "missing-item", "explicit gRPC status and error trailers"); }
        }
        using (var deadline = echo.Wait(request, deadline: DateTime.UtcNow.AddSeconds(5)))
        {
            Ensure((await deadline.ResponseHeadersAsync).GetValue("sample-started") == "yes", "response headers committed before native deadline");
            Ensure(await deadline.ResponseStream.MoveNext(default), "one message before deadline");
            try { await deadline.ResponseStream.MoveNext(default); throw new InvalidOperationException("Expected the native whole-call deadline."); }
            catch (G.RpcException error)
            { Ensure(error.StatusCode == G.StatusCode.DeadlineExceeded, "native method deadline survives response headers"); }
        }
    }
}
