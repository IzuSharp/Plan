# Local mixed-load plan selection

`select_load_cohorts.py` derives a new plan from the unchanged continuation-4
generator. It does not run the printed command, start a consumer/database, build
anything, or qualify a host. It requires Python 3.11 or later. No CI changes are
involved.

| Purpose | Original generator lane / seconds | Selected measured cohorts | Derived seconds each | Final credit requested |
| --- | --- | --- | ---: | --- |
| Same-condition before supplement | `offered` / 30 | before, candidate | 120 | None |
| Final comparison | `final` / 1800 | candidate, Dapper | 1800 | Two cells per database |

Every derived plan retains the original candidate fixture as its first command,
with `timingRequested=false`. The three original consumer identities remain in
`inputs` for provenance, but only the selected two cohorts execute measurements.
The baseline plan retains its `offered` lane; the final plan retains `final` and
its 15-second post-drain idle observation. All other workload, concurrency,
arrival-rate, queue, affinity, warmup and verification settings remain identical
to the supplied original plan. Each plan gets a fresh database/output location.

## Fixed tool identities and validation

The original generator is
[`continuation-4/generate_local_plan.py`](../../continuation-4/generate_local_plan.py),
SHA-256 `68deb860bd8ae1f0f268220e5c3b72606ff666b08a7511e1245d750b3fb1cc78`.
Its historical bytes are unchanged. Selector SHA-256 is
`507afc98c5b448bba3daeae3c3fb77ea748d983029f42a6baf5870098abba43d`.

The selector checks the complete original shape, exact lane/duration, unique
cohorts and executables, fixture boundary, full argument arrays, workload
manifest/case order, tool/native/executable hashes and output ownership. It
requires the exact full runner-source commit and verifies committed runner and
manifest bytes. It rereads every input after derivation, rejects existing output
paths, and records `derivedFrom` plan/generator/selector hashes and source tree.
It uses the source-bound runner's pure `validate_plan` function before writing.

[236 finite offline controls](verification/controls-01.json) and an
[independent review with a separate 236-control execution](verification/selector-review.md)
passed. They cover both providers and purposes, malformed or duplicated cohorts,
wrong duration/fixture/arguments/manifest/source/hash, nonfinite rates and
overwrite rejection. The preserved sample plans use **C=2, R=123 only as test
inputs**. They are not calibrated measurement plans. No sample output directory
or measured process was created. Original and derived sample JSON bytes are
retained under `verification/author-plans/` and `verification/reviewer-plans/`.

## Prepare the actual plans

Use the current final source and published consumer directories. Choose C and R
from the recorded local calibration and retain the same values for baseline and
final plans of each provider. Queue capacity and all 35 mixed cases must also
match. The selector does not choose a rate or infer a performance threshold.

For each provider, use the unchanged generator twice: `--lane offered` for the
120-second supplement's source plan, and `--lane final` for the final source
plan. Supply the actual paths and explicit C/R:

```bash
python3 "$DB_PLAN_ROOT/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-4/generate_local_plan.py" \
  --source "$DB_KORDA_SOURCE" --provider postgresql --lane final \
  --before-dir "$DB_BEFORE_BIN" --candidate-dir "$DB_CANDIDATE_BIN" \
  --dapper-dir "$DB_DAPPER_BIN" --postgres-bin "$DB_POSTGRES_BIN" \
  --concurrency "$DB_CONCURRENCY" --rate "$DB_ARRIVAL_RATE" --queue-capacity 64 \
  --plan "$DB_ORIGINAL_PLAN" --output "$DB_UNUSED_ORIGINAL_OUTPUT"

sha256sum "$DB_ORIGINAL_PLAN"

python3 "$DB_PLAN_ROOT/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/local-load-tools/select_load_cohorts.py" \
  --input "$DB_ORIGINAL_PLAN" --input-sha256 "$DB_ORIGINAL_PLAN_SHA256" \
  --generator "$DB_PLAN_ROOT/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-4/generate_local_plan.py" \
  --source-commit "$DB_RUNNER_SOURCE_COMMIT" --kind final \
  --plan "$DB_DERIVED_PLAN" --output "$DB_NEW_EVIDENCE_DIRECTORY"
```

