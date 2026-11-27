# frame-pool08 local diagnostics01 — bounded resource and fault controls

## Result and identity

Passed one Release Native AOT build at isolated diagnostic head
`c429effc45c6fcd946c999553d0420b71369abfe`, tree
`8255e3ba82eb9d63febcdd394fe506950fd92f35`. It is the reviewed03 overlay on
ordinary13b, not a performance consumer or a shipping package. The outer
controller observed two serial direct child process launches: fault PID126
(parent controller10) and resource PID133 (outer parent2), each exit0. Those
PIDs are in the inherited command namespace; no procfs/startTicks mapping is
claimed. The same ELF/DBG and fixture SHA, plus all tracked source bytes,
matched after both processes. Complete commands, generated-source hashes and
ELF build IDs remain in faults/receipt.json. No database server was started.

## Fault cleanup:10 cases,102 assertions

Each of two semantic profiles executed five synthetic controls against the real
C++ command ABI fixture: post-rent Encode; Seal Metadata; CTE Metadata; Seal
origin publication; CTE origin publication. All ten hit their actual armed
site exactly once and retained the original exception object. Each Seal used
the controlled private rental; each CTE kept its fresh-frame path.

The two post-rent Encode controls made zero native submissions and zero owner
releases. The eight Metadata/origin controls each observed one real native OK
nonzero result and exactly one corresponding release/forward after the final
forced-finalization drain. No duplicate release was suppressed. Native owner
counts remained4→4 within each failure interval and were zero after the suite.
Frame slots were returned once and fully cleared; the CTE controls left the
private-pool slot untouched. The protective duplicate interceptor would fail
the control while avoiding a fixture double-delete; it did not activate.

This is positive cleanup evidence for the common ownership fix and pool
finally. The old unsafe05/749 path was not run. Native result addresses repeat
across separate completed fixture cases; that is not an executed reproduction
of the old production-registry ABA risk. No new native owner was allocated
within a pointer-specific observation interval. The faults are synthetic
exceptions, not real OOM events or new public business error semantics.

## Resource mechanism: one fresh process,99 assertions

The4096-byte stack Seal completed before any private-pool access, with zero
private-pool creations and zero rent/return records. The first eligible graph
and every subsequent eligible graph had logical length60480 and physical
rental length65536. These are valid size-controlled single-root fixture graphs,
not the actual32-related-row business query. Six fixture compiles completed,
with zero final native owners and zero actual database SQL executions.

| Controlled operation | Actual array identity | Rent allocation delta | Return allocation delta | Pool creations | Returned clear range |
|---|---:|---:|---:|---:|---:|
|4096 stack|none|no rent|no return|0|none|
|60480 cold|1|67000B|0B|1|65536B|
|60480 warm1|1|0B|0B|no additional|65536B|
|60480 warm2|1|0B|0B|no additional|65536B|
|60480 warm3|1|0B|0B|no additional|65536B|
|60480 forced miss|2|65560B|0B|no additional|65536B|

There are exactly11 raw boundary records: one nested pool initialization and
five actual rent/return pairs, all on managed thread1, with no overflow or
foreign-thread event. The four deliberately held64KiB slots had distinct
identities1,3,4,5; the miss returned identity2. All four held slots were returned
once in finally, outside the measured Seal boundaries. The max bucket has no
larger fallback bucket in the locked private Create(65536,4) implementation.

The first outer Rent interval includes the nested ArrayPool.Create interval
of1400B. Its raw counters show40B before that nested interval and65560B after
it. The40B allocation kind is not separately identified. The later65560B span
matches the forced-miss boundary amount and is consistent with a65536-byte
array plus24-byte x64 managed overhead; this comparison does not turn all
cold-boundary bytes into exclusively attributed array cost. Runtime holder
initialization and EventSource contributions are not independently decoded.
Never add the1400B nested interval to the67000B outer interval.

ClearBytes means the full actual array.Length range passed through
Return(clearArray:true), supported by the locked runtime's clearing behavior
and complete zero readback. It is not hardware store-byte sampling. The five
returns cover327680B in total. Compared with the old60480-byte exact frame,
each return clears5056B of additional bucket tail. This is a resource tradeoff,
not evidence of a CPU improvement. The cold private pool also has initialization
allocation and the known cache-miss array is larger than an exact frame.

## Limits and decision boundary

The fixed32-entry recorder and measuring API were initialized before the first
private-pool access. Record writes, formatting, file I/O and the full-zero scan
were outside each measured allocation interval. The nested init record writes
use a preallocated value-type entry. The recorder keeps strong array references,
and return readback is valid only in this serial controlled process. These
choices alter liveness and work; they provide no ordinary CPU, latency, RSS,
throughput, GC-pause or whole-query allocation credit.

The three warm controls directly observed zero additional managed allocation
inside the actual Rent and Return boundaries. They do not establish0B for all
of Seal, framework execution, DTO creation or the mixed workload. The prior
60504B fresh-frame allocation evidence remains the old baseline's measurement;
no additional baseline diagnostic was built or run. The actual dual-provider
ordinary12 comparison must establish any end-to-end allocation/CPU benefit and
regression before product adoption. No new business matrix or long test ran.

The earlier local overlays01 and02 remain source-only identities, never run.
The ordinary Binding557 and Relations1244 results are separate correctness
suites, and the retained Relations01 compile failure remains a failed attempt.
Do not add their assertions to these two diagnostic counters as one scope.
