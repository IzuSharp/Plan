# Perf-01 codec baseline preparation and prospective calibration

Status: preparation complete; no performance run or 30-minute acceptance is
claimed by this record. Root owns the exclusive measurement resource and the
final cross-domain configuration freeze. This record complements
`source-codec.md` and does not replace the main handoff.

## Before artifacts

The complete A17 package preparation finished at
`2026-11-19T06:56:24.075926+00:00`. Its clean product checkout was
`IzuSharp/NativeWeave@ea5fa528035d025bd7a28698ee7c71194432236c`, before any Perf-01
product implementation change. The separate driver checkout was
`e0df0a8992c7ad6ec51b223e6b323e85837d7797`.

The build directory, relative to this session's project ROOT, is
`perf01-codec-checks/package-before-001/`. The root agent accepted retaining
this completed clean build instead of duplicating it in another output folder.
The source repository itself remains unchanged by the package preparation.

| Artifact relative to the build directory | SHA-256 |
| --- | --- |
| `manifest.json` | `80a906a0675dca8182240a8117c900cd57238465d499f0a094a875a290204a3c` |
| `commands.json` | `9731c54af9ab71c7667ba952e0798eca89db03642a65bae535bb28c661745ba9` |
| `aot/NativeWeave.Engines.SyncProof.Tests` | `0c6b206a59b74a16640655a6e24513713387b63f53d70a9da823614e649614a1` |
| `aot/libnativeweave_engine_syncproof.so` | `3a472d8e51ad5d69a28ade2b00cd23fc9a2bb8d9fa1e2c4df47b769316acff79` |
| `direct-target/release/perf01-codec-direct` | `f91076cf2a31c895914ff7333289210a191d8ef1eaf99f1f6cadabf128831477` |
| `packages/NativeWeave.Core.0.1.0-proof.1.nupkg` | `e664d0611e4f5f98f62fed352a2eb7f22920c1c9f6e32da8bc526550eacaef96` |
| `packages/NativeWeave.Engines.SyncProof.0.1.0-proof.1.nupkg` | `fbc1bbe997125945bf3b891d08f3c2f9485e33a0b3eddb10ddbe6d607df5ee65` |

The manifest also retains exact source/lock hashes, the resolved AOT NuGet lock,
copied consumer sources, A21 and driver hashes, the two-package A17 receipt, and
the original producer's ordinary managed-edit/native-unchanged check. Its
`executed_performance` field is false. The receipt proves the original A17
package consumer's JIT and AOT execution. The new Perf-01 consumer was compiled
and linked in this prepare invocation; its actual timed use, mapped module hash
and validity checks belong to each future measurement receipt.

All 25 recorded preparation commands met their expected exit codes, including
the two deliberately failing source-compatibility negatives. The driver uses
SDK `11.0.100`, Rust `1.100.0`, and the original package/module versions. Rust
product and direct Release profiles use thin LTO, one codegen unit, unwind panic
and stripped debug information. Native build command:

```sh
cargo build --locked --release -p nativeweave-engine-syncproof
```

The actual Perf-01 consumer publish uses Release, `linux-x64`,
`PublishAot=true`, `IlcTreatWarningsAsErrors=true`, `--no-restore`,
`UseSharedCompilation=false`, `-nr:false` and `-m:1`; exact absolute arguments
are retained in `commands.json`.

### AOT instruction-set observation

The emitted response file is
`consumer/obj/Release/net11.0/linux-x64/native/NativeWeave.Engines.SyncProof.Tests.ilc.rsp`,
SHA-256 `527621a20549f1360cabd6546a88d1dcba01a1a5b7a069b5aea9027e64171b37`.
It contains `--targetos:linux`, `--targetarch:x64` and `-O`, with no
`--instruction-set` argument. Installed ILC 11.0.0
`build/Microsoft.NETCore.Native.targets:300` adds that argument only for a
nonempty `IlcInstructionSet`. The installed text documentation inspected here
does not specify the compiler's resolved default feature set. Record this as
**ILC 11.0.0 x64 compiler default, explicit argument omitted**; do not assert
that it is x86-64-v2 or x86-64-v3. Root accepted keeping this exact build policy
for both variants. The same unchanged publish command must produce the after
consumer.

## Frozen corpus and memory floor

The independently checked corpus resides at
`ROOT/perf01-codec-checks/corpus/`; its manifest SHA-256 is
`92932f7ecba2b3a7104b19344d22a42c3c40605f23eb158a0941d48bfff0465d`.
It contains 10,494,464 raw bytes and 5,263,812 encoded bytes, totaling
15.028263 MiB. The manifest identifies its own exact generator binary. Corpus
generation preceded the final direct Release profile alignment; every encoded
byte remains checked against the locked miniz algorithm and the raw bytes
against the independent Python generator. Reuse the corpus bytes unchanged;
the timing comparator is the final direct executable listed above.

