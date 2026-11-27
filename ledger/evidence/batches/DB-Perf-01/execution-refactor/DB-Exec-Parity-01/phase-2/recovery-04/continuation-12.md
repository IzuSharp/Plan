# Continuation12 — independent owner cleanup before the frame08 comparison

**Continue the finite short-only experiment; no long run is selected.** The
retained performance strategy is still integrated05. A separately reviewed
correctness fix is now in Korda #40. The bounded final-frame rental08 implementation
remains isolated and has no measured benefit or adoption credit.

## Direct answer about remaining optimization space

The last completed same-round text1000 comparison still gives retained05/Dapper
client CPU ratios of **5.55 / 7.10 for SQLite and 7.94 / 9.42 for PostgreSQL**.
Managed allocation ratios are only about 1.01. These measurements show a substantial
remaining execution-cost gap, not a promise that all of it is removable. They
belong to the original05 artifacts in [Continuation10](continuation-10.md); do not
relabel them as measurements of the new cleanup or frame08 source.

The completed local-queue experiment07 is rejected and its optional mixed/extra
rounds stay closed. Historical runtime-spin sensitivity is already measured; no
new spin setting, text1000 repetition or long campaign is selected here. The next
resource target remains the measured 60,504 B final array in related32, about
11.7% of its 516.1 KB whole-process allocation. That target does not explain the
several-times thousand-row CPU gap, and frame08 has not yet demonstrated a saving.

## Source-confirmed inherited ownership defect

Reviewing the required post-compile failure boundary found a pre-existing issue
in both Plan and CTE construction. The old object initializer first adopted the
native result in a finalizable DatabaseOwner, then evaluated allocating metadata.
If metadata threw, the catch released the raw handle while the temporary
SafeHandle still owned it. The actual native registry uses storage addresses
without generations. A later repeated release can therefore affect another owner
if that address has been reused.

The [independent source report](frame-pool08-implementation-12/inherited-owner-failure-review-01/README.md)
binds the actual managed/native code and locked-runtime SafeHandle implementation.
This is a source-confirmed failure condition. No real database corruption,
forced OOM or address-reuse incident has been observed in these new steps.

The independent fix computes complete Plan/CTE metadata inside the existing
raw-owner try/catch **before** constructing DatabaseOwner. Its constructor sets
the handle only after all checks, as its last operation; the subsequent existing
auto-property assignments do not allocate. Validation, native calls, status/null
checks and origin publication keep their order. Metadata now precedes wrapper
allocation, so the exact allocation/OOM ordering is explicitly changed.

The [fix review](frame-pool08-implementation-12/independent-owner-cleanup-review-01/README.md)
passed its finite source/identity/impact checks. Runtime synthetic failure checks
are still pending; source review does not replace them. No shipping fault hook,
new callback allocation, public API or native ABI was introduced.

| Identity | Meaning |
| --- | --- |
| Local `69b2383dadc280f1a81de592592a1442069eed0c` | Independent cleanup on integrated05 |
| Published Korda `106fe68b6f6c2537f478daf65a71ab97cc4b15ff` | Same tree `f7660759bba43ae83324620e2fb731efd479c3b5`, normal PR40 update |
| Isolated `74917fd4f5e483a8cceeeaa56d5b59026e6ba1d2` | Original frame-pool08 product-only change |
| Isolated `b0a6f2294512b354eb9ca203f9de2e5763c38a14` | Same cleanup applied to08, tree `7d2b760c112ecc20044fde910654f89380cf4921` |

The cherry-pick needed only indentation adaptation inside Seal's new outer
try/finally. Its actual 11 added and 2 removed lines are the same two cleanup
blocks. Original product-only08 evidence remains unchanged.

## Preserve the causal comparison

Both sides of the next comparison carry the same cleanup. The new ordinary
baseline family is `ownership05`, local package version `0.1.0-parity05.2`, built
from local69b. Candidate family `frame-pool08`, version `0.1.0-parity08.1`, adds only
the selected pool strategy plus its separate correctness tests. Original05
consumers remain intact. Cleanup is never credited as a buffer-pool benefit.

[Continuation11](frame-pool-08-hypothesis.md) still specifies the allocation,
logical-length, clearing, synchronous borrowing and error/ownership contracts.
Complete the affected Binding/Relations Native AOT correctness and separately
identified local mechanism/fault checks first. Synthetic faults must occur at
the actual metadata/origin/encoding site; do not move them to make the old
ownership sequence appear safe. No genuine OOM is needed.

The [reviewed ordinary controller](frame-pool08-implementation-12/independent-ordinary-controls-review-01/README.md)
keeps **twelve** business processes: two providers, ownership05/candidate/Dapper,
then reverse, related32, C1, persistent sessions, batch32, 2048 measured businesses
and 128 case-specific warmups. The existing 32-row mixed35 correctness preflight remains
before those warmups and outside the measurement boundary. Actual inputs will
be bound after builds; source-only controller review is not input verification.

Every route uses its existing five-second released-idle option. The source puts
this observation after the measured CPU/allocation boundaries and all
worker/session/source drain, with no forced GC. Report it as released-idle RSS,
not the lowest possible RSS or the private pool's exclusive footprint. Keep
cold pool allocation and static residency explicit and PostgreSQL server costs
separate. No new broad matrix, pressure campaign or long run is a pending gate.

## Recovery, space and existing CI

[Archive05](https://github.com/IzuSharp/Plan/tree/1c6ee6b91446486689990a72cc7c3557682a7502/ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/phase-2/recovery-04/archives-05)
now preserves the complete closed07 source, ordinary consumers, correctness,
machine-code analysis, raw short results and reviews. All **100 published files /
35,366,017 bytes** passed actual remote Git byte/length/SHA256 readback. Its
748 expanded originals and six artifact aliases retain their exact manifests;
the alias exercise was check-only, not a fresh full filesystem restore. Only the
twelve verified local compressed duplicate parts were removed afterward.

The ten separately reviewed, positively retired legacy PostgreSQL data directories
were removed for actual affected AOT/short-test space. Their 983 surrounding raw
files were unchanged and 60 configurations copied/read back. The removed inventories
accounted for 653,553,664 allocated bytes; observed free space rose by 653,545,472
bytes, including concurrent filesystem effects. Nested sampled-small03, four pg_ctl-only exclusions and the
earlier two completed retirements were outside this operation. The exact
receipt and exclusions remain evidence; do not retry the completed deletion.

Plan Continuation11's existing CI run45993241805 passed. Design11's two existing
CI runs45993389137/45993389143 also passed. New Korda cleanup CI remains pending
at this checkpoint. The committed impact was read before push: existing shared
Linux checks and independently routed SQLite/PostgreSQL package/API/correctness/
AOT checks are selected. Native and older test reasons are cumulative unmerged05
changes; the new fix is managed Binding only. No CI benchmark, profiling,
calibration or pressure action was added or indirectly invoked.

All copied [source and receipt records](frame-pool08-implementation-12/source-records.json)
preserve their bytes. At this checkpoint no08 ordinary workload has run and
no08 result is accepted. Continue local builds/tests from the existing task root,
not earlier completed07 or tail06 gates. Independent final review, normal merges,
existing main CI/rule-selected release and public NuGet AOT verification remain
authorized and incomplete. Go drafts Plan35/Korda39 stay unchanged.
