#!/usr/bin/env python3
"""Task-local correctness only; retain all failures and stop all three servers."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import socket
import subprocess
import time
from urllib.parse import urlsplit, urlunsplit

BASE = Path('/workspace/scratch/17ac3f8f2fbf/worktrees/DB-Exec-02-retirement-fence')
BUILD = BASE / 'artifacts/cmake/linux-x64-release'
OUT = BASE / 'artifacts/retirement-fence-4c6f188-pg'
PG = Path('/workspace/scratch/17ac3f8f2fbf/tools/postgres-tools/install/bin')
OUT.mkdir(exist_ok=False)
env = {key: value for key, value in os.environ.items() if not key.startswith('PG')}
records, servers = [], []

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(label, args, extra=None, timeout=180):
    args = [str(arg) for arg in args]
    log = OUT / (label + '.log')
    started = time.monotonic()
    with log.open('w') as stream:
        result = subprocess.run(args, cwd=BASE, env=env | (extra or {}), stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)
    record = {'label': label, 'args': args, 'exit': result.returncode, 'seconds': time.monotonic() - started,
              'binarySha256': sha(args[0]), 'logSha256': sha(log)}
    records.append(record)
    (OUT / 'commands.json').write_text(json.dumps(records, indent=2) + '\n')
    print(label, result.returncode, flush=True)
    if result.returncode:
        raise RuntimeError(label + ' failed; original log retained')

spec = importlib.util.spec_from_file_location('fence_pg_certificates', BASE / 'tests/Data.Postgres/verify.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)
paths = ['native/cpp/include/nw/host.hpp', 'native/cpp/src/host.cpp', 'native/cpp/tests/transaction_tests.cpp',
         'native/cpp/tests/fixtures/sqlite.cpp', 'native/cpp/src/provider.cpp', 'native/cpp/tests/postgres_sync_tests.cpp']
manifest = {'sourceCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=BASE, text=True).strip(),
            'gitStatus': subprocess.check_output(['git', 'status', '--short'], cwd=BASE, text=True),
            'correctnessOnly': True, 'sourceSha256': {path: sha(BASE / path) for path in paths},
            'fixtureSha256': sha(BUILD / 'fixtures/libkorda_postgres_fixture.so'),
            'postgresSha256': sha(PG / 'postgres'), 'startedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
status = 'failed'
try:
    certs = OUT / 'certificates'
    (OUT / 'certificates.json').write_text(json.dumps(verify.certificates(certs), indent=2) + '\n')
    urls = {}
    for name, tls in [('valid', True), ('expired', True), ('plain', False)]:
        data = OUT / ('pg-' + name)
        run('init-' + name, [PG / 'initdb', '-D', data, '-U', 'korda', '--auth=trust', '--no-locale', '--encoding=UTF8'])
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        with (data / 'postgresql.conf').open('a') as conf:
            conf.write('\nfsync=on\nssl=' + ('on' if tls else 'off') + '\n')
            if tls:
                conf.write(f"ssl_cert_file='{certs / name}.pem'\nssl_key_file='{certs / name}.key'\n")
        logfile = (OUT / ('server-' + name + '.log')).open('w')
        process = subprocess.Popen([str(PG / 'postgres'), '-D', str(data), '-h', '127.0.0.1', '-p', str(port), '-k', ''],
                                   env=env, stdout=logfile, stderr=subprocess.STDOUT)
        servers.append((process, data, logfile))
        for _ in range(200):
            if process.poll() is not None:
                raise RuntimeError(name + ' server exited during startup')
            if subprocess.run([str(PG / 'pg_isready'), '-h', '127.0.0.1', '-p', str(port)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                break
            time.sleep(.05)
        else:
            raise RuntimeError(name + ' server startup timeout')
        urls[name] = f'postgresql://korda@localhost:{port}/postgres'
    (OUT / 'topology.json').write_text(json.dumps(urls, indent=2) + '\n')
    native_env = {'NW_PG_URL': urls['valid'], 'NW_PG_EXPIRED_URL': urls['expired'], 'NW_PG_PLAIN_URL': urls['plain'],
                  'NW_PG_ROOT': str(certs / 'root.pem'), 'NW_PG_UNTRUSTED_ROOT': str(certs / 'untrusted.pem')}
    run('provider', [BUILD / 'tests/nw_provider_tests'], native_env)
    run('postgres-fixture', [BUILD / 'tests/nw_postgres_fixture_tests'], native_env | {'NW_PG_REPORT': str(OUT / 'postgres-report.json')})
    run('create-sync-database', [PG / 'createdb', '--maintenance-db', urls['plain'], 'retirement_fence_sync'])
    parts = urlsplit(urls['plain'])
    sync_url = urlunsplit((parts.scheme, parts.netloc, '/retirement_fence_sync', parts.query, parts.fragment))
    run('postgres-sync', [BUILD / 'tests/nw_postgres_sync_tests', sync_url])
    for path, expected in manifest['sourceSha256'].items():
        if sha(BASE / path) != expected:
            raise RuntimeError('source changed during validation: ' + path)
    status = 'passed'
except Exception as error:
    (OUT / 'failure.txt').write_text(str(error) + '\n')
    print(str(error), flush=True)
finally:
    stopped = []
    for process, data, logfile in reversed(servers):
        stop = subprocess.run([str(PG / 'pg_ctl'), '-D', str(data), 'stop', '-m', 'fast'], env=env,
                              stdout=logfile, stderr=subprocess.STDOUT)
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        stopped.append({'data': str(data), 'pid': process.pid, 'pgCtlExit': stop.returncode, 'serverExit': process.returncode})
        logfile.close()
    (OUT / 'summary.json').write_text(json.dumps({'status': status, 'sourceCommit': manifest['sourceCommit'],
        'correctnessOnly': True, 'allServersStopped': all(s['serverExit'] is not None for s in stopped),
        'stopped': stopped, 'commands': len(records), 'finishedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat()}, indent=2) + '\n')
print(status, flush=True)
raise SystemExit(0 if status == 'passed' else 1)
