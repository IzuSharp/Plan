# B09 independent native review — Linux x64

Decision: **accepted for the reviewed native binding, ABI, identity, state, metadata and relation scope** at `5bfaaa2e15726321be8b06a21557f3f62cb389e9`. There are no remaining native review findings. The separate managed ownership/Cdecl/API review is owned by `/root/environment_review`; the batch coordinator combines both reviews.

## Exact scope and inputs

The review read B09 revision 0.4.0, its ORM fragment, the dependency graph, and the pinned Design commit `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. All 18 API input hashes and 6 contract hashes were independently verified. The exact 42-signature inventory matched the pinned Design; an independent C11 compile of the generated header passed with warnings as errors. That header is byte-identical at the final candidate.

The product remains an internal direct binding and bounded native validation component using B01 canonical models, projections, relations, codecs and wire formats. It adds no managed SQL AST, B04 runtime or B11 renderer. The reviewed guide explicitly assigns actual SQL tree/driver/session obligations to their owning tasks.

## Findings closed

| Finding | Accepted correction |
| --- | --- |
| R1: alias slot numbering | All provisional, dependency and invalidation paths use the same one-based slot identity. Commit/abort invalidate dependent expressions; fresh committed left-alias columns are nullable. |
| R2: ON expression admission | Pure expression clauses are allowed during the reservation; query mutation is still rejected. An independent test builds CASE inside ON and proves transitive invalidation. |
| R3: aggregate result type | SUM/AVG follow exact widening and configured numeric identity; arbitrary numeric result IDs reject. |
| R4: aggregate versus OVER root | Aggregate dependency and exact windowable-root permission are separate. Derived expressions and repeated OVER cannot gain that permission. |
| R5: imported budgets | Retained plans and CTEs charge transitive nodes, bytes and nested depth before publication. |
| R6: propagation through list/IN/lift | Derived predicates retain aggregate dependency; NullableLift preserves the underlying windowable root because it adds no SQL operator. A matching-profile SUM-to-IN-to-WHERE rejection reaches the intended branch. |
| R7: clone/mutation state | General Clone preserves an optional selection and new generation; root mutation seal requires a WHERE and rejects the guarded unsupported shapes. B11 retains additional actual SQL shape validation. |
| R8: relation capabilities | Registration/load require the exact metadata/codecs/query/streaming/explicit-relationship prerequisites before publication. |
| R9: single execution and retention | Ordinary terminal plans share an atomic one-shot submission flag with their query and retain the root model. Immutable terminal8 remains reusable only when prepared execution is supported. |
| R10: scalar alias | Exactly one empty alias is admitted through B01 scalar parsing only on the registered scalar path; inline query projections and multi-field empty aliases reject. |
| R11: test operation terminal state | The fixture snapshots cancellation at terminal selection and holds a callback-active retirement barrier. Late cancel does not rewrite success. This is a scoped fixture correction, not a second production host. |
| R12: exact capability mapping | The native snapshot parses the exact section9.3 mask and rejects reserved bits. Missing explicit JOIN, SET, recursive CTE and prepared-execution capabilities reject before mutation. Internal terminal8 seal/import still works for composition without prepared execution. |

## Independent executions

`native-probes/` contains four reviewer-authored, isolated Rust regressions calling the production crate directly. All four passed on native candidate `c5bbd96` with related source hashes unchanged: ON CASE and transitive alias invalidation; aggregate list propagation; strict scalar sentinel roles; exact missing-capability guards including the internal composition exception. These do not reuse the author's test implementation or count as managed/AOT proof.

The later `5bfaaa2` commit fixes managed logical owner closing and changes only the managed owner, its tests and guide. I verified that every native input used by the independent probes is unchanged at that final candidate. The native tests therefore remain valid without repeating them. The separate managed reviewer independently reproduced the earlier Closing defect and owns verification of that repair.

`independent-native-first.log` records an earlier reviewer compilation attempt while the author replaced the old capability helper. Its helper-name compile failure is retained and is not classified as a product behavior failure. `independent-native-final.json` binds the passing tests to their actual source hashes.

## Final formal receipt reviewed

The author's immutable `artifacts/B09/attempt-002` receipt passed all 31 commands on the final committed candidate. Attempt001 remains retained and explicitly superseded by the logical Closing repair. I read the verifier, command log, native test log, managed result records and artifact manifest. I independently recomputed all 90 declared source-input hashes and all 6 binary/XML artifact identities at the final candidate; all matched.

- 16 native state/property groups passed in Release, alongside formatting and Clippy.
- The managed product bindings invoked the actual production validator fixture in JIT: 66 assertions across 10 groups.
- The Linux x64 Native AOT executable ran the same 10 groups with dynamic code disabled: 67 assertions.
- Both modes observed zero native owners, operations and buffers at completion.
- Minimal/composition samples built and executed in JIT and AOT.
- The compiled API/XML/reference gate reported zero public CLR symbols and 42 exact Cdecl declarations.
- Source hashes were stable before and after the complete formal run.

This receipt proves the B09 component, using an explicitly test-only source/session/callback transport and canonical EOS cursor. It does not claim actual database execution, B04 lifecycle implementation, B11 rendering, pristine NuGet consumption, another platform, or a performance benefit.

The machine-readable final receipt is `review-final.json`; all raw independent evidence and probe source are adjacent. No author source, shared build file or Plan state was modified by this reviewer.
