# Perf-01 separate gRPC mode resource profiles

Status: **source-prepared only**. No build, server/client, profile, raw extraction
or test was executed while preparing these files. They reuse the existing
`tests/Perf01.Protocols/run.py`, adapter, independent Native AOT client, server
fixture and offline reader. There is no new driver or execution framework.
Every profile and command is ineligible for formal comparison/noise/long credit.

## Fixed small workload

Each fresh process measures exactly one ordinary mode over HTTP/2 + TLS. The
configuration derives from `protocol-layered/grpc-streams.json`: server/client
limits, transport defaults, seed 20261119 and resource gates are unchanged.
The only selected payload mix is the row below. C4, 16 calls/s and a nominal
20-second duration reuse the existing legal small layered profile. The existing
100 ms scheduling guard produces **323 planned measurement calls** and 20.125
seconds of planned first-to-last spacing. Actual counters and denominators come
from the result, not that nominal schedule.

| File / mode | Data bytes / configured messages | Request messages per successful call | Response messages per successful call | Request / response Data bytes per successful call |
|---|---:|---:|---:|---:|
| `unary.json` | 64 / 1 | 1 | 1 | 64 / 64 |
| `server-stream.json` | 4,096 / 32 | 1 | 32 | 4,096 / 131,072 |
| `client-stream.json` | 4,096 / 32 | 32 | 1 | 131,072 / 0 |
| `duplex.json` | 4,096 / 32 | 32 | 32 | 131,072 / 131,072 |

The client-stream response has an empty Data field, but its validated aggregate
acknowledgement contains nonzero protobuf bytes. Encoded-byte counters exclude
the five-byte gRPC envelope, HTTP/2 framing and TLS. The existing independent
client validates protobuf content, hashes, cardinalities, status and trailers.
This diagnostic adds no compression: identity-only remains fixed. Deadline and
cancellation probes remain in the accepted mixed protocol workloads; they are
not inserted into these four ordinary-mode resource windows.

Each cell retains 24 warmup calls, 32 same-server recovery calls at a 0.25-second
period, and five seconds of post-load idle. These phases are separate from the
measurement counters. Original service checks remain zero unexpected errors,
arrival p99 at most 500 ms, sampled application RSS at most 256 MiB, and both
native/managed payload caps at 64 MiB. The per-request retained cap is the
already selected gRPC 64 MiB cap; max message size remains 1 MiB. C4 is a client
limit, not an assertion that four HTTP/2 streams are continuously active.

## Immutable actual before inputs

The before server and **common independent client** both use
`ROOT/perf01-build/before/protocols-v2/build.json` SHA-256
`818643898f04803f3070cb55f6bf0894dc23c1f9c21ff7d556a8e99b6b96d8c3`,
from before product commit `ea5fa528035d025bd7a28698ee7c71194432236c`.
The existing recorded actual identities are:

| Artifact | SHA-256 |
|---|---|
| Before server AOT | `5ba1df0946ece4a490d7bb43b295b7c720c3d32159c7e47e0cd28f0a3098460d` |
| Common client AOT | `acb1c163cd51e291f58dbe51ae12c04f82c2b51538aa36e446a05890e06aadd0` |
| Native server library | `4827a6ecc76f871e0b4828f4ff6fe23a0d0a4ca1c57c5fc89a10a8e4d83ffe69` |
| TLS test certificate | `9c5c88b63e03a095061b6af052a3c8aa714a96bcf3a01fde9124bbd781b57b35` |
| TLS test key, local only | `c9238030f5a0b9c7352007b3edca6ca75b92a85291e7d56d8918e2ee3dbd789a` |

These pins were copied from the immutable protocol command records, not rescanned
from binaries or private TLS contents during active calibration. Existing
`prepare` verifies the actual package, executable, native, source and TLS files
before use. `commands.json` binds the exact current driver/helper/source hashes,
Python 3.12.14, fixed common client, TLS pair and four new profile hashes.
Services stay on CPUs 2,3 and generators on CPUs 0,1. Core counters retain their
existing one-second sampling; the measurement protocol/source is unchanged.

## Minimal execution queue, after owner releases the resource

