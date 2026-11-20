# Perf-01: superseded ADA database candidate

This report preserves the completed 48-process comparison of before product
`ea5fa528035d025bd7a28698ee7c71194432236c` and candidate
`ada13b865ec5d19876745498f6f51d8ad2367399`, with the direct Rust and managed controls.
ADA was subsequently superseded by `0715ffb6376b1ae08259ad7e2cb30ff0320d83e7`
after the separate retirement ablation. These are retained experimental results,
not the final product comparison and not long-duration acceptance.

All 48 processes exited zero and passed complete evidence/correctness validation.
Forty-three met the fixed service standard; five PostgreSQL controls (three
managed and two direct) did not. All five remain service-ineligible observations,
with zero measurement-invalid rows. Thresholds and original failures are retained.

The original 16-process collection ended at 05:18:10.259307 UTC with an outer
exit 1 because it treated an observed service miss as collection failure. The
fixed suffix ran from 05:54:37.826927 to 06:30:03.350327 UTC; all 34 commands
(32 application processes and two original readers) exited zero. No process was
replaced. The narrowly corrected terminal-state reader subsequently completed
both providers, preserving the five service misses.

Full offline projection completed on 2026-11-20 from 06:45:02.788997 to
06:45:16.964890 UTC, exit zero. It validates every row and the original persisted
results. Its first attempt failed before extraction because it used the wrong
frozen A21 module identity; that failed attempt remains retained. The correction
uses the observer's frozen A21 identity for DB and the original identity for
protocol/codec. Fifteen finite checks passed before the successful extraction.

The PostgreSQL C16 aggregate showed mean call latency 27.341228 to 23.348294 ms
and mean-of-process p99 145.983807 to 111.536260 ms. The frozen A21 mean decision
was inconclusive: the confidence interval did not clear the measured noise band.
No statistical improvement is claimed for that row, and p99 is descriptive.

[`database.json`](database.json) retains all exact numeric rows, process tails,
CPU/RSS, errors, SQLite surfaced BUSY/retry counts, correctness and persisted
result checks, source/artifact hashes, differences and A21 decisions.
[`coverage.json`](coverage.json) retains the validated matrix coverage and the
then-pending protocol/codec/after-capacity slots; it correctly reports global
completion false. [`publication-manifest.json`](publication-manifest.json) binds
these exact copies and the actual private extraction receipt. Missing domains
in this historical snapshot have no execution credit. Full raw operational
records remain in the measurement workspace; only the listed numeric files are
published here. Git retention follows repository history.
