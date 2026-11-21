# Perf-01 historical closeout: runtime replacement and scope conflict

## Status

This is evidence preservation, not performance acceptance or a new measurement
epoch. No build, workload, cleanup unlink, hardlink deduplication, PR reopening,
merge, or DB-Scope-01 implementation was started after the observations below.

The current conversation requested continued Perf-01 execution. The repository
subsequently recorded conflicting project-owner directions: close Perf-01
without merging, stop further performance work, and continue a database-only
DB-Scope-01 task from fresh main checkouts. Those directions are recorded in
[NativeWeave PR19's closure comment](https://github.com/IzuSharp/NativeWeave/pull/19#issuecomment-7062385421)
and [Plan PR23's closure comment](https://github.com/IzuSharp/Plan/pull/23#issuecomment-7062388062).
Both PRs are closed and unmerged. This continuation preserves that state and
requests scope clarification in the originating conversation; it does not
silently choose either conflicting task.

## Runtime interruption

At 2026-11-21T12:12:15Z, a fresh executor observation found both the previous
ROOT and current scratch directory empty. The old epoch-002 directory and
canonical Plan worktree were absent. The replacement host reported hostname
`f0eae17d9af6`, boot ID `b1268a3a-2a35-4bc5-938a-19cc43bb91f2`, and disk usage
55,791,616 bytes used / 64,077,996,032 bytes free. SHA-256 of the raw current
boot-ID file, including its newline, is
`fab4c6b647b597723c31a077dddfe6e4fe590c6b3b4d2eb026bd98403ae5467b`.

No final cache unlink had executed. The completed read-only inventories had
proposed 4,465 Rust intermediates / 3,262,537,728 allocated bytes and 585 NuGet
extraction copies / 1,385,099,264 allocated bytes. Their combined estimate did
not reach the unchanged 16 GiB entry floor. The last NuGet plan had observed
SHA-256 `4b4415b4f95ca88470459f521fde6200024512ba82aff1cfb29bc4b48fa62112`.
The hardlink alternative was only an idea. These remembered identities do not
assert that the lost local plans or private configs are recoverable.

The host-bound admission and noise from epoch-002 cannot qualify this new host.
No old timing, capacity or long-duration credit is transferred. No new epoch,
freeze or admission has been created. Later local source wrappers/indexes also
must not be reconstructed from remembered hashes and presented as recovered
bytes.

## Retained product and diagnostic conclusions

The selected minimal source remains
[`7e7732cd7ee40aec319961d328f38b593a4af5da`](https://github.com/IzuSharp/NativeWeave/commit/7e7732cd7ee40aec319961d328f38b593a4af5da),
tree `55c3926a6963f5276de24e35314a2c8678c61f90`. It has the two explicit
1 ms Data/Server coordinator options above the cleanup-corrected 2f product.
The original shared coordinator, 10 ms default, AsyncOperation and gRPC writer
are unchanged. [CI44900482037](https://github.com/IzuSharp/NativeWeave/actions/runs/44900482037)
passed all seven jobs. Fresh local005 producers and affected B04/B17/B18
acceptance were not executed for this selected source.

The six completed SQLite C16 application diagnostics compared actual 2f with
a5748, not EA5 with final7e. They completed 18,006 successful business operations
with independent durable-state and drain checks. Mean process p99 was
172.307494 versus 47.522623 ms; measurement CPU time increased 12.355% on the
published projection. Zero observed BUSY/LOCKED exceptions and explicit retries
in these processes do not explain or erase the earlier 567.131236 ms failure.

Retry TLS had 13/15 lower paired case-p99 observations and increased active and
idle CPU. The per-message writer and occupied-prefix experiments remain
unretained: their streaming tail and/or after-idle RSS regressions prevented
retention despite allocation or CPU savings. Constructed native cleanup
regressions do not establish the cause of the earlier real-TLS high-load
missing-header/drain failure. Existing mixed capacity/long gates remain the
required application-level proof if Perf-01 is explicitly resumed.

Historical product2f formal status remains **15/16 short scenes, 0/15 capacity
runs, and 0/10 accepted current-artifact 30-minute segments**. None is credited
to selected7e or the replacement host. Earlier historical long results remain
separately described in their original records; they do not complete this
final-version acceptance.

## Actual durable retrieval after replacement

All 21 previously saved completed-diagnostic archives were fetched by their
exact file IDs, Library IDs and version0 into the replacement workspace.
The transfer helper checked each retained archive SHA-256. The standalone
[readback verifier](verify_perf01_retained_archives_assertions_001.py) then independently checked
the archive hash, unique safe regular-file member set, exact identity manifest
hash, every member's size/mode/SHA-256, original recorded hashes where present,
and all aggregate counts. The actual invocation used `python3 -E` with optimization level0 and enabled
assertions, recorded in the receipt; the verifier rejects disabled assertions.
Verification completed at
2026-11-21T12:21:23.902912Z.

- 21 archives; **128,686,740 compressed bytes**.
- 379 original members plus 21 identity manifests; **400 members verified**.
- **662,573,236 original payload bytes**.
- 336 member hashes had prior recorded provenance; 43 were observed when the
  archive was made. The latter are not relabeled as earlier producer hashes.

[The retrieval index](completed-diagnostics-retention-001.json) contains every
exact filename, file ID, Library ID, version, archive hash, byte count, member
count and owner-authorized link. [The member index](completed-diagnostics-members-001.json)
preserves all 21 verified embedded identities. No signed transfer URLs or
completion tokens are published. Owner-authorized links do not grant other
GitHub readers access.

This archive scope covers the completed retry TLS, scalar and full SQLite C16
diagnostics, A06 principals and selected actual package/binary principals,
including the actually used common TLS client. It does **not** claim to retain
the later prefix TLS raw set or a complete runnable old-host environment.

No automatic file expiration was reported. Availability was verified at the
timestamp above; no minimum future retention guarantee is claimed. The owner
may delete the saved items. The public identities remain available for as long
as the Plan Git history is retained. This closeout has **zero performance or
long-test credit**.
