# Perf-01 obsolete build-copy retention: actual checklist

Root completed this separate lossless storage operation on **2026-11-20,
14:16:12.930893–14:16:56.673625 UTC**. All **342** fixed obsolete generated
`bin/Release` copies were retained as **643,251,109 gzip bytes**, with complete
original-to-decoded hash equality recorded before each removal. Original apparent
size was **1,428,425,528 bytes**; original allocated size was **1,391,017,984 bytes**.
This is storage evidence only, with no correctness, performance, capacity or
30-minute measurement credit.

| Old build role | Files | Original apparent bytes | Gzip bytes |
| --- | ---: | ---: | ---: |
| after-001 | 171 | 714,213,560 | 321,625,898 |
| after-002 | 171 | 714,211,968 | 321,625,211 |
| Total | **342** | **1,428,425,528** | **643,251,109** |

The apparent original-minus-gzip difference is **785,174,419 bytes**. The receipt
separately records free space rising from **7,840,792,576** to **8,587,464,704 bytes**,
an observed difference of **746,672,128 bytes**. Sparse allocation and filesystem
bookkeeping make these different quantities. This point-in-time free-space value
remained below the 10 GiB PostgreSQL preflight and does not predict headroom after
subsequent builds. The preceding [cleanup006](../compiler-cache-cleanup-006/README.md)
remains a separate operation and receipt.

## Scope and preservation

The executed selection is the exact fixed 342-file map, restricted to eight named
obsolete generated bin subtrees per old build. Both old successful nine-producer
receipts and all 18 producer manifests remain preserved. The executor binds 55
source/control files, including the current final003 dependency index
`e95bbd5bf04f677c715c0293c0e6eed0870d26f195984eb9ca0cada68795992c`.

The selected copies are ordinary single-link DLL, SO, debug and executable files.
Canonical executed artifacts, native-stable outputs, feeds/package archives,
source, projects/locks, manifests/receipts/logs, Cargo targets and `obj` paths,
before/direct/comparator/corpus inputs, current 004, final003 and DB diagnostic
paths are outside this selection. Actual historical producer identities and
measurement outcomes are unchanged. Explicit restoration is available for a
future replay that specifically needs these old generated bin locations.

## Actual verification and ownership

For every file, the executor opened the anchored ordinary source, checked its
exact recorded identity, hashed and compressed it, fsynced the archive, decoded
the complete archive, and required original/decoded hash and byte-count equality.
It then reread the original, revalidated the bound controls and active-file guard,
and durably saved the verified mapping before unlinking the exact old copy.
All 342 final records are removed, with unique original/archive/restore mappings
and verified timestamps preceding removal timestamps. Partial bundles were not
resumed or overwritten.

Root first passed all **six temporary-file checks** at 14:16:07 UTC, including
round-trip bytes/mode/mtime, overwrite and corrupt-archive rejection, special-mode
rejection, scope exclusion, and active mapping/descriptor rejection. Their actual
log reports six checks in 0.069 seconds. The check and retention commands both
exited 0, with their process groups and adopted descendants fully retired,
no cleanup signals and no adopted-cleanup errors. The retention child held the
exclusive global timing lock; its parent's inherited descriptor remained unheld.

The previously reviewed retention source/index were unchanged. The independent
read of the small stage adapter in this reporting pass happened **after** actual
execution; it is not represented as pre-execution approval. Its exact source and
actual owner receipts are bound below. The command owner recorded retention
elapsed time of **43.906702351 seconds**, including process startup/retirement;
the manifest interval above covers the retention operation itself.

This projection reads only bounded manifests, selection/source/command metadata,
small owner receipts and logs. It reconciles all 342 file records against the
fixed map, sums their byte counts, checks decoded-hash equality and recorded
restore attributes, and verifies source/owner/log hashes. It does not read gzip
or original payloads, repeat compression/decode, import the executor, restore
files, scan active processes or run another test/workload. The actual executor's
full payload verification remains distinct from this metadata audit.

## Evidence and restoration

[public-summary.json](public-summary.json) holds the numeric/hash checklist;
[manifest.json](manifest.json) binds these two public files.

| Actual evidence | SHA-256 |
| --- | --- |
| Complete private retention manifest | `7246f36320248c631f6b0438e003b85cb309ac4f72df5c6aff31921a86b1711d` |
| Exact fixed selection | `72571c667235e67c3c20e76489cadc05de6a777bd62ac88adfb2120dc228bc34` |
| Retention source | `8d8067dfea34ebd40815ea752d63f46a0aaa137d535d98d7ced25922b99b6918` |
| Source index | `30b43853a1c326d2a84b68ae8a4fa7c1e2322f4b5095ef582c25f808cb414201` |
| Owned retention receipt | `7baba630c4a9176a50c8913a41035d50a18cba86100a30619b98f9270dee1652` |
| Actual six-check receipt | `1b9066a3ab00e56cf31923137103953931747ef82c1870d153745edfb14a64e7` |
| Stage adapter | `10652cafd6286ee40673fa3823134a8eb3b77fc0220abb2f1f666c403bad6549` |

The complete gzip bundle, per-file hashes/size/attribute map, source and actual
restore command remain privately retained under obsolete-build-cold-retention-001.
The stored command binds the exact final manifest and writes only into a fresh
restoration directory. Restoration verifies each compressed and decoded hash,
reapplies the recorded ordinary `0744` or `0755` mode and nanosecond mtime, and
checks the restored bytes and attributes before the final rename. New inode and
ctime are expected; no in-place overwrite or identical filesystem identity is
claimed. No actual bundle restoration was performed by this checklist.

The public synthetic checklist remains in Git while repository history is retained.
The private archive has no promised remote retention period; no remote copy or
public binary publication is claimed.
