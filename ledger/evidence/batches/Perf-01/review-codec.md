# Perf-01 independent codec harness source review

Reviewer role: database/ORM task owner, separate from the codec harness author.
Reviewed repository: `IzuSharp/NativeWeave`.
Reviewed codec harness commit: `e0df0a8992c7ad6ec51b223e6b323e85837d7797`.
Scope: `tests/Perf01.Codec`, read-only review; no product source or codec-owner
worktree was edited by this reviewer. This review establishes source properties,
not an executed performance result, formal long-stage acceptance or an external
maintainer review.

## Findings and resolution

The initial source was reviewed before its first commit. Concrete findings were
sent to the codec owner and integration owner. The final commit above was then
read again to verify these changes.

| Concern | Initial finding | Reviewed resolution |
| --- | --- | --- |
| Direct Rust build equivalence | The standalone comparator had a different release optimization profile. | `native/Cargo.toml` now matches thin LTO, one codegen unit, unwind panic and debug-info stripping. Exact compiler/target flags still belong in each prepared manifest. |
| Same-driver measurement | Artifact hashes were checked, but the current driver and A21 were not compared with their prepared hashes. | `driver.py::measure` checks `driver_inventory`, A21, executable/native/package artifacts, copied consumer sources and resolved consumer locks. |
| Partial runs | Dispatched but unfinished requests and actual phase start could be lost before `schedule` returned. | Dispatch events are persisted immediately. Failed runs retain unfinished request records, IDs, partial phase progress and zero long-stage credit. |
| Long-run aggregation | Reading every JSONL row into full dictionaries could add substantial avoidable memory use after a high-rate 30-minute run. | `summarize` reads JSONL incrementally and retains compact integer latency arrays and counters. Memory still grows with the finite sample count; it does not become constant-space. |
| Planned versus actual load | The original aggregate offered count could include generator-capacity skips without a separate sent count. | Phase counters distinguish planned, attempted, sent, admitted, completed and terminal outcomes. Ready-event worker/queue settings are checked against the requested plan. |
| Overload recovery | The first controller version immediately performed its final drain. | A separately counted low-rate recovery phase now runs in the same live target before drain and idle. |
| Comparator labels | Direct Rust and ZLibStream reused array/owned workload labels despite different result interfaces. | README and plan identify direct `Vec<u8>` results and the managed-array alias. Managed full-operation/arrival results are explicitly not strict semantic equivalents. |
| Copy accounting | A derived copy count might be mistaken for all allocator/workspace copying. | The documented count is the C#/Rust output payload copy only; native workspace initialization/growth and allocator internals are not measured. |

## Source properties checked

`Program.cs::Worker` invokes actual `ZlibCodec` array/owned APIs, checks every
produced byte against the frozen corpus, and separates public-call, consumption
and ownership-release timing. The standalone Rust target invokes the same
locked miniz core API with the same level-six zlib settings, bounded allocation
growth, full-input consumption and exact output checks. Native and direct
preflights reject truncated, corrupt, trailing and concatenated streams and
oversized input or decoded output. ZLibStream's buffered input does not expose
the same strict trailing-data rule; its limitation is stated explicitly.

The external controller checks request identity, admission/completion order,
byte counts, encoded bounds and timing decomposition. Target queue admission is
bounded; controller in-flight capacity and scheduled dispatch lag can invalidate
a measurement. A requested duration has a small declared dispatch guard, and
the actual first-to-last dispatch span must still reach that duration. Warmup,
recovery and idle have separate counters and receive no measured-load duration
credit. Drain checks native owners, active operations and capacities where those
counters exist. `/proc` mappings verify the actual loaded codec native hash.

## Remaining execution obligations

No remaining source blocker was found within the reviewed concerns. The
integration owner must still freeze the final arrival rates, worker/queue
counts, CPU affinity, deadline, p99 and memory criteria before product changes;
inspect generator CPU/dispatch lag on actual cells; run independent interleaved
short processes; and execute both matching 1,800-second stages with complete
correctness, drain and resource receipts. Compilation, check-only preflight and
this review cannot substitute for those measurements.

Primary reviewed source locations are `tests/Perf01.Codec/driver.py`,
`tests/Perf01.Codec/Program.cs`, `tests/Perf01.Codec/native/src/main.rs`,
`tests/Perf01.Codec/native/Cargo.toml` and `tests/Perf01.Codec/README.md` at the
commit stated above. Product semantic parity was checked against
`src/Engines.SyncProof/ZlibCodec.cs` and
`native/engines/sync-proof/src/lib.rs` at the unchanged baseline
`ea5fa528035d025bd7a28698ee7c71194432236c`.