This payload floor does not intrinsically preclude the proposed 256 MiB target
RSS ceiling. It is not a prediction of measured RSS: managed collection policy,
native allocation retention, in-flight output capacity, thread stacks and the
runtime add memory. The queue holds bounded action identifiers referencing the
same corpus rather than copying payloads per queued request. Actual RSS maxima
and idle behavior must come from the process samples.

## Prospective calibration rule

The following rule was sent to root before product edits. Numeric sustainable
rates are deliberately unselected until baseline calibration.

1. Fix the target, direct comparator and controller to the same allowed two
   CPUs (root proposes CPUs 2 and 3). Use one worker to isolate a single caller,
   then two workers for the main mixed-load candidate. Four workers, if useful,
   are a separately labeled oversubscription stress setting.
2. Keep the existing 160-action corpus cycle, queue 64, maximum in-flight 256,
   deadline 1,000 ms, maximum generator dispatch lag 50 ms, 20-second warmup,
   10-second same-process recovery at one operation per second, and 60-second
   final idle observation fixed.
3. Begin at four operations per second and double the offered rate in fresh
   30-second baseline cells. A failing intended-load validity check invalidates
   the sample rather than establishing server capacity. A valid SLO failure
   provides an overload bracket; retain its errors and recovery observations.
4. Refine a passing/failing capacity bracket until its width is at most 10% of
   the passing rate. Confirm the highest passing candidate with three
   independent 60-second baseline processes. Root's proposed common service
   standard is zero unexpected errors, arrival p99 at most 500 ms, and sampled
   target RSS maximum at most 256 MiB. All byte/limit/owner checks and generator
   validity checks must also pass. A percentile with insufficient tail samples
   remains unavailable rather than passing.
5. Freeze the 30-minute rate at 80% of the highest consistently passing baseline
   rate, with the chosen worker count and unchanged mixture. The after run uses
   that exact load. Run the same offered load against direct Rust and conduct a
   separate capacity ladder under the same SLO. Interleave independent short
   before/after processes using root's A21 noise procedure.

The codec driver's current `service_standard_met` flag covers intended-load
validity and unexpected outcomes. Root's integrated acceptance must additionally
apply the declared 500 ms p99 and 256 MiB RSS tests to summary/resource evidence;
the standalone flag alone is not the full cross-domain service standard.

Proposed long invocation, after root freezes `WORKERS` and `RATE`:

```sh
python3 tests/Perf01.Codec/driver.py run \
  --manifest "$ROOT/perf01-codec-checks/package-before-001/manifest.json" \
  --corpus "$ROOT/perf01-codec-checks/corpus" --route nativeweave \
  --workers "$WORKERS" --rate "$RATE" --queue 64 --inflight 256 \
  --deadline-ms 1000 --max-lag-ms 50 \
  --duration-seconds 1800 --warmup-seconds 20 \
  --recovery-seconds 10 --recovery-rate 1 --idle-seconds 60 \
  --output "$NEW_IMMUTABLE_RESULT_DIRECTORY"
```

Only root's coordinated timing window may execute it. The actual dispatch span
must reach the requested duration; recovery/idle do not receive duration credit.
Interrupted results retain partial dispatch records and receive no long-stage
credit. Neither the prospective rule nor compilation establishes sustained
performance, improvement, direct-Rust parity, or the required 30-minute result.

## Independent review status

The database agent read the codec driver and spot-checked final test commit
`e0df0a8992c7ad6ec51b223e6b323e85837d7797`. Its reported source issues were
resolved: direct compiler profile parity, current driver/A21 and consumer
provenance checks, interrupted dispatch retention, compact streamed summaries,
phase counts, resource configuration checks, same-process recovery, copy-counter
scope and managed ownership alias disclosure. The agent reported no remaining
source blocker in those areas. This is independent source review, not an
execution or long-run acceptance claim. Root still needs actual generator
CPU/lag, resource, correctness and duration observations.

## Preparation 002: optional generator affinity diagnostic

Root subsequently authorized a Python-only diagnostic option to investigate
generator scheduling on separate spare CPUs. Product test commit
`d14be5432c7fcce7d2aeaaf5d4218b3f6bd40fd3` adds `--generator-cpus 0,1` to the
codec `run` command. The target is first spawned on the controller's inherited
two-CPU mask, for example CPUs 2 and 3. Only afterward does the controller move
its main thread and every current Python thread, including any child watcher,
to the requested disjoint generator CPUs. The target is never moved. Plans,
phase observations and one-second resources retain actual main and thread masks;
observed leakage invalidates the load. Invalid setup reaps the target, and
cleanup restores and verifies the controller's original mask. Default mode
performs no affinity mutation. Source tests cover malformed CPU lists and an
otherwise-correct main thread whose watcher leaks onto the service CPUs.

The separate protocol agent independently reviewed this change and found no
source blocker. It also checked the explicit sampler stop before expected
target exit, avoiding an exit-versus-procfs race being reported as affinity
failure. These source tests were not executed by the codec agent at this
checkpoint. Root decides whether this remains a diagnostic cohort or becomes
the prospectively frozen policy; split and shared CPU results are not equivalent
resource cohorts.

