# Exact before protocol long commands

Status: **planned, not executed**. The companion
[`protocol-before-long-commands.json`](protocol-before-long-commands.json)
contains six explicit argument arrays: prepare, measure and post-run verify for
HTTP, then the same three existing commands for gRPC. This document introduces
no controller or supervision implementation. Root must commit the complete
freeze and own the serial measurement resources before executing either group.

## Actual selections and planned counts

The completed v5r1 before selections fix HTTP at **500 logical checks/s** and
gRPC at **128 logical checks/s**, both with 64 client workers. These same rates
must be used for paired after long runs. The selection/controller copies and
their exact hashes are in `checks/protocol-http-v5r1-selection/` and
`checks/protocol-grpc-v5r1-selection/`.

| Group | Rate (/s) | Period (ns) | Duration argument | Planned measurement checks | First-to-last scheduled span |
| --- | ---: | ---: | ---: | ---: | ---: |
| HTTP | 500 | 2,000,000 | 1,802 s | 901,051 | 1,802.100000000 s |
| gRPC | 128 | 7,812,500 | 1,802 s | 230,670 | 1,802.101562500 s |

These are prospective source arithmetic, not observed operations. The unchanged
protocol preparation formula includes its existing 100 ms dispatch-lag guard:

```text
period_ns = round(1e9 / rate)
requests = ceil((1802 * 1e9 + 100000000) / period_ns) + 1
```

Counts include the frozen expected cancellation/deadline probes. Ordinary
business calls and their bytes/messages remain separate in the result. Both
profiles retain **24 warmup checks, 32 same-process recovery checks spaced by
0.25 seconds, and 60 seconds idle**. These phases do not earn measurement
duration credit. The idle and recovery settings come from the original mixed
profiles; they are not extra CLI flags.

HTTP uses `tests/Perf01.Protocols/profile-v1.json`, SHA-256
`b523306d177fe23a9c32025fdb97fa8efb422a182320a64d8f037905e31efa6a`.
It retains real TLS HTTP/1.1 and HTTP/2, tiny/JSON responses, completed 1 MiB
upload/download, a slow-reader path and the declared 8 MiB cancellation probe.
The canceled probe transmits only a prefix and is not reported as a completed
8 MiB transfer. Completed 8 MiB transfers were covered by the separate short
partitions whose before-only noise is now frozen.

gRPC uses `grpc-budget-profile-v2.json`, SHA-256
`fcd529ae210b57a6c3030f7521127204f665f33978ec50d848d13259a7b697af`.
It retains TLS HTTP/2, identity compression, both unary payload sizes, all three
streaming cardinalities, and exact deadline/cancellation probes. Global managed
and native payload caps remain 64 MiB each; per-request caps remain 4 MiB for
HTTP and the prospectively selected 64 MiB for gRPC. No cap or acceptance
criterion changes are encoded in these argument arrays.

## Producer, source and lock identity

The package-based before server and unchanged common client come from
`ROOT/perf01-build/before/protocols-v2/build.json`, SHA-256
`818643898f04803f3070cb55f6bf0894dc23c1f9c21ff7d556a8e99b6b96d8c3`.
Its producer is clean main `ea5fa528035d025bd7a28698ee7c71194432236c`, Release
Native AOT, locked SDK 11.0.100 and explicit x86-64-v2. The JSON retains the
producer's server/client executable and actual Server native-library hashes.
It uses the explicit Python 3.12.14 executable from the frozen policy; source
`ROOT/perf01-toolchain/env.sh` before executing the arrays.

The timing driver remains the root checkout's unchanged protocol/A21/common
sources. Their exact content hashes were checked against the completed noise
index. The separate post-run verifier remains SHA-256
`3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82`.
This preparation hashed source and small metadata only. It did not rescan
binaries, packages, TLS bytes or raw operation ledgers. Existing prepare/run
checks all frozen artifacts and actual loaded identities before timing.

Both prepare and measure arrays start on **CPUs 2,3**, with
`--generator-cpus 0,1` supplied at preparation. The adapter starts the real
server on CPUs 2,3 and moves generator roles onto CPUs 0,1 using the existing
all-thread affinity checks. The protocol `run` command itself acquires the
shared `ROOT/perf01-evidence/timing.lock` using nonblocking exclusive `flock`.
**Do not wrap it in a second outer `flock`**, which would contend with its own
driver. No lock was acquired during this document preparation.

## Fresh output directories and post-run proof

| Group | Measurement output | Separate verification receipt |
| --- | --- | --- |
| HTTP | `ROOT/perf01-evidence/long/before/http-001` | `ROOT/perf01-evidence/long/before/http-001-verification.json` |
| gRPC | `ROOT/perf01-evidence/long/before/grpc-001` | `ROOT/perf01-evidence/long/before/grpc-001-verification.json` |

`ROOT` is expanded to the actual absolute workspace path in every JSON argument.
Prepare creates a fresh output; it must not overwrite an existing or partial
cell. Run one group at a time. Record actual argv, start/end and exit code, and
verify known owned processes have stopped before using the CPU 8 verification
array or starting another load. On interruption, preserve partial evidence and
inspect/clean up the known owned process tree; do not assume successful drain.

A driver exit of zero is insufficient. Require the unchanged 500 ms arrival
p99, zero unexpected errors, 256 MiB sampled server RSS, payload caps, full
correctness, expected probe behavior, recovery and idle owner/request drain.
The separate verifier must return `accepted=true`, including the conservative
successful ordinary-operation span **D−C≥1800 seconds**, the original dispatch
span and complete accounting. Expected probes cannot provide those ordinary
duration endpoints. Scheduled guards, warmup, recovery and idle cannot supply
missing effective duration. Both groups currently have zero long-duration
credit in this planned command document.

The committed short comparison noise index is
`ROOT/perf01-evidence/protocol-short/noise-before-001/noise-index.json`, SHA-256
`af9b4a68014c231fbc8c6b3e651a310045e155d83bd06d1bd9cbf4fe3b5bed20`.
It governs only the six exact C4 short partitions; it is not a noise band for
these mixed long loads. Future comparison commands must use fresh disjoint
before/after/direct processes and that exact index pin.

After producer/package identities are deliberately left outside these runnable
before arrays. Root will bind actual after artifacts while retaining these
same profiles, counts, common client, timing sources, CPU masks and rates.

## Independent source review

The database reviewer passed the bounded source/small-metadata review of all six
argv arrays and JSON SHA-256
`5c15a741134fb1ae74cb8f70dcb30ab3c603fcde4466554bfad7e71404e50c45`.
It checked the current CLI and count formula, profile timing, actual final
selections, all 16 source/metadata/profile/index pins, CPU masks, internal lock,
producer/client binding, output paths and separate verifier. It did not execute
a command, test, build, workload or verifier, or rescan binary/TLS/raw-ledger
contents. The command JSON remains unchanged after that review.
