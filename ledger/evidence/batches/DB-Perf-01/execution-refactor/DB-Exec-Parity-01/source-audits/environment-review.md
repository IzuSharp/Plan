# DB-Exec-Parity-01 — independent review of local observation probes

## Disposition

**Accepted for a narrow environment-capability claim:** the recorded Linux environment permits a user-mode, calling-thread `perf_event_open` software CPU-clock sampler; sampled IPs resolve against the retained native probe ELF to source, an inline frame and machine instructions. A second probe also records this thread's switch-out/switch-in timestamps using `PERF_RECORD_SWITCH` on the sampled event.

**Not accepted as product profiling, a complete scheduler trace, hardware-instruction accounting, or a lossless production profiling implementation.** These are standalone GCC native probes, not Korda, Dapper, .NET Native AOT, SQLite or PostgreSQL consumers. No product hotspot conclusion follows.

I reviewed both `.c` sources, both `.jsonl` outputs, both summary JSON files, retained ELF files, `readelf`/`objdump` text, the environment collector, and the SHA-256 manifest. I independently recomputed all manifest hashes (no mismatches), counted raw JSONL event kinds, recomputed timing deltas and switch pairs, re-read ELF headers, and ran `addr2line -f -C -i` against all unique perf sample IPs. I did not rebuild or rerun either workload.

## Observed evidence

| Item | First probe | Scheduler-enabled probe | Meaning |
| --- | --- | --- | --- |
| CPU-clock event | Open succeeds, fd 3, errno 0 | Open succeeds, fd 3, errno 0 | Actual permission and event creation demonstrated. |
| Ring mmap | Succeeds | Succeeds | Actual sampled-data delivery path demonstrated. |
| CPU samples in raw JSONL | 299 | 299 | Nonempty, plausible calling-thread user IP samples, not just successful open. |
| Signal samples | 74 | 74 | Separate supporting ITIMER_PROF address sampling. Requested 1 ms is not demonstrated 1 kHz delivery. |
| Context-switch count event | exclude_kernel=1, opens; 8-byte count reads **0** | exclude_kernel=0, open fails errno **13** | First zero is not a usable switch census; second capability is denied. |
| sched_switch tracepoint ID path | ENOENT | ENOENT | This tracefs path unavailable. Does not erase switch metadata from the other perf event. |
| PERF_RECORD_SWITCH | Not requested / not emitted | **4 records**, same PID/TID 10/10 | Two paired off-CPU intervals for this thread. |
| rusage switch deltas across work+wait | 6 involuntary + 1 voluntary | 1 involuntary + 1 voluntary | Aggregate corroboration, not a wakeup timeline. |
| /proc/self/schedstat | Read succeeds | Read succeeds | Aggregate on-CPU/runqueue/slice counters, not per-wait attribution. |

The first probe's work interval is 300,010,305 ns wall and 299,947,209 ns thread CPU; its wait interval is 20,150,752 ns wall and 67,281 ns thread CPU. The second work interval is 300,043,885 ns wall and 300,027,650 ns thread CPU; its wait interval is 20,228,358 ns wall and 114,110 ns thread CPU. These intervals contain observer/printing/timer overhead and sequential, non-atomic clock reads; they are capability examples, not precision overhead measurements.

The scheduler probe records these pairs in `CLOCK_MONOTONIC_RAW`:

| Switch-out ns | Switch-in ns | Difference ns | Observed relation |
| ---: | ---: | ---: | --- |
| 57,248,782,860,906 | 57,248,782,885,312 | 24,406 | Inside busy-work phase. No individual waiting cause is serialized. |
| 57,248,907,273,752 | 57,248,927,416,763 | 20,143,011 | Inside the explicit nanosleep phase. This is off-CPU duration, not solely wakeup/runqueue latency. |

All 299 second-probe CPU sample timestamps fall between its recorded work_start and work_end, and all have the same PID/TID. The event has `use_clockid=1` with `CLOCK_MONOTONIC_RAW`, so its retained times can be compared with this probe's same-clock boundaries. Do not compare them directly with arbitrary CLOCK_MONOTONIC timestamps from other instrumentation without a clock-domain conversion.

## Symbol and machine-code binding

Both binaries are ELF64 x86-64 `ET_EXEC` (non-PIE), so these recorded absolute IPs do not require a PIE load-bias correction. All unique perf IPs resolve to `mix_value` inlined into `measured_busy_work` in the corresponding preserved source. For example, scheduler-probe IP `0x401ec7` has 136 samples and resolves to `mix_value` line 42, inline caller `measured_busy_work` line 52. The preserved `objdump` contains the matching machine address and instructions in `measured_busy_work` with the inline source mapping.

Original executable SHA-256 values at review:

- `self_probe`: `579e8221fbace6ae264742b0bd25fbee8567356a4a522b36b0fe56886ae8984c`.
- `self_probe_sched`: `7dfadb5e68002c9a4276ea760b286538f240bdad0ee47722c044d1ac575ad800`.

