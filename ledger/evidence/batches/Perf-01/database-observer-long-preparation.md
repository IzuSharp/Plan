# Perf-01 database long preparation with the adopted observer

Status: prospective, before-only preparation. No new long segment has run and no
duration credit is granted by this document. Source review, actual public byte
readback and the integration owner's exclusive timing window precede execution.

## Actual qualification and immutable inputs

The measurement driver is `a3ce0f6295c535b0a81de95fc0f98aa19deb259c`, full tree
`eb6b61e7c159c343513f7a50359f1a6c09f8df77`. The product remains the original before
runtime `ea5fa528035d025bd7a28698ee7c71194432236c`. The adopted deferred-GC/threaded
sampling contract is `98f8e537d87cac9de87cb2d1ae1150465a5c9a052333451f0772398b58ad58c3`.
The actual completed calibration execution is
`04a052a4902d8b191ccb68d8c2a22b8632db37db33a1d51cfe14b786c145325c`; the actual completed
noise extraction is `ba45fbd2141eae25b3896bb7f0fda00af8401a0a897f00e5e1f544e067f2b8a5`.
Both calibration controllers and both noise extractions actually exited zero.
The public numerical qualification is retained at Plan commit
`356ec64c10881004a65d357c7915667120743608`.

| Provider | Fresh confirmed capacity, operations/s | Fixed long rate, operations/s | Planned measured operations | New output ID |
|---|---:|---:|---:|---|
| PostgreSQL | 220 | 144 | 259,526 | `postgresql-observer-002` |
| SQLite | 60 | 40 | 72,091 | `sqlite-observer-001` |

Each qualification uses its entire last three fresh, passing 60-second processes.
The controller, selection and noise hashes are explicit in
`database-observer-long-amendment-001.json`. PostgreSQL's mixed/cycle/page noise
ranges are 34.038736/38.390880/29.685932 ms; SQLite's are
2.880009/5.668908/0.497169 ms. The larger PostgreSQL ranges are retained. These are
the original three-process mean-range noise statistics at 220/60 operations/s;
they are not invented significance bounds for the separate 144/40 long loads.
No earlier failed 25/s calibration, legacy noise or invalid PostgreSQL long is
reused as qualification.

## Preserved workload and acceptance

Both groups keep C16, 1802 scheduled seconds, 16 warmup operations, 32 recovery
cycles and 60 seconds of idle observation. The original mixed cycle/page sequence,
seed 20261119, repetition0, connection reuse, database initial state/durability,
package/application artifacts and CPU split are retained. The actual driver argv
differs from the original long command only in its adopted driver path, fresh
output path, and appended explicit `deferred`/`threaded` flags.

`verify_db_observer_long.py` calls the unchanged original `verify_long.verify`
once. Original verifier SHA-256 is
`3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82`.
All original full-operation correctness, continuous schedule, 100 ms maximum lag,
zero unexpected errors, 500 ms arrival p99, 256 MiB application RSS, independent
persistence, recovery, actual loaded identity and drain requirements remain.
Both the original dispatch span and the conservative successful ordinary-operation
lower bound must reach 1800 seconds. Warmup, recovery and idle earn no credit.

The wrapper adds an AND condition for the exact driver commit/full tree/source
closure, explicit policy descriptors, restored scheduler GC and completed observer
evidence. It reuses the existing `scheduler_gc.valid_receipt` and the previously
reviewed noise helper's actual Perf-01/resource-file byte binding. The standalone
generator observer receipt must equal the summary observer after removing only
its added path/hash fields. No diagnostic continuation whitelist applies. Failure
of either verifier path leaves acceptance false and duration credit zero.

The pinned `sample_in_worker` shields the same executor job, waits for its result,
publishes once and then propagates cancellation. The pinned target awaits its
sampler before publishing final observer metadata; the application target likewise
awaits its sampler before closing the sample file. The added receipt describes
this completed implementation contract. It does not claim an independently
observed zero count of default-pool threads or that every worker thread exited.

