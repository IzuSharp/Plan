#!/usr/bin/env python3
"""Record existing PostgreSQL correctness gates for one clean native candidate."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

output = Path(__file__).resolve().parent
root = output.parent.parent
native = root / 'artifacts/cmake/linux-x64-release'
pg = Path(os.environ['NW_POSTGRES_BIN']).resolve()
design = Path('/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-02-frozen-design')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def git(*arguments):
    return subprocess.check_output(['git', *arguments], cwd=root, text=True).strip()

candidate = git('rev-parse', 'HEAD')
if candidate != 'a781e51d23c2e858605fd9f4592c90ddc29129ed' or git('status', '--short'):
    raise RuntimeError('This receipt requires clean native candidate a781e51.')
names = subprocess.check_output(['git', 'ls-files', '-z', '--',
    'native/cpp', 'native/database', 'native/interop', 'native/dependencies.lock.json',
    'CMakeLists.txt', 'CMakePresets.json', 'cmake', 'eng/cpp_toolchain.py',
    'tests/Data.NativeHost/run.py', 'tests/Data.Postgres/verify.py',
    'src/Data.Postgres/design-inputs.json'], cwd=root).decode().split('\0')
inputs = [{'path': name, 'sha256': sha(root / name)} for name in names if name]
binaries = [native / 'tests/nw_postgres_sync_tests', native / 'tests/nw_postgres_fixture_tests',
    native / 'fixtures/libkorda_postgres_fixture.so', native / 'fixtures/libkorda_data_postgres.so',
    native / 'tests/nw_provider_tests', pg / 'postgres', pg.parent / 'lib/libpq.a']
manifest = {
    'task': 'DB-Exec-02', 'scope': 'native-candidate-postgresql-correctness',
    'candidate': candidate, 'source_status': git('status', '--short'),
    'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'design_commit': subprocess.check_output(['git', '-C', str(design), 'rev-parse', 'HEAD'], text=True).strip(),
    'source_inputs': inputs, 'native_artifacts': [{'path': str(path), 'sha256': sha(path)} for path in binaries],
    'postgres_version': subprocess.check_output([str(pg / 'postgres'), '--version'], text=True).strip(),
    'compiler_provenance': (native / 'compiler-provenance.txt').read_text(),
    'environment_setup': '/workspace/scratch/4a65d70f0fe1/tools/task-env.sh',
    'environment_setup_sha256': sha('/workspace/scratch/4a65d70f0fe1/tools/task-env.sh'),
    'driver_sha256': sha(__file__), 'performance_work': False,
    'independent_package_acceptance': False,
}
(output / 'source-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
commands = [
    ('protocol', [sys.executable, str(root / 'tests/Data.NativeHost/run.py'), '--postgres-bin', str(pg),
        '--output', str(output / 'protocol'), '--', sys.executable, '-c',
        'import os,sys; os.execv(sys.argv[1], [sys.argv[1], os.environ["NW_TEST_POSTGRES"]])',
        str(native / 'tests/nw_postgres_sync_tests')]),
    ('fixture', [sys.executable, str(root / 'tests/Data.Postgres/verify.py'), '--native-only',
        '--postgres-bin', str(pg), '--native-build', str(native), '--design-root', str(design),
        '--output', str(output / 'fixture')]),
    ('provider', [sys.executable, str(root / 'native/cpp/tests/provider_verify.py'),
        '--binary', str(native / 'tests/nw_provider_tests'), '--postgres-bin', str(pg),
        '--output', str(output / 'provider')]),
]
records = []
for label, command in commands:
    began = time.monotonic()
    log = output / (label + '-driver.log')
    print('START ' + label, flush=True)
    with log.open('w') as stream:
        result = subprocess.run(command, cwd=root, env=os.environ.copy(), stdout=stream,
            stderr=subprocess.STDOUT, timeout=600)
    records.append({'name': label, 'command': command, 'exit_code': result.returncode,
        'seconds': round(time.monotonic() - began, 3), 'log': str(log.relative_to(output)), 'sha256': sha(log)})
    (output / 'commands.json').write_text(json.dumps(records, indent=2) + '\n')
    print(label + ' exit=' + str(result.returncode), flush=True)

stable = candidate == git('rev-parse', 'HEAD') and git('status', '--short') == ''
stable = stable and all(sha(root / item['path']) == item['sha256'] for item in inputs)
stable = stable and all(sha(item['path']) == item['sha256'] for item in manifest['native_artifacts'])
summary = {'status': 'passed' if stable and all(item['exit_code'] == 0 for item in records) else 'failed',
    'candidate': candidate, 'source_and_artifacts_unchanged': stable,
    'manifest_sha256': sha(output / 'source-manifest.json'), 'commands': records,
    'performance_work': False, 'independent_package_acceptance': False}
(output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({key: summary[key] for key in ('status', 'candidate', 'source_and_artifacts_unchanged')}), flush=True)
raise SystemExit(0 if summary['status'] == 'passed' else 1)
