# Perf-01 compiler-cache cleanup 003: actual preservation checklist

The reviewed, explicitly invoked storage operation completed successfully from
**2026-11-20 11:20:28.291970 to 11:21:49.420436 UTC**, under the exclusive
measurement lock on CPU8. It removed 23,034 reproducible compiler/cache files,
6,338,895,088 apparent bytes. No product workload ran during this operation;
it grants zero performance or long-duration credit.

| Selected class | Actual removed files | Apparent bytes |
| --- | ---: | ---: |
| Rust intermediate objects and metadata | 774 | 1,061,028,621 |
| Rust incremental cache | 728 | 173,063,331 |
| SDK members fully reproducible from retained nupkg | 21,532 | 5,104,803,136 |
| Total | 23,034 | 6,338,895,088 |

Free space was **4,467,671,040 bytes before** and **10,827,952,128 bytes after**.
These are actual observations during the operation, not a guarantee of free
space after later builds. The ending value is approximately 10.08 GiB.

## What was preserved and verified

All 168 original package archives, totaling 2,843,002,904 bytes, remain in
place. The executor fully hashed each archive before removal and again at
completion. Every selected SDK file was compared byte-for-byte with its full
decoded archive member and checked against its CRC before unlink. Each selected
file was separately SHA-256 hashed and checked for unchanged device, inode,
size, timestamp, mode and single-link identity immediately before unlink.

The operation preserved actual test/application executables, product shared
libraries, published outputs, package archives, source, logs, manifests and all
raw measurement records. It did not delete entire Cargo build directories:
this layout also stores actual executable/shared-library outputs inside them.
Forty-seven multiply-linked candidates were excluded during preparation.
The protected set comprised 281 absolute references from 65 actual manifests
and the final-002 long-test binding; no selected path overlapped that set.
Active gRPC diagnostic/build roots were outside the fixed selection.

The append-only journal contains exactly 23,034 fsynced verification intents
and 23,034 matching unlink completions, with one start and one end record.
No resume or inferred-absence reconciliation occurred. A separate post-operation
review checked every intent/completion pair, confirmed all selected paths were
absent, rehashed all 65 protected manifests, checked the 168 retained archives'
unchanged filesystem identities, and verified the source/inventory/receipt
bindings. The reviewer did not repeat the executor's large archive byte hashes.

## Receipts and reproduction boundaries

[public-summary.json](public-summary.json) preserves the exact counts, interval,
space observations, selection and verification hashes. [manifest.json](manifest.json)
binds these public files. The actual execution receipt SHA-256 is
`ab650af5362acac89d97228a2a69a966c25a2af7f2e20599623041144eb7bd9f`;
the full journal SHA-256 is
`0220bb1b7b0720e89fffd28e6787e771050d16517ee4789e3eb72d8d500c8549`.

The first read-only inventory attempt refused a multiply-linked rlib and
stopped without deleting anything. That failure remains recorded; the corrected
selector excluded all such candidates. Eight bounded temporary-file checks
then exercised preservation, stale identities, symlink/hardlink rejection,
SDK byte mismatch and explicit interruption/resume handling. The production
cleanup itself completed on its first attempt with no error.

Expanded SDK caches are intentionally incomplete after cleanup. Rebuilding an
old consumer may require restoring the exact selected members from its retained
nupkg, checking the archive hash and decoded file hashes in the journal; ordinary
NuGet restore may trust existing completion metadata. Rust compiler intermediates
can be regenerated from the pinned sources, toolchain and dependencies. The
actual tested programs and their published dependencies remain available.

Public synthetic counts and checklists remain in Git while repository history
is retained. The exact operational inventory, per-file journal and archive-hash
list remain in the measurement workspace. No remote raw operational archive is
claimed, and no accepted or failed measurement classification is changed.
