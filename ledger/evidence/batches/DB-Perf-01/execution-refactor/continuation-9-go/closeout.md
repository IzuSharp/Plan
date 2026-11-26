# DB-Go-01 — completed measurements and actual local source cleanup

## Current disposition

The requested Go comparison is complete: SQLite and PostgreSQL each finished
one 1,800-second offered interval, drained all admitted work and passed their
business/oracle checks. This resumption performed **zero new benchmark runs**
and changed no product runtime. Korda #39 and Plan #35 remain **open drafts,
unmerged, with auto-merge disabled**. No product release is selected.

The [complete report](final-report.md), [exact comparison](comparison.json),
[SQLite raw result](measurements/sqlite-final-01/go-c4.json) and
[PostgreSQL raw result](measurements/postgresql-final-01/go-c8.json) retain all
measurements and their source identities. The historical Korda/Dapper.AOT
measurements were reused unchanged, not rerun.

| Go result | SQLite | PostgreSQL |
| --- | ---: | ---: |
| Successful operations | 5,386,460 | 6,468,551 |
| Rejected arrivals | 13,540 | 11,449 |
| Successful operations/s | 2,992.477591 | 3,593.636177 |
| Scheduled p50 / p95 / p99, ms upper bounds | 0.252928 / 2.146304 / 6.586368 | 0.407552 / 2.867200 / 5.898240 |
| Service p50 / p95 / p99, ms upper bounds | 0.104448 / 1.425408 / 3.440640 | 0.305152 / 2.457600 / 4.063232 |
| Client CPU microseconds/success | 556.720960 | 388.866609 |
| Whole-command peak RSS, MiB | 23.730469 | 21.539063 |
| Post-close idle RSS, MiB | 21.625000 | 15.488281 |
| Go TotalAlloc bytes/success | 3,139.808005 | 4,132.255247 |
| Go GC cycles during steady window | 9,186 | 10,112 |
| Business failures / oracle failures / retries | 0 / 0 / 0 | 0 / 0 / 0 |

These fixed-rate, single-run observations are not maximum-capacity measurements.
Go is database/sql with manually written typed DTO readers, not an ORM. Runtime
heap figures include business objects, driver and harness work; cross-runtime GC
counts and heap bytes are not interchangeable framework-only measurements.
The report includes the slightly higher Go scheduled p50 alongside its lower
observed p99/CPU/RSS relative to historical Dapper.AOT.

## Evidence retained before deletion

- [Independent resumption audit](resumption-evidence-review.md): raw counts,
  35 cases, all 1,800 seconds, four histograms, resources, 38 frozen files,
  31 analysis references, 11 measured runtime source blobs and 186 Go archive
  members were checked without rerunning a test.
- [Initial remote byte readback](cleanup/remote-evidence-readback.json): all
  61 existing result/source/archive files at Plan `3aef334c5c44aac364ca500d9bafffd66a8152b1`
  matched their length, SHA-256 and Git blob identity.
- [Supplemental remote byte readback](cleanup/supplement-remote-readback.json):
  all 17 added/updated files at Plan `6c4730346f05e9bff3da192d686fdc0c0ffcb922`
  matched. This includes the additional historical archive and cleanup review.
- [Final input recheck](cleanup/final-freeze-recheck.json): 38/38 frozen files
  still matched immediately before the primary cleanup.
- [Additional retained history](archive/additional/manifest.json): six previously
  modified/untracked handoff files, their diff, recovery notes, old failed build
  logs, historical text artifacts and exact incremental Git bundles were
  preserved. All 976 members passed local readback; prerequisites were verified
  at immutable remote commit identities.

Go archive SHA-256 is
`eac700a195dce834006a56a50df1f2934a095e15f6a2b1f66fc21a0931d9ce3d`;
legacy supplement is
`51b6fa864fc108c71365d5e356a0672453d1cf0df4def65df209ff362da15787`;
additional history is
`1b343b5243d4d9c22d8a67217bd0acaf57ad37485844abb4e34032e25bc39c29`.
These archives preserve source/evidence and omission records. They intentionally
do not retain every compiled executable, package cache, database file or key.

## Actual source, worktree, database and cache removal

