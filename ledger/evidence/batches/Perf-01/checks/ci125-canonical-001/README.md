# Perf-01 CI125 canonical and package evidence

[CI125](https://github.com/IzuSharp/NativeWeave/actions/runs/44726962784),
attempt 1, completed successfully at **2026-11-20 11:38:02 UTC** for public
head `423c07c1d8969298e605e9488b4c271ea3d0148a`. This source includes the
per-value gRPC header-credit correction and the still **unretained** managed
scratch candidate. Build job 136256707733, A20 job 136256707444, four security
jobs and aggregate Verify job 136264200231 all succeeded.

This is finite functional CI evidence. It grants **zero performance or
30-minute measurement credit**. The separately executed local corrected-control
B18 gate passed JIT and then failed Native AOT: the second persistent TLS/H2
call returned `Internal: managed dispatch unavailable` after the first call's
physical owner and native gauges had retired. This CI success does not replace
that failed gate, establish the cause of its failure, or accept the candidate.

## Exact checked-out source

The actual checkout is merge commit
`45a20165f6344f91b79ad703b36cebb0cf26bd9c`. The build log and archived
source-commit log identify it, and the source-status log is empty. Separate
GitHub commit reads confirm that the checkout and reported public head have
the same tree: `86c4ac7a7c4d17f705d3fa52af4fafdb6959d2da`. The checkout
parents are frozen main `ea5fa528035d025bd7a28698ee7c71194432236c` and the
stated public head. Source-drift checks passed.

The actual Rust test log includes the ordered-acceptor-outcome and real-network
shutdown regressions. The Host suite reports 19 passed and zero failed. This
report does not claim that every module's dedicated functional suite ran in
CI125, or that the new persistent-header fixture has passed the local B18 gate.

## Complete archive readback and retention

| Field | Actual observation |
| --- | --- |
| [Evidence artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44726962784/artifacts/14626275105) | 14626275105 |
| Complete ZIP bytes | 46,773,056 |
| Complete ZIP SHA-256 | `24a379cb320389029f5a75859e4c93c1cb1d5352317288dd5e7db489124715b5` |
| ZIP members | 1,248 |
| GitHub expiration | 2026-12-04 11:37:44 UTC |
| Inspected named members | Ten result JSON members and the actual Rust test log |

The artifact connector fetched the complete ZIP. Actual size and SHA-256 match
GitHub metadata. The inspector read named members directly without full
extraction. The owner retains the archive, build log, identity reads and
inspection receipts. Availability beyond the stated artifact expiration is not
promised. The small repository summary and manifest remain available while
repository history is retained.

## Observed checks

The canonical verification reports passed for all 11 declared checks: Rust
formatting, Clippy and tests; locked restore, managed build and formatting;
source interop tests, compiled API/XML, package layout, isolated package
consumption and actual Native AOT execution. Basic package and native hashes
in the summary identify this gate; they are not substituted for measured domain
packages or actually loaded measurement-host libraries.

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
pristine-consumer receipts have pristine-machine true. The summary preserves
these distinct original values. Historical performance and fault/soak runs were
not rerun by these package gates.

## A20, inspection method and limits

The same checkout/tree has separately inspected [A20 evidence](../ci125-a20-001/README.md):
48 expected command outcomes, 96 verified log hashes, enabled C
ASan/UBSan/leak checks and 20,000 actual fuzz units. This summary binds that
projection by SHA-256 and verifies source, checkout and tree agreement. Rust,
CLR and Native AOT runtime sanitizer coverage is not claimed.

The existing strict CI124 inspector was reused with only actual source,
artifact, job, run and location substitutions. The canonical offline inspection
ran on CPU 8 and exited 0 in **0.167407420 seconds** without executing a test
or workload. Its private source, execution and download receipts are bound by
the manifest. Existing CI124 reports and archives were not changed.

CI tools and binaries remain distinct from the fixed measurement-host compiler,
locally built packages and loaded native libraries. No later source change is
covered. No performance improvement, long-run duration, public domain release
or other-platform acceptance is granted. The local B18 failure and its
subsequent investigation must retain their own actual outcomes.

The published files contain fixed roles, numbers, booleans and verified hashes.
Raw commands, logs, host paths, process identifiers and operational controls
remain outside this projection.