`commands.json` contains sixteen concrete argument arrays in execution order:
prepare, mark-profile, run and check for unary, server-stream, client-stream and
duplex. Its source-prepared SHA-256 is
`81921bd9809844d54214f29f398058b68c8c6561991b06ee11f2b8fdb530d5f0`.
The integration owner must publish/review the exact source and command pins and
record actual argv, exit, log hashes and output paths when execution happens.
Nothing in this document authorizes execution during another active timing window.

The existing `prepare` command freezes a plan and verifies prebuilt artifacts;
it performs no compilation. It refuses an existing output directory. The next
command copies the unchanged selected profile to a new `profiling.json` with
exclusive file creation. Both that marker and `profile.json` have
`formal_timing_eligible=false`. The existing comparison reader explicitly retains
profiling-only ineligibility, and the long verifier rejects the marker. Do not
remove either marker or relabel a profile as a formal comparison.

The following executes **one selected mode** from the exact arrays. Repeat with
`server-stream`, `client-stream`, then `duplex` only after the preceding cell and
its check finish. This small shell snippet delegates all work to the existing
driver; it is not a new measurement controller. The owner retains exclusive
ownership across the gaps between commands. The supplied prepare/check commands
take the existing nonblocking timing lock. `run` acquires that lock internally;
do not wrap it in a second flock on the same file.

```bash
PERF01_ROOT=/workspace/scratch/01c249676f47
source "$PERF01_ROOT/perf01-toolchain/env.sh"
PERF01_PY=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
PERF01_E="$PERF01_ROOT/.worktree/Perf-01-linux/Plan/ledger/evidence/batches/Perf-01"
PERF01_MODE=unary
taskset -c 8 "$PERF01_PY" - "$PERF01_E/grpc-mode-profiles/commands.json" "$PERF01_MODE" <<'PY'
import hashlib, json, subprocess, sys
from pathlib import Path
document = Path(sys.argv[1])
assert hashlib.sha256(document.read_bytes()).hexdigest() == '81921bd9809844d54214f29f398058b68c8c6561991b06ee11f2b8fdb530d5f0'
configuration = json.loads(document.read_text())
python = configuration['python']
assert '.'.join(map(str, sys.version_info[:3])) == python['version']
assert Path(sys.executable).resolve() == Path(python['executable']).resolve()
assert hashlib.sha256(Path(sys.executable).resolve().read_bytes()).hexdigest() == python['sha256']
assert sys.argv[2] in {row['id'] for row in configuration['rows']}
for name, expected in configuration['required_source_sha256'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
for name, expected in [(configuration['before_server_build']['path'], configuration['before_server_build']['sha256']),
                       (configuration['tls']['certificate'], configuration['tls']['certificate_sha256']),
                       (configuration['tls']['private_key_local_only'], configuration['tls']['private_key_sha256'])]:
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
for command in configuration['commands_before']:
    if command['mode'] == sys.argv[2]:
        print(json.dumps({'id': command['id'], 'argv': command['argv']}), flush=True)
        subprocess.run(command['argv'], cwd=command['working_directory'], check=True)
PY
```

Preserve failed/partial cells and logs. The post-run command requires completed,
valid, service-standard-passing, correctly drained results, all 323 measured
business calls, and passed recovery; driver exit zero alone is insufficient.
There is no automatic retry, rate change or favorable subset selection.

## Results to retain and interpret

`result.json` already provides each mode's offered/dispatched/admitted/completed
calls, ordinary successes, actual maximum in-progress calls, arrival percentiles,
message/Data/encoded totals and rates, server/client/adapter/controller CPU/RSS,
server managed allocation and GC deltas, native/managed high-water gauges,
recovery, idle gauge recession and retirement receipt. Keep the underlying
`requests.jsonl`, independent `execution/client/operations.jsonl`,
`execution/process-resources.jsonl`, server managed time series and close/cleanup
receipts. Source/producer/package/loaded-native identities remain bound in the
existing plan/adapter/result chain.

For the actual first/last allocation observation bracket, reuse
`protocol_compare.read_cell`, which also rechecks all raw outcomes/cardinalities
and source identities. Run this read-only extraction **after all profile process
trees have stopped**, under the same nonblocking timing lock. No large raw file
was read during this source preparation. One example for an actual unary result:

