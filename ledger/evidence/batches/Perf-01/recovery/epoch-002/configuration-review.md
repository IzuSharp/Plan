# Perf-01 recovery epoch 002: independent configuration review

**Verdict: ACCEPT for prospective configuration only.** This review does not
accept a build, loaded binary, correctness run, performance result or long segment.
Reviewed at `2026-11-21T01:23:39.280024+00:00`. No build, test, target import, service or workload was run.

## Exact inputs

| Input | SHA-256 |
| --- | --- |
| Epoch-002 freeze | `a1cc0cfb0d354335a90c61f64941353bba899fbc9916c716ad839cc7e6402cd5` |
| Parent epoch-001 freeze | `eda07013d5fa06f793ea9f15667cc99f4a7a4368c733bbbba75f76932319f862` |
| Original policy | `0c7cd866b1ad0fc86d647e31dd1b6fe0b148d2e7ca54d83b7286cec09f11cafc` |
| Inherited effective policy | `b70aebe88bbf271b1ea53dad2b68b8e29c9f1796b32bb0e1721ab09db3f54760` |
| Public workload bundle | `30af3a81ca377436cdedcae33a074b91df510256d403ba9fca11763186da44cf` |

Public source context is Plan `42a71aa6ea28fdee0f1d21d5c839c14ce56413aa`.
The baseline remains `ea5fa528035d025bd7a28698ee7c71194432236c`; the common driver and
retained ON source remain `2e3995df8d86583ee9443348276ca8d918056bfc` with tree
`246de1eb9368efbc62f46ce10c4a8a894d646152`. The required Design revision remains
`c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. These are source requirements, not reconstructed artifacts.

## Unchanged workload and service constraints

I compared the complete long-group and machine objects with the parent freeze,
as well as the policy, toolchain, lock, profile, driver, analysis-source and
workload-bundle identities. All are unchanged. Independently rehashed source
bytes match all **3 lock files, 11 public driver files, 9 public analysis files
and 9 profiles** named by the freeze.

| Group | Fixed rate per second | Concurrency / workers | Scheduled seconds | Planned operations |
| --- | ---: | --- | ---: | ---: |
| postgresql | 144 | 16 | 1802 | 259526 |
| sqlite | 40 | 16 | 1802 | 72091 |
| http | 500 | 64 | 1802 | 901051 |
| grpc | 115 | 64 | 1802 | 207243 |
| codec | 192 | 2 workers | 1802 | 346005 |

Every accepted segment still requires at least **1,800 seconds of actual effective
load**, excluding warmup, calibration, recovery and idle. The inherited fixed rates
remain prospective until fresh baseline qualification; the original failure and
invalid-sample rules remain in force.

The service standard remains arrival p99 at most 500 ms, application RSS at most
256 MiB, zero unexpected errors, and generator dispatch lag at most 100 ms.
Service/database CPUs remain 2 and 3; generator CPUs remain 0 and 1; bounded
source/control work uses CPU 8. Timing remains serial. The actual boot digest
read during this review matches both freezes. This does not establish equivalence
to the older physical measurement host or qualify a future workload run.

The hashed workload bundle preserves PostgreSQL 18.0 with fsync, synchronous
commit and full-page writes; SQLite WAL/FULL with IMMEDIATE transactions,
foreign keys and the 5,000 ms busy timeout; and the same database initial-state,
connection and business-operation configuration. HTTP and gRPC retain their
TLS transport profiles, connection reuse, stream limits and identity-only protocol
compression. The independent codec corpus retains its seed, sizes, action/interface/
entropy weights, zlib level 6, Adler32 and encoded/decoded limits.

## Recovery boundaries and clarified history

The updated freeze explicitly records that diagnostic instrumentation has started,
while no final runtime edit or new measurement has started. Its build, measured
binary and fresh-noise bindings are null; final runtime selection is also null.
This is an honest edited diagnostic candidate, with zero formal credit.

The old raw measurement records and producer/binary outputs are unavailable.
The retained 18 fixed-load and 28 capacity process projections and their earlier
independent review remain historical evidence; they do not recreate missing bytes
or transfer main before/final acceptance. The formerly ambiguous interruption
field now explicitly identifies pre-epoch-001 history. The inherited policy's
recovery-001 provenance labels likewise do not identify this new epoch's artifacts.

The old TLS private key is unavailable. A fresh localhost certificate/key must be
bound before new measurement and shared by the new before/final/direct cells,
using the same frozen TLS configuration. No old certificate-byte recovery is claimed.
Actual toolchain receipts, builds, package/native identities, qualification and
measurement evidence remain future work under the existing policy.

**Current credit remains 0 before groups and 0 after groups; all ten 30-minute
segments remain outstanding.** The publication statement limits any future
archives to authorized project evidence and makes no uploaded/read-back raw archive
claim. This review creates no additional test or approval requirement.
