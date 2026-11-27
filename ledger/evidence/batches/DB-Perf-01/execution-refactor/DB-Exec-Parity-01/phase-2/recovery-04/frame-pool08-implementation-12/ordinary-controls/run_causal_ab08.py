#!/usr/bin/env python3
"""Finite frame-pool08 related32 reversed A/B with existing 5-second released idle observation.

The caller must reserve an exclusive timing window. Allocation-profile runs are
separately identified and never receive timing credit.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

p = argparse.ArgumentParser()
p.add_argument('--provider', choices=['sqlite', 'postgresql'], required=True)
p.add_argument('--baseline', type=Path, required=True)
p.add_argument('--candidate', type=Path, required=True)
p.add_argument('--dapper', type=Path)
p.add_argument('--sqlite-library', type=Path)
p.add_argument('--scenario', action='append', required=True, help='case:rows:mode')
p.add_argument('--operations', type=int, default=2048)
p.add_argument('--warmup', type=int, default=64)
p.add_argument('--rounds', type=int, default=2)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--allocation-profile', action='store_true')
p.add_argument('--prepare-only', action='store_true')
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
out = a.output.resolve()
assert not out.exists() and not out.with_suffix('.plan.json').exists()
assert a.operations > 0 and a.rounds > 0
assert a.scenario == ["related:32:prepared"] and a.operations == 2048 and a.warmup == 128 and a.rounds == 2
assert not a.allocation_profile, "This finite ordinary screen is not a diagnostic build"
assert not any(os.environ.get(k) for k in ['LD_PRELOAD', 'KORDA_TAIL_DIAGNOSTIC_PATH', 'DOTNET_PROCESSOR_COUNT',
    'DOTNET_ThreadPool_UnfairSemaphoreSpinLimit', 'COMPlus_ThreadPool_UnfairSemaphoreSpinLimit'])
def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()
paths = {'baseline': a.baseline.resolve(), 'candidate': a.candidate.resolve()}
if a.dapper:
    paths['dapper'] = a.dapper.resolve()
manifest = root / 'worktrees/Korda/benchmarks/db-perf/workload/queries-v3.json'
assert sha(manifest) == '76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2'
names = {q['name'] for q in json.loads(manifest.read_text())['queries']}
plan = {'task': 'DB-Exec-Parity-01', 'provider': a.provider, 'driverSha256': sha(__file__),
    'ordinaryTiming': not a.allocation_profile, 'workloadManifestSha256': sha(manifest),
    'observerSha256': sha(root / 'experiments/recovery/run_proc_tree_observer.py'),
    'originalDriverSha256': sha(root / 'local-tools/run_causal_ab.py'),
    'scope': 'Repeated isolated causal screen, not final sustained parity; one query at a time, zero external refusals',
    'commands': []}
if a.provider == 'sqlite':
    plan['connection'] = str(out / 'fixture.sqlite')
else:
    plan['postgres'] = {'bin': str(root / 'toolchain/postgres-18.0/install/bin'),
        'data': str(out / 'postgres-data'), 'maxConnections': 100, 'maxClientConcurrency': 1, 'cpus': '4-7'}
initialize = root / f'consumers/baseline-final-{a.provider}/korda-workload/out/DbPerf.Korda'
plan['commands'].append({'name': 'initialize', 'phase': 'fixture-only', 'cpus': '0-3', 'timeoutSeconds': 240,
    'executableSha256': sha(initialize), 'argv': [str(initialize), '--connection', '{connection}',
        '--initialize', '--tenants', '8', '--orders-per-tenant', '1024']})
for round_index in range(a.rounds):
    order = list(paths) if round_index % 2 == 0 else list(reversed(paths))
    for scenario in a.scenario:
        case, rows, mode = scenario.split(':')
        assert case in names and int(rows) in (1, 32, 100, 1000) and mode in ('prepared', 'dynamic')
        for route in order:
            label = f'r{round_index + 1}-{case}{rows}-{mode}-{route}'
            argv = [str(paths[route]), '--connection', '{connection}', '--case', case,
                '--mode', mode, '--session', 'persistent', '--concurrency', '1',
                '--warmup', str(a.warmup), '--operations', str(a.operations),
                '--rows', rows, '--batch-rows', '32', '--tenants', '8', '--orders-per-tenant', '1024',
                '--idle-seconds', '5',
                '--output', '{output}/' + label + '.json']
            # --verify runs every fixed mixed35 contract as an extra warmup.
            # Its Dapper related32 query cannot accept another parent count.
            # Every selected warmup/measured operation always calls Validate
            # (row count + digest), independent of this optional preflight.
            if int(rows) == 32:
                argv += ['--verify']
            if route == 'dapper' and a.provider == 'sqlite':
                argv += ['--native-library', str(a.sqlite_library.resolve() if a.sqlite_library else root / 'builds/baseline-matched-sqlite/sqlite-image/shared/libsqlite3.so')]
            if a.allocation_profile:
                shim = root / 'restored-stage1/diagnostics/allocation-shim/libdb-perf-alloc.so'
                argv = ['env', 'LD_PRELOAD=' + str(shim), 'DB_PERF_ALLOC_PROFILE_LIBRARY=' + str(shim),
                    'DB_PERF_ALLOC_CAPACITY=1048576', *argv, '--allocation-profile']
                plan['allocationShim'] = {'path': str(shim), 'sha256': sha(shim)}
            plan['commands'].append({'name': label, 'round': round_index + 1, 'route': route,
                'case': case, 'rows': int(rows), 'mode': mode, 'cpus': '0-3', 'timeoutSeconds': 600,
                'phase': 'allocation-diagnostic' if a.allocation_profile else 'ordinary-causal-ab',
                'executableSha256': sha(paths[route]), 'argv': argv})
out.parent.mkdir(parents=True, exist_ok=True)
plan_path = out.with_suffix('.plan.json')
plan_path.write_text(json.dumps(plan, indent=2) + '\n')
if a.prepare_only:
    print(plan_path)
    raise SystemExit(0)
subprocess.run(['taskset', '-c', '8', 'python3', str(root / 'experiments/recovery/run_proc_tree_observer.py'),
    str(plan_path), '--output', str(out), '--sample-seconds', '0.25'], check=True)
records = []
for command in plan['commands'][1:]:
    path = out / (command['name'] + '.json')
    result = json.loads(path.read_text())
    assert result['NativeAot'] and result['Completed'] == a.operations and result['Started'] == a.operations
    assert result['Failed'] == 0 and result['Retries'] == 0 and result['OracleFailures'] == 0
    assert not result['Errors'] and result['OfferedLoad'] is None
    assert result['TimingComparisonEligible'] == (not a.allocation_profile)
    assert result['ExecutableSha256'] == command['executableSha256']
    if command['route'] != 'dapper':
        assert result['OwnersReturnedToZero']
    if a.allocation_profile:
        assert result['NativeAllocationProfile']['passed']
    records.append({k: command[k] for k in ['name', 'round', 'route', 'case', 'rows', 'mode']} | {
        'resultSha256': sha(path), 'completed': result['Completed'], 'resultRows': result['Rows'],
        'cpuUsPerSuccess': result['CpuSecondsPerSuccessfulOperation'] * 1e6,
        'allocatedBytesPerSuccess': result['BytesPerSuccessfulOperation'],
        'serviceLatencyUs': {k: v for k, v in result['Latencies'].items() if k.startswith('P')},
        'expectedResult': result['ExpectedResults'][command['case']],
        'nativeAllocationProfile': result.get('NativeAllocationProfile')})
for scenario in a.scenario:
    case, rows, mode = scenario.split(':')
    same = [r for r in records if r['case'] == case and r['rows'] == int(rows) and r['mode'] == mode]
    assert len({(r['expectedResult']['Rows'], r['expectedResult']['Digest']) for r in same}) == 1
summary = {'task': 'DB-Exec-Parity-01', 'passed': True, 'planSha256': sha(plan_path),
    'ordinaryTiming': not a.allocation_profile, 'newFinalCellCredit': False, 'records': records}
(out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({'passed': True, 'processes': len(records), 'summary': str(out / 'summary.json')}))
