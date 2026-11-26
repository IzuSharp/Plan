# DB-Exec-Parity-01 — decimal configuration strategy for Design integration

Author: `pg_numeric_audit`. Product candidate: `23845016b707a2876e6777cf935667dc546ca6d5`.

Integration status: the source-bound allocation mechanism, independent source reviews, both standalone package/AOT builds and necessary native correctness suites have passed. Root-controlled ordinary `codec-b-ordinary-02` is complete and independently reviewed. Its repeated PG money32/money1000/wide32 CPU/p50 changes support retaining the targeted candidate for integration. Small adverse control observations remain explicit below. This text does not accept final mixed35 parity or release. Root can insert the strategy section into `docs/database/execution-parity-01.md` and attach the exact Plan evidence commit alongside the reviewed ordinary result. No Design, Plan, product or remote files were edited by this preparation.

## Selected strategy: parse canonical decimal configuration without JSON trees

Configured PostgreSQL decimal (codec 13) retains its current validation boundaries and reads the existing canonical precision/scale configuration with a bounded primitive parser. The accepted byte language remains exactly `{"precision":P,"scale":S}`, with precision 1–29, scale 0–28 and scale no larger than precision. The parser requires the existing key order, ASCII punctuation, unsigned integer spelling without leading zeroes and no trailing bytes. Integer conversion reports overflow; no temporary JSON object, string normalization or decimal-string reconstruction is needed on this valid path.

All configurations rejected by the primitive parser continue through the original JSON validation and error path. Unsupported provider/profile and missing-configuration checks still occur first. An invalid configuration retains its previous error before OID/value failures. The implementation does not broaden acceptance of whitespace, alternate key spelling/order, duplicate keys, strings, floating numbers, signs, escapes, embedded NUL or extra data. It adds no cache or mutable shared state: changing a Codec configuration between calls is immediately visible.

The same primitive parser supplies precision/scale to the final scalar range check after the existing configuration, fixed-width, flag, coefficient and canonical-value checks. The implementation does not remove the three existing Codec validation calls per decoded non-NULL PG decimal. NULL handling, provider OID compatibility, fresh result metadata, field-size/byte admission, decimal scale/precision loss checks, exact 96-bit coefficient rules, errors, cancellation, stream lifetime, transaction outcome and safe connection return keep their existing ordering and semantics.

The native execution, buffering, handoff and completion strategy is unchanged by this codec decision. The C# Fluent surface, generated reader contract, Native AOT and the two independent PostgreSQL/SQLite packages remain intact. SQLite still rejects ordinary numeric-decimal codec 13; FixedScaleMoney/id 15 and its valid SQLite storage remain on their original path. Shared native-source routing requires both provider package gates even though the selected hot path is PostgreSQL-specific.

## Evidence that selected this scope

Source scopes on the original real PostgreSQL/Release Native AOT workload established four configuration JSON parses and three configuration validations for every successfully decoded non-NULL decimal. The fourth parse was confirmed after an initial three-parse hypothesis failed: `postgres_compatible → postgres_oid → check_profile` repeats validation before the scalar validation path. That failed attribution attempt is retained.

With the candidate, all three validation calls remain and the four configuration JSON parses become zero. For the same money1000 SQL, DTO, result digest and row count, the inclusive decimal-decode scope changes from 48,000 to 1,000 public malloc/calloc calls, and from 1,135,980 to 3,980 requested bytes. The measured reduction of 47,000 calls/1,132,000 bytes exactly matches the prediction recorded before implementation. All per-configuration validation/range allocations disappear. Two independent diagnostic processes per business reproduce every count and byte result; money1/money32/wide32/customer-totals show the same per-decimal mechanism. An Int64 numeric32 control remains zero throughout.

These source-scope results do not establish whole-heap live bytes, RSS, managed allocations, wait time, exclusive CPU or end-to-end speed. Nested allocation scopes are inclusive and cannot be added together. The pinned ordinary native ELF retains the primitive-parser call and old JSON error fallback at the corresponding sites; actual ELF/debug/generated/package identities and disassembly remain separate from diagnostic-image identities. Ordinary before/after and Dapper.AOT results belong to the Plan comparison, not to this design's mechanism counters.

The original workload named `numeric` and the earlier narrow Int64/string thousand-row phase do not use configured decimal. This decision therefore cannot be used to explain their repeated-row CPU gap or claim general query parity. The relevant original mixed35 cases are money, wide and customer-totals.

## Retained, rejected and deferred choices

| Choice | Disposition | Reason and boundary |
| --- | --- | --- |
| Exact primitive parsing on the canonical decimal success path | Retain for integration after source-resource proof and ordinary02 review; combined/final acceptance remains separate | Source/machine-code path and repeated allocation counts identify four unnecessary JSON trees per value; exact acceptance equivalence and correctness tests support the narrow replacement. |
| Existing configuration/profile/OID/scalar validation locations | Retained | Validation frequency stays three per decimal, avoiding new trust, invalidation or error-order assumptions. Eliminating tree construction addresses the measured cost. |
| Original JSON rejection path | Retained | Preserves established malformed/type/key/range/canonical diagnostic classification and text; unsuccessful fast parsing is not a new public error. |
| A cache attached to mutable Codec/configuration or a global configuration map | Not selected | Adds lifetime, invalidation, synchronization and memory-policy obligations absent from this proof. The stack parser already removes all measured configuration allocations. |
| Removing repeated validation or marking arbitrary values trusted | Not selected | Changes trust and failure-order boundaries; no independent evidence or contract proof in this causal experiment justifies it. |
| Extending the parser rewrite to SQLite FixedScaleMoney/id 15 | Deferred | This experiment has no comparable source-allocation proof for that path. Shared-source regression still covers it unchanged. |
| Rewriting binary PG numeric conversion or eliminating its residual allocation | Deferred | The whole decode still records one small allocation per value. The unchanged conversion vector is a source-supported explanation, but the residual allocation site has not been independently instrumented or accepted in ordinary A/B. It is a separate hypothesis. |
| Broad metadata, ownership, protocol or scheduling refactor within this change | Not selected | No part of the codec allocation proof requires those changes; their separate hypotheses and semantic proofs remain with the corresponding execution-path work. |

