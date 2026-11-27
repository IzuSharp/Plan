# DB-Exec-Parity-01 · relation clone selection · recovery 03

Status: measured diagnostic selection, before any candidate product edit. This is a newly recovered experiment. It does not recover or claim the missing earlier Query.Binding/Relations test results quoted by the user.

## Identity and scope

The clean product candidate worktree remains `origin/main` (`7ff7b57b907b689defb880b8af62d83679608603`). Diagnostic source is `4376c54` on `task/DB-Exec-Parity-01-relations-diagnostic-recovery-03`; first-layer source was `ac5cc94`, with the receipt eligibility correction at `b1688dd`. The local managed-only packer verifies original baseline package archives, every unsigned entry, dependency/native source input hashes, and native ELF hashes before reusing identical native bytes. It does not alter a product validation tool or rebuild the native image. The native SQLite SHA is `7b5291667a731d2b48647079ced0588003ba3d6c0f9edfb2648e3e581c2f0c53`; PostgreSQL SHA is `1909e79db9265f9da2d2b22073090e03c06989fcd4af06ba656a493bce047fed`.

Runs are actual Release Native AOT, 32 warmup operations then 128 measured related32 operations, one connection, same 32 composite input keys, 53 child rows and digest `2847736615530494015`. Every business operation performs exactly one SQL statement; PostgreSQL reports four existing protocol submissions and SQLite zero. Success is 128/128, business/oracle failures zero, all final native owners zero. Every counted allocation span starts and ends on the same OS thread; no span crosses an await. Thirty-two empty prewarmed controls each allocate zero bytes. Scope records and whole-process total use separate boundaries; nested scopes are not summed twice.

Parent authorized allocation/count diagnostics while other builds may overlap. All these receipts are marked `TimingComparisonEligible=false`; timestamps and thread CPU are diagnostic correlation data, not ordinary latency/CPU comparison evidence. Parent's newly matched `-g` native baseline/candidate comparison is a different native identity and must not be subtracted from these data.

## Observed allocation boundaries

Each figure below is per one related32 business operation, after warmup. Exact values were identical across all 128 observations unless stated as a median/mean. First-layer dual-provider observations establish shared work before selecting this managed path.

| Disjoint phase | SQLite bytes | PostgreSQL bytes | Calls/business |
|---|---:|---:|---:|
| Input validation and key snapshot | 280 | 280 | 1 |
| One result projection construction | 4,864 | 4,864 | 1 |
| Fresh branch/context construction | 51,712 | 51,712 | 32 |
| SelectParent, median | 331,264 | 331,264 | 32 |
| Combine | 181,760 | 181,760 | 31 |
| ToList synchronous prefix, median | 95,640 | 95,640 | 1 |
| Grouping after await | 2,896 | 2,896 | 1 |
| Branch/final disposal | 0 | 0 | 32 |
| Whole process, first-layer mean | 685,850.0625 | 685,916.6875 | 1 |

SQLite second-layer instrumentation selected the largest phase and Clone nested in Combine. Whole-process mean is 685,842.125 B, disjoint scoped mean 669,294 B and remaining process residual 16,548.125 B. The residual includes unobserved framework, DTO and harness work; it is not attributed entirely to any one component. No zero-framework-allocation claim is made.

| Nested phase/event | Actual calls/business | Actual allocation or copied bytes/business |
|---|---:|---:|
| Clone inside Combine | 31 | **120,776 B allocated**, exact across 128 operations |
| Clone tape ToArray copy | 31 | **54,932 payload bytes copied** |
| Import metadata/checks | 31 | 11,160 B allocated |
| Import append | 31 | 17,152 B allocated |
| Tape growth Array.Resize | 98 | 63,488 old-capacity bytes copied; 126,976 new-capacity bytes allocated |
| Other tape payload CopyTo | 542 | 51,008 bytes copied |
| Key value wire encode | 64 | 27,648 B median |
| Key predicate composition | 64 | 78,848 B |
| Key WHERE clauses | 64 | 66,560 B |
| Projection expression array/construction | 32 | 78,336 B median |
| Selection | 32 | 75,520 B median |

These are actual event counters adjacent to the executed copy or resize operation and same-thread allocation measurements, not source-level multiplication. Value's 37,632 B is nested under predicates/projection and must not be added again. Clone is 17.6% of current whole-process allocation, not the entire relation problem. PostgreSQL second-layer confirmation is next; its first-layer 31 Combine calls and 181,760 B already exactly match SQLite.

## Proposed single causal hypothesis and narrow product boundary

Hypothesis: each of the 31 private temporary relation branches is already owned solely by `LoadRelatedAsync` and disposed immediately after Combine. Transferring that command graph into the destination instead of cloning its full command and validation containers can remove exactly 31 Clone calls and 54,932 tape-copy bytes. Allocation reduction is predicted at approximately 120,776 B/business, subject to any added bookkeeping. All other construction, metadata, union clauses, key snapshots, validation and execution work remain selected as-is for this experiment. No template/cache, row mapper, codec, native scheduler, or public Combine change is bundled into this hypothesis.

Proposed internal-only entry point: `QueryBinding.ConsumeAndImport` (name provisional), reached through internal `QueryContext.ImportConsumed` and `QuerySelection.CombineConsumed`. The sole product caller is the `using (var next = From(...))` branch in `RelationBatch.cs`. Public `Combine` continues to call `SnapshotAndImport` and retains its independent mutable-source snapshot contract.

Ownership and commit sequence:

