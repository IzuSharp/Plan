# Perf-01: successful default-inspection cache candidate

Status: source correctness study, prospective regression design and a later
diagnostic allocation observation. This document does not establish measured
loader attribution, authorize skipping the frozen before measurements, or claim
a performance gain. Root owns any implementation and shared-path integration.

## Inspected baseline

Product source is `ea5fa528035d025bd7a28698ee7c71194432236c`; the relevant files
remain unchanged in root's integration worktree at this inspection.

| Source | Inspected behavior |
| --- | --- |
| `src/Interop.Negotiation/EngineMetadata.cs:47–96` | Immutable `EngineInfo`; capabilities copied, ordered and privately indexed |
| `src/Interop.Negotiation/EngineMetadata.cs:103–133` | Sealed `EngineDescriptor`, fixed manifest/assembly, public `Inspect` delegates directly |
| `src/Interop.Negotiation/EnginePackage.cs:13–148` | Sealed readonly assets; manifest snapshots collections; descriptor construction reads no files |
| `src/Interop.Negotiation/EngineModuleLoader.cs:20–126` | Slot identity validation, pending-load join, resident metadata, explicit override revalidation, per-assembly resolver bind, required capabilities |
| `src/Interop.Negotiation/EngineModuleLoader.cs:203–296` | Identity construction, process slots, resolver conflict prevention, per-call option snapshot |
| `tests/Interop.Negotiation/Program.cs:121–257` | Coexistence, concurrent explicit loads, options, output-record repair, conflicts, latched and retryable failures, override revalidation |
| `tests/Interop.Negotiation/verify.py:23–32` and execution sections | A02 case inventory and actual JIT/AOT/package consumer verifier |
| `src/Engines.SyncProof/ZlibCodec.cs:98–135` | Every codec run reaches `Descriptor.Inspect()` with null options before capability and native calls |

Default resident inspection already avoids hashing the native file. Its repeated
work still includes an options record, RID asset query, identity construction
with `StringBuilder`/temporary strings/capability ordering, the slot lock, native
import filename/basename construction and the resolver lock. Source shape alone
does not determine how much of a complete codec or application call this costs.

## Minimal candidate

Add one private nullable `EngineInfo` reference to each `EngineDescriptor`.
When and only when the caller passes `options == null`, read it with acquire
publication semantics. On a miss, execute the existing loader unchanged and
publish the returned successful metadata with `Interlocked.CompareExchange`
or an equivalent release write. The assignment must occur after the complete
loader call returns, including resolver binding. When options is nonnull, always
execute the original slow path, even for an apparently empty options object.

Illustrative control flow, not an implemented product patch:

```csharp
if (options is not null)
    return EngineModuleLoader.Inspect(this, options);

EngineInfo? cached = Volatile.Read(ref _defaultInfo);
if (cached is not null)
    return cached;

EngineInfo validated = EngineModuleLoader.Inspect(this, null);
return Interlocked.CompareExchange(ref _defaultInfo, validated, null) ?? validated;
```

The existing loader remains responsible for serializing first load. Losing
callers may redundantly execute its resident path once; they still receive the
same `LoadedModule.Info`. No extra descriptor lock, failure cache, owner,
thread, executor, native export, or public API is required. The field retains
metadata already retained by the process slot and does not own a library handle.

Keep `ResolveExport` unchanged in the first experiment. It currently calls the
loader directly while establishing operation tables; changing that separate
path broadens the experiment without evidence that it is per-operation cost.

## Why the narrow cache preserves validation

The descriptor's manifest, selected asset and assembly are immutable. Process
architecture/RID do not change during its lifetime. Successfully selected native
modules are deliberately resident and are never replaced or hot-unloaded. The
global slot can latch a failure only during its initial mapped load; it does not
replace an already published successful module. Resolver entries reject a
conflicting handle before changing an existing basename mapping.

These conditions make a successful default result stable for that descriptor.
An independent descriptor with the same engine ID has an empty local cache and
must still perform the existing full identity conflict check and its own
assembly's resolver binding. A failed conflicting selection does not invalidate
the original resident descriptor, matching existing behavior.

