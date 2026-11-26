# DB-Go-01 — additional Go comparison

The owner requested only two new local Linux x64 cells on 2026-11-26:
SQLite for 1,800 seconds, then PostgreSQL for 1,800 seconds. Reuse the frozen
35-case SQL, data, result digests, offered rates, worker counts, queue, affinity,
warmup and idle boundaries from continuation-8. The four completed Korda and
Dapper.AOT cells remain historical, unchanged and are not rerun.

The implementation is a standalone Go `database/sql` consumer. PostgreSQL uses
pgx without retained server prepared statements, matching the Npgsql reference's
`MaxAutoPrepare=0` policy. SQLite uses go-sqlite3 linked to the exact previously
selected SQLite 3.51.3 shared image. Go compiler and module identities, actual
loaded SQLite image, SQL/parameter/result contract, build, raw histograms,
process-wide heap allocation and GC counters, CPU, RSS, and all failures will
be retained. Go GC counters are not .NET generation counters. Business and
harness allocations remain included; framework-only allocation is not inferred.

The existing local `benchmarks/db-perf/run.py` supplies PostgreSQL ownership,
settings, resource sampling, command lifetime CPU/maxRSS and finite timeouts.
Fixture initialization may reuse the frozen initializer with zero measured
operations. Only Go receives new timed workload credit. There is no new CI
performance workflow, job, trigger, schedule or hidden benchmark invocation.

Work starts from Korda main `7ff7b57b907b689defb880b8af62d83679608603` and
Plan main `03efe57ffbe3046bd89919ddb2c16c90a377954d`, in DB-Go-01 worktrees.
After source review, Go-only preflight and the two serial cells, archive and
read back all report/evidence bytes before the owner's requested removal of
local task worktrees, builds, databases and caches. Preserve unrelated tools,
shared runtime files and credentials. Record the concrete cleanup inventory
and outcome; no previous unpublished unique work may be silently discarded.

Status: source and final inputs frozen; neither Go 1,800-second cell has run yet. Current authority
adds this comparison and final local cleanup; it does not reopen product
optimization, previous measurements or package releases.

## Frozen checkpoint

Implementation PR: [Korda #39](https://github.com/IzuSharp/Korda/pull/39),
source commit `d5f4f9d6616bad54a08aebb7d1aca7937b18eb93`, tree
`f8744d7735e47552c657d3b18ad5cd9e39946db9`. The local final tree is identical.
Measured binaries record local runtime commit
`94eb3a7675a44e30c6f9ed6c7a7edda987fe36db`; later source additions contain only
independent verification and unit tests, and the exact local commit chain is
retained in a Git bundle for reproducible checkout.

The [input freeze](checkpoint/freeze.json) binds 38 actual files, including both
executables, exact SQLite image, PostgreSQL tools, manifest, observer, plans,
source and preflight acceptance. Its SHA-256 is
`fc08a113b690b55a38aee9c1f295c65475058c81ed8ee4be0e1ec19d16a63fe8`.
The [host observation](checkpoint/host-before-final.json) has the same hostname
and boot identity as the completed four-cell campaign, available CPUs 0–8,
about 2.13 GB free disk, and no active database/build/benchmark process. It does
not assert exclusive physical tenancy or an invisible cgroup quota.

Provider-specific five-second preflights passed: SQLite 15,000 successes and
zero rejections; PostgreSQL 17,927 successes and 73 explicit rejections. Both
had zero business/oracle failures or retries and all four/eight observed
connection counts returned to zero. These are correctness/preparation evidence,
not thirty-minute results or capacity estimates. Go unit tests and the existing
45 Tooling checks (one existing skip) passed. The impact plan assigns all new
files to the existing benchmark ownership path and selects no provider package
build or publication.

The restart-visible local supervisor is [run_serial.py](checkpoint/run_serial.py).
It refuses to overwrite prior campaign state and starts PostgreSQL only after
SQLite, its idle period and its observer have exited successfully. Resume by
inspecting local campaign-state.json and existing command receipts; never
restart a completed thirty-minute segment because the conversation was
interrupted. Final results, archive readback and the owner's requested full
local cleanup are still outstanding at this checkpoint.
