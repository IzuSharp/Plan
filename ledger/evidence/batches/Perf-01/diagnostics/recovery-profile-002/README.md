# Perf-01 epoch002 layered diagnostic preparation

**Prepared source only. No profile, build, test or load was executed by this
preparation. No numeric result, performance improvement or long-test credit is
asserted.** This is a new small caller around surviving public original probes;
the lost historical private profiling wrapper has not been restored.

The actual before/common replacement build and B18 receipts must satisfy
[`recovery-measure-002` admission](../recovery-measure-002/MEASUREMENT.md) before
any command can start. The separate final binding is mandatory for `after`;
this plan selects no final product. No narrative hash substitutes for an
actual manifest, package, native library or completed receipt.

## Diagnostic questions and unchanged producers

| Profile | Original input / work | Interpretation |
|---|---|---|
| `inspect` | Original `tests/Perf01.InspectProfile/prepare.py`; one isolated Release/Native AOT consumer from the selected codec manifest; three independent processes, each 10,000 warmup calls and 10 × 100,000 measured calls | Public metadata lookup and calling-thread allocation. First load is reported separately. Process CPU surrounds a wider bracket; very small CPU deltas are resolution limited. It does not measure codec computation. |
| `page-sqlite`, `page-postgresql` | Already built original Shared PageProbe; 1,000 complete 100-row pages; original 20 warmup pages, limits, ordered DTO validation and cleanup | Serial public typed query, DTO/list materialization and stream retirement. CPU/allocation include validation and runtime work. The new logical seed-verification session may reuse a physical pooled connection; it is not an independent external durability oracle. |
| `retirement-sqlite`, `retirement-postgresql` | Already built original Shared RetirementProbe; 1,000 scalar calls after 20 warmup calls | Existing test-hook timestamps for start, terminal copy, take and retirement. Observer storage/work is included. No direct observation of the retirement Pending count. |
| `postgresql-cycle`, `postgresql-page` | Original `profile_postgresql.py`, 180 arrivals/s, C16, 20 seconds, 100ms requested wait-observer idle | Whole application with durable private PostgreSQL 18.0, statement-duration logging and sampled backend wait states. Parse/bind/execute are separate protocol steps, not business operation counts. Concurrent statement time cannot be subtracted from application wall time. |
| `http-tiny`, `http-json` | Byte-identical original allocation profiles, 32/s, C4, 20s | Real HTTP/1.1 and HTTP/2 TLS fixtures, small handler versus JSON response. Preserve whole-process resource brackets and actual successful response validation. |
| Four `grpc-*` modes | Byte-identical original cardinality profiles, 16 calls/s, C4, 20s each | Independent HTTP/2 + TLS client: unary64B/1message; server/client/duplex4096B/32messages. Calls, request/response messages, logical checks and encoded payload are distinct denominators. |

Counts, quotas, SQLite persistence settings, fixed data, profile bytes,
protobuf, TLS admission and original source remain unchanged. Shared probes
reuse the actual completed role producers; their manifests retain
`executed: false` as the original **build** receipt. Runtime evidence goes to a
new directory. Inspect preparation creates only a new managed AOT consumer
from existing packages; it preserves the original no-Rust traps and locked
dependency checks. Native assets are not rebuilt or relabelled.

The optional direct/managed roles exist only where the original drivers have
those actual common producers. The before-produced protocol client is used
for **all** protocol roles. Native allocation counters are unavailable for the
direct Rust process; managed GC allocation is not applicable there.

## Inspect preparation from existing external dependencies

Only the `inspect` preparation command receives `NUGET_FALLBACK_PACKAGES`.
Its diagnostic-local fallback view exposes exact external package/version
directories from the same admitted role's `codec/consumer-cache`, using the
bound codec `project.assets.json` library and exact runtime-download entries.
It contains no `NativeWeave.*` package. The unchanged original preparer still
creates its fresh writable cache, copies the role's two project packages into
its local feed, and performs the original locked restore and native identity
checks. No shared/protocol profile setting or measured process environment is
changed. The original environment is restored in `finally` before the first
Inspect probe, including on preparation failure.

The preparation receipt records the codec manifest/assets identities and
external archive hashes. Ordinary external libraries retain their existing
build-bound archive hashes. Runtime download packs named by the bound assets
file were not individually present in the original build's resolved-library
map; their existing same-role archive/sidecar/metadata bytes are pinned at this
preparation and explicitly marked `archive_bound_by_build: false`. The caller
does not claim a new signature validation or pristine-machine restore. The
fallback is read-only from NuGet's perspective; only six external version
directories are exposed for the current producer. The new caller performs no
dependency download itself and leaves audit, TLS and package sources intact.
Fallback package availability does not prove that NuGet performs no network I/O.

The preparation command alone also inherits the ordinary tool-provided
`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY` and corresponding lowercase
environment keys when present, as the original producer build environment did.
It supplies no new endpoint, credential or route. Only inherited key names are
recorded; their values are neither copied into this source nor written to the
preparation receipt. This permits the unchanged NuGet audit request to use the
existing network configuration instead of suppressing audit failures. The
same `finally` restores the original runtime environment before every probe;
formal measurements and other profile branches retain their original settings.

