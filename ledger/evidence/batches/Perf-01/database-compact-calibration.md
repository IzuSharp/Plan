# Perf-01 fresh compact database calibration

Status: source-prepared command/controller recipe. The integration owner actually
passed the 29 A21 tests and six DB affinity tests before starting
`db-generator-compact-001`; those receipts belong to the integration record.
This document claims no new calibration, selection or diagnostic outcome.

The earlier full-retention SQLite/PostgreSQL calibration directories remain
immutable preparatory evidence. Do not reuse their selected rates or noise
receipts as the final compact-mode selection, and do not relabel a generator
failure as a product regression. Both providers restart at the policy-4 low
point after the new diagnostic and source freeze are accepted.

## Unchanged policy and execution path

`database_calibrate.py` narrowly derives the database path from
`ROOT/perf01-run/calibrate-apps-v4.py`. It delegates each cell to the existing
`tests/Perf01.Database/run.py`, whose A21/B23 supervisor, provider setup, exact
response/durable oracle, observer, recovery, cleanup and process-mask checks
remain in force. It adds no alternate target or supervision implementation.
The complete command, driver/controller/policy hashes, outcome and evidence
directory are checkpointed before/after each call. The supplied package-probe
progress and observer/comparator metadata hashes are pinned across the entire
selection. NativeWeave package/observer provenance must identify the same clean
runtime source and every package's actual repository commit must agree; before
must identify the frozen `ea5fa528...` commit. Each actual frozen route is checked
against these supplied source/producer bindings. Outputs must be new.

| Setting | Value |
| --- | --- |
| Runtime before source | `ea5fa528035d025bd7a28698ee7c71194432236c`, actual retained package/observer manifests |
| Providers | SQLite and PostgreSQL, separate serial fresh-process cells and fresh databases |
| Business mix | Alternating durable cycle / typed 100-row page; original seed `20261119` |
| Client slots | 16 for capacity/long selection; 1/4/8 diagnostics remain separate |
| Service / generator CPUs | 2,3 / 0,1, with existing actual masks and identities checked |
| Oracle retention | Explicit `--compact-observation` on every compared route |
| Startup / recovery / idle | 16 warmup calls; 16 same-process recovery cycles; 5-second short idle, all separate from measured load |
| Thresholds | Zero unexpected errors, scheduled-arrival p99 at most 500 ms, app RSS at most 256 MiB, generator lag at most 100 ms |
| Initial rates | 5, 10, 20, 40, 80, 160, 320, 640 logical operations/s |
| Ladder / confirmation | 30-second stages; three new 60-second processes at the selected rate |
| Refinement | Bisect passing/failing bracket to at most 10% width or adjacent integer rates; on confirmation failure step down 10%, at most 10 rounds |
| Before long rate | `max(1, min(500, floor(0.8 * highest_consistently_passing_rate)))` |

If all listed points pass, doubling continues within the actual driver's
10,000/s and one-million-observation limits. An unbracketed result remains a
measured lower bound. All three confirmations run even when an earlier one
fails, matching the existing policy implementation; no favorable subset is
selected. The cell's zero exit status is also required, so a post-summary
cleanup failure cannot qualify. Generator-invalid failures do not establish a
server-capacity upper bound. Overload recovery is the existing same-process
driver phase; it never replaces the failed measurement verdict.

The new controller is not a restart/resume engine. An incomplete child stops the
sequence and preserves its directory and partial controller receipt. Root must
inspect the existing supervision evidence and confirm all owned processes have
stopped before starting a new attempt. Do not skip an incomplete row or reuse its
output path. SIGTERM or forced termination of this thin wrapper is not claimed
to run a graceful checkpoint/child cleanup; the last checkpoint may still say
`running` and the already registered domain descendants may remain live. Root
must inspect and stop those known processes using the existing supervision
receipts before another load. An after/comparator capacity selection never changes the paired
before-derived long rate.

## Exact before command

The diagnostic must have completed and root must own the exclusive resource
window. Source the existing toolchain environment so the exact interpreter also
finds the pinned HTTPX dependencies. The policy SHA is captured from the actual
immutable revision-4 file; the controller verifies it before every cell.

