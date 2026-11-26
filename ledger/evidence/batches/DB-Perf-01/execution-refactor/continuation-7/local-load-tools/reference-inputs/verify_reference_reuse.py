#!/usr/bin/env python3
"""Verify existing reference consumers and allocation overlays without executing them."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

FILES = {}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def bind(path, expected=None):
    path = Path(path).resolve(strict=True)
    value = sha(path)
    need(expected is None or value == expected, 'Hash differs: ' + str(path))
    need(str(path) not in FILES or FILES[str(path)] == value, 'Input changed: ' + str(path))
    FILES[str(path)] = value
    return {'path': str(path), 'sha256': value}


def read(path, expected=None):
    item = bind(path, expected)
    return json.loads(Path(item['path']).read_bytes())


def elf(path, expected):
    entry = bind(path, expected)
    with Path(path).open('rb') as stream:
        header = stream.read(20)
    need(header[:6] == b'\x7fELF\x02\x01' and int.from_bytes(header[18:20], 'little') == 62, 'Not Linux x64 ELF')
    return entry


def committed(repository, commit, relative, expected):
    value = subprocess.check_output(['git', '-C', str(repository), 'show', commit + ':' + relative])
    need(hashlib.sha256(value).hexdigest() == expected, 'Source differs from committed reference: ' + relative)
    bind(repository / relative, expected)
    return {'commit': commit, 'repositoryPath': relative, 'sha256': expected}


def ordinary(folder, expected_receipt=None, source=None, commit=None):
    receipt_path = folder / 'build-receipt.json'
    receipt = read(receipt_path, expected_receipt)
    need(receipt.get('exit_code', receipt.get('exitCode')) == 0 and not receipt.get('postValidationError')
         and not receipt.get('post_validation_error'), 'Unsuccessful ordinary consumer')
    project = Path(receipt['command'][2])
    need(project.parent == folder and not ET.parse(project).getroot().findall('.//ProjectReference'), 'Not independent package consumer')
    bind(project, receipt.get('project_sha256', receipt.get('projectSha256')))
    bind(folder / 'publish.log', receipt.get('publish_log_sha256', receipt.get('logSha256')))
    role = 'Korda' if 'package' in receipt else 'Dapper'
    source_folder = 'benchmarks/db-perf/' + ('query-phases' if role == 'Korda' and receipt['kind'] == 'query-phases'
                    else 'managed/DapperQueryPhases' if receipt['kind'] == 'query-phases' else 'managed/' + role)
    source_refs = {}
    for name, expected in receipt['sources'].items():
        bind(folder / name, expected)
        relative = source_folder + '/' + name
        if not (source / relative).is_file():
            relative = 'benchmarks/db-perf/managed/Shared/' + name
        source_refs[name] = committed(source, commit, relative, expected)
    bind(folder / 'global.json')
    bind(folder / 'NuGet.Config')
    assets = read(folder / 'obj/project.assets.json', receipt.get('assets_sha256', receipt.get('assetsSha256')))
    generated = receipt.get('generatedSourceSha256', {})
    for name, expected in generated.items():
        bind(folder / 'generated' / name, expected)
    package_source = None
    if 'package' in receipt:
        package, version = receipt['package'].lower(), receipt['version'].lower()
        path = folder / 'packages' / package / version / (package + '.' + version + '.nupkg')
        bind(path, receipt['package_sha256'])
        with zipfile.ZipFile(path) as archive:
            meta = ET.fromstring(archive.read(receipt['package'] + '.nuspec'))
            package_source = meta.find('.//{*}repository').attrib
        for name, expected in receipt['native_images'].items():
            elf(folder / 'out' / name, expected)
        stem = 'DbPerf.QueryPhases' if receipt['kind'] == 'query-phases' else 'DbPerf.Korda'
    else:
        need(set(receipt['packages']) == {n for n, x in assets['libraries'].items() if x['type'] == 'package'}, 'Ordinary restore package set differs')
        for entry in receipt['packages'].values():
            bind(entry['path'], entry['sha256'])
        stem = 'DbPerf.DapperQueryPhases' if receipt['kind'] == 'query-phases' else 'DbPerf.Dapper'
    image = elf(folder / 'out' / stem, receipt.get('executable_sha256', receipt.get('executableSha256')))
    return {'receipt': bind(receipt_path), 'receiptData': receipt, 'executable': image,
            'packageSource': package_source, 'copiedSourcesMatchReferenceCommit': source_refs}, assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'session', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), 'Fresh output required')
    root, session = args.root.resolve(), args.session.resolve()
    reused = read(session / 'reused-comparison-inputs.json')
    refreshed = read(session / 'refreshed-baseline-phase-inputs.json')
    old_phase = read(session / 'reused-baseline-phase-inputs.json')
    source, commit = Path(reused['source']), reused['sourceCommit']
    tree = subprocess.check_output(['git', '-C', str(source), 'rev-parse', commit + '^{tree}'], text=True).strip()
    bind(__file__)
    originals = {}
    summaries = []
    for entry in reused['inputs']:
        folder = Path(entry['directory'])
        value, _ = ordinary(folder, entry['receiptSha256'], source, commit)
        need(value['executable']['sha256'] == entry['executableSha256'] and entry['sourcesMatchCurrentBenchmark'] is True, 'Reference index differs')
        originals[str(folder)] = value
        summaries.append({'provider': entry['provider'], 'cohort': entry['cohort'], 'consumer': str(folder),
                          'receipt': value['receipt'], 'executable': value['executable'], 'packageSource': value['packageSource']})
    for entry in refreshed:
        value, _ = ordinary(Path(entry['consumer']), entry['buildReceiptSha256'], source, commit)
        need(value['receiptData']['package_sha256'] == entry['packageSha256']
             and value['executable']['sha256'] == entry['executableSha256']
             and value['receiptData']['native_images'] == entry['nativeImages'] and entry['harnessMatches'] is True,
             'Refreshed baseline phase identity differs')
        summaries.append({'provider': entry['provider'], 'cohort': 'before-phases', 'consumer': entry['consumer'],
                          'receipt': value['receipt'], 'executable': value['executable'], 'packageSource': value['packageSource']})
    builder_path = source / 'benchmarks/db-perf/allocation-diagnostics/build.py'
    observer_path = builder_path.with_name('BusinessAllocation.cs')
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('reference_allocation_builder', builder_path)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    overlays = []
    for provider, name in [('sqlite', 'allocation-dapper-sqlite-05'), ('postgresql', 'allocation-dapper-postgresql')]:
        folder = root / 'consumers' / name
        receipt_path = folder / 'allocation-build-receipt.json'
        receipt = read(receipt_path)
        need(receipt['status'] == 'built-not-run' and receipt['timingCredit'] is False and receipt['family'] == 'dapper-aot'
             and receipt['provider'] == provider and receipt['mapperMethods'] == 1 and receipt['nativeImages'] == {}, 'Unexpected allocation receipt')
        need(read(folder / 'out/allocation-build-receipt.json') == receipt, 'Published diagnostic receipt differs')
        committed(source, commit, 'benchmarks/db-perf/allocation-diagnostics/build.py', receipt['builderSha256'])
        committed(source, commit, 'benchmarks/db-perf/allocation-diagnostics/BusinessAllocation.cs', receipt['observerSha256'])
        need([x['name'] for x in receipt['commands']] == ['generate', 'publish'] and all(x['exitCode'] == 0 for x in receipt['commands']), 'Failed allocation commands')
        for command in receipt['commands']:
            bind(folder / command['log'], command['logSha256'])
        original = originals[receipt['consumer']]
        need(original['receipt']['sha256'] == receipt['inputBuildReceiptSha256'] and original['receiptData'] == receipt['inputBuildReceipt']
             and receipt['inputSources'] == original['receiptData']['sources'], 'Overlay differs from its successful ordinary consumer')
        for name, expected in receipt['instrumentedSources'].items():
            bind(folder / name, expected)
        need(set(receipt['instrumentedSources']) == {p.name for p in folder.glob('*.cs')}, 'Instrumented source inventory differs')
        bind(folder / 'DbPerf.DapperQueryPhases.csproj', receipt['instrumentedProjectSha256'])
        bind(folder / 'generated-mapper.patch', receipt['generatedMapperPatchSha256'])
        bind(folder / 'packages.lock.json', receipt['lockFileSha256'])
        assets = read(folder / 'obj/project.assets.json', receipt['assetGraphSha256'])
        original_assets = read(Path(receipt['consumer']) / 'obj/project.assets.json', original['receiptData']['assetsSha256'])
        need(assets['libraries'] == original_assets['libraries'], 'Overlay changes ordinary restore graph')
        package_names = set()
        for package in receipt['packages']:
            need(package['identity'] not in package_names, 'Duplicate allocation package')
            package_names.add(package['identity'])
            entry = bind(package['path'], package['sha256'])
            meta = read(Path(entry['path']).parent / '.nupkg.metadata')
            need(meta['contentHash'] == package['nugetContentHash'], 'NuGet content identity differs')
            if package['identity'] in original['receiptData']['packages']:
                need(original['receiptData']['packages'][package['identity']]['sha256'] == package['sha256'], 'Overlay package differs from ordinary package')
            if package['identity'] in assets['libraries']:
                need(assets['libraries'][package['identity']]['sha512'] == meta['contentHash'], 'Asset graph contentHash differs')
        need(set(original['receiptData']['packages']) <= package_names, 'Overlay omits an ordinary package')
        mapper_methods = 0
        for name, expected in receipt['generatedSources'].items():
            before, after = folder / 'generated-original' / name, folder / 'generated-instrumented' / name
            bind(before, expected['originalSha256'])
            bind(after, expected['instrumentedSha256'])
            original_text = before.read_text(encoding='utf-8-sig')
            if expected['mapper']:
                expected_text, count = builder.instrument_mapper(original_text, 'dapper')
                mapper_methods += count
            else:
                expected_text = original_text
            need(after.read_text() == expected_text, 'Generated instrumentation differs from the pinned builder')
        need(mapper_methods == 1 and len(receipt['generatedSources']) == 21, 'Generated mapper/source inventory differs')
        image = elf(folder / 'out/DbPerf.DapperQueryPhases', receipt['executableSha256'])
        historical = []
        native = None
        for rows in (1, 100, 1000):
            path = root / 'measurements' / ('allocation-' + provider + '-01') / ('dapper-rows' + str(rows) + '.json')
            raw = read(path)
            need(raw['ExecutableSha256'] == image['sha256'] and raw['ConnectionClosed'] is True, 'Historical overlay image/connection differs')
            if provider == 'sqlite':
                current_native = elf(raw['NativePath'], raw['NativeSha256'])
                need(native is None or native == current_native, 'Historical native changes between row counts')
                native = current_native
            else:
                need(raw['NativePath'] is None and raw['NativeSha256'] is None, 'Npgsql declares unexpected native image')
            historical.append({'rows': rows, 'receipt': bind(path), 'scope': 'Historical allocation-only identity; not current-candidate performance credit'})
        overlays.append({'provider': provider, 'directory': str(folder), 'reusableAsAllocationOnly': True, 'timingCredit': False,
                         'receipt': bind(receipt_path), 'executable': image, 'bundledNativeImages': {}, 'runtimeNativeLibrary': native,
                         'originalConsumer': original['receipt'], 'originalExecutable': original['executable'],
                         'builder': bind(builder_path), 'observer': bind(observer_path), 'packages': receipt['packages'],
                         'historicalObservations': historical,
                         'nextInvocationRequirement': 'Bind the corresponding new ordinary candidate receipt for the same rows; SQLite also needs this exact external native library'})
    failures = []
    for name in ('allocation-dapper-sqlite-03', 'allocation-dapper-sqlite-04'):
        folder = root / 'consumers' / name
        receipt = read(folder / 'allocation-build-receipt.json')
        need(receipt['status'] == 'failed' and receipt['timingCredit'] is False, 'Historical failure marker changed')
        for command in receipt['commands']:
            bind(folder / command['log'], command['logSha256'])
        failures.append({'directory': str(folder), 'receipt': bind(folder / 'allocation-build-receipt.json'),
                         'status': receipt['status'], 'failure': receipt['failure'], 'builderSha256': receipt['builderSha256']})
    for path, expected in FILES.items():
        need(sha(path) == expected, 'Input changed during read-only verification: ' + path)
    output = {'schemaVersion': 1, 'scope': __doc__, 'compatibleReferenceSource': {'repository': str(source), 'commit': commit, 'tree': tree,
              'meaning': 'Copied source bytes and diagnostic builder match this committed reference; this does not relabel historical build timestamps or infer an unrecorded original harness commit'},
              'ordinaryReferenceConsumers': summaries, 'allocationOverlays': overlays, 'retainedFailures': failures,
              'oldBaselinePhaseMismatchRetained': old_phase, 'inputFiles': FILES, 'inputsUnchanged': True,
              'workloadProcessesStarted': 0, 'buildsStarted': 0, 'currentFinalCredit': '0/4', 'passed': True}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(output, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'passed': True, 'ordinaryConsumers': len(summaries), 'allocationOverlays': len(overlays),
                      'retainedFailures': len(failures), 'inputFiles': len(FILES), 'output': str(args.output)}))


if __name__ == '__main__':
    main()
