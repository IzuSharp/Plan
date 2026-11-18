# B23 Linux checkpoint

## Current continuation — 2026-11-18

The user-scoped B22 Linux gate has closed: both frozen 30-minute provider rows
and final 60-second idle observations passed independent review. The user
deferred 24-hour/72-hour execution; those rows remain unexecuted and do not
block this scoped continuation.

The independently reviewed finite operating-point plan started at
2026-11-18T14:01:25Z under `/root/b23_finish`, retained exec `97908`. Its exact
request SHA-256 is
`d11abdbc8e01bd0180e9a9bb556db227c9599706eba56b5a89bc663f145f67ff`;
all 169 input hashes matched before launch. The controller remains
`94060930b06d1da8978c0b71e1b8caa94abd7ec0`. The active launcher record is
`ROOT/task07-b23/root-launch-retirement-f889/launch.json`, with the execution
receipt in the same directory. Cohort state is
`ROOT/task07-b23/operating-point-cohorts-retirement-f889/cohorts.json`.

The plan bounds search to 72 processes, calibration to 198 and eligible
confirmation to 198. Failed and unsupported cells remain explicit report
outcomes; no outcome-driven retry or threshold change is allowed. B23 owns
the exclusive local timing window. Original 200/s adverse results remain
unchanged and are not relabeled by a lower-rate observation. B24 implementation
continues to wait for the completed, independently reviewed B23 report.

The [completed search checkpoint](finite-search-b593/search-checkpoint.json)
records all 72 valid processes and eight completed units. Selection ended at
2026-11-18T14:10:46Z and froze profile
`baae204fa8dd662b7bcd3584427b68d175712493d77798443d917b8b4125dd1b`.
The 30-case matrix is now running. The
[existing continuation rules](finite-search-b593/continuation-semantics.md)
describe how to follow a surviving run or resume only a safely closed boundary;
an unknown executor ID does not prove termination, and an interrupted invocation
cannot be silently retried or adopted.

## Historical checkpoint — retained unchanged

The ordinary three-route implementations, profile/controller, diagnostics and
reporter are complete. Final B23 acceptance remains gated by B22 correctness and
all declared durations. The batch handoff records exact worktrees/commits/PRs.

The immutable accepted NativeWeave AOT application is compared with a standalone
managed NativeAOT Kestrel/ADO.NET executable and direct Rust SQLx/SeaQuery/Axum.
Each comparator passed six provider/transport readiness cells:127 checks per
managed cell and126 per Rust cell,1518 total. Sources, locks, compiler/package/
native/executable hashes and limits are in `comparators-final-001/manifest.json`.
No comparator is substituted for the NativeWeave product host or DB engine.

The full controller functional preflight at e85bc13 passed66 cells, covering
three ordinary routes, both databases, HTTP1/TLS/H2, nine product diagnostic modes
and matched minimal/DI queries. Its report/raw archive remains expressly
functional. Correction92f9e6b pins TLS and PostgreSQL executable bytes and checks
the full attachment DTO. All nine affected stream/TLS/PG cells passed, with
independent source/raw contract closure. See `functional-review-003`,
`independent-contract-review` and `independent-review/pre-measurement.json`.

The first isolated timed calibration/confirmation window has now started with
frozen92f9e6b sources/profile/artifacts. Planned calibration198 fresh processes
(66 supported cells x3 independent repetitions); confirmation requires all
calibration cells valid and complete matching frozen bands. Root coordinates
no competing application/fault/soak/build load. Exact live invocation/progress
is under ROOT/task07-b23/timed-window-001.json and calibration-001. Results are
still pending; no speed or memory improvement is asserted by this checkpoint.

Fixed raw ADO.NET queries, startup migration/runtime differences and unavailable
native allocator/FFI/copy attribution remain explicit. Unimplemented comparator
DI/diagnostics/overload/fault/maintenance profiles are not advertised as equivalent.
Functional failure, unequal inputs or generator saturation invalidate a cell.
B22 and B24 remain separate gates; Linux data do not establish other platforms.
