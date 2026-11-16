# B09 Linux component handoff

Status: implementation and task-owned Linux x64 component verification complete. Both independent technical reviews accepted the final candidate with no open findings. Batch integration, PR processing and post-merge checks remain the coordinator's responsibility.

## Identity and recoverable changes

- Owner: `/root/plan_requirements`.
- Branch: `task/Task-02-B09-linux`.
- Worktree: `/workspace/scratch/0898a75257bc/.worktree/Task-02-B09-linux/NativeWeave`.
- Final tested candidate: `5bfaaa2e15726321be8b06a21557f3f62cb389e9`.
- Owned implementation commits: `88784c9`, `26d0521`, `c5bbd96`, `5bfaaa2`.
- Root-owned shared registration commits in this worktree: `83969db`, `5513805`, `66c7051`; the coordinator already unions these manifests/IVT/solution changes into the batch rather than duplicating them.
- Exact Design commit: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
- Final run: `attempt-002/`; source/lock manifest contains 90 files, unchanged before/after execution. Worktree was clean for the run and remains clean.

## Delivered scope

The internal managed component binds the exact 42 Cdecl signatures through canonical A01 records. It adds separate logical owner closing and physical SafeHandle access leases, query admission, same-source owner/token validation, immediate B01 operand/projection/value encoding, clone/import composition and independent relation binding. There are no public CLR exports or new application facade types.

The native component reuses B01 model/projection/codec/relation/db-wire types. It validates direct operation kinds, versions, fields, types, capability bits, generations, finite node/depth/byte budgets and legal states before publication. JOIN reservation/commit/abort invalidate captured provisional expressions. Parameter identities are source-bound; ordinary plan execution is atomic one-shot and root model/dependencies remain retained. Independent relation registration/load copies bounded arguments without changing frozen Table identities.

B11 still owns actual SeaQuery statements/rendering and tree/session-dependent validation; B04 owns the runtime and Core operation coordinator. The test-only fixture executes production B09 validation through real FFI, provides explicit test source/session owners and a canonical EOS cursor, and does not execute database SQL. No B04/B11 implementation or acceptance is claimed. Ordinary managed source builds do not invoke Cargo; the maintainer fixture is precompiled before the JIT/AOT consumers run.

## Actual verification

| Gate | Final result |
| --- | --- |
| Source-bound command runner | 31 of 31 commands passed |
| Native Release state/property groups | 16 passed |
| Exact compiled Cdecl signatures | 42 matched pinned Design and generated C/Rust/C# inventory |
| Compiled public API / XML / reference | 0 public types/members; internal call XML and generated reference complete |
| JIT direct FFI consumer | 66 assertions across 10 groups passed |
| Linux x64 Native AOT direct FFI consumer | 67 assertions across the same 10 groups passed; dynamic code disabled |
| Minimal and composition sample | Actual JIT and Native AOT execution passed |
| Native terminal resource observations | 0 owners, 0 operations, 0 buffers after all scopes |
| Independent native review | 4 additional reviewer-authored regression groups passed; all 12 findings resolved |
| Independent managed review | Original logical-closing defect reproduced; unchanged probe passes repaired candidate; exact 42-signature and final receipt audit accepted |

The direct FFI cases include invalid/default/mixed owners, native token generations, logical versus physical disposal, control failure atomicity, JOIN capture invalidation/nullability, self-composition without recursive admission, exact parameter schema/copying, relation registration/key/projection validation, kind2 single transfer, bounded EOS fetch/close/retirement, untaken-result cleanup, late cancellation preserving a successful terminal, and Pending retirement while its callback is active.

`attempt-001` passed its finite suite but is explicitly superseded by independent finding M1: physical SafeHandle.IsClosed remained false while an old access lease delayed release, allowing a new source call after disposal. The original independent failure and unchanged successful follow-up probe are retained. Commit `5bfaaa2` publishes logical Closing before base disposal and checks it before/after AddRef. No earlier passing result is presented as final acceptance for that defect.

## Evidence and remaining coordinator steps

- `attempt-002/status.json`, `commands.json`, `source-inputs.json`, `source-inputs-after.json`, and `artifact-identities.json` bind source, lock/features, actual native/managed/AOT artifacts and response files.
- `independent-native/review-final.json` and `review-final.md` accept the native component; raw independent probes and finding resolutions are adjacent.
- `independent-managed/final-review.json` and `final-review.md` accept ownership/ABI/callback/documentation scope; the original and repaired independent probes, exact-signature audit and all raw text logs are retained.
- `evidence-index-linux.json` hashes this complete curated packet. Compiled binaries and build caches are omitted; their actual hashes and source identities are retained. One small native reviewer input fixture is retained for reproducibility.

Next: coordinator persists this packet under Plan `ledger/evidence/B09`, updates batch handoff and the existing linked NativeWeave/Plan PRs, completes required integration checks/reviews and the authorized merge/post-merge workflow. B09 has no remaining implementation blocker on Linux. Windows, pristine package consumption, assembled database-host behavior and performance comparisons are not claimed by this component receipt.
