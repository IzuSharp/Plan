# DB-CPP-01: independent input-admission compatibility review

Status: development patch verified; formal source4 build, full regression, package comparison and CI remain separate gates.

## Fixed references

- Rust product: `465cd0f90e6af05ec50eb581156240377cf0825b`.
- Rejected C++ candidate: `3e49cee95d206468a32c94f0a3b98e923f02acbf`.
- Reviewed development patch is based on the same C++ head. No new commit or package provenance is claimed by this review.

The reviewer changed no product, C#, ABI or acceptance files. Diagnostics load the two unchanged public ABI implementations in separate processes, use the same input bytes, and query persistence independently with Python sqlite3 or PostgreSQL psql. All executed diagnostic outputs and original candidate failures remain available.

## Findings and correction

1. SQLite retained a separate physical command-input limit. The old provider reserved `SQL bytes + 2 * complete parameter wire bytes`, after asynchronous operation admission and before provider statement dispatch. C++ only checked each logical envelope. For the existing four-column mutation, SQL is 81 bytes and the wire is `N + 275` bytes for JSON Text length N: N=7000 needs 14,631 bytes and must reject with domain status 13/code 6 under 8192; N=3000 needs 6,631 bytes and remains admissible.
2. Empty parameters still encode the full 96-byte wire header. A business command therefore needs SQL bytes plus 192 bytes. Internal SQLite describe with no ParameterInput needs SQL bytes only. The corrected helper preserves this distinction.
3. PostgreSQL B07 preflight bounds the provider representation, not only canonical wire bytes. JSON adds one version byte and Numeric retains the old conservative 24-byte bound. Every parameter, including NULL, adds four framing bytes. B07 failures map to status 13/code 3; SQLite physical grant failure stays code 6.
4. The old query path prepares/describes SQL and admits parameters before checking B06 row-buffer limits. C++ originally returned row-buffer code 14 first. The corrected path describes SQLite SQL without values before full input admission, then prepares the actual statement on both providers before row-buffer checks. Preparation does not step SQLite or send PQsendQueryPrepared; actual execution/row reads remain delayed.

### Read-only source review

The old implementation was traced through `native/database/host/src/config.rs` (Limits::sqlite/codec), `host/src/session.rs` (execute_count/CursorOwner::open), `sqlite/src/session.rs` (prepare/run_query), `sqlite/src/admission.rs` (Reservation), and `codecs/src/lib.rs` plus `codecs/src/scalar.rs` (provider_size).

The new helper uses overflow-safe subtraction/division, preserves SQL Configuration code 8 before physical ResourceLimit code 6, maps only B07 conversion errors to code 3, and keeps the original SQLite decode budget rather than applying the PostgreSQL source field limit. The existing per-session CommandGate retains exclusive input ownership through execution/cursor retirement; no new source-global budget was introduced. Transaction and administrative control lanes do not call the new business-command helper.

The complete provider-width table, normalized decimal handling, NULL framing, source-bound configured codec IDs, statement RAII cleanup and lazy execution were reviewed. No remaining blocking issue was found in the reviewed production diff.

## Actual public ABI replay

| Case | Frozen Rust | Source3 C++ | Fixed development leaf | Independent persistence |
| --- | --- | --- | --- | --- |
| SQLite empty wire, exact SQL+192 budget | Success | Success | Success | 1 row |
| SQLite empty wire, budget one byte smaller | 13 / 6 | Success | 13 / 6 | Rust/fix 0 rows; source3 1 |
| SQLite 7000-character JSON query, normal batch | 13 / 6 | Success cursor | 13 / 6 | 0 rows |
| SQLite same input plus missing table | 13 / 1 | 13 / 1 | 13 / 1 | 0 rows |
| SQLite oversized input plus 135-byte batch | 13 / 6 | 13 / 14 | 13 / 6 | 0 rows |
| SQLite missing table plus 135-byte batch | 13 / 1 | 13 / 14 | 13 / 1 | 0 rows |
| PostgreSQL 11-byte JSON, field limit 11 | 13 / 3 | Success | 13 / 3 | Rust/fix 0 rows; source3 1 |
| PostgreSQL same JSON, field limit 12 | Success | Success | Success | 1 row |

All eight fixed results exactly match their independently observed Rust status/domain/code, affected count, persistence count and six retired resource counters. Every counter is zero. Probe source hashes and input hashes were unchanged between reference, rejected candidate and development replay. The PostgreSQL server was 18.0 for both phases. All processes, sources, sessions, cursors and private PostgreSQL servers retired successfully.

## Evidence and identities

- `_validation/parameter-budget-review-1/result.json`: SHA256 `a85e3212078b5ca27cd8ad0b663538367337110ccc1a01e45b0a93867efe17d6`.
- `_validation/sqlite-input-review-2/result.json`: SHA256 `e3c89f693b023825d6218fbffe7a8ec4c979cbadefdb12a4ebd1f7ec6de8902e`.
- `_validation/parameter-budget-fixed-development-1/result.json`: SHA256 `59defa05f3fe23132d1596c9601c07840d223fe02d946f448371d306b6857be2`.

A first SQLite diagnostic draft accidentally selected Memory mode. It is retained under `sqlite-input-review-1` with `excluded.json`, and is not used for persistence claims. The accepted SQLite diagnostic uses ReadWriteCreate file mode and an independent file observer.

Development ELF hashes:
- postgresql: `86dd277482bbe3a3adf48b91afe3af5a5a583120178b6d30daeb60b5aa93cd07`.
- sqlite: `aad32bab9c6bae6744fd34480eeaa5aa596c02efde71db249803761cf778031c`.

Reviewed production-file hashes were unchanged throughout replay:
- `native/cpp/include/nw/provider.hpp`: `82ca8ad2cb37d2af68d1e3fc1048165b612f48af8a6995b754134b8136ef33da`.
- `native/cpp/src/host.cpp`: `eb1c23c0e0bc87b0f2f647dae17fcfaaf4f4d132b1dbef2c22298993d8a5c536`.
- `native/cpp/src/provider.cpp`: `ff2a99f8dfa0a1dcc995735f0c2980fd5aec7efef26c69333416b442c887794f`.

## Remaining acceptance work

The development replay is intentionally not a replacement for unchanged Orm.Relations JIT/AOT assertions, the complete native Release/sanitizer gates, new candidate package production, or the final four-cell Rust/C++ PackageReference comparison. The PG native boundary test was initially outside the SQLite-only host_review target; root/linux have wired a dual-provider target and isolated PostgreSQL invocations into the Release and sanitizer runners. Their actual execution remains owned by those agents.

No production behavior was weakened, no C# assertion was edited, no existing failure evidence was overwritten, and no native package/consumer hash verification was bypassed.
