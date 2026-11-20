# Perf-01 compiler/cache cleanup 006: actual checklist

Root executed the fixed cleanup on **2026-11-20, 14:07:34.296243–14:07:51.458655 UTC**.
The fresh attempt completed in **17.162547964 seconds** with the exclusive global
timing lock on CPU 8. It removed only the exact reproducible cache members and
Native AOT compiler objects in the reviewed allowlist. No functional, performance,
capacity or long-test acceptance is granted.

| Selected kind | Files | Apparent bytes | Recorded allocated bytes |
| --- | ---: | ---: | ---: |
| Archive-backed non-NativeWeave NuGet members | 2,257 | 1,034,484,387 | 1,038,675,968 |
| Native AOT compiler objects | 23 | 963,208,790 | 963,313,664 |
| Total | **2,280** | **1,997,693,177** | **2,001,989,632** |

The legacy executor label `sdk-extracted-member` covers the selected non-NativeWeave
NuGet members; it does not mean all selected files belong to the .NET SDK.
The receipt records free space increasing from **5,941,751,808** to
**7,930,380,288 bytes**, an observed difference of **1,988,628,480 bytes**.
These are point-in-time filesystem observations, distinct from apparent or
allocated selected-file totals. The final free-space value remained below the
10 GiB PostgreSQL long-test preflight and does not promise headroom after builds.

## Verified scope and preserved inputs

The exact union came from two completed metadata censuses. Its immutable selection
contains 2,257 archive-backed members and 23 AOT `.o` files. The protection set
retains **160 package archives, 135 manifest/source records, 2,684 actual-artifact
hashes and 3,317 absolute references**. Actual tested executables, native libraries,
source and proof inputs, package archives, raw measurements, logs and database data
remain outside the deletion scope. The earlier preparation failure, which exposed
a missing SQLite probe protection pin, remains recorded; the executed selection
includes the corrected shared-probe input/output and project pins.

For every selected archive member, the executor compared all decoded bytes with
the current extracted file, checked length and CRC, and computed the original
SHA-256. It hashed each AOT object and bound its index to the actual successful
publish provenance and retained actual outputs. The historical 003 control's
successful publish and subsequent failed B18 execution remain distinct; cleanup
does not change that failed result.

The actual journal has **2,280 verified unlink intents and 2,280 matching completed
unlinks**, with one attempt-start and one completed attempt-end. Every intent
precedes its own unlink, identifies an exact selected file and records the same
file hash as the completion. All 2,257 archive-member intents name unique durable
restore records and exact retained-archive hashes. There were no resumed files or
reconciled absences. Protected inputs and all retained archives passed the
executor's before/after hash checks before its completed state was written.

## Actual checks and projection method

Root passed all **ten new temporary-file safety checks** immediately before the
cleanup, from 14:07:23.164225 to 14:07:23.328366 UTC. Their receipt elapsed time is
0.164146654 seconds; the test log reports ten tests in 0.031 seconds. These checks
cover the changed AOT and explicit member-restoration boundaries. Earlier 004/005
checks remain historical and are not substituted for these ten checks.

This independent public projection reads bounded metadata only: the completed
result, exact selection, archive-hash list, AOT provenance, small source/check
receipts and the 3,992,303-byte per-file journal. It reconciles all selected-file
counts, bytes, intent/completion ordering, restore-proof references and hashes.
It does **not** reread selected payloads, repeat package/binary hashes, rescan
selected paths, restore files or rerun any check or cleanup operation. The actual
executor's verification and this metadata reconciliation are recorded separately.

## Retrieval and reproducibility

[public-summary.json](public-summary.json) contains numeric counts, booleans and
verified receipt hashes; [manifest.json](manifest.json) binds the two public files.

| Retained evidence | SHA-256 |
| --- | --- |
| Actual completed result | `b55fd9d846af7e976f22968a0223120acc24aef3d1228ad9f7fadad3781dd251` |
| Fixed selection | `8abd0f519c59e0ac8f7379cc41bbafa3fb6465d3c8b5d3eafe599b6e706077cb` |
| Actual journal | `cd35faeb8c0af2324a3863fb13bfe088c6db229d5fbb62a8e837a5b8e3cc43b4` |
| Retained archive-hash list | `2f53dfdace97fa49730f5b79d54ebadb160bef95a3dae12719dbeb8085381155` |
| AOT producer provenance | `9b7ee11bfc04017869553993d369ab1883820bd7188755c3d960da1ccec6bbc3` |
| Executed cleanup source | `13a4a63796d3bf05cc59c21612c42bb130e5ebf5aead959cae36de9a9f5b2a87` |
| Actual ten-check receipt | `87032124db515dcb6bb4e0787fcc379186c7ed66f70fbc033de0e6e70fb7f4dd` |

Private selection, provenance, journal, per-member restore proofs and complete
execution records remain under compiler-cache-cleanup-006 in the measurement
workspace. Before reusing a cleaned cache, use the exact explicit member restore
command recorded in its original verified intent. The helper verifies the retained
archive and complete decoded bytes, refuses overwrite, and restores bytes and
ordinary mode. NuGet cache markers alone are not a restoration guarantee.

The 23 compiler objects can be rebuilt from their recorded project/consumer inputs,
locked tools/dependencies and publish options in fresh isolated outputs, after any
required cache restoration. Byte-identical AOT-object reproduction is not claimed.
Actual tested binaries remained protected and need no reconstruction for their
existing evidence. No restoration or rebuild was executed by this checklist.

The public synthetic checklist remains in Git while repository history is
retained. Private workspace records have no promised remote retention period;
no remote raw archive is claimed.
