using System.Net;
using System.Runtime.CompilerServices;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using NativeWeave.Grpc.Sample.Messages;
using NativeWeave.Server;
using NativeWeave.Server.Grpc;

var tls = args.Contains("--tls");
var minimal = args.Contains("--minimal");
if (args.Contains("--require-aot"))
    ClientDemo.Ensure(!RuntimeFeature.IsDynamicCodeSupported && !RuntimeFeature.IsDynamicCodeCompiled, "actual Native AOT process");
using var certificate = tls ? new LocalCertificate() : null;
var builder = NativeServer.CreateBuilder();
builder.Listen(IPAddress.Loopback, 0, listener =>
{
    listener.Protocols = ServerProtocols.Http2;
    if (certificate is not null) listener.Tls = ServerTlsOptions.FromPemFiles(certificate.CertificatePath, certificate.PrivateKeyPath);
});
builder.Options.RequestTimeout = TimeSpan.FromSeconds(5);
await using var application = builder.Build();
application.MapGrpc(new EchoService());
application.MapGrpc(new CounterService());
await application.StartAsync();

// grpc-dotnet is only the independent demo client. Rust owns the listening server.
using var handler = new SocketsHttpHandler();
if (certificate is not null)
    handler.SslOptions.RemoteCertificateValidationCallback = (_, presented, _, _) => presented?.GetCertHashString(HashAlgorithmName.SHA256) == certificate.Fingerprint;
using var http = new HttpClient(handler);
using var channel = global::Grpc.Net.Client.GrpcChannel.ForAddress(application.BoundAddresses.Single(), new() { HttpClient = http });
var echo = new EchoApi.EchoApiClient(channel);
var counter = new CounterApi.CounterApiClient(channel);
await ClientDemo.Minimal(echo, counter);
if (!minimal) await ClientDemo.Advanced(echo);
var close = await application.CloseAsync(TimeSpan.FromSeconds(5));
ClientDemo.Ensure(close.Status == ServerCloseStatus.Completed && close.PendingRequests == 0 && close.RetainedManagedBytes == 0 && close.RetainedNativeBytes == 0, "bounded close joins managed and native ownership");
Console.WriteLine($"B18 two-service sample: mode={(minimal ? "minimal" : "advanced")}; transport={(tls ? "HTTP2+rustls" : "HTTP2 loopback")}; dynamic={RuntimeFeature.IsDynamicCodeSupported}");

// An ephemeral certificate trusted only by exact fingerprint in this local demo.
// Production listeners should receive their configured certificate/key paths.
internal sealed class LocalCertificate : IDisposable
{
    private readonly string _directory = Path.Combine(Path.GetTempPath(), "nw-grpc-sample-" + Guid.NewGuid().ToString("N"));
    internal string CertificatePath { get; }
    internal string PrivateKeyPath { get; }
    internal string Fingerprint { get; }
    internal LocalCertificate()
    {
        Directory.CreateDirectory(_directory);
        using var key = RSA.Create(2048);
        var request = new CertificateRequest("CN=localhost", key, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        var names = new SubjectAlternativeNameBuilder(); names.AddDnsName("localhost"); names.AddIpAddress(IPAddress.Loopback);
        request.CertificateExtensions.Add(names.Build());
        using var certificate = request.CreateSelfSigned(DateTimeOffset.UtcNow.AddMinutes(-1), DateTimeOffset.UtcNow.AddDays(1));
        CertificatePath = Path.Combine(_directory, "certificate.pem"); PrivateKeyPath = Path.Combine(_directory, "private-key.pem");
        File.WriteAllText(CertificatePath, certificate.ExportCertificatePem());
        File.WriteAllText(PrivateKeyPath, key.ExportPkcs8PrivateKeyPem());
        if (!OperatingSystem.IsWindows()) File.SetUnixFileMode(PrivateKeyPath, UnixFileMode.UserRead | UnixFileMode.UserWrite);
        Fingerprint = certificate.GetCertHashString(HashAlgorithmName.SHA256);
    }
    public void Dispose() => Directory.Delete(_directory, recursive: true);
}
