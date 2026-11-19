# Perf-01 database layered comparisons and frozen noise

This is a source-prepared execution guide, not a record that the commands ran.
Use the committed Perf-01 DB driver for every route. NativeWeave before is the
frozen product commit `ea5fa528035d025bd7a28698ee7c71194432236c`; its fresh
package application is `perf01-build/before/reference-002`, with the identical
catch/log/rethrow observer in `perf01-build/before/db-observer/manifest.json`.
The after application/observer must come from the actual complete rebuilt B24
closure and remain immutable after preparation. Ordinary DTO/handler source and
the measurement driver remain identical across the two versions.

The final DB measurement driver is a detached, immutable checkout at
`ce2a3c75cbd535490897d062b6cbb7c095408307`, located at
`ROOT/.worktree/Perf-01-frozen-drivers-linux/NativeWeave`. All later DB timed
before/after/direct/managed cells and before-only noise extraction use that
checkout. Its reader remains SHA-256
`8034692b643f4dbb1385cd61e25c9d4d6f084d7b71268fec02411b5c2fcdbeb4`;
the separately invoked final post-run verifier may advance without changing the
measurement helper. Product packages are prepared from their respective source
commits and supplied through explicit package/observer descriptors. No full-file
source comparison is weakened when a post-run-only protocol verifier changes.

## Completed before-only bindings

Final v5 calibration selected SQLite **50/s** (paired long **40/s**) and
PostgreSQL **180/s** (paired long **144/s**). The exact three final confirmation
processes supplied the before-only noise receipts at **13:10:14–13:10:20 UTC on
2026-11-19**, after all DB calibration stopped and before any runtime edit or
after measurement. This six-second extraction ran no application load. See the
[executed noise record](checks/database-noise-freeze-001/README.md), the
[SQLite selection](observations-before/sqlite-compact-v5-selection-001/README.md),
the [PostgreSQL selection](observations-before/postgresql-compact-v5-selection-001/README.md)
and [domain freeze bindings](database-final-freeze-draft.json). The later
comparison cohorts described below remain prospective and must use fresh
processes. The recorded scripts use exclusive creation and must not overwrite
these frozen receipts.

## Scene and load selection

Run PostgreSQL and SQLite independently. A logical `cycle` contains a durable
create, same-key replay and recovery lookup; a `page` is one typed 100-row page;
`mixed` alternates those logical operations 50:50. Report logical operations and
actual successful commits separately. These are whole-application socket paths,
not isolated SQL execution latency. The public PageProbe supplies a separate,
profiling-only buffered-query view.

The prospective scoped comparison is one matched **mixed/concurrency16** anchor
per provider, with three fresh independent processes per route and separate
conditional cycle/page extraction. In addition, run one exploratory **mixed** cell
per route/provider at concurrency **1, 4, 8**; concurrency16 reuses the anchor.
Keep the physical database pool, durability, seed, HTTP/1 connection reuse, CPU
masks and application limits unchanged; `--concurrency` changes the external
client slots only. All routes at one point use the same offered rate, duration
and inputs. The same explicit compact-observation mode and actual driver bytes
are required throughout.

Select rates from **before-only** evidence before product edits. The existing
primary capacity ladder is mixed/concurrency16. Its final accepted selection and
three final 60-second confirmation processes define the high-load anchor. Keep
that exact anchor for the formal fixed-load before/after/direct comparison.
The initial before-only exploratory grid is
`min(5 * concurrency, confirmed_mixed_rate)` logical operations/s at concurrency
1,4,8. Freeze these actual points before examining candidate results and use
them unchanged for after/direct/managed cells. An exploratory failure remains a
failure and does not trigger a candidate-dependent retune.

Keep the formal C16 anchor at **three fresh 60-second processes per route**.
For the descriptive grid, use **one 60-second process at C1** and **one 20-second
process at each of C4 and C8** per route/provider. These durations are chosen
prospectively before any product edit or after result and remain identical for
before/after/direct/managed. The grid cannot claim statistical significance.

