# Generate local execution plans

`generate_local_plan.py` writes one new JSON plan for the existing Korda
`benchmarks/db-perf/run.py` and prints its command. It does not execute that
command, start a database, build a consumer, or grant performance acceptance.
Use Python 3.11 or later. Source, binary and native-library paths must already
exist; the plan records their actual SHA-256 values. Producer receipts remain
the source of binary-to-source-commit provenance; this tool invents no commit.

```bash
python3 generate_local_plan.py \
  --source "$KORDA_SOURCE" --provider postgresql --lane phases \
  --before-dir "$BEFORE_PHASE_BIN" --candidate-dir "$CANDIDATE_PHASE_BIN" \
  --dapper-dir "$DAPPER_PHASE_BIN" --postgres-bin "$POSTGRES_BIN" \
  --plan "$NEW_PLAN_JSON" --output "$NEW_EVIDENCE_DIRECTORY"
```

Directories contain the published executable directly: phases use
`DbPerf.QueryPhases` / `DbPerf.DapperQueryPhases`; the other lanes use
`DbPerf.Korda` / `DbPerf.Dapper`. For SQLite, select `--provider sqlite` and
replace `--postgres-bin` with `--sqlite-library /actual/path/libsqlite3.so`.
Pass the matching workload binary directories for mixed-load lanes.

| Lane | Generated serial measurements |
| --- | --- |
| `phases` | before/candidate/Dapper, each at 1/100/1000 rows; 256 iterations × 3 windows; Dapper reads that run's corresponding candidate receipt |
| `calibration` | All 35 cases, C=1/4/8, 15 seconds each; cohort order rotates before→candidate→Dapper, candidate→Dapper→before, Dapper→before→candidate |
| `offered` | Three cohorts, 30 seconds each; requires the explicitly selected `--concurrency C --rate R` |
| `final` | Three cohorts, 1800 seconds each plus 15 idle seconds; requires the same explicit C/R; before remains baseline |

Mixed runs explicitly pass the names in the actual `queries-v3.json` order,
rows/batch=32, tenants=8, orders/tenant=1024, prepared mode, persistent sessions,
warmup=64 and verification. `--queue-capacity` defaults to the existing consumer
default of 64 and is explicit in every mixed command; pass a different observed
choice explicitly. The generator does not choose a rate or an acceptance threshold.
Both providers must use the chosen matching parameters for their cohorts.

Every plan owns a fresh database inside its fresh output directory. Mixed plans
begin with a separate Korda `--initialize --operations 0` command, which exits
after initialization and receives no timing credit. The phases consumer instead
has positional `initialize` and always runs a probe afterward: its separate
fixture command uses 1 iteration/1 window and is wholly excluded from timing
comparison. Its existing fixture is 2 tenants × 1000 rows; the 8×1024 mixed
dataset does not apply to phases. All nine ordinary phase commands omit initialization.

The printed runner command pins the observer to CPU 8; commands pin clients to
0–3, and runner-owned PostgreSQL uses 4–7 with a private `pgdata` directory and
at least eight spare connections. These are requested affinities, not proof of
exclusive CPUs or cgroup accounting. Existing runner observations must document
the real host. Run provider plans serially with compilation, tests and profiling
stopped. Keep diagnostic instrumentation in separate processes.

Plan/output paths cannot already exist, and the plan must be outside the output
directory. Existing runner freshness checks also apply when the printed command
is eventually executed. Preserve failed directories and generate new paths for
retries. Rehash frozen inputs around execution; this generator's hashes describe
generation time, not a claim that later files cannot change. The four final
candidate/Dapper cells across two providers receive credit only through the
existing continuation analysis of actual receipts, counts and per-second
progress. Before data, calibration, fixture probes and plan text grant no such
credit. No CI or historical acceptance tool is changed.
