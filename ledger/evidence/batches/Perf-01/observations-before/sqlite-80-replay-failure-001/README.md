# SQLite 80/s: failed replay, intact durable recovery

This is a read-only diagnosis of completed cell
`ROOT/perf01-evidence/calibration/before-sqlite-compact-v4/04-ladder-80`.
Its verdict remains **invalid**, with 860 successful logical operations, one
failed operation and 1,540 canceled tail records. No request, SQL query, load,
driver edit or replacement verdict was produced for this diagnosis.

The [receipt](receipt.json) pins the original summaries, exact excerpts and source
positions. The four accompanying small logs are verbatim copies of the original
adapter errors, classified errors, captured HTTP failures and application stderr.

## What actually failed

Logical operation 534 was a mixed-load business cycle. Its captured observations
are:

| Leg | Actual result | Content check |
| --- | --- | --- |
| Create, POST `/v1/items` | 201 | Complete 190-byte created-item DTO |
| Same-key replay, POST `/v1/items` | 500 | Complete empty response body |
| Within-cycle recovery, GET `/v1/operations/…` | 200 | Exact same 190-byte DTO as create |

The create and recovery body SHA-256 is
`16a7258bfa0f701fe6252cc7d2217a71e90e37f46eae7d93be897fbfffbf015b`.
The original adapter exception explicitly records `replay_equal=false` and
`recovery_equal=true`. The replay leg failed; the successful recovery response
did not return a changed or malformed DTO.

The independent durable oracle passed. It observed **431 committed measurement
mutations**, while only **430 complete cycles** succeeded; 430 page operations
also succeeded. The failed cycle's successful create is not erased by a later
replay failure. The source starts each create/replay through its transaction and
claim path (`DatabaseService.cs:24–51,56–79`); recovery returns the stored response
bytes (`117–131`). No conclusion about the precise failing SQL statement follows
from the available generic exception record.

Application stderr records one actual `DatabaseException`, `kind=Provider`,
`provider=5`, correlation 1237. The observer's primary-code accounting reports
one SQLite BUSY and zero LOCKED. This is an actual provider observation; HTTP 500
alone is not used to infer BUSY. The saved exception lacks a SQL-stage stack, so
the exact statement and its lock-wait duration remain unavailable.

## Why the classifier reports recovery 200

`Target.operation` in `src/Benchmarks.Domain/http_target.py:392–410` performs the
recovery GET after the replay response, then passes all three outcomes into the
whole-cycle oracle. `complete` at `271–277` raises `IntegrityFailure` for the
aggregate mismatch. The context-local `last_response` is therefore the later,
correct recovery 200. `PerfTarget.capture_error` in
`tests/Perf01.Database/target.py:125–147` classifies that last response rather
than the earlier failed replay leg. Its recorded `stage=recovery` is the
within-cycle GET, not the separate post-load recovery phase.

Consequently, the preserved classifier row is
`integrity_or_unclassified_failure`, `http_status=200`, with permanent halt set.
The source then emits canceled outcomes for later arrivals without further
measurement HTTP (`http_target.py:597–627`). This is a classification limitation
in the existing aggregate cycle adapter, not evidence that the successful 200
content was incorrect. The failed logical cycle remains a real zero-error/SLO
failure, and its canceled tail cannot establish sustained 80/s service load.

All 16 separately timed post-load recovery cycles and the subsequent independent
durable oracle passed. Consumer and database resources were released and the
server reached Disposed. Those recovery results do not turn the failed
measurement into an accepted capacity point. The driver stays frozen for this
round; the higher failed point and all original evidence are retained.
