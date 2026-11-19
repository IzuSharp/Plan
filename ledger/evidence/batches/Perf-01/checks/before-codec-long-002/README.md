# Perf-01 codec before attempt002: accepted numerical report

This is an offline numerical projection of the existing accepted run. It adds no
load, changes no raw evidence, and grants no additional acceptance beyond the
independent verifier. The interrupted attempt001 remains separate with zero credit.

## Actual result

- Product: `ea5fa528035d025bd7a28698ee7c71194432236c`; actual Native AOT package consumer, Linux x64.
- Measurement first dispatch: 2026-11-19T21:46:34.974014+00:00.
- Measurement last observed completion: 2026-11-19T22:16:37.132710+00:00.
- Supervisor completed: 2026-11-19T22:17:58.861155+00:00; both actual exits were zero.
- Successful measurement operations: 346,005/346,005; warmup 3,861 and recovery 12, all successful.
- Independent ordinary-operation duration credit: 1802.104068505 s.
- Actual first-to-last dispatch: 1802.104435880 s; observation window: 1802.156792877 s.
- Success rate: 191.994948146/s; arrival p99: 105.719745 ms.
- Target CPU: 64.405051% of one core; sampled peak RSS: 114.906250 MiB.
- Normal owner drain: live/capacity/active = 0/0/0; separately observed idle: 60.077662539 s.

## Fields and interpretation

`summary.json` retains all 32 payload/action/interface partitions and four pooled
action/interface summaries. The eight corpus cases cover 256 B, 4 KiB, 1 MiB and
4 MiB with compressible and fixed-seed pseudorandom input. Compression and
decompression are separate. Expected partition counts follow the frozen shuffled
160-operation cycle; they are not equal subdivisions of the total.

Wall MiB/s divides original raw bytes by the full observation window. Summed-call
MiB/s divides raw bytes by summed public codec-call time and is not concurrent
throughput. Every row is a contribution to this mixed workload, not standalone
capacity. Raw/encoded ratios are computed from byte sums, not averaged ratios.
Array call time includes copying and native result retirement. Owned call time
ends before Read/Dispose; consume/release/operation fields retain those costs.
Pooled quantiles are recomputed from actual operations using the unchanged A21
percentile function, never averaged from row percentiles.

CPU/RSS and managed/native telemetry belong to the whole mixed process. The
measurement CPU bracket also includes bounded fixture/oracle/telemetry work.
GC and total-allocation deltas use the first/last telemetry observations inside
the stated interval; their actual relative endpoints are retained. They do not
precisely cover the entire measurement. Total allocated bytes use the consumer's
`GC.GetTotalAllocatedBytes(false)` observation. Per-call allocation is measured
on the worker thread before output formatting; the including-validation counter
also includes validation/ownership work. These scopes must not be equated.

The 30-second numerical resource buckets retain first/last/peak RSS, observed CPU
intervals, thread/descriptor peaks and managed/native deltas/peaks. All original
approximately one-second samples remain in the private raw evidence. Bucket
delta sums omit gaps between observation brackets; use the whole interval delta
for totals. Post-drain observations include the drained event and subsequent idle
samples. Released owners are cumulative; live is an owner count, capacity is
result Vec capacity in bytes, active is an engine-call count. No allocator/workspace
coverage or unsampled peak guarantee is implied. RSS and GC heap need not return
to zero when all owners retire.

Output copying and FFI counts are derived only for the result payload copy and
codec/result-free pair. Native allocator counts, upstream workspace peaks, all
internal copies, per-partition CPU, GC pause time and queue occupancy are unavailable.
No network compression, before/after improvement or direct-Rust gap is claimed.
The three-process frozen-noise comparator remains a separate comparison workflow.

## Integrity and publication boundary

The pinned `codec_compare.py` reads and hashes every original operation, event and
resource line and checks the complete 32-row corpus, phases, bytes, timing,
native identity, service standard and drain. This projection additionally binds
the actual supervisor/verifier to attempt002, reconciles saved partition metrics,
and matches verifier hashes, duration, lag and RSS. The original six raw hashes,
producer/corpus, acceptance and exact source hashes remain in the numerical report.

Public output is explicitly reconstructed from finite numbers, booleans, null,
fixed enums and reviewed SHA identities. It excludes raw controls, arbitrary
strings, payload contents, command lines, process IDs, process start ticks, host
paths, environment values and ownership tokens. Relative observation times are
used in JSON; the human UTC interval is stated above. The original raw data and
receipts are unchanged and are not embedded or archived here.

## Reproduction

Run outside every measurement window, on CPU8, with the locked Python and the
original retained codec002 evidence. The program acquires the existing timing
lock nonblocking and rejects existing output files. `PERF01_ROOT`, `PLAN_CHECKOUT`
and `NEW_OUTPUT` refer to the retained workspace, this Plan checkout and a fresh
output directory; no network or workload is started.

```bash
taskset -c 8 "$LOCKED_PYTHON" -B \
  "$PLAN_CHECKOUT/ledger/evidence/batches/Perf-01/checks/before-codec-long-002/project_numbers.py" \
  --root "$PERF01_ROOT" --plan-root "$PLAN_CHECKOUT" --output "$NEW_OUTPUT"
```

Reproduction binds the unchanged global freeze, original codec commands, attempt002
configuration/supervisor, comparator, A21 and verifier. Input paths are resolved
locally; only their reviewed content identities are published. The manifest
records output hashes and the actual offline projection duration. It does not
pretend that an in-process completion record is a separate observed process exit.
