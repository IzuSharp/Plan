# PostgreSQL 200/s: short pass and first confirmation capacity rejection

The completed `08-refine-200` 30-second cell passed. The completed
`10-confirmation-0-200` 60-second cell failed **only** the recorded A21
`generator saturation: in-flight capacity` gate. Both results remain unchanged.
This is a read-only comparison of existing metadata and the small application /
generator procfs series, while the later calibration cells continue separately.
No new workload, profile, SQL query or operation-ledger analysis was performed.

| Observation | 200/s for 30 s | First 200/s for 60 s |
|---|---:|---:|
| Offered | 6,001 | 12,001 |
| Dispatched and successful | 6,001 | 11,884 |
| Rejected before dispatch | 0 | 117 |
| Successful-operation p99 | 116.193470 ms | 3,053.415963 ms |
| Measured durable commits | 3,001 | 5,942 |
| App CPU (% of one core) | 92.086526 | 90.002641 |
| App RSS peak | 43,950,080 B | 63,778,816 B |
| Scheduler CPU (% of one core) | 11.533967 | 12.377303 |
| HTTPX target CPU (% of one core) | 63.265951 | 71.848392 |
| Scheduler RSS peak | 35,438,592 B | 49,999,872 B |
| HTTPX target RSS peak | 68,464,640 B | 101,519,360 B |

All actually dispatched logical operations succeeded. Provider exceptions,
classified HTTP failures and the permanent integrity halt were absent. Both
independent durable checks passed and both closed receipts released consumer /
database owners and reached server `Disposed`.

## What the recorded capacity gate means

In the pinned A21 source `src/Benchmarks.Harness/nativeweave_bench.py:723-734`, the
scheduler rejects a scheduled operation before writing it when its outstanding
set already contains 512 operations. This set spans IPC, target queuing, active
HTTP operations and completion observation. It does not measure a native queue.
In `src/Benchmarks.Domain/http_target.py:595-609`, admission is emitted only after
the C16 HTTP-client semaphore has been acquired. Outstanding scheduler work may
therefore be waiting before HTTP admission.

Neither cell records a dispatch-lag violation. This distinguishes the **recorded
failure reason** from the previous Python scheduler GC/dispatch-lag problem; it
does not establish the cause of this cell's accumulated outstanding work. The
capacity check precedes the lag check, and the rejected operations have no actual
dispatch time. A statement that PostgreSQL, Rust, a native queue or a specific GC
pause caused the slowdown would exceed this evidence.

## Available interval observations

The failed cell's application CPU in successive approximate 10-second bins was
67.7%, 99.6%, 95.4%, 92.8%, 92.9% and 91.7% of one core. The HTTPX target's values
were 67.9%, 95.3%, 79.4%, 64.0%, 60.6% and 61.8%; scheduler values stayed near
10–14%. App RSS peaked during the first 10 seconds and remained below that peak
in later bins. These sampled process observations cannot locate the queue or
prove the initiating event. Exact bin endpoints and counter deltas are in
`audit.json`; each bin is relative to the first application measurement sample,
not an independently recovered operation start.

The failed cell's maximum observed scheduler sample gap was 1.048004164 seconds
at nominal 1 Hz. The maximum wall interval for one scheduler procfs sample was
1.491540 ms. The separate application series, nominally 50 ms, had a maximum
122.757976 ms gap. These are observer intervals, not GC pause measurements.

Both route descriptors have `instrumented=false`; the application receipt's
`last_probe` is null and its diagnostics oracle explicitly reports no benchmark
instrumentation. Managed GC/alloc intervals, native queue depths, Python GC
callback intervals, PostgreSQL process CPU/RSS and exact pool/SQL/lock waits are
**unavailable** in these ordinary cells. The earlier separate PostgreSQL statement
profile remains a different workload observation, not a decomposition of this
failed cell.

Target RSS rises with duration in both cells. The historical B23 target retains
operation results; this growth alone cannot be classified as a leak. The
original operation and event ledgers remain available but were not scanned for
this bounded review. `audit.json` binds the summary/frozen metadata and resource
series hashes; it records the summary's prior whole application-receipt hash and
a fresh hash of the bounded prefix used for the null-probe observation.