This demonstrates symbol resolution of sampled instructions, not a statistical claim that a particular instruction consumed a precise fraction of CPU cycles. The event is a software CPU-clock timer and does not measure instructions retired, hardware cycles, branch misses, cache misses or precise-IP sampling. Perf and SIGPROF run simultaneously and perturb the loop. Native AOT executables and shared native libraries will need their own build IDs, exact debug files, mappings/load biases, generated-source identities and observed sample bindings.

The retained manifest/collector currently has no standalone compile-command receipt for these two probes. Preserve the actual compiler commands and execution receipt from the root's tool history if the capability record is to be reproduced independently; do not invent them from likely flags. This does not invalidate the observed binary/IP/source linkage.

## Ring parser assessment

The inspected `/usr/include/linux/perf_event.h` documents the layouts used here. For `PERF_SAMPLE_IP | PERF_SAMPLE_TID | PERF_SAMPLE_TIME`, a sample payload is `u64 ip; u32 pid,tid; u64 time`. For `PERF_RECORD_SWITCH` with `sample_id_all`, there is no additional switch payload before the sample-ID suffix; the selected identity fields are `u32 pid,tid; u64 time`. Thus the second probe's two struct layouts and switch direction bit are correct for the configured event. IP is intentionally absent from the non-sample sample-ID suffix. An acquire load of `data_head` is appropriate before reading the ring.

These limitations must be preserved in the report and fixed before using this parser for product attribution:

1. The code does not record/check return values for reset/enable/disable ioctls. Nonempty samples establish that sampling worked in these runs, but absent events alone could not distinguish a zero workload from an ioctl failure.
2. It assumes ring offset/size from the requested mapping instead of checking `data_offset` and `data_size`. It checks only generic header size; it does not enforce event-specific minimum size, `tail + size <= head`, or explicitly record final head/tail and parse completion. Raw ring/header bytes are not retained, so JSONL cannot independently establish exhaustive parsing.
3. `lost_records` counts PERF_RECORD_LOST headers, not the header's `lost` event count. It also ignores THROTTLE/UNTHROTTLE and other record types. The defensible statement is **no PERF_RECORD_LOST record was reported by this probe**, not an unqualified lossless-capture guarantee.
4. It does not advance `data_tail`; this is acceptable only for its short stop-then-read capability demonstration. A long run must drain continuously, preserve ordering on tail writes and report losses/overruns. The visible second-probe payload is only 9,664 bytes (299×32 + 4×24), below the requested 32 KiB data ring, but this reconstruction does not replace retained head/tail/header validation.
5. The switch JSON serializes only `PERF_RECORD_MISC_SWITCH_OUT`; it discards the preemption flag and has no `PERF_SAMPLE_CPU`, next/previous task identity, wakeup record or lock information. Hence per-record involuntary/preempt reason and cross-thread causality remain unknown.

No parser issue found overturns the narrow conclusion that nonempty CPU samples and switch metadata arrived for this native probe. The issues do block promotion of this code unchanged to a production-quality, exhaustive event recorder.

## Scope and clock corrections

`perf_event_open(... pid=0, cpu=-1 ...)` with zero-initialized `inherit=0` observes the **calling thread**, not all threads in a process. This probe is single-threaded, so the records' `self-process` wording should be interpreted and reported as “self-thread native capability probe.” It does not demonstrate permission to attach to another thread/process or an entire PostgreSQL server. The next multithreaded consumer needs explicit per-thread attachment/inheritance and thread lifetime/mapping capture, verified in that environment.

`RUSAGE_THREAD`, thread CPU clocks and the perf event agree on the same single thread here. In a multithreaded workload, `/proc/self/schedstat` is not a substitute for `/proc/self/task/<tid>/schedstat`. CPU-clock deltas from different TIDs cannot be subtracted. C argument evaluation order makes the clock and CPU readings in `printf` sequential and not necessarily source-order; avoid nanosecond-level wall-minus-CPU attribution from these endpoints. `clock_ns` also returns zero without recording an error; a reusable recorder must report clock errors.

ITIMER_PROF counts process CPU and signals can coalesce; the retained 74 samples over roughly 0.3 s demonstrate delivery, not the requested 1000 samples/s. Sampling and output scopes must separate profiling perturbation from formal timings. There is no per-request correlation or allocation/copy instrumentation in these capability probes.

## Approved wording and blocking boundary

Suggested claim: “An independent native self-thread probe successfully collected 299 software CPU-clock samples in each of two runs, resolving the retained ELF IPs to an inline function and its machine instructions. The second run recorded four self-thread switch-in/out records on a common monotonic-raw clock. Aggregate rusage/schedstat also worked. sched tracefs was absent, the kernel-inclusive switch-count event was denied, and wakeup/lock-owner/per-instruction costs remain unobserved.”

Do not say perf is wholly blocked merely because the `perf` executable is absent, and do not say scheduling is wholly invisible after the second probe. Equally, do not call this a complete scheduler trace or proof of database-stage attribution.

**Product Stage 1 remains open** until actual locked Korda/Dapper Release Native AOT consumers, SQLite/PostgreSQL engines, generated readers, matching symbols/machine-code samples and per-business observations are collected. An environment probe cannot replace that gate. Toolchain/dependency availability is a separate prerequisite; transient network failures must be reported with their actual attempt receipts and updated when later retries succeed.
