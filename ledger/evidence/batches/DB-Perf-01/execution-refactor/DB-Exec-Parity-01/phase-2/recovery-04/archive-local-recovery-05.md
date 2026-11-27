# Local recovery after published-archive cleanup

**Current local availability: the compressed archive parts and duplicate canonical/roundtrip files listed in the cleanup receipt have been deleted. They must be retrieved from the pinned remote Plan commits before running an archive verifier or restorer. They are not still present locally.** Original experiment raw results, ELF/debug/native outputs, generated source, nupkg, source trees and database fixtures were retained, so continuing measurements from the existing workspace does not require restoring the archives.

This note supersedes the local-availability statements in the earlier archive README and uploader resume snapshots. Those files remain unchanged as historical evidence. In particular, their old statements that incomplete capacity parts remain local, that publication is still pending, or that local parts can immediately be verified describe their creation-time state, not the post-cleanup workspace.

## Published recovery locations

The archive directories below are in `IzuSharp/Plan`, under `ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/phase-2/recovery-04/`. Readback receipt paths are relative to the original task workspace, not to that repository directory.

| Archive set | Pinned published commit | Directory and verified mapping | Root-agent readback receipt |
|---|---|---|---|
| archives-01 | `b54054bd1f3befe94e1817cc29f494bd782854b9` | `archives-01/`; original **189 mapped files**, including 153 ordered parts for 8 packages; publication also retained 3 upload-log files | `observations/recovery/archive04-published.json`: `remotePublication=true`, `blobMapReadbackMatched=true` |
| archives-02 | `27e0f35709036b0737ed101ba6472ce1461c0538` | `archives-02/`; **103 exact file/mode/Git-blob mappings**, including 56 ordered parts for 4 packages and the corrected restorer | `observations/recovery/archive02-published.json`: all blobs reachable and matching, no extra files, no truncated tree |

Archive trees are `c20cd01bd243feecc84e822054d5b9a390521215` for archives-01 and `396512ac9327ce31c3cd88b12390bc161cae475f` for archives-02. The archived package indexes, member manifests, versioned scripts and upload receipts remain available locally as metadata; local source paths recorded in those manifests are provenance, not a claim that the compressed files still exist.

## Exact cleanup and retained evidence

The authorized cleanup wrote `cleanup-published-archives-05.json` before removing any file. `cleanup-published-archives-receipt-05.json` records successful verification of every selected inode's expected SHA before the first deletion, followed by all **255 removed path names / 236 distinct inodes**. The manifest includes both names of the 19 foundation hardlinks, so released space was counted on the final unlink rather than double-counting the names.

The cleanup finished at `2026-11-27T08:22:16.864520+00:00`, released **1,202,978,816 allocated bytes** by final unlink, and recorded **2,041,270,272 free bytes** immediately afterwards. These are historical receipt values; later measurement writes change free space. `df-after-published-archive-cleanup-05.txt` preserves the corresponding filesystem observation.

Only the listed published parts, reconstructable compressed canonical/roundtrip copies and incomplete failed-capacity compressed duplicates were removed. All manifests, failed-attempt records, review results, publication readbacks and original artifacts were retained. The failed capacity attempt remains a failed source-freeze attempt; deleting its redundant compressed bytes does not erase or change that verdict. `local-archive-availability-05.json` is the machine-readable availability checkpoint.

## How to resume safely

1. Continue from the existing original source/raw/consumer paths when they are still present. Do not rebuild or rerun already completed experiments merely because their compressed backups were removed.
2. If archive verification or extraction is required, retrieve the archive directory, its ordered `raw-archives/*/part-*.bin` files, index, member manifests and verifier from the **pinned commit above** into a staging location with sufficient space. Use the authenticated repository connector or an existing authorized Git checkout. A blob-upload receipt alone is not the recovery location; the published commit and root-agent readback are the evidence of reachability.
3. Verify the downloaded files against their published Git-blob mapping and package hashes, then follow that archive directory's restore instructions. The corrected `archives-02/streaming_archive.py` verifies parts and members without reconstructing a full compressed file; extraction still needs space for the restored outputs. Restore archives-01 before explicitly overlaying archives-02. The historical Stage 1 dependencies identified by archives-01 remain part of full-from-scratch recovery.
4. Preserve original local-built versus connector-published source identities, failure verdicts and performance-credit boundaries. A restore is not a new measurement. Do not rewrite the absolute paths embedded in immutable raw receipts as though they described new executions.

The active `zero-cost-05` campaign and later results are outside this cleanup. Do not archive or delete a still-running campaign directory. During a measurement quiet window, perform no archive downloads, scans, hashing, compression or cleanup; wait for the root agent's explicit end-of-window notification.
