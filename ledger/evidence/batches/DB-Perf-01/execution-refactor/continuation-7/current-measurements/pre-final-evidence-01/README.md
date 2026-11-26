# Pre-final original evidence retained

This archive retains the completed 17da short/diagnostic/calibration/offered
measurements, the rejected 92b9230 paired experiment, the completed 120-second
before/candidate baseline supplement, and the exact pre-final frozen input
union. **It contains zero executed final 1800-second segments and grants zero
final acceptance credit.** Later final observations need a separate archive
and the existing arithmetic/identity acceptance gates.

The retention operation completed successfully on 2026-11-26. Its receipt
records `08:23:00.264726` through `08:23:02.884902` UTC, with exit code 0 in
[command.json](command.json). No workload or product process was launched, and
no original input was modified or deleted by this operation.

| Retained object | Identity or count |
| --- | --- |
| [evidence.tar.gz](evidence.tar.gz) | 5,992,490 bytes; SHA-256 `544bcb1e77fd48fd04c74f1f6edf800431ca4ffac55c59b78d4b491ecc2eea5d` |
| [manifest.json](manifest.json) | SHA-256 `26f6b469978c66d838f55b7b22216a8a41bacd372301af6d396112d6beb29f81` |
| Archived original files | 1,391 files, 49,734,968 original bytes |
| Explicitly recorded exclusions | 66 files, 369,364,053 original bytes |
| Merged pinned input inventory | 1,225 entries; document SHA-256 `6d76ab9cd3dc4f0816af6b41259b9aced8166a224b7faa7adf5cf02c327c7284` |
| Archive tool | SHA-256 `0e3d18c4c67072c119cba0477fc2ead22f60ab6c0c722a40dbee1960f195be3b` |
| Verification | All archive members and gzip stream read back; every original rehashed; original identities and root file inventory unchanged |

The original inventory document is
`/workspace/scratch/fd78534029f7/measurements/pre-final-evidence-inputs-01.json`,
using its `/inputFiles` object. It combines the actual frozen/source identities
and the supplied short/baseline/diagnostic analysis inputs. The complete command
with every source and exclusion path is retained in `command.json`; the actual
archive result is [receipt.json](receipt.json). Both the input inventory and the
archive manifest itself are included in the tar file.

## What is preserved and excluded

Every original file under the current measurement root, together with the pinned
input union, was enumerated. Included raw JSON, JSONL, stdout, logs, plans,
receipts, manifests, source and generated source retain their original bytes.
The manifest records each original path, byte length, SHA-256, provenance and
either its archive member or its explicit exclusion reason. The archive's
`measurements/` and `original-inputs/` prefixes preserve this mapping without
embedding absolute extraction paths.

All nine existing `measurements/retained-databases/*.tar.gz` files were explicitly
excluded as database bytes, including five earlier retained databases and the
four newly retained stopped fixtures. Their manifests and retention receipts
remain included. SQLite databases/sidecars, package files and compiled binaries
were also excluded by the documented classifications. Every excluded object
was actually hashed twice and retains its original location and hash. These
exclusions mean this archive is not a ready-to-run binary or database bundle;
it does not claim that a later rebuild reproduces the excluded bytes.

The separate stopped-database operation had already retained and verified its
four exact fixtures before this archive began. This tool did not repeat that
compression or delete any database. Compression and hashing were serial with
the parent task's measurements and stopped-database retention work.

## Preserved preflight failure

Before the actual retention tool ran, the invocation wrapper incorrectly
expected exactly four database archives. A metadata-only enumeration found nine,
so that assertion stopped before reading measurement contents or creating the
archive output directory. The original observation is retained in
[pre-final-archive-preflight-failure-01.json](../tools/pre-final-archive-preflight-failure-01.json).
The corrected invocation explicitly excluded all nine actual archive paths,
as requested. No failed archive output was overwritten; this directory was
still absent when the successful tool execution created it.

## Reproduction and later evidence

The retention script, scope, exclusion rules and 20 finite synthetic controls
are described in [measurement-archive.md](../tools/measurement-archive.md).
Reproducing the operation requires its actual original paths and a new output
directory. A changed source, missing original, altered pinned input or changing
measurement tree fails the operation and preserves a separate failure record.

The archive preserves provenance and analysis inputs; correctness and measured
performance remain bound to their corresponding source, packages, processes
and original reports. 92b9230 remains performance-rejected, 17da remains the
formal candidate, historical short observations remain short observations,
and the 120-second supplement does not count as a 30-minute segment.
