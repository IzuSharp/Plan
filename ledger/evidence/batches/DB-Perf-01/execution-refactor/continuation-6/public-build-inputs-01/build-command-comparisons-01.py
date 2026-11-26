from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import sys

BASE = Path('/workspace/scratch/4a65d70f0fe1')
PROVIDER = sys.argv[1]
if PROVIDER not in ('sqlite', 'postgresql'):
    raise RuntimeError('Unknown provider')
SOURCE = BASE / ('worktrees/DB-Exec-07-pack-' + PROVIDER)
EXPECTED = '8789a45a52cc0cc0a0b62737542d9c120b753c9b'
OUTPUT = BASE / ('artifacts/command-comparison-build-' + PROVIDER + '-01.json')
if OUTPUT.exists() or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=SOURCE, text=True).strip() != EXPECTED:
    raise RuntimeError('Fresh exact-source build required')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

environment = os.environ | {'DOTNET_PROCESSOR_COUNT': '1', 'UseSharedCompilation': 'false', 'MSBUILDDISABLENODEREUSE': '1'}
stages = [
    ('baseline-workload', [sys.executable, 'benchmarks/db-perf/managed/build.py', '--provider', PROVIDER,
        '--feed', str(BASE / 'worktrees/DB-Exec-02-before-f0078da7/artifacts/public/feed'),
        '--version', '0.1.0-ci.1', '--kind', 'workload',
        '--output', str(BASE / ('consumers/before-current-' + PROVIDER + '-workload-01'))]),
    ('ffi-workload', [sys.executable, 'benchmarks/db-perf/cursor-diagnostics/build.py',
        '--consumer', str(BASE / ('consumers/command-' + PROVIDER + '-workload-01')),
        '--source', str(SOURCE), '--output', str(BASE / ('consumers/ffi-command-' + PROVIDER + '-workload-01'))]),
]
records = []
for stage, argv in stages:
    log = BASE / ('artifacts/command-comparison-' + PROVIDER + '-' + stage + '-01.log')
    row = {'stage': stage, 'argv': argv, 'cwd': str(SOURCE),
           'startedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with log.open('xb') as stream:
        result = subprocess.run(argv, cwd=SOURCE, env=environment, stdout=stream, stderr=subprocess.STDOUT)
    row.update(exitCode=result.returncode, finishedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               log=str(log), logSha256=sha(log))
    records.append(row)
    OUTPUT.write_text(json.dumps({'task': 'DB-Exec-07', 'provider': PROVIDER, 'sourceCommit': EXPECTED,
        'scriptSha256': sha(__file__), 'buildOnlyProcessorCount': 1, 'records': records,
        'scope': 'Fresh current harness over original baseline package and separate ABI-only diagnostic over current candidate.'}, indent=2) + '\n')
    print(json.dumps({'provider': PROVIDER, 'stage': stage, 'exitCode': result.returncode}), flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)
print(json.dumps({'receipt': str(OUTPUT), 'sha256': sha(OUTPUT)}), flush=True)
