# Perf-01 CI121 canonical and package evidence

This is an observed functional CI checkpoint for product head
`3db42f3131c72be217e49e386ba61ece7cee27fb`, not final performance acceptance.
The subsequently prepared native shutdown correction is outside this run.
No local build, sanitizer change, benchmark or long segment was executed for
this inspection.

## Actual source and run

[CI121](https://github.com/IzuSharp/NativeWeave/actions/runs/44671262148)
completed successfully. Build job `136072602761`, A20 job `136072602385`, four
security jobs and aggregate Verify job `136080351564` all reported success.
The actual checkout was merge commit
`7613d9eedad779ee34a7e74855b9bf3c77854150`. GitHub commit reads confirmed that
this checkout and the head both have tree
`efadf940789569f3beaf94c41d9be88f11883a94`; its parents are the frozen main
`ea5fa528035d025bd7a28698ee7c71194432236c` and the stated head. The retained
source-commit log agrees, and its source-status log is empty.

The actual canonical `eng/build.py verify` step, fresh SDK container step,
Task-04 and Task-07 steps, their source-drift checks and artifact uploads all
completed successfully. The run is not evidence that every domain-specific
functional suite ran; those remain separately tracked local or CI obligations.

## Verified archive and retention

The [complete evidence artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44671262148/artifacts/14600614730)
was downloaded through the normal GitHub artifact connector and read back:

| Field | Observed value |
| --- | --- |
| Artifact ID | 14600614730 |
| Complete ZIP size | 46,797,212 bytes |
| Complete ZIP SHA-256 | `ad5e09e481294b6556931a06554d8c2f517e3540cc12562a4718fc9936e7891b` |
| ZIP members | 1,248 |
| GitHub expiration | 2026-12-04 04:19:52 UTC |
| Inspection | Full archive byte hash and size; named JSON members and source logs read directly from ZIP |

The downloaded archive matches GitHub's actual size and digest. It was not
fully extracted. The owner retains the complete private archive, build log,
GitHub metadata and exact source identity readbacks. No raw archive, raw log,
operational command, host path or control record is copied into this public
numeric projection. Artifact availability after the stated GitHub expiration
is not promised. The repository retains this small summary and its manifest.

## Observed results

Canonical verification reports `passed` for all 11 declared checks: Rust
formatting, Clippy and tests; locked restore, managed build and formatting;
source interop tests, compiled API/XML, package layout, isolated package
consumption and actual Native AOT execution. The summary pins the actual
package/native hashes and ten individually inspected JSON member hashes.

Task-04 records a passing Core closure, 17 passing package guard cases and an
actual pristine consumer with Rust absent, offline use after restore and
ordinary managed Entity/DTO/Handler edits. Its minimum-CPU evidence is emulator
execution; physical CPU certification remains false.

Task-07 records a passing 17-package candidate across six graphs, 54 completed
consumer processes, ten passing negative cases, 11 passing publication/rollback
mechanism cases and seven passing runtime-only transfer cases. The candidate
consumer's pristine-machine field is true with Rust absent; the separate
runtime-only receipt reports its expected build tools absent. Public domain
release and new signer authentication remain false.

The basic fresh-SDK receipt has Rust-absent-before-build and AOT-executed fields
true, but its `pristineMachine` field remains **false**. That original value is
preserved in the summary; the Task-04 and Task-07 pristine receipts above are
separate evidence. A20's job status is successful here; its CI121 artifact was
not independently downloaded in this inspection. The earlier CI120 A20 report
contains the completed deep artifact inspection for its own exact source tree.

## Limits and next gate

This checkpoint grants zero performance or 30-minute credit. The measurement
host, frozen compiler settings, packages and loaded native libraries must still
be identified by the actual local after build and performance records. The
later native shutdown code change needs its own regressions and normally
triggered final-head CI. No result here is relabelled as covering that change.
