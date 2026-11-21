# Epoch-002 measurement caller

Status: **new source, unexecuted**. No module import, build, workload or timed
test was performed while preparing this change. The accepted build/B18
`run.py` and `sources.json` (`268d10b6…`) remain unchanged. This caller has a
separate `measurement-sources.json` and separate actual execution receipts.
Current epoch-002 long credit remains **0/10**.

## Baseline can proceed before final construction

Populate one local `measurement-inputs.example.json` copy from the **actual
completed build attempt**. There is no hardcoded attempt-001 dependency.
It binds before/common producer receipts, functional-before, the exact build
input/source index, full toolchain/Python identities inherited from those
inputs, and one fresh shared TLS pair. Keep that admission immutable.

Before noise, before capacity and all five before longs can execute without
an after build. Comparison and every after stage require a separate populated
`final-binding.example.json`: full selected clean commit, actual after build
and functional-after, tied to the unchanged baseline admission SHA. Admission
then revalidates actual c752 producer receipts and their bound file hashes,
selected role identities and original external package equality. Baseline
evidence is not relabelled when the final descriptor arrives.

All new commands run only through the existing c752 finite owner. The caller
takes the build input's exclusive lock **before** full artifact admission; this
is its outer orchestration reservation. Original protocol children receive a
different `protocol_timing_lock`, avoiding recursive lock acquisition. The
root is the sole executor; no concurrent profile, build or other load belongs
inside these reservations. Main owners run on CPU8, service/database children
on CPUs2,3, and original drivers move the generator/client to CPUs0,1.

Use the original TLS creation mechanism once, outside timing, then bind the
actual certificate/key hashes in the admission:

```sh
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout "$KEY" -out "$CERTIFICATE" -days 7 -subj /CN=localhost \
  -addext 'subjectAltName=DNS:localhost,IP:127.0.0.1'
chmod 600 "$KEY"
```

No certificate or key identity is claimed recovered from the lost epoch.
Private key bytes and full operational maps stay local.

## Exact workload and CLI mapping

Every call starts with:

```sh
taskset -c 8 "$PYTHON" "$CALLER/measure.py" --root "$ROOT" \
  --admission "$ADMISSION" --admission-sha256 "$ADMISSION_SHA" \
  --source-index-sha256 "$MEASUREMENT_SOURCE_INDEX_SHA" \
  --stage STAGE --group GROUP --label FRESH_LABEL
```

| Stage | Additional selection | Actual original execution/reading |
|---|---|---|
| `noise` | DB `--scene c16`; HTTP/gRPC one of six scene IDs; codec `--scene w1` or `w2` | Three fresh before processes. Original domain driver; original protocol `freeze-noise`, codec `freeze`, or DB anchor `triplet_gate` and exact original max(1000 ns, process-mean range) band formula |
| `compare` | Same scene; add final-binding and noise-publication descriptors | Original frozen route order. DB c16 has three processes per four routes; c1/c4/c8 each have one descriptive process per route. Protocol has three per three routes; codec has three per four routes, with original managed-comparator scope |
| `capacity` | `--role before`, `after` or `direct`; after/direct require noise publication; after requires final binding | Original protocol/codec calibrator CLI. DB calls original command/observer policy plus the unchanged ladder/refinement/three-confirmation/step-down algorithm under new role admission |
| `long` | `--role before` or `after`; matching capacity proof and noise publication; after requires final binding | Original domain driver and original `tests/Perf01/verify_long.py`; one group per invocation |

Descriptor flags are `--final-binding PATH --final-binding-sha256 SHA`,
`--noise-publication PATH --noise-publication-sha256 SHA`, and
`--capacity-proof PATH --capacity-proof-sha256 SHA`. The capacity proof is the
actual completed outer capacity `execution.json` for that role/group/context.

The workload-only source is
`reproduction/workloads-001/workloads.json`, SHA-256
`30af3a81ca377436cdedcae33a074b91df510256d403ba9fca11763186da44cf`.
Its historical final-product labels do not select the new runtime; actual
runtime identity comes solely from the fresh role bindings.

- Database: PG/SQLite separately; c16 at 180/s and 50/s for 60 seconds;
  descriptive c1=5/s×60s, c4=20/s×20s, c8=40/s×20s. Together the comparison
  queue has 48 processes. Mixed durable cycle/page, deferred GC and threaded
  sampling are retained. Explicit business retries remain zero.
- Protocol: `http1-small`, `http2-small`, `http1-large`, `http2-large`,
  `grpc-unary`, `grpc-streams`: original six profiles, 54 comparison processes,
  actual TLS sockets and common before client. gRPC stays identity-only.