Because the driver source guard changed, root authorized a **new full prepare**
rather than editing the existing build manifest. It completed at
`2026-11-19T07:56:48.983868+00:00`, again using clean product
`ea5fa528035d025bd7a28698ee7c71194432236c`, at
`ROOT/perf01-codec-checks/package-before-002/`. All 25 preparation commands met
their expected exits, including the original package consumer JIT/AOT checks
and deliberate negative builds. No timing or additional functional workload
was executed by this agent. The original fixed corpus is reused unchanged.

| Preparation 002 artifact | SHA-256 |
| --- | --- |
| `manifest.json` | `4a448f9f9a9e3b9dd1887fced2aae2da33280aa6b6ca7e3c9ef416fe50fc9c87` |
| `commands.json` | `04b48792f0c47303a6a1ff4792e69d048a72994f3d9f46f618899cf41d451512` |
| `aot/NativeWeave.Engines.SyncProof.Tests` | `769d267596d4b77cf96bf7664063f11a6619b2b4f9acc05d904ef9b4bc62c95d` |
| `aot/libnativeweave_engine_syncproof.so` | `3a472d8e51ad5d69a28ade2b00cd23fc9a2bb8d9fa1e2c4df47b769316acff79` |
| `direct-target/release/perf01-codec-direct` | `f91076cf2a31c895914ff7333289210a191d8ef1eaf99f1f6cadabf128831477` |
| `packages/NativeWeave.Core.0.1.0-proof.1.nupkg` | `e664d0611e4f5f98f62fed352a2eb7f22920c1c9f6e32da8bc526550eacaef96` |
| `packages/NativeWeave.Engines.SyncProof.0.1.0-proof.1.nupkg` | `693fa8b4e05b74d53967695507fb46b3985461c678a2b7792fb59cbb3a9cb71c` |

The target `Program.cs`, consumer project, direct Rust source and Cargo lock
hashes are unchanged from preparation 001. The resulting AOT executable and
codec package archive hashes differ after fresh preparation; the actual 002
identities above must be used for its evidence, rather than assuming byte
identity from unchanged input source. The native module and direct executable
hashes remain identical. Any reuse of a measured result still requires matching
the reported binary, fixture and run configuration exactly.

## Source audit: duration, acceptance and evidence retention

This checkpoint reads the controller at
`IzuSharp/NativeWeave@d14be5432c7fcce7d2aeaaf5d4218b3f6bd40fd3`; it performs no
build, load or timing while root owns calibration. The inspected locations are
`tests/Perf01.Codec/driver.py:302-498` (events, scheduling and cleanup),
`driver.py:513-566` (streamed summaries), and
`tests/Perf01.Codec/Program.cs:63-72,215-225` (worker join and owner snapshot).

The controller records a dispatch before writing each frame, and increments
`sent` only after its input drain succeeds. Its completed measurement must have
an actual first-to-last sent dispatch span at least as long as the requested
duration. The declared scheduling guard does not replace this check. Arrival
latencies include controller/IPC observation. Successful throughput divides by
the window from the planned first arrival through the later of the scheduled
last arrival and final measured completion; overdue work is not discarded to
shorten that denominator. Warmup, same-process recovery, final drain and idle
remain separately counted phases. The UTC first-dispatch string is read after
the corresponding input drain; use monotonic dispatch timestamps for precise
duration arithmetic.

For a qualifying long result, integrated acceptance must require all of:

- `complete == true`, `valid == true`, the intended immutable configuration,
  matching loaded module/artifact identities, and an actual dispatch span of at
  least 1,800 seconds;
- zero unexpected measurement failures, timeouts and rejections, plus the
  prospectively frozen p99 and sampled RSS limits; the standalone
  `service_standard_met` field does not itself implement these two limits;
- `recovery_standard_met == true` for the configured recovery phase; this is a
  separate field and is not folded into `service_standard_met`;
- the native route's final `drained` snapshot with `live`, `capacity` and
  `active` all zero and no correctness errors, followed by the separately
  recorded idle interval and successful process retirement.

The frozen C# native route always emits the three owner fields after joining
every worker. Direct Rust and managed ZLibStream deliberately report native
owner counters as unavailable; their completion/worker-retirement evidence
must not be presented as observed NativeWeave counters. Persistent corpus and
allocator/runtime RSS after drain are separate from live native result owners.

`events.jsonl`, `operations.jsonl` and `resources.jsonl` are flushed during the
load. A handled interruption retains pending request IDs, phase progress and
zero long-stage duration credit. An abrupt process/session loss can occur
before cleanup or the final receipt is written; retain its surviving raw rows
as an incomplete attempt. Do not reconstruct a passing long stage solely from
the elapsed wall clock or a partially written result. Result directories are
created exclusively, so a resumed attempt must use a new directory.

The build receipts and corpus locations above are presently local project
workspace paths. This checkpoint does not claim an uploaded archive, a remote
retention period, or retrieval verification. Root's final evidence publication
must record the selected Plan/CI artifact location, hashes and actual retention
policy, then verify readback. A completed source audit grants no 30-minute
acceptance credit and does not establish a performance improvement.
