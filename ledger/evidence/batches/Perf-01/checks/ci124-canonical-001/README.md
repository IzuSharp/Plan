# Perf-01 CI124 candidate canonical and package evidence

[CI124](https://github.com/IzuSharp/NativeWeave/actions/runs/44715862136),
attempt 1, completed successfully at **2026-11-20 10:19:13 UTC** for public
gRPC scratch candidate `458939dab00d4080cd36076d31d912114f245340`.
Build job 136218972146, A20 job 136218971778, four security jobs and aggregate
Verify job 136226862215 all succeeded. The candidate remains **unretained**.
This is functional CI evidence, with zero local performance or 30-minute credit.
It does not replace the separately failed local B18 cancellation/retirement gate.

## Exact source

The actual checkout is merge commit
`a2cb240f0c08face6eac2779d66e14b2ed828566`. The build log and archived
source-commit log identify it, and source-status is empty. GitHub commit reads
confirm that checkout and reported head have the same tree:
`6dad1215d22d5c950c33dafeae3e9d876ec7cd0b`. Its parents are frozen main
`ea5fa528035d025bd7a28698ee7c71194432236c` and the stated product head.
The normal source-drift checks passed.

The archived Rust test log includes successful ordered-acceptor-outcome and
real-network shutdown regressions. The Host suite reports 19 passed and zero
failed. This report does not claim every module's dedicated functional suite
ran in CI124, or grant the new cross-call writer fixture a local B18 pass.

## Full archive readback and retention

| Field | Actual observation |
| --- | --- |
| [Evidence artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44715862136/artifacts/14619839281) | 14619839281 |
| Complete ZIP bytes | 46,772,904 |
| Complete ZIP SHA-256 | `43be934c47fb8906bc9e271b90d9296dbd98e90dc221a056f07092492eae7637` |
| ZIP members | 1,248 |
| GitHub expiration | 2026-12-04 10:18:57 UTC |
| Inspected named members | Ten result JSON members and the actual Rust test log |

The normal artifact connector fetched the complete ZIP; its size and SHA-256
match GitHub metadata. Named members were inspected directly without full
extraction. The owner retains the archive, build log, identity reads and actual
inspection receipts. Artifact availability beyond the stated expiration is not
promised. The small summary and manifest remain available while repository
history is retained.

## Observed checks

The canonical verification reports passed for all 11 declared checks: Rust
formatting, Clippy and tests; locked restore, managed build and formatting;
source interop tests, compiled API/XML, package layout, isolated package
consumption and actual Native AOT execution. The basic package and native
hashes in the summary describe this gate; they are not substituted for measured
domain-package or loaded-library identities.

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
those distinct original values. Historical performance and fault/soak runs were
not rerun by these package gates.

## A20, independent inspection and limitations

The same checkout/tree has separately inspected [A20 evidence](../ci124-a20-001/README.md):
48 expected outcomes, 96 verified logs, enabled C ASan/UBSan/leak checks and
20,000 actual fuzz units. This summary binds that projection by SHA-256 and
checks source, checkout and tree agreement. Rust, CLR and Native AOT runtime
sanitizer coverage is not claimed.

The CPU8 canonical artifact inspection exited 0 in 0.117628762 seconds without
running tests or workloads. A separate reviewer compared the CI123 and CI124
inspection sources and found only identity/location substitutions; verified
source and receipt bindings; and rehashed both complete archives. No gate was
weakened. The original inspector was not rerun during that review.

CI tools and binaries remain distinct from the fixed measurement-host compiler,
locally built packages and actually loaded native libraries. No later source
change is covered. This report grants no performance improvement, long-run
duration, public domain release or other-platform acceptance. The local B18
cancellation timeout must still be diagnosed and resolved before the candidate
can enter its frozen performance screen.

The published files contain fixed roles, numbers, booleans and verified hashes.
Raw commands, logs, host paths, process identifiers and operational controls
remain outside this projection.
