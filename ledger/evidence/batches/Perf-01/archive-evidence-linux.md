# Perf-01 finalized evidence publication

Status: source-prepared archive procedure. No large evidence file was read,
compressed, restored or uploaded while preparing this note. The packer and its
finite synthetic checks are not yet executed. Run those checks in a separate
validation window before using the tool; packing must remain outside all
measurement and profiling intervals. Root owns upload and readback.

The user authorized publication of this project's synthetic numeric samples,
resource series and correctness checklists. Keep exact input bytes so readers
can recover the raw observations, recompute summaries and repeat the common
long-duration consistency check. Archive acceptance and measurement acceptance
are separate: a finalized failed cell can be retained, but packaging never
changes its failure state or grants duration credit.

## Complete publication set

All paths below are relative to one finalized cell. Include the original
`tests/Perf01/verify_long.py` output as `duration-verification.json`, including
its verifier source hash and every consumed file hash. Preserve profiling
markers and affinity snapshots when present. Do not edit or redact original
verifier inputs in place: their hashes bind the reported result.

| Domain | Exact public inputs retained | Purpose |
| --- | --- | --- |
| Codec | `summary.json`, `plan.json`, `result.json`, `phase-progress.json`, `operations.jsonl`, `events.jsonl`, `resources.jsonl`; optional `command.json` | All dispatch/admit/completion counts, individual call/consume/release/queue/arrival intervals, managed allocation counters, original/encoded byte counts, CPU/RSS/GC/owner samples, phase timing, drain and payload/limit checks. The files contain fixture identities and counts, not payload dumps. |
| HTTP / gRPC | `result.json`, `plan.json`, `adapter.json`, `oracle.json`, `profile.json`, `requests.jsonl`, `dispatches.jsonl`, `events.jsonl`, `execution/receipt.json`, `execution/ready.json`, `execution/processes.json`, `execution/client/operations.jsonl`, `execution/process-resources.jsonl`, `execution/server/closed.json`; route-appropriate `execution/server/managed-resources.jsonl` or `native-resources.jsonl`; optional `started.json` | Frozen protocol/cardinality oracle; all scheduled, issued and completed operations; successful payload/message counts and raw client outcomes; process/GC/native gauges; application/client identity, actual mappings, recovery and shutdown proof. The native route's raw managed samples also contain available native owner gauges. |
| SQLite / PostgreSQL | `summary.json`, `progress.json`, `frozen-inputs.json`, `plan.json`, `target.json`, `dataset.json`, `observation.json`, `observation.events.jsonl`; the selected `applications/<receipt-dir>/receipt.json`, `perf01.json`, `generator-resources.jsonl`, `generator-observer-receipt.json`, `application/resources.jsonl`; optional `classified-errors.jsonl`, `postgres/identity.json` | A21 planned and observed request ledgers, expected synthetic values, complete resource series, executed business counts, SQLite BUSY/retry classifications, independent durable oracle, recovery and application/engine identities. The raw IPC event file is retained without decoding/re-encoding its source bytes. |

Common optional files are `controller-affinity-before.json`,
`controller-affinity-after.json`, `controller-affinity-end.json`,
`controller-affinity-restored.json`, `profile-driver.json`,
`postgres-profile-summary.json` and `profiling.json`. The last three can make
a cell ineligible for formal measurement and must not be dropped to make an
archive appear eligible.

The exact selected application directory comes from the existing DB summary,
mapped relative to the original `plan.oracle.dataset` parent, matching the
common verifier. The packer accepts only the expected
`applications/<one-directory>/receipt.json` shape. It never recursively follows
an artifact map, command path, package directory or arbitrary receipt path.

Also publish the small exact producer, package, native, common-client and corpus
JSON manifests needed by each row. The optional `--binding NAME=PATH` labels
are `build`, `client-build`, `direct-build`, `packages`, `native`, `corpus`,
`policy`, `source` and `observer`; they become `bindings/NAME.json`. These are
explicit metadata inputs, not permission to follow their referenced files.
The final report's index must identify the relevant NativeWeave, Plan and
Design commits; raw-input and build-manifest hashes; executable and loaded
native hashes; frozen driver source and dependency locks; corpus/seed; selected
rate, mix, concurrency, masks and SLO. Existing driver manifests supply those
identities. Missing provenance must be resolved before publishing a comparison.

## Excluded inputs and actual schema review

