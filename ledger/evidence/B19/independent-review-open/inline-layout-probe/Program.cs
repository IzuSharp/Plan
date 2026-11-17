using System.Net;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Runtime.CompilerServices;
using NativeWeave.Server;
using NativeWeave.Server.Mcp;

const int count = 128;
string arguments = "{\"Items\":[" + string.Join(',', Enumerable.Repeat("{}", count)) + "]}";
_ = JsonSerializer.Deserialize(arguments, ReviewJson.Default.Input);
long before = GC.GetAllocatedBytesForCurrentThread();
var parsed = JsonSerializer.Deserialize(arguments, ReviewJson.Default.Input)!;
long measured = GC.GetAllocatedBytesForCurrentThread() - before;
long occupiedInlineBytes = (long) Unsafe.SizeOf<Padded>() * 1 * parsed.Items.Length;
Console.WriteLine($"Shape: input + array + item + one BCL explicitly sized inline struct; one Padded property per item; count={parsed.Items.Length}");
Console.WriteLine($"Padded inline bytes={Unsafe.SizeOf<Padded>()}; allocation in warmed source-generated Deserialize={measured}; inline live storage lower bound={occupiedInlineBytes}");
GC.KeepAlive(parsed);
var registry = new McpRegistry();
int calls = 0;
registry.AddTool("inline-value", "Bounded inline value review", ReviewJson.Default.Input, ReviewJson.Default.Empty, (Input input, McpCallContext context) =>
{
    calls++;
    Console.WriteLine($"ACTUAL HANDLER ENTERED: items={input.Items.Length}; live inline storage lower bound={(long) Unsafe.SizeOf<Padded>() * 1 * input.Items.Length}");
    GC.KeepAlive(input);
    return Task.FromResult(McpToolResult<Empty>.Success(new Empty()));
});
Console.WriteLine("Public AddTool accepted sparse inline-value DTO");
var builder = NativeServer.CreateBuilder();
builder.Listen(IPAddress.Loopback, 0, listen => listen.Protocols = ServerProtocols.Http1);
builder.Options.RequestTimeout = TimeSpan.FromSeconds(4);
builder.Options.ShutdownTimeout = TimeSpan.FromSeconds(3);
await using var app = builder.Build();
app.MapMcp("/mcp", registry);
await app.StartAsync();
Console.WriteLine("Actual native Host schema registration accepted");
using var client = new HttpClient { BaseAddress = app.BoundAddresses.Single(), Timeout = TimeSpan.FromSeconds(8) };
const string meta = "\"_meta\":{\"io.modelcontextprotocol/protocolVersion\":\"2026-07-28\",\"io.modelcontextprotocol/clientCapabilities\":{}}";
string wire = "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"inline-value\",\"arguments\":" + arguments + "," + meta + "}}";
using (var doc = JsonDocument.Parse(wire))
{
    (long nodes, long strings) Count(JsonElement item)
    {
        long nodes = 1, strings = item.ValueKind == JsonValueKind.String ? Encoding.UTF8.GetByteCount(item.GetString()!) : 0;
        if (item.ValueKind == JsonValueKind.Object) foreach (var prop in item.EnumerateObject()) { nodes++; strings += Encoding.UTF8.GetByteCount(prop.Name); var sub = Count(prop.Value); nodes += sub.nodes; strings += sub.strings; }
        if (item.ValueKind == JsonValueKind.Array) foreach (var child in item.EnumerateArray()) { var sub = Count(child); nodes += sub.nodes; strings += sub.strings; }
        return (nodes, strings);
    }
    var (nodes, strings) = Count(doc.RootElement);
    long w = Encoding.UTF8.GetByteCount(wire);
    long totalGrant = 3*w + 4096*nodes + 8*strings + 65536 + 2*1024*1024;
    Console.WriteLine($"WireBytes={w}; nodes={nodes}; strings={strings}; current full managed reservation including entire 2MiB reply pregrant={totalGrant}; default request-side budget=4194304");
}
using (var request = new HttpRequestMessage(HttpMethod.Post, "/mcp") { Content = new StringContent(wire, Encoding.UTF8, "application/json") })
{
    request.Headers.Add("Accept", "application/json, text/event-stream");
    request.Headers.Add("MCP-Protocol-Version", "2026-07-28");
    request.Headers.Add("Mcp-Method", "tools/call");
    request.Headers.Add("Mcp-Name", "inline-value");
    using var response = await client.SendAsync(request);
    Console.WriteLine($"HTTP {(int)response.StatusCode}: {await response.Content.ReadAsStringAsync()}; handler count={calls}");
}
var close = await app.CloseAsync(TimeSpan.FromSeconds(3));
Console.WriteLine($"Close={close.Status}, requests={close.PendingRequests}, native={close.RetainedNativeBytes}, managed={close.RetainedManagedBytes}");
public sealed class Empty { }
public sealed class Input { public Item[] Items { get; set; } = null!; }
public sealed class Item { public Padded P00 { get; set; } }
[StructLayout(LayoutKind.Sequential, Size = 65_536)]
public struct Padded { public int A { get; set; } }
[JsonSerializable(typeof(Input))]
[JsonSerializable(typeof(Empty))]
internal partial class ReviewJson : JsonSerializerContext { }
