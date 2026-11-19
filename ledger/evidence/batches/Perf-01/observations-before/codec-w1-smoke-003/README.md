# Before-only codec W1 smoke, package before-003

This records root's completed smoke and a later read-only evidence audit. No
workload, test suite, extraction cohort or long acceptance was run by this
review. The exact original metadata and resource samples are copied here;
`audit.json` pins them and the original operation/event ledgers.

The target used one worker at a planned 134 operations/s, the complete frozen
mixture, target CPUs 2,3 and generator CPUs 0,1. It started measurement at
2026-11-19T11:00:08.712639+00:00, ended observation at
11:00:18.887999+00:00, and closed at 11:00:34.957897+00:00. The measured dispatch
span was 10.105096397 seconds; effective scheduled load was 10.104478198 seconds.
Warmup, recovery and five seconds of idle observation were separate.

All 1,355 offered measurement operations were admitted and completed correctly;
the raw outcome, terminal status and target status are all `ok`. Whole-measurement
arrival p50/p95/p99 were 1.550745/95.450964/110.687603 ms. Maximum measured dispatch
lag was 29.997771 ms, below the fixed 100 ms bound. Successful observed throughput
was 133.1562681355582 operations/s over the completion-observation denominator;
the planned rate remains 134/s.

All declared smoke bounds passed. Across all 47 resource samples the maximum
sampled target RSS was 104,849,408 bytes, below 256 MiB, and every target/generator
thread mask stayed within its assigned pair. Whole-process measurement CPU was
4.35 seconds, or 42.747584235400616% of one core. Target file descriptors stayed
at five. The final RSS sample was 60,952,576 bytes versus 48,562,176 at startup;
this is not a claim that allocator memory returned to the initial level.

Warmup completed 2,695/2,695 and recovery 12/12 successfully. The drained record
and all five idle records have zero native live owners, retained capacity,
active calls and errors. The process exited zero and the controller restored
all recorded thread affinities to CPUs 2,3.

The frozen source is ea5fa528035d025bd7a28698ee7c71194432236c. The plan records
the actual before-003 manifest, A21 and loaded native library hashes, matching
the [build receipt](../../builds/before-codec-003/README.md). This passing smoke
selects W1=134/s for 120-second full short cells, as recorded in
[the selection decision](../../codec-short-selection-linux.md). W2 remains
268/s for 60-second cells. The smoke is excluded from both noise triplets and
confirmation cohorts: 1,355 total successes and eight in the rarest row do not
meet the required 16,000 total and 100 per row. It earns zero long-duration credit.

The original raw ledgers remain at
`ROOT/perf01-evidence/smoke/before-codec-w1-003`. This commit retains small metadata
and resource samples in repository history without a task-specific expiry;
it does not claim that raw ledgers or binaries were uploaded.
