#!/usr/bin/env python3
"""Archive completed cb233 build failures without loading/building the product."""
from pathlib import Path
import datetime
import gzip
import hashlib
import io
import json
import re
import subprocess
import tarfile

ROOT = Path('/workspace/scratch/fd78534029f7')
REPO = ROOT / 'worktrees/DB-Exec-10-korda'
HERE = Path(__file__).resolve().parent
OLD_COMMIT = 'cb233a7a60dc9e9ef2110811d78db11b1c009438'
OLD_TREE = '0ea8d431f2d322dc9278e516da99d084413add7f'
NEW_COMMIT = '17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa'
NEW_TREE = 'bc9087d843d8d741d83d44f53d0b2c5af26dcffc'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    target = HERE / 'failed-candidate-cb233-01.tar.gz'
    manifest_path = HERE / 'failed-candidate-cb233-01.manifest.json'
    if target.exists() or manifest_path.exists():
        raise ValueError('Archive or manifest already exists; never overwrite evidence')
    inputs = {}
    facts = []
    signatures = json.loads((REPO / 'native/database/binding/signatures-v1.json').read_text())['signatures']
    for name in ['query-command-v1.json', 'cursor-pull-v1.json', 'command-completion-v1.json']:
        signatures += json.loads((REPO / 'native/database/binding' / name).read_text())['signatures']
    expected = {re.search(r'\b(nw_db_\w+_v1)\(', s).group(1) for s in signatures}
    expected |= {'nw_db_diagnostic_count_v1', 'nw_database_get_abi_v1'}
    for provider in ['sqlite', 'postgresql']:
        directory = ROOT / 'builds' / ('candidate-' + provider + '-01')
        receipt = json.loads((directory / 'build-receipt.json').read_text())
        native = json.loads((directory / 'native/manifest.json').read_text())
        for record in [receipt, native]:
            assert record['sourceCommit'] == OLD_COMMIT
            assert record['sourceTree'] == OLD_TREE and record['sourceDirty'] is False
        assert [(r['stage'], r['exitCode']) for r in receipt['records']] == [
            ('impact', 0), ('native', 0), ('native-correctness', 0), ('bundle', 1)]
        for record in receipt['records']:
            assert digest(Path(record['log']).read_bytes()) == record['logSha256']
            assert record['sourceUnchanged'] is True
        assert 'NWPKG005: Export inventory differs' in (directory / 'logs/bundle.log').read_text()
        source = Path(receipt['source'])
        absent = [directory / 'public', directory / 'consumers',
                  source / 'artifacts/public/feed', source / 'artifacts/public/release.json']
        assert all(not p.exists() for p in absent)
        assert not list(directory.rglob('*.nupkg'))
        if (source / 'artifacts/public').exists():
            assert not list((source / 'artifacts/public').rglob('*.nupkg'))
        chosen = {directory / n for n in ['build-receipt.json', 'ci-plan.json',
                   'native/manifest.json', 'native/compile_commands.json']}
        chosen |= {p for p in directory.rglob('*') if p.is_file() and
                   (p.suffix == '.log' or 'logs' in p.relative_to(directory).parts)}
        for path in sorted(chosen):
            inputs[provider + '/' + path.relative_to(directory).as_posix()] = (path, path.read_bytes())
        ctest = source / ('artifacts/cmake/linux-x64-' + provider + '/Testing/Temporary')
        for path in sorted(ctest.glob('*.log')):
            inputs[provider + '/ctest/' + path.name] = (path, path.read_bytes())
        asset = native['assets'][0]
        binary = Path(asset['path'])
        assert digest(binary.read_bytes()) == asset['sha256']
        symbols = subprocess.check_output(['readelf', '--wide', '--dyn-syms', str(binary)], text=True)
        exports = {parts[-1].split('@', 1)[0] for line in symbols.splitlines()
                   if len(parts := line.split()) >= 8 and parts[4] in ('GLOBAL', 'WEAK')
                   and parts[5] == 'DEFAULT' and parts[6] not in ('UND', 'ABS')}
        declared = expected | {'nw_database_' + provider + '_get_abi_v1'}
        assert exports - declared == {'nw_db_find_plan_create_v1'}
        assert not declared - exports
        facts.append({'provider': provider, 'source': str(source),
                      'receiptSha256': digest((directory / 'build-receipt.json').read_bytes()),
                      'nativeManifestSha256': digest((directory / 'native/manifest.json').read_bytes()),
                      'excludedNativeImage': {'path': str(binary), 'sha256': asset['sha256'], 'bytes': binary.stat().st_size},
                      'actualExportCount': len(exports), 'oldExpectedExportCount': len(declared),
                      'onlyUnexpectedExport': 'nw_db_find_plan_create_v1',
                      'newExpectedExportsEqualActual': exports == declared | {'nw_db_find_plan_create_v1'},
                      'absentProducts': [str(p) for p in absent], 'nupkgCount': 0,
                      'performanceCredit': False, 'publicAcceptanceCredit': False,
                      'stageExits': {r['stage']: r['exitCode'] for r in receipt['records']}})
    inputs['builder/build_public_inputs.py'] = (Path(receipt['script']), Path(receipt['script']).read_bytes())
    assert digest(inputs['builder/build_public_inputs.py'][1]) == receipt['scriptSha256']
    for name in ['plan.json', 'historical-main.txt', 'continuation.txt']:
        path = ROOT / 'ci-review-17da-01' / name
        inputs['review/' + name] = (path, path.read_bytes())
    metadata = {'schemaVersion': 1, 'capturedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'failedSourceCommit': OLD_COMMIT, 'failedSourceTree': OLD_TREE,
                'successorPublicCommit': NEW_COMMIT, 'successorTree': NEW_TREE,
                'sourceLocalCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
                'facts': facts, 'archivedInputs': [
                    {'archivePath': name, 'sourcePath': str(path), 'bytes': len(data), 'sha256': digest(data)}
                    for name, (path, data) in sorted(inputs.items())],
                'excluded': 'Native ELFs remain hash-bound in their original locations; PostgreSQL data directories and ongoing -02 attempts are not archived.',
                'notRun': ['product load', 'build', 'benchmark', 'stress']}
    inputs_for_tar = {name: value[1] for name, value in inputs.items()}
    inputs_for_tar['archive-inputs.json'] = (json.dumps(metadata, indent=2) + '\n').encode()

    def encode():
        result = io.BytesIO()
        with gzip.GzipFile(fileobj=result, mode='wb', mtime=0, filename='') as zipped:
            with tarfile.open(fileobj=zipped, mode='w', format=tarfile.PAX_FORMAT) as tar:
                for name, data in sorted(inputs_for_tar.items()):
                    info = tarfile.TarInfo(name)
                    info.size = len(data)
                    info.mode = 0o644
                    tar.addfile(info, io.BytesIO(data))
        return result.getvalue()

    encoded = encode()
    assert encode() == encoded
    with tarfile.open(fileobj=io.BytesIO(encoded), mode='r:gz') as tar:
        assert sorted(tar.getnames()) == sorted(inputs_for_tar)
        for name, data in inputs_for_tar.items():
            assert tar.extractfile(name).read() == data
    for name, (path, data) in inputs.items():
        assert path.read_bytes() == data, 'Original changed: ' + name
    with target.open('xb') as stream:
        stream.write(encoded)
    final = {**metadata, 'archive': {'file': target.name, 'sha256': digest(encoded),
             'bytes': len(encoded), 'members': len(inputs_for_tar)},
             'verification': {'deterministicDoubleEncoding': True, 'allMembersReadBack': True,
                              'allOriginalBytesRechecked': True}}
    with manifest_path.open('x') as stream:
        stream.write(json.dumps(final, indent=2) + '\n')
    print(json.dumps({'archive': final['archive'], 'facts': facts}, indent=2))


if __name__ == '__main__':
    main()