| Scope | Observed outcome |
| --- | --- |
| Registered worktrees | 65 removed and unregistered: 62 primary, 3 additional |
| Primary temporary targets | All 32 absent; 24 removed as temporary targets and 8 already absent after their worktree removal |
| MSBuild temporary directories | All 66 exact directories removed |
| Older source/recovery areas | Older project root and recovery subdirectory removed, including two upstream study clones |
| Primary source areas | All 25 remaining project-owned top-level children removed from three roots, including repository mirrors, consumers, measurements, tools, builds and caches |
| NuGet HTTP cache and scratch locks | 57 cache files and 1,243 empty lock files removed |
| Read-only Go modules | Official task-scoped go clean -modcache succeeded; module-cache target absent |
| Go telemetry | Nine original files removed; three recreated by the official cleanup invocation subsequently removed, with empty task wrappers |
| Stale CLR diagnostics | Twelve exact FIFOs removed after checking process lifetimes and open descriptors |
| SDK advertising/control files | Empty advertising directories and original temporary cleanup controls removed |
| Process signals / platform permission changes | None |

Actual receipts:
[additional cleanup](cleanup/additional-cleanup-receipt.json),
[primary original attempt](cleanup/primary-cleanup-receipt.json),
[successful narrower continuation](cleanup/primary-resumed-cleanup-receipt.json),
[official Go cache cleanup](cleanup/go-module-cache-cleanup.json), and
[final runtime/control remnants](cleanup/residual-temporary-cleanup-receipt.json).
The cache command internally adjusts modes of its task-owned module directories
as part of official removal; it does not alter platform-owned directories.

### Preserved refusal and narrower continuation

The original frozen helper completed 94 recorded actions, then could not remove
a platform-owned control directory inside the first workspace root. Its status
remains **refused-or-partially-completed**. The failure and original interruption
state were preserved; it was not relabelled successful or modified to bypass
permissions. Three platform control directories and their containing roots
remain deliberately in place.

An [independent follow-up review](cleanup/primary-cleanup-continuation-review.md)
confirmed the exact residual project scope and the separate read-only Go module
cache issue. The official Go cache command resolved the owned cache. The
[narrower continuation](cleanup/finish_project_cleanup.py) then revalidated the
original archive gate and state, required no registered worktrees or blocking
processes, and removed only the 25 exact project-owned children with inode,
mount and symlink checks. Its successful receipt explicitly says the project
content is absent and the root directories themselves were not removed.

A separate first supplementary execution was refused before mutation because its
acceptance file had not been generated after a preparation parsing error. That
[zero-action refusal](cleanup/additional-cleanup-refused-no-acceptance.json) is
retained. Correct preparation then supplied the already-authorized, verified
archive acceptance; no guard was relaxed.

## Final inspection and temporary closeout workspace

The [post-cleanup scan](cleanup/post-cleanup-source-inventory.json) found no
project source files, Git markers or known task caches outside this temporary
closeout workspace. The completed scan returned exit 0 with no warnings across
workspace, user-home, temporary and available var/tmp locations, excluding the
execution platform and persistent Library storage. An initial filesystem
recovery-directory warning is preserved as a separate earlier observation.

**Final closeout staging removal is complete.** After all 25 cleanup-record
files at Plan `490436ad456581762ea204dddf820d1b155d0d71` passed
[remote byte readback](cleanup/final-receipt-readback.json), all 46 task-created
top-level staging entries were removed, including temporary scripts, archive
copies and controls. The [last cleanup receipt](cleanup/final-workspace-cleanup-receipt.json)
records the actual removal and a final exit-0 scan with no warnings: zero project
source files, zero Git markers and zero known task caches remain. System software,
platform/session metadata and persistent remote storage are retained.

## Checks and stopping point

No performance workflow, job, trigger, schedule or hidden CI benchmark was added.
Korda source CI run `45825411327` succeeded. The retention commit's existing
Plan integrity run `45843144041` succeeded; later evidence commits observe their
own existing checks separately. The historical record gate was run at its exact
CI-selected frozen commit and passed; the rejected wrong-input invocation is
retained in [validation](cleanup/closeout-validation.json), without giving any
historical gate new performance credit.

The work stops after durable records, local-source cleanup and Draft-state
verification. No merge, release, additional benchmark or optimization follows.
