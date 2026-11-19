# Compact database outcome receipt finite gates

Actual execution at **2026-11-19 12:34:49–12:34:50 UTC** passed against clean
NativeWeave commit `70246e23246f824da2e4483525946346c02b4b57` using the pinned Python 3.12.14 on
CPU 8. `receipt.json` records exact commands, interpreter/source hashes, start/end
times, exits and raw-log hashes; the three logs are verbatim copies.

| Suite | Actual result |
|---|---|
| `tests/Perf01.Database/test_outcomes.py` | 8 tests passed |
| Existing `test_streaming.py` | 6 tests passed |
| Common `tests/Perf01/test_verify_long.py` | 15 tests passed |

The new fixtures check complete pretty-JSON byte equivalence for all three DB
routes, completion order/duplicate/warmup preservation, immutable appended
snapshots, partial write/flush/close/replace/replay failures, sticky late-append
failure, compact-only save override/restoration, bounded parent projection and
malformed/trailing JSON. The common verifier retains the full receipt hash and
profiling/correctness/durable/drain gates while avoiding whole-receipt loading.

Protocol and codec agents independently source-reviewed their respective
writer/owner and parent/reader scopes; those reviews are recorded separately in
`review.json`. The reviewers did not execute these tests. Root also read the
core candidate. A21, historical B23 `http_target.py` and `common.py` remain
byte-identical, so no redundant A21 rerun was performed.

This commit also adds `perf01_outcomes.py` to the prospective DB calibration
controller's source pins. The root integration and actual unchanged-product
profile occur separately. The preceding compact-v4 SQLite/PostgreSQL calibration
is preparation evidence after this target-retention change; its original valid
and invalid outcomes remain untouched, and no noise receipt was generated from
it. Fresh compact-v5-target DB selection is required before freezing final
before/after rates and noise bands. Codec/protocol timing-driver identities are
unaffected.

No application, PostgreSQL/SQLite, HTTP, benchmark load or build was started by
this finite test invocation. It provides no long-run credit and establishes no
product performance change.
