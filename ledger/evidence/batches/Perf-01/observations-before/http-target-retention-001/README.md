# HTTPX target retention remaining after streamed A21 finalization

This source-only audit answers the remaining long-run memory question. The
streamed compact path removed the scheduler's repeated accepted-payload graphs
and large observation serialization. **The inherited B23 HTTPX target still
retains one normalized outcome per operation and has a full-receipt writer and
parent reader.** It is finite in request count, not constant-memory. This is
measurement-harness memory; it is not product RSS or an optimization result.

## What survives each request

| Owner / source in the pinned driver | Retention | Lifetime / bound |
|---|---|---|
| `Target.operations`, `src/Benchmarks.Domain/http_target.py:626` | Each `{id,status,value}` result | All measured and warmup outcomes until the target exits; O(requests) |
| List operation, same file `411-416` | 100 parsed title strings plus title and version lists, each 100 elements | The normalized page is appended to `operations`; identical pages are not shared here |
| Cycle operation, `391-408` | Normalized scalar outcome, including title and equality Booleans | No full replay/recovery response is deliberately kept after the task ends |
| `Target.mutations`, `385-388` | Operation/item IDs, key, scope, hash, status and initial response encoded as hex | Required by the independent durable oracle; O(committed cycles) |
| `Application.samples`, `108-118` | Every 50 ms procfs dictionary | O(application lifetime); already-written resource JSONL is also retained on disk |
| `PerfTarget.sample_generator_resources`, `tests/Perf01.Database/target.py:81-101` | One transient generator row per write | It does not accumulate its 1 Hz generator samples |
| `PerfTarget.extra` | Phase/identity/counter metadata plus configured recovery records | No inherited page-payload replacement or interning |

The full parsed page DTO dictionaries and HTTP response body are local to the
operation and its context. They are not placed in the durable result ledger.
The retained title strings are references taken from those parsed DTOs, so the
100 strings continue to live through the normalized title list. Version values
are repeated integer references, not a claim of 100 distinct integer objects.
Completed tasks are removed from the active task set. The separately bounded
in-flight tasks and contexts therefore do not explain the whole retained
per-operation graph.

## Additional drain / reporting peaks

`Target.durable_oracle` (`http_target.py:540-568`) materializes all independent SQL
rows and a key-to-mutation dictionary while the outcome, mutation and application
sample lists still live. `Database.sql` (`common.py:66-75`) uses `fetchall` for
SQLite and captured CSV output plus a tuple list for PostgreSQL. These are
post-load transients; they are not an exact SQL execution-time observer.

At final shutdown, the target sets `receipt.operation_outcomes = self.operations`
and calls `common.save` (`http_target.py:661-676`, `common.py:28-33`). That helper
builds the entire indented JSON string before writing. The pinned Python 3.12
`JSONEncoder.encode` (`json/encoder.py:200-203`) first collects encoder chunks
into a list and then joins them. Both the retained object graph and serialization
transients can coexist. A page's 200 list elements also generate many individual
JSON chunks; the final UTF-8 file size is not an upper bound on encoding memory.

Finally, `tests/Perf01.Database/run.py:298` still loads the entire application
receipt through `common.load`, even on the compact path. The code only consumes
`status`, `durable_oracle` and `closed` from that object. This parent peak occurs
after the target has exited, so it must not be added as if both complete target
and parent graphs necessarily coexist. Neither this peak nor the target's
serialization high-water mark is directly captured by the current phase sampler.

## Existing actual 120-second profile

The already completed profiling-only `db-generator-streamed-001` ran at 171/s
with 20,522/20,522 successful operations. Its target's sampled RSS peaks were:

| Phase | Target RSS peak (bytes) |
|---|---:|
| Startup and seed | 33,529,856 |
| Measurement | 152,498,176 |
| Reconciliation | 163,319,808 |
| Recovery | 163,319,808 |
| Idle | 175,685,632 |
| Final reconciliation and shutdown | 181,960,704 |

Its final application receipt is 42,562,221 bytes. These metadata are read from
the existing summary and file size, with summary/source hashes and the summary's
prior receipt hash in `audit.json`. No new load or profile was run. The scheduler's
separately recorded 90,337,280-byte lifetime peak is **not** the HTTPX target's
lifetime peak and cannot substitute for one.

A deliberately simple linear extrapolation subtracts the observed startup RSS,
scales the remaining increment by successful logical-operation count, and adds
the startup RSS again. Under that assumption, 200/s for 1802 seconds gives about
**2.1 GB** live target RSS and **0.75 GB** of final JSON; 500/s gives about **5.3
GB** live target RSS and **1.87 GB** of final JSON before accounting for encoding
chunks, SQL-oracle transients and other processes. These are illustrative
estimates, not measured peaks, hard bounds or selected PostgreSQL rates. The
120-second increment also includes time-dependent resources, and allocator/GC
behavior can change with scale.

Consequently, the 500/s request-accounting cap is **not** a demonstrated memory
budget. The current short evidence cannot certify a long-run host-memory bound
or rule out target GC/queue interference. A lower actual selected rate reduces
this exposure but does not turn these unobserved postprocessing peaks into
measurements. This note does not change the driver, the calibration selection,
any service threshold or any existing validity result.
