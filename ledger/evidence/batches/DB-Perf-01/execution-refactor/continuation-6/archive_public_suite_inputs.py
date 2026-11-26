#!/usr/bin/env python3
"""Lossless evidence assembly only; never builds or executes a consumer."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile

BASE = Path('/workspace/scratch/4a65d70f0fe1')
KORDA = BASE / 'worktrees/DB-Exec-02-continuation'
OUT = Path(__file__).resolve().parent
PREFIX = 'public-suite-and-matched-inputs-01'
items: dict[str, bytes] = {}
origins: dict[str, str] = {}
checks = []


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def add(path: Path, name: str, expected: str | None = None) -> None:
    value = path.read_bytes()
    if expected is not None:
        assert sha(value) == expected, path
    if name in items:
        assert items[name] == value, name
    items[name] = value
    origins[name] = str(path)


def put(name: str, record: object) -> None:
    items[name] = (json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode()
    origins[name] = 'assembled observation; original receipts remain unchanged'


def git(*args: str) -> bytes:
    return subprocess.check_output(['git', *args], cwd=KORDA)


for number in (1, 2, 3):
    folder = BASE / 'validation-evidence' / f'command-public-suites-{number:02d}'
    record = json.loads((folder / 'result.json').read_text())
    prefix = f'public-suites/{folder.name}/'
    add(folder / 'result.json', prefix + 'result.json')
    add(Path(record['sourceFiles']), prefix + 'source-files.json', record['sourceFilesSha256'])
    add(Path(record['script']), prefix + 'run.py', record['scriptSha256'])
    if (folder / 'asset-pairing.json').is_file():
        add(folder / 'asset-pairing.json', prefix + 'asset-pairing.json')
    for suite in record['suites']:
        for item in suite['records']:
            # The recorded list contains logs, JSON receipts and asset identity
            # JSON, not ELF/native/cluster contents.
            assert Path(item['path']).suffix in {'.log', '.json'}, item
            add(folder / item['path'], prefix + item['path'], item['sha256'])
        executable = suite['executable']
        path = Path(executable['path'])
        assert sha(path.read_bytes()) == executable['sha256'], path
    # Record-source files include all product/test inputs; compare original git
    # blobs in one batch without rebuilding or substituting a newer source.
    source_files = json.loads(Path(record['sourceFiles']).read_text())
    requests = ''.join(record['sourceCommit'] + ':' + entry['path'] + '\n' for entry in source_files).encode()
    raw = subprocess.check_output(['git', 'cat-file', '--batch'], input=requests, cwd=KORDA)
    stream = io.BytesIO(raw)
    for entry in source_files:
        header = stream.readline().decode().split(); assert len(header) == 3 and header[1] == 'blob'
        value = stream.read(int(header[2])); assert stream.read(1) == b'\n'
        assert sha(value) == entry['sha256'], (record['sourceCommit'], entry['path'])
    checks.append({'group': folder.name, 'source': record['sourceCommit'], 'sourceFilesChecked': len(source_files),
                   'sourceFilesMatchCommit': True, 'recordedFilesAndExecutablesRehashed': True,
                   'passed': record['passed'], 'suites': [{'suite': x['suite'], 'exitCode': x['exitCode']} for x in record['suites']],
                   'publicPackageCredit': False, 'performanceCredit': False})

profiles = BASE / 'validation-evidence/command-public-suites-03/generated-provider-profiles'
profile_record = json.loads((profiles / 'result.json').read_text())
add(profiles / 'result.json', 'public-suites/generated-provider-profiles/result.json')
for item in profile_record['profiles']:
    add(Path(item['copy']), 'public-suites/generated-provider-profiles/' + Path(item['copy']).name, item['sha256'])

final_suite_source = '8736d93da65f1d7ae19508afb28f68de224e19de'
paths = git('ls-tree', '-r', '--name-only', final_suite_source, '--', 'tests/Query.Fluent', 'tests/Orm.Relations',
            'tests/ProviderProfileChecks.cs', 'tests/Data.NativeHost/run.py', 'eng/database_regressions.py',
            'eng/build.py', 'Directory.Build.props', 'Directory.Build.targets', 'Directory.Packages.props',
            'global.json', 'NuGet.Config').decode().splitlines()
for path in paths:
    name = 'public-suites/final-source/' + path
    items[name] = git('show', final_suite_source + ':' + path)
    origins[name] = 'git:' + final_suite_source + ':' + path

aggregate = BASE / 'artifacts/dapper-matched-builds-01.json'
add(aggregate, 'dapper/dapper-matched-builds-01.json')
builds = json.loads(aggregate.read_text())
add(BASE / 'artifacts/build-dapper-matched-01.py', 'dapper/run-builds.py', builds['scriptSha256'])
for build in builds['results']:
    provider = build['provider']; folder = Path(build['receipt']).parent
    prefix = f'dapper/{folder.name}/'
    receipt = json.loads(Path(build['receipt']).read_text())
    add(Path(build['receipt']), prefix + 'build-receipt.json', build['receiptSha256'])
    add(Path(build['log']), prefix + 'outer-build.log', build['logSha256'])
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix in {'.cs', '.csproj', '.json', '.props', '.targets', '.Config', '.log'}:
            add(path, prefix + path.name)
    for path, expected in receipt['sources'].items():
        assert sha((folder / path).read_bytes()) == expected, (provider, path)
    assert sha((folder / 'DbPerf.Dapper.csproj').read_bytes()) == receipt['projectSha256']
    assert sha((folder / 'project.assets.json').read_bytes()) == receipt['assetsSha256']
    assert sha((folder / 'publish.log').read_bytes()) == receipt['logSha256']
    for key in ('sqlContract', 'generatedSqlContract'):
        file = receipt[key]; assert sha((folder / file['path']).read_bytes()) == file['sha256']
    generated = json.loads((folder / receipt['generatedSqlContract']['path']).read_text())
    add(folder / generated['generatedFile'], prefix + generated['generatedFile'], generated['generatedSha256'])
    assert generated['generatedFactoriesVerified'] is True and generated['runtimeSqlTraceVerified'] is False
    assert len(generated['calls']) == 12
    executable = folder / 'out/DbPerf.Dapper'
    assert sha(executable.read_bytes()) == receipt['executableSha256'], executable
    checks.append({'group': folder.name, 'source': builds['sourceCommit'], 'publishExitCode': receipt['exitCode'],
                   'generatedCalls': len(generated['calls']), 'generatedSourceSha256': generated['generatedSha256'],
                   'sourceFilesAndAssetsGraphRehashed': True, 'executableSha256': receipt['executableSha256'],
                   'runtimeSqlTraceVerified': False, 'consumerExecutedByThisEvidence': False, 'performanceCredit': False})

static = BASE / 'artifacts/dapper-sql-matched-static-01'
static_record = json.loads((static / 'result.json').read_text())
for path in sorted(static.iterdir()):
    if path.is_file(): add(path, 'dapper/static/' + path.name)
assert len(static_record['checks']) == 17
for path, expected in static_record['protectedInputs'].items():
    original = Path(path)
    relative = original.relative_to(BASE)
    add(original, 'dapper/historical-control-inputs/' + str(relative), expected)
for provider in ('sqlite', 'postgresql'):
    folder = BASE / 'consumers' / f'dapper-{provider}-workload'
    for path in sorted((folder / 'generated').rglob('*.cs')):
        add(path, 'dapper/historical-control-inputs/consumers/' + folder.name + '/' + str(path.relative_to(folder)))

for path in ('benchmarks/db-perf/managed/build_orm.py',
             'benchmarks/db-perf/workload/check_dapper_contract.py',
             'benchmarks/db-perf/workload/lifecycle-sql-matched-v1.json',
             'benchmarks/db-perf/workload/lifecycle-sql-matched-v1.md',
             'benchmarks/db-perf/workload/queries-v3.json'):
    name = 'dapper/tool-source/' + path
    items[name] = git('show', builds['sourceCommit'] + ':' + path)
    origins[name] = 'git:' + builds['sourceCommit'] + ':' + path

for leaf in ('one-shot-publication-intent-01.json', 'one-shot-publication-receipt-01.json', 'one-shot-publication-payload-01.json'):
    add(BASE / 'artifacts' / leaf, 'publication/' + leaf)
for path in sorted((BASE / 'artifacts/command-managed').iterdir()):
    if path.is_file() and path.suffix in {'.json', '.log', '.c'}:
        add(path, 'managed-development/' + path.name)

put('verification.json', {'groups': checks, 'staticSqlChecks': 17, 'noConsumersExecutedDuringAssembly': True,
                         'noBuildDuringAssembly': True, 'noPerformanceCredit': True})
items['assemble.py'] = Path(__file__).read_bytes(); origins['assemble.py'] = str(Path(__file__))
readme = '''# Public API development suites and matched Dapper inputs

This archive preserves original Query.Fluent / Orm.Relations development AOT attempts01–03, including every recorded failure and the final pass. Attempt01 used native9605507 and failed public query sealing because capability bit28 was rejected. Attempt02 used corrected374a253 assets: Query.Fluent passed; Orm.Relations stopped at an obsolete positive generic-retirement assertion. Attempt03 at8736d93 preserves ResourceLimit and zero-SQL checks while observing the real direct command; both suites and all seven compile-negative cases passed. These source/project consumers are not final public NuGet package evidence. The original receipt includes exact commands, source/native identity, actual ELF hash and unchanged-input checks. Actual generated provider identity files were copied after the successful publish as a separately labeled supplement.

The Dapper section preserves both newly built matched SQL Native AOT consumer source sets, projects, asset graphs, package hashes, publish logs, and actual emitted interceptor/command/row factories. Each provider's actual generated contract validates twelve lifecycle call sites, including Int64 tenant/id/take=2 for Find. Seventeen static checks and historical negative-control inputs remain separate. The raw generated C# is included, not merely its hash. No runtime SQL trace, workload execution, timing or allocation credit is granted by these builds. The unchanged historical consumers remain separately identified; their old generated factories cannot be credited as matched SQL.

Public source8789a45 has the same tree as integrated locald8beff6. Its publication request/receipt are retained as source identity, not execution evidence. The managed compile/format/ABI failures and successful later stages are retained as development-only logs. The stopped empty-log compile and initial formatting failure have not been erased.

Assembly only reads existing evidence and git blobs. It checks the original recorded file hashes, source hashes against each recorded commit, generated-source hashes, asset graphs and retained executable hashes. It creates deterministic gzip twice, checks byte identity, extracts and verifies every member. No ELF/so, bin/obj, restore cache, database data or private certificate is included; paths and hashes permit separate recovery. The archive's original scripts still contain the original absolute workspace paths. Reproduction requires the pinned repositories/toolchain or equivalent path remapping; do not bypass asset identity checks.
'''
items['README.md'] = readme.encode(); origins['README.md'] = 'assembled scope explanation'
items['SHA256SUMS'] = ''.join(f'{sha(value)}  {name}\n' for name, value in sorted(items.items())).encode()
origins['SHA256SUMS'] = 'generated hashes of every other member'


def pack() -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode='wb', filename='', mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode='w', format=tarfile.PAX_FORMAT) as tar:
            for name, value in sorted(items.items()):
                member = tarfile.TarInfo(name); member.size = len(value)
                member.mode = 0o644; member.mtime = member.uid = member.gid = 0
                member.uname = member.gname = ''
                tar.addfile(member, io.BytesIO(value))
    return output.getvalue()


first = pack(); assert first == pack()
archive = OUT / (PREFIX + '.tar.gz'); archive.write_bytes(first)
with tempfile.TemporaryDirectory(prefix='command-inputs-verify-', dir=BASE / 'artifacts') as temp:
    with tarfile.open(archive, 'r:gz') as tar:
        assert set(tar.getnames()) == set(items)
        assert all(member.isfile() and member.mtime == member.uid == member.gid == 0 for member in tar.getmembers())
        tar.extractall(temp, filter='data')
    for name, value in items.items():
        assert (Path(temp) / name).read_bytes() == value, name
manifest = {'schemaVersion': 1, 'archive': archive.name, 'bytes': len(first), 'sha256': sha(first),
            'members': len(items), 'twoEncodingsByteIdentical': True, 'allExtractedBytesVerified': True,
            'groups': checks, 'performanceCredit': False,
            'files': [{'path': name, 'bytes': len(value), 'sha256': sha(value), 'origin': origins[name]}
                      for name, value in sorted(items.items())]}
(OUT / (PREFIX + '.manifest.json')).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
(OUT / (PREFIX + '.README.md')).write_text(readme)
print(json.dumps({key: manifest[key] for key in manifest if key not in {'files', 'groups'}}, indent=2))
