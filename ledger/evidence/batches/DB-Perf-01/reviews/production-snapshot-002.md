# DB-Perf-01: frozen production snapshot 002 review

## Status and decision

**Source review completed; the candidate performance effect was unmeasured at this review boundary.** The minimum `TypedStream` change is suitable for a controlled, single-variable experiment. It removes the unconditional per-move completion owner and creates that owner only when disposal actually overlaps a move. No correctness defect was found in the reviewed interleavings below. Passing the proposed AOT lifecycle checks and the matching external-package allocation measurements remains a condition for retaining the change.

This is not acceptance of whole-framework zero allocation, a throughput claim, or approval of every change present in the other worktree. The separate `DbWire` and decimal changes were reviewed as independent proposals and are not part of the selected experiment. The original six public-package baseline processes are retained and must not be rerun merely to replace their results.

## Capture and reproducibility

The other active worktree was treated as read-only. Production and associated test sources were copied into a separate directory, with source hashes computed before and after copying and the copied bytes checked against both. All 39 captured files were stable during capture. Both HEAD readings were `771bc77cbd68d3f932b99ed2497c0697bbba5f02`. The source had uncommitted changes; the candidate is therefore identified by file hashes, not by pretending those changes belong to the fixed commit.

| Item | Recorded value |
| --- | --- |
| Capture time | `2026-11-24T09:34:23.588379+00:00` |
| Read-only source | `/workspace/scratch/b94e2a0e0c3f/Korda-DB-Perf-01-linux` |
| Frozen snapshot | `/workspace/scratch/754bc732518e/production-snapshot-002` |
| Original files | `baseline/<repository-relative path>` inside the snapshot |
| Candidate files | `candidate/<repository-relative path>` inside the snapshot |
| Hash manifest | `manifest.json` inside the snapshot |
| Manifest SHA-256 | `9dd8b902aed5179f2d4608a9a4e1d803fb432fb3f295faea10da83f445d34ff3` |
| Complete captured diff | `changes.patch` inside the snapshot; this is evidence, not an instruction to apply all changes |

The working copy authorized for the experiment is `/workspace/scratch/754bc732518e/Korda-DB-Perf-01-linux`. Only `src/Data.Streaming` and `tests/Data.Streaming` are owned by this reviewer for application. No command in the capture wrote to the other active worktree, published packages, changed a remote branch, or started a heavy build.

| Reviewed source | Original SHA-256 | Frozen candidate SHA-256 |
| --- | --- | --- |
| `src/Data.Streaming/TypedStream.cs` | `8972c8d0e55ead50627b3a31555f29bd883115c7d8b658c59ba23a3d3f6fadc5` | `91294bd51fcba16aec116512ce89f08866108de73751dd47ef255218201bf6af` |
| `src/Data.Abstractions/DbWire.cs` | `bc4070dd7b97b14b8888ff3648dda76832acef51f07ae5471e1875b389296696` | `1a5375924f92181c62b11e416efcbd9f4edd8ae058155389479959888cfa889f` |
| `src/Data.Abstractions/Codecs.cs` | `e52520cca6565933c95fbf25ae44e7dd0f2a3132ee79966ae77f3bc89da5e826` | `fc7ab82e410fd9d10dbca2e7bcf127f166dd1a0e23a9e4ea7294d7c226a66760` |
| `tests/Data.Streaming/AllocationProbe.cs` | New file | `3328d624865e396eadea2cbcc66bd2d341e5a968f10bcf23a64f0cb940ca19dc` |
| `tests/Data.Streaming/AllocationProbeGate.cs` | New file | `367956a0a9c034325789c356a57ec61aa7fd4f5feb1638151fed24bab39610ba` |
| `tests/Data.Streaming/AllocationProbeRaces.cs` | New file | `4454d2c7731f31c525e1d31f18f90200f15fe95a3c89bd5067a0f136147c6ffe` |
| `tests/Data.Streaming/Program.cs` | `39461addf8f729618b95d1a6f27dea62f1b9a4cf2c622a5e66a01c7f50073b58` | `5243b341b117a599ae055433c0bad0e735dfa852147fce7059194ad700822eff` |

