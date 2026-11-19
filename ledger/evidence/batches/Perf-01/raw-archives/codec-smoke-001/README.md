# Codec archive transport smoke

This is the exact previously verified synthetic-data archive smoke, not a final
Perf-01 before/after measurement. Both original and restored common-verifier
receipts rejected it because its idle observation was only five seconds.
It has **zero long-duration credit**. The manifest preserves the original
producer, input hashes, exact source bytes and that rejected verdict.

The independent gzip shards contain only the packager allowlisted synthetic
operation/event samples, resource series and JSON receipts. Private keys, local
credentials, database files and product binaries are excluded.

Use the committed Perf-01 pack_evidence.py verify/restore commands with this
directory as --bundle. Remote transfer and readback are recorded separately
after actual completion. Committed evidence has no automatic expiry and remains
available while the repository and its reachable history retain it.
