# Perf-01 calibration-postgresql-cold-retention-009: actual storage checklist

The reviewed storage operation completed successfully for **historical before-calibration**, from **2026-11-20T12:51:16.863116+00:00** to **2026-11-20T13:01:13.776216+00:00**, under the exclusive measurement lock on CPU8. It preserved the original bytes and restore mapping, then removed only the verified originals. This operation grants zero performance, comparison or long-duration credit.

| Actual quantity | Result |
| --- | ---: |
| Historical stopped clusters | 79 |
| Removed ordinary single-link files | 2,031 |
| Original bytes | 971,964,416 |
| Gzip bytes | 252,866,865 |
| Logical payload reduction, bytes | 719,097,551 |
| Actual free bytes before | 2,494,746,624 |
| Actual free bytes after | 3,206,930,432 |
| Bound control entries | 484 |

The scope was fixed before execution: numbered PostgreSQL relation/segment/FSM/VM files and exact WAL names at least 256 KiB, within the selected stopped historical clusters. The unchanged gates required their exact successful stop receipts, absent PID files, no live PostgreSQL process, original completed stage/cell bindings and unchanged control hashes/identities. Current outputs, accepted before-long inputs, SQLite data, configuration, keys, logs and all measurement outcomes were excluded.

The existing engine checked regular single-link identity, wrote and fsynced a fresh gzip member, fully hashed compressed and decoded bytes, reread and hashed the original, revalidated the controls and wrote a durable verified record before unlink. Every manifest row records original path/stat/size/hash, gzip name/size/hash and verification/removal times. The original valid, invalid or interrupted outcomes remain unchanged.

Six bounded source/temporary-metadata checks passed before these three operations; the actual shared receipt is `4a2ec4a6722c5b308b92b7f5303b9bba153571bcd5e6732bc08cef1c3860731b` (0.217392584 seconds). The public projection re-read this final manifest and reconciled every row's state, totals, path uniqueness, source and selection bindings. It did not repeat any payload hashes, scan current archive/original paths, materialize a restore, run PostgreSQL or execute new checks.

The same 79 calibration clusters already have 245 different larger members in `calibration-postgresql-cold-retention-003` (manifest SHA-256 `44699ccb0fcca6107e6dd7fdd88db7252a1f373bcf4c40e47a0085768f940b4c`). Full cluster reassembly needs both bundles and the surviving files. The original 12 invalid calibration cells remain invalid.

## Retrieval and restoration

[public-summary.json](public-summary.json) contains the exact numerical result. [manifest.json](manifest.json) binds this public checklist. The actual archive manifest SHA-256 is `9968fdb4184d585a056d349c151b23f948911d79ef5519aa3e404c931b068c62`; helper SHA-256 is `dd885851608a45a62935928cefc747235a472761067383dc9a5dfccea18980d5` and fixed selection SHA-256 is `6cfa591c2fa5445e61e4f22684eba63441e9fd6d152be881c584c0da5f0dcff5`.

The compressed originals and complete path-by-path restore map remain in the measurement workspace under the `calibration-postgresql-cold-retention-009` bundle. Use its generated `RESTORE.txt` with this exact final manifest hash and a fresh destination under the workspace restore area. The fixed helper verifies compressed, decoded and materialized bytes. It never overwrites surviving cluster files, and it does not recreate original inode numbers or automatically restore original ownership/modes. Any cluster reassembly must include all applicable prior manifests, restore every missing member with its original hash and required owner/mode, and preserve surviving controls before PostgreSQL is started.

The synthetic public checklist remains in Git while repository history is retained. The local compressed bundle has no promised remote retention period. No remote raw archive, whole-cluster snapshot, restore execution or additional measurement acceptance is claimed. Free-space changes are storage observations and do not guarantee later build or PostgreSQL preflight headroom.
