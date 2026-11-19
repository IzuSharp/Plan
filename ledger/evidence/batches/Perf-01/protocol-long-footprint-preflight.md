# Perf-01 protocol long-run footprint preflight

## Status and method

This is a source and filesystem-metadata inspection requested before the paired
long runs. It is **not a load, allocation measurement, test, benchmark, or long-run
acceptance result**. All local inspection ran on CPU 8 during the integration
owner's exclusive DB calibration. Only source files, small plan metadata, and
file sizes were read; the large request/event/client ledgers and result histogram
documents were not scanned or decoded. The inspection itself made no product,
protocol-driver, or verifier implementation changes. A subsequently authorized
post-run verifier fix is recorded separately below.

The inspected integration checkout was
`ce2a3c75cbd535490897d062b6cbb7c095408307` with these actual source hashes:

| Source | SHA-256 |
|---|---|
| `tests/Perf01.Protocols/run.py` | `ee5867cfd5c29b52595b96a69328fc612c88ebdd38fd5796ed7582102c4c49b4` |
| `tests/Perf01.Protocols/adapter.py` | `21254a039396e8de485d5729cc3a7236e4c12ae7b41a4427f703af86e3e77f69` |
| `tests/Perf01.Protocols/Client/Program.cs` | `6bfc40c993b7f02ffd4406606d78b692c298482cc786717cdd05316688a4ea4d` |
| `tests/Perf01/verify_long.py` | `8034692b643f4dbb1385cd61e25c9d4d6f084d7b71268fec02411b5c2fcdbeb4` |
| `src/Benchmarks.Harness/nativeweave_bench.py` | `dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53` |

## Observed existing file sizes

Root directory:
`/workspace/scratch/01c249676f47/perf01-evidence/calibration/before-http-v3r1`.
The small plans identify each final 1152/s confirmation as 60 seconds and
**69,237 scheduled operations**. Sizes below are actual filesystem byte counts;
this inspection did not recompute the large files' hashes or reevaluate their
validity.

| File | `16-confirmation-0-1152` | `17-confirmation-1-1152` | `18-confirmation-2-1152` |
|---|---:|---:|---:|
| `result.json` | 5,733,195 | 6,769,234 | 5,190,246 |
| `plan.json` | 14,275 | 14,275 | 14,275 |
| `oracle.json` | 6,771,342 | 6,771,342 | 6,771,342 |
| `requests.jsonl` | 22,380,116 | 22,380,116 | 22,380,116 |
| `events.jsonl` | 15,106,165 | 15,106,165 | 15,106,165 |
| `dispatches.jsonl` | 7,604,960 | 7,604,960 | 7,604,960 |
| `execution/client/operations.jsonl` | 30,186,897 | 30,186,897 | 30,186,897 |
| `execution/process-resources.jsonl` | 421,612 | 421,671 | 421,679 |
| `execution/server/managed-resources.jsonl` | 58,430 | 58,418 | 58,397 |
| `execution/receipt.json` | 15,228 | 15,231 | 15,231 |

## Finite population and pending work

`run.py:78-83` uses the rounded nanosecond period and includes one dispatch-lag
allowance in its finite population. The following are arithmetic projections of
the requested prospective rates, not a final rate selection or actual dispatch:

| Group / rate | Duration | Period | Planned operations | Deadline-heap bound |
|---|---:|---:|---:|---:|
| HTTP at 500/s | 1802 s | 2,000,000 ns | 901,051 | 12,501 |
| gRPC at 166/s | 1802 s | 6,024,096 ns | 299,150 | 4,152 |

Both populations remain below the existing one-million-operation limit. The
controller's outstanding admission set is limited to 1024. The C# client uses a
bounded 1024-command channel and 64 fixed workers for this profile
(`Client/Program.cs:73-90`); each operation is written directly to JSONL before
its completion event (`:93-128`). It has no retained list of all operation result
objects. The Python adapter forwards one command/event at a time through bounded
pipe buffers. These are separate configured bounds, not an assertion that all
queues are simultaneously full.

The A21 deadline heap retains entries until their deadlines expire, even when a
call has already completed (`nativeweave_bench.py:402-409`). With the 25-second
timeout and a regular frozen schedule, its upper count is
`ceil(25_000_000_000 / period_ns) + 1`, capped by the total population. It is not an
unbounded accumulation of every completed call.

The client deliberately retains the five payload arrays and five protobuf
backings. Their byte payload sum is **19,013,760 bytes**, independent of operation
count (`Client/Program.cs:47-54`); object headers and active request/response
buffers are additional. The server's existing payload, request, connection, and
stream quotas remain separate. This preflight does not infer server RSS from
those quotas.

## Controller retention and finalization

The protocol controller still uses the ordinary A21 Oracle and RunState. The
Oracle decodes the full array of short input/expected token pairs
(`nativeweave_bench.py:165-204`); RunState retains one scalar record and completion
membership per operation, plus the short observed token (`:379-461`). Counter
metadata is one shared dictionary assigned to completions by `run.py:209-210`,
then removed from each raw request record before JSONL output (`:315-318`). The
large DB page-result graphs that motivated the DB journal are absent here, but
the controller is still **O(N)** in Python objects.

