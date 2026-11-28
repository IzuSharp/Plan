using System.Runtime;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Security.Cryptography;

internal sealed record MappedRuntimeImage(string Path, string Sha256);
internal sealed record RuntimeIdentity(
    string FrameworkDescription, string EnvironmentVersion, bool DynamicCodeSupported,
    bool DynamicCodeCompiled, bool IsServerGc, bool SatoriGc,
    Dictionary<string, string> GcConfiguration, MappedRuntimeImage[] RuntimeImages,
    string ManagedAssemblySha256, string? CgroupMembership,
    string ClientMemoryBudgetStatus, long RequestedClientBudgetBytes,
    bool ClientMemoryBudgetEnforced, bool TimingComparisonEligible, string[] AdmissionFailureReasons,
    long RequestedGcHeapBudgetBytes, ulong ObservedConfiguredGcHeapHardLimitBytes,
    long GcTotalAvailableMemoryBytesAtStartup, bool GcHeapBudgetEnforcementProven,
    bool OwnerAcceptedUnenforcedMemoryPolicy, string MemoryPolicy,
    string EvaluatedCompilerFeatures, bool RuntimeAsyncMetadataPresent,
    int RuntimeAsyncMethodCount, string[] RuntimeAsyncMethodExamples)
{
    internal static RuntimeIdentity ReadAndValidate()
    {
        if (!RuntimeFeature.IsDynamicCodeSupported || !RuntimeFeature.IsDynamicCodeCompiled)
            throw new InvalidOperationException("This EF Core lane requires the JIT runtime.");
        var values = GC.GetConfigurationVariables();
        var isSatori = values.TryGetValue("SatoriGC", out var value) && value is true;
#if EXPECT_SATORI
        if (!isSatori) throw new InvalidOperationException("The published Satori build did not load Satori GC.");
#else
        if (isSatori || GCSettings.IsServerGC)
            throw new InvalidOperationException("The stock comparison must load Workstation GC.");
#endif
        var images = File.ReadLines("/proc/self/maps")
            .Select(line => line.Split(' ', 6, StringSplitOptions.RemoveEmptyEntries))
            .Where(parts => parts.Length == 6)
            .Select(parts => parts[5])
            .Where(path => Path.GetFileName(path) is "libcoreclr.so" or "libclrjit.so" or "libclrgc.so" or "libclrgcexp.so")
            .Distinct(StringComparer.Ordinal)
            .Order(StringComparer.Ordinal)
            .Select(path => new MappedRuntimeImage(path, HashFile(path)))
            .ToArray();
        if (!images.Any(image => Path.GetFileName(image.Path) == "libcoreclr.so")
            || !images.Any(image => Path.GetFileName(image.Path) == "libclrjit.so"))
            throw new InvalidOperationException("Could not prove the actual CoreCLR/JIT image identities.");
        var assembly = typeof(RuntimeIdentity).Assembly;
        var compilerFeatures = assembly.GetCustomAttributes<AssemblyMetadataAttribute>()
            .Single(attribute => attribute.Key == "CompilerFeatures").Value ?? "";
        var asyncMethods = assembly.GetTypes()
            .SelectMany(type => type.GetMethods(BindingFlags.Public | BindingFlags.NonPublic
                | BindingFlags.Static | BindingFlags.Instance | BindingFlags.DeclaredOnly))
            .Where(method => (method.GetMethodImplementationFlags() & MethodImplAttributes.Async) != 0)
            .Select(method => method.DeclaringType!.FullName + "." + method.Name)
            .Order(StringComparer.Ordinal).ToArray();
        if (!compilerFeatures.Split(';').Contains("runtime-async=on", StringComparer.Ordinal)
            || asyncMethods.Length == 0)
            throw new InvalidOperationException("The application does not contain the requested runtime-async compiler feature and Async method metadata.");
        const long requestedGcHeapBudgetBytes = 201_326_592;
        if (!values.TryGetValue("GCHeapHardLimit", out var heapLimitValue)
            || Convert.ToUInt64(heapLimitValue, System.Globalization.CultureInfo.InvariantCulture) != requestedGcHeapBudgetBytes)
            throw new InvalidOperationException("The accepted comparison policy requires an observed 192 MiB GCHeapHardLimit configuration value.");
        var configuredHeapLimit = Convert.ToUInt64(heapLimitValue, System.Globalization.CultureInfo.InvariantCulture);
        return new(
            RuntimeInformation.FrameworkDescription, Environment.Version.ToString(),
            RuntimeFeature.IsDynamicCodeSupported, RuntimeFeature.IsDynamicCodeCompiled,
            GCSettings.IsServerGC, isSatori,
            values.ToDictionary(pair => pair.Key, pair => Convert.ToString(pair.Value,
                System.Globalization.CultureInfo.InvariantCulture) ?? "null", StringComparer.Ordinal),
            images, HashFile(typeof(RuntimeIdentity).Assembly.Location),
            File.Exists("/proc/self/cgroup") ? File.ReadAllText("/proc/self/cgroup") : null,
            "Owner explicitly accepts a 192 MiB GC configuration without cgroup enforcement. Report actual GC availability/RSS and any excess; no total client-memory cap or Satori heap-limit enforcement is claimed.",
            requestedGcHeapBudgetBytes, false, true, [],
            requestedGcHeapBudgetBytes, configuredHeapLimit, GC.GetGCMemoryInfo().TotalAvailableMemoryBytes,
            false, true, "owner-accepted-192MiB-GC-configuration-without-cgroup; external runner checks business correctness and duration",
            compilerFeatures, true, asyncMethods.Length, asyncMethods.Take(16).ToArray());
    }

    private static string HashFile(string path)
    {
        using var stream = File.OpenRead(path);
        return Convert.ToHexStringLower(SHA256.HashData(stream));
    }
}
