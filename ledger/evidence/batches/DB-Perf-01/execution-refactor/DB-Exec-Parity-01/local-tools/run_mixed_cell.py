#!/usr/bin/env python3
"""One ordinary mixed35 cell, fresh deterministic DB, unchanged existing observer.

All setup and warmup are outside the consumer's measured monotonic interval.
The helper never grants acceptance from elapsed wall time alone.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('provider', choices=['sqlite', 'postgresql'])
parser.add_argument('route', choices=['korda', 'dapper'])
parser.add_argument('--family', default='baseline')
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--seconds', type=int, required=True)
parser.add_argument('--rate', type=float, required=True)
parser.add_argument('--concurrency', type=int)
parser.add_argument('--queue', type=int, default=64)
parser.add_argument('--idle', type=int, default=5)
parser.add_argument('--allocation-profile', action='store_true')
parser.add_argument('--prepare-only', action='store_true')
args = parser.parse_args()
out = args.output.resolve()
if out.exists() or out.with_suffix('.plan.json').exists():
    raise SystemExit('Every cell/attempt requires fresh output and plan paths')
if args.seconds < 1 or args.rate <= 0 or args.queue < 1:
    raise SystemExit('Finite positive duration/rate/capacity required')
if any(os.environ.get(k) for k in ['LD_PRELOAD', 'DOTNET_ThreadPool_UnfairSemaphoreSpinLimit', 'COMPlus_ThreadPool_UnfairSemaphoreSpinLimit']):
    raise SystemExit('Ordinary cells require default runtime and no inherited instrumentation')

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

manifest = root / 'worktrees/Korda/benchmarks/db-perf/workload/queries-v3.json'
assert sha(manifest) == '76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2'
cases = [x['name'] for x in json.loads(manifest.read_text())['queries']]
assert len(cases) == len(set(cases)) == 35
concurrency = args.concurrency or (4 if args.provider == 'sqlite' else 8)
initialize = root / f'consumers/baseline-{args.provider}/korda-workload/out/DbPerf.Korda'
family = 'baseline' if args.route == 'dapper' else args.family
exe = root / f'consumers/{family}-{args.provider}/{args.route}-workload/out/DbPerf.{args.route.capitalize()}'
if not exe.exists():
    raise SystemExit('Actual consumer missing: ' + str(exe))
argv = [str(exe), '--connection', '{connection}', '--case', 'mixed', '--cases', ','.join(cases),
        '--mode', 'prepared', '--session', 'persistent', '--concurrency', str(concurrency),
        '--warmup', '64', '--seconds', str(args.seconds), '--idle-seconds', str(args.idle),
        '--arrival-rate', str(args.rate), '--queue-capacity', str(args.queue),
        '--rows', '32', '--batch-rows', '32', '--tenants', '8', '--orders-per-tenant', '1024',
        '--verify', '--output', '{output}/result.json']
if args.route == 'dapper' and args.provider == 'sqlite':
    argv += ['--native-library', str(root / 'builds/baseline-sqlite/sqlite-image/shared/libsqlite3.so')]
if args.allocation_profile:
    library = root / 'diagnostics/allocation-shim/libdb-perf-alloc.so'
    argv = ['env', 'LD_PRELOAD=' + str(library), 'DB_PERF_ALLOC_PROFILE_LIBRARY=' + str(library),
            'DB_PERF_ALLOC_CAPACITY=1048576', *argv, '--allocation-profile']
plan = {
    'task': 'DB-Exec-Parity-01', 'provider': args.provider, 'route': args.route, 'family': family,
    'scope': 'Separate process-scope native allocation diagnostic; no timing credit' if args.allocation_profile
             else 'Ordinary default-runtime Release Native AOT mixed35; acceptance requires result and evidence review',
    'logicalFixture': {'manifestSha256': sha(manifest), 'tenants': 8, 'ordersPerTenant': 1024,
                       'customers': 256, 'seed': 'Unchanged Dataset.cs deterministic formulas; new empty dedicated database for each cell'},
    'sourceHelperSha256': sha(__file__),
    'commands': [
        {'name': 'initialize', 'phase': 'fixture-only', 'cpus': '0-3', 'timeoutSeconds': 240,
         'executableSha256': sha(initialize),
         'argv': [str(initialize), '--connection', '{connection}', '--initialize', '--tenants', '8', '--orders-per-tenant', '1024']},
        {'name': 'client', 'phase': 'native-allocation-diagnostic' if args.allocation_profile else 'ordinary-mixed35',
         'cpus': '0-3', 'timeoutSeconds': args.seconds + args.idle + 180,
         'executableSha256': sha(exe), 'argv': argv},
    ],
}
if args.provider == 'postgresql':
    plan['postgres'] = {'bin': str(root / 'toolchain/postgres/install/bin'), 'data': str(out / 'postgres-data'),
                        'maxConnections': 100, 'maxClientConcurrency': concurrency, 'cpus': '4-7'}
else:
    plan['connection'] = str(out / 'mixed35.sqlite')
out.parent.mkdir(parents=True, exist_ok=True)
plan_path = out.with_suffix('.plan.json')
plan_path.write_text(json.dumps(plan, indent=2) + '\n')
if args.prepare_only:
    print(plan_path)
    raise SystemExit(0)
subprocess.run(['taskset', '-c', '8', 'python3', str(root / 'worktrees/Korda/benchmarks/db-perf/run.py'),
                str(plan_path), '--output', str(out), '--sample-seconds', '0.25'], check=True)

# Reuse the repository's unchanged full business/accounting checker, without
# substituting its historical environment-admission policy for this task's scope.
import sys
sys.path.insert(0, str(root / 'worktrees/Korda/benchmarks/db-perf'))
from campaign import normalized_result
result = json.loads((out / 'result.json').read_text())
normalized = normalized_result(result, cases, args.seconds, args.rate, require_coverage=True)
assert normalized['correctnessPassed'] and normalized['counts']['failed'] == 0
if args.allocation_profile:
    assert result['NativeAllocationProfile']['passed']
else:
    assert result['TimingComparisonEligible']
record = {'task': 'DB-Exec-Parity-01', 'planSha256': sha(plan_path), 'resultSha256': sha(out / 'result.json'),
          'ordinaryTiming': not args.allocation_profile, 'newFinalCellCredit': False,
          'normalized': normalized,
          'scope': 'Accounting/oracle validation only. Long-cell identity, duration, serial execution, resource visibility and freeze require separate review.'}
(out / 'validation.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'provider': args.provider, 'route': args.route, 'family': family, 'seconds': args.seconds,
                  'rate': args.rate, 'counts': normalized['counts'], 'successOpsPerSecond': normalized['successOpsPerSecond']}), flush=True)
