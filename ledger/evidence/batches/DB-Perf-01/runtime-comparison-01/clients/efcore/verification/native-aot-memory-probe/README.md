# Bounded Native AOT GC heap-limit check

This independent .NET 11.0.0 Release Native AOT program checks whether the
runtime enforces `DOTNET_GCHeapHardLimit=0x8000000`. It is a single bounded
configuration probe, not a database test, pressure test or performance result.
It does not prove a 128 MiB limit on total client/process memory.

The algorithm matches the existing JIT/Satori probe: keep at most 24 arrays of
8 MiB alive, touch one byte every 4,096 bytes, and catch `OutOfMemoryException`.
The maximum retained-array budget is 192 MiB. JSON is written explicitly with
`Utf8JsonWriter`; reflection-dependent JSON serialization is not used.

## Observed result

| Observation | Value |
| --- | --- |
| Runtime | .NET 11.0.0 |
| Dynamic code supported / compiled | false / false |
| Server GC | false |
| GC configuration heap limit | 134,217,728 bytes |
| GC total available memory before / after | 134,217,728 / 134,217,728 bytes |
| Retained, touched arrays when allocation failed | 125,829,120 bytes (120 MiB) |
| Managed out-of-memory exception observed | true |
| Retained arrays exceeded requested heap budget | false |
| Reported GC committed bytes | 126,070,784 bytes |
| RSS / peak RSS at reporting | 131,809,280 / 131,809,280 bytes |
| Mounted cgroup memory-limit file present | false |

This execution supports that the tested Native AOT runtime actually applies
the requested **GC heap** budget. It supplies no evidence of an enforced
128 MiB process/RSS budget. A small probe's observed RSS is not a memory-limit
enforcement mechanism and cannot be substituted for the Dapper client's RSS.

The published executable SHA-256 is
`1f24ff8c0c28b68df7955e736c6d6334ef34912fe5a799f70ee383d5963538ed`.
`publish-receipt.json` records the exact command, source hashes and one-thread
IL compiler setting. `run-receipt.json` records the executed ELF identity,
environment override, result hash and timestamps. `result.json` contains the
full actual GC configuration and observed values. The single run exited 0;
the managed OOM was caught intentionally.

The source is named `Program.cs.txt` and explicitly included by this probe's
project so the surrounding frozen EF client does not discover it as another
application source. Generated outputs are excluded from its default source
glob. No frozen EF source, PDB, runtime-async receipt or original memory probe
was changed.