The fixed allowlist excludes TLS certificate/key PEM files, runtime server and
client configurations, `application/config.private.json`, SQLite database/WAL/
SHM files, PostgreSQL data directories, payload/body/header captures, binaries,
NuGet archives, free-form stdout/stderr logs and supervision registries/receipts.
Their paths or content hashes may remain in original identity manifests;
that is a reference to an excluded input, not archived contents.

Current DB `target.json` contains only the local synthetic connection URI
`postgresql://nativeweave@127.0.0.1:<port>/postgres`: the producer uses isolated
`initdb --auth=trust`, and private application configuration is separate
(`src/Benchmarks.Domain/run.py`, target construction). The packer checks the
actual URI and refuses a changed username, host, password, query or database.
Do not assume a future target is safe because the current source is safe.

`src/Benchmarks.Domain/supervision.py` stores a registration token in owned
process records and its supervision receipt. Those files are unnecessary for
the common verifier and are excluded, while the application drain proof and
supervision outcome already in the public summary remain. If a later report
needs additional process metadata, create a separately reviewed public
projection with both source and projection hashes and an explicit omission
description; it is not a byte-identical substitute for a required verifier
input.

The packer walks JSON scalars without materializing large DB arrays. It rejects
known private field names, PEM text, bearer-shaped secrets, unreviewed URI
credentials and nonempty embedded stderr, and also inspects decoded
`wire_base64` IPC events. JSONL may be empty where a valid producer emits an
empty optional classification ledger. It rejects symlink inputs and escaped
paths. These are conservative checks for the inspected fixture schemas, not a
general secret-detection guarantee. The owner must still review the selected
metadata inventory. An input guard failure leaves an incomplete local bundle
without a final manifest; do not upload it or silently omit the rejected numeric
file. Any nonzero pack/verify exit is a failed archive, including a final
readback failure after the manifest has been written.

## Exact bytes, bounded shards and retrieval

`pack_evidence.py` splits each selected original file into consecutive chunks
of at most 8 MiB raw bytes by default. Each chunk is independently gzip encoded
with level 6, zero timestamp and no embedded source filename. Chunk boundaries
may cut a JSON line or UTF-8 character; restoration concatenates the decompressed
bytes in listed order before interpreting the file. No rounding, sampling,
timestamp normalization, redaction or JSON reserialization occurs.

The manifest records each file's full SHA-256, byte count and newline count,
each compressed and uncompressed chunk hash/length, packer source hash,
verifier identity and original acceptance/duration verdict. The packer verifies
that required consumed-file hashes match the original verifier receipt and
that file identity/size/mtime did not change during scanning and packing. A
successful pack includes a complete readback through its bounded verifier.

Local safety bounds are 1–32 MiB per raw chunk, at most the selected raw chunk
limit plus 64 KiB per compressed chunk, 128 selected files, 16 GiB total raw
bytes, 20,000 unique chunks, 64 MiB per small control JSON, depth 64 and
4,194,304 characters per streamed JSON scalar. These are this utility's bounds,
not claims about GitHub limits. A larger valid cell requires an explicit source
review of the needed bound. Restore creates a new destination outside the
bundle, opens files exclusively, validates paths, and refuses duplicate or
oversized chunks. A fresh trusted manifest hash in the report index is still
required; hashes within a modified manifest alone do not authenticate it.

Use a fresh directory such as
`ledger/evidence/batches/Perf-01/raw/<before-or-after>/<group>-<cell-id>/`
for the manifest and numbered `chunks/*.gz`. The final Plan index should record
the merged Plan commit, exact path, manifest SHA-256, readback date and outcome,
original receipt verdict, and the corresponding report row. Root uploads only
the manifest and its listed chunks through the approved GitHub connector.
Retain the files in the project history without a scheduled expiry; this is
repository retention, not a guarantee against later repository deletion or
history rewriting. Record any additional CI artifact URL and its actual expiry
separately. Existing ordinary CI artifacts are not a substitute for these raw
files and their independent retrieval check.

## Commands for a separate validation and archival window

First run the small synthetic checks. They use temporary files, including a
multi-chunk UTF-8 JSONL, an empty JSONL, deliberately excluded fake private
inputs, changed hashes, symlinks, unsafe paths and damaged/bounded gzip members.
Database-specific fixtures retain original absolute dataset/receipt paths while
restoring under a different root, and reject escaping receipt paths and changed
connection credentials/host/database/port.
They do not start an application or claim measurement acceptance.

