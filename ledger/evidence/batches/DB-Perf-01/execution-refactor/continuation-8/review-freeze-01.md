# Independent freeze and measurement recovery review

Date: 2026-11-26 (Asia/Shanghai). Reviewer: `plan_freeze_audit`.

This review read the existing Plan instructions, freeze specification and
receipt, generated plans, short-run analyses, source-bound auditors, archive
records and publication receipts. It did not execute a workload, correctness
test, build, compression job or full input-hash sweep. It did not change product
or measurement inputs. Existing hashes below were read from their records,
except that the local Plan Git tree identity was obtained from Git itself.

## Recovery decision and source identities

The existing frozen consumers and final plans can be used for the outstanding
four final intervals after the coordinator checks current host conditions and
revalidates the complete frozen inputs. Rebuilding consumers or repeating
already completed short measurements is not required by this review.

| Binding | Observed identity |
| --- | --- |
| Product, candidate harness and runner | `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` |
| Product tree | `bc9087d843d8d741d83d44f53d0b2c5af26dcffc` |
| Reused Dapper harness | `05fdd6b507bbfa9e971caa739784cf42dfb7199c` |
| Local Plan commit | `e66ae1025e098fe487d86b1590cda11d7a166413` |
| Local Plan tree | `ea0fa9e359a44d9aefd163d2db976c2784b5ef9f` |
| Public Plan commit in existing publication receipt | `9e4aad4c04c68dd30ab3bcad68a977000b4717e2` |
| Public Plan verified tree in that receipt | `ea0fa9e359a44d9aefd163d2db976c2784b5ef9f` |

The public/local Plan mapping is supported by the local tree and
`/workspace/scratch/fd78534029f7/publication/checkpoint-04/receipt.json`, whose
`refUpdated` is true. The public Plan commit object was not present in the local
repository during this reading; this review is not a new remote verification.
The coordinator separately owns current GitHub head checks.

Both `/tmp/DB-Exec-10-pack-sqlite-02` and
`/tmp/DB-Exec-10-pack-postgresql-02` existed, had clean worktrees and reported
HEAD `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`. At the time of this reading,
neither final output directory existed. No executed final interval is credited
by this review.

## Existing freeze

Freeze path:
`/workspace/scratch/fd78534029f7/measurements/final-freeze-01.json`.

- SHA-256: `fc1dae9be0a76b0de38c4f94c3836e47b398e10b5ff23f3c8f82313a3cb4bc1a`.
- `status=frozen`, `inputsUnchanged=true`, 373 fixed input identities.
- Recorded at `2026-11-26T08:05:00.628117+00:00`.
- `workloadProcessesStarted=0`.
- Specification:
  `/workspace/scratch/fd78534029f7/measurements/final-freeze-spec-01.json`.
- Reviewed identity auditor SHA-256:
  `99f458030b41cfe9f5740cd536a0f5d3314b0955a8a72de9abce10d3ab3c91e2`.

This is a pre-run identity freeze, not a completed final audit. Its full
source/package/ELF/generated-code/tool inventory must be revalidated rather
than inferring immutability from a still-existing filename.

## Exact final invocations and ordering

The commands below are the `runnerCommand` values already stored in the derived
plans. Do not execute their original three-cohort `*-final-source-01.json`
parents. Do not add the before cohort to the final four cells.

First:

```bash
taskset -c 8 python3 /tmp/DB-Exec-10-pack-sqlite-02/benchmarks/db-perf/run.py \
  /workspace/scratch/fd78534029f7/measurements/plans/sqlite-final-01.json \
  --output /workspace/scratch/fd78534029f7/measurements/sqlite-final-01
```

Only after that complete runner, including drain and idle, exits:

```bash
taskset -c 8 python3 /tmp/DB-Exec-10-pack-sqlite-02/benchmarks/db-perf/run.py \
  /workspace/scratch/fd78534029f7/measurements/plans/postgresql-final-01.json \
  --output /workspace/scratch/fd78534029f7/measurements/postgresql-final-01
```

| Order | Provider | Consumer | Concurrency | Offered rate | Steady interval |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | SQLite | Korda | 4 | 3,000/s | 1,800 s |
| 2 | SQLite | Dapper.AOT | 4 | 3,000/s | 1,800 s |
| 3 | PostgreSQL | Korda | 8 | 3,600/s | 1,800 s |
| 4 | PostgreSQL | Dapper.AOT | 8 | 3,600/s | 1,800 s |

Each provider runner first executes its candidate fixture with timing disabled.
Each measured consumer has a separate 15-second post-disposal idle observation
and a 2,115-second command timeout. The common workload is queue capacity 64,
all 35 cases, requested/batch rows 32, 8 tenants with 1,024 orders each,
persistent sessions and 64 warmup operations per worker. Known local builds,
correctness tests, profilers, other loads and bulk archive/hash operations must
not overlap the measured intervals.

## Calibration and same-condition before supplement

The selected settings follow a recorded prospective rule, not a choice made
after seeing the final results:

- SQLite C8 provided only 8.5% more short-run throughput than C4 while p99 rose
  from 10.748 to 25.821 ms, selecting C4.
- PostgreSQL C8 provided 31.4% more throughput than C4, selecting C8 for this
  pressure comparison.
- The 30-second offered candidate observations completed 94.01% of SQLite
  R3000 and 92.73% of PostgreSQL R3600. Both met the predeclared 90% selection
  rule, had zero business failures and drained all eight candidate owners.
