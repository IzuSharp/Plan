# Perf-01 completed database cohort extraction

`database_compare.py` is a source-prepared, post-run report generator. It starts
no process, application, socket or database and changes no runtime source. Do
not execute it while a calibration, profile or formal load owns the measurement
machine: streaming and hashing the full numerical ledgers is real CPU/I/O work.
No results are supplied in this note, and preparing the script is not a claim
that it or its finite fixtures have passed execution.

## Inputs and command

One invocation compares one exact provider/scenario/concurrency/rate/duration
point. Supply every completed independent process directory explicitly: normally
three before, three after and three direct Rust processes, plus three managed
Native AOT processes where available. The selected files must be finalized; a
missing or malformed ledger fails extraction rather than synthesizing a row or
discarding the process. Completed cells with observed failures stay in the
report and force an inconclusive performance comparison.

Use the unchanged A21 source actually bound by the cells, and the reviewed common
`tests/Perf01/verify_long.py` streaming reader. The script verifies their source
hashes, each cell's summary/freeze/plan/dataset hashes, and the original
application/Perf-01 receipts. It reads the raw A21 records and frozen dataset in
lockstep, checks ordered IDs/scheduled timestamps, recomputes successful latency
and count metrics, checks the independent normalized values and verifies the
existing summary metrics. Every consumed file is freshly hashed. A file that has
no earlier recorded digest is newly pinned, not authenticated against arbitrary
historical edits. Each application PID/start-tick identity must be distinct
across the supplied process cells, and their original A21 measurement windows
must not overlap on this shared monotonic clock. Every path remains recorded;
matching uses logical source names and actual artifact/lock/native hashes,
source commit/scope and toolchain metadata, not staging-directory equality.

The noise receipt comes from the before-only procedure in
`database-layered-runbook.md`, adapted to the selected scene when necessary.
Its exact SHA-256 must already be bound by the frozen Plan record. Do not generate
or widen a band after inspecting candidate values. The extractor validates the
receipt's workload, seed, data, thresholds, source-file hashes and before package
identity, and checks its recorded creation time precedes all supplied after
cells. A timestamp alone does not establish prior publication; the frozen Plan
hash remains the provenance anchor. Repository HEAD is not used as a driver-byte
comparison: runtime or unrelated analysis commits may change HEAD while the
measurement driver files remain identical.

The complete `plan.settings`, including `features.compact_observation`, is part
of the matched configuration and frozen-band check. The extractor additionally
requires that Boolean to agree with `frozen-inputs.compact_observation`; a missing
flag on both sides means the original full-retention mode. Reports display the
mode explicitly. Compact replay restores the original A21 row value/counter and
timestamp schema, so the raw-result and scheduled-arrival checks are unchanged.
Full-retention and compact cells cannot be mixed into an equivalent cohort.

```sh
PERF01_ROOT=/workspace/scratch/01c249676f47
PERF01_PRODUCT="$PERF01_ROOT/.worktree/Perf-01-linux/NativeWeave"
PERF01_PLAN="$PERF01_ROOT/.worktree/Perf-01-linux/Plan"
PERF01_PYTHON=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3

# Set these to the actual finalized matched cells and the already frozen receipt.
# The variables below are inputs, not assertions that results exist or passed.
taskset -c 8 "$PERF01_PYTHON" \
  "$PERF01_PLAN/ledger/evidence/batches/Perf-01/database_compare.py" \
  --nativeweave "$PERF01_PRODUCT" \
  --before "$PERF01_BEFORE_1" "$PERF01_BEFORE_2" "$PERF01_BEFORE_3" \
  --after "$PERF01_AFTER_1" "$PERF01_AFTER_2" "$PERF01_AFTER_3" \
  --direct "$PERF01_DIRECT_1" "$PERF01_DIRECT_2" "$PERF01_DIRECT_3" \
  --managed "$PERF01_MANAGED_1" "$PERF01_MANAGED_2" "$PERF01_MANAGED_3" \
  --noise-receipt "$PERF01_FROZEN_NOISE" --noise-sha256 "$PERF01_FROZEN_NOISE_SHA256" \
  --output "$PERF01_NEW_COMPARISON_DIRECTORY"
```

