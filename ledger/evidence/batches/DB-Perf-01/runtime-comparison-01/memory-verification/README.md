# Observed C# memory configuration behavior

These are bounded configuration probes, not database pressure tests. Both builds
used the same source in `../clients/memory-probe`, requested
`System.GC.HeapHardLimit=134217728`, and retained at most 24 arrays of 8 MiB. Every
array was touched once per memory page. PostgreSQL was not involved or limited.

| Observed value | Stock Workstation | Satori |
| --- | ---: | ---: |
| Runtime | .NET 11.0.0 | .NET 11.0.2-ci |
| Satori configuration marker | false | true |
| Reported HeapHardLimit | 134,217,728 B | 134,217,728 B |
| Available memory reported by GC | 134,217,728 B | 10,451,427,328 B |
| Successfully retained array bytes | 125,829,120 B (120 MiB) | 201,326,592 B (192 MiB) |
| OutOfMemoryException observed | yes | no |
| GC committed bytes | 126,070,784 B | 217,579,520 B |
| Process RSS at observation | 157,945,856 B | 248,610,816 B |

The standard runtime enforced its GC heap setting. This is not a 128 MiB limit
on the whole client process: its observed RSS was larger. The selected Satori
runtime read and reported the same setting but demonstrably retained more than
128 MiB of managed arrays. The setting cannot be credited as an enforced Satori
heap bound. Its `GCSettings.IsServerGC` was true even though the enumerated
ServerGC configuration value was false; use the explicit Satori marker and the
loaded runtime hashes to identify it.

A separate run of the same Satori executable additionally supplied the documented
environment form `DOTNET_GCHeapHardLimit=0x8000000`. It likewise retained all
192 MiB without OutOfMemoryException and continued to report the host-sized
available-memory budget. Its separate result and command receipt are retained;
switching configuration transport did not resolve the enforcement difference.

Raw result JSON, runtime binary/configuration hashes, exact build/run commands
and logs are in this directory. The probe is bounded at 192 MiB of retained
arrays and does not infer an unmeasured maximum for Satori. It does not establish
the memory behavior of a full EF workload.

The current execution environment has no mounted cgroup interface or accessible
`memory.max`. No client process hard memory boundary has been established. A
different enforcement mechanism must be verified before a Satori result may be
described as a 128 MB constrained comparison. Database memory is outside this
client requirement. No system security or parent resource settings were changed.

The owner subsequently requested `runtime-async=on` for the JIT database
consumers. This probe contains no async methods and does not use that compiler
feature. Its identity and results remain this configuration check; the revised
EF consumers require their own fresh builds and correctness receipts.