```bash
PERF01_NW="$PERF01_ROOT/.worktree/Perf-01-linux/NativeWeave"
PERF01_CELL="$PERF01_ROOT/perf01-evidence/profiling/before/grpc-unary-resources-001"
/usr/bin/flock --nonblock "$PERF01_ROOT/perf01-evidence/timing.lock" \
  taskset -c 8 "$PERF01_PY" - "$PERF01_E" "$PERF01_NW" "$PERF01_CELL" before \
  "$PERF01_CELL-observation.json" <<'PY'
import hashlib, json, sys
from pathlib import Path
analysis, product, cell, variant, output = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4], Path(sys.argv[5])
assert not output.exists()
document = analysis / 'grpc-mode-profiles/commands.json'
assert hashlib.sha256(document.read_bytes()).hexdigest() == '81921bd9809844d54214f29f398058b68c8c6561991b06ee11f2b8fdb530d5f0'
configuration = json.loads(document.read_text())
python = configuration['python']
assert '.'.join(map(str, sys.version_info[:3])) == python['version']
assert Path(sys.executable).resolve() == Path(python['executable']).resolve()
assert hashlib.sha256(Path(sys.executable).resolve().read_bytes()).hexdigest() == python['sha256']
source = analysis / 'protocol_compare.py'
assert hashlib.sha256(source.read_bytes()).hexdigest() == 'a8cead371ceed5b2d6a865c1e6b113110005db7880af7566d5125f46429c032f'
sys.path.insert(0, str(analysis))
import protocol_compare as existing
a21_path = product / 'src/Benchmarks.Harness/nativeweave_bench.py'
reader_path = product / 'tests/Perf01/verify_long.py'
pins = configuration['required_source_sha256']
for path in (a21_path, reader_path):
    assert hashlib.sha256(path.read_bytes()).hexdigest() == pins[str(path)]
a21 = existing.module('grpc_profile_existing_a21', a21_path)
reader = existing.module('grpc_profile_existing_reader', reader_path)
observed = existing.read_cell(cell, variant, a21, reader, existing.sha(a21_path))
receipt = {'task': 'Perf-01', 'formal_timing_eligible': False, 'duration_credit_seconds': 0,
           'scope': 'Existing reader, one ordinary mode; no allocation stack or formal timing claim',
           'reader_sha256': existing.sha(source), 'observation': observed}
with output.open('x') as stream:
    json.dump(receipt, stream, indent=2, sort_keys=True); stream.write('\n')
assert observed['eligible'] is False
assert observed['issues'] == ['Profiling-only cell cannot establish a timing comparison'], observed['issues']
assert len(observed['scenarios']) == 1
print(json.dumps({'output': str(output), 'sha256': existing.sha(output), 'formal_timing_eligible': False}))
PY
```

The reader reports the original expected profiling-only issue; do not suppress
it or call the cell comparison-eligible. Additional correctness/resource/source
issues remain in the written receipt and cause the example to fail.

Managed allocation is approximate **whole-server-process**
`GC.GetTotalAllocatedBytes(false)` growth between the first/last one-second
measurement snapshots. Report its actual bracket duration and MiB/s, not exact
bytes/call. Leading/trailing partial seconds may be absent. Shared transport,
fixtures and telemetry are included even when only one mode is active. There
is no allocation-stack, unique codec/marshalling attribution or native allocator
count. Client managed allocation/GC are unavailable; client CPU/RSS are sampled.
RSS is retained process memory, not cumulative allocation. Socket/connection
observations are not a measurement of HTTP/2 stream count. Idle connections may
remain pooled until shutdown; owner/request/payload drainage and final close
receipts have their own explicit checks.

## Later after package

Use these exact profile/source/TLS/common-client hashes and all existing load and
resource fields. Change only `prepare --build` to the actual reviewed final after
server producer, plus fresh after output paths and receipt variant labels. Bind
that producer's actual package/AOT/native/source hashes before running it. Keep
`--client-build` pointing to the immutable **before-v2** producer. Existing
`prepare` rejects changed C#/.proto/.csproj fixture sources relative to that client.
No after path/hash is invented here. The same ordinary-mode profiles are
descriptive before/after resource evidence; they neither reuse the six formal
comparison partitions' noise bands nor replace the accepted mixed gRPC long test.
