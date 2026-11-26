# DB-Exec-Parity-01 — PG codec B resource proof and candidate handoff

Candidate `23845016b707a2876e6777cf935667dc546ca6d5` preserves every decimal validation site and replaces construction of four general JSON trees per non-null PG decimal with exact primitive parsing of the already-required canonical configuration. The allocation hypothesis is now observed on both independent diagnostic images. Ordinary performance acceptance remains with the root-controlled interleaved A/B.

## Same-business measured resource change

Each cell executes one measured business after eight warmups, twice, with the original SQL, generated DTO readers and correctness oracle. All SQL, result-row identities and expected digests match baseline to candidate. Both repeats have exactly equal scope counts and bytes. The separate diagnostic images have no ordinary timing credit.

| Original case | Decimal outputs | Config JSON parses, before → after | Config validations, before → after | Whole decimal decode allocation calls, before → after | Requested bytes, before → after |
| --- | ---: | ---: | ---: | ---: | ---: |
| numeric32 | 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| money1 | 1 | 4 → 0 | 3 → 3 | 48 → 1 | 1,136 → 4 |
| money32 | 32 | 128 → 0 | 96 → 96 | 1,536 → 32 | 36,352 → 128 |
| money1000 | 1,000 | 4,000 → 0 | 3,000 → 3,000 | 48,000 → 1,000 | 1,135,980 → 3,980 |
| wide32 | 32 | 128 → 0 | 96 → 96 | 1,536 → 32 | 36,352 → 128 |
| customer-totals32 | 9 | 36 → 0 | 27 → 27 | 432 → 9 | 10,242 → 54 |

For money1000 the observed reduction is **47,000 allocator calls and 1,132,000 requested bytes per business**. This exactly matches the prediction made before the product change. Three validations per decoded value remain; their configuration scope and the final range-configuration scope now make zero public malloc/calloc calls. The whole decode retains one small allocation per decimal (3,980 B over 1,000 values). The unchanged numeric conversion vector is a source-supported candidate explanation for that residual; its precise allocation site is not separately instrumented here, and this experiment does not change it.

`numeric32` is Int64, not configured NUMERIC/decimal, and stays a zero-decimal negative control. Consequently this result does not explain or claim to resolve the earlier Int64/string phase1000 client CPU gap. It directly addresses the original `money`, `wide` and `customer-totals` decimal paths.

Raw baseline: `measurements/pg-codec-b-baseline-02/`; candidate: `measurements/pg-codec-b-candidate-01/`. Each contains exact commands, raw workload receipts, cumulative `.codec.json` snapshots with process/thread identity and monotonic boundaries, scoped deltas and completion receipts. All 24 measured businesses completed with zero business/oracle errors/retries and native owners returned to zero. All scopes have equal entry/exit totals at both boundaries, no backwards counters and no scoped allocation failures.

## Proven call chain and actual machine code

Original `postgres_decode_into → check_profile → Codec::validate` accounts for the first validation. `postgres_compatible → postgres_oid → check_profile → Codec::validate` accounts for a second. `checked_scalar → validate_scalar → Codec::validate` accounts for the third; `validate_scalar` then parsed the configuration again to read precision/scale. These four parse calls, not the initially predicted three, are directly observed. The failed three-parse assertion is retained in `measurements/pg-codec-b-baseline-01/`; it was a falsified attribution hypothesis, with a correct business result.

`builds/pg-codec-b-identities-01/identities.json` binds actual ordinary package/native/AOT bytes, matching ELF/debug Build IDs, real generated code, source commits and disassembly. Baseline native SHA-256 is `1909e79db9265f9da2d2b22073090e03c06989fcd4af06ba656a493bce047fed`; candidate PG native is `37fbd74a7638da19b2b41d42c74b9bd2a5a2a74dba827ae9555968ab65f10f6e`. Candidate `Codec::validate` at `0x30480` calls `decimal_configuration` at `0x304ee → 0x30c10`; its original invalid-input JSON fallback remains at `0x30519 → parse_json`. Candidate `validate_scalar` at `0x3a2c0` still calls `Codec::validate` at `0x3a2dc` and calls the primitive configuration reader at `0x3a6c1 → 0x30c10`. The retained disassembly plus scope counts establish the exercised mechanism; static instruction listings do not establish instruction latency or scheduled CPU samples.

## Contract boundary and source scope

Only `native/cpp/src/contracts.cpp` and `native/cpp/tests/scalar_tests.cpp` change in the product commit. Exact canonical decimal configurations require precision 1–29, scale 0–28 and scale ≤ precision, canonical key order/ASCII punctuation and canonical unsigned decimal spelling. `from_chars` checks overflow, and the wrapper rejects multichar leading zeroes. Those are exactly the old JSON-validation + canonical-string reconstruction acceptance conditions. All noncanonical/invalid forms continue through the unchanged JSON fallback, preserving error classification and text. SQLite rejects decimal codec13 before the new parser, missing configuration retains its earlier error, and no mutable Codec cache is introduced.