```sh
PERF01_ROOT=/workspace/scratch/01c249676f47
source "$PERF01_ROOT/perf01-toolchain/env.sh"
PERF01_PRODUCT="$PERF01_ROOT/.worktree/Perf-01-linux/NativeWeave"
PERF01_PLAN="$PERF01_ROOT/.worktree/Perf-01-linux/Plan"
PERF01_ANALYSIS="$PERF01_PLAN/ledger/evidence/batches/Perf-01"
PERF01_PYTHON=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
PERF01_POLICY="$PERF01_ANALYSIS/prospective-policy.json"
read -r PERF01_POLICY_SHA PERF01_POLICY_PATH_TOKEN < <(sha256sum "$PERF01_POLICY")

taskset -c 2,3 "$PERF01_PYTHON" "$PERF01_ANALYSIS/database_calibrate.py" \
  --nativeweave "$PERF01_PRODUCT" \
  --policy "$PERF01_POLICY" --policy-sha256 "$PERF01_POLICY_SHA" \
  --package-probe "$PERF01_ROOT/perf01-build/before/reference-002" \
  --observer "$PERF01_ROOT/perf01-build/before/db-observer/manifest.json" \
  --postgres-bin "$PERF01_ROOT/perf01-toolchain/postgres18/bin" \
  --variant before --groups sqlite postgresql --attempt compact-v4 \
  --output-root "$PERF01_ROOT/perf01-evidence/calibration" \
  --isolation-note 'Exclusive Perf-01 compact DB calibration; all other local builds/profiles/loads stopped; service CPUs2,3 and generator CPUs0,1; physical-host controls unavailable'
```

This creates `before-sqlite-compact-v4/` and
`before-postgresql-compact-v4/`, each with its own `controller.json`, individual
cell directories/logs and final `selection.json` if the complete sequence passes.
The policy file is not edited. Application/library hashes still come from the
actual consumer/observer/loaded-mapping evidence, not this command's path labels.

Root may run one provider at a time by supplying only that provider in
`--groups`. The other provider still starts from its own low point and fresh
database. The source controller and flags must stay identical for both.

## Direct Rust, managed and final after comparisons

For an independently requested comparator capacity ladder, use the same command
and controller with the actual comparator manifest, replace `--variant before`
with `--variant direct` or `--variant managed`, and replace `--observer ...` with:

```sh
--comparators "$PERF01_ROOT/perf01-build/comparators/comparators.json"
```

All workload/affinity/compact-observation/SLO/recovery flags remain identical.
The controller chooses `direct-rust` or `managed-aot` and never launches the
NativeWeave exception observer for those routes. Their provider BUSY/LOCKED
observability remains whatever the actual comparator supplies; missing counters
are unavailable, not inferred from HTTP failures. These capacity ladders do not
freeze a new long rate. A later after ladder uses `--variant after` plus the
actual fresh after package and observer manifests, with the same controller.

Fixed-load short before/after/direct/managed comparison cells continue to use
the existing direct DB driver command from `database-layered-runbook.md`, adding
`--compact-observation` to **every** route. Use the new before selection's rate
and fresh independent noise/confirmation cohorts. Do not use a rate selected
from after or direct results to retune the paired load. Long stages likewise
add this flag and use the same before-derived rate with the prospective
1802-second schedule and separate 60-second idle/32-request recovery; final
credit still requires the common conservative 1800-second verifier.

## Extraction compatibility and review

Compact replay restores the complete original A21 `records`, including exact
normalized values, counter dictionaries, late metadata and all operation/window
timestamps. `database_compare.py` continues to validate those final rows and
the pinned A21 source rather than guessing a new abbreviated schema.
Its existing full `plan.settings` equality and noise applicability already
compare `features.compact_observation`. The explicit consistency check now also
requires the Boolean to agree with `frozen-inputs.compact_observation` and
prints the mode. Both absent means the original mode; an integer/string flag or
a plan/freeze mismatch is rejected. New compact and old full-retention cells
cannot enter an equivalent matched cohort.

Root independently passed the control-loop, existing supervision, actual exit
status, compact-mode and before-only selection source review of `5f543385`.
The codec reviewer also passed those paths and requested the producer metadata
pin/provenance tightening described above. The protocol reviewer subsequently
passed the complete producer-pin follow-up, actual metadata/route binding,
compact-mode/type fixture and explicitly limited interruption contract. These
source reviews are not execution claims. Root's selected finite
gate remains separate. No controller, test, extraction or new workload was
executed by the author during the active compact diagnostic. Update the
integration execution record with actual source commits and results before using
them for final measurements or reporting. If this wrapper is interrupted,
inspect and stop its known supervised descendants before any other load; this
is not a new long-running supervision mechanism.
