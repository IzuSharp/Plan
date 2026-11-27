# DB-Exec-Parity-01 — resumed relation deep allocation boundaries

This completes the previously committed but unbuilt `5b330a2` deep diagnostic.
It does not change a product execution path and grants no ordinary timing,
RSS, CPU, final mixed35 or publication credit. Source at
`5b330a24b55332fbbd463b146acd228ae7acbc14`, tree
`c1880288211a62f2c9da081bb4b221e3bd0a44f9`, was clean before and after the build.
It includes the previously selected private consuming-import candidate and
diagnostic scopes; the initial 31-Clone optimization is not rerun or recounted
as a new result.

## Actual execution and identities

`deep-layer/impact.json` was produced from the committed diff before building.
It selects the shared managed database/binding/relation chain and both independent
provider package checks. No workflow was changed, no performance check was put
in CI, and its release list is empty. This is a local diagnostic subset, not a
claim that all selected correctness/API/package acceptance actions ran here.

The existing verified managed-experiment packer retained exactly the original
baseline native bytes after checking package entries, native and dependency
source hashes. The packages use version `0.1.0-relation04.deep`. The unchanged
external consumer builder restored one real `PackageReference` per provider and
produced Release linux-x64 Native AOT executables, generated C#, dependency
receipts and matching `.dbg` files. The original native identities intentionally
differ from the newer `-g` native integrated group and must not be added to its
absolute resource values. `deep-layer/source-identity.json`, provider package and
consumer `build-receipt.json`, `build-commands.json` and `machine-code/identity.json`
bind the exact source/package/ELF/debug/native bytes and commands.

Builds ran sequentially, on two allowed CPUs, with the restored locked
`toolchain/environment.sh`; existing pack/build commands use `-m:1`. Both
diagnostics used `run_related.py`, 32 warmups then 128 measured related32
operations, one connection, the same 32 composite keys, and real local databases.
Other task build/count diagnostics were allowed concurrently. No observed
instrumented time is compared between providers or to earlier runs.

Each provider completed 128/128 businesses, with 53 rows and digest
`2847736615530494015` per business, zero business/oracle failures and all recorded
native owner classes zero. Each business performed one SQL; PostgreSQL retained
the existing four protocol submissions. Each trace contains 523,296 finished
records with zero overflow. All allocation scopes begin and end on the same OS
thread; all 32 prewarmed empty controls allocate zero bytes.

The original analyzer was retained and invoked without changes. The new
`analyze_deep.py` independently reconstructs the same-thread nesting from actual
start/end boundaries and verifies allocation-counter containment, nonnegative
exclusive allocation, complete request inventory, exact per-request graph/key
counts, and absence of Clone/CloneCopy. It includes the new graph-copy events
that the earlier analyzer did not list. One SQLite operation completes grouping
synchronously within the invocation; nesting handles that case without adding
it twice. PostgreSQL grouping occurs after invocation return in all 128 cases.

## Newly measured residual work

All values below are bytes per related32 business. Exact values match all 128
requests in both providers unless explicitly described as medians. Inclusive
columns include their nested scopes; they must not be summed as disjoint work.
Exclusive means outside the immediate recorded child scopes, not exclusive CPU.

| Actual scope | Calls/business | Inclusive B | Exclusive B | Meaning |
| --- | ---: | ---: | ---: | --- |
| SelectParent, median | 32 | 331,264 | 4,352 | Most cost lies in its measured children |
| Final ToList synchronous prefix, median | 1 | 95,640 | 0 | Stream creation and async start account for this boundary |
| TapeResize | 98 | 129,328 | 129,328 | Actual byte-array growth allocations, including array overhead |
| GraphFrameAllocation | 1 | 60,504 | 60,504 | Final 60,480-byte transport frame plus observed array overhead |
| GraphEncode | 1 | 73,992 | 13,448 | Graph dictionaries/lists and other work outside frame/owner-array children |
| Fresh From/context construction | 32 | 51,712 | 51,712 | Existing per-branch construction |
| EmitShape | 384 | 44,032 | 44,032 | Actual shape-table updates |
| EmitNode | 384 | 27,648 | 27,648 | Actual managed node allocations |
| BindCodec | 300 | 0 | 0 | Already has zero observed same-thread managed allocation |
| SelectionEncoding | 32 | 0 | 0 | Already has zero observed same-thread managed allocation |

`NativeCompile` is one synchronous call and its own-thread managed allocation is
zero. That statement neither measures native allocation nor excludes callbacks
or execution on other threads. The final graph frame is still copied through
the native compile contract; no buffer-lifetime change was made.

Whole-process managed allocation is 565,233.625 B/business on SQLite and
565,120.6875 on PostgreSQL. The nonoverlapping observed scope totals average
549,332.3125 and 548,585.8125 B respectively, leaving 15,901.3125 and 16,534.875 B
unassigned. These residuals include unobserved framework/DTO/harness work and
are not a framework-only measure or an exact counter-subtraction attribution.

### Actual capacity and copy sequence

The actual trace records, in both providers and every request:

- Each of 32 SelectParent branches grows `256 → 512 → 1024 → 2048`, three
  array resizes each. These account for 96 of the 98 resizes.
- The retained root then grows `2048 → 4096` during Combine of parent index 3,
  and `4096 → 8192` during Combine of parent index 25.
