# Perf-01 public workload reproduction map

This directory supplies the unchanged workload configuration and public driver
entry points for Linux x64. It contains nine byte-identical profile copies and a
workload-only extraction in `workloads.json`. It creates no driver, scheduler,
statistic, acceptance result or new workload. Publication/readback of this bundle
and actual measured results are separate records.

## Sources and chronology

Use the same public measurement sources from NativeWeave commit
`2e3995df8d86583ee9443348276ca8d918056bfc` for both product versions. Build the
baseline product from `ea5fa528035d025bd7a28698ee7c71194432236c` and the retained
product from `2e3995df8d86583ee9443348276ca8d918056bfc` (tree
`246de1eb9368efbc62f46ce10c4a8a894d646152`). The JSON pins the actual public relative
driver paths and their previously checked SHA-256 values. Product commit identity,
measurement-source identity and built artifact identity are separate.

The original freeze is `85061c4e01b28fc72a5b20519ce2d8c01d79cae271238ba36e0a3465b0b8f4a3`.
Its original gRPC long rate of 128/s was superseded prospectively by amendment 002
(`2c4d5a0a00cf2f763e4641043f7d6908319ea4d3e7fdbaf2760039bc6808b513`) at 115/s.
The failed 128/s attempt and unexecuted amendment 001 remain history. The DB
observer policy adds the explicit deferred scheduler-GC/threaded sampling modes
before the accepted paired measurements, preserving rates and service limits.
Codec W2 uses 241/s for 67 s; its paired long rate is 192/s. Historical 268/s,
307/s and capacity-specific 384/s observations do not replace those settings.

`source_control_sha256` identifies the original immutable configuration sources.
Their operational orchestration documents are not copied here. The profile
copies retain their original prospective status text because rewriting that text
would change the measured bytes. Current execution status comes from the actual
result/checklist, not a configuration's historical status field.

## Fixed machine, builds and artifact binding

Use .NET SDK **11.0.100**, Rust **1.100.0**, PostgreSQL **18.0**, and measurement
Python **3.12.14**, with the repository locks unchanged. The recorded interpreter
binary SHA-256 is in `workloads.json`. Native producers use locked Release builds,
thin LTO, one codegen unit and unwind, without a host-native ISA override.
Protocol Native AOT targets use x86-64-v2; existing B21/A17 consumers retain their
original compiler defaults. Do not assert that every producer uses the same ISA.

All measured services/databases use CPU IDs 2,3 and generators use 0,1 on one
machine, with one timed process tree at a time. Reuse the same physical machine
and assigned CPUs for each pair. Frequency/power controls and dropped OS caches
were unavailable; a fresh application/database is not a cold OS-cache claim.
The fixed service standard is zero unexpected errors, arrival p99 at most 500 ms,
application sampled peak RSS at most 256 MiB, and generator dispatch lag at most
100 ms. A resource or generator failure stays a failed/ineligible observation.

Run the following examples **from the public driver checkout**. Set local
`PERF_PYTHON`, `PERF_DOTNET`, `PERF_PRODUCT`, `PERF_OUT`, `PERF_PG_BIN`,
`PERF_VERSION`, `PERF_UPGRADE_VERSION` and `PERF_CONFIG` first. These mean the exact
interpreter/executable, selected clean product checkout, new absolute output
root, PostgreSQL 18 bin directory, separate exact package versions, and this Plan
configuration directory. These are user-selected local paths, not saved host
paths from the measurement machine. Put the pinned tools on PATH as required by
the existing builders. Run each producer before timing.

