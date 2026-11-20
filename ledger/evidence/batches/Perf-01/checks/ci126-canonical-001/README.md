# Perf-01 CI126 canonical and package evidence

[CI126](https://github.com/IzuSharp/NativeWeave/actions/runs/44732929976),
attempt 1, completed successfully at **2026-11-20 12:24:11 UTC** for public
head `12c477f0cdbc01fb026e98ac0e26eb45617424ed`. That source contains
both the per-value gRPC header-credit correction and managed request-admission
lifetime correction, plus the still **unretained** scratch candidate. Build job
136276995145, A20 job 136276995126, four security jobs and aggregate Verify
job 136285582142 all succeeded.

This is finite functional CI evidence. It grants **zero performance, capacity
or 30-minute measurement credit**. Dedicated local B17, B18, Application, MCP
and diagnostics gates retain their own results. Earlier failed B18 gates and
their separate causal reproductions remain preserved; this CI success does not
rewrite them or select the scratch implementation.

## Exact checked-out source

The actual checkout is merge commit
`abe83d5ae77049a2d4a7795ff45958a197bc787c`. The build log and archived
source-commit log identify it, and the source-status log is empty. Independent
GitHub commit reads confirm that checkout and public head have the same tree:
`0c763ba3b908dcc289528369231daf1788f87571`. Checkout parents are frozen
main `ea5fa528035d025bd7a28698ee7c71194432236c` and the stated public
head. Source-drift checks passed.

The Rust test log includes the ordered-acceptor-outcome and real-network shutdown
regressions. The Host suite reports 19 passed and zero failed. This report does
not claim that CI126 executed every dedicated module suite or replace the local
gate for the new request-owner retirement fixtures.

## Complete evidence archive and retention

| Field | Actual observation |
| --- | --- |
| [Evidence artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44732929976/artifacts/14627024955) | 14627024955 |
| Complete ZIP bytes | 46,773,059 |
| Complete ZIP SHA-256 | `988889907d3484b67c32b86a70431dd5554c5875d66d37aa5e5bceb6342c1d38` |
| ZIP members | 1,248 |
| GitHub expiration | 2026-12-04 12:23:54 UTC |
| Inspected named members | Ten result JSON members and the actual Rust test log |

The complete ZIP was downloaded; actual size and SHA-256 match GitHub metadata.
The inspector read named members directly without full extraction. Archive
bytes, the build log, identity reads and inspection receipts are retained
privately. Availability beyond the stated expiration is not promised. The small
repository summary and manifest remain retrievable while history is retained.

## Observed checks

Canonical verification reports all 11 declared checks passed: Rust formatting,
Clippy and tests; locked restore, managed build and formatting; source interop
tests, compiled API/XML, package layout, isolated package consumption and actual
Native AOT execution. The summary preserves the original independent-review
and public-publication fields as false.

| Scope | Actual archive result |
| --- | --- |
| Task-04 Core closure | Passed |
| Task-04 minimum CPU | Emulator case passed; physical CPU certification false |
| Task-04 package guards | 17 cases passed |
| Task-04 pristine consumer | Passed; Rust absent; ordinary managed Entity/DTO/Handler edits and offline-after-restore execution retained |
| Task-07 candidate | 17 packages, six graphs, 54 exited consumer commands and ten passed negative cases |
| Task-07 publication/rollback mechanism | 11 cases passed; public domain release and new signer authentication remain false |
| Task-07 runtime-only transfer | Seven cases passed, 17 packages and expected build tools absent |

The basic fresh SDK receipt has `pristineMachine` false and actual AOT
execution/Rust-absent-before-build true. The separate Task-04 and Task-07
pristine-consumer receipts have pristine-machine true. These distinct original
values remain explicit. Historical performance and fault/soak runs were not
rerun by these package gates.

## Separately retained basic candidate

The [basic candidate artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44732929976/artifacts/14628112420)
was also downloaded and inspected without executing its code. It is the
experimental HelloWorld bootstrap package, not a measured domain package.

| Field | Actual observation |
| --- | --- |
| Artifact ID and complete bytes | 14628112420; 322,001 bytes; three ZIP members |
| Complete ZIP SHA-256 | `945f86d4d01b088f83ccaead11eeaebea2a501abad381f3e40902282bf4498b6` |
| GitHub expiration | 2026-12-04 12:23:58 UTC |
| Package bytes and SHA-256 | 255,532; `89de40ac01398d448ccc414d6b6d72f7e20881e48c7b1263d25eb86c8f5d1d8e` |
| Embedded native bytes and SHA-256 | 413,168; `763c704c05b61d8f1d7689f60da094b46cb25403951d83b528893228d464e985` |
| Source inventory | All 1,496 declared tracked-file hashes verified |

Both declared archive checksums match actual bytes. The package's embedded
manifest is byte-identical to the outer manifest, and its native hash and
package hash match canonical verification. Both manifest producer fields name
the actual CI checkout with source-dirty false. The complete source inventory
was checked against the clean local `9de3f74444246e356a2b12ab664ef99286309aaf`
checkout after independently verifying its identical tree. That local commit is
only a source-byte reference; the CI producer identity remains `abe83d5...`.

## A20, method and limits

The same checkout/tree has independently inspected
[A20 evidence](../ci126-a20-001/README.md): 48 expected command outcomes,
96 verified log hashes, enabled C ASan/UBSan/leak checks and 20,000 actual fuzz
units. This summary binds that projection by SHA-256 and checks source,
checkout and tree agreement. Rust, CLR and Native AOT runtime sanitizer
instrumentation is not claimed.

The strict CI125 canonical inspector was reused with only actual source,
artifact, job, run and location substitutions. Its CPU-8 offline inspection
exited 0 in 0.107898434 seconds. The additional basic-candidate/source audit
exited 0 on CPU 8 in 0.397523078 seconds. No local product test, native code
load or workload ran. Private inspector sources, actual receipts and download
identities are bound by the manifest. Earlier CI records were unchanged.

CI tools, domain consumers and the basic candidate remain separate from the
measurement host's fixed compiler, locally produced packages and actually loaded
native libraries. No later source change is covered. No performance improvement,
long-run duration, public domain release or other-platform acceptance is granted.

Published files contain fixed roles, numbers, booleans and verified hashes.
Raw commands, logs, host paths, process identifiers and operational control
records remain outside this projection.