For SQLite, use `--provider sqlite` and replace `--postgres-bin` with the exact
`--sqlite-library "$DB_SQLITE_LIBRARY"`. For the baseline supplement, change
the generator lane to `offered` and selector kind to `baseline`; the selector
sets 120 seconds. `DB_RUNNER_SOURCE_COMMIT` is the full 40-character commit of
`DB_KORDA_SOURCE`; consumer package source identities are frozen separately.
Use distinct fresh names for all four original plans, four derived plans and
their output directories. Do not run the original three-cohort plans.

## Execute and analyze the four final segments

The selector prints the actual existing runner entry point:

```bash
taskset -c 8 python3 "$DB_KORDA_SOURCE/benchmarks/db-perf/run.py" \
  "$DB_DERIVED_PLAN" --output "$DB_NEW_EVIDENCE_DIRECTORY"
```

After source/package/input freeze and the host observation, run the two
120-second provider plans and then the two final provider plans serially. Each
final provider plan runs fixture, candidate 1800 seconds, then Dapper 1800
seconds; the two providers therefore produce exactly four measured final
segments. Wait for one complete runner (including drain/idle) before starting
the next. Known local compilation, correctness tests and profiling must have
stopped; existing observer records preserve visibility limitations. Any failure
gets its own retained directory and a fresh numbered retry, not overwritten
receipts or an undisclosed best-trial selection.

The existing host observer is
[`continuation-5/observe_host.py`](../../continuation-5/observe_host.py):

```bash
taskset -c 8 python3 "$DB_HOST_OBSERVER" \
  --source "$DB_KORDA_SOURCE" --output "$DB_NEW_HOST_RECORD"
```

After all four directories are complete, the unchanged indexer and analyzer can
include both the supplement and final observations:

```bash
python3 "$DB_PLAN_ROOT/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-5/prepare_load_index.py" \
  --directory "$DB_SQLITE_BASELINE_RESULTS" --directory "$DB_POSTGRES_BASELINE_RESULTS" \
  --directory "$DB_SQLITE_FINAL_RESULTS" --directory "$DB_POSTGRES_FINAL_RESULTS" \
  --host-record "$DB_NEW_HOST_RECORD" --group-prefix DB-Exec-10 \
  --output "$DB_NEW_LOAD_INDEX"

python3 "$DB_PLAN_ROOT/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-3/analysis/analyze_execution.py" \
  --index "$DB_NEW_LOAD_INDEX" --korda-root "$DB_KORDA_SOURCE" \
  --output "$DB_NEW_LOAD_ANALYSIS"
```

The index has eight measured observations: four `offered` supplement entries and
four `final` entries. The existing analyzer accepts two-cohort comparison groups;
it does not require a `before` long run. Its `finalFour` check requires one
candidate and one Dapper result for each database, 1800 seconds, all 35 cases,
each second's business progress, raw counter conservation and nonoverlapping
intervals through drain and recorded idle. Its process exit code alone is not
an acceptance result: inspect the four cell states, timing eligibility, missing
inputs, source identities and pairwise intervals. Phase coverage appears
separately and is not fabricated by these load plans.

## Identity and ownership supplement

The final collection also requires exact source/tree, consumer source and
generated-source hashes, package/ELF/loaded-native identities, SQL contract,
generator/selector/runner hashes and each segment's actual start/end times.
The unchanged arithmetic analyzer is not a package producer attestation. Its
six owner checks plus `PullChannels` also predate `CommandCompletions`.
[`audit_final_identity.py`](audit_final_identity.py) adds those checks with
`freeze` before execution and `audit` after the existing arithmetic report.
Its [complete specification and collection procedure](final-freeze-and-audit.md)
keep source identity, business arithmetic and historical observations explicit.
The original analysis tools and measurement outputs remain unchanged.