For a final before anchor of at least 40/s, the declared rates are 5/s, 20/s and
40/s at C1/C4/C8. The unchanged finite scheduler uses
`ceil(seconds * 1e9 / round(1e9 / rate)) + 1` planned operations. Consequently:

| Descriptive point | Duration | Planned operations | Cycle / page observations if all succeed |
|---|---:|---:|---:|
| C1 at 5/s | 60 s | 301 | 151 / 150 |
| C4 at 20/s | 20 s | 401 | 201 / 200 |
| C8 at 40/s | 20 s | 801 | 401 / 400 |

These are prospective population calculations, not executed results. Recalculate
from the actual frozen `min(5 * concurrency, anchor)` rate if the final anchor is
lower. A slice needs at least 100 successes for p99; otherwise report it
unavailable. No candidate-dependent rate or duration retune is permitted.
Preserve each overload/recovery row. A failed error/SLO/generator point
cannot establish a latency improvement; a generator-limited point does not bound
server capacity. The selected maximum sustainable sampled rate is a separate
result from fixed-arrival latency. NativeWeave, direct Rust and managed routes
must meet the same zero-error/500-ms-p99/256-MiB-application-RSS criterion.

This scope is selected before final formal cohorts and product edits. A full
standalone-cycle/page × concurrency1/4/8/16 × all-route triplet matrix would add
many fresh processes without isolating another changed boundary. The mixed
anchor exercises both typed paging/DTO materialization and durable transactions;
the smaller concurrency grid exposes contention/queueing changes, and the public
100-row PageProbe supplies the separate buffered-query profile. Standalone
cycle/page runs remain optional if a concrete unresolved hotspot requires them.
Existing preparatory or failed cells are not relabeled as these formal cohorts.

## Exact command template

Set `PERF01_AFTER_PACKAGE` and `PERF01_AFTER_OBSERVER` from the actual after build
receipts, not a historical candidate. The shell function below is documentation;
invoke it only under root's exclusive timing ownership, serially.

```bash
PERF01_ROOT=/workspace/scratch/01c249676f47
source "$PERF01_ROOT/perf01-toolchain/env.sh"
PERF01_PRODUCT="$PERF01_ROOT/.worktree/Perf-01-frozen-drivers-linux/NativeWeave"
PERF01_PLAN="$PERF01_ROOT/.worktree/Perf-01-linux/Plan"
PERF01_PYTHON=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
PERF01_BEFORE_PACKAGE="$PERF01_ROOT/perf01-build/before/reference-002"
PERF01_BEFORE_OBSERVER="$PERF01_ROOT/perf01-build/before/db-observer/manifest.json"
PERF01_COMPARATORS="$PERF01_ROOT/perf01-build/comparators/comparators.json"

perf01_db_cell() {
  local provider="$1" scene="$2" slots="$3" rate="$4" variant="$5" repeat="$6" output="$7"
  local seconds
  case "$slots" in
    1|16) seconds=60 ;;
    4|8) seconds=20 ;;
    *) return 2 ;;
  esac
  local package="$PERF01_BEFORE_PACKAGE"
  local -a route_args=() provider_args=()
  case "$variant" in
    before) route_args=(--route nativeweave-aot-rust --observer "$PERF01_BEFORE_OBSERVER") ;;
    after) package="$PERF01_AFTER_PACKAGE"
           route_args=(--route nativeweave-aot-rust --observer "$PERF01_AFTER_OBSERVER") ;;
    direct) route_args=(--route direct-rust --comparators "$PERF01_COMPARATORS") ;;
    managed) route_args=(--route managed-aot --comparators "$PERF01_COMPARATORS") ;;
    *) return 2 ;;
  esac
  if [ "$provider" = postgresql ]; then
    provider_args=(--postgres-bin "$PERF01_ROOT/perf01-toolchain/postgres18/bin")
  fi
  taskset -c 2,3 "$PERF01_PYTHON" "$PERF01_PRODUCT/tests/Perf01.Database/run.py" \
    --package-probe "$package" "${route_args[@]}" "${provider_args[@]}" \
    --provider "$provider" --protocol http1 --scenario "$scene" --stage short \
    --variant "$variant" --repetition "$repeat" --rate "$rate" --seconds "$seconds" \
    --concurrency "$slots" --warmup 16 --recovery-requests 16 --idle-seconds 5 \
    --seed 20261119 --max-p99-ms 500 --max-rss-mib 256 \
    --generator-cpus 0,1 --continue-classified-overload --compact-observation --output "$output" \
    --isolation-note 'Exclusive Perf-01 timing; service/database CPUs2,3; generator CPUs0,1; physical-host controls unavailable'
}
```