- Refusals remain explicit: SQLite 5,335/90,000 arrivals and PostgreSQL
  7,792/108,000. They are not successful operations.

The four completed 120-second before/current observations retain equal
provider-specific settings, recorded host identity, business contracts and
literal Korda diagnostic SQL. All four report zero business failures:

| Provider | Before successful op/s | Current successful op/s |
| --- | ---: | ---: |
| SQLite | 542.872 | 2,668.577 |
| PostgreSQL | 1,241.453 | 3,458.224 |

Their refusals remain in the raw counters. They have no post-drain idle RSS
observation and provide no 1,800-second credit. Current final measurements must
supply their own idle data and duration evidence.

## SQL and business equivalence boundaries

The unchanged arithmetic analysis records 35 diagnostic-text differences
between the mixed Korda and Dapper workloads. Ordinary statements largely
differ in provider parameter markers (`?`/`$n` versus Dapper `@pN`); lifecycle
entries also compare older descriptive summaries with explicit SQL. These
recorded differences are not erased by equal business-result digests.

The separate freeze auditor requires the matched Dapper lifecycle policy and
recomputes its static-source and actual generated-command-factory proofs. Those
records include the Find and update call sites, parameter `DbType` values and
value-member bindings. The source contracts and actual business assertions are
stronger evidence than equal digests alone, but they do not make every recorded
diagnostic SQL string byte-identical. `runtimeSqlTraceVerified=false` remains
explicit. Neither this review nor a successful identity audit establishes an
observed server wire trace.

## Host limits and interruption recovery

The last existing host observation reports node `89394ab90f06`, Linux
`6.18.57`, architecture `x86_64`, client CPUs `0-3`, PostgreSQL CPUs `4-7` and
observer CPU `8`. The cgroup-v2 mount is unavailable. The record does not prove
exclusive physical hardware, invisible cgroup quota, or system-wide process
silence across tool PID namespaces.

A new pre-run host observation must describe the actual resumed environment
and be compared with those recorded identities. Reusing the old host file does
not make it a new observation. Preserve all visibility limits in the final
conclusions.

Keep any failed or interrupted output directory intact. A retry requires a new
numbered destination and an explicitly identified new plan/freeze when the
destination changes. Never overwrite a partial receipt or edit an old freeze
so changed sources, binaries or argv inherit the old run's identity.

## Final evidence acceptance

After both provider runners finish, use the unchanged
`continuation-5/prepare_load_index.py` and
`continuation-3/analysis/analyze_execution.py`. An index containing both existing
120-second directories and both final directories has eight measured
observations, exactly four marked final. Then run the existing identity auditor
against the original freeze and exact freeze SHA-256:

```bash
python3 /workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/local-load-tools/audit_final_identity.py audit \
  --freeze /workspace/scratch/fd78534029f7/measurements/final-freeze-01.json \
  --freeze-sha256 fc1dae9be0a76b0de38c4f94c3836e47b398e10b5ff23f3c8f82313a3cb4bc1a \
  --analysis <new-analysis.json> \
  --output <new-identity-audit.json>
```

The final evidence must show:

- Four actual steady intervals of at least 1,800 seconds, successful business
  progress in every second 0 through 1,799, and all 35 cases observed.
- Raw counter conservation, successful command/observer execution and explicit
  fixture exclusion.
- The same recorded host and no overlap through steady execution, drain or
  recorded idle.
- All eight candidate owners present as integer zero, including `PullChannels`
  and `CommandCompletions`; Dapper's own application connection owner is also
  present as integer zero.
- Complete source/tree, package, ELF, loaded-native, generated-code, runner,
  plan and actual argv identity checks against the full frozen input inventory.
- Identity-audit `status=passed`, four explicit `segments` and
  `inputsUnchanged=true`.

The arithmetic tool explicitly states `taskAcceptance: Not decided by this
arithmetic report`. It retains failures/refusals and does not invent an SLO.
A successful exit or complete four-cell matrix therefore does not replace
review of business correctness, owners, throughput, latency, CPU, RSS,
allocation, process-GC scope, remaining gaps and the stopping rationale.

## Evidence and Plan closeout

Create a separate final archive using the existing archive helper and the union
of frozen inputs plus actual final analysis/audit inputs. Retain original
JSON/JSONL, stdout, command and runner receipts, source/generated code,
publish/restore metadata, host observations and failed attempts. Read back every
archive member and rehash every included original. Preserve explicit binary,
package and database exclusions with their original paths and hashes. Do not
replace the pre-final archive or claim its excluded bytes are recoverable from
hashes alone.

The top of `execution-refactor/current-checkpoint.md` still describes the older
15:16 checkpoint with PostgreSQL phases running. Append a new current recovery
or completed checkpoint and retain older text as history. Refresh stale PR-body
continuation links and final-cell counts during closeout.

Keep material limits visible: `FrameworkOnlyBytes=null`; no proof of
whole-framework additional managed 0 B; no causal timing attribution for every
remaining copy, hash, validation or dispatch; and the rejected `92b9230`
quiet-close experiment stays rejected. Its PostgreSQL direction varied between
rounds and SQLite 1,000-row total p50 regressed 6.78%. Rejecting that experiment
does not prove every possible optimization is exhausted.

The old Plan `verify_db_perf.py` history gate must continue to run at the
existing CI's immutable Plan snapshot
`38f8ce8a01f88e6e4c4459926f197c5438c2f6fc`. The current-tree allowlist failure is
already preserved. Do not edit that verifier, CI selection or historical
acceptance to turn the current-tree invocation into a pass.