Preparation also builds the finite Oracle entry array and writes it with the
whole-document `save` helper (`run.py:37-41,104-105`). A simple file-size ratio
from the existing mix projects an approximately **88.1 MB** Oracle at 901,051
operations. This is a decimal-MB storage projection, not a measured long file or
Python RSS estimate. Runtime Oracle loading additionally creates the decoded
object graph. Exact CPython allocation and RSS were not measured in this check.

The final request ledger is emitted one row at a time; the result does not embed
that full record array. Summarization reads independent client rows one at a time
and retains two signed-64-bit latency arrays totaling at most `16*N` payload
bytes, plus a two-event concurrency array of another `16*N` bytes
(`run.py:366-440`). At the projected HTTP count, each pair is 14,416,816 bytes;
at the projected gRPC count, each pair is 4,786,400 bytes. Python/container
overhead, list conversions for sorting, and histogram maps are additional.

Five whole-profile histograms and two histograms per scenario remain in the
result. A21 preserves sparse integer bins and computes exact nearest-rank tails
using sorted samples (`nativeweave_bench.py:215-247`). Bin populations depend on
the data, with a loose finite bound of seven times the operation count across
the five global histograms plus the two partitioned scenario histograms. The
final `save` constructs the complete pretty JSON text while the result and A21
state are still alive. There is consequently no small constant bound on the
controller's postprocessing peak.

Adapter process samples and the controller's resource-summary input grow at
approximately one sample per second, rather than one full object per request.
Sampling ends when the adapter closes, **before** controller histogram building
and final JSON serialization (`adapter.py:86-97,183-194`; `run.py:285-319`). The
existing traces can show live-load controller RSS but do not observe its later
postprocessing peak. That peak remains unavailable in this metadata check.

## Concrete common-verifier size hazard

`verify_long.py:366-367` currently loads `result.json` through `Evidence.load`,
which rejects any document above **64 MiB = 67,108,864 bytes** (`:194-197`). The
result's variable histogram maps make it unsuitable for an assumed small-summary
bound. Scaling only the three observed result sizes by population gives
**74.612 MB, 88.095 MB, and 67.546 MB** at 901,051 operations. These are illustrative
size projections: repeated bins may reduce growth, so they are not a prediction
of the actual final file. The source nevertheless provides no guarantee that an
otherwise valid long result remains below the verifier's hard limit.

The verifier already streams the Oracle, independent client results, request
records, and resource rows (`:390-426`). Its own per-request bookkeeping is three
bytearrays (span IDs, token indices, client IDs), plus a token vocabulary limited
to 256. The other fully loaded protocol inputs are the small plan, adapter, and
retirement receipt; their schema does not contain the large record collections.

The narrow remedy to consider before long acceptance is to project only the
consumed result metadata and nested exact-tail fields with the existing
streaming JSON reader, preserving the complete original result/histogram bytes
and their hash. Increasing the 64 MiB guard alone would retain the whole decoded
histogram graph. This preflight proposes no live-driver, workload, statistics,
or binary change. The integration owner must authorize and review any verifier
change; the subsequently authorized scoped change is recorded below.

The finite queue and record limits are established from source. A low generator
RSS or acceptable postprocessing peak is **not** established. Before/after
comparability still requires the same frozen driver and actual valid generation;
this note grants no performance or 30-minute duration credit.

## Subsequently prepared verifier fix

After receiving this preflight, the integration owner authorized the minimal
post-run remedy. Product commit
`4c28329129ce50cc8273128889c349e97410c795`, based on the inspected `ce2a3c75`,
changes only protocol result projection and adds three finite synthetic test
methods and documentation. The new verifier SHA-256 is
`3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82`.
It pins the complete original result before parsing, validates skipped JSON and
EOF, retains every consumed original field including profiling/invalid flags,
five counts, recovery, measurement span/resource window, hashes and nested p99,
and leaves all subsequent acceptance checks unchanged. The generic reader,
`Evidence.load`, DB/codec paths, result schema, timing drivers, A21 and product
runtime are unchanged.

The codec reviewer independently passed the three-file source diff. The finite
tests cover the oversized-summary metadata boundary with multi-chunk JSON while
forbidding a whole-result read or decoded histogram map; they also retain the
negative field/hash/recovery/tail and malformed-skipped-JSON gates. No syntax
execution, tests, build or load has been performed for this patch at this
checkpoint. The root owner must execute its finite gate in an authorized window.

Documentation-only follow-up
`1f0b3930458c21c325b2e3c7a57fdf73fd76de02` distinguishes the integration decision
from actual checkout creation: all future DB timing routes are to use a detached
`ce2a3c75cbd535490897d062b6cbb7c095408307` checkout at
`ROOT/.worktree/Perf-01-frozen-drivers-linux/NativeWeave`, preserving the original
`8034692b...` timing-parser bytes and final-v5 noise provenance. Its creation and
identity verification remain the root owner's pending step. The main post-run
verifier may advance independently and records its own exact hash in each new
acceptance receipt. This source-only note does not claim that the planned frozen
checkout has already been created.
