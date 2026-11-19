# Perf-01 protocol layered profiles

Status: source-prepared configurations only; no profile, workload, build or test
was executed while preparing this directory. Root owns execution after the
current calibration window. These profiles supplement the existing long mix;
`tests/Perf01.Protocols/profile-v1.json` remains unchanged. Before product edits,
root selected the separate `../grpc-budget-profile-v2.json` for new gRPC mixed
calibration and both paired versions. It changes only the per-request retention
cap to 64 MiB. The two gRPC partitions below now use that same cap. HTTP profiles
and their 4 MiB per-request cap remain unchanged.

Independent source review by the codec agent checked all eight files against
the base, catalog SHA-256 values, count arithmetic, immutable fixture/client
paths, byte/protobuf checks, commands, and allocation/RSS interpretation. No
source blocker remained. That review ran no harness, build, workload or test;
actual wire execution and measurement validity remain root's gates.

The baseline application is the immutable package Native AOT server at
`ROOT/perf01-build/before/protocols-v2/build.json`, produced from NativeWeave
`ea5fa528035d025bd7a28698ee7c71194432236c`. Every route reuses its independent
client, SHA-256
`acb1c163cd51e291f58dbe51ae12c04f82c2b51538aa36e446a05890e06aadd0`.
The existing direct engine is
`ROOT/perf01-build/direct/protocols-v3/build.json`, generic x86-64 Rust,
with the same client. No C# fixture or Rust binary change is needed.

## Small set of actual paths

All mixes below contain ordinary successful operations only. Expected deadline,
cancellation and slow-reader probes remain in the separate unchanged long mix
and correctness gates, with the prospective gRPC-only budget revision above.
Each selected mix has equal weights. The catalog records
profile hashes and the current preparation formula's planned counts.

| Profile | Group / actual protocol | Selected calls | Rate / client slots / scheduled seconds | Planned calls; minimum per reported scenario |
| --- | --- | --- | --- | --- |
| `json-allocation` | HTTP; equal H1 TLS / H2 TLS | Public typed `Results.Json(SmallReply)` only | 32/s / 4 / 20 | 645; 322 |
| `tiny-allocation-control` | HTTP; equal H1 TLS / H2 TLS | 16-byte `Results.Bytes` only | 32/s / 4 / 20 | 645; 322 |
| `http1-small` | HTTP/1.1 TLS only | 16-byte response, 1 MiB upload, 1 MiB download | 16/s / 4 / 20 | 323; 107 |
| `http2-small` | HTTP/2 TLS only | Same three paths | 16/s / 4 / 20 | 323; 107 |
| `http1-large` | HTTP/1.1 TLS only | Completed 8 MiB upload and download | 8/s / 4 / 30 | 242; 121 |
| `http2-large` | HTTP/2 TLS only | Completed 8 MiB upload and download | 8/s / 4 / 30 | 242; 121 |
| `grpc-unary` | HTTP/2 TLS, identity only | Unary with 64-byte and 65,536-byte Data fields | 16/s / 4 / 20 | 323; 161 |
| `grpc-streams` | HTTP/2 TLS, identity only | Server, client and duplex streaming, 32 messages of 4096 Data bytes | 16/s / 4 / 20 | 323; 107 |

The first two cells are diagnostic allocation observations, outside formal
timing. Their profile metadata and the supplied `profiling-marker.json`
explicitly say so. Run the tiny control if interpreting JSON's additional
allocation rather than merely checking that a large process-wide allocation
delta exists. Do not turn either diagnostic cell into an optimization percentage.

The six comparison partitions require 140 seconds of scheduled load per route
and repetition, plus separate warmup/recovery/idle. They reduce redundant process
starts while keeping each reported scenario above the A21 100-success minimum
for p99 when the cell succeeds completely. These are fixed low-load comparison
candidates, not measured sustainable rates or high-concurrency capacity. Preserve
a failed candidate as failed; any replacement rate must be selected
prospectively and used for all paired versions.

For each comparison row, collect the unchanged A21 minimum of three fresh
processes per route and interleave before/after/direct, reversing the order on
the next repetition. Root still freezes each scene's noise band from before
observations. These cells do not replace the mixed capacity ladders or the
ten required long segments.

