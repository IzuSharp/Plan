using System.Diagnostics;
using System.Diagnostics.Metrics;
using System.Net;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using NativeWeave.Server;

int activities = 0, measurements = 0, sample = 0;
using ActivityListener tracing = new()
{
    ShouldListenTo = source => source.Name == "NativeWeave.Server",
    Sample = (ref ActivityCreationOptions<ActivityContext> _) => ++sample % 8 == 0 ? ActivitySamplingResult.AllDataAndRecorded : ActivitySamplingResult.None,
    ActivityStopped = _ => Interlocked.Increment(ref activities)
};
ActivitySource.AddActivityListener(tracing);
using MeterListener metrics = new();
metrics.InstrumentPublished = (instrument, listener) => { if (instrument.Meter.Name == "NativeWeave.Server") listener.EnableMeasurementEvents(instrument); };
metrics.SetMeasurementEventCallback<long>((_, _, _, _) => Interlocked.Increment(ref measurements));
metrics.SetMeasurementEventCallback<double>((_, _, _, _) => Interlocked.Increment(ref measurements));
metrics.Start();
var warnings = new LocalWarnings();
var builder = NativeServer.CreateBuilder().Listen(IPAddress.Loopback, 0);
builder.Services.AddLogging(logging => { logging.SetMinimumLevel(LogLevel.Warning); logging.AddProvider(warnings); });
var app = builder.Build();
var writeFinished = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
var releaseFinish = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
var finishObserved = new TaskCompletionSource<Exception?>(TaskCreationOptions.RunContinuationsAsynchronously);
app.MapRaw("/tail", ["GET"], async (context, token) =>
{
    string phase = "write";
    try
    {
        context.Response.ContentLength = 4;
        await context.Response.WriteAsync("tail"u8.ToArray(), token);
        Probe.Emit("write_finished");
        writeFinished.TrySetResult();
        phase = "gate";
        await releaseFinish.Task;
        phase = "complete";
        Probe.Emit("complete_enter", fields: json => json.WriteBoolean("request_cancelled", token.IsCancellationRequested));
        // Deliberately reach FinishAsync instead of failing a cancelled-token precheck.
        await context.Response.CompleteAsync();
        Probe.Emit("complete_returned");
        finishObserved.TrySetResult(null);
    }
    catch (Exception error)
    {
        Probe.Emit("handler_exception", error, json => json.WriteString("phase", phase));
        writeFinished.TrySetException(error);
        finishObserved.TrySetResult(error);
        throw; // Preserve the application's normal failure/diagnostics path.
    }
});

