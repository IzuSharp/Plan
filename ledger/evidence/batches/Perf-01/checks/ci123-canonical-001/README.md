# Perf-01 CI123 final-source canonical and package evidence

[CI123](https://github.com/IzuSharp/NativeWeave/actions/runs/44690977311), attempt1,
completed successfully for product head
`0715ffb6376b1ae08259ad7e2cb30ff0320d83e7`. The build job `136136417413`,
A20 job `136136417002`, four security jobs and aggregate Verify job
`136144603220` all completed successfully. The workflow ended at 2026-11-20 07:14:28 UTC.
This is actual functional CI,
with zero local performance or 30-minute credit.

## Exact source

The actual build checkout is merge commit
`36a10cb612d06edc0298596a843b7a4dc66b258a`. The build log and archived
source-commit log both identify it; the archived source-status log is empty.
GitHub commit reads independently confirmed that the checkout and reported
head have the same tree, `cd0a6022e0115c22f133aedf6c801d9244640523`.
The merge parents are frozen main `ea5fa528035d025bd7a28698ee7c71194432236c`
and the stated head. The normal source-drift checks also succeeded.

This tree removes the extra post-result retirement retry while retaining the
lazy stream waiter and Host acceptor shutdown correction. The archived actual
Rust test log contains successful ordered-acceptor-outcome and real-network
shutdown tests; the Host suite reports 19 passed, zero failed. The independent
local B17/B19/B15/B18 gates remain separate evidence, and this CI report does
not claim that every module's dedicated functional suite ran here.

## Full archive readback and retention

| Field | Actual value |
| --- | --- |
| [Evidence artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44690977311/artifacts/14610125599) | 14610125599 |
| Complete ZIP size | 46,773,136 bytes |
| Complete ZIP SHA-256 | `4769c245431ac003ec4127af52872cb5e5f5b30e810f02120222a11cbd0770b0` |
| Members | 1,248 |
| GitHub expiration | 2026-12-04 07:14:10 UTC |
| Independently inspected named members | Ten result JSON members and the actual Rust test log |

The normal artifact connector fetched the complete archive. Its actual size
and SHA-256 match GitHub's metadata. Named members were inspected directly
inside the ZIP, without full extraction. The owner retains the original
archive, build log, GitHub metadata, commit identity reads and actual offline
inspection receipt. GitHub artifact retention after the stated expiration
is not promised. The small repository summary and manifest retain the
numeric and hash evidence.

## Observed checks

The canonical `eng/build.py verify` step reports passed for all 11 declared
checks: Rust formatting, Clippy and tests; locked restore, managed build and
formatting; source interop tests, compiled API/XML, package layout, isolated
package consumption and actual Native AOT execution. The package/native hashes
under `canonical` describe that basic package gate; they are not substituted
for the measured domain packages or native libraries.

The fresh SDK container step and Task-04/Task-07 verification and drift steps
all completed successfully. Their actual archive results record:

| Scope | Actual result |
| --- | --- |
| Task-04 Core closure | Passed |
| Task-04 minimum CPU | Emulator case passed; physical CPU certification false |
| Task-04 package guard cases | 17 passed |
| Task-04 pristine consumer | Passed; Rust absent; ordinary managed Entity/DTO/Handler edits and offline execution after restore retained |
| Task-07 candidate | 17 packages, six graphs, 54 exited consumer commands, ten passed negative cases |
| Task-07 publication/rollback mechanism | 11 cases passed; public domain release and new signer authentication remain false |
| Task-07 runtime-only transfer | Seven cases passed, 17 packages, expected build tools absent |

The basic fresh SDK receipt's `pristineMachine` field is false, while its
Rust-absent-before-build and actual AOT execution fields are true. The separate
Task-04 and Task-07 pristine-consumer receipts have their pristine-machine
fields true. The summary preserves these distinct original values.

## A20 and scope limits

The same checkout/tree also has the separately inspected [A20 artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44690977311/artifacts/14608019637).
Its complete byte readback, 48 actual expected exits, 96 log hashes, enabled
ASan/UBSan/LSan and actual 20,000 fuzz units are recorded in the adjacent
`ci123-a20-001` report. This summary binds that report by SHA-256 and verifies
its head, checkout and tree agree with the canonical evidence.

CI functional tools and binaries are distinct from the fixed measurement-host
compiler, final locally built packages and actually loaded native libraries.
The performance driver records those independently. No local canonical build
was rerun for this archive inspection, and no result is inferred for a later
source change. This checkpoint does not grant performance improvement,
long-run duration, public package release or another platform's acceptance.

The published summary contains only fixed roles/enums, numbers, booleans and
verified hashes. Raw commands, host paths, process identifiers, logs and
control records stay outside this projection. The private artifact inspector
ran on CPU8, exited0 and did not execute any test or benchmark program.

An independent reviewer compared this inspection source with the preceding
CI122 method and checked the new small summary bindings. No verification gate
was weakened; changes were confined to exact identities and output locations.
That review did not rerun the inspectors or rehash the archives. The actual
full-byte and named-member audit execution is recorded separately above.