The HTTP selector was source-reviewed and committed at
`d9c9572322c176f409f316e898103ca01d2eedcc`. It must be integrated only after
active calibration finishes, so no running cell's frozen driver changes.
Diagnostics omit the optional selector and work with the earlier driver too.
The singleton selector affects offered requests only; both TLS listeners remain
present. HTTP scenario keys omit payload size, so 1 MiB and 8 MiB instances of
the same upload/download path are deliberately in different cells.

## Preserved settings and real byte checks

These standalone JSON files copy the exact base profile identified in
`catalog.json`, changing the selected mix, optional HTTP protocol,
short idle duration and descriptive metadata. The gRPC-only retention revision
is also recorded in that catalog. Managed/native global payload caps remain
64 MiB each; per-request retention is 4 MiB for HTTP and 64 MiB for gRPC,
JSON/message maxima 1 MiB, stream maximum 64 MiB, and body chunks 32 KiB. Connection,
handshake, HTTP/2 stream, queue, timeout, bearer authentication and TLS settings
are unchanged. Client HTTP/2 still has four reusable connections and the same
bounded queue. Service CPUs are 2,3; generator/controller/client CPUs are 0,1.

The earlier 4 MiB gRPC mixed cell at 8 calls/s remains a failed service-standard
sample: two ordinary server-stream calls returned `ResourceExhausted`. The
fixed codec grant plus two maximum-size frame grants cannot fit its request
cap. See `../grpc-baseline-quota-observation.md` for pinned raw evidence, the
source bounds, unavailable exact throw attribution, and the distinction between
operation retirement and escaped frame ownership. The new cap is a prospective
workload-budget selection, not a product improvement. Direct Rust reads the same
numeric caps and reserves the same codec/request-metadata floor, but charges
actual outgoing frame bytes where NativeWeave retains maximum-message grants.
Report that existing admission-accounting difference in direct-Rust comparisons.

Every profile retains 24 warmup calls, 32 same-server recovery calls at the
existing quarter-second interval, owner drain, and five seconds of separately
timed idle, matching the prospective short-cell policy. The long profile retains
its own sixty-second idle and mixed paths.

The actual immutable server exposes 1 MiB and 8 MiB download payloads
(`Server/Program.cs:46–56`); the client allocates and independently hashes
those sizes (`Client/Program.cs:48–55`). A 4 MiB completed fixture is not in
these binaries. Root selected the already-supported completed 8 MiB transfer
instead of changing the common client/server source. The existing cancellation
probe declares an 8 MiB body but sends a prefix: it is never counted here as a
completed 8 MiB transfer.

HTTP downloads require exact Content-Length, total bytes, SHA-256 and hash
header. Uploads compute the server-side SHA-256 while reading the actual socket
body and return the acknowledged byte count/hash, which the independent client
checks. The tiny response is byte-compared. The JSON diagnostic checks the
static DTO fields and records actual response byte count; do not describe that
particular check as a per-response SHA-256. All clients require exact negotiated
HTTP versions, TLS certificate pinning and no response compression
(`Client/Program.cs:130–184`).

gRPC invokes the real public service and validates full protobuf equality,
ordered messages, half-close, success status and terminal trailers
(`Client/Program.cs:190–270`). Count calls, messages and byte fields separately:

| gRPC shape | Request / response messages per successful call | Request / response Data bytes |
| --- | ---: | ---: |
| Unary small | 1 / 1 | 64 / 64 |
| Unary large | 1 / 1 | 65,536 / 65,536 |
| Server stream | 1 / 32 | 4096 / 131,072 |
| Client stream | 32 / 1 | 131,072 / 0 |
| Duplex | 32 / 32 | 131,072 / 131,072 |

The client-stream response carries count, total bytes and digest in other
protobuf fields; its Data count is zero while encoded protobuf bytes are
nonzero. The driver reports encoded bytes separately, excluding the five-byte
gRPC envelope, HTTP framing and TLS. The largest actual fixture remains below
the existing direct Tonic codec bounds documented in `source-protocols.md`.
No protocol compression is supported or negotiated.

## Concrete commands

Use the exact Python 3.12.14 interpreter and a fresh output for every process.
These commands build nothing. They run only when root has the exclusive
measurement resource and has completed the relevant source integration.

