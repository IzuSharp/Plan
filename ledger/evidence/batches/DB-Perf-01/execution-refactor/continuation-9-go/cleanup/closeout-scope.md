# DB-Go-01 closeout scope and retention

The owner requested the already-completed Go results in the latest Draft PR,
followed by removal of all project source-related content on this execution
machine. Both Korda #39 and Plan #35 remain open drafts, with no merge, auto-merge,
release or additional benchmark run. The original runtime results are unchanged.

## Evidence already recovered

The resumption independently verified the two raw 1,800-second cells, all 35
business cases, every measured second, the histograms and process counters,
38 frozen inputs, 31 analysis input references, 11 runtime source blobs and all
186 original Go archive files. The [resumption review](../resumption-evidence-review.md)
records the exact scope and limitations.

All 61 existing files at Plan `3aef334c5c44aac364ca500d9bafffd66a8152b1`
were downloaded through immutable HTTPS raw URLs. The
[remote readback](remote-evidence-readback.json) records 19,228,242 bytes,
matching length, SHA-256 and Git blob identity for every file. That readback
includes both the Go and legacy archives and the exact source-history bundle.

The current handoff supersedes the archived pre-run RESUME.md. The full report
also now explicitly retains the initial wrong-module-directory Go test setup
failure; its raw log was already archived. Neither final long run failed.

## Additional retention before whole-machine source cleanup

The original frozen cleanup helper covers three roots, 62 registered worktrees
and 32 exact temporary paths. The owner's broader current instruction also
covers the older 697b7eeade37 source area, e91ce0ee6584/recovery, three extra
registered worktrees, two upstream study clones, 66 MSBuild temporary
directories, NuGet HTTP/cache-lock leftovers and nine task-created Go telemetry
files. The [additional inventory](cleanup-additional-inventory.json) binds
those paths and their observed identities. Four Go configuration wrappers may
be removed only when empty.

The [additional archive](../archive/additional/evidence.tar.gz) retains six
modified/untracked Plan files plus their binary diff, 18 recovery/closeout
files, 62 MSBuild records, 881 historical artifact text files, two incremental
Git bundles and their remotely verified prerequisite identities. All 976 archive
members passed local SHA-256 readback. The compressed archive is 830,044 bytes,
SHA-256 `1b343b5243d4d9c22d8a67217bd0acaf57ad37485844abb4e34032e25bc39c29`.
See its [manifest](../archive/additional/manifest.json) and
[local readback](../archive/additional/local-readback.json).

The manifest explicitly records 89 omitted rebuildable, duplicate or credential
items. It preserves identities and omission reasons, not credentials. The Go,
legacy and supplemental evidence archives are not binary recovery images:
compiled executables, package/compiler caches, database files and certificate/key
material are intentionally not copied into the new evidence archive.

## Deletion procedure and status at this retention commit

The [independent safety review](cleanup-safety-review.md) binds both helpers and
the inventories. The original helper bytes are unchanged. The supplementary
helper uses only the exact inventoried paths, inode/content/mount checks and a
remote-readback acceptance; it never signals processes. It also supplies the
read-only process check across both scopes before the original helper runs.

The [residual inventory](residual-temporary-inventory.json) separately identifies
12 old CLR diagnostic FIFOs and two empty SDK advertising directories. No old
CLR lifetime or open FIFO handle was observed; root must recheck immediately
before exact unlink/empty-rmdir. Random unrelated temporary directories are not
included.

**At this retention commit, deletion is not yet claimed complete.** Publish and
read back the supplemental archive first. Then root runs the supplementary
cleanup, regenerates and accepts the original cleanup plan, runs the combined
process check, and executes the original frozen helper. Actual receipts and a
post-cleanup source inventory are committed afterward. The current closeout
workspace, scripts and temporary control files are removed last after their
receipts are durable. System/platform runtime and identity resources remain.

[Closeout validation](closeout-validation.json) retains the initial invocation of
a frozen historical verifier on the wrong current input and the successful run
at the exact commit selected by existing CI. No validation rule or source pin
was relaxed. Historical record checks do not grant additional timed-run credit.
