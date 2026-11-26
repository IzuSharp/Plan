# Continued causal experiments and current decisions

This checkpoint continues the completed measured Stage1 gate. No final parity or
1800-second acceptance is claimed. The main Korda task worktree is still the
unmodified7ff7b57; experimental product trees are isolated and source-bound.

## Completed evidence and selection scope

| Candidate | Causal observation | Ordinary endpoint evidence | Current disposition |
| --- | --- | --- | --- |
| Common completion-tail A | Actual registered-before continuation becomes contained in setter after the last coordinator bookkeeping; native callback never consumes the row | Two interleaved rounds do not show a stable thousand-row CPU/latency gain | Do not integrate this complexity on the available endpoint evidence |
| SQLite v3 prepare flags A | Same engine VM/step/SQL work; lookaside becomes usable. Actual Host allocator has repeatable lower counts/bytes in numeric32, text32, wide32 and early stop | No stable narrow1000 endpoint improvement; exact32/mixed still require combined regression checks | Retain as a resource optimization subject to final mixed acceptance |
| PostgreSQL no-op cancel hooks A |1002 installs become0 without changing per-row checks; closures use SBO, so no1002heap-allocation claim | No stable ordinary endpoint gain | Not selected |
| Scoped read lease B | Per1000 query1032 redundant Release(0)/Monitor entries removed, actual owner release unchanged;531 AOT assertions pass | CPU reduction reverses between SQLite rounds and is not present in PG | Not selected as a performance change |
| PostgreSQL decimal configuration B | Per1000 decimal values JSON parses4000->0, validations3000 unchanged, decode public malloc/calloc48000->1000, requested bytes1135980->3980 | Two quiet reverse ordinary rounds CPU7875/7889us->5348/5098us and p506553.6us->3604.48/3571.71us | Retain for the measured decimal path; still8.5x Dapper CPU in that case, not parity |
| Ready-row C | Existing count evidence identifies968 ready batch-local rows per1000. Smaller guarded state preserves the async builder context boundary; plain sync mapping and FromException(OCE) shortcuts rejected | AOT tests/build and ordinary comparison are separate gates; ongoing at this checkpoint | Pending actual causal A/B |

The PG decimal result does not imply every query improved. Money1 CPU is unchanged
in reverse round; customer-totals reverse-round CPU is15.2% higher. Integer-control
CPU is almost unchanged, but its p50 increases4.6–7.9%; SQLite wide p50 increases
3.9–5.9%. These short256-operation/two-round cells are screening evidence, not proof
of universal non-regression or long-run p99. The combined ordinary mixed campaign
must disclose and resolve material remaining regressions. Decimal validation/error
order, mutable-input handling, PG OID/profile checks and SQLite id13 rejection are
unchanged; malformed/noncanonical configs retain the original JSON fallback.

## Failure preservation and equal isolated warmup

codec-b-ordinary-01 aborted when Dapper's --verify all35 warmup ran the related
contract with rows1. That generated contract requires exactly32 parent keys. The
candidate did not cause the failure. Attempt02 uses the same selected-case warmup64
and256 measured operations for baseline, candidate and Dapper. Each operation still
unconditionally validates rows/digest and the sticky correctness oracle. Only the
all35 precheck is omitted for isolated non32 cases; mixed35 keeps rows32/batch32
and the full --verify precheck. Attempt01 is retained and receives no A/B credit.

## Zero-refusal costs and measurement-tool control

The new matched GC-metrics baseline consumers execute the unchanged mixed35/SQL/
schedule with one added cumulative GC-pause value at existing ProcessReading
boundaries. Both implementations receive the same transform; actual AOT probe and
stuck-zero negative control passed. No forced GC exists in ordinary consumers.

Each realDB baseline cell ran30s at200 offered/s, all6000 operations succeeded,
no rejections, business errors or retries, all35 covered and owners returned.
Client process CPUus/success: SQLite Korda2841.90/Dapper2239.59; PG2907.61/2229.50.
The separate10s empty-driver controls use precomputed results and execute no
measured SQL. Their CPU is1904.83–1957.06us/control completion. The original producer
spins when its scheduled deadline is within2ms, explaining a large tool component
at200/s. Do not subtract empty controls to manufacture pure framework CPU: they do
not reproduce real asynchronous I/O, wakeups, scheduling or result work. All process
CPU/allocation/GC measurements retain their whole-process scope.

GC pause delta in the realDB30s cells is62.610/20.328ms (SQLite Korda/Dapper) and
61.131/37.366ms (PG). These are process cumulative endpoint deltas, not per-business
or framework attribution. Long peak/released RSS and steady capacity remain pending.

## Remaining measured targets

The original168 isolated-case measurements identify an additional concentrated
managed allocation: related32 uses686326/686278B per Korda business (SQLite/PG),
versus74274/51243B Dapper. Its simple equal35 weighting is17.5/18.1KB excess per
mixed business, close to the observed mixed gap. This weighting prioritizes a
source/diagnostic investigation; it is not exact concurrent attribution. Read the
relation-batch construction path and measure synchronous boundaries before any
product change. Input snapshots, duplicate-key positions, native collation, one
SQL statement, bounded groups, DDL metadata and failure order remain mandatory.

A separate source-only feasibility review examines execution on an admitted managed
worker after leaving the caller. Existing Async forbids initiating-thread native
waits; it does not alone prove a worker strategy safe. The current ABI always posts
the native executor, so merely blocking on it from ThreadPool cannot remove the
handoff. Any further experiment must preserve source admission, queue capacity,
cancel/generation fences and the declared EngineLocalAsync behavior. No such
execution rewrite is selected or implemented at this checkpoint.

## Evidence durability and resume

The previous baseline/Stage1 archives are now remotely published in Plan commit
21d2ad79a90beb74a20699ac1dfd2247ce054954, exact tree606322ee0e1f43db7ced2bf5d81731ef7b9844fa,
125verified blobs. New Stage2 raw/actual artifacts remain in the named task workspace
and will be included in the next source/artifact archive; the copied summaries here
do not claim those new binaries are already remote. See live-recovery.md for exact
worktrees, identities and command locations. Preserve failed attempts and original
actualELFs, generated C#, native images and symbols. FinishedPG fixtures are only
replaced by member-by-member verified lossless archives, never discarded.

Next: finish ready-row A/B and the two measured-target investigations, integrate only
supported changes, build/validate the actual combination, freeze the ordinary
GC-metrics consumers, run zero-refusal costs and pressure ramps incl historical
SQLite3000/PG3600 andqueue64, then supplement before data and run the required four
serial1800-second mixed35 cells. No profiling/benchmark/load is added or invoked in
CI; final committed product diff must pass and explain the existing impact planner.
Normal review/merges/release/public NuGet AOT acceptance and final report remain open.