Nonnull options retain all current checks on every call: absolute-path shape,
bounded and unique capability snapshots, actual file/hash/format revalidation
for an explicit path, and actual advertised required capabilities. Reusing a
mutable capability list in an options object still takes a new snapshot and
can fail after a previous successful call. An explicit-load success need not
populate the default cache; its first subsequent null call can perform the
unchanged resident loader path once before publishing.

Do not use `Lazy<EngineInfo>` with exception caching. Before a module is mapped,
missing/corrupt output records, assets and filesystem access failures remain
retryable after repair. The loader clears its selected identity for such
failures. A descriptor cache must remain empty after every exception. Existing
post-map bootstrap failures remain latched by the loader and are not converted
into retryable failures. Do not use a global `EngineId -> EngineInfo` shortcut:
that would skip new descriptor identity checks and per-assembly resolver setup.

## Required behavioral regression additions

Existing A02 cases are a useful base, but several only exercise explicit
`PathOptions` and therefore would miss a broken null-only cache.

| Case | Added observable assertion | Existing coverage to retain |
| --- | --- | --- |
| Concurrent first null call | Install a valid real output record, start 64 null-option calls together, require identical returned metadata and one actual native bootstrap | `Concurrent` currently passes `PathOptions` to every call |
| Options after cache publication | Prime null success, then require failures for wrong bytes, missing or relative paths, null/default/duplicate/oversized capabilities and missing advertised capability | `Options`, `CachedOverride`, `Coexist` |
| Mutable option snapshot | After null priming, inspect an options object with a mutable capability list; change the list to an unsupported capability and require the next call to fail | Existing mutable-list test occurs before explicit default-cache priming |
| Independent conflicting descriptor | Prime original null success; new descriptors differing in bytes, ABI, package version or capability mapping must fail; original remains usable and bootstrap count remains one | `Conflict` currently does not prime null before conflicting descriptors |
| Default pre-map repair | Same descriptor first fails on absent or malformed default output record, then succeeds after valid repair and publishes only that success | `OutputRecord` already repairs malformed record; add absent/default retry transition |
| Resident default versus explicit override | After null success, delete or alter the on-disk output/asset test copy; default still returns resident metadata while an explicit override must rehash and reject the missing/changed file | Existing behavior promises resident reuse and explicit override verification |
| Post-map failure latching | Keep identical exception identity on repeated failed bootstrap and reject a conflicting descriptor | `LatchedFailure` |
| Per-assembly resolver ownership | If an existing fixture can supply another static facade assembly with the same identity, its first inspection must still bind that assembly and permit its native import | Real package consumer/coexistence path; do not introduce dynamic assembly scanning |

Assertions should use the public behavior, actual native fixture bootstrap count
and package imports. Avoid tests that only inspect a private cache field. A
steady-state no-allocation observation can substantiate a stated cost guarantee
after implementation, but cannot replace correctness or application timing.

Run the complete A02 JIT and actual AOT verifier once at the selected candidate,
including its real NuGet consumer and resolver negatives. Because the cache is
shared, preserve A17 codec, A18 async proof, extension proof and relevant
database/server package construction smoke checks. It does not change native
ABI ownership, cancellation or error containment; additional unrelated stress
tests should be driven by concrete changed risks or required repository gates.

## Measurement decision

First obtain exclusive profiles and fixed-load samples from the frozen before
binary. If descriptor inspection is material, compare the minimal candidate
using the same small-codec array/owned single-caller and concurrent cells, then
the frozen mixed application load. Keep direct miniz as the boundary reference.
Report codec-call and full operation/arrival times separately: the controller's
byte oracle/JSON observations are outside the codec call but part of complete
application throughput. Revert or decline the candidate if its application
benefit is within the A21 noise range or if any preserved behavior regresses.

## Test-only implementation checkpoint

Product test commit `015b0c0` implements four focused cases in the existing A02
verifier without modifying `EngineDescriptor`, `EngineModuleLoader` or any other
runtime source. `default-concurrent` synchronizes eight dedicated first callers
for 64 null inspections, checks each immediately usable native import, shared
metadata identity and one actual bootstrap. `default-retry` repairs missing and
malformed default records plus missing and wrong-hash assets on the same
descriptor, entirely before mapping. `default-options` primes default success,
then checks explicit paths, invalid/missing/mutated capability requirements and
continued resident use after unlinking the test output. `default-conflict`
checks independent descriptors differing in bytes, ABI, package version and
capability mapping after the original null path succeeds.

