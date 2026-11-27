# Continuation11 — isolated Seal final-frame rental08

**Selected for implementation and finite validation, not adopted into the retained
product:** reuse only the final temporary byte frame of `QueryCommand.Seal` when
its logical length is greater than 4096 and at most 65536 bytes. Use the pinned
runtime's private `ArrayPool<byte>.Create(65536, 4)`. The root accepts the
[independent selection review](frame-pool08-selection-11/independent-selection.md)
after the [ownership read](frame-pool08-selection-11/ownership.md) and
[locked runtime read](frame-pool08-selection-11/runtime-review.md). Record this
strategy in Design before product edits.

Base only on integrated05, Korda `2ea67ce1902f330679c3ebff4d6d5733be20f69c`,
tree `4e3989f2ce9e0c554585aab5a8bbb656e689b18d`. Do not layer on rejected tail06 or
pull-local07. [Continuation10](continuation-10.md) retains the closed07 result and
the current measured gap. Use task-marked frame-pool08 worktrees and branches.
All [long measurements remain cancelled](short-only-scope-08.md).

## Measured reason and a falsifiable target

Existing related32 scope evidence identifies one final frame allocation of
60,504 B for a 60,480 B logical payload. Current ordinary related32 uses about
516.1 KB managed bytes per business; its 53 result rows and 32 relation keys remain
the same business contract. The target is that one temporary array, roughly
11.7% of current whole-process bytes, not a prediction of net savings or CPU.

The 59,680 B source-tape copying remains. Multiple tapes must form one contiguous
envelope, with dependency/origin ordinals rewritten in the destination. Existing
public clones/captures do not give unique rewrite rights over those source tapes.
Do not combine tape transfer, graph caches, another scheduler, SharedArrayPool,
Render/CTE pooling or a runtime setting with this experiment. No current evidence
assigns this frame allocation an exclusive CPU share or explains the text1000
CPU gap with it.

## Exact implementation boundaries

- Preserve the existing 4096 B single-root stack path, all Render/CreateCte
  allocation behavior, the small graph slow path and sizes above 65536. Initialize
  the private pool only on the first eligible rental; the stack path must not
  trigger pool construction. Keep C# Fluent, Native AOT, C++ execution and both
  independent provider packages unchanged.
- Keep logical-size, depth, record, origin-binding and owner checks at their
  existing positions. Acquire a rental at the original final-array allocation
  point. A pool miss allocates normally and must not become a business refusal.
- Seal has the only lexical rental owner. Its try/finally must already exist
  before entering the Encode that can rent; record the returned array immediately,
  before any later encoding or sidecar operation can throw. No new per-rental heap
  lease is selected. EncodedCommand remains a copyable borrowed descriptor and
  must not own disposal or expose the rental in persistent graph state.
- Carry explicit logical length into header, command span and native view.
  Oversized bucket tails are never submitted. Initialize all reserved bytes
  explicitly. Preserve the complete original bytes, source-tape copy, fixups,
  sidecar, metadata and origin-publication sequence.
- Retain the array through synchronous Compile and the original metadata/origin
  completion flow. Return it to the same private pool exactly once on success
  or failure, with `clearArray:true`. Preserve original native-owner cleanup and
  error ordering; do not suppress rental errors or weaken snapshot/DDL/mapper
  contracts.

The ABI borrows frame input only until synchronous Compile returns. The actual
C++ implementation copies literal cells and origin identities into owned bytes;
PublishOrigins does not read the frame. These source facts justify a lifetime
experiment but are not substitutes for poison/re-rent and actual-plan tests.

## Count the known costs as well as the proposed saving

The actual ILCompiler 11.0.0 source pins VMR
`297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`, runtime
`deae2e32bf0e018e09d64597b7c59b62b73bb3ce`. Four official files were read and
independently matched by Git blob identity; their exact bytes accompany this
decision. The configurable pool uses bucket SpinLocks and has no automatic trim.

The four reachable buckets can cache at most 491,520 payload bytes, plus object
and index overhead. Related32 uses the 65536-byte bucket, whose four cached arrays
hold 262,144 payload bytes. These are cache bounds, not active-memory or RSS bounds:
more than four simultaneous rentals can allocate, and pending garbage can remain.
The static cache can remain after release and idle observation.

A cold related32 array is 65,560 B including the observed x64 array overhead,
5,056 B larger than the current exact-size array, plus first pool initialization.
Return clears the entire actual 65,536 B array even if a full bucket then discards
it. Any initial encoding clear is additional. Count rent/return, actual lengths,
miss/new-array allocation, cold initialization and all clearing bytes. Do not
move costs outside the reported scope or claim a zero-cost buffer swap.

## Finite validation and selection

First review the actual source and committed module impact. New files under the
existing registered source/test modules need no performance CI route. Public
API and existing affected package checks remain selected independently for both
providers. Before any product push run and explain the committed impact plan.

Correctness uses existing envelope/sidecar and real-database regressions plus
focused lease controls: 4096/4097/65536/65537 boundaries, dirty oversized arrays,
quota rejection before rent, failure after rent but before Encode returns, native
status error and OK/null result, held synchronous borrowing, poison/re-rent followed
by actual old-plan execution, and existing public Combine/origin/input snapshots.
Use existing relation 1/2/32, duplicate/empty/key-width/mapper/cancel/owner coverage.
Do not create a new broad business matrix. A post-compile metadata/origin synthetic
fault may use a separately identified local test build; do not add shipping global
failure callbacks or force genuine process OOM to manufacture coverage.

Allocation, clearing, miss and timing observation remains in separately identified
local diagnostics, never CI correctness commands. Preserve actual ordinary local
NuGet PackageReference AOT consumers, generated C#, ELF/debug/native/package
identities and commands. Diagnostics get no ordinary timing credit.

After lifetime correctness and the intended resource mechanism hold, run one
predefined dual-provider related32 reverse-order comparison: retained05,
candidate08 and Dapper, then reverse, with the same SQL/DTO, persistent session,
C1, batch32, 2048 measured businesses and 128 extra warmups per process. Record
whole-process allocated bytes, client CPU, service p50/p95/p99, GC and the exact
RSS observation available; add the existing finite released-idle observation if
the chosen harness supports it without changing the business measurement. Keep
PG server costs separate. Twelve business processes suffice for this first gate.

Only repeated net resource saving with acceptable CPU/tail/memory cost can advance
this candidate. If a concrete concurrent-cache or retained-memory risk remains,
select the smallest existing short mixed observation that answers it; no automatic
mixed, pressure or large matrix is added merely because a candidate exists.
Reject or narrow on lifetime/snapshot/length/error failures, a moved allocation
of similar size, non-repeating saving, or material measured CPU/p99/RSS regression.
No text1000, coordinator or generic spin repeat is selected. No long run is selected.

## Recovery state

At this selection no product implementation, build or new performance measurement
has run. The selected product remains 05; 08 earns no correctness or benefit credit.
The [evidence index](frame-pool08-selection-11/source-records.json) preserves this
read-only boundary. Continue from the same local task root and keep Go drafts
Plan35/Korda39 unchanged. The remaining authorized normal reviews, merges,
existing CI/release and actual public NuGet AOT verification stay in scope.