The required `--package-probe` is retained for comparator invocations, but the
comparator descriptor uses the separately hashed `comparators.json` artifacts.
Do not pass a NativeWeave exception observer to direct Rust or managed routes.
The immutable comparator manifest uses the locked Rust/SQLx and managed Native
AOT producers, including the pinned bundled SQLite source. It is not rebuilt
against the optimized product. Preserve unsupported semantics explicitly instead
of substituting another implementation.

At the mixed/concurrency16 anchor, use repetition0 order `before, after, direct, managed`, repetition1
the reverse order, then repetition2 the first order again. Every invocation gets
a new directory and equivalent fresh database. Record the executed order and
source/package/executable/actual native hashes. These short settings deliberately
match the current confirmation shape; the ten formal long cells separately use
1802 seconds, their frozen high-load mix, at least32 recovery calls and60 seconds
idle, plus the common duration verifier.

At each exploratory concurrency1/4/8 point, run only the declared repetition0
matched order, with 60/20/20 seconds respectively, and label its metrics
descriptive. Do not submit one such process
as a three-process statistical cohort or reuse the anchor's noise band there.

## Freeze mixed-anchor noise before seeing after results

Use the **final complete confirmation triplet**, not three favorable rows chosen
from failed attempts. In each provider's finalized
`perf01-evidence/calibration/before-PROVIDER-compact-v5-target` (or the explicitly
named fresh final attempt with the same outcome-journal implementation), `selection.json` identifies the
accepted rate and pins `controller.json`. The final three controller entries must
be `confirmation-0`, `confirmation-1`, `confirmation-2`, all at that rate, each
completed, valid and service-qualified. Require their summaries and raw A21 rows
to contain full on-time logical success, exact loaded identities, independent
durable correctness and valid generation. Do not run this extraction while those
files are still being written. Full-retention calibrations, profiling-only
directories and prior compact versions with different driver/reader bytes are
preparatory evidence and cannot supply this band's triplet.

Yes: these final three 60-second before-only confirmations can supply the noise
calibration without another identical triplet, **at that exact selected mixed
load only**. They are the predetermined final complete group, not a favorable
subset of attempts. The subsequent comparison still uses fresh interleaved
before/after/direct processes. Freeze and publish the receipt before any after
timing; its SHA is a required input to `database_compare.py`.

For each independent process, compute exact scheduled-arrival means from raw
`completion_ns - scheduled_ns` separately for all rows, cycle rows and page rows.
Classify cycle/page using that cell's actual hashed `dataset.json` input token,
not its observed latency or response status. Preserve three process means for
each slice; do not treat thousands of requests inside one process as independent
process replicates.

For each slice, freeze:

```python
band = {
    "baseline_id": "Perf-01/<provider>/mixed/c16/r<rate>/<slice>/<receipt-sha256>",
    "absolute_noise_ns": max(1000, max(before_process_means) - min(before_process_means)),
    "relative_noise": 0,
}
comparison = a21.noise_comparison(
    comparison_before_process_means, comparison_after_process_means, band, 20261119)
```

