#!/usr/bin/env python3
"""Real AOT support probe. No performance result is produced by this program."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PRIOR = Path('/workspace/scratch/82a414196324')
SDK = PRIOR / 'tooling/dotnet/dotnet'
NATIVE = PRIOR / 'Korda-DB-Rename-01-linux/artifacts'
CLANG = NATIVE / 'toolchain/llvm-23.1.5/bin/clang'
PG = NATIVE / 'postgres-tools/install/bin'
ENV = os.environ | {
    'PATH': str(CLANG.parent) + ':' + str(SDK.parent) + ':' + os.environ['PATH'],
    'DOTNET_ROOT': str(SDK.parent),
    'DOTNET_CLI_HOME': str(ROOT / 'dotnet-home'),
    'NUGET_PACKAGES': str(ROOT / 'cache'),
    'DOTNET_NOLOGO': 'true',
    'DOTNET_CLI_TELEMETRY_OPTOUT': '1',
    'DOTNET_SKIP_FIRST_TIME_EXPERIENCE': '1',
    'MSBUILDDISABLENODEREUSE': '1',
    'LD_LIBRARY_PATH': str(ROOT / 'native'),
}
RECORDS = []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(name, command, cwd=ROOT):
    command = list(map(str, command))
    start = datetime.datetime.now(datetime.UTC).isoformat()
    log = ROOT / 'logs' / (name + '.log')
    with log.open('wb') as output:
        result = subprocess.run(command, cwd=cwd, env=ENV, stdout=output, stderr=subprocess.STDOUT)
    RECORDS.append(dict(name=name, command=command, cwd=str(cwd), started_utc=start,
        finished_utc=datetime.datetime.now(datetime.UTC).isoformat(), exit_code=result.returncode,
        log=str(log.relative_to(ROOT)), log_sha256=digest(log)))
    (ROOT / 'evidence/commands.json').write_text(json.dumps(RECORDS, indent=2) + '\n')
    print(name + ' exit=' + str(result.returncode) + ' log=' + str(log), flush=True)
    if result.returncode:
        print(log.read_text(errors='replace')[-10000:], flush=True)
        raise RuntimeError(name + ' failed')


def main():
    (ROOT / 'native').mkdir(exist_ok=True)
    run('sdk-info', [SDK, '--info'])
    source = NATIVE / 'cmake/linux-x64-release/_deps/nw_sqlite-src/sqlite3.c'
    if not source.exists():
        candidates = list(NATIVE.glob('**/sqlite3.c'))
        source = next(x for x in candidates if digest(x) == '9512509b1bccb7461f79bea8aad6280ae4699e925fa4804381b71f59e7efb0c5')
    if digest(source) != '9512509b1bccb7461f79bea8aad6280ae4699e925fa4804381b71f59e7efb0c5':
        raise ValueError('SQLite source differs from Korda pinned input')
    run('sqlite-native-build', [CLANG, '-O3', '-DNDEBUG', '-DSQLITE_THREADSAFE=1', '-DSQLITE_ENABLE_COLUMN_METADATA',
        '-fPIC', '-shared', source, '-o', ROOT / 'native/libsqlite3.so', '-lm', '-ldl', '-lpthread'])
    for provider in ('sqlite', 'postgresql'):
        project = ROOT / provider
        run(provider + '-publish', [SDK, 'publish', 'OrmProbe.csproj', '-m:1', '-nr:false', '-p:UseSharedCompilation=false',
            '-c', 'Release', '-r', 'linux-x64', '-p:PublishAot=true', '-o', 'out'], project)
    run('sqlite-execute', [ROOT / 'sqlite/out/OrmProbe', ROOT / 'sqlite/probe.db'])
    run('postgres-initdb', [PG / 'initdb', '-D', ROOT / 'pgdata', '-U', 'korda', '-A', 'trust', '--no-locale'])
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    run('postgres-start', [PG / 'pg_ctl', '-D', ROOT / 'pgdata', '-l', ROOT / 'logs/postgres-server.log',
        '-o', f"-k '' -h 127.0.0.1 -p {port}", '-w', 'start'])
    try:
        run('postgresql-execute', [ROOT / 'postgresql/out/OrmProbe',
            f'Host=127.0.0.1;Port={port};Database=postgres;Username=korda;Pooling=false;SSL Mode=Disable'])
    finally:
        run('postgres-stop', [PG / 'pg_ctl', '-D', ROOT / 'pgdata', '-m', 'fast', '-w', 'stop'])
    receipt = {
        'purpose': 'Native AOT micro-ORM support only; no performance acceptance',
        'sdk': '11.0.100', 'orm': {'Dapper': '2.1.79', 'Dapper.AOT': '1.1.0'},
        'providers': {'postgresql': 'Npgsql 11.0.0', 'sqlite': 'Microsoft.Data.Sqlite.Core 11.0.0 / SQLitePCLRaw.provider.sqlite3 2.1.11'},
        'sqlite_source_sha256': digest(source), 'sqlite_library_sha256': digest(ROOT / 'native/libsqlite3.so'),
        'executables': {p: digest(ROOT / p / 'out/OrmProbe') for p in ('sqlite','postgresql')},
        'results': {p: (ROOT / 'logs' / (p + '-execute.log')).read_text() for p in ('sqlite','postgresql')},
        'source_files': {str(p.relative_to(ROOT)): digest(p) for p in ROOT.rglob('*') if p.is_file() and (p.suffix in ('.csproj',) or p.name in ('Program.cs','Directory.Build.props','global.json','NuGet.Config','run_probe.py')) and 'obj' not in p.parts},
        'command_count': len(RECORDS), 'status': 'passed',
    }
    (ROOT / 'evidence/result.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        (ROOT / 'evidence/failure.json').write_text(json.dumps({'status':'failed','error':repr(ex),'command_count':len(RECORDS)}, indent=2)+'\n')
        raise
