using System.Net;
using System.Security.Claims;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using NativeWeave.Server;
using NativeWeave.Server.Mcp;

bool selfTest = args.Contains("--self-test"), minimal = args.Contains("--minimal");
foreach (Version version in selfTest ? new[] { HttpVersion.Version11, HttpVersion.Version20 } : new[] { HttpVersion.Version11 })
{
    var builder = NativeServer.CreateBuilder();
    builder.Listen(IPAddress.Loopback, selfTest ? 0 : 5000, options => options.Protocols = version == HttpVersion.Version20 ? ServerProtocols.Http2 : ServerProtocols.Http1);
    if (!minimal) builder.UseAuthentication(new SampleAuthenticator()).UseAuthorization(new SampleAuthorizer());
    await using var app = builder.Build();
    var registry = new McpRegistry().AddTool("add", "Add two integers", SampleJson.Default.AddInput, SampleJson.Default.AddOutput,
        static (input, context) => Task.FromResult(McpToolResult<AddOutput>.Success(new(checked(input.Left + input.Right), context.Name))));
    if (!minimal)
    {
        registry.AddResource("nativeweave:guide", "guide", "text/plain", static _ => Task.FromResult(new McpTextResource("nativeweave:guide", "A typed static tool on the Rust Host.")))
            .AddPrompt("greeting", "Greet a caller", [new("name", "Caller name", Required: true)], static (arguments, _) => Task.FromResult<IReadOnlyList<McpPromptMessage>>([new("assistant", "Hello " + arguments["name"])]));
    }
    var endpoint = app.MapMcp("/mcp", registry);
    if (!minimal) endpoint.RequireAuthorization("sample-caller");
    if (!selfTest) { Console.WriteLine("Listening on http://127.0.0.1:5000/mcp; advanced mode requires X-Demo-Caller: local."); await app.RunAsync(); continue; }
    await app.StartAsync();
    using var client = new HttpClient { BaseAddress = app.BoundAddresses.Single(), DefaultRequestVersion = version, DefaultVersionPolicy = HttpVersionPolicy.RequestVersionExact };
    async Task<string> Send(string method, string fields = "", string? name = null, bool authorized = true, int status = 200)
    {
        const string meta = "\"_meta\":{\"io.modelcontextprotocol/protocolVersion\":\"2026-07-28\",\"io.modelcontextprotocol/clientCapabilities\":{}}";
        string json = "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"" + method + "\",\"params\":{" + fields + (fields.Length > 0 ? "," : "") + meta + "}}";
        using var request = new HttpRequestMessage(HttpMethod.Post, "/mcp") { Version = version, VersionPolicy = HttpVersionPolicy.RequestVersionExact, Content = new StringContent(json, Encoding.UTF8, "application/json") };
        request.Headers.Add("Accept", "application/json, text/event-stream"); request.Headers.Add("MCP-Protocol-Version", "2026-07-28"); request.Headers.Add("Mcp-Method", method);
        if (name is not null) request.Headers.Add("Mcp-Name", name); if (authorized) request.Headers.Add("X-Demo-Caller", "local");
        using var response = await client.SendAsync(request); if ((int)response.StatusCode != status) throw new Exception($"{method}: {(int)response.StatusCode}, expected{status}");
        return await response.Content.ReadAsStringAsync();
    }
    if (!minimal) await Send("tools/list", authorized: false, status: 401);
    if (!(await Send("tools/list")).Contains("inputSchema", StringComparison.Ordinal)) throw new Exception("No native tool schema.");
    using (var result = JsonDocument.Parse(await Send("tools/call", "\"name\":\"add\",\"arguments\":{\"left\":2,\"right\":3}", "add")))
        if (result.RootElement.GetProperty("result").GetProperty("structuredContent").GetProperty("total").GetInt32() != 5) throw new Exception("Typed result mismatch.");
    if (!minimal)
    {
        if (!(await Send("resources/read", "\"uri\":\"nativeweave:guide\"", "nativeweave:guide")).Contains("Rust Host", StringComparison.Ordinal)) throw new Exception("Resource mismatch.");
        if (!(await Send("prompts/get", "\"name\":\"greeting\",\"arguments\":{\"name\":\"Linux\"}", "greeting")).Contains("Hello Linux", StringComparison.Ordinal)) throw new Exception("Prompt mismatch.");
    }
    var closed = await app.CloseAsync(TimeSpan.FromSeconds(3));
    if (closed.Status != ServerCloseStatus.Completed || closed.PendingRequests != 0 || closed.RetainedManagedBytes != 0 || closed.RetainedNativeBytes != 0) throw new Exception("Ownership did not retire.");
    Console.WriteLine($"MCP sample minimal={minimal}, HTTP/{version}, dynamic={System.Runtime.CompilerServices.RuntimeFeature.IsDynamicCodeSupported}: passed");
}
internal sealed record AddInput(int Left, int Right);
internal sealed record AddOutput(int Total, string Tool);
[JsonSerializable(typeof(AddInput))]
[JsonSerializable(typeof(AddOutput))]
[JsonSourceGenerationOptions(PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase, GenerationMode = JsonSourceGenerationMode.Metadata)]
internal partial class SampleJson : JsonSerializerContext;
internal sealed class SampleAuthenticator : IServerAuthenticator
{
    public Task<ClaimsPrincipal?> AuthenticateAsync(RequestContext context, CancellationToken cancellationToken) => Task.FromResult(context.Request.Headers.GetSingle("X-Demo-Caller") == "local" ? new ClaimsPrincipal(new ClaimsIdentity([new Claim(ClaimTypes.Name, "local")], "sample")) : null);
}
internal sealed class SampleAuthorizer : IServerAuthorizer
{
    public Task<bool> AuthorizeAsync(RequestContext context, string policy, CancellationToken cancellationToken) => Task.FromResult(policy == "sample-caller" && context.User.Identity?.IsAuthenticated == true);
}
