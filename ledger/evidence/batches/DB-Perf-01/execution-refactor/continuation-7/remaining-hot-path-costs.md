# Three remaining cost-attribution directions

The original inventory inspected product `47fe650dfed5d7bba1c4d74c4a127c5d08b66082`.
The selected final 17da path is described in the [final result](../continuation-8/final-report.md).
This is a shortlist of unresolved cost questions, not an implementation approval
or proof that any proposed change will improve performance.

## 1. Immutable compiled-shape lookup

General Fluent/prepared rendering reconstructs identity bytes, computes the shape
hash, locks and searches the bounded cache, verifies collision identity and updates
LRU state. ABI/profile/source/generation/query/parameter/projection identity and
literal-value exclusion remain required. Acquired shapes must survive eviction
and clear, with bounded concurrent retention. Rebuilding a key for an already
immutable shape is a candidate for attribution; its isolated benefit is unmeasured.

**Find is excluded from this repeated-cache hypothesis:** the selected private
Find path already owns a bounded exact-Table shape and bypasses the general cache.
A new investigation should include both one hot shape and a realistic bounded set.

## 2. Immutable SQL and descriptor ownership

Native render copies immutable SQL/Expectation into the execution representation;
the subsequent move is not another copy. BatchWriter owns descriptors and emits
a bounded canonical batch. A shared immutable owner might avoid redundant metadata
copies, provided it outlives every provider/batch reader and still enforces limits.

Independent mutable parameter/value snapshots are required. Prepared executions
on different sessions, wrapper disposal, cache eviction and changing binary keys
must not share mutable execution data. Do not remove value ownership together
with immutable metadata copies. Separate driver conversion, row encoding, partial
batch compaction and business DTO allocation before attributing a gain.

## 3. Per-batch readiness and continuation scheduling

The pull route retains native fetch work, a readiness callback, managed scheduling,
typed take and asynchronous continuation. Generation accounting, cancellation
registration drain, parent notification-tail joins and exactly-once publication
are required. User continuations must not execute on the unmanaged callback stack.

The historical inline-completion alternative was rejected before performance
acceptance: completion publication precedes fallible continuation dispatch, so a
later error cannot be repaired by republishing an exception or disposing an
already delivered batch. The separate quiet-final-close experiment failed its
measured guard. Neither result proves every current queue hop is irreducible.

Attribute readiness/take/mapping/release intervals, batch counts and whole-process
CPU before choosing another change. Broad read-phase time alone does not identify
queue cost. PostgreSQL description-before-execution, unknown COMMIT outcomes,
protocol drains and safe-return proofs remain contract constraints.