The verifier inventory includes these cases for both JIT and actual Native AOT
execution. The copied fixture paths are private to each case; only never-mapped
bytes are rewritten, while resident copies are unlinked during cleanup. Root
and the separate protocol agent independently read the patch and reported no
source blocker. At this checkpoint, the cases have **not been compiled or
executed**; the active measurement window prohibited such work. Root will run
the appropriate existing A02 gate with the selected runtime candidate. The
tests assert existing public behavior and do not require a cache implementation.

## Observed allocation: attribution remains open

Root's completed `ROOT/perf01-evidence/diagnostic/codec-split-384-001/` observes
baseline product `ea5fa528035d025bd7a28698ee7c71194432236c` through preparation
002, manifest SHA-256
`4a448f9f9a9e3b9dd1887fced2aae2da33280aa6b6ca7e3c9ef416fe50fc9c87`.
It uses two target workers on CPUs 2,3 and the controller on CPUs 0,1, with
384 planned operations per second. All 23,061 measurement operations completed
correctly over a 60.050331522-second actual dispatch span. It remains a
layout-selection diagnostic, with no before/after or 30-minute acceptance credit.

The operation records measure `GC.GetAllocatedBytesForCurrentThread()` around
each synchronous public codec call, before payload validation and owned-result
release; see `tests/Perf01.Codec/Program.cs:161-190` at driver `d14be543`.
Read-only aggregation of the existing records finds 11,516 of 11,531 successful
owned calls at exactly **2,784 allocated managed bytes**. Fifteen owned calls
report higher values. Selected group means are:

| Payload and operation | Interface | Successful calls | Mean allocated managed bytes per public call |
| --- | --- | ---: | ---: |
| 256 B compressible, compress (case 0) | Owned | 1,440 | 2,784 |
| 256 B compressible, compress (case 0) | Array | 1,441 | 2,920 |
| 4 KiB compressible, decompress (case 2) | Owned | 721 | 2,784 |
| 4 KiB compressible, decompress (case 2) | Array | 721 | 6,904 |
| 4 MiB compressible, decompress (case 6) | Owned | 144 | 2,784 |
| 4 MiB compressible, decompress (case 6) | Array | 144 | 4,197,112 |

The 4 KiB and 4 MiB array/owned allocation differences are respectively 4,120
and 4,194,328 bytes. This is consistent with the source's additional output
array, but this mixed diagnostic is not a paired latency experiment. The
constant owned-call cost makes shared managed preparation a concrete candidate
for profiling. It does **not** establish that descriptor inspection accounts
for all 2,784 bytes: `CodecHandle`, `NativeBuffer`, `NativeResourceOwner`, and
other managed/runtime work occur in the same bracket. Native allocation and
hardware memory traffic are not measured by this counter. Attribute any removed
cost only after the frozen candidate's profile and equivalent-load comparison;
retain owner construction and concurrency semantics.

Evidence already committed by root:
[32-group diagnostic summary at Plan ab893999][diagnostic-summary]. Raw
`operations.jsonl` SHA-256 is
`4d57985752b3f3340d7e5e7cb44c1397a17c8d6074257735ece85b4766501d03`;
the driver's `summary.json` SHA-256 is
`08d9fa2c429e51cef8f4739aa85c0805327b6c3721dd51bf3f416e00d02091b6`;
`result.json` SHA-256 is
`e64fdb825c653666ab52b9729ae0afc4acf4a6a6746c8674bc85d0fdc892739c`.
The additional distribution above filters raw rows to measurement/ok/owned,
then counts `target.managed_allocated_bytes`; no new load was run.

[source-binding-wasmtime.md](source-binding-wasmtime.md) supplies a pinned
external binding comparison for reusable successful metadata and explicit owner
lifetime. Its source patterns are design evidence, not a prediction of the
candidate's measured benefit.

[diagnostic-summary]: https://github.com/IzuSharp/Plan/blob/ab893999e45991b1f45b10af31decc3f124dc2c0/ledger/evidence/batches/Perf-01/observations-before/codec-split-diagnostic-summary.json
