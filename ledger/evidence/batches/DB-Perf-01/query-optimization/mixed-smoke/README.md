# Local mixed correctness evidence

The checked summary and correctness ledger contain only the public synthetic
35-case workload's outcomes, counts, expected row/digest values, owner drain
observations and source/package/executable/result hashes. Eight cells complete
560/560 scheduled operations. These are correctness checks during concurrent
builds; timing acceptance remains false.

Four lifecycle results contain 11 passed checks and one explicitly unsupported
Dapper/Microsoft.Data.Sqlite active-cancellation check. No equivalent active
cancellation is claimed for that route. PostgreSQL runs in one task-owned TCP
server lifecycle and shuts down successfully.

The ordinary existing `benchmarks/db-perf/managed/build.py`, `build_orm.py` and
`run.py` perform external PackageReference AOT builds and local verification.
The implementation sources and public workload manifest remain in Korda #37.
The original source/build/log archive is retained for local recovery and is not
attached to the Plan PR. Automatic approval review rejected attaching that broad
archive because generated source, restore graphs, local paths and environmental
logs could disclose nonpublic organizational data. This narrower publication
omits those contents and records the task's numeric test evidence instead.

`correctness-ledger.json` is an explicitly extracted view, not relabeled raw
bytes. Every cell retains the unmodified original result SHA-256 in the local
records. No performance values, missing observations or acceptance status were
backfilled.
