#!/usr/bin/env bash
# Prepared only. Execute after the exclusive measurement window ends.
# Python body is copied verbatim from the committed database layered runbook.
set -euo pipefail
PERF01_ROOT=/workspace/scratch/01c249676f47
source "$PERF01_ROOT/perf01-toolchain/env.sh"
PERF01_PRODUCT="$PERF01_ROOT/.worktree/Perf-01-linux/NativeWeave"
PERF01_PYTHON=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
PERF01_DB_CALIBRATION="$PERF01_ROOT/perf01-evidence/calibration/before-sqlite-compact-v4"
PERF01_NOISE_RECEIPT="$PERF01_ROOT/perf01-evidence/noise/sqlite-mixed-c16-r54-001.json"
mkdir -p "$PERF01_ROOT/perf01-evidence/noise"
sha256sum --check <<'SHA256'
441c963149925fd232d0f3570d65d6f100bdd2b2f462ddc29c9c49fdc72b8b36  /workspace/scratch/01c249676f47/perf01-evidence/calibration/before-sqlite-compact-v4/selection.json
87102e3784fe34106058d943ad0b4f5a443c4afe0bfae101fc4eceddfb8f835e  /workspace/scratch/01c249676f47/perf01-evidence/calibration/before-sqlite-compact-v4/controller.json
dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53  /workspace/scratch/01c249676f47/.worktree/Perf-01-linux/NativeWeave/src/Benchmarks.Harness/nativeweave_bench.py
e59f692009cd2233e0a94a17ce1dea6a399b0da76a929a43d8e240407bc29ec5  /workspace/scratch/01c249676f47/.worktree/Perf-01-linux/NativeWeave/tests/Perf01/verify_long.py
SHA256
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
