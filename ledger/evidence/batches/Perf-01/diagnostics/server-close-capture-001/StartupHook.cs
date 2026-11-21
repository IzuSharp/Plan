using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Runtime.ExceptionServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading;

// The runtime requires this type name without a namespace.
internal static class StartupHook
{
    private const string ExpectedSampleMessage = "Application details stay out of diagnostic output.";
    private const string CapturePrefix = "PERF01_SERVER_FIRST_CHANCE ";
    private const int MaximumEvents = 32;
    private static int _captured;
    private static int _hookFailures;
    [ThreadStatic] private static bool _insideHook;

    public static void Initialize()
    {
        _insideHook = true;
        try
        {
            AppDomain.CurrentDomain.FirstChanceException += Capture;
            AppDomain.CurrentDomain.ProcessExit += OnExit;
            Console.Error.WriteLine("PERF01_SERVER_HOOK_READY");
        }
        catch
        {
            Interlocked.Increment(ref _hookFailures);
            try { Console.Error.WriteLine("PERF01_SERVER_HOOK_ERROR"); } catch { }
        }
        finally { _insideHook = false; }
    }

    private static void Capture(object? sender, FirstChanceExceptionEventArgs args)
    {
        if (_insideHook || Volatile.Read(ref _captured) >= MaximumEvents) return;
        _insideHook = true;
        try
        {
            Exception error = args.Exception;
            if (string.Equals(error.Message, ExpectedSampleMessage, StringComparison.Ordinal)) return;
            string stack = error.StackTrace ?? string.Empty;
            string stackScope = "exception";
            if (!stack.Contains("NativeWeave.Server.", StringComparison.Ordinal))
            {
                stack = new StackTrace(1, false).ToString();
                stackScope = "first-chance notification stack";
                if (!stack.Contains("NativeWeave.Server.", StringComparison.Ordinal)) return;
            }
            int number = Interlocked.Increment(ref _captured);
            if (number > MaximumEvents) return;
            Emit(CapturePrefix, writer =>
            {
                writer.WriteNumber("number", number);
                writer.WriteNumber("pid", Environment.ProcessId);
                writer.WriteNumber("managed_thread_id", Environment.CurrentManagedThreadId);
                writer.WriteString("utc", DateTimeOffset.UtcNow.ToString("O"));
                writer.WriteString("type", error.GetType().FullName ?? error.GetType().Name);
                writer.WriteString("message", Clip(error.Message, 4096));
                writer.WriteString("stack_scope", stackScope);
                writer.WriteString("stack", Clip(stack, 32768));
                if (number == 1) WriteModules(writer);
            });
        }
        catch
        {
            Interlocked.Increment(ref _hookFailures);
            try { Console.Error.WriteLine("PERF01_SERVER_HOOK_ERROR"); } catch { }
        }
        finally { _insideHook = false; }
    }

    private static void OnExit(object? sender, EventArgs args)
    {
        _insideHook = true;
        try
        {
            Emit("PERF01_SERVER_HOOK_EXIT ", writer =>
            {
                writer.WriteNumber("pid", Environment.ProcessId);
                writer.WriteNumber("captured", Math.Min(Volatile.Read(ref _captured), MaximumEvents));
                writer.WriteNumber("hook_failures", Volatile.Read(ref _hookFailures));
                WriteModules(writer);
            });
        }
        catch
        {
            try { Console.Error.WriteLine("PERF01_SERVER_HOOK_EXIT_ERROR"); } catch { }
        }
        finally { _insideHook = false; }
    }

    private static string Clip(string value, int maximum) =>
        value.Length <= maximum ? value : value[..maximum] + " [truncated]";

    private static void WriteModules(Utf8JsonWriter writer)
    {
        string? failure = null;
        writer.WriteStartArray("observed_server_modules");
        try
        {
            using Process process = Process.GetCurrentProcess();
            var paths = new HashSet<string>(StringComparer.Ordinal);
            foreach (ProcessModule module in process.Modules)
            {
                string path = module.FileName;
                if (Path.GetFileName(path) != "libnativeweave_server.so" || !paths.Add(path)) continue;
                using FileStream file = File.OpenRead(path);
                string hash = Convert.ToHexStringLower(SHA256.HashData(file));
                writer.WriteStartObject();
                writer.WriteString("file_name", Path.GetFileName(path));
                writer.WriteString("sha256", hash);
                writer.WriteEndObject();
            }
        }
        catch (Exception error) { failure = error.GetType().FullName ?? error.GetType().Name; }
        writer.WriteEndArray();
        if (failure is not null) writer.WriteString("module_observation_error", failure);
    }

    private static void Emit(string prefix, Action<Utf8JsonWriter> fields)
    {
        using var buffer = new MemoryStream();
        using (var writer = new Utf8JsonWriter(buffer))
        {
            writer.WriteStartObject();
            fields(writer);
            writer.WriteEndObject();
        }
        Console.Error.WriteLine(prefix + Encoding.UTF8.GetString(buffer.GetBuffer(), 0, checked((int)buffer.Length)));
    }
}
