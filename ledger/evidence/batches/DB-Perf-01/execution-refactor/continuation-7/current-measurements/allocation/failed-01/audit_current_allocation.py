#!/usr/bin/env python3
"""Read-only audit of 12 current allocation diagnostics; no load or timing credit."""
import argparse
import collections
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

COMMIT = '17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa'
TREE = 'bc9087d843d8d741d83d44f53d0b2c5af26dcffc'
OWNERS = ('Sources', 'Sessions', 'Operations', 'Cursors', 'Buffers', 'Owners', 'PullChannels', 'CommandCompletions')
ROWS = (1, 100, 1000)
FIELDS = ('Operations', 'MapperCalls', 'ListConstructorCalls', 'ListAddCalls', 'MapperBytes',
          'ListConstructorBytes', 'ListAddBytes', 'ObservedMapperAndListBytes', 'ProcessAllocatedBytes',
          'ProcessGen0', 'ProcessGen1', 'ProcessGen2')
BUILDER_SHA = '9697deb087e2a0d036dee4698e1c9bb7bfe6454c79585ee2b2eac77abc534932'
OBSERVER_SHA = '3cd87e22b476fac01bb3933b0c1949174d4c5816640189e76faf772e88a5923b'
PUBLIC_REVIEW_SHA = 'f0595d46fe40af1c8c8ee9f1b2dae2483fe2e3ddb64c7d1ccd0046c8b03b706e'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def integer(value, label, minimum=0):
    need(type(value) is int and value >= minimum, 'Invalid integer: ' + label)
    return value


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'Duplicate JSON field: ' + key)
        result[key] = value
    return result


