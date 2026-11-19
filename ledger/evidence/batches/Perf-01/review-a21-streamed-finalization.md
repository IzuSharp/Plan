# Perf-01: independent review of compact A21 finalization

## Disposition and review scope

**Source review passed** for the scoped child-controller index/writer changes
listed below. The protocol agent reviewed the database agent's working tree on
CPU 8, starting from product commit
`2804fe42e77dba61093be94380daceb1a06ccf3e`. The reviewed snapshot was uncommitted
when these file hashes were captured. This review performed no test execution,
application workload, build, or performance measurement. The author owns the
finite executable gates; the codec agent separately reviews the parent DB
reader, validation and summary calculations.

| Reviewed file | SHA-256 |
| --- | --- |
| `src/Benchmarks.Harness/nativeweave_bench.py` | `dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53` |
| `src/Benchmarks.Domain/cell_worker.py` | `fa9105f875a28788ab13f3c461e4edfc6114d37b280c8e78d54346abc362e179` |
| `tests/Benchmarks.Harness/test_harness.py` | `7c5e0044f38887e1ebad3ad4d31544b90ff952e3ffe5b24670c988e79539d3ae` |
| `tests/Perf01/verify_long.py` | `77633e6a670201224be67fe733d24a8aeb110344f9252d29082be69d5676bd51` |
| `tests/Perf01.Database/profile_a21_generator.py` | `41bcd332157abe60e25295749caddb872e89db094f9a036937bfc6c1b5cd125d` |

The last two files were reviewed only for the new bounded reader interface and
diagnostic phase/return forwarding, respectively. This does not replace the
independent parent-reader review or revalidate every pre-existing long-run
verifier condition.

## Integrity and output findings

1. `RunState.event` retains the existing live acceptance path. Moving payload
   reconstruction into `_accepted_completion_payloads` (line 461) preserves
   raw ordinal, strict request ID, observer timestamp, outcome, successful-value
   equality and complete versioned counter validation. Duplicates and malformed
   records cannot substitute for an accepted event. The replay poison flag is
   still set before a partial replay can mutate or index accepted state.
2. `CompletionPayloadIndex` (line 550) fully exhausts the replay iterator before
   it can be used to publish output. That proves accepted-event coverage and the
   SHA-256 of the entire live-written raw stream. It retains finite numeric
   offsets/lengths, fixed-size per-line digests and accepted late-event IDs,
   without attaching payload/counter graphs to scalar operation records.
3. Random-access reads verify each exact raw line's digest and the indexed
   event identity. `_record_with_payload` (line 518) preserves the original
   field insertion order. Record emission follows scheduled ID order; late
   events follow accepted raw-stream order, including out-of-ID-order late
   completions. Full extra event fields remain in late-event evidence.
4. `write_streamed_observation` (line 598) emits bounded rows and incrementally
   dumps metadata/resources to a new `.partial` file. Its final whole-stream
   digest check also covers malformed or unaccepted raw lines. Only after that
   check succeeds is the final file atomically published. Missing, changed or
   invalid accepted data cannot publish a complete observation. A failed
   attempt is not reusable; its partial artifact can remain as failure evidence.
5. The normal `run_cell` API and the existing full rehydration mode remain
   available. The new scalar in-memory return requires both explicit compact
   retention and the new stream-output option. The cell worker opts in only
   under `--compact-observation`, and ignores that return. The on-disk object
   retains the original schema; the explanatory scalar-return marker is added
   only after writing and therefore does not enter the evidence file.

The output is emitted one row at a time. Python iteration may briefly retain a
previous row while decoding the next, so this review does not claim that exactly
one payload allocation is alive at every instruction. The relevant bound is
independent of the number of accepted payload graphs; the scalar request ledger,
finite index, histogram metadata and resource samples still occupy memory.

## Startup oracle and timing separation

The compact-only Oracle path (line 168) verifies the dataset hash, streams every
entry through the original input-token gates, and canonicalizes its expected
value before accumulating the entry. Too few/many entries and trailing JSON are
rejected. Existing bounded canonicalization limits and value equality remain
unchanged. The normal non-streaming Oracle path is retained.

In `run_cell` (lines 768 onward), indexing and publication begin only after the
target, event reader and resource sampler have stopped and the observation end
has already been fixed. The diagnostic hook marks this as post-window work.
This patch changes external observation storage; it establishes no product
performance improvement and no numerical CPU/RSS benefit by itself. Fresh
diagnostic/calibration inputs must pin these driver and reader bytes before
formal before/after comparisons.

## Finite fixture coverage inspected

The added test source checks byte-exact pretty JSON against the full path,
including Unicode, out-of-order success, duplicate/malformed inputs and late
ordering. It also checks missing or wrong raw digests, mutation of an indexed
line, mutation of an unaccepted tail, no final publication on these failures,
and one-shot behavior. Streamed Oracle tests forbid a whole-file `read_text`,
check shared equal values and preserve count/token/trailing-input rejection.
The finite child-process cases cover valid results, late timeout evidence,
oracle corruption and malformed events while reading the complete disk schema.

The reviewer found no remaining source blocker in this scope. Actual finite
test results and any subsequent source changes must be recorded separately.
