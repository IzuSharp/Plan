# Direct-close development evidence archive

This archive preserves the original local development evidence for native 055ff32,
managed 0b5ea94, the Native AOT test commit 4067d76, and native provider producer
ecbf008. Later source publication is recorded separately as public bc6ba1a.
Existing source identities, embedded timestamps, command receipts and every raw
log byte are unchanged. Source parity does not relabel earlier execution as a
public-candidate run and does not grant public package or performance acceptance.

Contents: all 18 close-ready-01 text inputs plus their original manifest; the
native development receipt and its six hash-bound logs (the saved test-03-details
snapshot, never a later CTest LastTest.log); managed build and empty format logs;
publication intent/receipt; both development native manifests and their three
command logs each; and the saved impact logs/plans. Derived provenance and
product-parity records are explicitly identified as archive-time analysis.

The complete NativeHost run has an original subprocess exitCode=0 receipt. The
preceding narrower close-only run has all expected PASS summaries but no retained
direct tool exit metadata; that limitation remains explicit. The managed-library
format log is empty and has no independent original exit-code receipt; the
original implementation agent reported tool exit0, recorded as attribution only.

SOURCE-MANIFEST.json retains each original absolute path, observed original file
mtime, size and SHA256. Archive metadata uses deterministic uid/gid/mtime0 with
regular mode0644 files and sorted names. MANIFEST.sha256 covers every other tar
member, including the source manifest. The external manifest records tar SHA256,
two-generation byte reproducibility and complete readback/extraction comparison.
Original file mtimes are observations, not inferred execution times.

No executable, shared library, bin/obj, restore cache, PostgreSQL data, credentials,
or private certificates are included. The archiver performs no build, test,
benchmark, planner execution, repository modification, or Plan update.