- Growth copies 63,488 old-capacity bytes and allocates 126,976 bytes of new
  array capacity per business; the 98 array headers account for the remaining
  2,352 B of the measured 129,328 B.
- Final graph encoding copies 32 actual tape payloads: 31 × 1,772 B private
  branches and one 4,748 B root, totaling 59,680 B. Together with the 32-byte
  envelope and 32 × 24-byte block headers, the frame is exactly 60,480 B.
- Other tape append copies remain 542 events / 51,008 payload B. Clone remains
  absent. No repeated key encoding, selection validation or node work is claimed
  removed by this observation.

`QueryCommand.Append` performs the growth; `QueryCommand.Encode` constructs the
final graph; `QueryCommand.Emit` owns the shape/node work. The exact matched AOT
images and debug build IDs were resolved for Append, Emit, Encode, Seal, Column
and Metadata. `machine-code/` retains actual ELF disassembly, call instruction
addresses, exact direct-call targets when named, and `.dbg` source/inline stacks.
This establishes executed-code identity and allocation call sites, not sampled
CPU costs or runqueue causality.

## Smallest next causal experiment, not yet a selected product change

The measured tape-growth repetition justifies a separate private relation
capacity experiment. It does not justify increasing every QueryCommand's
initial 256-byte array or caching complete user queries.

Proposed scope: after SelectParent has constructed the first branch, take a
bounded capacity hint from that admitted private command. For later temporary
branches, reserve once while their tape is still empty, before the unchanged
SelectParent construction. Keep the existing geometric growth fallback and
every existing Append/RecordQuota, node/depth/envelope, parameter, projection,
snapshot, error and ownership check. Do not reuse literal bytes or owners and do
not introduce a global cache. Public From/Combine behavior remains selected as-is.

For the observed equal-size 32-parent case, reserving 2,048 B for each of the 31
later branches would replace 93 existing growth allocations with 31 reservations.
The first branch and two root growths would be unchanged. The falsifiable
predictions are therefore:

| Predicted counter | Current measured | Proposed same-case prediction |
| --- | ---: | ---: |
| Growth/reservation allocations | 98 | 36 |
| New capacity B in those allocations | 126,976 | 79,360 |
| Their managed allocation B, including observed headers | 129,328 | 80,224 |
| Their copied B, if empty reserve replaces without copying | 63,488 | 7,936 |
| Final payload/frame bytes | 59,680 / 60,480 | Unchanged |

The predicted managed reduction is 49,104 B/business, roughly 8.7% of this
candidate's whole-process allocation. These are predictions from the current
actual event counts, not candidate measurements. The initial 256-byte array per
branch would still be allocated and discarded by this minimal design. An early
reserve is not free: 31 new 2,048-byte arrays remain, and allocating them earlier
can affect GC and residency even if current final capacities match.

The first key may be much wider than later keys. A bounded hint policy must
explicitly limit overreservation, and must be justified against different
key widths and parent counts, not simply assume all branches match. A fixed
capacity ceiling changes memory tradeoffs and should be documented and measured.
An exact-size estimate that reimplements wire-layout formulas would carry extra
maintenance/contract risk; it is not required for this first experiment. An
ArrayPool-backed final graph frame is a separate candidate with retention,
return-on-exception, zeroing and contention risks and should not be bundled.

Before any ordinary A/B: prove the same complete command and native result,
unchanged resource-limit/error ordering, input snapshots, public Combine source
independence, internal consume ownership and cancellation/mapper cleanup. Include
parent counts 1/2/32; small-first/large-later and large-first/small-later key
controls; finite envelope/node/depth rejection; empty input; and repeated parent
positions. Diagnostics must show exactly which allocations/copies disappeared and
which merely moved into construction. Then use matched uninstrumented real
packages for serial AB/BA, preserving process allocation, peak/post-release RSS,
CPU and tail metrics. Drop the hint if resource cost increases without useful
repeated benefit or if it changes the contracts.

## Existing candidate set and remaining gates

- Worker-D: its current repeated thousand-row CPU gain and corrected full AOT
  suite support integrated evaluation; own boundary/count review remains separate.
- Decimal canonical parsing: source review found no new valid-input domain,
  lifetime or error-order change. Its PG money1000 native-allocation saving is
  real, but repeated money1 CPU regression remains explicit until the combined
  candidate and scheduler-boundary evidence explain or bound it. Do not claim
  universal benefit from the canonical-parser change.
- SQLite prepare hint removal: actual resource saving supports retention for
  integrated evaluation. CPU benefit is not stable. It does not implement a
  physical statement cache, and existing DDL/prepare/bind/step/finalize contracts
  remain applicable.
- Private relation consuming import: retain provisionally. It removes exactly
  31 clones and preserves public Combine snapshots; the new evidence confirms
  substantial construction remains. Its small peak RSS and Gen1 increase and
  unsettled public-control tails remain process-level observations.

The four existing candidates still require matched integrated package/API/native
and AOT correctness gates, ordinary per-case negative controls, both-zero-refusal
cost and historical-pressure comparison, and the requested four frozen serial
1,800-second mixed35 cells. The proposed capacity experiment is not part of that
set until measured independently. No additional relation product change was made
in this diagnostic continuation.
