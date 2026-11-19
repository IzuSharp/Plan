# Perf-01 actual archive smoke 001

Root ran the existing packer and restore path on a completed preparatory codec
short cell on 2026-11-19, 10:39:12–10:39:15 UTC. This directory retains the
original small metadata/log bytes and a later read-only review. No packing,
restoration, verifier run, compression or large-ledger read was repeated for
this note.

The bundle describes 10 exact files, 23,921,929 raw bytes and 12 gzip chunks.
The chunks total 2,603,788 bytes; including the 7,956-byte manifest the bundle
is 2,611,744 bytes. The actual pack and restore commands exited zero, and
`02.log` reports all 10 files verified. The manifest includes every whole-file
and chunk hash, plus the producer's prior raw-ledger pins. Its SHA-256 is
`4e772853d523bcc9a1a2b7656c821431277bc72f832d63269bdb732c7486adf5`.

The original and relocated common-verifier receipts both reject long acceptance,
return exit code 1 and award zero seconds. They record the same three consumed
metadata hashes and the same early failure:
`ValueError: Codec exit/drain/idle observation incomplete`. This preserves a
short-cell rejection; it does not establish that all later 30-minute gates were
visited or passed. The existing successful restore receipt, rather than a new
verification run by this reviewer, supports the exact-byte roundtrip claim.

## Command receipt limitation

The verbatim `commands.json` first array entry already names the **restored**
output and receipt, although `original-verification.json` identifies the
original source cell and its 10:39:12 check. Therefore that first command array
is not a reliable exact record of the initial executed argv. It is preserved
unchanged and explicitly flagged in `review.json`. The actual original/restored
verifier receipts, their file hashes and the pack/restore logs remain primary;
no corrected or reconstructed initial execution log is supplied.

The actual source cell is
`ROOT/perf01-evidence/calibration/before-codec-v3/19-confirmation-0-336`.
The bundle and restored full files remain at
`ROOT/perf01-evidence/archive-smoke-001/{bundle,restored}`. This Plan record
retains small metadata in repository history without a task-specific expiry;
it does not publish the gzip chunks or claim a remote artifact retention term.
The allowlist continues to exclude private runtime configuration, credentials,
TLS private keys, database files, binaries and supervision registration tokens.
