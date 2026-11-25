# SQLite case 4 owner-count failure — retained failure and isolated diagnosis

## Status

The first complete candidate B regression gate failed `native.sqlite14`. The original failure remains a failure. No production source, formal binary, or test oracle was changed in this investigation. The isolated natural reproduction also exited with status 2; observing later zero counts is diagnostic evidence, not a passing result.

Formal source: `a27ff3189bd48b9c08d58e38338b2bfde7669bdd` (native source identical to candidate B `dc82792c519ee90be30f5c49b2f785ecd33ad915`). Before source: `f0078da720e07031bc56464995af6791c41aaae8`.

## Original evidence

- Complete gate log: `/workspace/scratch/17ac3f8f2fbf/managed-research/test-results/candidate-b-complete-v2/regressions/logs/native-component-regressions.log`.
- Preserved original SQLite files: `/workspace/scratch/17ac3f8f2fbf/managed-research/test-results/candidate-b-complete-v2/sqlite14-failure-artifacts`.
- Original temporary directory: `/tmp/korda-b03-cpp-51030163897688`.
- Passed scenario messages were 1, 2, 3. Failure occurred after **case 4 `savepoints()` returned**, before its PASS message.
- The immediate zero assertion checks `source_count`, `session_count`, `cursor_count`, `buffer_count`, and `operation_count`. It does not print which counter failed in the original binary.
- Formal fixture executable SHA256: `dc6cbb9353492fd2757d5d30b94a5648d389e34f18c8bfbb028ac1b80ff1a38d`.
- Formal `libkorda_sqlite_fixture.so` SHA256: `8f8bdcdbd8e427caa7e13c218c60a57a69c39a4855fb1addef80cfaaa4218f9b`.

This is independent evidence from the earlier CI abort; no causal equivalence to that abort has been established.

## Isolated natural reproduction

`prepare_diagnostic.py` copies the existing compiled fixture dependencies to `natural/original-objects`, compiles only a diagnostic copy of `fixtures/sqlite.cpp`, and links to a new shared library in the same scratch directory. The production `host.cpp` object, provider, query, contracts, and SQLite objects are reused without source or object modification. The existing fixture executable is copied and resolves the isolated shared library through an explicit `LD_LIBRARY_PATH`; `natural/ldd.log` records resolution.

The fixture runs the existing `savepoints()` case up to 300 times, with a separate database per round. It retains the original immediate zero predicate, records the exact sampled counter values used for that predicate, and observes weak references only after a failure has already been recorded. It never waits to turn a failed zero predicate into a pass.

At zero-based round 289 (the 290th case), the predicate failed:

| Observation | Value |
|---|---|
| Source / Session / Cursor / Buffer / Operation counts | `1 / 1 / 0 / 0 / 0` |
| Transaction strong count after weak lock | 2, including the diagnostic observer |
| Transaction state | `retired=1`, `primary_ready=1`, `finishing=0` |
| Session state | `retired=1`, `active=0`, `connection=null` |
| Source state | `retired=1`, `leased=0`, `pending=0` |
| After a bounded observation loop | All five counts 0; transaction weak reference expired |
| Diagnostic exit status | **2 (failure)** |

The observer had no retained strong references before the failed snapshot. Each diagnostic weak lock is released before the subsequent observation loop. The 100 ms bound is used only after the failure to distinguish a persistent leak from delayed destruction; it is not a new test acceptance rule.

Artifacts:

- `natural/run.log`
- `natural/run-receipt.json`
- `natural/build-manifest.json` (all compile/link arguments and reused object hashes)
- `natural/instrumentation.patch`
- `natural/run-artifacts/korda-b03-cpp-51557449807711`

Diagnostic fixture SHA256: `0f7c06f5323d8d4570d39abbc804dd77192522a08ea55d9b521ac1b51608b016`.

## Source explanation and limits of the current evidence

The actual source provides two retained-reference windows:

1. `Transaction::finish()` and `schedule_cleanup()` start a detached lambda capturing `self` and `gate`. `finish_worker()` sets `retired=true` and notifies before returning; the lambda releases its captures only after that return.
2. `finish_worker()` starts a second detached lambda capturing `self` for `deadline_worker()`. The deadline loop exits after it observes `retired`, so scheduling may retain this owner after another waiter has already observed retirement.