Omit the entire `--managed` option when that comparator is unavailable. An output
directory must be new and outside all raw cells. The command writes
`comparison.json` and English `comparison.md`; it never overwrites original
receipts or earlier reports. A nonzero command exit means extraction did not
complete and no output may be treated as accepted. No toolchain environment
changes are needed for this standard-library-only postprocessor.

## Statistical and accounting scope

Each process row reports success-only scheduled-arrival mean, conventional
median, A21 nearest-rank p50/p95/p99, successful logical operations/s, all outcome
counts, actual dispatch attempts, application CPU/RSS/fd/socket observations,
independently queried durable measurement commits, actual available provider
error counts and explicit retry scope. Percentiles are withheld when A21's
sample-count rule cannot resolve the requested tail. All failures remain in
the denominator/outcome ledger; success-only tails from a failed cell cannot
establish an improvement.

For mixed load, `cycle` and `page` rows are conditional slices of the same
application run. Their rates use the whole observation window. Their latency
distributions receive no separate CPU/RSS or provider-error attribution. A pure
cycle or page invocation has only a whole-load row and requires a scene-specific
band: mixed-load bands never qualify a standalone query/write point merely
because its conditional operation has the same name.

Cohort tables use equal-weight arithmetic means of per-process metrics and
retain all individual values and ranges in JSON. In particular, a mean of
process p99 values is neither a pooled p99 nor a p99 confidence interval. The
unchanged `A21.noise_comparison` bootstraps independent process means with the
already frozen workload seed. It is called only when both compared cohorts and
the supplied band are eligible; otherwise the result explicitly remains
inconclusive. A21 itself requires at least two independent processes per route;
the declared Perf-01 comparative cohort is exactly three; other supplied counts
remain descriptive and inconclusive. No favorable subset is selected
from a failed cohort.

The change rows include after-minus-before and NativeWeave-minus-direct-Rust
absolute differences and percentages. Direct Rust is the gap denominator.
The same calculations are available for the managed comparator where supplied.
A zero denominator or any missing process metric produces N/A; unavailable
values are never silently replaced by zero. Descriptive changes remain visible
when the statistical conclusion is inconclusive.

The application resource values describe the complete measured business path:
HTTP, authentication, static JSON, typed ORM/DTO work, binding, SQL and I/O.
PostgreSQL service CPU/RSS, exact connection-pool/SQL/lock-wait durations and
internal SQLite busy-handler attempts remain unavailable. SQLite BUSY/LOCKED
observer counts cover the application's lifetime, including setup and recovery;
they must not be relabeled as measurement-only counts. The independent committed
mutation count is phase-classified and excludes seed, warmup and recovery.

The extractor checks existing evidence consistency; it does not repeat network,
database durability, resource retirement or 30-minute acceptance. Long credit
still requires the separate common verifier. Capacity ladders and overload
recovery remain separate from these equal-arrival latency comparisons.

## Review and execution status

The independent protocol-domain reviewer passed the final source-only review:
exactly three independent processes gate comparative eligibility; content-based
source/artifact identities permit checkout-path differences; before/after
toolchains are compared; PID/start identities and A21 windows reject reuse or
overlap; full and conditional resource/count scopes remain explicit. The
reviewer did not execute the utility, tests or any workload. The finite synthetic
execution gate remains pending. Record its exact commit and actual outcome
before using this reporting artifact for delivered result tables.

`test_database_compare.py` prepares seven finite synthetic checks: raw cohort and
direct-denominator arithmetic with conditional resource scope; an explicitly
retained failed process; rejection of a changed band source through an
inconclusive result; zero denominator/repeated directory handling; and a changed
raw oracle value; plus two-process ineligibility and logical source-path
normalization; and compact-mode consistency/type checks. Fixtures do not execute
or accept any application load. In a
separately approved validation window, run the test file with the exact Python
above. It finds the sibling NativeWeave checkout by default; set
`PERF01_NATIVEWEAVE` explicitly when validating another checkout.