## Correctness and routing required for integration

All 463 legal precision/scale configurations are exercised through Codec validation, scalar validation and PG decoding. Invalid tests include noncanonical/duplicate/reordered/escaped/missing keys, signs, leading zeroes, wrong numeric types, overflow, NUL/trailing data, configuration mutation, profile rejection, and configuration versus invalid-OID/value precedence. Existing nonzero, precision-loss, scale, exact 96-bit, SQLite canonical storage and PostgreSQL binary tests remain active.

The candidate passed the existing scalar/contracts, real PostgreSQL+SQLite provider, PostgreSQL protocol, completion, queued cancellation, transaction and all 11 PostgreSQL component cases, plus the independently built SQLite fixture/ABI. Two independent source reviews found no blocking parser-equivalence, overflow or error-order issue. Exact diagnostic-text preservation is grounded in the retained fallback implementation; the new suite does not claim to assert every error string individually.

The committed diff selects native checks and both independent public packages via the unchanged impact planner. Both actual standalone package consumers are built as Release Native AOT with retained generated C#, ELF, matching debug symbols and exact native/package identity. Final integration still requires the combined candidate's selected ordinary/public consumer regressions, normal review/merge, existing CI, rule-triggered release and public NuGet AOT execution. No benchmark, diagnostic counter, profiling, calibration or pressure invocation belongs in CI.

## Scope of the ordinary02 correction — evidence note for Plan

The first ordinary attempt (`measurements/codec-b-ordinary-01`) failed before the measurement gate. Dapper was launched for `money --rows1 --batch-rows32 --verify`; `--verify` first executes all 35 cases during warmup. Its existing frozen related reader requires exactly 32 parent keys (`Rows==32`, `BatchRows>=32`), so `related` throws and the process-lifetime sticky oracle records `Phase=warmup, CaseId=related`. This is an unsupported harness combination for that unrelated frozen case, not a money-result or candidate codec failure. Preserve the command, exception and oracle failure; do not grant timing credit or pool the two completed preceding Korda cells with the replacement attempt.

In `codec-b-ordinary-02`, all three routes (baseline Korda, candidate Korda, Dapper.AOT) omit only the preliminary all 35 sweep for the per-business screen and perform 64 warmups of the selected business. Both implementations still call `Validate` unconditionally after every executed business in warmup and measurement, comparing row count and digest. `CorrectnessOracle.RequireClean` remains before the timing gate. This correction does not disable result validation. The mixed35 cells keep rows32/batch32 and `--verify`, retaining their all 35 correctness gate.

Actual retained consumer source confirms baseline/candidate Korda Measurement and Workload bytes are identical. The relevant Dapper Measurement/Workload/frozen-related sources are also identical across providers. The isolated ordinary screen holds prepared mode, persistent connection, one worker, rows/batch/dataset, affinity and operation count constant; baseline/candidate/Dapper order reverses in the second round. SQLite Dapper loads the pinned baseline sqlite3 image. New output directories and new fixture identity distinguish the corrected attempt.

This is a short causal screen: two rounds of 256 measured operations per case. Reversed order reduces one direction of drift; it does not remove all host noise, CPU-counter quantization or warm-state effects. Small-case CPU and p99 need conservative interpretation. The single-case warming policy must not be silently compared with older all 35-warmed cells. Closed-loop case service latency is not the final arrival-rate/queue-inclusive SLO. The baseline-final mixed metric/empty-driver controls in the same script are distinct from the codec-only candidate screen and cannot be reported as the candidate's mixed improvement.

## Evidence locations in the shared task directory

- `analysis/pg-codec-b-result.md` and `.json`: source-resource/correctness/package handoff.
- `measurements/pg-codec-b-baseline-01/`: retained falsified three-parse prediction.
- `measurements/pg-codec-b-baseline-02/` and `measurements/pg-codec-b-candidate-01/`: 24 source-bound resource controls and raw snapshots.
- `builds/pg-codec-b-identities-01/identities.json`: ordinary source/ELF/debug/generated/package/native/disassembly binding.
- `measurements/pg-codec-b-correctness-01/` and `measurements/pg-codec-b-sqlite-correctness-02/`: native regression receipts.
- `measurements/codec-b-ordinary-01/`: failed all 35-warmup attempt; no combined comparison credit.
- `diagnostics/run_codec_b_ordinary.py`, `measurements/codec-b-ordinary-02/`: corrected root-controlled ordinary screen, with independent interpretation at `analysis/pg-codec-b-ordinary-review.md` and `.json`.

Ordinary results were read only after root confirmed completion. The independent verifier checks 48 raw processes/16 groups, exact row/digest equivalence, ordered SQL placeholder equivalence, accounting formulas and unchanged within-Korda SQL/protocol totals. PG money1000 CPU falls 32.09% / 35.38% and p50 falls 45.00% / 45.50%, yet candidate CPU remains 8.51× / 8.48× Dapper. PG money32/wide32 improve in both rounds; singleton CPU and customer-totals show no stable gain. Int64 control p50 worsens 7.89% / 4.59% and SQLite wide32 p50 worsens 3.92% / 5.94%. These adverse short-screen observations remain visible and cannot establish either causal regression or its absence. Retain the narrowly supported decimal change without claiming broad alignment; mixed35/final frozen-candidate gates remain separate.