```sh
(cd "$PERF_PRODUCT" && "$PERF_PYTHON" eng/task07_native.py \
  --output "$PERF_OUT/native-stable")
(cd "$PERF_PRODUCT" && "$PERF_PYTHON" src/Packaging.Domain/prepare.py \
  --output "$PERF_OUT/packages" \
  --previous-version "$PERF_VERSION" --candidate-version "$PERF_UPGRADE_VERSION" \
  --native-manifest "$PERF_OUT/native-stable/manifest.json")
"$PERF_PYTHON" tests/Reference.TaskService/package_probe.py \
  --source "$PERF_PRODUCT" --runner tests/Reference.TaskService/run.py \
  --feed "$PERF_OUT/packages/previous/feed" --version "$PERF_VERSION" \
  --postgres-bin "$PERF_PG_BIN" --output "$PERF_OUT/reference" \
  --variants baseline --providers sqlite --modes jit aot --protocols http1 --build-only
"$PERF_PYTHON" tests/Perf01.Database/prepare_observer.py \
  --package-probe "$PERF_OUT/reference" --output "$PERF_OUT/db-observer" \
  --dotnet "$PERF_DOTNET"
"$PERF_PYTHON" tests/Perf01.Protocols/build.py \
  --feed "$PERF_OUT/packages/previous/feed" --version "$PERF_VERSION" \
  --sdk "$PERF_DOTNET" --output "$PERF_OUT/protocols" \
  --package-manifest "$PERF_OUT/packages/manifest.json" \
  --native-manifest "$PERF_OUT/native-stable/manifest.json"
```

