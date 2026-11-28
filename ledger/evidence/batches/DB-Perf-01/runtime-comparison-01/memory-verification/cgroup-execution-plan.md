# Cgroup v2 client memory boundary

## Status

**Superseded for the current campaign:** the owner subsequently accepted
192 MiB and explicitly said no cgroup was needed. See
[the current policy](../campaign/memory-policy-192.json). This historical
protocol is retained as the answer to the earlier cgroup question. It is not a
current admission requirement and is not being applied to the requested runs.

The owner asked whether cgroup can enforce the Satori client memory limit.
Yes: the Linux memory controller applies independently of the managed runtime.
This is an execution protocol for a suitable Linux host, **not evidence that
the limit has been applied or that a constrained workload completed here**.

[cgroup-environment.json](cgroup-environment.json) records the actual current
namespace: UID 1000, membership `0::/`, no cgroup mount in `/proc/self/mountinfo`,
and no `/sys/fs/cgroup` directory. There is no accessible delegated memory
controller with which to establish this task's client boundary. This observation
does not establish that the host or an inaccessible ancestor is unrestricted.
No host security or parent resource settings were changed.

## Exact boundary

The task uses 128 MiB = **134,217,728 bytes** for the owner's 128 MB C# budget.
On a host with a delegated cgroup v2 memory controller, create a fresh leaf for
one client cell and set these values before starting its executable:

| Interface | Value | Meaning |
| --- | ---: | --- |
| `memory.max` | `134217728` | Kernel-enforced cgroup memory boundary |
| `memory.swap.max` | `0` | No anonymous swap allowance |
| `memory.oom.group` | `1` | Treat the client group as one workload on group OOM |

Use the same boundary and launch procedure for each C# runtime. Do not substitute
`GCHeapHardLimit`, sampled RSS, a virtual-address-space limit, or a requested
configuration value for this enforcement. Leave `memory.high` unchanged unless
a separate explicitly recorded experiment selects throttling; it is not the
hard limit. Preserve the historical CPU affinity independently of this memory
boundary.

The budget is the controller's **charged memory**, not a byte-for-byte RSS
counter or just the managed heap. It includes charged anonymous memory, file
cache and kernel memory. Shared pages retain cgroup ownership according to the
kernel's accounting rules. The kernel documents that usage can temporarily
exceed `memory.max`; when reclaim cannot satisfy the boundary, a group-local OOM
or allocation failure is possible. Do not claim a strict instantaneous RSS cap.

Put the child in the new group **before `exec` of the client runtime and before
warmup**. Moving an already warmed client is insufficient: existing memory
charges do not move with the PID, and the runtime may have cached its startup
memory budget. Keep the supervisor, observer and PostgreSQL server outside the
client group. Do not launch the server as a descendant after entering the group.

PostgreSQL's server memory has no additional task-imposed cap. Its historical
`shared_buffers=128MB` setting is preserved and is not a total server limit.
SQLite runs inside the client process: its native heap, page cache and driver
memory are included in the client boundary. A cgroup cannot exclude SQLite's
memory while including the C# runtime in the same process.

## Admission and observation on a capable host

1. Record the delegated mount, parent/controller state, applicable ancestor
   limits and new empty leaf. Apply and read back all three values above.
2. Launch the actual release executable inside that leaf. Record its
   `/proc/PID/cgroup`, loaded runtime hashes and GC-reported available memory.
   The runtime's view is a separate observation from the kernel's enforcement.
3. Verify that PostgreSQL and the observer have different membership. Use a
   fresh copy of the SQLite fixture and document page-cache ownership and warmup
   consistently; cgroup file-cache charges need not equal the process RSS.
4. Run a bounded admission/configuration check, then the 35 correctness cases.
   Capture `memory.current`, `memory.peak`, `memory.stat`, `memory.events`,
   `memory.swap.current` and `memory.pressure` where available. Retain unsupported
   counters as unavailable, never zero.
5. Rebuild and rebind any preparation consumer whose admission code changes.
   The currently frozen EF preparation build intentionally refuses a requested
   1,800-second interval because enforcement has not been attested. Do not
   relabel its existing short results or remove that check without establishing
   the actual boundary and recording the new build identity.
6. Only then admit the serial long cells. Observe from outside the client
   group and retain final counters even if the client dies. Record exit status,
   OOM counter deltas, completed duration and partial operations. An OOM-ended
   attempt is a failure under this budget, not a completed 30-minute result;
   do not restart it silently or increase the limit.

Satori surviving and performing well within this boundary remains unmeasured.
The ability of the kernel to enforce a limit does not prove that the collector
will reclaim early enough to avoid an OOM under the selected mixed workload.

## Primary references

- [Linux cgroup v2 memory controller](https://docs.kernel.org/admin-guide/cgroup-v2.html#memory)
- [Linux cgroup v2 memory ownership](https://docs.kernel.org/admin-guide/cgroup-v2.html#memory-ownership)

The kernel documents `memory.max`, `memory.swap.max`, `memory.oom.group`, charged
memory ownership, and OOM behavior. Actual access and actual Satori behavior
remain the separate local observations linked above and in this directory.
