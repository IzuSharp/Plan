using System.Net;
using System.Text;
using System.Text.Json;
using ExternalModels;
using NativeWeave.Server;
using NativeWeave.Server.Mcp;

long expected = long.Parse(args.Single(), System.Globalization.CultureInfo.InvariantCulture);
foreach (var version in new[] { HttpVersion.Version11, HttpVersion.Version20 })
{
    int entered = 0;
    var registry = new McpRegistry().AddTool("external", "Precompiled external static context",
        ExternalJson.Default.ExternalInput, ExternalJson.Default.ExternalOutput,
        (input, _) => { entered++; return Task.FromResult(McpToolResult<ExternalOutput>.Success(new(input.Value + input.Touch()))); });
    var builder = NativeServer.CreateBuilder();
    builder.Listen(IPAddress.Loopback, 0, options => options.Protocols = version == HttpVersion.Version20 ? ServerProtocols.Http2 : ServerProtocols.Http1);
    await using var app = builder.Build();
    app.MapMcp("/mcp", registry); await app.StartAsync();
    using var client = new HttpClient { BaseAddress = app.BoundAddresses.Single() };
    async Task<JsonDocument> Send(string method, string fields = "", string? name = null)
    {
        const string metadata = "\"_meta\":{\"io.modelcontextprotocol/protocolVersion\":\"2026-07-28\",\"io.modelcontextprotocol/clientCapabilities\":{}}";
        string body = "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"" + method + "\",\"params\":{" + fields + (fields.Length == 0 ? "" : ",") + metadata + "}}";
        using var request = new HttpRequestMessage(HttpMethod.Post, "/mcp") { Version = version, VersionPolicy = HttpVersionPolicy.RequestVersionExact, Content = new StringContent(body, Encoding.UTF8, "application/json") };
        request.Headers.Add("Accept", "application/json, text/event-stream"); request.Headers.Add("MCP-Protocol-Version", "2026-07-28"); request.Headers.Add("Mcp-Method", method);
        if (name is not null) request.Headers.Add("Mcp-Name", name);
        using var response = await client.SendAsync(request); response.EnsureSuccessStatusCode();
        return JsonDocument.Parse(await response.Content.ReadAsStringAsync());
    }
    using (var listed = await Send("tools/list"))
    {
        long nodeBytes = listed.RootElement.GetProperty("result").GetProperty("tools")[0].GetProperty("inputSchema").GetProperty("x-nativeweave-managed-peak-v1").GetProperty("nodeBytes").GetInt64();
        if (nodeBytes != expected) throw new Exception($"External private layout proof is stale: {nodeBytes}, expected {expected}.");
    }
    using (var called = await Send("tools/call", "\"name\":\"external\",\"arguments\":{\"value\":7}", "external"))
        if (called.RootElement.GetProperty("result").GetProperty("structuredContent").GetProperty("value").GetInt32() != 7 || entered != 1) throw new Exception("External typed handler did not complete exactly once.");
    var closed = await app.CloseAsync(TimeSpan.FromSeconds(3));
    if (closed.Status != ServerCloseStatus.Completed || closed.PendingRequests != 0 || closed.RetainedNativeBytes != 0 || closed.RetainedManagedBytes != 0) throw new Exception("External consumer retained request owners.");
    Console.WriteLine($"External private layout node_bytes={expected}, HTTP/{version}, dynamic={System.Runtime.CompilerServices.RuntimeFeature.IsDynamicCodeSupported}: passed");
}
