# Native execution-path review — retained conclusions

This historical inventory predates the final specialized Find path. The selected
result is in [the final report](../continuation-8/final-report.md); use its scope
when describing final behavior. Reading source is not an isolated cost measurement.

The dynamic Fluent path still constructs a bounded command, performs native
semantic compilation and captures execution-owned values. Prepared execution
reuses compiled shape/parameter layout. SQL/Expectation ownership, cache identity
and dispatch remain potential cost questions; their existence alone does not
establish an achievable speedup.

PostgreSQL metadata preparation and common Parse/Describe/Sync confirmation protect
DDL mismatch and the no-execution-at-open contract. Execute begins at first fetch.
Natural EOF may reuse actual completion proof, while unfinished readers still
drain and uncertain/failed transactions retain independent confirmation before
safe reuse. A physical statement cache was not selected. SQLite prepares and
binds without stepping at open; completion/error finalizes the statement.

Native row conversion validates field shape, NULL, numeric/UTF-8 representation,
batch byte/row limits and lease generations. Direct BatchWriter output removes
old row staging and whole-frame managed copying, while canonical row construction
and partial-batch compaction still cost work. Generated DTO readers create owned
CLR values; borrowed views must not escape across awaits.

Snapshot isolation, source/parent lifetime, admission, cancellation, generation
and notification-tail proofs remain required. Their current encodings and number
of queues are implementation choices. The [remaining shortlist](remaining-hot-path-costs.md)
separates three concrete attribution candidates from these necessary responsibilities.
