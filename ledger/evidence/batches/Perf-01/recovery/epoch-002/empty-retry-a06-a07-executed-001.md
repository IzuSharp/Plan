# Perf-01: completed, unselected empty-retry component verification

The original A06 and A07 verifiers passed against actual source `08d716ed2eab448a1a890cb579d086c131613291`. This is historical component evidence for the isolated empty-coordinator experiment. The final selected candidate remains `7e7732cd7ee40aec319961d328f38b593a4af5da`; the empty guard is not selected, and no additional B04 or application experiment is planned for it.

The shared finite owner executed the two original offline verifiers sequentially from 2026-11-21T11:47:01.836190+00:00 through 2026-11-21T11:49:47.846570+00:00. Both outer commands exited zero and retired. Their final owned-process and owner-child lists were empty, with no cleanup signals. An earlier nonblocking lock collision did not execute a command or produce a test result.

## Actual original verifier results

| Check | A06 callbacks | A07 async |
|---|---:|---:|
| Normal JIT assertions | 6,332 | 355 |
| Normal Native AOT assertions | 6,333 | 356 |
| Rust unit tests passed | 5/5 | 4/4 |
| Original child commands | 35 | 39 |
| Exit-zero commands | 32 | 39 |
| Original expected negative commands | 3 | 0 |
| Observed owned process identities | 74 | 65 |
| Final live owned processes / owner children | 0 / 0 | 0 / 0 |
| Outer exit code / retired | 0 / true | 0 / true |

A06 normal JIT/AOT each checked 43 owners and 32 GC races, ending with zero pending callbacks, active callbacks and roots. Its two InvalidUco processes deliberately exited -6 with `InvalidProgramException`, without entering the invalid callback body. The invalid-signature build deliberately exited 1 and reported `CS8894`. These expected failures are part of the original verifier's passing result.

A07 normal JIT/AOT each created and released 59 native owners, ended with zero live owners, input bytes and result owners, and passed the lost-wake product regression. Its six isolated fault processes preserve a different original contract: **each intentionally retains one native owner and reports `retirement_reported_success=false`**. Indeterminate-start and callback-then-reject also retain 3 input bytes and one context root; retire-fault records a poisoned operation. The fault fixtures have 3 JIT or 4 AOT assertions. Their controlled process exits do not establish successful native retirement, and those expected quarantines are not presented as normal-path cleanup.

Both results record the exact clean 08d source and `source_unchanged=true`. The original verifiers recompute source hashes before setting that final flag. The 103-file union in their scopes agrees with the frozen recipe.

## Independent review and source retrieval

The independent continuation reviewer checked 32 named plan/result/receipt/log hashes, including 26 bounded stdout/stderr files, the 103-file source-hash union, negative-case markers, original end-of-run source checks and both terminal outer retirement records. The 103-entry comparison used the source hashes recorded by the original executions and recipe; this audit did not independently reopen all 103 source files. No factual or binding blocker was found. The reviewer performed read-only work; no new build, workload or verifier execution occurred in that audit. Intermediate process states were not substituted for the final owned-process checks.

Exact source tree `c95491f4c7b86703d0d4f697eb185cd4f5fc1a47` is retrievable as [snapshot 3afbebf9](https://github.com/IzuSharp/NativeWeave/commit/3afbebf97352bc9ddbbc13e2bd1adefee339c4cb), on `task/Perf-01-empty-retry-linux`. The changed coordinator was remotely read back byte for byte; its SHA-256 is `4d2f79814b425b5ead5ea2918c021cd3f29910c396c026a801967eb5af968ada`. The actual test identity remains local 08d. Publishing an identical-tree snapshot does not rewrite it.

The [source review](empty-retry-source-review-001.md) and [recipe review](empty-retry-a06-a07-recipe-review-001.md) remain their original, earlier source/preparation records. This later execution record supplies actual outcomes without changing their timestamps or scope. During the storage owner's metadata freeze, this continuation stopped local writes and additional builds; this publication is assembled from completed, reviewed evidence.

## Exact records and limits

| Record | SHA-256 |
|---|---|
| Frozen finite plan | `6e1a1aed51f6246e1be4a3ff50f11cb03bbe59e0852f959aa05cbcddca07090b` |
| Outer execution | `6538641383ebbb2822e3874e4146a5487445d4e8e0a319fd16aa7e4d9835f221` |
| A06 result | `f3ca6ff16d0c7967c64843f00f984171e8488e064c0ec66f0378811ff29a4036` |
| A07 result | `8920220fb4e135f83ace921d7ae0e0546649d036dc6d27135951a55f7af170c7` |
| A06 outer receipt | `f0f16fcae0054baa74fe911a54b1210a0086736e3be922b305e617373d9dba8d` |
| A07 outer receipt | `4f91b9d564ee80332b249731d5beb6823be5a3b99dba2d83fdb1963cca1232e8` |

[Machine-readable evidence summary](empty-retry-a06-a07-executed-001.json) and [source publication receipt](experimental-empty-source-publication-001.json) retain those identities. Original private outputs remain under `perf01-recovery/epoch-002/empty-retry-a06-a07-001`.

This component verification supplies zero formal-comparison, capacity or long-run credit. It does not directly validate final 7e domain packages or replace their Native AOT, database and real TLS regressions. It makes no performance claim for the empty guard.