Use fresh product worktrees without prior managed bin/obj outputs and the
**complete 17-package previous feed**, including all common packages, for each
role. The unused candidate feed is not the measured closure. Record native and
package producer commits, every selected archive hash, actual consumer resolution
(including the observer's project.assets.json and resolved nupkg SHA-256/SHA-512),
AOT executable hashes and actual mapped native hashes. Matching native hashes
alone does not prove that common managed code came from the right role. Preserve
all producer manifests/commands/locks. New local builds are new evidence and
cannot silently stand in for this run's hash-bound binaries.

The reference producer's `--providers sqlite --build-only` is its original build
selection; the resulting application supports both measured providers. Each
measurement creates its own provider instance. Use the actual after/before
manifests, not filenames or version text alone, to select a role.

## HTTP and gRPC: one public cell at a time

| Profile | Group | Offered calls/s | Client slots | Requested s |
| --- | --- | ---: | ---: | ---: |
| profiles/http1-small.json | http | 16 | 4 | 20 |
| profiles/http2-small.json | http | 16 | 4 | 20 |
| profiles/http1-large.json | http | 8 | 4 | 30 |
| profiles/http2-large.json | http | 8 | 4 | 30 |
| profiles/grpc-unary.json | grpc | 16 | 4 | 20 |
| profiles/grpc-streams.json | grpc | 16 | 4 | 20 |

The small HTTP profiles mix tiny responses and real 1 MiB upload/downloads; the
large profiles mix real 8 MiB upload/downloads. Unary contains 64 B and 65,536 B
payloads. Each streaming method exchanges 32 messages of 4,096 B. Exact weights,
server/client bounds, timeouts, hash rules, connection/stream counts, seed and
warmup/recovery/idle parameters are in the unchanged profiles and public
`tests/Perf01.Protocols/run.py`. All these protocol paths use real TLS sockets;
gRPC negotiates identity only. Standalone codec gains are not network compression
gains.

Set `PERF_SERVER_BUILD` to the selected role's build.json,
`PERF_COMMON_CLIENT` to the single baseline AOT client build.json, and
`PERF_CELL` to a fresh output directory. This example is one H1 small cell:

```sh
taskset -c 2,3 "$PERF_PYTHON" tests/Perf01.Protocols/run.py prepare \
  --build "$PERF_SERVER_BUILD" --client-build "$PERF_COMMON_CLIENT" \
  --profile "$PERF_CONFIG/profiles/http1-small.json" \
  --group http --rate 16 --duration 20 --concurrency 4 \
  --generator-cpus 0,1 --certificate "$PERF_CERT" --private-key "$PERF_KEY" \
  --output "$PERF_CELL"
taskset -c 2,3 "$PERF_PYTHON" tests/Perf01.Protocols/run.py run \
  --plan "$PERF_CELL/plan.json" --exclusive-lock "$PERF_TIMING_LOCK"
```

Use both local certificate/key options or omit both on the first prepare to let
the existing driver generate the localhost certificate/key. Keep that same local
pair for all roles; do not publish the key. The six short profiles run three
independent processes per role in before/after/direct, direct/after/before,
before/after/direct order. This directory adds no loop or retry mechanism.

Build the direct server through the existing public entry point, retaining that
same common client:

```sh
"$PERF_PYTHON" tests/Perf01.Protocols/build-direct.py \
  --client-build "$PERF_COMMON_CLIENT" --output "$PERF_DIRECT_PROTOCOLS"
```

The direct fixture uses locked Hyper/rustls/Tonic and a current-thread Tokio
runtime. Its narrower actual-frame versus configured-maximum byte reservation
semantics remain a comparison limit. No pure-C# protocol result is available.

## PostgreSQL and SQLite: explicit effective flags

The public `tests/Perf01.Database/run.py` derives its cell plan from these flags
and the settings in `src/Benchmarks.Domain/profile-v1.json`. Use the inherited
SQLite WAL/FULL/foreign-key/BEGIN IMMEDIATE/5,000 ms busy-timeout and PostgreSQL 18
fsync/synchronous-commit/full-page-write/ReadCommitted settings. Do not use the
historical B23 profile's workload rates or seed. Perf-01 seeds 128 rows and mixes
50% durable business cycles with 50% typed 100-row pages at seed 20261119.

| Stratum | PostgreSQL rate/s | SQLite rate/s | Concurrency | Requested s | Processes/role |
| --- | ---: | ---: | ---: | ---: | ---: |
| C1 | 5 | 5 | 1 | 60 | 1 |
| C4 | 20 | 20 | 4 | 20 | 1 |
| C8 | 40 | 40 | 8 | 20 | 1 |
| C16 | 180 | 50 | 16 | 60 | 3 |

Example C16 SQLite cell, with `PERF_REFERENCE` and `PERF_OBSERVER` selecting the
same role's completed producer outputs:

```sh
flock --nonblock "$PERF_TIMING_LOCK" taskset -c 2,3 "$PERF_PYTHON" \
  tests/Perf01.Database/run.py \
  --package-probe "$PERF_REFERENCE" --observer "$PERF_OBSERVER" \
  --route nativeweave-aot-rust --provider sqlite --protocol http1 \
  --scenario mixed --stage short --variant before --repetition 0 \
  --rate 50 --seconds 60 --concurrency 16 --warmup 16 \
  --recovery-requests 16 --idle-seconds 5 --seed 20261119 \
  --generator-cpus 0,1 --continue-classified-overload --compact-observation \
  --scheduler-gc-policy deferred --resource-sampling-policy threaded \
  --max-p99-ms 500 --max-rss-mib 256 --output "$PERF_CELL" \
  --isolation-note 'Exclusive local window; service/database CPUs2,3; generator CPUs0,1'
```

For PostgreSQL use `--provider postgresql --rate 180 --postgres-bin "$PERF_PG_BIN"`.
The before/after source and output selection changes; all workload flags stay
equal. For C16 use the role order in `workloads.json`. C1/C4/C8 are descriptive,
without borrowing C16 significance. Each new cell uses an equivalent fresh
database; the independent persisted SQL result is part of acceptance.

Build comparators with
`tests/Perf01.Database/prepare_comparators.py --product-root "$PERF_PRODUCT" --output "$PERF_DB_COMPARATORS"`.
Comparator cells replace the observer option with
`--comparators "$PERF_DB_COMPARATORS/comparators.json"` and use
`--route direct-rust --variant direct` or `--route managed-aot --variant managed`.
Preserve the existing narrower comparator lifetime/fault/cancellation scope.
BUSY/LOCKED observations, explicit business retry count and durable commits must
stay separate; internal busy-handler retry/sleep is not inferred from HTTP errors.

## Compression and decompression

The public codec driver creates the corpus from fixed seed 2654435769: 256 B,
4 KiB, 1 MiB and 4 MiB, weights 50/25/20/5, equal compressible/pseudorandom data,
equal compression/decompression and array/owned interfaces. It retains the
160-action cycle, zlib format, level 6, Adler32, 4 MiB raw/decoded limit and
4,259,840 B encoded limit. These are source-defined, not platform codec defaults.

```sh
"$PERF_PYTHON" tests/Perf01.Codec/driver.py prepare \
  --product-root "$PERF_PRODUCT" --output "$PERF_OUT/codec"
"$PERF_PYTHON" tests/Perf01.Codec/driver.py corpus \
  --direct "$PERF_BEFORE_CODEC/direct-target/release/perf01-codec-direct" \
  --output "$PERF_CORPUS"
flock --nonblock "$PERF_TIMING_LOCK" taskset -c 2,3 "$PERF_PYTHON" \
  tests/Perf01.Codec/driver.py run \
  --manifest "$PERF_CODEC_MANIFEST" --corpus "$PERF_CORPUS" \
  --route nativeweave --interface mixed --action mixed --workers 2 \
  --queue 64 --inflight 256 --rate 241 --duration-seconds 67 \
  --warmup-seconds 20 --recovery-seconds 10 --recovery-rate 1 \
  --idle-seconds 5 --deadline-ms 1000 --max-lag-ms 100 \
  --generator-cpus 0,1 --output "$PERF_CELL"
```

W1 changes only workers/rate/duration to 1/134/120; W2 is 2/241/67. All four roles
run three independent processes in the exact order stored in `workloads.json`.
Use the same generated/hashed corpus for both versions. The direct-rust and
managed-zlib routes use the original before codec manifest, including its exact
direct executable. The managed owned label aliases the managed array path; its
valid-corpus isolated-call observations do not prove equivalent ownership,
strict trailing-input semantics or end-to-end arrival performance.

The public driver also accepts `--action compress|decompress`,
`--interface array|owned`, and `--case 0..7` for isolated diagnostics. These
optional invocations are distinct from the frozen full-mixture formal cohorts
and must not replace them. Corpus hashes, byte-for-byte round trips and limit
rejections remain required.

## Five paired long groups and capacity

| Group | Rate/s | Slots/workers | Requested s | Profile / driver |
| --- | ---: | ---: | ---: | --- |
| HTTP | 500 | C64 | 1802 | Public product tests/Perf01.Protocols/profile-v1.json, group http |
| gRPC | 115 | C64 | 1802 | profiles/grpc-budget-profile-v2.json, group grpc |
| PostgreSQL | 144 | C16 | 1802 | DB mixed, HTTP1 |
| SQLite | 40 | C16 | 1802 | DB mixed, HTTP1 |
| Codec | 192 | W2 | 1802 | Codec full 160-action mix |

Use the same public command templates with these values. Protocol profiles use
24 warmup calls, 32 recovery calls at 250 ms intervals and 60 s idle. DB uses
`--stage soak --warmup 16 --recovery-requests 32 --idle-seconds 60`, retaining
all explicit GC/sampling/overload/seed/limit flags above. Codec retains 20 s
warmup and 10 s recovery at 1/s, changing idle to 60 s. Warmup, recovery, drain
and idle are separate from the actual effective load duration. A requested 1802 s
alone does not prove the required 1800 effective seconds. Actual 10 segment
intervals, success populations, integrity/durability, generator validity and
post-drain resources are accepted only by their unchanged hash-bound verifiers.

`workloads.json.capacity` copies the existing finite sampled-rate policy, not a
new implementation. Use the same public single-cell commands for the actual
listed ladder/refinement/confirmation cells and preserve failures and recovery.
Capacity DB uses 16 warmup/16 recovery/5 s idle; codec capacity intentionally uses
5 s warmup/4 s recovery/5 s idle, distinct from fixed-comparison 20/10. The two
included capacity protocol profiles are exact existing `profile-short.json`
bytes, differing from the corresponding long/base profile only by 5 s idle.
Ladder points last 30 s, confirmations 60 s in three fresh processes; the existing
bounded refinement/stepdown rule and generator-limited/unbracketed caveats remain.
No failed rate is silently retried or used to retune the fixed paired long rate.

## Evidence boundary

Record all actual planned/issued/accepted/successful populations, tails, errors,
CPU/RSS/GC where available, package/native/artifact identities and original
correctness/drain outputs. Compare means/percentiles with their original scopes;
whole-profile resources cannot be assigned to individual scenario partitions.
Existing numerical reports provide exact result values and evidence hashes;
this bundle supplies configuration and commands only. It does not publish
operational orchestrators, raw argv/environment, host paths, TLS keys, binaries,
database contents or synthetic payload archives. Fresh public invocations do
not by themselves claim this run's source review, provenance or 30-minute credit.
