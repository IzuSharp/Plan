#!/usr/bin/env python3
"""Preserve the nine completed groups and their original source/input identities.

This reads immutable records, verifies hashes, and creates one deterministic
archive. It never executes a consumer, database, build, benchmark or CI job.
"""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import zipfile


GROUPS = ('single-row-matched-sqlite-01', 'single-command-sqlite-01',
          'single-row-matched-postgresql-01', 'single-command-postgresql-01',
          'single-commit-proof-postgresql-01', 'ffi-single-command-sqlite-01',
          'ffi-single-command-postgresql-01', 'phases-command-sqlite-01',
          'phases-command-postgresql-01')
TEXT = {'.json', '.jsonl', '.log', '.txt', '.cs', '.py', '.c', '.h', '.hpp', '.cpp',
        '.md', '.xml', '.nuspec', '.csproj', '.props', '.targets', '.config', '.patch', '.sh', '.in'}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--korda', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, evidence, output = args.root.resolve(), args.evidence.resolve(), args.output.resolve()
    manifest_path = output.with_name(output.name.removesuffix('.tar.gz') + '.manifest.json')
    need(output.name.endswith('.tar.gz') and not output.exists() and not manifest_path.exists(), 'Fresh archive required')
    payload, entries, checked, excluded, package_sources = {}, {}, {}, {}, {}

    def add_bytes(name, value, provenance):
        need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'Unsafe member name')
        need(name not in payload or payload[name] == value, 'Archive name collision')
        payload[name] = value
        entries[name] = {'path': name, 'sha256': sha(value), 'bytes': len(value), **provenance}

    def default_name(path):
        if path.is_relative_to(root):
            return 'original/' + str(path.relative_to(root))
        if path.is_relative_to(evidence):
            return 'recovery/' + str(path.relative_to(evidence))
        return 'external/' + sha(str(path).encode())[:12] + '/' + path.name

    def add(path, expected=None, name=None):
        path = Path(path).resolve(strict=True)
        value = path.read_bytes()
        digest = sha(value)
        need(expected is None or digest == expected, 'Changed bound input: ' + str(path))
        checked[str(path)] = digest
        if value.startswith(b'\x7fELF') or path.suffix.lower() not in TEXT:
            excluded[str(path)] = {'sha256': digest, 'bytes': len(value), 'reason': 'Bound binary/tool/package; original bytes are not embedded'}
            if path.suffix.lower() == '.nupkg':
                with zipfile.ZipFile(io.BytesIO(value)) as archive:
                    for item in archive.namelist():
                        if item.endswith('.nuspec') or item in ('korda/public.json', 'korda/database-assets.json'):
                            add_bytes('package-metadata/' + digest + '/' + item, archive.read(item), {'packagePath': str(path), 'packageSha256': digest})
            return
        add_bytes(name or default_name(path), value, {'sourcePath': str(path)})

    def bind(value):
        if isinstance(value, dict):
            if isinstance(value.get('path'), str) and 'sha256' in value:
                path = Path(value['path'])
                if path.is_absolute():
                    add(path, value['sha256'])
            for child in value.values():
                bind(child)
        elif isinstance(value, list):
            for child in value:
                bind(child)

    series_path = root / 'artifacts/command-short-series-01.json'
    series = json.loads(series_path.read_text())
    need(tuple(x['name'] for x in series) == GROUPS, 'Unexpected/missing/reordered recovered groups')
    add(series_path)
    for name in ('command-short-plans-01.json', 'command-short-host-before-01.json',
                 'run-command-short-series-01.py', 'prepare-command-short-series-01.py',
                 'analyze-command-single-review-01.json', 'analyze-command-single-review-02.json'):
        add(root / 'artifacts' / name)
    consumers = set()
    commands = []
    previous_end = None
    for run in series:
        need(run['exitCode'] == 0, 'Failed outer group')
        folder = root / 'measurements' / run['name']
        plan_path = folder / 'plan.json'
        add(plan_path, run['planSha256'])
        add(run['command'][-3], run['planSha256'])
        add(run['log'], run['logSha256'])
        plan = json.loads(plan_path.read_text())
        need(run['command'] == plan['runnerCommand'] and run['command'][-2:] == ['--output', str(folder)], 'Outer argv differs')
        bind(plan['inputs'])
        for consumer in plan['inputs']['consumers'].values():
            path = consumer.get('executable', consumer)
            consumers.add(Path(path['path']).parent.parent)
        for item in plan['commands']:
            receipt = json.loads((folder / (item['name'] + '.command.json')).read_text())
            need(receipt['success'] is True and receipt['exitCode'] == 0 and receipt['timedOut'] is False
                 and receipt['observerErrors'] == [], 'Failed command/observer')
            start, end = receipt['startedMonotonicNs'], receipt['finishedMonotonicNs']
            need(start < end and (previous_end is None or start >= previous_end), 'Groups/commands overlap or reorder')
            previous_end = end
            for name, digest in receipt['files'].items():
                add(folder / name, digest)
            commands.append({'group': run['name'], 'name': item['name'], 'phase': item['phase'],
                             'exitCode': receipt['exitCode'], 'startedMonotonicNs': start, 'finishedMonotonicNs': end})
        # Only top-level observation files; no database or restore-cache walk.
        for path in sorted(folder.iterdir()):
            if path.is_file() and path.suffix in {'.json', '.jsonl', '.log', '.txt'}:
                add(path)
    need(len(commands) == 63 and sum(x['phase'] == 'fixture' for x in commands) == 9, 'Command/fixture count differs')

    for folder in sorted(consumers):
        receipt_path = folder / ('diagnostic-build.json' if (folder / 'diagnostic-build.json').exists() else 'build-receipt.json')
        add(receipt_path)
        receipt = json.loads(receipt_path.read_text())
        for path in sorted(folder.iterdir()):
            if path.is_file() and path.suffix.lower() in TEXT:
                add(path)
        for path in sorted((folder / 'generated').rglob('*.cs')):
            add(path)
        for name, digest in receipt.get('sources', {}).items():
            add(folder / name, digest)
        for name, digest in receipt.get('native_images', {}).items():
            add(folder / 'out' / name, digest)
        for path in (folder / 'out').glob('*'):
            if path.is_file() and path.suffix in ('.json',):
                add(path)
        if receipt.get('package'):
            package, version = receipt['package'].lower(), receipt['version'].lower()
            add(folder / 'packages' / package / version / (package + '.' + version + '.nupkg'), receipt['package_sha256'])
        if receipt.get('executable_sha256'):
            stem = 'DbPerf.QueryPhases' if receipt.get('kind') == 'query-phases' else 'DbPerf.Korda'
            add(folder / 'out' / stem, receipt['executable_sha256'])
        elif receipt.get('executableSha256'):
            stem = 'DbPerf.DapperQueryPhases' if 'phase' in receipt.get('kind', '').lower() else 'DbPerf.Dapper'
            add(folder / 'out' / stem, receipt['executableSha256'])
        bind(receipt.get('packages', {}))
        assets = folder / 'obj/project.assets.json'
        if assets.exists():
            add(assets)

    for name in ('command-paired-03.json', 'row-before-paired-02.json', 'pg-experiment-02.json', 'phases-01.json'):
        path = evidence / 'analysis' / name
        result = json.loads(path.read_text())
        inputs = result['inputFiles']
        pairs = inputs.items() if isinstance(inputs, dict) else ((x['path'], x) for x in inputs)
        for source, entry in pairs:
            if isinstance(entry, str):
                add(source, entry)
            elif isinstance(entry, dict):
                add(source, entry.get('storedSha256', entry.get('sha256')))
    for dirname in ('analysis', 'failed-analysis-01', 'failed-controls-01', 'tools', 'review'):
        for path in sorted((evidence / dirname).rglob('*')):
            if path.is_file() and path.suffix.lower() in TEXT:
                add(path)

    for kind in ('row-packages', 'command-packages-01', 'commit-proof-packages-01'):
        for path in sorted((root / 'artifacts' / kind).glob('*/release.json')):
            add(path)
            release = json.loads(path.read_text())
            package_sources[str(path)] = {k: release[k] for k in ('source_commit', 'source_tree', 'source_dirty')}
    for path in sorted((root / 'artifacts').glob('*commit-proof*.json')):
        add(path)
    for path in sorted((root / 'artifacts').glob('*commit-proof*.py')):
        add(path)
    for path in sorted((root / 'artifacts').glob('commit-proof*.log')):
        add(path)
    add(root / 'artifacts/commit-proof-native-product-01.patch')
    for rel in ('src/Data.NativeHost/DataSource.cs', 'src/Data.NativeHost/HostTransactionTransport.cs',
                'src/Data.Transactions/DataTransaction.cs'):
        commit = '8789a45a52cc0cc0a0b62737542d9c120b753c9b'
        value = subprocess.check_output(['git', '-C', str(args.korda), 'show', commit + ':' + rel])
        add_bytes('source-pins/' + commit + '/' + rel, value,
                  {'commit': commit, 'repository': 'IzuSharp/Korda', 'repositoryPath': rel})
    # Preserve local-only experimental source so its future branch retention is
    # not required to inspect the exact product delta or original tests.
    before = '8736d93da65f1d7ae19508afb28f68de224e19de'
    experiment = 'd2c137bf44eb0b8490c8c4f59f12f34d2df75ac2'
    patch = subprocess.check_output(['git', '-C', str(args.korda), 'diff', '--binary', before, experiment])
    add_bytes('source-pins/commit-proof-d2c137b.patch', patch,
              {'baseCommit': before, 'experimentCommit': experiment, 'repository': 'IzuSharp/Korda'})

    for path, expected in checked.items():
        need(sha(Path(path).read_bytes()) == expected, 'Input changed during archive: ' + path)
    manifest = {'schemaVersion': 1, 'scope': __doc__, 'groups': list(GROUPS),
                'commandCountIncludingFixtures': 63, 'fixtureCount': 9,
                'commands': commands, 'allRecordedCommandsSucceeded': True,
                'seriesCommandIntervalsNonoverlapping': True, 'finalLongCredit': '0/4',
                'packageSources': package_sources, 'files': sorted(entries.values(), key=lambda x: x['path']),
                'excludedBoundFiles': excluded, 'sourceHashChecks': checked,
                'exclusions': ['ELF/native images', 'NuGet/tool binaries', 'SQLite and PostgreSQL data', 'restore caches'],
                'reproductionLimit': 'Original binary/package bytes are hash-bound but not embedded. Recover those exact inputs or rebuild as a separately identified reproduction; do not relabel a different binary as this measurement.'}
    payload['manifest.json'] = (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode()
    payload['SHA256SUMS'] = ''.join(x['sha256'] + '  ' + x['path'] + '\n' for x in manifest['files']).encode()

    def encode():
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode='w', format=tarfile.PAX_FORMAT) as archive:
            for name, data in sorted(payload.items()):
                info = tarfile.TarInfo(name)
                info.size, info.mode = len(data), 0o644
                info.mtime = info.uid = info.gid = 0
                info.uname = info.gname = ''
                archive.addfile(info, io.BytesIO(data))
        return gzip.compress(output.getvalue(), compresslevel=9, mtime=0)

    encoded = encode()
    need(encoded == encode(), 'Archive bytes are not deterministic')
    with tarfile.open(fileobj=io.BytesIO(encoded), mode='r:gz') as archive:
        need(set(archive.getnames()) == set(payload), 'Archive members differ')
        for item in archive.getmembers():
            need(item.isfile() and archive.extractfile(item).read() == payload[item.name], 'Readback differs')
    with output.open('xb') as stream:
        stream.write(encoded)
    external = {'schemaVersion': 1, 'archive': {'path': output.name, 'sha256': sha(encoded), 'bytes': len(encoded)},
                'members': len(payload), 'deterministicDoubleEncodingEqual': True, 'allMembersReadbackEqual': True,
                'manifest': manifest}
    with manifest_path.open('x') as stream:
        json.dump(external, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'archive': str(output), 'sha256': sha(encoded), 'bytes': len(encoded), 'members': len(payload)}))


if __name__ == '__main__':
    main()