1. Check same source and reject self-transfer before mutation. Acquire both existing fail-fast gates; never wait while holding one. Require buffered command composition on both ends. Direct ABI, missing/expired source, or unsupported owner states do not fall back to a different path.
2. Validate current source selection via its QueryContext and keep its context/binding admitted. Do not alter input snapshot behavior: `parentKeys.ToArray`, value wire copy, parameter metadata and existing query-origin retention all remain unchanged.
3. Invoke the existing command-level SnapshotAndImport using the source command object under both gates. It retains the source graph, validates source selection/seal state, builds metadata, checks source, finite budgets, parameter collisions and record capacity, and performs ImportAppend plus imported metadata updates. On any exception before the full method returns, **do not consume the source**. Existing command compensation releases its temporary retained reference and removes dependency/fixup staging; existing semantic budget/identity failures occur before append. Tests must exercise those failure points and then use both source and destination. This proposal adds no new claim of recovery from process-wide out-of-memory failures beyond the existing implementation.
4. Only after the complete command import has returned successfully, mark the source binding disposed using its existing atomic admission flag. This is the commit boundary, later than ImportAppend; the destination has a durable retained dependency. The source gate's normal exit releases its original binding reference. There is no allocating/fallible action between successful import and source invalidation. Mark source context sealed so no borrowed selection is reusable. Source Dispose is then idempotent.
5. Keep the existing parameter-definition merge and union clause validations. If a later union clause or outer relation operation fails after transfer, the source remains consumed, and the private caller's existing `finally`/`using` and root-query catch dispose both owners. The destination owns exactly one dependency and releases it once. This is an internal consuming operation; public Combine never takes this path.

The source binding remains intact for pre-commit quota, source, projection, direct-mode and concurrent-use failures. Successful transfer intentionally invalidates only the private temporary source. Destination/source public API usability and snapshots continue to be verified through existing public Combine tests and new internal targeted tests. A concurrently requested source Dispose remains governed by existing admission/deferred release; a transferred graph remains alive through the destination retained reference.

## Verification and acceptance before retaining candidate

- New Query.Binding AOT tests: byte-for-byte equivalent submitted envelope/rendered SQL to existing clone-import path; frozen literal input after caller mutation; public source still reusable after public Combine; source unusable after private transfer; source and destination usable after pre-commit finite-budget failure; self/cross-source/direct-mode failure; concurrent-use gate failures; idempotent disposal and no native owner leak.
- Existing Query.Binding suite with independent C++ fixture (built from main, no product/native change) and existing Relations suite as real dual-provider Native AOT executables. Relations covers key-input snapshot, duplicate positions, composite/null keys, native collation, one SQL/nonempty and zero SQL/empty, shared row budgets, mapper exception identity/session reuse and cancellation.
- Reapply identical diagnostic scopes to the candidate under a distinct source identity: Clone31 → 0 and CloneCopy54,932 → 0, no extra SQL/protocol messages, unchanged 53 rows/digest and owner release. Record allocation delta; no timing credit.
- Build uninstrumented baseline and candidate managed packages using exactly the same verified native bytes and toolchain. Request an exclusive local measurement window from root for interleaved A/B (including reversal); only ordinary runs may support CPU/latency benefit. Parent's integrated native candidates require their own later matched-identity validation.
- Stop/abandon if ownership semantics fail, observed Clone work does not disappear, ordinary measurements show a regression, or benefit cannot be repeated. Report remaining SelectParent/From/ToList allocation instead of claiming zero extra managed allocation.

## Raw and derived evidence hashes

| Path relative to task root | SHA-256 |
|---|---|
| `experiments/relations-recovery-03/first-layer/sqlite/run/analysis.json` | `6972f8066f2a53728641920d04559124cbb08a9a1c07483650a5210fbf29c003` |
| `experiments/relations-recovery-03/first-layer/postgresql/run/analysis.json` | `b2fc6f71a2495f25aa0dee79cb10c82f285861dd31a934c7152b3416de7923dd` |
| `experiments/relations-recovery-03/second-layer/sqlite/run/analysis.json` | `f576e7aee93ca6f6f057467296bebd566bdc3d286c17cc6ca4cfe9f6d124762e` |
| `experiments/relations-recovery-03/second-layer/sqlite/run/receipt.json` | `7fffc250ed095f249c96e11881240690444224a7707e6dd8f8ac7e9da23fa91f` |
| `experiments/relations-recovery-03/second-layer/sqlite/run/receipt.json.relation-scopes.csv` | `9bf316f93baa4efea60438a3e620b0a14d54c7683b629819fc701859fb9c1f2e` |
| `experiments/relations-recovery-03/second-layer/sqlite/run/receipt.json.relation-status.json` | `edbc4377849dc21c8303321d58533b98aecbd38832cc7df683ffa5584b3dd241` |
| `experiments/relations-recovery-03/second-layer/sqlite/consumer/out/DbPerf.Korda` | `018de4c35ad952f178d97c08e42163fe9bceef07ee788af48fa9afb2a97c1cc5` |
| `experiments/relations-recovery-03/second-layer/sqlite/consumer/out/DbPerf.Korda.dbg` | `d988450803c14c6a8806e8a2b32fa954ae8c58e9d5a41b78c1e81909c434d76e` |
| `experiments/relations-recovery-03/second-layer/sqlite/package/build-receipt.json` | `1510ae92d3919d1b214ceab9c430a4a27420f1b133143f7278e449f3f020e390` |
| `experiments/relations-recovery-03/pack_managed.py` | `b8e45f3b7b63f1ac56053761ca0af237e210f95b20bcefdb86cdf8f3cb0fa852` |
| `experiments/relations-recovery-03/analyze_scopes.py` | `48014c556a1bc314b045827d27afe150bbec16e7568f90725dd9283ad57b614a` |
| `experiments/relations-recovery-03/run_related.py` | `f529f21980ce611135f69037d04095e4951e8249d61c28f40f72393c291bb446` |
