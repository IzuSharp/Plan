# Independent review of the private complete-key Find path

Reviewed source:
[`dc235553309e1f5c282fd530fabd225204070d05`](https://github.com/IzuSharp/Korda/commit/dc235553309e1f5c282fd530fabd225204070d05),
parent
[`47fe650dfed5d7bba1c4d74c4a127c5d08b66082`](https://github.com/IzuSharp/Korda/commit/47fe650dfed5d7bba1c4d74c4a127c5d08b66082),
tree `080875d44e84bc991e462c95598f40c007ace0f8`.

**Disposition: retain this Find candidate.** The independent reviewer read the
exact parent-to-commit diff and the final correctness evidence. No remaining
blocking source defect was found. This review does not grant performance credit
or substitute for the integrated candidate's package-consumption and CI gates.
The reviewer did not edit product code, run a product build, or execute a
benchmark. The implementation author executed the tests; the reviewer reread
the logs and independently rehashed their artifacts and committed source blobs.

## Actual replacement and retained responsibilities

| Layer | Decision | Reason and boundary |
|---|---|---|
| Public `DataSession.FindAsync` | Replace its repeated Fluent construction with the private shape route; delete the former production body. | Keep complete-key validation, open-state checks and precancellation before shape acquisition. The removed body remains only in the test oracle, with an actual test caller. |
| Cold native construction | Compile one immutable complete-key plan through the additive Find factory. | Ordered key equalities, full declaration-order projection, terminal 3 and the existing typed Int64 `LIMIT 2` remain identical to the old query. Construction does not call the provider. |
| Parameter schema | Reuse `PreparedParameterLayout.CreateWireLayout`. | Private ordinal definitions use the same canonical JSON/hash/descriptors as public prepared parameters, including configured codecs. They never allocate public parameter identities. |
| Key admission | Keep small scalar counters and the original per-key error order. | No Fluent tape or temporary per-key value frame is emitted. The native factory returns the actual fixed logical byte fee; changing payload bytes are charged synchronously and rechecked natively. |
| Projection ownership | Share the source-registered projection in both the native arena and plan. | The initially retained parsed duplicate was removed before sealing. Mapper identity remains the exact managed Table object. |
| Repeated execution | Copy the owned key snapshot directly into one execution values frame. | Each execution owns independent values and uses the existing cursor pull, TypedStream terminal and exact Table.Row mapper. |
| General native ShapeCache | Bypass only for private Find. | The Find LRU already owns this plan and its immutable compilation. Repeated ABI/identity buffer construction, hashing, mutex/LRU lookup and second cache retention add no reuse here. Ordinary Fluent and public Prepare still enter their existing cache. |
| Provider I/O, cancellation and retirement | Reuse the existing execution and completion paths. | No physical connection, prepared statement, row description, Session, cancellation token or transaction is retained by the Find cache. |

The concrete entry is
[Crud.cs](https://github.com/IzuSharp/Korda/blob/dc235553309e1f5c282fd530fabd225204070d05/src/Orm.Relations/Crud.cs).
Cache ownership, admission and frame writing are in
[FindPlan.cs](https://github.com/IzuSharp/Korda/blob/dc235553309e1f5c282fd530fabd225204070d05/src/Orm.Relations/FindPlan.cs).
The shared parameter-schema implementation is in
[QueryContext.cs](https://github.com/IzuSharp/Korda/blob/dc235553309e1f5c282fd530fabd225204070d05/src/Query.Fluent/QueryContext.cs).
Native construction, rendering and import rejection are in
[query.cpp](https://github.com/IzuSharp/Korda/blob/dc235553309e1f5c282fd530fabd225204070d05/native/cpp/src/query.cpp).

## Isolation, ownership and bounded retention

The private registry starts its parameter ordinals at 1 independently of the
source-wide public registry. Importing this plan into an ordinary query fails
before public registry mutation. The command dependency path also reaches that
import check; the private plan does not publish a mutable query or command-origin
collection from which a public CTE can be built. Ordinary terminal-3 plans remain
one-shot. Only the private Find flag permits this immutable plan's repeated use;
public prepared-shape capability is neither required nor granted by that flag.

The source LRU keys by exact Table reference rather than metadata or projection
hash. Equal model/row metadata therefore cannot substitute a different mapper.
Acquisition, LRU mutation, byte accounting and source-cache release use the
existing registration lock. A caller receives its own retained reference before
the lock is released and holds it through terminal completion. Eviction and
Source close release the cache reference; they do not dispose another caller's
active lease. The cache captures no Session or physical statement. The final
reference disposes the native Plan owner.

Both count and conservative retained-byte charge are bounded. A single shape
larger than the cache byte limit remains executable without admission. The
review required and obtained a real byte-eviction case with a permissive entry
limit, plus execution through a lease retained across eviction. The native arena
and compiled shape are charged; already registered model/projection objects are
shared with their source registry. This charge is a retention budget, not a
measurement of malloc/GC object size or an aggregate process-RSS ceiling. The
existing general shape cache remains separately bounded for other queries;
private Find no longer inserts entries into it.

The managed and native provider profiles, package capability lists and fake
provider fixtures consistently add bit 29, `db.find.shape.v1`; bit 30 becomes
reserved. Source creation requires the capability and its export before source
use, following the existing pull/completion extension closure. The frozen ABI
declarations are unchanged. The new factory returns an ordinary Plan owner,
cache charge and actual fixed logical bytes; valid output slots are cleared on
failure. See the
[extension contract](https://github.com/IzuSharp/Korda/blob/dc235553309e1f5c282fd530fabd225204070d05/native/database/binding/find-shape-v1.md),
[factory boundary](https://github.com/IzuSharp/Korda/blob/dc235553309e1f5c282fd530fabd225204070d05/native/cpp/src/host_abi.cpp)
and
[Source admission/release](https://github.com/IzuSharp/Korda/blob/dc235553309e1f5c282fd530fabd225204070d05/src/Data.NativeHost/DataSource.cs).

## Exact errors and finite query budgets

The behavior oracle copies the removed baseline Find construction, which uses
ExpressionValues plus `Binding.Value`. A convenience `WhereEqual` call is not
an equivalent oracle because its bounded encoder has a different rejection path.
The baseline
[QueryCommand](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/src/Query.Binding/QueryCommand.cs)
uses DomainError/0x4442/code 11 for query quota, mapping to InvalidState. It must
not be relabeled ResourceLimit. Host metadata capacity remains a separate
ResourceLimit failure. Individual expression-frame size failure remains an
ArgumentException.

The final admission order is model registration on a cache miss, then each
key's global frame bound, Column, Value frame bound, Value logical charge,
equality and WHERE. Root expanded-node count starts at 1, matching the original
command. Shared wire constants determine the single-key frame and WHERE charges.
The native plan reports its actual remaining fixed query fee; managed Find adds
payload lengths before allocating the execution frame or returning a Task.
Subtraction guards and checked conversions prevent oversized/overflow bypass.
Native rendering independently validates the frame, schema, nonnull complete
key and fixed-plus-changing byte total before SQL dispatch. Foreign Source
status and the generic query-domain conversion were not remapped.

The final two-provider oracle assertions cover warm logical overflow, a single
oversized frame, metadata-before-key failure, an early composite-key quota before
a later oversized frame, root-expanded-node quota before a later oversized
frame, uncached logical overflow, cold node quota and compiled argument quota.
They compare actual exception type, DatabaseErrorKind and synchronous timing and
assert no SQL dispatch. A subsequent valid key still works after rejection.

An intermediate review hypothesis that compiled argument quota should be an
asynchronous failure was disproved by the real old/new oracle: both are
synchronous. The baseline complete-command compiler already calls
`compiled_shape()` eagerly. The failed expectation is retained; the correction
changes the test expectation and introduces no deferred-error state or extra
intermediate format.

## Why the Find-only cache bypass is safe

`ShapeCache::acquire` supplies cross-plan deduplication, an ABI-prefixed hash key,
collision checking and bounded LRU retention. It does not perform execution
admission: an oversized cache item already executes using its own shape.
The private Find plan already owns exactly the compilation selected by its
bounded managed cache. Its compile result fixes engine/source/generation/profile,
metadata and projection identities, SQL, parameter schema, codecs and argument
order. The provider image/ABI is bound at Source creation; there is no second
plan or ABI namespace being selected when this exact object is reused.

The new render condition is precisely `cache && !is_find_shape()`. The existing
capability, SourceIdentity, parameter frame, null, logical byte and rendered
command checks remain. Native assertions pass a non-null general-cache argument
through two Find executions, verify that the cache still has `(0, 0)` entries and
bytes, then verify ordinary execution inserts one entry and public Prepare
inserts another. The ordinary one-shot and public prepared paths remain covered
by their existing cache tests. This removes redundant private-Find lookup work;
it makes no claim about a measured whole-query speedup.

## Final evidence, source binding and independent rehash

The author's immutable receipt is
`/tmp/DB-Exec-10-find/evidence/find-validation.json`, SHA-256
`7440ad341d66c9d9c0e61adeaa32c3626ca79dc2a31abcbef1480cf8ed5a46a2`.
It explicitly states that checks ran on the exact worktree content subsequently
committed as `dc23555`; it does not falsely claim that a final commit ID was
embedded before that commit existed. The saved `find-final.patch` equals the
reviewer's independently recomputed binary Git diff exactly, SHA-256
`6d77852b4ace049fdd3c2fb68157ab98436ccf3687a1f52ab9f1fa2c53f66a64`.

The independent reviewer rehashed **25 committed changed source blobs, 58
evidence files and 6 native artifacts** against that receipt; all matched.
The reviewer result is
`/workspace/scratch/fd78534029f7/native-review/find-receipt-rehash.json`, SHA-256
`4762a751acb1f66fa4c172f09b9045a56feb5f1130767c99f20f41908dcce431`.

| Final check | Observed result | Raw evidence SHA-256 |
|---|---|---|
| Native query suite | 1,017 checks; 52 SQL/ordered-argument goldens | `query-tests-06.log`: `75e43bc9b6bf91482100968bc31ebb3890ee5a0a070f7db479a99e40d3a68c5f` |
| Release Native AOT, actual SQLite and PostgreSQL | 1,152 assertions; 118 managed retirements | `orm-run-06.log`: `9307c009a70be4bd9191b31b658c8cb1b970165edab21ae0d99f50a5d35eb4fc` |
| Find cases within that final run | SQLite 192; PostgreSQL 192; both report eight zero owner counters | Same run-06 log; consumer copy `5fe1af82238c52f517a27b91504224f9c367844be176cea476ee6de7c79b149d` |
| ABI signature check | 42 frozen declarations unchanged; one additive Find declaration | `abi-signatures-final.log`: `6fee0732f1a7bcf25d062beaa07b06e658ddf648c5545a63a0e449777f7bfa1a` |
| C ABI consumers and formatting | Both provider C harnesses; native format and managed whitespace checks passed | Harness binaries and empty-success format logs are bound in the author receipt; an empty log alone is not used as exit-status proof. |

The final AOT executable SHA-256 is
`a1f7b45cb6628081eecaf202a2e0ea08274dac539664f8ec2e67e9ed36ae0b8d`.
Its copied SQLite and PostgreSQL native assets are respectively
`79c40b95979653610cddd2ec0dad3ca7dcd01dc2b7079e095ca572095d1245fe`
and `8df8a295dde4990f5c72f43b5e6e7b5c8275aff421942d6071b05f4d4a2e8184`.
All three were independently rehashed as Linux x64 ELF files. These are local
correctness artifacts, not the integrated candidate's final package consumers.

The eight owner indexes `[0..5,8,9]` are Sources, Sessions, Operations, Cursors,
Buffers, Owners, PullChannels and CommandCompletions. The final Find checks and
the complete AOT run wait for all eight to return to zero. Functional coverage
includes exact mapper identity across two sessions and eviction, key snapshots,
configured money/binary composite schema, public parameter isolation after
repeated private evictions, count/byte eviction, held leases, source close during
mapper failure, cancellation, no-row behavior and provider schema changes.
See the fixed
[managed Find assertions](https://github.com/IzuSharp/Korda/blob/dc235553309e1f5c282fd530fabd225204070d05/tests/Orm.Relations/FindShapes.cs)
and
[native assertions](https://github.com/IzuSharp/Korda/blob/dc235553309e1f5c282fd530fabd225204070d05/native/cpp/tests/query_tests.cpp).

### Why run-05 has a different assertion total

Run-05 is retained separately: SQLite Find **192**, PostgreSQL Find **194**,
complete run **1,154 assertions / 119 retirements**. Run-06 is SQLite Find **192**,
PostgreSQL Find **192**, complete run **1,152 / 118**. The
[test callback](https://github.com/IzuSharp/Korda/blob/dc235553309e1f5c282fd530fabd225204070d05/tests/Orm.Relations/Program.cs)
adds two `Check` calls and one retirement for every actual `TestRetirement`
callback. The difference is one observed callback, not two removed logical test
cases. These dynamic totals must not be relabeled as fixed test inventory.

The original receipt's `count_note` incorrectly said run-05 Find was 194 in
both providers. The raw logs were not changed. The author appended
`find-validation-erratum.json`, SHA-256
`3fbf173549b655e18407c97319c436bd43de966cad9aaa698b947acabdfe0dc9`,
which extracts the correct values from the original run-05/run-06 logs.

## Preserved failed attempts and remaining scope

The receipt preserves the first invalid Source-owner variant build, the native
parity helper that omitted Fluent projection field 5, two canceled restore
attempts, the statement-count baseline that included opening a Session, the
incorrect ResourceLimit expectation, the discovered metadata-before-key
precedence difference, and the incorrect asynchronous compiled-quota
expectation. It also preserves the format-command option failure and the two
cache-test fixture failures (missing ABI constructor argument and forbidden zero
ABI hash). These were not erased or relabeled as successful candidate checks.
The stage-04 source patch is retained with SHA-256
`57fdd701903fc5a111a756b4367ba3df6071288e36bef77fe943088e15667926`.
All failed logs are bound by the original receipt's evidence inventory; they
are debugging records, not timing evidence.

The fixed candidate removes the repeated Find Fluent/NWQC construction and
private-Find general-cache lookup. It still needs an owned execution-values
frame, native owned argument bytes, current provider validation, batch/mapping
ownership and the established completion fences. The general dynamic path's
shape hash and render SQL/Expectation copies have not gained an isolated cost
attribution from this review. Neither zero framework allocation nor any latency,
CPU, RSS or throughput improvement is established by these correctness runs.

The PG commit-proof changes are separate reviewed commits. Their later
integration validation, the final independent provider-package consumption,
diff-selected CI, and current-candidate local performance measurements belong to
their own evidence records. No performance workflow, job, CI button or hidden
pressure test is added by this Find commit.

## Subsequent independent-package closure correction

After this exact-Find source review, the root's independent provider-package
build exposed a separate closure omission: the package capability model already
advertised bit 29, but `src/Packaging.Domain/inventory.py` did not include the
Find extension descriptor in its expected native-export inventory. The root
reported both native builds and ctest passing before bundle assembly rejected
the extra export with `NWPKG005`. That package rejection is separate from the
run-06 correctness evidence above and must remain in the integration record.

The reviewer independently read the complete follow-up
[`040911c5abdee740c0cd9fbf8295bf511c9cc69d`](https://github.com/IzuSharp/Korda/commit/040911c5abdee740c0cd9fbf8295bf511c9cc69d).
It adds only `('find-shape-v1.json', 29)` to the extension inventory tuple, with
line wrapping. The existing version/bit/capability cross-check and exact native
export audit remain active; the new export is admitted through its normative
descriptor rather than by weakening the audit. This correction is required in
the integrated product. Its new package builds and consumption results belong
to the root's integration evidence; success is not inferred from this source
diff or from the earlier module-level AOT run.