def strict(data):
    return json.loads(data, object_pairs_hook=strict_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite JSON: ' + value)))


def module(name, path, expected):
    need(hashlib.sha256(path.read_bytes()).hexdigest() == expected, 'Helper source differs: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def owner_check(raw, drained):
    for name in OWNERS:
        value = integer(raw[name], name)
        if drained or name in ('Operations', 'Cursors', 'Buffers', 'PullChannels', 'CommandCompletions'):
            need(value == 0, 'Nonzero owner: ' + name)


def window_check(window, original, rows, candidate):
    for name in FIELDS:
        integer(window[name], name)
    for name in ('ProcessAllocatedBefore', 'ProcessAllocatedAfter', 'RowsPerOperation', 'Index'):
        integer(window[name], name)
    need(window['Operations'] == integer(original['Operations'], 'original operations') == 256,
         'Operation count differs')
    need(window['RowsPerOperation'] == rows and window['Route'] == original['Route']
         and window['Index'] == original['Index'], 'Window identity differs')
    need(window['MapperCalls'] == window['ListAddCalls'] == 256 * rows
         and window['ListConstructorCalls'] == 256, 'Mapper/List count does not conserve results')
    need(window['FrameworkOnlyBytes'] is None, 'Framework subtraction is forbidden')
    need(window['ObservedMapperAndListBytes'] == sum(window[n] for n in
         ('MapperBytes', 'ListConstructorBytes', 'ListAddBytes')), 'Scope byte sum differs')
    before = integer(original['AllocatedBefore'], 'AllocatedBefore')
    after = integer(original['AllocatedAfter'], 'AllocatedAfter')
    need(after >= before and window['ProcessAllocatedBefore'] == before and window['ProcessAllocatedAfter'] == after
         and window['ProcessAllocatedBytes'] == after - before, 'Process allocation delta differs')
    need(len(original['Samples']) == 256, 'Sample count differs')
    for sample in original['Samples']:
        need(type(sample['Rows']) is int and sample['Rows'] == rows, 'Incomplete result sample')
    for generation in range(3):
        need(window['ProcessGen' + str(generation)] == integer(original['Gen' + str(generation)], 'GC'),
             'Process GC delta differs')
    if candidate:
        for label in ('NativeBefore', 'NativeAfter'):
            owner_check(original[label], False)
        need(integer(original['NativeAfter']['SqlExecutions'], 'SQL after') -
             integer(original['NativeBefore']['SqlExecutions'], 'SQL before') == 256, 'SQL execution count differs')


class MemoryFiles:
    """Run the pinned text instrumentation without touching its actual inputs."""
    def __init__(self, values):
        self.values = values

    def __truediv__(self, name):
        owner = self
        class Entry:
            def read_text(self, **unused):
                return owner.values[name]

            def write_text(self, value, **unused):
                owner.values[name] = value
        return Entry()


def audit(root, repository, output):
    here = Path(__file__).resolve().parent
    c7 = here.parents[1]
    need(not output.exists(), 'Never overwrite an audit output')
    sys.dont_write_bytecode = True
    reference_path = c7 / 'local-load-tools/reference-inputs/verify_reference_reuse.py'
    ref = module('allocation_reference_identity', reference_path,
                 '0bb2d6f2ab9c0b4f8987edb4f493d2f85bab91eb9d58e88db82bc28e09f1ddfb')
    final_path = c7 / 'local-load-tools/audit_final_identity.py'
    final = module('allocation_public_identity', final_path,
                   '99f458030b41cfe9f5740cd536a0f5d3314b0955a8a72de9abce10d3ab3c91e2')
    def read(path, expected=None):
        return strict(Path(ref.bind(path, expected)['path']).read_bytes())
    need(final.source_identity(repository, COMMIT)['tree'] == TREE, 'Wrong source tree')
    public_review = read(c7 / 'current-ci-review-evidence/completed-public-builds-17da-02.json', PUBLIC_REVIEW_SHA)
    need(public_review['passed'] is True, 'Public build identity review did not pass')
    public = {item['provider']: item for item in public_review['facts']}
    builder_path = repository / 'benchmarks/db-perf/allocation-diagnostics/build.py'
    observer_path = builder_path.with_name('BusinessAllocation.cs')
    ref.committed(repository, COMMIT, str(builder_path.relative_to(repository)), BUILDER_SHA)
    ref.committed(repository, COMMIT, str(observer_path.relative_to(repository)), OBSERVER_SHA)
    builder = module('allocation_pinned_transform', builder_path, BUILDER_SHA)
    records, builds, totals, commands = [], {}, collections.Counter(), []
    for provider in ('sqlite', 'postgresql'):
        directory = root / 'measurements' / (provider + '-allocation-01')
        ordinary_dir = root / 'measurements' / (provider + '-phases-01')
        plan = read(directory / 'plan.json')
        runner = read(directory / 'runner.json')
        need(plan['provider'] == provider and plan['sourceCommit'] == COMMIT and plan['timingCredit'] is False,
             'Plan source/provider/scope differs')
        ref.bind(directory / 'plan.json', runner['planSha256'])
        expected_names = {family + '-rows' + str(rows) for family in ('candidate', 'dapper') for rows in ROWS}
        need(len(plan['commands']) == 6 and {c['name'] for c in plan['commands']} == expected_names,
             'Expected exactly six diagnostic commands per provider')
        need({p.name.removesuffix('.json.allocation.json') for p in directory.glob('*.allocation.json')} == expected_names,
             'Unexpected or missing allocation records')
        for command in plan['commands']:
            name = command['name']; family, count = name.split('-rows'); rows = int(count)
            need(command['cohort'] == family and command['timingRequested'] is False
                 and command['phase'] == 'allocation-diagnostic-no-timing-credit', 'Unexpected timing credit or cohort')
            execution = read(directory / (name + '.command.json'))
            need(type(execution['exitCode']) is int and execution['exitCode'] == 0 and execution['success'] is True
                 and execution['timedOut'] is False and execution['observerErrors'] == []
                 and execution['longRunAcceptance'] is False, 'Diagnostic command did not finish cleanly')
            argv = [value.replace('{connection}', plan['connection']).replace('{output}', str(directory))
                    for value in command['argv']]
            need(execution['argv'] == ['taskset', '-c', command['cpus'], *argv], 'Executed command differs from plan')
            need(integer(execution['finishedMonotonicNs'], 'command finish') >
                 integer(execution['startedMonotonicNs'], 'command start'), 'Bad command interval')
            for name_in_output, expected in execution['files'].items():
                ref.bind(directory / name_in_output, expected)
            commands.append({'provider': provider, 'name': name, 'startedUtc': execution['startedUtc'],
                             'finishedUtc': execution['finishedUtc'], 'startedMonotonicNs': execution['startedMonotonicNs'],
                             'finishedMonotonicNs': execution['finishedMonotonicNs']})
            path = directory / (name + '.json.allocation.json'); data = read(path)
            need(data['SchemaVersion'] == 1 and data['NativeAot'] is True and data['TimingCredit'] is False
                 and data['Failed'] is False and type(data['ResultRows']) is int and data['ResultRows'] == rows,
                 'Invalid allocation receipt')
            route_family = 'korda' if family == 'candidate' else 'dapper-aot'
            need(data['RouteFamily'] == route_family, 'Wrong allocation route family')
            base_path = Path(data['BaseReceiptPath'])
            need(base_path == directory / (name + '.json'), 'Base receipt from another command')
            base = read(base_path, data['BaseReceiptSha256'])
            need(base['Scope'].startswith('ALLOCATION-INSTRUMENTED; TimingCredit=false.') and base['NativeAot'] is True
                 and base['Provider'] == ('Sqlite' if provider == 'sqlite' else 'PostgreSql')
                 and type(base['ResultRows']) is int and base['ResultRows'] == rows, 'Base identity/scope differs')
            build_path = Path(data['BuildReceiptPath']); build = read(build_path, data['BuildReceiptSha256'])
            folder = Path(build['output']); original_folder = Path(build['consumer'])
            need(build_path == folder / 'out/allocation-build-receipt.json'
                 and read(folder / 'allocation-build-receipt.json') == build, 'Published build receipt differs')
            need(build['status'] == 'built-not-run' and build['timingCredit'] is False and build['provider'] == provider
                 and build['family'] == route_family and build['builderSha256'] == BUILDER_SHA
                 and build['observerSha256'] == OBSERVER_SHA, 'Wrong diagnostic build identity')
            stem = 'DbPerf.QueryPhases' if family == 'candidate' else 'DbPerf.DapperQueryPhases'
            executable = folder / 'out' / stem
            need(argv[0] == str(executable) and plan['inputs'][family]['path'] == str(executable), 'Wrong plan image')
            need(data['ExecutableSha256'] == base['ExecutableSha256'] == build['executableSha256'] ==
                 plan['inputs'][family]['sha256'], 'Image receipt hash differs')
            if str(build_path) not in builds:
                image = ref.elf(executable, data['ExecutableSha256'])
                original, original_assets = ref.ordinary(original_folder, build['inputBuildReceiptSha256'], repository, COMMIT)
                need(original['receiptData'] == build['inputBuildReceipt'] and build['inputSources'] == original['receiptData']['sources'],
                     'Overlay changes ordinary input receipt/source set')
                need(not Path(str(executable) + '.dll').exists(), 'Not standalone Native AOT')
                need([item['name'] for item in build['commands']] == ['generate', 'publish'], 'Unexpected diagnostic build stages')
                for item in build['commands']:
                    need(type(item['exitCode']) is int and item['exitCode'] == 0, 'Failed diagnostic build stage')
                    ref.bind(folder / item['log'], item['logSha256'])
                need(set(build['instrumentedSources']) == {p.name for p in folder.glob('*.cs')}, 'Instrumented source inventory differs')
                expected_sources = {n: (original_folder / n).read_text(encoding='utf-8-sig') for n in build['inputSources']}
                builder.instrument_consumer(MemoryFiles(expected_sources), route_family)
                expected_sources['BusinessAllocation.cs'] = observer_path.read_text()
                need(set(expected_sources) == set(build['instrumentedSources']), 'Unexpected source introduced by overlay')
                for source_name, expected in build['instrumentedSources'].items():
                    ref.bind(folder / source_name, expected)
                    need((folder / source_name).read_text() == expected_sources[source_name], 'Consumer instrumentation differs from pinned builder')
                for filename, field in [(stem + '.csproj', 'instrumentedProjectSha256'),
                                        ('generated-mapper.patch', 'generatedMapperPatchSha256'), ('packages.lock.json', 'lockFileSha256')]:
                    ref.bind(folder / filename, build[field])
                assets = read(folder / 'obj/project.assets.json', build['assetGraphSha256'])
                need(assets['libraries'] == original_assets['libraries'], 'Overlay restore graph differs')
                package_names = set()
                for package in build['packages']:
                    need(package['identity'] not in package_names, 'Duplicate overlay package')
                    package_names.add(package['identity']); ref.bind(package['path'], package['sha256'])
                    meta = read(Path(package['path']).parent / '.nupkg.metadata')
                    need(meta['contentHash'] == package['nugetContentHash'], 'NuGet contentHash differs')
                    if package['identity'] in assets['libraries']:
                        need(assets['libraries'][package['identity']]['sha512'] == meta['contentHash'], 'Restore contentHash differs')
                need({n for n, x in assets['libraries'].items() if x['type'] == 'package'} <= package_names, 'Overlay package missing')
                method_count = 0
                for generated_name, hashes in build['generatedSources'].items():
                    before, after = folder / 'generated-original' / generated_name, folder / 'generated-instrumented' / generated_name
                    ref.bind(before, hashes['originalSha256']); ref.bind(after, hashes['instrumentedSha256'])
                    original_text = before.read_text(encoding='utf-8-sig')
                    if hashes['mapper']:
                        expected_text, count_methods = builder.instrument_mapper(original_text, 'korda' if family == 'candidate' else 'dapper')
                        method_count += count_methods
                    else:
                        expected_text = original_text
                    need(after.read_text() == expected_text, 'Generated mapper instrumentation differs')
                need(method_count == build['mapperMethods'] == (2 if family == 'candidate' else 1), 'Wrong mapper method count')
                for generated_dir in ('generated-original', 'generated-instrumented'):
                    need({str(p.relative_to(folder / generated_dir)) for p in (folder / generated_dir).rglob('*.cs')} ==
                         set(build['generatedSources']), 'Generated inventory differs')
                oracle = folder / ('Program.cs' if family == 'candidate' else 'PhaseProbe.cs')
                source = oracle.read_text()
                need('rows[i].Id != i + 1 || rows[i].Note != _notes[tenant - 1][i]' in source
                     and 'id % 5 == 0 ? null : $"note-{tenant}-{id}"' in source
                     and 'throw new InvalidOperationException("Incomplete result.")' in source, 'Business row oracle absent')
                product = None
                if family == 'candidate':
                    fixed = public[provider]
                    need(original['receipt'] == fixed['phaseConsumer']['buildReceipt'] and original['executable'] == fixed['phaseConsumer']['executable'],
                         'Candidate overlay is not the current public build')
                    package = next(x for x in build['packages'] if x['identity'].startswith('Korda.Database.'))
                    product = final.package_source(repository, COMMIT, original['receiptData'],
                              {'packages': {package['identity']: {'path': package['path']}}}, fixed['releaseReceipt']['path'])
                    ref.bind(fixed['releaseReceipt']['path'], fixed['releaseReceipt']['sha256'])
                    need(build['nativeImages'] == original['receiptData']['native_images'] == fixed['nativeImages'], 'Candidate native differs from public package')
                else:
                    expected_build = {'sqlite': 'f86651d51402ce91aec58148ab59a82657497e623f820dd459be074bc63f602a',
                                      'postgresql': '62e2d1228337a3bdd048a629816a83538b0843f0458d2a1ccc1d964ab4617746'}[provider]
                    need(data['BuildReceiptSha256'] == expected_build and build['nativeImages'] == {}, 'Dapper overlay differs from retained successful input')
                for native_name, expected in build['nativeImages'].items():
                    ref.elf(folder / 'out' / native_name, expected)
                builds[str(build_path)] = {'buildReceipt': ref.bind(build_path), 'executable': image,
                    'originalConsumer': original, 'mapperMethods': method_count, 'generatedFilesVerified': len(build['generatedSources']),
                    'sourceBytesMatchCommit': COMMIT, 'historicalBuildCommitNotRelabelled': family == 'dapper',
                    'instrumentationRecomputed': True, 'product': product, 'oracle': ref.bind(oracle)}
            if family == 'candidate' or provider == 'sqlite':
                ref.elf(base['NativePath'], base['NativeSha256'])
                if family == 'candidate':
                    need(base['NativePath'] == str(folder / 'out' / next(iter(build['nativeImages']))) and
                         base['NativeSha256'] == next(iter(build['nativeImages'].values())), 'Observed candidate native differs')
                    need(base['PackageVersion'] == '0.1.0-ci.1+' + COMMIT, 'Observed candidate source differs')
                else:
                    need(base['NativeSha256'] == '2f693e43707c8174c862283185610abca5c671bbf17b6b1af7866bfbcd290282', 'SQLite native reference differs')
            else:
                need(base['NativePath'] is None and base['NativeSha256'] is None, 'Unexpected Npgsql native image')
            routes = {'fluent', 'prepared', 'host-sql'} if family == 'candidate' else {'dapper-aot'}
            keys = {(route, index) for route in routes for index in range(3)}
            need(len(data['Windows']) == len(base['Windows']) == len(keys), 'Wrong window count')
            originals = {(w['Route'], w['Index']): w for w in base['Windows']}
            need(set(originals) == keys and {(w['Route'], w['Index']) for w in data['Windows']} == keys, 'Window duplicated or missing')
            route_totals = collections.defaultdict(collections.Counter)
            for window in data['Windows']:
                window_check(window, originals[(window['Route'], window['Index'])], rows, family == 'candidate')
                for field in FIELDS:
                    route_totals[window['Route']][field] += window[field]
                totals['windows'] += 1; totals['operations'] += window['Operations']; totals['mapperCalls'] += window['MapperCalls']
                totals['listConstructors'] += window['ListConstructorCalls']; totals['listAdds'] += window['ListAddCalls']
            ordinary_path = ordinary_dir / ('candidate-rows' + str(rows) + '.json')
            ordinary_raw = read(ordinary_path)
            need(ordinary_raw['ExecutableSha256'] == public[provider]['phaseConsumer']['executable']['sha256']
                 and ordinary_raw['PackageVersion'] == '0.1.0-ci.1+' + COMMIT and ordinary_raw['ResultRows'] == rows,
                 'Current ordinary reference differs')
            if family == 'candidate':
                owner_check(base['Drained'], True)
                need(base['Sql'] == ordinary_raw['Sql'] and base['RawTemplate'] == ordinary_raw['RawTemplate'], 'Candidate SQL differs from ordinary')
            else:
                need(base['ConnectionClosed'] is True and base['CacheCommand'] is True
                     and type(base['PhysicalConnectionsOpened']) is int and base['PhysicalConnectionsOpened'] == 1
                     and type(base['PostgreSqlMaxAutoPrepare']) is int and base['PostgreSqlMaxAutoPrepare'] == 0, 'Dapper connection/prepare contract differs')
                contract = base['Contract']
                need(contract['KordaReceiptPath'] == str(ordinary_path), 'Dapper references a different or historical ordinary receipt')
                ref.bind(ordinary_path, contract['KordaReceiptSha256'])
                need(argv[argv.index('--korda-receipt') + 1] == str(ordinary_path)
                     and contract['KordaExecutableSha256'] == ordinary_raw['ExecutableSha256']
                     and contract['KordaSql'] == ordinary_raw['Sql']
                     and base['Sql'] == base['RawTemplate'] == contract['RawTemplate'] == ordinary_raw['RawTemplate'], 'Dapper SQL proof differs')
            records.append({'provider': provider, 'family': family, 'rows': rows, 'allocationReceipt': ref.bind(path),
                            'baseReceipt': ref.bind(base_path), 'buildReceipt': ref.bind(build_path),
                            'currentOrdinarySqlReference': ref.bind(ordinary_path), 'routes': {k: dict(v) for k, v in route_totals.items()},
                            'candidateAllEightOwnersZero': family == 'candidate', 'timingCredit': False, 'frameworkOnlyBytes': None})
    need(len(records) == 12 and len(builds) == 4, 'Wrong final record/build inventory')
    ordered = sorted(commands, key=lambda x: x['startedMonotonicNs'])
    need(all(a['finishedMonotonicNs'] <= b['startedMonotonicNs'] for a, b in zip(ordered, ordered[1:])), 'Diagnostic commands overlap')
    for path, expected in ref.FILES.items():
        need(ref.sha(path) == expected, 'Input changed during audit: ' + path)
    report = {'schemaVersion': 1, 'status': 'passed', 'checkedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': __doc__, 'scriptSha256': ref.sha(__file__), 'sourceCommit': COMMIT, 'sourceTree': TREE,
              'algorithmDerivedFrom': [str(c7.parent / 'continuation-3/allocation-audits' / ('audit-allocation-' + p + '-01.py')) for p in ('sqlite', 'postgresql')],
              'timingCredit': False, 'frameworkOnlyBytes': None, 'subtractionPerformed': False,
              'gcScope': 'Process-wide GC.CollectionCount deltas inside each original window; not per-thread or reconstructed process-lifetime GC including gaps.',
              'allocationScope': 'Actual generated mapper and List scopes include codec/driver scratch inside those bodies; not pure live DTO size. Whole-process window allocation is reported independently.',
              'resultOracleEvidence': 'All JSON sample row counts checked; hash-bound unchanged per-row Id/order/Note/null oracle source checked. No invented row-digest field.',
              'records': records, 'builds': builds, 'totals': dict(totals), 'commands': ordered, 'inputFiles': ref.FILES,
              'inputsUnchanged': True, 'workloadsStarted': 0, 'buildsStarted': 0}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        json.dump(report, stream, indent=2); stream.write('\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.root.resolve(), args.repository.resolve(), args.output.resolve())
    print(json.dumps({'status': report['status'], 'records': len(report['records']), 'totals': report['totals'], 'output': str(args.output)}))
    for r in report['records']:
        for route, values in r['routes'].items():
            print(json.dumps({'provider': r['provider'], 'family': r['family'], 'rows': r['rows'], 'route': route,
                  'mapperBytesPerOperation': values['MapperBytes'] / values['Operations'],
                  'listBytesPerOperation': (values['ListConstructorBytes'] + values['ListAddBytes']) / values['Operations'],
                  'observedScopesBytesPerOperation': values['ObservedMapperAndListBytes'] / values['Operations'],
                  'processBytesPerOperation': values['ProcessAllocatedBytes'] / values['Operations'],
                  'processGC': [values['ProcessGen' + str(i)] for i in range(3)]}))


if __name__ == '__main__':
    main()