To validate the frozen capture without reading or mutating the active source again:

```bash
python3 - <<'PY'
import hashlib, json
from pathlib import Path
root = Path('/workspace/scratch/754bc732518e/production-snapshot-002')
manifest = json.loads((root / 'manifest.json').read_text())
assert manifest['source_hashes_stable_during_capture']
assert manifest['head_before'] == manifest['head_after'] == '771bc77cbd68d3f932b99ed2497c0697bbba5f02'
for record in manifest['files']:
    data = (root / 'candidate' / record['path']).read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    assert actual == record['snapshot_sha256'] == record['source_sha256_before'] == record['source_sha256_after']
    if record['baseline_sha256'] is not None:
        original = (root / 'baseline' / record['path']).read_bytes()
        assert hashlib.sha256(original).hexdigest() == record['baseline_sha256']
print('Verified', len(manifest['files']), 'frozen files')
PY
```

## Selected change: create the move join only when needed

The original [move admission and completion](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Streaming/TypedStream.cs#L125-L190) creates a `TaskCompletionSource` and its task for every `MoveNextAsync`, including moves that only map an already parsed numeric row and complete synchronously. [Disposal](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Streaming/TypedStream.cs#L223-L244) is the only reader of that separate completion task.

The frozen candidate changes the admission marker to `_moving`, protected by the existing `_gate`. `_moveJoin` remains null unless `DisposeAsync` enters while `_moving` is true. Concurrent disposers share that single, non-resettable task. The `finally` block clears `_moving`, detaches `_moveJoin`, and completes the detached join while holding the same lock. Its `RunContinuationsAsynchronously` policy is retained. The method body, `Task<bool>` result, stop requests, wire ownership, mapper execution, exception attachment and once-only cleanup owner are unchanged.

This replaces an unconditional allocation with a bounded, demand-created owner. It introduces no global cache, no buffer pool, no transfer to the native heap, no extra copy and no retained array. There can be at most one move join associated with the enumerator's admitted move. Closing the enumerator prevents admission of another move, so this field cannot grow with the number of rows.

### Semantic review

All locations below refer to the frozen candidate `src/Data.Streaming/TypedStream.cs`; the original linked source establishes the semantics being preserved.

| Path | Review of ordering and ownership | Required observation |
| --- | --- | --- |
| Synchronous in-batch move, lines 126–194 | Admission still rejects overlapping moves under `_gate`. The mapper runs while the batch is owned. `finally` marks the move inactive before returning. An unobserved join is never created. | The same rows and primitive checksum; completed-successfully checks; raw allocation counts, not rounded averages. |
| Pending start, lines 143–148 | Dispose marks `_closed` before waiting. If start has not delivered a transport, its first stop request has no transport to act on. After start returns, the move installs the transport, registers cancellation, notices closure and enters existing cleanup. The lazy waiter is released only after that move unwinds. | Dispose cannot complete before the start's actual transport retirement. No fetch and no release of an untransferred batch. |
| Pending fetch, lines 153–168 | Dispose cannot release the active move's batch. The move awaits the accepted fetch, validates/owns the delivered batch and notices closure before mapping. Catch performs compensation and retirement before finally publishing the join. | No early row mapping or early batch release; one release and one retirement join. |
| Mapper already executing, lines 167–194 | The existing closure check occurs before the synchronous mapper. A Dispose that overlaps an already admitted mapper still waits for that mapper. A successful row may be returned, as before; the patch does not add a second closure check or revoke a completed mapping. | A blocked mapper retains its live batch. Both disposers remain pending until the mapper exits and cleanup retires. |
| Mapping failure and cleanup failure, lines 179–194, 196–225 | The primary mapper exception remains primary. A cleanup exception remains attached under `Korda.Database.StreamCleanup.v1`. Repeated cleanup calls observe the existing `_cleanup.Task`; lazy move completion conveys completion, not the move's result or exception. | Original exception object retained; both disposers observe the same cleanup failure; one batch release and retirement. |
| Cancellation during accepted fetch, lines 140–148, 196–250 | Registration and `RequestStop` are unchanged. Cancellation requests stop; it does not locally synthesize completion or release an accepted native operation. The move still awaits the fetch's terminal result and actual retirement. | Pending move remains pending after requesting cancellation; admitted cancellation token retained; disposal waits for retirement. |
| Multiple Dispose calls, lines 227–250 | All set `_closed` under the same lock. While a move is active they share `_moveJoin.Task`. After it finishes they use `Task.CompletedTask`, then join `_cleanup.Task`. Clearing `_moveJoin` is safe because previously returned task references remain immutable and valid. | Multiple/repeated Dispose calls do not double release; no task reset, version reuse or stale waiter. |
| Concurrent MoveNext, lines 126–134 | `_moving` replaces the old non-null completion owner as the admission predicate under the same lock. The `ConcurrentUse` error and throw location are preserved. | A second pending move is rejected without replacing the accepted move's join. |

Completion of the separate move join occurs in `finally`, before the async method builder publishes the `Task<bool>` result. That was also true of the original `_activeMove` completion. The patch does not newly promise that Dispose observes the caller's result task as completed before it proceeds; it preserves the stronger resource requirement that mapping and the move's cleanup work have left their protected lifetime.

### Allocation boundaries and remaining cost

The [original external package baseline](../preflight/korda-allocation/summary.md) already measured **11,176 raw process-wide bytes for each 127-row synchronous in-batch window, or 88 B/row**, in all 768 windows across six processes and two providers. The matching empty synchronous controls were zero. This is evidence for investigating the unconditional completion owner; it is not a sampled attribution stack or proof that every framework allocation has been identified.

| Boundary | Candidate hypothesis, source-only at this review | Cost explicitly outside that hypothesis |
| --- | --- | --- |
| Numeric row already in a parsed batch; no overlapping Dispose | Eliminate the unconditional completion owner. Preserve the synchronous `Task<bool>` completion path. Zero raw bytes is a testable target for this narrow window. | Query construction, start, fetch, parse, replenishment, final false, cleanup, connection/session creation and application reference outputs. |
| One full dynamic or prepared query | Remove one unconditional owner for every admitted move, including the terminal move. | Query/stream/enumerator objects, descriptors, binding, callback/operation owners, real async tasks, batch leases and copies, final cleanup tasks. Full query measurement must include final false and Dispose. |
| One replenishment batch | Remove the move's unconditional owner only. | Transport completion, `RowBatchLease`, wire parsing structures and payload copies remain. |
| Move overlapping Dispose | One shared join may still be allocated, plus awaiting disposer state. | This path is deliberately not advertised as zero allocation. Correct lifetime and retirement take priority. |
| Real asynchronous suspension | The extra eager completion owner is removed; the existing async `Task<bool>` state remains. | Await infrastructure, public transport tasks and completion owners are not eliminated by the patch. |
| Cancellation, exceptions, pool pressure | No optimization or zero-allocation claim. | Error objects, cancellation registration/linking and cleanup failures are separate evidence categories. |

**A zero-byte row window would not make a zero-byte query.** Full-process counters and all-generation GC counts remain necessary for each accepted boundary. No empty-driver subtraction is permitted to turn a nonzero raw total into a claimed zero. Throughput and elapsed time in this preflight are diagnostic only because the host is not reserved for exclusive performance measurement.

## Tests reviewed and proposed for adoption

`AllocationProbeRaces.cs` uses explicit, bounded completion gates, not sleeps. It exercises pending start, pending fetch, concurrent MoveNext rejection, two simultaneous disposers, disposal while a synchronous mapper is blocked, primary mapping error, cleanup error, cancellation token preservation and once-only owner retirement. The synthetic transport represents ownership transitions only; it is not evidence of actual PostgreSQL or SQLite cancellation behavior.

`AllocationProbe.cs` includes an isolated, preconstructed managed transport. Its synchronous in-batch lane measures process-wide cumulative bytes only after the first fetched/parsed row; immutable inputs, output buffers and diagnostics are constructed outside the interval. Its scalar and full-stream diagnostic lanes are optional and are not needed to accept this TypedStream-only change. Its asynchronous stream transport withholds each fetch completion until the caller has observed an incomplete move, so `MoveAsync` really encounters an incomplete fetch. A reported incomplete await is kept distinct from a measured thread switch.

`AllocationProbeGate.cs` requires exactly zero raw bytes in each of 16 warmed windows of 4,095 already available numeric rows. It also checks zero measured fetches and incomplete moves, zero live batches and pending completions after drain, zero reference business outputs, and the explicit `publicProviderAcceptance=false` classification. The default test entry point runs this gate and the lifecycle races before the existing actual-provider tests. A dedicated `--allocation-gate-only` invocation allows the narrow allocation gate to run without implying provider coverage; a separate `--allocation-probe-races` invocation runs the lifecycle checks.

The tests do not validate native provider behavior by themselves. The unchanged external `benchmarks/Database/allocations/Program.cs`, copied outside the repository and compiled against one top-level provider package at a time, is required for the matching public API result.

## Independent proposals not applied in this experiment

### Strict UTF-8 validation without materializing a discarded string

Frozen `DbWire.cs` lines 137 and 149 replace `Validation.Utf8.GetString(bytes)` with `GetCharCount(bytes)` for string/JSON scalar validation. The intended transformation preserves the same strict encoding instance and validation pass while discarding only a temporary string that callers cannot observe. [The original code](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/DbWire.cs#L127-L156) validates before later owned value decoding. This is a plausible independent hotspot, but no benefit for text is established by the primitive-long baseline. Required checks include malformed and truncated UTF-8, overlong forms, surrogate encodings, maximum Unicode scalars, empty text, supplementary characters, JSON BOM rejection, JSON depth limits and preserved exception classification. The JSON `bytes.ToArray()`, `JsonDocument` parse and actual returned string/DTO allocation remain. Do not call this zero-allocation JSON.

### Decimal canonicality without encode/decode round trip

Frozen `Codecs.cs` lines 254–267 replace the [original re-encode comparison](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/Codecs.cs#L237-L270) with a bounded 96-bit coefficient held in `UInt128`. A decimal coefficient is canonical exactly when zero has zero scale/sign, or a nonzero coefficient with positive scale is not divisible by ten. Header length, scale range, sign and reserved-byte checks remain. This is consistent with the original normalizing encoder, but must be verified independently across zero/negative zero, scale 0–28, maximum coefficient, trailing-zero coefficients, both signs and invalid headers. The candidate snapshot contains property-style round-trip tests and a separate scalar probe. They are not adopted with the row-join change. PostgreSQL decimal fit checking still parses codec configuration and is not made allocation-free by this proposal.

### Incidental lockfile changes

The two changed normal lockfiles add empty RID sections. They are not an optimization and are not needed for the selected source change. Do not import them merely because they were present in the active worktree. A real required restore input update must be reviewed on its own evidence.

## Objective limits under the retained public API

The existing API exposes immutable `Task<T>` results and reference-identity session/transaction/stream owners. A caller may retain and await a task more than once. Reusing a single resettable task for different operations would change that contract. A completed result task for a distinct live session or stream cannot be replaced by the same previous result task. Resetting a disposed owner object to represent another operation would also make old aliases observe the new owner and would violate ownership unless an additional compatible identity mechanism were introduced. This review authorizes no such API substitution.

This is a reason to report scope honestly, not a reason to ignore avoidable allocation. Synchronously completed boolean moves can benefit from the runtime's completed-task path, as the narrow AOT counter gate will test. Internal buffers may be pooled only with finite capacities, tracked native/managed retention and unchanged lifetimes. Real suspension on the existing `Task`-returning operation paths still needs distinct stable completion state; removing all of it cannot be claimed from this local patch. The full source inventory is in [allocation-audit.md](../allocation-audit.md), and the public-package baseline reports both complete queries and batches without subtracting a guessed framework fraction.

## Validation sequence and commands

Only ordinary serial builds are authorized for this experiment. Reuse the verified SDK support packages read-only, with candidate packages restored to separate writable caches. Do not invoke an older launcher, rebuild the other worktree or share its PostgreSQL cluster. The estimated new test/consumer outputs are approximately 100–180 MB; full C++ rebuilding and the entire bundle closure are a separate disk-budget decision owned by the parent task.

After applying only the reviewed Streaming files, publish the affected test executable using the real tools and the committed AOT lock inputs:

```bash
export DOTNET_ROOT=/workspace/scratch/82a414196324/tooling/dotnet
export PATH=/workspace/scratch/82a414196324/Korda-DB-Rename-01-linux/artifacts/toolchain/llvm-23.1.5/bin:$DOTNET_ROOT:$PATH
export DOTNET_CLI_USE_MSBUILD_SERVER=0
export MSBUILDDISABLENODEREUSE=1
cd /workspace/scratch/754bc732518e/Korda-DB-Perf-01-linux
dotnet publish tests/Data.Streaming/Korda.Data.Streaming.Tests.csproj \
  -c Release -r linux-x64 -p:PublishAot=true -p:RestoreLockedMode=true \
  --configfile /workspace/scratch/754bc732518e/allocation-consumers-attempt-001/postgresql/app/NuGet.Config \
  -p:NuGetAudit=false -p:UseSharedCompilation=false -nr:false -m:1 \
  -o /workspace/scratch/754bc732518e/streaming-lazy-join-validation/aot
/workspace/scratch/754bc732518e/streaming-lazy-join-validation/aot/Korda.Data.Streaming.Tests \
  /workspace/scratch/754bc732518e/streaming-lazy-join-validation/gate \
  --require-aot --allocation-gate-only
/workspace/scratch/754bc732518e/streaming-lazy-join-validation/aot/Korda.Data.Streaming.Tests \
  /workspace/scratch/754bc732518e/streaming-lazy-join-validation/races \
  --require-aot --allocation-probe-races
```

The configuration above contains a readonly fallback view of only six SDK support package IDs. The test project uses project references, so that configuration's baseline provider feed is not a product dependency of this internal check. The external acceptance build must use the after-candidate feed instead. Preserve its exact app source hashes from the baseline manifest.

The existing full affected-module runner is `tests/Data.Streaming/verify.py`, with ordinary C++ Release fixtures, compiled API/XML comparison, actual AOT provider checks and the AOT sample. It must be run against a matching fixture/build or produce a recorded blocker; the narrow commands above do not replace that gate. The parent task is responsible for official bundle creation, package metadata/API verification and determining the affected downstream checks.

When two verified after candidates are available under `AFTER_ARTIFACTS`, the unchanged external runner can be reused in a fresh directory:

```bash
python3 benchmarks/Database/allocations/run.py \
  --artifacts "$AFTER_ARTIFACTS" \
  --work /workspace/scratch/754bc732518e/allocation-consumers-after-lazy-join \
  --evidence /workspace/scratch/754bc732518e/Plan-DB-Perf-01-linux/ledger/evidence/batches/DB-Perf-01/preflight/korda-allocation-after-lazy-join \
  --dotnet /workspace/scratch/82a414196324/tooling/dotnet/dotnet \
  --clang-bin /workspace/scratch/82a414196324/Korda-DB-Rename-01-linux/artifacts/toolchain/llvm-23.1.5/bin \
  --postgres-bin /workspace/scratch/82a414196324/Korda-DB-Rename-01-linux/artifacts/postgres-tools/install/bin \
  --support-cache /workspace/scratch/82a414196324/Korda-DB-Rename-01-linux/artifacts/nuget-packages \
  --warmup 64 --iterations 128 --processes 3
```

The runner creates and stops its own TCP-only PostgreSQL cluster (`-k ''`), uses fixed data and limits, interleaves independent processes, includes complete query cleanup, records raw process-wide counters before any division, keeps empty controls separate, and hashes the package, actual executable and mapped native library. `AFTER_ARTIFACTS` is deliberately an unresolved input until official candidate packaging is complete. The after report must bind a dirty-source manifest or final commit to the candidate package; the original main SHA alone is insufficient to identify changed binaries.

No after measurement, race execution, or AOT test result is asserted by this source-review document. Subsequent execution logs and a comparison report must supply those results explicitly.
