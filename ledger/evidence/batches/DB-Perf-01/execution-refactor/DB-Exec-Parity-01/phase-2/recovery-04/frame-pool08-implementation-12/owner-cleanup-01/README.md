# Independent native result adoption cleanup

This correctness fix precedes the frame-pool08 comparison. The old Plan and CTE
object initializers adopted `result` into a finalizable SafeHandle before evaluating
allocating metadata. If that evaluation threw, the catch performed a raw native
release while the temporary SafeHandle still owned the same value. Native handles
are address-keyed and may later reuse an address; a second release is not safely
assumed to be a harmless no-op. This is source-confirmed risk, not a claim that an
ABA incident has been observed in a running database.

Commit `69b2383dadc280f1a81de592592a1442069eed0c`, tree
`f7660759bba43ae83324620e2fb731efd479c3b5`, is based directly on retained05
`2ea67ce1902f330679c3ebff4d6d5733be20f69c`. The sole changed product file prepares
complete Plan/CTE metadata inside the existing raw-owner try/catch before adopting
that owner in DatabaseOwner. The existing constructor performs all checks before
SetHandle, which is its last operation. The later auto-property assignments do not
allocate. Native errors, null-result checks, validation, compilation and origin
publication retain their order. Metadata moves before wrapper allocation; this is
an explicitly acknowledged allocation-order change, not an assertion that an OOM
would occur at the identical allocation site. No public API, native ABI, ownership
registry, callback allocation or performance setting changes.

Both performance comparison sides will carry this same cleanup: an `ownership05`
baseline and a `frame-pool08` candidate. The original05 measurements retain their
original identity and will not be relabeled. Cleanup earns no pool-performance
credit. The planned comparison remains twelve related32 processes; no broad new
matrix or long run is authorized. Local synthetic post-compile failures remain a
separate test-build identity and do not manufacture process OOM or inject shipping
global callbacks.

The required committed-diff impact command was run. It selects the existing shared
Linux build/API/dependency/correctness actions and separate PostgreSQL and SQLite
package, packed-API, correctness, AOT consumption and validation actions. The
native and earlier test reasons come from cumulative unmerged05 changes relative
to origin/main. This fix itself is managed Binding only; run_steps is empty, and
no CI workflow or performance invocation was changed. Source review and affected
AOT correctness validation are still pending at this record.