```sh
PERF_ROOT=/workspace/scratch/01c249676f47
PERF_PLAN="$PERF_ROOT/.worktree/Perf-01-linux/Plan"
PERF_DRIVER="$PERF_ROOT/.worktree/Perf-01-linux/NativeWeave"
PERF_ARCHIVE="$PERF_PLAN/ledger/evidence/batches/Perf-01"
PERF_PYTHON=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3

taskset -c 8 "$PERF_PYTHON" "$PERF_ARCHIVE/test_pack_evidence.py"

PERF_GROUP=codec
PERF_CELL="$PERF_ROOT/perf01-evidence/long/before-codec-001"
PERF_RECEIPT="$PERF_ROOT/perf01-evidence/verification/before-codec-001.json"
PERF_BUNDLE="$PERF_ROOT/perf01-archive/before-codec-001"

taskset -c 8 "$PERF_PYTHON" "$PERF_DRIVER/tests/Perf01/verify_long.py" \
  --group "$PERF_GROUP" --output "$PERF_CELL" --receipt "$PERF_RECEIPT"

taskset -c 8 "$PERF_PYTHON" "$PERF_ARCHIVE/pack_evidence.py" pack \
  --group "$PERF_GROUP" --cell "$PERF_CELL" --receipt "$PERF_RECEIPT" \
  --output "$PERF_BUNDLE" --shard-mib 8 \
  --binding build="$PERF_ROOT/perf01-codec-checks/package-before-002/manifest.json" \
  --binding corpus="$PERF_ROOT/perf01-codec-checks/corpus/manifest.json"
```

The example cell paths are proposed destinations, not claims that those cells
exist or passed. Create receipt parents as needed; use the actual finalized
cell and its pinned build. Verify the packer manifest and member inventory
before upload. Retrieve the published manifest and all its listed chunks into
a separate fresh local directory, check the manifest against the hash in the
merged Plan index, then restore and repeat the common consistency check:

```sh
PERF_DOWNLOADED="$PERF_ROOT/perf01-readback/before-codec-001"
PERF_RESTORED="$PERF_ROOT/perf01-restored/before-codec-001"
taskset -c 8 "$PERF_PYTHON" "$PERF_ARCHIVE/pack_evidence.py" verify --bundle "$PERF_DOWNLOADED"
taskset -c 8 "$PERF_PYTHON" "$PERF_ARCHIVE/pack_evidence.py" restore \
  --bundle "$PERF_DOWNLOADED" --output "$PERF_RESTORED"
taskset -c 8 "$PERF_PYTHON" "$PERF_DRIVER/tests/Perf01/verify_long.py" \
  --group "$PERF_GROUP" --output "$PERF_RESTORED" \
  --receipt "$PERF_ROOT/perf01-readback/before-codec-001-verification.json"
```

Use the same verifier source hash for original and readback checks. Its new
receipt timestamps/absolute root can differ; compare acceptance, duration
credit, identities, counters and consumed-file hashes. Relocation support is
already part of the common verifier, including DB application receipt mapping.
This check recomputes consistency from original numeric records; it does not
replay network, database, codec correctness or a 30-minute workload.

Incomplete interrupted cells remain preserved locally with their partial
ledgers and failure record. This fixed finalized-cell packer intentionally does
not manufacture missing receipts, closed-owner proof or final summaries; an
interruption requires a separate explicit partial-evidence inventory, retaining
its ineligible status. No interruption receives 30-minute credit.

## Source review disposition

The independent protocol reviewer checked the current controller/adapter
writers, common verifier input set and small existing adapter metadata. The
HTTP/gRPC allowlist, route-specific resource names, omission of private inputs
and compatibility of known public fields passed source review. That review did
not run the packer, compress or restore data, or execute workload/tests.

The independent database reviewer checked the actual DB target, application
and sampler writers, common verifier relocation rules, private-input exclusions,
exact-byte and input-hash checks, and bounded gzip/path/symlink/restore guards
at source checkpoint `d70e9a49185ebddc899939892defc3d1020e63b2`. The review found
no source blocker and requested the additional DB relocation and URI-rejection
fixtures above. A follow-up independent source check passed those three new
fixtures, including the relocated selected-file set and zero-port rejection.
The finite execution gate is still pending; neither source review read large
evidence, compressed data or executed tests/workloads.
