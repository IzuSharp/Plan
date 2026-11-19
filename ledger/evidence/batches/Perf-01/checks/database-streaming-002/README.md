# Compact database streaming finite gates

The exact Python 3.12.14 process ran these synthetic gates on CPU 8 at
2026-11-19 11:35:00–11:35:02 UTC. The original receipt and logs are copied
verbatim; their original scratch paths are provenance, not a separate published
artifact promise. No database/application load or product build was run.

| Gate | Actual result | Log |
| --- | --- | --- |
| A21 behavioral, replay and process fixtures | 33 passed | `00.log` |
| Compact DB preparation and parent reader | 6 passed | `01.log` |
| Common long-duration verifier | 14 passed | `02.log` |

The first streaming run also passed at 11:32:51–11:32:54 UTC and remains at
`perf01-evidence/functional/db-streaming-tools-001`. Independent parent review
then found that two streamed object loops accepted a trailing comma. The final
source rejects it; three finite malformed-input cases cover top-level and nested
selected objects. This repeat validates that concrete correction.

The fixtures compare complete formatted observation and dataset bytes, including
out-of-order completion, late-event order and Unicode. Missing/changed accepted
raw records, indexed payload changes and unaccepted-tail changes cannot publish
a final observation. Default full returns and the legacy replay path are kept.
Parent tests prohibit full observation `read_text`, check histogram projection,
and compare unchanged shape validation, dispatch span, outcomes and conditional
percentile inputs, including insufficient-population tails.

The mode still retains finite O(N) scalar/oracle/index/resource state. It avoids
whole payload-graph restoration and whole-document formatting/parsing peaks;
these finite tests do not establish a long-run memory limit. The next exclusive
profile records scheduler lifetime RSS high water, including post-window work.
That profiling-only field was added after these gates and is explicitly recorded
as source-reviewed rather than exercised by them in `review.json`.

`review.json` binds the implementation commit and verifies that every tested core
source still matches the executed receipt. The independent source reviews are
separate from the author's actual executions. No formal timing or long-duration
credit is assigned.
