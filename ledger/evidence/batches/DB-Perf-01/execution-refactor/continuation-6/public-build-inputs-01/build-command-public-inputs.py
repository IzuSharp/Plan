from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys

BASE = Path('/workspace/scratch/4a65d70f0fe1')
PROVIDER = sys.argv[1]
if PROVIDER not in ('sqlite', 'postgresql'):
    raise RuntimeError('Choose one independent provider')
SOURCE = BASE / ('worktrees/DB-Exec-07-pack-' + PROVIDER)
EXPECTED = '8789a45a52cc0cc0a0b62737542d9c120b753c9b'
RECEIPT = BASE / ('artifacts/command-public-build-' + PROVIDER + '-01.json')
records = []

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def run(stage, argv, build_dotnet=False):
    log = BASE / ('artifacts/command-public-' + PROVIDER + '-' + stage + '-01.log')
    environment = os.environ.copy()
    if build_dotnet:
        environment.update(DOTNET_PROCESSOR_COUNT='1', UseSharedCompilation='false', MSBUILDDISABLENODEREUSE='1')
    row = {'stage': stage, 'argv': list(map(str, argv)), 'cwd': str(SOURCE), 'startedUtc': now(),
           'buildOnlyProcessorCount': 1 if build_dotnet else None}
    with log.open('xb') as stream:
        result = subprocess.run(argv, cwd=SOURCE, env=environment, stdout=stream, stderr=subprocess.STDOUT)
    row.update(exitCode=result.returncode, finishedUtc=now(), log=str(log), logSha256=sha(log))
    records.append(row)
    RECEIPT.write_text(json.dumps({'sourceCommit': EXPECTED, 'sourceTree': tree, 'sourceDirty': False,
        'provider': PROVIDER, 'scriptSha256': sha(__file__), 'records': records,
        'scope': 'Independent package and external Native AOT build inputs; execution and performance are separate.'}, indent=2) + '\n')
    print(json.dumps({'provider': PROVIDER, 'stage': stage, 'exitCode': result.returncode}), flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)

head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=SOURCE, text=True).strip()
tree = subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}'], cwd=SOURCE, text=True).strip()
if head != EXPECTED or tree != 'c8f398ae4db2d39302335a51a6378b737409f2fb' or RECEIPT.exists():
    raise RuntimeError('Fresh exact published input required')
if subprocess.check_output(['git', 'status', '--porcelain'], cwd=SOURCE, text=True):
    raise RuntimeError('Producer checkout must be clean')
run('impact', [sys.executable, 'eng/ci/impact.py', 'origin/main', '--output', 'artifacts/plan.json'])
plan = json.loads((SOURCE / 'artifacts/plan.json').read_text())
if set(plan['actions']) != {'interop', 'linux', 'postgresql', 'sqlite'} or plan['run_steps']:
    raise RuntimeError('Unexpected CI selection; stop and explain before building')
native = BASE / ('artifacts/command-native-' + PROVIDER + '-01')
run('native', [sys.executable, 'eng/task07_native.py', '--provider', PROVIDER, '--output', native])
run('bundle', [sys.executable, 'eng/ci/bundles.py', '--provider', PROVIDER, '--plan', 'artifacts/plan.json',
               '--version', '0.1.0-ci.1', '--native', native / 'manifest.json'], build_dotnet=True)
run('public-validate', [sys.executable, 'eng/ci/validate_public.py', 'artifacts/public',
                       'artifacts/plan.json', '0.1.0-ci.1', '--module', PROVIDER])
package = BASE / 'artifacts/command-packages-01' / PROVIDER
shutil.copytree(SOURCE / 'artifacts/public', package)
for kind, suffix in (('query-phases', 'phases'), ('workload', 'workload')):
    run('consumer-' + suffix, [sys.executable, 'benchmarks/db-perf/managed/build.py', '--provider', PROVIDER,
        '--feed', package / 'feed', '--version', '0.1.0-ci.1', '--kind', kind,
        '--output', BASE / ('consumers/command-' + PROVIDER + '-' + suffix + '-01')], build_dotnet=True)
print(json.dumps({'provider': PROVIDER, 'receipt': str(RECEIPT), 'sha256': sha(RECEIPT)}), flush=True)