`src/Benchmarks.Harness/nativeweave_bench.py:noise_comparison` is the unchanged
authority: 2000 seeded independent-process bootstrap mean differences, the
existing 95% order-statistic interval, and the frozen absolute band. The effect is
candidate mean minus before mean, so a negative value is lower latency. The
small three-process count limits precision. p99 is reported separately; this
mean bootstrap must not be relabeled a p99 confidence interval.

Before any after timing, write and commit an immutable noise receipt containing
provider, mixed scenario, concurrency16, exact offered rate/period, duration,
the three directories and process means/counts, all three bands, and SHA-256 for
each `summary.json`, `frozen-inputs.json`, `plan.json`, `dataset.json`, and
`observation.json`. Also pin the final selection/controller, A21 source, DB
driver/target/resource/affinity sources, extraction code or this reviewed recipe,
policy revision, actual before package/observer/native identities and CPU layout.
An existing receipt must not be overwritten. Root's final frozen record binds it.

The following extraction command implements that calculation without running an
application. Set `PERF01_DB_CALIBRATION` to the finalized provider calibration
directory and `PERF01_NOISE_RECEIPT` to a new evidence path. Execute after a
timing window, using the already reviewed common streaming reader:

```bash
taskset -c 8 "$PERF01_PYTHON" - "$PERF01_PRODUCT" "$PERF01_DB_CALIBRATION" "$PERF01_NOISE_RECEIPT" <<'PY'
import base64, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
product, calibration, destination = map(Path, sys.argv[1:])
sys.path.insert(0, str(product / 'tests/Perf01'))
from verify_long import array_records
def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
def read(path):
    return json.loads(Path(path).read_text())
selection = read(calibration / 'selection.json')
controller = read(calibration / 'controller.json')
assert sha(calibration / 'controller.json') == selection['controller_sha256']
assert selection['policy_sha256'] == controller['policy_sha256']
assert selection['compact_observation'] is True and controller['compact_observation'] is True
assert selection['variant'] == controller['variant'] == 'before' and controller['state'] == 'completed'
triplet = controller['cells'][-3:]
assert [row['phase'] for row in triplet] == ['confirmation-0', 'confirmation-1', 'confirmation-2']
means = {key: [] for key in ('mixed', 'cycle', 'page')}
inputs, processes, signatures, instances, windows = {}, [], [], [], []
for cell in triplet:
    assert cell['state'] == 'completed' and cell['exit_code'] == 0 and cell['valid'] and cell['qualifies']
    assert cell['rate'] == selection['highest_consistently_passing_rate'] and cell['seconds'] == 60
    root = Path(cell['directory']); summary = read(root / 'summary.json')
    frozen = read(root / 'frozen-inputs.json'); plan = read(root / 'plan.json')
    assert sha(root / 'summary.json') == cell['summary_sha256']
    assert sha(root / 'frozen-inputs.json') == cell['frozen_inputs_sha256']
    assert summary['valid'] and summary['qualifies_service_standard'] and summary['successful'] == summary['offered']
    assert summary['variant'] == 'before' and summary['scenario'] == 'mixed' and summary['concurrency'] == 16
    assert summary['provider'] == selection['group'] and summary['rate'] == cell['rate']
    assert frozen['compact_observation'] is True and plan['settings']['features']['compact_observation'] is True
    assert frozen.get('formal_timing_eligible') is not False
    assert frozen['route']['source']['commit'] == 'ea5fa528035d025bd7a28698ee7c71194432236c'
    assert sha(root / 'frozen-inputs.json') == summary['frozen_inputs_sha256']
    assert sha(root / 'plan.json') == frozen['plan_sha256']
    assert sha(root / 'dataset.json') == frozen['dataset_sha256'] == plan['oracle']['sha256']
    signatures.append({'seed': plan['seed'], 'dataset_sha256': frozen['dataset_sha256'], 'service_standard': frozen['service_standard'],
                       'timing': plan['timing'], 'settings': plan['settings'], 'source_files': frozen['source_files'], 'route': frozen['route'],
                       'host': {key: value for key, value in frozen['host'].items() if key != 'background_load'},
                       'affinity': {key: frozen['affinity'].get(key) for key in ('mode', 'service_cpus', 'generator_cpus')}})
    sums = {key: 0 for key in means}; counts = dict(sums)
    metadata = {'measurement_window_ns': None}
    rows = array_records(root / 'observation.json', 'records', metadata)
    data = array_records(root / 'dataset.json')
    for index, (row, entry) in enumerate(zip(rows, data, strict=True)):
        assert row['id'] == index and row['status'] == 'ok'
        assert row['scheduled_ns'] <= row['dispatch_ns'] <= row['admission_ns'] <= row['completion_ns']
        item = json.loads(base64.urlsafe_b64decode(entry['input']))
        assert item['kind'] in ('cycle', 'list')
        kind = 'cycle' if item['kind'] == 'cycle' else 'page'
        latency = row['completion_ns'] - row['scheduled_ns']
        for key in ('mixed', kind): sums[key] += latency; counts[key] += 1
    assert counts['mixed'] == plan['timing']['requests'] == summary['offered']
    assert min(counts.values()) >= 100
    for key in means: means[key].append(sums[key] / counts[key])
    identities = summary['resources']['measurement']['identities']
    assert len(identities) == 1
    instance = (identities[0]['pid'], identities[0]['start_ticks'])
    assert all(type(value) is int and value > 0 for value in instance)
    instances.append(instance)
    window = metadata['measurement_window_ns']
    assert type(window['start']) is int and type(window['end']) is int and window['end'] > window['start']
    windows.append((window['start'], window['end']))
    processes.append({'directory': str(root), 'counts': counts, 'sum_arrival_ns': sums, 'loaded_files': summary['loaded_files'],
                      'application_instance': identities[0], 'measurement_window_ns': window})
    for name in ('summary.json', 'frozen-inputs.json', 'plan.json', 'dataset.json', 'observation.json'):
        inputs[str(root / name)] = sha(root / name)
assert all(signature == signatures[0] for signature in signatures)
assert len(set(instances)) == 3
windows.sort()
assert all(windows[index - 1][1] <= windows[index][0] for index in range(1, len(windows)))
for path in (calibration / 'selection.json', calibration / 'controller.json', product / 'src/Benchmarks.Harness/nativeweave_bench.py', product / 'tests/Perf01/verify_long.py'):
    inputs[str(path)] = sha(path)
identity = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
bands = {key: {'baseline_id': f"Perf-01/{selection['group']}/mixed/c16/{selection['highest_consistently_passing_rate']}/{key}/{identity}",
              'absolute_noise_ns': max(1000, max(values) - min(values)), 'relative_noise': 0} for key, values in means.items()}
receipt = {'task': 'Perf-01', 'created_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'before-only mixed anchor and conditional cycle/page slices',
           'provider': selection['group'], 'rate': selection['highest_consistently_passing_rate'], 'concurrency': 16,
           'policy_sha256': controller['policy_sha256'], 'process_means_ns': means, 'bands': bands,
           'processes': processes, 'configuration': signatures[0], 'inputs_sha256': inputs}
with destination.open('x') as stream:
    json.dump(receipt, stream, indent=2, sort_keys=True); stream.write('\n')
print(sha(destination))
PY
```

