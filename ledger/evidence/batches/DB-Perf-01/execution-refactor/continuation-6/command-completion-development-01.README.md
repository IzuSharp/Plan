# One-shot command completion development evidence

Final managed test source: `21fd325cc528eab720f06e681c1f5cd9aee64da2`.
Integrated root source: `d8beff6dc31f6190caaed333a28847511b7adbc5`.
No-hook independent provider assets were built at `374a253f09f47d0b42f9d18491677158287ba18b`; all product bytes in the final tested and root integrated sources are identical to that producer source. The precise comparisons are in `final-integrated-parity.json`.

## Final successful gates

- `attempts/command-completion-11`: six native gates, including actual capability closure positive/negative controls, new command completion, scalar Count at MaxBatchRows1, transactions, streaming, host review, and the frozen C ABI.
- `attempts/command-completion-12`: final new native tests, 377 default checks and 8 real PostgreSQL queued cancellation checks. A native before-work barrier proves cancel happens before any provider dispatch; an actual query proves no table side effect.
- `attempts/command-managed-05`: real Release Native AOT, command-only and full NativeHost suites both exit0 against two independent no-hook provider assets. Command-only observed 451 assertions per provider; full observed command451 SQLite /452 PostgreSQL, 438 main-suite assertions and36 genuine generic retirements, with all nested suites passing. Assertion totals are observations from each run, not a claimed fixed work count. All native owner diagnostics0..5/8/9 end at zero.
- Existing pull matrix retains exact one SQL execution, exact fetch request/ready/take/publication counts, exact final-close request/ready/take/publication counts, and zero normal generic operations for 0/1/32/64/100/1000 rows on both providers.
- Final AOT executable SHA256: `37a8b860029c98faba728da59f7cce56dca66260df00a449e622fcf7606dde44`. Its source, input manifest and both provider hashes remained unchanged across the tests.

## Failure boundaries retained

`attempt-classification.json` distinguishes actual product failures from fixture/compiler/runner mistakes. The original f8 missing-secondary cleanup failure and the bit28 query capability parser failure are retained. The PG cancellation fixture in managed03 incorrectly assumed that holding managed request return meant native dispatch had not happened; existing dispatched PostgreSQL nonquery semantics preserve the eventual confirmed write result. Final tests distinguish native pre-dispatch cancellation (zero SQL) from a real dispatched UPDATE blocked by a separately held row lock (task remains pending after cancellation intent, then confirms affected count and effect after lock release). The old pg_sleep branch was deleted.

Managed04's full-suite failure was an obsolete generic observer for session close. Final session-close checks require actual kind7/result101 accepted+ready+taken+published+fully-drained state, await real DisposeAsync and LocalResourcesReleased, and still require that the synchronous mapper remains blocked with exactly one live native result buffer. A transferred result owner is independent of the parent's provider join. Source close keeps its genuine generic retirement observer. Full classification of all TestRetirement sites is in the final attempt's retirement-observation-audit.json.

## Reproduction and scope

Original run scripts and argv/exit/timestamp records remain in each attempt. Historical CTest details are immutable copies saved during the corresponding attempt; no later LastTest.log was substituted. Final test/build inputs and all test/fix patches are included. Every source manifest is compared with its recorded git blobs in source-manifest-validation.json. Native attempts07/08/09 include hashes of then-uncommitted managed test drafts (6/6/9 entries). These files were not compiled or executed by those native attempts; all native inputs match their recorded commits. Recoverable exact later-committed draft bytes are included. Some unused probe-formatting draft bytes have only their original hashes; no managed credit is assigned to those attempts. All final native10–12 and managed01–05 manifests match their recorded commits in full. The initial archive audit correctly rejected a claim of universal clean-tree identity; its script/failure log is retained. The latest actual impact plan selects existing interop/linux plus independently validated PostgreSQL/SQLite packages; its actions contain no benchmark, calibration, profiling, or pressure workload.

This archive grants development correctness credit only. It does not grant public package, performance, final30-minute campaign, CI, or release credit. Original Fluent/Relations suites have separate receipts produced by another agent and are not relabeled as this suite. ELF/so files, bin/obj, restore caches, PostgreSQL cluster data and private certificates are excluded. Retained executable paths/hashes are recorded separately. Rebuild from the pinned sources and locked toolchain, using the supplied matching provider manifests; do not bypass the package asset hash check.

Archive metadata is deterministic (mtime/uid/gid0), with SHA256SUMS for every other member. Assembly creates the archive twice and requires byte identity, then extracts to a temporary directory and checks every file byte/hash. The external manifest includes the archive hash, member hashes, original file paths and verification results.
