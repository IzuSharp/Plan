#!/usr/bin/env python3
"""Finite correctness only: 35 cases plus 64 warmup operations, never offered load.

Run only when the campaign owner grants exclusive ownership of the shared PG
instance. A failed start never authorizes this helper to stop another instance.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_json(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--task-root', type=Path, required=True)
p.add_argument('--output', type=Path, required=True, help='New finite-correctness directory')
args = p.parse_args()
task = args.task_root.resolve()
project = Path(__file__).resolve().parent
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=False)
java = task / 'toolchains/java'
database = task / 'toolchains/native-db'
binary = project / 'target/runtime-comparison-java'
identity = json.loads((project / 'build-identity.json').read_text())
assert identity['nativeImage'] is True
assert digest(binary) == identity['executableSha256'], 'Native executable differs from build identity'
for name, expected in identity['sourceHashes'].items():
    assert digest(project / name) == expected, 'Source changed since build: ' + name
provenance = json.loads((project / 'source-provenance.json').read_text())
receipt = {'isPressureTest': False, 'startedUtc': utc(), 'status': 'running',
           'nativeExecutableSha256': identity['executableSha256'],
           'buildIdentitySha256': digest(project / 'build-identity.json'),
           'commandScriptSha256': digest(Path(__file__)), 'commands': [],
           'timingComparisonEligible': False, 'postgresServerStopped': None}


def command(label, argv, *, check=True):
    start = utc()
    result = subprocess.run(argv, text=True, capture_output=True, timeout=180)
    with (output / (label + '.txt')).open('x') as log:
        log.write(result.stdout)
        if result.stderr:
            log.write('\nSTDERR\n' + result.stderr)
    receipt['commands'].append({'label': label, 'command': argv, 'startedUtc': start,
        'finishedUtc': utc(), 'exitCode': result.returncode,
        'outputSha256': digest(output / (label + '.txt'))})
    if check and result.returncode:
        raise RuntimeError(f'{label} failed with exit {result.returncode}; see its retained output')
    return result


def validate(path, provider):
    value = json.loads(path.read_text())
    assert value['Provider'] == provider
    assert value['NativeAot'] is True
    assert value['VerificationOnly'] is True
    assert value['VerifiedCasesPerWorker'] == 35
    assert value['WarmupPerWorker'] == 64
    assert value['Concurrency'] == 1
    assert value['OracleFailures'] == 0
    assert value['TimingComparisonEligible'] is False
    assert value['ExecutableSha256'] == identity['executableSha256']
    assert value['ContractSha256'] == provenance['contractSha256']
    assert len(value['ExpectedResults']) == 35
    receipt[provider] = {'status': 'passed', 'receiptSha256': digest(path),
        'verifiedCases': 35, 'warmupOperations': 64, 'oracleFailures': 0}


started_pg = False
setup = json.loads((database / 'fixtures/postgresql-setup-receipt.json').read_text())
pg = database / 'postgres/bin'
try:
    private_sqlite = output / 'sqlite-native.sqlite'
    shutil.copyfile(database / 'fixtures/seed.sqlite', private_sqlite)
    receipt['sqliteSeedCopySha256'] = digest(private_sqlite)
    common = ['--case', 'mixed', '--mode', 'prepared', '--session', 'persistent',
              '--concurrency', '1', '--warmup', '64', '--verify-only', '--idle-seconds', '0']
    sqlite_output = output / 'sqlite-native.json'
    command('sqlite-native', [str(binary), '--provider', 'sqlite', '--connection', str(private_sqlite),
        '--sqlite-jni-directory', str(java / 'sqlite-jni'), '--sqlite-native-library',
        str(database / 'sqlite/lib/libsqlite3.so'), *common, '--output', str(sqlite_output)])
    validate(sqlite_output, 'sqlite')

    command('postgres-start', setup['startCommand'])
    started_pg = True
    admin = [str(pg / 'psql'), '--no-psqlrc', '--set', 'ON_ERROR_STOP=1', '--tuples-only',
             '--no-align', '--dbname', 'postgresql://korda@127.0.0.1:48277/postgres', '--command']
    exists = command('postgres-check-private-database', admin + [
        "SELECT count(*) FROM pg_database WHERE datname='db_perf_java_preflight'"]).stdout.strip()
    if exists == '0':
        command('postgres-create-private-database', admin + [
            'CREATE DATABASE db_perf_java_preflight TEMPLATE db_perf_01'])
    elif exists == '1':
        previous = json.loads((java / 'verification/postgresql-jit-lifecycle.json').read_text())
        assert any(x['label'] == 'create-private-template' and x['exitCode'] == 0
                   for x in previous['commands']), 'Existing database lacks this task ownership receipt'
    else:
        raise RuntimeError('Unexpected database existence result')
    pg_output = output / 'postgresql-native.json'
    command('postgresql-native', [str(binary), '--provider', 'postgresql', '--connection',
        'jdbc:postgresql://127.0.0.1:48277/db_perf_java_preflight?user=korda&sslmode=disable',
        *common, '--output', str(pg_output)])
    validate(pg_output, 'postgresql')
    receipt['status'] = 'passed'
except BaseException as error:
    receipt['status'] = 'failed'
    receipt['error'] = repr(error)
    raise
finally:
    if started_pg:
        stopped = command('postgres-stop', [str(pg / 'pg_ctl'), '-D', setup['data'], '-m',
            'fast', '-w', '-t', '30', 'stop'], check=False)
        receipt['postgresServerStopped'] = stopped.returncode == 0
        if stopped.returncode:
            receipt['status'] = 'failed'
    receipt['finishedUtc'] = utc()
    create_json(output / 'verification-lifecycle.json', receipt)
if receipt['status'] != 'passed':
    raise SystemExit('Finite correctness did not pass; inspect verification-lifecycle.json')
print(json.dumps({k: v for k, v in receipt.items() if k != 'commands'}, indent=2))
