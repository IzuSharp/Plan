# B14 independent review and focused retention correction

The independent read-only review covered fa4badc8195e69f0e606970a4bc8a8671842bf51 against the exact Plan B14 task and pinned Design database.md, including §9.2.1, mutation control kind4, complete keys and concurrency tokens, and bulk outcome/error rules. Scope: Orm.Relations, native/database/relations, compound DataSession/DataTransaction admission, and BoundedJsonEncoding.

## Finding B14-RELATION-CURSOR-DEPS

The Created relation operation retained RelationLoad until execution transferred a cursor, but the cursor retained copied shape/provider values rather than the exact relation and projection dependencies. Design §9.2.1 steps4/6 and the ownership paragraph require transferred cursor retention independently of source cache roots through its own quiescence. This was a specified lifetime gap, not a demonstrated dangling provider read.

Commit 45372a3f3e9cea2feea52794fbaee2921cd8797f adds the existing relation Arc to SqlPlan and retains that plan in CursorOwner through provider-confirmed local retirement. The ordinary provider input remains copied and bounded. Failed or unconfirmed provider retirement preserves its bounded dependency root, following existing B06 isolation. It adds no public API, ABI symbol, runtime, SQL generator or copy protocol.

The focused test uses an actual SQLite session, canonical metadata and relation registration, the exact relation-load/Core callback/owner-transfer ABI, and an actual cursor fetch. Weak references independently observe the relation, both immutable models and the exact projection after releasing the relation wrapper and registry roots. All remain live before cursor close, then expire after the provider safety join even while the cursor wrapper remains. The test passes in Debug and Release; both existing provider compilation profiles and strict Clippy pass. These results do not claim a new two-provider managed/AOT matrix.

## Remaining reviewed paths

No other blocking finding was identified in complete tenant/key plus expected-version native CAS predicates, omitted versus NULL changes, independent upsert field8 values, compound session/transaction exclusion between awaited input batches, caller-owned savepoint rollback, acknowledged PerBatch history, Unknown commit propagation, or original input/converter exception preservation with independent cleanup. Existing tests exercise actual PostgreSQL backend termination for Unknown and rollback failure, same-version competing writers, source-close/materializer failures, and both provider ownership counters. Historical acceptance was read and reused, not rerun for this review.

The reviewer authored the narrow correction after reporting it; the correction itself still requires the parent integrator's independent review. Full final package/managed regression remains the parent batch's responsibility.
