# Perf-01 comparison-postgresql-cold-retention-007: actual storage checklist

The reviewed storage operation completed successfully for **historical final001 comparison**, from **2026-11-20T12:46:03.041513+00:00** to **2026-11-20T12:48:34.031874+00:00**, under the exclusive measurement lock on CPU8. It preserved the original bytes and restore mapping, then removed only the verified originals. This operation grants zero performance, comparison or long-duration credit.

| Actual quantity | Result |
| --- | ---: |
| Historical stopped clusters | 24 |
| Removed ordinary single-link files | 664 |
| Original bytes | 964,894,720 |
| Gzip bytes | 212,978,449 |
| Logical payload reduction, bytes | 751,916,271 |
| Actual free bytes before | 995,295,232 |
| Actual free bytes after | 1,745,084,416 |
| Bound control entries | 225 |

The scope was fixed before execution: numbered PostgreSQL relation/segment/FSM/VM files and exact WAL names at least 256 KiB, within the selected stopped historical clusters. The unchanged gates required their exact successful stop receipts, absent PID files, no live PostgreSQL process, original completed stage/cell bindings and unchanged control hashes/identities. Current outputs, accepted before-long inputs, SQLite data, configuration, keys, logs and all measurement outcomes were excluded.

The existing engine checked regular single-link identity, wrote and fsynced a fresh gzip member, fully hashed compressed and decoded bytes, reread and hashed the original, revalidated the controls and wrote a durable verified record before unlink. Every manifest row records original path/stat/size/hash, gzip name/size/hash and verification/removal times. The original valid, invalid or interrupted outcomes remain unchanged.

Six bounded source/temporary-metadata checks passed before these three operations; the actual shared receipt is `4a2ec4a6722c5b308b92b7f5303b9bba153571bcd5e6732bc08cef1c3860731b` (0.217392584 seconds). The public projection re-read this final manifest and reconciled every row's state, totals, path uniqueness, source and selection bindings. It did not repeat any payload hashes, scan current archive/original paths, materialize a restore, run PostgreSQL or execute new checks.

## Retrieval and restoration

[public-summary.json](public-summary.json) contains the exact numerical result. [manifest.json](manifest.json) binds this public checklist. The actual archive manifest SHA-256 is `31ca8d5d1506350077c872fdbdd7b6c65905d782048b50cb12877778c710bf56`; helper SHA-256 is `dfb5ce57f2f069fd64c55680635b75b2a91598d319cd6459e1532f1f10eca533` and fixed selection SHA-256 is `41cf897541f49f7b46ddf2de873e1aba4d0c194499f2af0ecf7730513c83d74a`.

The compressed originals and complete path-by-path restore map remain in the measurement workspace under the `comparison-postgresql-cold-retention-007` bundle. Use its generated `RESTORE.txt` with this exact final manifest hash and a fresh destination under the workspace restore area. The fixed helper verifies compressed, decoded and materialized bytes. It never overwrites surviving cluster files, and it does not recreate original inode numbers or automatically restore original ownership/modes. Any cluster reassembly must include all applicable prior manifests, restore every missing member with its original hash and required owner/mode, and preserve surviving controls before PostgreSQL is started.

The synthetic public checklist remains in Git while repository history is retained. The local compressed bundle has no promised remote retention period. No remote raw archive, whole-cluster snapshot, restore execution or additional measurement acceptance is claimed. Free-space changes are storage observations and do not guarantee later build or PostgreSQL preflight headroom.