Pin this committed recipe (or the exact copied extraction script) in the final
record as well. The command's result is calibration evidence, not an after
comparison. The unchanged A21 `noise_comparison` call above consumes fresh
matched before/after or before/direct process-mean vectors later.

The three mixed-derived bands apply only to that **same mixed/concurrency16/rate
anchor and its conditional slices**. They do not calibrate standalone page/cycle
or concurrency1/4/8 cells: those workloads change queueing and contention. The
prospectively selected single-process exploratory grid therefore carries an
explicitly descriptive/inconclusive noise verdict. Any future statistical claim
at another point needs its own before-only three-process band, frozen before its
after results. Use fresh interleaved before/after process means for the comparison
while keeping the previously frozen band; do not widen the band to accommodate
after variability or pool old overload failures into an apparently clean sample.

After all fresh anchor cohorts complete, the existing extractor consumes the
frozen receipt without recalculating its bands:

```bash
read -r PERF01_NOISE_SHA PERF01_NOISE_PATH_TOKEN < <(sha256sum "$PERF01_NOISE_RECEIPT")
taskset -c 8 "$PERF01_PYTHON" "$PERF01_PLAN/ledger/evidence/batches/Perf-01/database_compare.py" \
  --nativeweave "$PERF01_PRODUCT" \
  --before "$PERF01_BEFORE_0" "$PERF01_BEFORE_1" "$PERF01_BEFORE_2" \
  --after "$PERF01_AFTER_0" "$PERF01_AFTER_1" "$PERF01_AFTER_2" \
  --direct "$PERF01_DIRECT_0" "$PERF01_DIRECT_1" "$PERF01_DIRECT_2" \
  --managed "$PERF01_MANAGED_0" "$PERF01_MANAGED_1" "$PERF01_MANAGED_2" \
  --noise-receipt "$PERF01_NOISE_RECEIPT" --noise-sha256 "$PERF01_NOISE_SHA" \
  --output "$PERF01_COMPARISON_OUTPUT"
```

