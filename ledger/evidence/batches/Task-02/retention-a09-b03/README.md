# Task-02 retained evidence staging packet — Linux x64

This packet is staged by `/root/environment_review` for the main executor to copy into Plan. No Plan files were edited and no accepted test was rerun while preparing this packet. All retained original files preserve their exact bytes. `inventory.json` maps original absolute paths to packet-relative paths and SHA-256; `SHA256SUMS` verifies the staged copies and generated retention notes.

## Contents

- `B03/linux-final/attempt-003`: final 33-command receipt on `c1d249b0d7b5fcec0403c864c64ff0e22652461e` and every original stdout/stderr log. `attempt-001` and `attempt-002` retain superseded formal passes rather than rewriting history.
- `B03/linux-final/last-parent-review`: actual failing last-parent worker barrier, intermediate compile/regression logs, and a minimal independent test patch. `source-recovery.json` records that the recovered scenario bytes exactly match the SHA-256 in the original failing receipt. The test runner reconstruction is explicitly distinguished because the original receipt did not hash it separately.
- `B03/linux-final/acquire-timeout-review`: actual SQLx deadline panic probe, source, standalone Cargo manifest/lock and raw logs. The direct-rustc failed preparation is also retained. The manifest's historical absolute path is intentionally unchanged.
- `B03/linux-final/stream-handoff-review`: the original B06 development observation of provider row peak 3 and captured source hashes. Its HEAD is a development HEAD, not a claim that every uncommitted B06 file belonged to that commit.
- `A09/linux-review-fixed-001`, `A09/linux-review-fixed-002`: original fix-run formal receipts, every command stdout/stderr, artifact hash lists, deterministic outputs, actual parser inventories and actual raw-extractor outputs. The original A09 `attempt-001` is already retained verbatim in `Plan/ledger/evidence/A09/linux-run-001`; all 87 original text files were verified against that copy and are mapped in `inventory.json` rather than duplicated. Final accepted A09 source is `b459fdedb0a71be564a0dbb16355d0baa429d80c`; earlier passing formal runs were superseded after independent findings.
- `A09/linux-independent-review`: every unique independent review/probe input, canonical output, raw log, result and audit. `final-review.json` is the final technical decision. Earlier changes-requested reports remain unchanged.

## Filtering and path truth

Native/managed binaries, PDBs, database files, keys/certificates, caches, build trees and duplicate canonical product source are excluded. Artifact digests remain in the original receipts. The five copied A09 source snapshots are replaced by their exact Git checkpoint/path/hash entries in the exclusion list. Repeated copies of formal evidence are mapped as aliases to one retained author-run file. Repeated input/output files for separate independent probe phases remain present because each phase has its own original receipt and pathname.

Absolute paths inside original logs/receipts are historical facts. Do not rewrite those bytes to the Plan destination and thereby invalidate their hashes. Use `inventory.json` to resolve a retained file's relocated copy; the main executor can add a destination mapping or update the retention inventory when copying this directory. The `dev-jit-*` B03 directories contained only database fixtures and were excluded; no raw receipt is invented for those early development attempts.

## Reproduction without duplicating product source

Restore NativeWeave at the source commit indicated by the relevant receipt, using the repository's fixed toolchain and dependency locks. Product source remains authoritative in Git.

For A09 independent probes, build the task's ordinary test executable at the selected checkpoint, then invoke its existing `--emit <input.json> <new-output.json>` entry point using an input under `A09/linux-independent-review`. The phase result records the historical command, binary hashes, input hash and expected acceptance/rejection. Use a new output location; do not overwrite retained evidence. The original seven probes target 5c77f38, first fix/profile probes target eceff371, and final 14 probes target b459fded. The exact full commit identities are recorded in JSON.

For the B03 last-parent failure, restore e7fa398 and apply `B03/linux-final/last-parent-review/pre-fix-independent-test.patch`. The resulting scenario source must hash to `8996582ed64707b0d2b3711491727715c05c3052a7ddbee3c872172867e5c7f5`; the retained command then selects `last_parent`. For final acceptance, use the canonical committed regression in c1d249b instead of this historical patch.

For the deadline failure, restore 22e077e, copy the retained standalone probe crate into a separate reproduction directory, and rebind only its dependency path to that checkout. Preserve the original manifest as evidence. The source and lock are retained; no native binaries or database state are needed in this packet.

This retention operation provides no new runtime/CI result, GitHub approval, cross-platform acceptance, pristine package claim or publication claim.