`Transaction::join()` waits only for `retired`. `Source::join()` waits for its lease/pending counters and joins its admission, worker-pool, and control-pool threads; it does not join these detached transaction threads. Therefore successful joins can precede destruction of the final transaction/session/source references even when the provider connection has already closed.

The natural reproduction establishes a short retained transaction reference after cleanup and a matching counter failure. It does **not** identify which of the two detached lambdas held the last reference in that particular run. `gated_diagnostic.py` was prepared to pause each exact lambda epilogue separately, after its member function returns and before its existing captures are released. It had not been compiled or run at this checkpoint because the root agent began a quiet B/C measurement window. That pending gated experiment must not be described as passed or as executed evidence.

The entire implementation section from `TransactionOptions::parse` through all Transaction/Savepoint methods is byte-identical between f0078da and a27ff31: 20,814 bytes, SHA256 `c4831377ddaa94659f8c8afcab028a73d416f00043000d6aa6feaf7fdf11f0d5`. See `transaction-source-comparison.json`. This proves the relevant source pattern predates B; it does not establish a baseline failure frequency or prove that altered execution timing had no effect on exposing it.

Fixed sources:

- [Candidate transaction implementation](https://github.com/IzuSharp/Korda/blob/a27ff3189bd48b9c08d58e38338b2bfde7669bdd/native/cpp/src/host.cpp)
- [Before transaction implementation](https://github.com/IzuSharp/Korda/blob/f0078da720e07031bc56464995af6791c41aaae8/native/cpp/src/host.cpp)
- [Case 4 and immediate owner oracle](https://github.com/IzuSharp/Korda/blob/a27ff3189bd48b9c08d58e38338b2bfde7669bdd/native/cpp/tests/fixtures/sqlite.cpp)

## Repair design for review — not implemented

If the intended Join guarantee includes release of the final background transaction accessors, mirror the existing `Cursor::Completion` approach with an **independent completion ticket**:

- Keep `primary_ready`, Unknown/Committed/RolledBack, deadlines, cleanup outcome, and internal `retired` transitions at their existing semantic points. Primary completion must remain independent of final retirement.
- The finish and deadline lambdas each retain the independent ticket. Each signals its own completion only after releasing its transaction reference; the finish lambda must also release its retained `CommandGate`/Session reference first.
- The ticket publishes complete after both accessors have relinquished ownership. `Transaction::join()` waits on that ticket rather than only on the internal provider-cleanup state.
- Audit `wait_close()` and public `snapshot().Released` so a receipt never claims the stronger completion guarantee before the ticket is complete. Internal session/transaction admission checks may still require the earlier cleanup state to avoid a dependency cycle.
- Audit Source/Session close paths that do not explicitly call `Transaction::join()`. Fixing only the explicit case-4 helper would leave a possible parent-join gap if the public contract promises all descendant accessors have finished.
- Preserve the separate primary and cleanup time budgets and late Unknown monotonicity. A caller timing out remains a waiter outcome, not permission to release a live native accessor.

A weak capture alone is insufficient: locking a weak pointer for the worker method still retains a strong owner until the method/lock scope exits. Setting one more member flag before that strong reference is released has the same publication race. Moving all transaction work onto the general worker pool is a larger scheduling change and requires independent deadlock/admission analysis.

An alternative is a joinable deadline thread owned by the finish worker plus one external completion ticket for the finish lambda. That reduces the number of ticket participants, but its exception/stop path needs explicit treatment; a destructor that joins a timer still waiting for `retired` can deadlock on exceptional exit. Neither design has yet been implemented or tested here.

If the project deliberately defines retirement as provider-resource completion while allowing detached wrapper references to linger, the fixture's immediate zero assertion may be stronger than that contract. Changing it to eventual zero would be a conscious oracle/contract decision, not a fix demonstrated by later zero counts. The current task does not assume or make that change.

## Necessary validation after a chosen repair

1. Deterministic finish and deadline epilogue gates: Join must remain blocked until the chosen completion boundary, while primary result/deadline behavior remains unchanged.
2. Explicit transaction Join and parent-only Source/Session close, including dropped public transaction owners.
3. Unknown commit, failed rollback/recovery, pending cursor gate, timeout without abandonment, and original-error precedence from existing transaction tests.
4. The retained SQLite 14-case fixture with its original zero oracle and the complete candidate gate at the actual repaired source/image identity.

No new performance claim follows from this investigation.

## Implemented isolated correction and final targeted validation

The subsequent correction is isolated in `/workspace/scratch/17ac3f8f2fbf/worktrees/DB-Exec-02-retirement-fence`, branch `task/DB-Exec-02-retirement-fence`. It does not modify the frozen B checkout or binaries.

- `edca9bf42c18227da09a22faf517a461847ec69a`: independent transaction and Source retirement fences; exact worker-epilogue/parent/destructor/launch-compensation tests.
- `4c6f1888badbe4446fe4526c77cb9e88da030b9c`: preserves the old `gate->dispatched` happens-before deadline-worker startup, with a blocked-dispatch/expired-deadline oracle. This is the source identity of the completed targeted validation.

Both counters start at zero and count actual worker tickets. Two prepared threads wait on an independent startup gate, so a partial launch failure releases its registered participants without entering Transaction methods or publishing `finishing`. Each worker releases CommandGate and Transaction ownership before completing either independent ticket. Explicit Transaction Join/public Released waits for its own fence. Explicit Source Join waits for its descendant fence after lease/pending admission has drained and before stopping worker pools. Internal provider cleanup, COMMIT/Unknown results, lease return, and Session Join retain their earlier boundaries.

The Source destructor intentionally does **not** wait this fence. Its final reference can be dropped by the worker that still owns the ticket. The explicit Join caller retains Source throughout its wait; the independent ticket does not retain Source. The tests exercise both paths, including a held epilogue being the only remaining Transaction→Session→Source chain.

The later deterministic pre-fix epilogue experiment ran both modes: after `finish_worker()` return and after `deadline_worker()` return. Each failed immediately with `source/session=1/1`, closed connection/zero lease, then cleared only after the held closure was released. Both receipts retain exit 2 in `epilogue-gates/{finish,deadline}`. These remain negative evidence.

At **4c6f188**, the isolated corrected candidate passed:

| Correctness gate | Result |
|---|---|
| Native SQLite retained 14 scenarios, including actual case 4 held at both worker epilogues | 140,257 assertions |
| Native transaction lifecycle, old failure/Unknown tests plus new retirement/startup/dispatch cases | 120 checks |
| Natural case 4 loop, unchanged immediate zero-owner predicate, no epilogue hold | 300 / 300; 4,800 assertions |
| Real PostgreSQL/SQLite provider tests | 183 checks, zero failed cases, `postgres_verified=true` |
| Real PostgreSQL fixture | All 11 original groups |
| Real PostgreSQL protocol/response-loss/Unknown tests | 325 checks |

The 300-round loop uses a separately compiled diagnostic fixture with the **unaltered corrected production objects**. It is correctness evidence, not a performance benchmark or package consumer. Its fixture SHA256 is `e862dfa4ab3bc55982934246814b3606aa138163ddf8dcbe35e64a1d74260bdc` and executable SHA256 is `49494ae125a443b6e8e78e5dc302ff46bb4dc6e5303aaa6fae275818a4f9b26e`; all rounds and immediate zero checks passed. The three task-owned PostgreSQL servers were stopped successfully in the same runner invocation.

Complete source/binary/log custody index:
`/workspace/scratch/17ac3f8f2fbf/worktrees/DB-Exec-02-retirement-fence/artifacts/retirement-fence-validation-index.json`.
Logs and receipts:

- `artifacts/retirement-fence-4c6f188-native-details.log`
- `artifacts/retirement-fence-4c6f188-pg/{manifest,commands,summary}.json`
- `fixed-natural/{build-manifest,run-receipt}.json` and `fixed-natural/run.log`

This clears the identified defect for the isolated corrected source under these gates. It does not retroactively pass candidate B, constitute the final merged whole-path/package gate, or claim any throughput/allocation improvement.
