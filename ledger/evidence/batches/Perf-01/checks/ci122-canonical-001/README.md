# Perf-01 CI122 final-source canonical and package evidence

[CI122](https://github.com/IzuSharp/NativeWeave/actions/runs/44674553861), attempt1,
completed successfully for product head
`ada13b865ec5d19876745498f6f51d8ad2367399`. The build job `136083168564`,
A20 job `136083168197`, four security jobs and aggregate Verify job
`136088916652` all completed successfully. This is actual functional CI,
with zero local performance or 30-minute credit.

## Exact source

The actual build checkout is merge commit
`34ed067343298abfb78947f750730f7efb29c101`. The build log and archived
source-commit log both identify it; the archived source-status log is empty.
GitHub commit reads independently confirmed that the checkout and reported
head have the same tree, `0d1b1ca390b582b1f2ebf004f7778c8f084a68a4`.
The merge parents are frozen main `ea5fa528035d025bd7a28698ee7c71194432236c`
and the stated head. The normal source-drift checks also succeeded.

This tree includes the Host acceptor shutdown correction. The archived actual
Rust test log contains successful ordered-acceptor-outcome and real-network
shutdown tests; the Host suite reports 19 passed, zero failed. The independent
local B17/B19/B15/B18 gates remain separate evidence, and this CI report does
not claim that every module's dedicated functional suite ran here.

## Full archive readback and retention

| Field | Actual value |
| --- | --- |
| [Evidence artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44674553861/artifacts/14602412744) | 14602412744 |
| Complete ZIP size | 46,797,437 bytes |
| Complete ZIP SHA-256 | `ddfa6160f6f07f4864f0e279c30edef1b7716f0b0ab1ce4ff00a12a65013db71` |
| Members | 1,248 |
| GitHub expiration | 2026-12-04 04:43:36 UTC |
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

The same checkout/tree also has the separately inspected [A20 artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44674553861/artifacts/14602355702).
Its complete byte readback, 48 actual expected exits, 96 log hashes, enabled
ASan/UBSan/LSan and actual 20,000 fuzz units are recorded in the adjacent
`ci122-a20-001` report. This summary binds that report by SHA-256 and verifies
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
