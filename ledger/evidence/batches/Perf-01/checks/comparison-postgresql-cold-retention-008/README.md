# Perf-01 comparison-postgresql-cold-retention-008: actual storage checklist

The reviewed storage operation completed successfully for **historical final002 comparison**, from **2026-11-20T12:48:45.548928+00:00** to **2026-11-20T12:51:04.644492+00:00**, under the exclusive measurement lock on CPU8. It preserved the original bytes and restore mapping, then removed only the verified originals. This operation grants zero performance, comparison or long-duration credit.

| Actual quantity | Result |
| --- | ---: |
| Historical stopped clusters | 24 |
| Removed ordinary single-link files | 664 |
| Original bytes | 964,960,256 |
| Gzip bytes | 212,929,826 |
| Logical payload reduction, bytes | 752,030,430 |
| Actual free bytes before | 1,745,076,224 |
| Actual free bytes after | 2,494,754,816 |
| Bound control entries | 224 |

The scope was fixed before execution: numbered PostgreSQL relation/segment/FSM/VM files and exact WAL names at least 256 KiB, within the selected stopped historical clusters. The unchanged gates required their exact successful stop receipts, absent PID files, no live PostgreSQL process, original completed stage/cell bindings and unchanged control hashes/identities. Current outputs, accepted before-long inputs, SQLite data, configuration, keys, logs and all measurement outcomes were excluded.

The existing engine checked regular single-link identity, wrote and fsynced a fresh gzip member, fully hashed compressed and decoded bytes, reread and hashed the original, revalidated the controls and wrote a durable verified record before unlink. Every manifest row records original path/stat/size/hash, gzip name/size/hash and verification/removal times. The original valid, invalid or interrupted outcomes remain unchanged.

Six bounded source/temporary-metadata checks passed before these three operations; the actual shared receipt is `4a2ec4a6722c5b308b92b7f5303b9bba153571bcd5e6732bc08cef1c3860731b` (0.217392584 seconds). The public projection re-read this final manifest and reconciled every row's state, totals, path uniqueness, source and selection bindings. It did not repeat any payload hashes, scan current archive/original paths, materialize a restore, run PostgreSQL or execute new checks.

## Retrieval and restoration

[public-summary.json](public-summary.json) contains the exact numerical result. [manifest.json](manifest.json) binds this public checklist. The actual archive manifest SHA-256 is `49c892757f05ab50f95257643fea9b01d5ff41f67cc401b4e19585d98ed54caa`; helper SHA-256 is `8b5a1402ab031b7d8b147572b15342881a8523dd1d4b7c8cc8a78275c1aeda3f` and fixed selection SHA-256 is `8bb58e11bafa74f81ccda916903c6c9842e4b03eb5264279e69fe2a97e937e16`.

The compressed originals and complete path-by-path restore map remain in the measurement workspace under the `comparison-postgresql-cold-retention-008` bundle. Use its generated `RESTORE.txt` with this exact final manifest hash and a fresh destination under the workspace restore area. The fixed helper verifies compressed, decoded and materialized bytes. It never overwrites surviving cluster files, and it does not recreate original inode numbers or automatically restore original ownership/modes. Any cluster reassembly must include all applicable prior manifests, restore every missing member with its original hash and required owner/mode, and preserve surviving controls before PostgreSQL is started.

The synthetic public checklist remains in Git while repository history is retained. The local compressed bundle has no promised remote retention period. No remote raw archive, whole-cluster snapshot, restore execution or additional measurement acceptance is claimed. Free-space changes are storage observations and do not guarantee later build or PostgreSQL preflight headroom.
