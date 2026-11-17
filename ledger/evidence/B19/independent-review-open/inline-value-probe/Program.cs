using System.Net;
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
long occupiedInlineBytes = (long) Unsafe.SizeOf<Big06>() * 80 * parsed.Items.Length;
Console.WriteLine($"Shape: input + array + item + six inline struct levels; 80 Big06 auto-properties per item; count={parsed.Items.Length}");
Console.WriteLine($"Big06 inline bytes={Unsafe.SizeOf<Big06>()}; allocation in warmed source-generated Deserialize={measured}; inline live storage lower bound={occupiedInlineBytes}");
GC.KeepAlive(parsed);
var registry = new McpRegistry();
int calls = 0;
registry.AddTool("inline-value", "Bounded inline value review", ReviewJson.Default.Input, ReviewJson.Default.Empty, (Input input, McpCallContext context) =>
{
    calls++;
    Console.WriteLine($"ACTUAL HANDLER ENTERED: items={input.Items.Length}; live inline storage lower bound={(long) Unsafe.SizeOf<Big06>() * 80 * input.Items.Length}");
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
public sealed class Item
{
    public Big06 P00 { get; set; }
    public Big06 P01 { get; set; }
    public Big06 P02 { get; set; }
    public Big06 P03 { get; set; }
    public Big06 P04 { get; set; }
    public Big06 P05 { get; set; }
    public Big06 P06 { get; set; }
    public Big06 P07 { get; set; }
    public Big06 P08 { get; set; }
    public Big06 P09 { get; set; }
    public Big06 P10 { get; set; }
    public Big06 P11 { get; set; }
    public Big06 P12 { get; set; }
    public Big06 P13 { get; set; }
    public Big06 P14 { get; set; }
    public Big06 P15 { get; set; }
    public Big06 P16 { get; set; }
    public Big06 P17 { get; set; }
    public Big06 P18 { get; set; }
    public Big06 P19 { get; set; }
    public Big06 P20 { get; set; }
    public Big06 P21 { get; set; }
    public Big06 P22 { get; set; }
    public Big06 P23 { get; set; }
    public Big06 P24 { get; set; }
    public Big06 P25 { get; set; }
    public Big06 P26 { get; set; }
    public Big06 P27 { get; set; }
    public Big06 P28 { get; set; }
    public Big06 P29 { get; set; }
    public Big06 P30 { get; set; }
    public Big06 P31 { get; set; }
    public Big06 P32 { get; set; }
    public Big06 P33 { get; set; }
    public Big06 P34 { get; set; }
    public Big06 P35 { get; set; }
    public Big06 P36 { get; set; }
    public Big06 P37 { get; set; }
    public Big06 P38 { get; set; }
    public Big06 P39 { get; set; }
    public Big06 P40 { get; set; }
    public Big06 P41 { get; set; }
    public Big06 P42 { get; set; }
    public Big06 P43 { get; set; }
    public Big06 P44 { get; set; }
    public Big06 P45 { get; set; }
    public Big06 P46 { get; set; }
    public Big06 P47 { get; set; }
    public Big06 P48 { get; set; }
    public Big06 P49 { get; set; }
    public Big06 P50 { get; set; }
    public Big06 P51 { get; set; }
    public Big06 P52 { get; set; }
    public Big06 P53 { get; set; }
    public Big06 P54 { get; set; }
    public Big06 P55 { get; set; }
    public Big06 P56 { get; set; }
    public Big06 P57 { get; set; }
    public Big06 P58 { get; set; }
    public Big06 P59 { get; set; }
    public Big06 P60 { get; set; }
    public Big06 P61 { get; set; }
    public Big06 P62 { get; set; }
    public Big06 P63 { get; set; }
    public Big06 P64 { get; set; }
    public Big06 P65 { get; set; }
    public Big06 P66 { get; set; }
    public Big06 P67 { get; set; }
    public Big06 P68 { get; set; }
    public Big06 P69 { get; set; }
    public Big06 P70 { get; set; }
    public Big06 P71 { get; set; }
    public Big06 P72 { get; set; }
    public Big06 P73 { get; set; }
    public Big06 P74 { get; set; }
    public Big06 P75 { get; set; }
    public Big06 P76 { get; set; }
    public Big06 P77 { get; set; }
    public Big06 P78 { get; set; }
    public Big06 P79 { get; set; }
}
public struct Big01 { public decimal A { get; set; } }
public struct Big02 { public Big01 A { get; set; } public Big01 B { get; set; } }
public struct Big03 { public Big02 A { get; set; } public Big02 B { get; set; } }
public struct Big04 { public Big03 A { get; set; } public Big03 B { get; set; } }
public struct Big05 { public Big04 A { get; set; } public Big04 B { get; set; } }
public struct Big06 { public Big05 A { get; set; } public Big05 B { get; set; } }
[JsonSerializable(typeof(Input))]
[JsonSerializable(typeof(Empty))]
internal partial class ReviewJson : JsonSerializerContext { }
