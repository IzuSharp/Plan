# frame-pool08: actual ordinary SQLite ELF readback

This finite static check confirms that the selected pool branch, logical command length, delayed pool initialization, and `clearArray: true` survive into the actual ordinary Native AOT consumer. It supplies no timing credit and does not select frame-pool08. Both source/build/binding identities, native image, ELF and matching DBG were unchanged before/after capture.

## Bound images

| Identity | ownership05 baseline | frame-pool08 candidate |
| --- | --- | --- |
| Source | `69b2383dadc280f1a81de592592a1442069eed0c` | `13b25de2b67d858d8b6524f615e3a84b4c541817` |
| ELF SHA256 | `b0a7af867ef45a6aa6f874c9817a186e44829628958128866d23e3f8a882da43` | `ec550055ee9bcc77c552873037664e6c0736fdc6426365448a05b6a3cc944640` |
| DBG SHA256 | `e3d0dd531d3e4595524c26c913429a423cc411a997a44712ef834917e967b74d` | `7387962fb51a93f9c71a1697d06cd0154f486c86239c4473282e6901c00c21da` |
| ELF/DBG BuildID | `22e4605e545192b6d52e7d150a1b1db7c9b53e72` | `e57346d9f93186f101840aa48e62eddd952a9827` |

Both load native SHA256 `9389960168420aac399f2f08c7ebd88f2b2478faf491d3a6feb8db347cfc245c`, the same native04 image. The exact per-consumer build/binding/package receipts, source bytes, commands, selected symbols, line mappings and pre/post checks are in [capture receipt](actual-elf-sqlite-01/receipt.json). The additional four commands read only Array.Clear and program headers: [edge receipt](actual-elf-sqlite-edges-01/receipt.json). Full symbol-table output was not retained; only selected symbols were saved. No binary was executed.

## Source and machine-code correspondence

All application source references below are the committed `src/Query.Binding/QueryCommand.Submission.cs` copied beside each image capture. Runtime line mappings name the matching Native AOT CoreLib sources in `ConfigurableArrayPool.cs` and `Array.cs`.

| Contract / question | Observed ordinary candidate instructions | Conclusion and boundary |
| --- | --- | --- |
| Only eligible Seal frames rent | Encode tests `rentFrame` at `0x1338ad`, subtracts4097 at `0x1338b5`, compares unsigned to61439 at `0x1338bb`, and branches to rent at `0x1338c1`. Other sizes call `RhpNewArrayFast` at `0x1338cd`. | Inclusive4097–65536 condition is present. Baseline Encode unconditionally allocated the final frame with `RhpNewArrayFast` at `0x133864` after envelope capacity validation. No dynamic hit rate is inferred. |
| Ownership is recorded before later encoding failure | Virtual Rent at `0x1338fa`; byref store via `RhpCheckedAssignRef` at `0x133906`; subsequent frame span/write work begins at `0x13390b`. | Caller rental reference is established before later writes/sidecars, supporting the lexical finally contract. |
| Native receives logical length | Encode stores size in returned struct offset0x18 at `0x133e90`. Seal loads it at `0x13403c`, bounds-checks against physical array length at `0x13405b`, transfers it through `%r15d`, and passes it to `BindingChecks.View` at `0x134196` / `0x134199`, preceding Compile at `0x134230`. | Rented capacity is not substituted for command length. Span checks and exact logical view survive lowering. |
| Successful single-root path does not initialize the pool | `TryEncodeSingleRoot` call `0x133ffe` / success branch `0x134005` skips Encode. Rental remains null. Normal finally tests null at `0x1343c2` / skips pool at `0x1343c7`; exception finally does the same at `0x1344d3` / `0x1344d8`. | The pool-static access is behind the null guard. This proves no pool access along this selected Seal path, not zero extra CPU: the candidate still has changed stack/prologue/finally code. |
| Private pool limits are actual constants | `.cctor` allocates the receiver at `0x1387c8`, loads65536 at `0x1387d3` and4 at `0x1387d8`, then calls the ConfigurableArrayPool constructor at `0x1387dd`. | Explicit lazy nested class initializer and requested bounds are present. Cold initialization still does work if an eligible rental first occurs. |
| Successful and exceptional return clear the array | Normal finally loads1 into clearArray at `0x1343e6`, virtual Return at `0x1343ee`; exception finally has the same at `0x1344fc` / `0x134504`. Captured pool Return tests clearArray and calls `System.Array.Clear` at `0x26cf1c` before Bucket.Return at `0x26cf38`. | Actual clearArray argument is true. Array.Clear reads physical element count at `0x152114`, multiplies by component size at `0x152117`, then takes the non-reference clear helper for byte arrays. The clear extent follows physical array size, not the logical command slice. No total cleared-byte count was measured. |
| Pool work is not free | Captured Rent has bucket-search and miss-allocation paths. Bucket Rent and Return each contain `lock cmpxchg` (`0x26dc36`, `0x26dd6c`) and SpinLock slow-path call sites. | These are possible costs. This static report does not say how often they happen, whether they contend, or whether CPU improves. |

The Encode and Seal virtual calls use method-table slots0x30 /0x38. The actual receiver construction and matching source identify ConfigurableArrayPool<byte>. The receiver type data at `0x74a868` lies in hydrated memory beyond PT_LOAD file bytes; this readback did **not** dynamically inspect either slot. The report therefore does not claim a runtime indirect-target observation. The separate captured concrete Rent/Return bodies have matching symbols and line mappings.

## Ordinary / diagnostic boundary

Committed Query.Binding source and actual defined-symbol tables for both ordinary images contain none of `FrameRentalLocalFault`, `FrameRentalFaultPoint` or `FrameRentalResourceMetrics`. Those are the local03 diagnostic identifiers supplied by the author. Normal `SealFrameCache`, `.cctor`, Encode and Length belong to the product candidate and are not diagnostic contamination. Exact-name symbol absence alone cannot exclude unnamed, trimmed or inlined work; source and actual build identity are the additional binding evidence.

The report covers this SQLite pair only. It does not compare complete binaries, derive CPU from instruction count, establish branch frequencies or pool hit rate, provide new correctness/workload results, or claim an end-to-end gain. PostgreSQL must be separately captured after its actual ordinary consumer has built and passed binding verification.

## Resume

`capture_frame_elf.py` is parameterized for PostgreSQL. `capture_frame_elf_edges.py` binds its completed receipt and records only the clear edge and type-data limitation. The original SQLite capture is unchanged; findings and edge readback are adjacent additions. All raw commands and failed/unresolved boundaries remain available.
