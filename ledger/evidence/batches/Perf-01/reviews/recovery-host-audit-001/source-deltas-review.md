# Recovery source deltas: weak-writer ablation and DB reader

These are two bounded source-only verdicts. No product build, fixture, workload,
reader import or reader execution was performed by this review. Neither verdict
transfers a historical execution result into recovery epoch001.

## Optional weak-writer OFF reconstruction

**ACCEPT for experimental source preparation only.**

| Identity | Value |
| --- | --- |
| Actual new product commit | `0c67621f0d6cedca268f15e80fd75595d26b5094` |
| Direct parent | `2e3995df8d86583ee9443348276ca8d918056bfc` |
| Actual tree | `a8f33c1c07127d8e70642afeb84c3822fbf4565e` |
| Only changed file | `src/Protocols.Grpc/NativeTransport.cs` |
| Actual file SHA-256 | `02e175543f04eba7b6b2ee9a54706f41f385d00ce8fd43ed76dc09dd89c804cf` |

The actual clean repository diff contains one insertion and thirteen deletions
in that single file. It removes the weak array-reference field and the
lookup/clear/retarget block, replacing it with `new byte[encodedLimit]` after
the same managed-credit acquisition. It does not reconstruct the historical
private commit or its missing runtime evidence; the newly created commit above
is the actual producer identity for any later build.

`WriteCoreAsync` still obtains the same native reservation before allocation.
`EncodeAndCreate` retains the same managed credit, scoped `MessageWriter`
disposal, ordinary marshaller call, stream-limit check, pinned native copy,
request/token lease release and reservation transfer. The one-pending-write
gate and operation-retirement await are unchanged. A newly allocated array has
the zero-initialized contents previously obtained by clearing a retained array.
This observation concerns equivalent buffer contents, not a performance claim.

There is no native-source, public API, native ABI, DTO/Entity/Handler or package
contract change in this diff. The previously retained correctness fixes remain
in the unchanged parent tree. Optional OFF remains **unselected**. No OFF build,
runtime, noise, capacity, performance benefit or retention decision is accepted
by this review. Any later attribution must use actual newly bound artifacts and
the prospectively reviewed current-epoch ON/OFF measurement policy.

The implementation repository's current `AGENTS.md`, README and background
boundary were read. This narrow source verdict is not a claim that repository
verification or current functional regressions have executed for OFF.

## Database terminal-state reader correction

**ACCEPT for the demonstrated one-predicate schema correction.**

| Identity | Value |
| --- | --- |
| New Plan source commit | `42137397f8a1253740806cd87c0e2b83d34f5b0f` |
| New source scope | `ledger/evidence/batches/Perf-01/diagnostics/recovery-measure-001` |
| New `database_compare.py` SHA-256 | `3e8d461478e704bc5a94be8ed5cda6e3051fdf699f70c3b6d603176c99227d81` |
| Original public reader SHA-256 | `0f3ee6ca0d4ce9fcdce256df9b9fce1f9ce5eaa9032c3afa86e443aeceff59b8` |

The sole executable delta changes the terminal-state equality in `read_cell`:
NativeWeave before/after require `Disposed`; direct Rust and managed comparators
require `Stopped`. The original `ROUTES` lookup and exact summary role/route
equality already reject an unknown role before this condition. The conditional
does not introduce an additional unvalidated role.

The actual comparator sources at product
`2e3995df8d86583ee9443348276ca8d918056bfc` establish the schema:

| Source | SHA-256 | Relevant output |
| --- | --- | --- |
| `src/Benchmarks.Domain/comparators/direct-rust/src/main.rs` | `04022bb711b7e3e90d64f7cc1755332a4dc8706ae6f92d395f59454149b8a10d` | The final `CLOSED` record uses `serverState=Stopped`. |
| `src/Benchmarks.Domain/comparators/managed/Program.cs` | `5b633b215b2e309254d81496432f4bfbb924de1ce6df2a133ac4699831de8c18` | The shutdown report uses `Stopped` after awaited disposal and explicit retirement checks. |

The existing public
`checks/database-collection-checkpoint-001/public-summary.json` at Plan
`0d2ed1b460ca194978cd595417739bce99adc224`, SHA-256
`88f9c857a2443e58c96e17fb50364e6ca029e41cb2db5997375cd14c254f8e99`, separately
records this same schema distinction. Its historical private corrected source
and historical finite checks are not recovered or re-executed by the new edit.

The source diff changes no operation or durable oracle, resource-release flag,
error population, generator eligibility, SLO, percentile, A21 bootstrap or
other statistical predicate. The codec reader remains the unchanged public
`6f09ac17bc60544ef97c147a47cada66344f6ea068318821f204da0a6e468663` source; this
specific verdict does not claim recovery of its missing private successor or
accept any fresh codec result. Runtime admission and the complete current-epoch
reader integration remain separate source and actual-execution requirements.