The original verifier's RSS report remains phase-only. The unchanged driver's
`qualifies_service_standard` also applies its conservative phase/window overlap
RSS policy; that qualification is required independently. Do not relabel the
original verifier's RSS field as a newly computed overlap-aware maximum.
Application and generator resources are recorded separately. Independent
PostgreSQL-process CPU is unavailable in this path.

## Source, artifact and execution safeguards

| File | SHA-256 |
|---|---|
| `run_db_observer_long_001.py` | `da4ffe3491e129f3b8cb82194798f36fdfb251abb648dd22fb468315d1000c35` |
| `verify_db_observer_long.py` | `0b9f67e0afe54a29ec0d85d8df5e6c51358ebf994d7db871425be975783adb47` |
| `database-observer-long-amendment-001.json` | `4a50ac89cf20dbea779579dbeb1793753fa739de4390525a68cc19b86c75c176` |

The private actual command document SHA-256 is
`fa595b6fda5193319ea5a688d2ee4dab397c254fb039a74b7ce163fc88518bce`.
Its complete argv, package closure and paths remain local. The public amendment
contains only numbers, booleans, fixed enums and reviewed hash identities. Full
frozen source/toolchain maps contain 25 PostgreSQL and 21 SQLite entries; their
canonical JSON hashes are public, and their actual path maps remain private.
The supervisor checks all source/metadata pins, the original nine runtime artifact
pins, actual Python, full driver tree and the actual qualification chain before
starting a child. The wrapper checks the source/toolchain map again after timing.

The owner supplies actual fixed-commit readback in the existing format
`files: [{path, matched, sha256, remote_blob_sha}]`, with the returned commit SHA.
The supervisor requires matched readback for both new runtime scripts and the
amendment. No future publication success is asserted by this preparation.

Each group has exactly two child commands: the existing driver and the post-run
wrapper. Each child command has one nonblocking timing lock; the supervisor has
no outer flock. The owner reserves the serial resource window across the gap.
Both future logs and all output/verification/execution paths are checked before
that group starts, including dangling symlinks. Disk preflight requires 10 GiB
before PostgreSQL, to cover the remaining groups and margin, and 4 GiB before
SQLite. There is no automatic deletion, movement or archive cleanup.

Child exits come only from actual `Popen` completion. An exception or runtime reset
may leave a running/partial receipt and a still-running child; this supervisor does
not automatically kill that process tree or assert cleanup. Before resuming, the
owner must inspect the original driver's owned-process cleanup and timing-lock
release. Unknown exits remain unknown and never imply success. Original invalid
`postgresql-001` and all prior evidence are preserved.

## Owner reproduction

After exact public readback, choose one group (`postgresql` first, then `sqlite`)
and use the retained locked environment and private configuration:

```bash
taskset -c 8 "$LOCKED_PYTHON" -B \
  "$PLAN_CHECKOUT/ledger/evidence/batches/Perf-01/run_db_observer_long_001.py" \
  --root "$PERF01_ROOT" --document "$PRIVATE_CONFIGURATION" \
  --document-sha256 fa595b6fda5193319ea5a688d2ee4dab397c254fb039a74b7ce163fc88518bce \
  --source-sha256 da4ffe3491e129f3b8cb82194798f36fdfb251abb648dd22fb468315d1000c35 \
  --group "$GROUP"
```

Do not wrap this command in another flock. Review each actual result before
starting the next group. This wrapper is before-only. A future after binding must
retain the same a3ce measurement driver, original 3f5e verifier, workload and
equivalent added policy gates, with its actual candidate package identities.

## Actual finite source checks

`checks/database-observer-long-source-001/` records one CPU8 run under the
nonblocking timing lock: **103/103 passed**, actual exit0, 0.110800 seconds. It
checks source syntax/hashes, actual qualification metadata, 34 private source and
metadata pins, exact argv deltas, fresh paths, single locks, source-map/real-byte
rejection boundaries and public enum/hash scope. The nine runtime artifact hash
shapes are retained; the finite check did not rescan those application binaries.
The runtime supervisor will verify their actual bytes before load.

Only extracted bounded helpers ran. No driver was imported, no supervisor or
verifier main was invoked, no original long verifier ran, and no raw measurement
rows were replayed. This evidence validates preparation, not a long result.