```sh
PERF_ROOT=/workspace/scratch/01c249676f47
PERF_DRIVER="$PERF_ROOT/.worktree/Perf-01-linux/NativeWeave"
PERF_PROFILES="$PERF_ROOT/.worktree/Perf-01-linux/Plan/ledger/evidence/batches/Perf-01/protocol-layered"
PERF_PYTHON=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
PERF_COMMON="$PERF_ROOT/perf01-build/before/protocols-v2/build.json"
PERF_BUILD="$PERF_COMMON"
PERF_TLS="$PERF_ROOT/perf01-evidence/functional/before-grpc-001"
PERF_PROFILE=json-allocation
PERF_GROUP=http
PERF_RATE=32
PERF_SECONDS=20
PERF_OUT="$PERF_ROOT/perf01-evidence/profiling/protocols-json-before-001"

taskset -c 2,3 "$PERF_PYTHON" "$PERF_DRIVER/tests/Perf01.Protocols/run.py" prepare \
  --build "$PERF_BUILD" --client-build "$PERF_COMMON" \
  --profile "$PERF_PROFILES/$PERF_PROFILE.json" \
  --group "$PERF_GROUP" --rate "$PERF_RATE" --duration "$PERF_SECONDS" --concurrency 4 \
  --generator-cpus 0,1 --certificate "$PERF_TLS/certificate.pem" \
  --private-key "$PERF_TLS/private-key.pem" --output "$PERF_OUT"

# Only for the two diagnostic allocation profiles:
cp "$PERF_PROFILES/profiling-marker.json" "$PERF_OUT/profile-driver.json"

taskset -c 2,3 "$PERF_PYTHON" "$PERF_DRIVER/tests/Perf01.Protocols/run.py" run \
  --plan "$PERF_OUT/plan.json" --exclusive-lock "$PERF_ROOT/perf01-evidence/timing.lock"
```

For `tiny-allocation-control`, retain the rate/duration/slots and choose a
fresh diagnostic output. For each short row, set the profile/group/rate/seconds
from the table, omit the diagnostic marker copy, and use a fresh
`perf01-evidence/comparison/protocols-<profile>-<route>-<repetition>`
directory. After requires its newly built package server manifest; direct Rust
uses `$PERF_ROOT/perf01-build/direct/protocols-v3/build.json`.
Both still use `PERF_COMMON`, the same profile bytes, seed, TLS files,
rate/duration, CPU masks and slots. The generated comparison identity should
match across routes for a given profile. Private TLS key bytes are runtime
inputs, not Plan report content.

## Reading the allocation and comparison evidence

For the JSON pair retain `result.json.managed_gc` and the raw
`execution/server/managed-resources.jsonl`. The raw snapshots contain
`managed_allocated_bytes`, heap/committed bytes, Gen0/1/2 counters,
timestamp/frequency and phase. The server uses
`GC.GetTotalAllocatedBytes(false)`, so these are approximate whole-process
allocation observations, including handler, transport/interop, metrics and
runtime work. They are not method-local allocation measurements.

The existing summary subtracts the first and last measurement-phase snapshots;
the interval may omit part of the leading/trailing second. Report those actual
snapshot times and, if useful, allocated MiB per observed snapshot second.
Dividing that partial delta by every call in the entire cell is not an exact
bytes-per-call measurement. The matched tiny control helps locate the additional
JSON cost, but the difference is still an inference because response shape and
framework paths differ. JSON's existing eager maximum-sized buffer and
unchanged 3M pregrant are separately established by source analysis.

Report raw server CPU/RSS, client/generator CPU and dispatch lag, correct ordinary
calls, per-scenario p50/p95/p99, messages, actual successful payload bytes, and
owner/queue gauges. Per-scenario rates share the partition's whole measured
denominator; whole-process CPU/RSS cannot be attributed to an individual path
inside a partition. Do not use a mixed tail percentile in place of its individual
tiny/upload/download or gRPC cardinality rows. Direct Rust has no managed GC;
that field is inapplicable, not a measured zero allocation result.

The fixture permanently preallocates and retains the 1 MiB and 8 MiB downloads:
9 MiB of application payload backing in both C# and direct Rust servers,
outside per-request output credit. The common client creates raw arrays and
ByteString copies for 64, 4096, 65,536, 1,048,576 and 8,388,608 bytes, even for a
JSON-only profile. Those two sets total 19,013,760 payload bytes before object
overhead. Source locations are `Server/Program.cs:46–56`,
`DirectRust/src/main.rs:369–376` and `Client/Program.cs:48–55`.
They explain part of the baseline process footprint and startup work. Keep
reported RSS intact; backing capacity does not prove which pages are resident,
and subtracting it would not be a measured framework-only RSS value.
