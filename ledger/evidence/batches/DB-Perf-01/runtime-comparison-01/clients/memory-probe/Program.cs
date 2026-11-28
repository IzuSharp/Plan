using System.Diagnostics;
using System.Runtime;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text.Json;

// A bounded configuration check, not a database performance measurement.
// The requested heap setting is 128 MiB; keep at most 192 MiB alive to detect
// a setting that is reported but not enforced by the selected runtime.
const int MiB = 1024 * 1024;
var config = GC.GetConfigurationVariables();
var blocks = new List<byte[]>(24);
long retained = 0;
bool oom = false;
long availableBefore = GC.GetGCMemoryInfo().TotalAvailableMemoryBytes;
try
{
    for (int i = 0; i < 24; i++)
    {
        var block = new byte[8 * MiB];
        for (int page = 0; page < block.Length; page += 4096) block[page] = 1;
        blocks.Add(block);
        retained += block.Length;
    }
}
catch (OutOfMemoryException) { oom = true; }

var process = Process.GetCurrentProcess();
var result = new
{
    scope = "bounded runtime heap-limit configuration verification; no performance credit",
    requestedHeapBytes = 128L * MiB,
    runtime = RuntimeInformation.FrameworkDescription,
    dynamicCodeSupported = RuntimeFeature.IsDynamicCodeSupported,
    serverGc = GCSettings.IsServerGC,
    satoriGc = config.TryGetValue("SatoriGC", out var satori) && satori is true,
    configuration = config,
    availableMemoryBefore = availableBefore,
    availableMemoryAfter = GC.GetGCMemoryInfo().TotalAvailableMemoryBytes,
    retainedArrayBytes = retained,
    outOfMemoryObserved = oom,
    retainedArraysExceededRequestedHeap = retained > 128L * MiB,
    currentRssBytes = process.WorkingSet64,
    processPeakRssBytes = process.PeakWorkingSet64,
    gcCommittedBytes = GC.GetGCMemoryInfo().TotalCommittedBytes,
    cgroupMemoryLimitPresent = File.Exists("/sys/fs/cgroup/memory.max")
};
Console.WriteLine(JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true }));
GC.KeepAlive(blocks);
return 0;