The official [NuGet environment-variable reference](https://learn.microsoft.com/en-us/nuget/reference/cli-reference/cli-ref-environment-variables)
and [fallback folder reference](https://learn.microsoft.com/en-us/nuget/reference/nuget-config-file#fallbackpackagefolders-section)
were read on 2026-11-21. They document the environment variable and lookup
before package sources, which is why project packages are excluded from the
view. The actual SDK `11.0.100` `dotnet.deps.json` identifies
`NuGet.Configuration/8.0.0-rc.53118`; the actual `NuGet.Configuration.dll`
contains the environment-variable name and has SHA-256
`9dc08b0d1b6ef4a96cca70b9e0214e59dd21e76f5986f46d7a47664afb455245`.
This was a local file/source inspection, not an executed restore test of this
new caller. Root must preserve the first actual result and its original logs.

## Admission, ownership and isolation

`profile.py` verifies its source index and the reviewed measurement interface,
acquires the build admission's existing exclusive reservation, then uses its
`Context` for actual producer, package, source, toolchain, Python dependency,
TLS and functional admission. It reuses `Run.command` and the unchanged
`recovery-build-001/owner.py`, including real process identity, bounded waits,
descendant retirement, signal handling and failure receipts. No remembered
PID is signalled. Original measured manifests are immutable.

The outer caller stays on CPU8. Probe and service processes use CPUs2,3.
Protocol generators use CPUs0,1 and the distinct admitted protocol child
timing lock. The original PostgreSQL application profiler has no generator
mask option: its generator, service, database and wait observer inherit
CPUs2,3. This limitation is explicit; it is not a formal isolated-generator
sample. It also retains its original automatic GC/default sampling settings,
not the formal caller's deferred/threaded settings.

`pg_probe.py` only wraps one original Shared executable in the original
`src/Benchmarks.Domain/run.py::postgres` context. The finite owner covers
startup, including a failure before the context yields, probe execution and
shutdown. Observed version/durability must equal `18.0|on|on|on` before the
probe. The parent verifies the real PostgreSQL identities, successful final
stop command and selected role's runtime-loaded native hash. The original
cluster lifecycle and durability implementation are not copied.

Each invocation has a fresh label under the `profiles-001` sibling of the
admitted formal output directory. It cannot overwrite or resume a partial
run. Keep failure/partial outputs and use a new label for another attempt.
The output remains diagnostic even when original correctness and service
checks pass. Original protocol `read_cell` output retains its explicit
profiling-only comparison rejection; any additional reader issue fails this
caller. No profile marker is removed. PostgreSQL diagnostic summaries retain
their own policies and are not sent through the different formal DB gate.

## Root execution interface — do not execute during source preparation

Use actual hashes from completed descriptors and the reviewed source indices.
The variables below are operator inputs, not completed evidence:

```bash
taskset --cpu-list 8 "$PERF01_PYTHON" "$PERF01_PROFILE_CALLER" \
  --root "$PERF01_ROOT" \
  --admission "$PERF01_ADMISSION" \
  --admission-sha256 "$PERF01_ADMISSION_SHA256" \
  --measurement-source-index-sha256 "$PERF01_MEASUREMENT_INDEX_SHA256" \
  --profile-source-index-sha256 "$PERF01_PROFILE_INDEX_SHA256" \
  --role before --profile page-postgresql --label before-page-postgresql-001
```

For `after`, add `--final-binding` and `--final-binding-sha256` for the exact
selected final descriptor. Run one profile at a time; root alone executes.
The full profile identifiers and bounds are in [plan.json](plan.json).
`inspect` launches its three processes after one fresh consumer preparation.
Do not run these commands alongside formal timing, producer builds or other
profiles. After diagnostic work, formal samples still require the unchanged
measurement caller's separate publication, noise, capacity and long gates.

## Evidence and limits

The execution record binds its new source/plan, unchanged admission and actual
build proofs. Original child receipts/logs and original results are retained;
Shared results add runtime-loaded module hashes, and Inspect validates its
own AOT executable, codec and manifest. A retirement result does not itself
measure its executable hash; the selected executable is bound through its
producer and owned argv, and the result supplies actual loaded native hashes.

The protocol numeric reader is reused without a new statistics algorithm.
Its per-process CPU/RSS and approximate `GetTotalAllocatedBytes(false)` bracket
must not be distributed across scenarios or presented as exact allocation
stacks. The process resource observation, on-time successful ordinary calls,
expected probes and transfer cardinalities retain their original denominators.
Raw protobuf bytes exclude envelopes, framing and TLS. Cancellation does not
prove that every submitted client message reached the server.

Unavailable values stay unavailable: exact boundary/copy/pin counts, native
allocation attribution, exact async wakeup/context-switch attribution,
per-request pool wait, exact lock duration and retirement Pending counts.
Inspect and Shared probes do not sample RSS, queue trends or a post-idle
resource series; they report only their original counters and cleanup checks.
PostgreSQL sampled wait occupancy is not exact duration. These measurements
guide source analysis and minimal changes; separate equivalent formal
workloads must establish whether a change is worth retaining.

Runtime control records contain local paths and remain local. Publish only
reviewed project numeric/identity projections; do not publish raw control
arguments, private TLS key metadata or full build/cache maps. Source index
entries here use repository-relative paths. No historical numeric acceptance
or old long-test credit is carried into epoch002.