Set these directory variables from the actual completed cells; they are not
placeholder results. Omit `--managed` only when that optional equivalent cohort
was not executed. The extractor requires matching compact mode, seed, dataset,
timing/settings/service standard, relevant driver content hashes and before
package/application identity. It checks actual comparison-process identities and
nonoverlapping windows, retains failed cells, and permits checkout/output-path
differences through logical-file/content identities. It does not require the
entire driver repository HEAD to stay equal as runtime/test-only commits advance.
The receipt's frozen SHA and publication chronology must also be bound by the
Plan freeze; its JSON timestamp alone is not proof that it predates after work.
The noise triplet is separate from every later comparison process.

For direct Rust, report matched-load mean/p99 absolute values and
`100 * (NativeWeave - directRust) / directRust`, together with errors and actual
successful throughput. At a fixed open-loop arrival rate, equal success rates
alone do not imply equal maximum capacity. PostgreSQL service CPU/RSS, exact
pool/lock waits and internal SQLite busy-handler retry counts remain unavailable
in the timing adapter. Report measured application/generator resources and actual
independently reconciled commits; do not attribute the whole difference to FFI.

## Source review scope

The protocol-domain reviewer read the command template, current DB result
schema, revision-3 selection controller and extraction recipe. The final review
confirmed the locked environment setup, equality of selection/controller policy
hashes, seed/dataset/threshold provenance, process-mean noise calculation and
restriction of mixed-derived bands to their original mixed-load anchor. The
review reported no remaining source blocker. Neither the author nor reviewer
executed this extraction recipe or any application load while preparing this
runbook; measured selections and later comparisons require separate receipts.
The later scoped-grid/compact-mode clarification is prospective. Its updated
finite extraction example adds process/window checks and is still a documented
command, not an executed extraction or a new measurement result.
The protocol reviewer separately checked the updated compact controller schema,
scoped commands, process/window fields and existing extractor CLI. The two
requested comparisons against the controller's previously recorded summary and
frozen-input hashes are included. This follow-up was source-only; no extraction,
test or load was run by the reviewer.

The later 60/20/20-second descriptive-grid duration refinement is prospective,
before any runtime candidate or after data. C16 formal comparison remains three
fresh 60-second processes; no actual earlier cell is relabeled. The finite
population basis above and `database-final-freeze-draft.json` are policy inputs,
not completed measurements or frozen noise receipts.

Root and the protocol-domain reviewer independently source-checked the final
60/20/20-second grid, exact scheduler count formula, lower-anchor p99 rule and
source-pinned domain draft. Both reported no blocker; neither ran this grid or
any additional test/load to review the documentation change.
