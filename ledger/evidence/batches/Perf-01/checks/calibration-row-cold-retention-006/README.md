# Perf-01 historical calibration row retention 006: actual checklist

The reviewed storage operation completed on **2026-11-20, 12:10:49.195122–12:11:34.737953 UTC**, under the exclusive measurement lock on CPU8. It preserved **283 historical calibration row files, 2,599,219,116 original bytes**, as **334,650,699 gzip bytes**, then removed only the verified originals. It grants zero performance, comparison or long-duration credit.

| Historical group | Files | Original bytes | Gzip bytes |
| --- | ---: | ---: | ---: |
| before-codec | 26 | 223,871,520 | 32,940,527 |
| before-codec-final004 | 20 | 164,838,708 | 24,009,277 |
| before-codec-v2 | 50 | 499,065,179 | 73,315,341 |
| before-codec-v3 | 36 | 347,730,399 | 50,616,835 |
| before-grpc-v4 | 26 | 70,191,623 | 7,796,188 |
| before-grpc-v5r1 | 23 | 54,723,627 | 5,612,221 |
| before-http-v3r1 | 57 | 760,241,760 | 85,591,551 |
| before-http-v5r1 | 45 | 478,556,300 | 54,768,759 |
| Total | 283 | 2,599,219,116 | 334,650,699 |

The logical payload reduction is **2,264,568,417 bytes**. Actual free space changed from **8,395,300,864** to **10,659,487,744 bytes**. These are storage observations, not codec benchmark results or a guarantee of space after subsequent builds.

## Fixed scope and preserved outcomes

The selection covered 109 already closed historical HTTP, gRPC and codec calibration cells, including previously invalid cells with their original failure/status records intact. It excluded the two unfinished codec cells and all accepted before-long/current outputs. The 343 control files, plans, summaries, source identities, certificates, logs, databases, packages and actual executables remain unchanged. None of the calibration or later acceptance outcomes was promoted by this operation.

For each file the existing engine checked regular single-link identity, wrote and fsynced a fresh gzip member, fully hashed the compressed bytes and decoded contents, reread and hashed the original, revalidated the bound controls, and wrote a durable verified record before unlink. The final manifest records every original path, original filesystem metadata, byte count, original SHA-256, compressed filename/hash and verification/removal times. Partial bundles are never automatically resumed.

Five source/temporary-file checks passed before the operation. A separate metadata review confirmed all 283 original paths absent, all 283 gzip members present at their recorded sizes, and all 343 controls unchanged in hash and identity. That review did not repeat the executor's full payload hashes or materialize a second restore.

## Retrieval and restoration

[public-summary.json](public-summary.json) records exact results and hashes; [manifest.json](manifest.json) binds this checklist. The actual storage manifest SHA-256 is `943afb37034261bc9e38b1ee3084192c45cae0773e976a063dd8929d08489fd1`. The immutable selection SHA-256 is `07518a64fa9e5b7604cc8517eb79ed3a563e64b5e48f385ec50694037400dffc` and helper SHA-256 is `593035348d6231d299dababf2f9a2cdb9f806f395e6805c15b5004f3dcf90462`.

The original compressed payloads and path-by-path restore map remain in the measurement workspace under the calibration-row-cold-retention-006 bundle. Its generated `RESTORE.txt` and the fixed helper restore command require the actual final manifest hash above and a fresh directory under the workspace's restore area. Restoration verifies compressed, decoded and materialized bytes. Original paths and filesystem metadata are recorded; restoration creates new files and does not reproduce inode numbers. Restoring in place would be a separate reviewed action.

The public synthetic checklist remains in Git while repository history is retained. The local compressed bundle has no promised remote retention period, and no remote raw archive is claimed. Original failed/interrupted records remain available.
