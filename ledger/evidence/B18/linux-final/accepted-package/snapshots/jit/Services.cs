using Google.Protobuf;
using NativeWeave.Grpc.Sample.Messages;
using NativeWeave.Server;
using NativeWeave.Server.Grpc;

// Grpc.Tools generates the DTOs and independent clients from the .proto files.
// These application-defined static adapters map their exact methods to NativeWeave.
internal sealed class EchoService : IGeneratedGrpcService
{
    private static readonly GrpcMarshaller<EchoRequest> Request = new(
        static (value, output) => value.WriteTo(output),
        static bytes => EchoRequest.Parser.ParseFrom(bytes));
    private static readonly GrpcMarshaller<EchoReply> Response = new(
        static (value, output) => value.WriteTo(output),
        static bytes => EchoReply.Parser.ParseFrom(bytes));

    public void Map(ServerRoutes routes)
    {
        routes.MapGrpcUnary(Method("Echo", GrpcMethodKind.Unary), Echo, Limits());
        routes.MapGrpcServerStreaming(Method("Repeat", GrpcMethodKind.ServerStreaming), Repeat, Limits());
        routes.MapGrpcClientStreaming(Method("Sum", GrpcMethodKind.ClientStreaming), Sum, Limits());
        routes.MapGrpcDuplex(Method("Duplex", GrpcMethodKind.DuplexStreaming), Duplex, Limits());
        routes.MapGrpcUnary(Method("Fail", GrpcMethodKind.Unary), Fail, Limits());
        var deadline = Limits(); deadline.Timeout = TimeSpan.FromMilliseconds(250);
        routes.MapGrpcServerStreaming(Method("Wait", GrpcMethodKind.ServerStreaming), Wait, deadline);
    }

    private static GrpcMethod<EchoRequest, EchoReply> Method(string name, GrpcMethodKind kind)
        => new("/nativeweave.samples.EchoApi/" + name, kind, Request, Response);
    private static GrpcMethodOptions Limits() => new()
    {
        MaxEncodedMessageBytes = 8 * 1024,
        MaxDecodedMessageBytes = 8 * 1024,
        MaxStreamBytes = 64 * 1024,
        Timeout = TimeSpan.FromSeconds(3)
    };
    private static EchoReply Reply(EchoRequest request, int index)
        => new() { Text = request.Text, Payload = request.Payload, Index = index };

    private static async Task<EchoReply> Echo(EchoRequest request, GrpcCallContext call)
    {
        // Decoded binary metadata is separate from ordinary HTTP header wire text.
        var headers = new GrpcMetadata(); headers.Add("sample-service", "echo");
        var binary = call.RequestHeaders.GetBinaryValues("sample-bin");
        if (binary.Count != 0) headers.AddBinary("sample-bin", binary[0]);
        await call.WriteResponseHeadersAsync(headers, call.CancellationToken);
        call.ResponseTrailers.Add("sample-completed", "yes");
        return Reply(request, 0);
    }
    private static async IAsyncEnumerable<EchoReply> Repeat(EchoRequest request, GrpcCallContext call)
    {
        if (request.Count is < 0 or > 8)
            throw new GrpcException(GrpcStatusCode.InvalidArgument, "Count must be between zero and eight.");
        for (var index = 0; index < request.Count; index++)
        {
            call.CancellationToken.ThrowIfCancellationRequested();
            yield return Reply(request, index);
            await Task.Yield();
        }
    }
    private static async Task<EchoReply> Sum(IAsyncEnumerable<EchoRequest> requests, GrpcCallContext call)
    {
        var sum = 0;
        await foreach (var request in requests.WithCancellation(call.CancellationToken))
            sum = checked(sum + request.Count);
        return new() { Text = "sum", Index = sum };
    }
    private static async IAsyncEnumerable<EchoReply> Duplex(IAsyncEnumerable<EchoRequest> requests, GrpcCallContext call)
    {
        await foreach (var request in requests.WithCancellation(call.CancellationToken))
            yield return Reply(request, request.Count);
    }
    private static Task<EchoReply> Fail(EchoRequest request, GrpcCallContext call)
    {
        var trailers = new GrpcMetadata(); trailers.Add("sample-error", "missing-item");
        throw new GrpcException(GrpcStatusCode.NotFound, "The sample item was not found.", trailers);
    }
    private static async IAsyncEnumerable<EchoReply> Wait(EchoRequest request, GrpcCallContext call)
    {
        var headers = new GrpcMetadata(); headers.Add("sample-started", "yes");
        await call.WriteResponseHeadersAsync(headers, call.CancellationToken);
        yield return Reply(request, 0);
        // The native whole-call deadline remains active after response headers.
        await Task.Delay(Timeout.InfiniteTimeSpan, call.CancellationToken);
    }
}

internal sealed class CounterService : IGeneratedGrpcService
{
    private static readonly GrpcMarshaller<CounterRequest> Request = new(
        static (value, output) => value.WriteTo(output),
        static bytes => CounterRequest.Parser.ParseFrom(bytes));
    private static readonly GrpcMarshaller<CounterReply> Response = new(
        static (value, output) => value.WriteTo(output),
        static bytes => CounterReply.Parser.ParseFrom(bytes));

    public void Map(ServerRoutes routes) => routes.MapGrpcUnary(
        new GrpcMethod<CounterRequest, CounterReply>("/nativeweave.samples.CounterApi/Increment",
            GrpcMethodKind.Unary, Request, Response),
        static (request, call) =>
        {
            call.CancellationToken.ThrowIfCancellationRequested();
            return Task.FromResult(new CounterReply { Value = checked(request.Value + 1) });
        }, new() { MaxEncodedMessageBytes = 1024, MaxDecodedMessageBytes = 1024, MaxStreamBytes = 8192 });
}