int exitCode = 0;
try
{
    await app.StartAsync();
    using var client = new HttpClient { BaseAddress = app.BoundAddresses.Single(), Timeout = TimeSpan.FromSeconds(5) };
    using var request = new HttpRequestMessage(HttpMethod.Get, "tail") { Version = HttpVersion.Version11, VersionPolicy = HttpVersionPolicy.RequestVersionExact };
    using var response = await client.SendAsync(request, HttpCompletionOption.ResponseHeadersRead);
    if (response.StatusCode != HttpStatusCode.OK || response.Content.Headers.ContentLength != 4)
        throw new InvalidOperationException("Unexpected tail response headers.");
    await writeFinished.Task.WaitAsync(TimeSpan.FromSeconds(5));
    await using var body = await response.Content.ReadAsStreamAsync();
    using var readDeadline = new CancellationTokenSource(TimeSpan.FromSeconds(5));
    byte[] received = new byte[4];
    await body.ReadExactlyAsync(received, readDeadline.Token);
    if (!received.AsSpan().SequenceEqual("tail"u8)) throw new InvalidOperationException("Tail bytes did not match.");
    long closeStarted = Stopwatch.GetTimestamp();
    Task<ServerCloseResult> closeTask = app.CloseAsync(TimeSpan.FromSeconds(5));
    try
    {
        Probe.Emit("close_started", fields: json => { json.WriteNumber("close_started_ticks", closeStarted); json.WriteNumber("received_bytes", received.Length); });
        await Task.WhenAny(closeTask, Task.Delay(TimeSpan.FromMilliseconds(100)));
        Probe.Emit("close_observed_before_release", fields: json =>
        {
            json.WriteBoolean("close_task_completed", closeTask.IsCompleted);
            json.WriteNumber("nominal_observation_limit_ms", 100);
            json.WriteNumber("actual_elapsed_ms", Stopwatch.GetElapsedTime(closeStarted).TotalMilliseconds);
            json.WriteBoolean("acceptor_join_proven", false);
        });
    }
    finally
    {
        releaseFinish.TrySetResult();
        Probe.Emit("finish_gate_released");
    }
    Exception? finishError = await finishObserved.Task.WaitAsync(TimeSpan.FromSeconds(10));
    Probe.Emit("finish_observed", fields: json => json.WriteBoolean("complete_succeeded", finishError is null));
    ServerCloseResult close = await closeTask.WaitAsync(TimeSpan.FromSeconds(10));
    Probe.Emit("close_returned", fields: json =>
    {
        json.WriteString("status", close.Status.ToString());
        json.WriteNumber("pending_requests", close.PendingRequests);
        json.WriteNumber("retained_native_bytes", close.RetainedNativeBytes);
        json.WriteNumber("retained_managed_bytes", close.RetainedManagedBytes);
    });
}
catch (Exception error)
{
    exitCode = 1;
    Probe.Emit("orchestration_exception", error);
}
finally
{
    releaseFinish.TrySetResult();
    Probe.Emit("dispose_enter");
    try
    {
        // The unchanged external process owner enforces the overall deadline.
        await app.DisposeAsync();
        Probe.Emit("dispose_returned");
    }
    catch (Exception error) { exitCode = 1; Probe.Emit("dispose_exception", error); }
    metrics.RecordObservableInstruments();
    Probe.Emit("diagnostic_end", fields: json =>
    {
        json.WriteNumber("activities", activities);
        json.WriteNumber("measurements", measurements);
        json.WriteNumber("warning_or_error_events", warnings.Count);
        json.WriteNumber("exit_code", exitCode);
    });
}
return exitCode;

static class Probe
{
    internal static void Emit(string name, Exception? error = null, Action<Utf8JsonWriter>? fields = null)
    {
        using var bytes = new MemoryStream();
        using (var json = new Utf8JsonWriter(bytes))
        {
            json.WriteStartObject();
            json.WriteString("event", name);
            json.WriteString("utc", DateTimeOffset.UtcNow);
            json.WriteNumber("ticks", Stopwatch.GetTimestamp());
            json.WriteNumber("ticks_per_second", Stopwatch.Frequency);
            if (error is not null)
            {
                json.WriteString("exception_type", error.GetType().FullName);
                json.WriteString("message", error.Message);
                json.WriteString("stack", error.StackTrace);
            }
            fields?.Invoke(json);
            json.WriteEndObject();
        }
        Console.Error.WriteLine("PERF01_SERVER_CLOSE_TAIL " + Encoding.UTF8.GetString(bytes.ToArray()));
    }
}

sealed class LocalWarnings : ILoggerProvider, ILogger
{
    private int _remaining = 32;
    internal int Count => Math.Min(32, Math.Max(0, 32 - Volatile.Read(ref _remaining)));
    public ILogger CreateLogger(string categoryName) => this;
    public bool IsEnabled(LogLevel level) => level >= LogLevel.Warning && Volatile.Read(ref _remaining) > 0;
    public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;
    public void Log<TState>(LogLevel level, EventId id, TState state, Exception? error, Func<TState, Exception?, string> format)
    {
        if (Interlocked.Decrement(ref _remaining) < 0) return;
        string text = format(state, error);
        Probe.Emit("server_diagnostic", error, json =>
        {
            json.WriteString("level", level.ToString());
            json.WriteNumber("event_id", id.Id);
            json.WriteString("text", text.Length <= 256 ? text : text[..256]);
        });
    }
    public void Dispose() { }
}
