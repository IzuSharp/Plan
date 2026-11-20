# Perf-01 DB phase diagnostic 001: source-gate failure

The first **diagnostic-only** baseline build attempt stopped at its Clippy gate.
Formatting passed; Clippy returned **101** because two `SQLITE_TRACE_PROFILE as u32`
expressions cast a value to its existing `u32` type. The unchanged deny-warnings
policy rejected both locations in SQLite configuration, at lines **132 and 269**.
No lint allowance, timeout or assertion was weakened.

| Actual command role | Outcome | Exit code |
| --- | --- | ---: |
| Overlay formatting gate | Passed | 0 |
| Overlay Clippy gate | Failed: two unnecessary casts | 101 |

The attempt began at **2026-11-20 14:17:45.618408 UTC**. Clippy's process-group
owner finished at **14:19:05.285504 UTC**; the outer failed-stage receipt finished
at **14:19:05.293309 UTC**. Both owned process groups and all adopted descendants
retired, with no cleanup signals or adopted-cleanup errors. Original command
outcomes, timings and log hashes remain in the numeric checklist.

## Exact failed-source identity

| Diagnostic role | Unmodified product parent | Diagnostic child | Diagnostic tree |
| --- | --- | --- | --- |
| Before, source gates actually attempted | `ea5fa528035d025bd7a28698ee7c71194432236c` | `ffd2c0e798cb5ca2fac542bce39df4bd177b8f45` | `6515d491f5ac4f0f654b4bc296d5a5c3263be8b9` |
| Final, bound but never executed | `2e3995df8d86583ee9443348276ca8d918056bfc` | `e01fc07112d0823b8db2b24e29f22dadb02268a4` | `abb0d7dae8cd2c1651ab1a6778819fef5edfe4a1` |

The frozen preparation remains Plan commit
`88d16c14cad2440cf78e87f4936b18db639cc3f1`, execution source index
`a953baab0721a5ff6748e74d03e5ec26f0d7b964e1acd0d9feeb947f4657516d`.
Its original sources, child commits, outputs and failed receipt remain unchanged.
The actual two-role source binding is
`f0eb6318bf6b9414131ef0daafb824e3b562dd923db3f6598593bb3d598f9e61`.
These are separate instrumentation children; the retained shipped product and
frozen formal drivers were not modified by this diagnostic failure.

## Scope and next evidence boundary

Exactly two source-gate commands ran. **No provider regression, diagnostic native
producer, package producer, application producer or measurement command ran**;
the final-role pipeline never started. Clippy may check/compile dependency
metadata, but it is not a completed native/package producer. This attempt yields
no database phase measurements, correctness acceptance, performance comparison,
capacity result or long-duration credit.

A minimal separately prepared diagnostic 002 correction is pending at the time
of this record. It must use fresh source identities and outputs, and earn its own
actual source/producer/measurement results. A future 002 success must not rename
or replace the failed 001 evidence.

## Retained evidence

[public-summary.json](public-summary.json) contains fixed roles, numbers,
booleans and source/log hashes; [manifest.json](manifest.json) binds both public
files. The complete original failed owner receipt has SHA-256
`48fee8de0054e7325691e375876014c78097fabf0cfd2135e8f8f8861e78d338`. The Clippy stderr log has SHA-256
`56214252b86638be6832a4e970baf7773f9e22e8299e704ffd70ba0060872612`.
The exact original owner and adopted-descendant helper hashes are also retained.

The projection read only the small failed receipt, original logs, source index
and actual source-binding metadata. It matched both original exit codes and
retirement records and the two diagnostic locations. No source executor,
compiler, test, raw measurement reader or workload was replayed. Public data
contains no raw command, environment, host path or process identifier.

Original operational records remain privately retained under the diagnostic 001
run, while this synthetic checklist remains in Git while repository history is
retained. No remote raw-log archive or private-workspace retention period is
promised.