The final range check still follows the original profile, OID, byte-width, decimal flag/canonical coefficient checks. NULL handling, schema change, cancellation, transactions, command ordering, ownership, executor scheduling and provider behavior are untouched. FixedScaleMoney/id15 still uses its existing implementation because this experiment has no corresponding isolated source-allocation proof.

Independent source reviews from `lease_audit` and `recovery_ci_audit` found no blocking equivalence, overflow, error-order or ownership issue. The test inventory below establishes observed correctness; unchanged invalid-input fallback code is the basis for preserving exact diagnostic text, rather than a newly added string-for-string assertion for every error.

## Completed correctness and package identity

`measurements/pg-codec-b-correctness-01/` records the exact candidate binaries and all test commands. Existing nonzero/min/max/96-bit scalar checks remain and pass. New tests execute all **463** accepted precision/scale combinations through configuration validation, scalar validation and PG zero decoding; 31 malformed configuration strings plus embedded NUL, missing configuration, sequential mutation, SQLite profile rejection and conflicting bad OID/configuration checks pass. The scalar suite reports 17 scalar kinds and 116 rejected lossy/invalid values.

| Retained correctness target | Observed outcome |
| --- | --- |
| scalar | 463 accepted decimal configurations; 116 rejected lossy/invalid values; exact 96-bit, SQLite canonical storage, PG binary protocol passed |
| contracts | 10 cross-language goldens, 43 malformed rejections, registry atomicity passed |
| provider against real PG + SQLite | 183 checks, 0 failed; PostgreSQL actually verified |
| PostgreSQL sync/protocol confirmations | 432 checks passed |
| one-shot command completion | 377 checks passed |
| real PostgreSQL queued cancellation | 8 checks passed |
| transaction lifecycle | 13 retained families, 120 checks passed |
| PG fixture components | All 11, including TLS, timeout/rollback, early stream drop, codec roundtrip/wide rejection, savepoints, commit-response loss/Unknown, quarantine and ownership retirement passed |
| independently built SQLite package native fixture + ABI | `native.sqlite14` and `native.selected.abi`, 2/2 passed; receipt at `measurements/pg-codec-b-sqlite-correctness-02/` |

Both genuine independent top-level packages were composed and closure-validated as version `0.1.0-db-exec-parity-codec-b.1`. Four ordinary Release Native AOT consumers build successfully from those packages (no ProjectReference): `consumers/pg-codec-b-{postgresql,sqlite}/korda-workload/out/DbPerf.Korda` and `.../korda-query-phases/out/DbPerf.QueryPhases`. Actual AOT ELF, matching `.dbg`, generated C#, package lock/build receipts and native images are retained. This handoff claims package/AOT builds and native suite execution; ordinary package consumer execution/35-case mixed acceptance remains the parent measurement gate. The separate diagnostic PG package has actually executed all 12 resource-control businesses.

The committed diff was checked with the required `python3 eng/ci/impact.py origin/main --output artifacts/plan.json`. `database-native` owns `contracts.cpp`; `native-checks` owns the scalar tests. The plan selects Linux native/dependency/regression checks and independent PostgreSQL and SQLite build/dependency/pack/packed-api/test/AOT-consume/validate lanes. No CI, benchmark route or public API was changed. Both provider outputs are required because the product source is shared.

## What is still unknown and next decision

This allocation shim counts successful public glibc malloc/calloc/realloc requests while the current thread is inside the named source scope; nested scopes are inclusive, so parse + validation + decode totals cannot be summed. It does not count private/aligned allocation entry points, allocator metadata, frees, retained heap, RSS or managed allocations. It does not provide scheduling wait, retired-instruction or ordinary CPU attribution. No native CPU, latency, throughput or Dapper-parity claim is justified by these diagnostic numbers alone.

The next decision is the root-owned uninstrumented serial interleaved A/B on matching decimal workloads, with Int64 and SQLite controls and then the original mix. The candidate is appropriate only if those ordinary results support its selected scope without a contract regression; no additional optimization should be bundled into this causal experiment. The full task still requires aggregate/frozen-candidate gates and final four 30-minute runs, merge, existing CI and public NuGet AOT consumption.

All build and measurement processes owned by this component have exited. The only deleted files are documented reproducible, completed `bin` and `.o` intermediates; unique actual binaries/debug/generated/raw evidence remains. See `environment/pg-codec-b-finished-*-intermediates-*.json`. The initially missing `clang-tidy` preflight failure and initial unsourced-ctest command failure are retained separately; no check rules were relaxed.