- Codec: W1=134/s×120s with one worker; W2=241/s×67s with two workers.
  Original eight cases and 32 case/action/interface partitions; 18 primary
  comparison processes plus six managed observations. Original fixed format,
  level, checksum, limits, seeds, per-row minimums and managed scope remain.
- Long: PG144, SQLite40, HTTP500, gRPC115, codec192 per second; each requested
  duration is 1802 seconds plus separate warmup/recovery/idle. The original
  ordinary-success **D−C ≥ 1800 seconds** and actual dispatch-span checks alone
  establish duration credit. Neither schedule length nor a capacity proposal
  supplies accepted seconds.

Protocol/codec calibrators retain their original descriptive `long_rate`
proposal field. The caller records and ignores it. Long admission uses the
unchanged five frozen rates and requires the role's last three actual
60-second confirmations at a passing capacity at least that rate.

## Source and schema differences made explicit

`database_observer_calibrate.py` originally admits unavailable old parent
documents and conflates common application source with runtime package source.
`database_capacity.py` replaces that admission with actual c752 proofs, keeps
the original `command`, observer/GC descriptors and capacity algorithm, and
checks original raw results. PostgreSQL's recorded settings must be exactly
`18.0|on|on|on`, the actual bound binaries must match, and original `pg_ctl`
shutdown must succeed. The outer owner already covers pre-yield startup failure.

`readers/database_compare.py` is an exact original copy with one changed
eligibility condition: raw native `serverState` is **`Disposed`**, while direct
Rust and managed comparators emit **`Stopped`**. `NativeDisposed` is not a raw
state in the fixed source. All existing exit, durability, zero/resource-release
and observer checks remain; actual fresh CLOSED rows must match their route.
The native-only long runs use the original unmodified long verifier.
For HTTP/gRPC long results, identity and retirement metadata are read using
that verifier's existing streaming parser. The short comparison reader is not
used on long sparse histograms, which may exceed its 64 MiB file bound. The
unchanged original long verifier still checks all request rows, effective
duration, correctness, service limits and resource release before any credit.

Actual loaded DB files must match that role's observer artifact map, including
its selected provider and Server native hashes. Protocol loaded maps must
match that role's native manifest; codec must load its selected A17 native
asset. No union of before/after artifact maps can satisfy these role checks.

## Fresh noise publication/readback gate

Each completed noise invocation writes its original noise receipt plus a
numeric-only `numeric-noise-projection.json`. Root combines the ten scene
projections into a public document with `epoch`, `admission_sha256` and a
`noise` mapping keyed by:

```text
postgresql-c16, sqlite-c16, http1-small, http2-small,
http1-large, http2-large, grpc-unary, grpc-streams, codec-w1, codec-w2
```

Each value is the exact per-stage numeric projection: scene, noise SHA, bands,
and the three before-process result hashes. Publish this project-only document
in Plan and read back its exact bytes. The local gate descriptor has:

```json
{
  "epoch": "recovery-002",
  "admission_sha256": "ACTUAL_BASE_ADMISSION_SHA",
  "projection": {"path": "LOCAL_ROOT_RELATIVE_PROJECTION", "sha256": "ACTUAL_SHA"},
  "readback": {"path": "LOCAL_ROOT_RELATIVE_RETURNED_BYTES", "sha256": "ACTUAL_SHA"},
  "retrieval_receipt": {"path": "LOCAL_ROOT_RELATIVE_ACTUAL_RETRIEVAL_RECEIPT", "sha256": "ACTUAL_SHA"},
  "publication": {"repository": "IzuSharp/Plan", "commit": "ACTUAL_COMMIT", "path": "ledger/evidence/batches/Perf-01/ACTUAL_PATH", "blob_oid": "ACTUAL_BLOB"},
  "noise": {
    "SCENE": {
      "execution": {"path": "ACTUAL_ROOT_RELATIVE_NOISE_EXECUTION", "sha256": "ACTUAL_SHA"},
      "receipt": {"path": "ACTUAL_ROOT_RELATIVE_ORIGINAL_NOISE_JSON", "sha256": "ACTUAL_SHA"}
    }
  }
}
```

The actual retrieval receipt records `status: "retrieved"`, repository, commit,
path, blob OID, content `sha256`, `retrieved_utc` and `url` from the real retrieval.
The caller compares every published band to its original before-only receipt,
verifies completed owned execution/log hashes, matches saved readback bytes,
and checks the exact Git commit/path/blob. **Local Git inspection alone is not
remote readback.** The caller never publishes or invents a retrieval result.

All failed or interrupted stage directories and child receipts remain intact.
There is no automatic replacement of failed short cohorts or long groups.
Original finite capacity step-down is retained as its declared algorithm.
Only completed independent groups may be reused with the same actual binaries,
case, configuration, context and source index. Profiling remains a separate
later caller and grants no formal timing credit.
