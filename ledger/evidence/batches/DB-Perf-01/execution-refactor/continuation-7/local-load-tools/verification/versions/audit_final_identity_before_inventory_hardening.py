#!/usr/bin/env python3
"""Freeze, then audit final mixed-load producer/ELF/native identities and owners.

Read-only with respect to sources and evidence. No workload, build or database
is executed. The existing arithmetic report remains responsible for duration,
mixed-case coverage, fixture exclusion, counters and four serial final cells.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

SELECTOR_SHA = '507afc98c5b448bba3daeae3c3fb77ea748d983029f42a6baf5870098abba43d'
CONSUMER_READER_SHA = '0cec15c40be5a8c1db900d884daf2bc83f9f84fc5ff930c30d9ebac38d5a5730'
PROVIDERS = ('sqlite', 'postgresql')
COHORTS = ('candidate', 'dapper')
OWNERS = ('Sources', 'Sessions', 'Operations', 'Cursors', 'Buffers', 'Owners', 'PullChannels', 'CommandCompletions')
FILES = {}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(value).hexdigest()


def identity(path, expected=None):
    path = Path(path).resolve(strict=True)
    value = path.read_bytes()
    actual = digest(value)
    need(expected is None or actual == expected, 'Changed bound input: ' + str(path))
    need(str(path) not in FILES or FILES[str(path)] == actual, 'Input changed while reading: ' + str(path))
    FILES[str(path)] = actual
    return {'path': str(path), 'sha256': actual}


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def read(path, expected=None):
    entry = identity(path, expected)
    return json.loads(Path(entry['path']).read_bytes(), object_pairs_hook=strict_object,
                      parse_constant=lambda token: (_ for _ in ()).throw(ValueError('Nonfinite JSON: ' + token)))


def module(name, path, expected=None):
    entry = identity(path, expected)
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(name, entry['path'])
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def git(repository, *args):
    return subprocess.check_output(['git', '-C', str(repository), *args])


def source_identity(repository, commit):
    need(isinstance(commit, str) and re.fullmatch('[0-9a-f]{40}', commit), 'Exact full source commit required')
    actual = git(repository, 'rev-parse', '--verify', commit + '^{commit}').decode().strip()
    need(actual == commit, 'Source commit differs')
    return {'commit': commit, 'tree': git(repository, 'rev-parse', commit + '^{tree}').decode().strip()}


def source_file(repository, commit, relative, path=None, expected=None):
    value = git(repository, 'show', commit + ':' + relative)
    actual = digest(value)
    need(expected is None or actual == expected, 'Producer source differs from commit: ' + relative)
    if path is not None:
        identity(path, actual)
    return {'commit': commit, 'path': relative, 'sha256': actual}


def elf(path, expected):
    result = identity(path, expected)
    with Path(path).open('rb') as stream:
        header = stream.read(20)
    need(len(header) == 20 and header[:6] == b'\x7fELF\x02\x01'
         and int.from_bytes(header[18:20], 'little') == 62, 'Not Linux x64 ELF: ' + str(path))
    return result


def source_inventory(repository, commit, role):
    base = 'benchmarks/db-perf/managed/'
    folders = (base + ('Korda' if role == 'candidate' else 'Dapper'), base + 'Shared')
    result = {}
    for folder in folders:
        names = git(repository, 'ls-tree', '-r', '--name-only', commit, folder).decode().splitlines()
        for name in names:
            if str(Path(name).parent) == folder and name.endswith('.cs'):
                result[Path(name).name] = name
    return result


def package_source(repository, commit, receipt, consumer, release_path):
    release = read(release_path)
    source = source_identity(repository, commit)
    need(release['source_commit'] == source['commit'] and release['source_tree'] == source['tree']
         and release['source_dirty'] is False and release['rid'] == 'linux-x64', 'Release source/tree/RID differs')
    selected = [x for x in release['packages'] if x['id'] == receipt['package'] and x['version'] == receipt['version']]
    need(len(selected) == 1, 'Release package is missing/duplicated')
    package = selected[0]
    expected = receipt['package_sha256']
    need(package['upload_archive_sha256'] == expected and package['source_commit'] == commit, 'Release package hash/source differs')
    archive_path = next(iter(consumer['packages'].values()))['path']
    identity(archive_path, expected)
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) and set(names) - {'.signature.p7s'} == set(package['unsigned_entries']),
             'Package inventory differs from release receipt')
        for name, expected_sha in package['unsigned_entries'].items():
            need(digest(archive.read(name)) == expected_sha, 'Package member differs: ' + name)
        metadata = ET.fromstring(archive.read(receipt['package'] + '.nuspec'))
        need(metadata.find('.//{*}repository').attrib['commit'] == commit, 'Nuspec source commit differs')
        native = package['native']
        need(native['source_commit'] == commit and native['rid'] == 'linux-x64'
             and native['sha256'] == digest(archive.read(native['path'])), 'Packaged native identity differs')
        native_name = Path(native['path']).name
        need(receipt['native_images'] == {native_name: native['sha256']}, 'Published native differs from package')
    return {'source': source, 'releaseReceipt': identity(release_path), 'packageSha256': receipt['package_sha256'],
            'nativePackageMember': native, 'packageMemberHashes': package['unsigned_entries']}


def consumer_binding(repository, provider, role, descriptor, plan, reader, candidate_commit):
    need(set(descriptor) == {'buildReceipt', 'harnessCommit'} | ({'releaseReceipt'} if role == 'candidate' else set()),
         'Unexpected consumer descriptor')
    receipt_path = Path(descriptor['buildReceipt']).resolve(strict=True)
    folder = receipt_path.parent
    receipt = read(receipt_path)
    harness = source_identity(repository, descriptor['harnessCommit'])
    executable = plan['inputs']['consumers'][role]
    need(Path(executable['path']).resolve() == folder / 'out' / ('DbPerf.Korda' if role == 'candidate' else 'DbPerf.Dapper'),
         'Plan executable belongs to another producer')
    need(not Path(executable['path'] + '.dll').exists(), 'Consumer is not a standalone AOT image')
    bound = {'buildReceipt': identity(receipt_path), 'receiptData': receipt,
             'executable': elf(executable['path'], executable['sha256']),
             'sources': {name: identity(folder / name, expected) for name, expected in receipt['sources'].items()}}
    need(set(receipt['sources']) == {p.name for p in folder.glob('*.cs')}, 'Consumer source file inventory differs')
    inventory = source_inventory(repository, harness['commit'], role)
    need(set(inventory) == set(receipt['sources']), 'Consumer source set differs from committed harness')
    copied = {name: source_file(repository, harness['commit'], relative, folder / name, receipt['sources'][name])
              for name, relative in inventory.items()}
    builder = 'benchmarks/db-perf/managed/' + ('build.py' if role == 'candidate' else 'build_orm.py')
    builder_source = source_file(repository, harness['commit'], builder,
                                 expected=receipt['builder_sha256'] if role == 'candidate' else None)
    project = folder / ('DbPerf.Korda.csproj' if role == 'candidate' else 'DbPerf.Dapper.csproj')
    source_file(repository, harness['commit'], 'benchmarks/db-perf/managed/' +
                ('Korda' if role == 'candidate' else 'Dapper') + '/' + project.name, project)
    source_file(repository, harness['commit'], 'global.json', folder / 'global.json')
    need(not ET.parse(project).getroot().findall('.//ProjectReference'), 'Consumer has a project reference')
    command = receipt['command']
    need(command[:3] == ['dotnet', 'publish', str(project)] and '-p:PublishAot=true' in command
         and command[command.index('-c') + 1] == 'Release' and command[command.index('-r') + 1] == 'linux-x64',
         'Producer is not the Release Native AOT Linux x64 build')
    if role == 'candidate':
        package, version = receipt['package'].lower(), receipt['version'].lower()
        path = folder / 'packages' / package / version / (package + '.' + version + '.nupkg')
        bound['packages'] = {receipt['package'] + '/' + receipt['version']: identity(path, receipt['package_sha256'])}
        bound['nativeImages'] = {name: elf(folder / 'out' / name, expected) for name, expected in receipt['native_images'].items()}
        identity(folder / 'publish.log', receipt['publish_log_sha256'])
        identity(folder / 'NuGet.Config', receipt['config_sha256'])
        assets = read(folder / 'project.assets.json', receipt['assets_sha256'])
        need({name for name in assets['libraries'] if name.lower().startswith('korda.')} == set(bound['packages']), 'Restored Korda graph differs')
    else:
        bound['packages'] = receipt['packages']
        for entry in bound['packages'].values():
            identity(entry['path'], entry['sha256'])
        identity(folder / 'publish.log', receipt['logSha256'])
        identity(folder / 'NuGet.Config')
        assets = read(folder / 'project.assets.json', receipt['assetsSha256'])
        need({name for name, value in assets['libraries'].items() if value['type'] == 'package'} == set(bound['packages']),
             'Restored Dapper graph differs')
        need(receipt['lifecycleSqlMode'] == 'matched', 'Final Dapper must use the matched SQL contract')
        validator_path = repository / 'benchmarks/db-perf/workload/check_dapper_contract.py'
        source_file(repository, harness['commit'], 'benchmarks/db-perf/workload/check_dapper_contract.py',
                    validator_path, receipt['contractValidatorSha256'])
        source_file(repository, harness['commit'], 'benchmarks/db-perf/workload/lifecycle-sql-matched-v1.json',
                    validator_path.with_name('lifecycle-sql-matched-v1.json'), receipt['lifecycleSqlPolicySha256'])
        validator = module('final_sql_validator', validator_path, receipt['contractValidatorSha256'])
        static = read(folder / receipt['sqlContract']['path'], receipt['sqlContract']['sha256'])
        generated = read(folder / receipt['generatedSqlContract']['path'], receipt['generatedSqlContract']['sha256'])
        need(validator.contract_receipt(folder / 'workload-manifest.json', folder / 'Contracts.generated.cs', 'matched') == static,
             'Recomputed static SQL contract differs')
        need(validator.validate_generated(folder, static) == generated, 'Recomputed actual generated factory proof differs')
    pseudo = {'provider': provider, 'inputs': {'manifest': plan['inputs']['manifest'],
             'consumers': {'korda' if role == 'candidate' else 'dapper': bound}}}
    reader.consumer_inputs(pseudo)
    for name, expected in reader.FILES.items():
        identity(name, expected)
    generated_sources = {str(path.relative_to(folder)): identity(path) for path in sorted((folder / 'generated').rglob('*.cs'))}
    need(generated_sources, 'Actual generated source files are absent')
    identity(folder / 'workload-manifest.json', plan['inputs']['manifest']['sha256'])
    result = {'provider': provider, 'cohort': role, 'harnessSource': harness, 'builderSource': builder_source,
              'copiedCommittedSources': copied, 'consumer': bound, 'generatedSources': generated_sources}
    if role == 'candidate':
        result['product'] = package_source(repository, candidate_commit, receipt, bound, descriptor['releaseReceipt'])
    return result


def make_bindings(spec_path, require_fresh):
    spec = read(spec_path)
    need(set(spec) == {'schemaVersion', 'repository', 'runnerCommit', 'candidateCommit', 'generator', 'selector',
                       'consumerReader', 'arithmeticAnalyzer', 'plans', 'consumers'}
         and type(spec['schemaVersion']) is int and spec['schemaVersion'] == 1,
         'Unexpected freeze specification')
    repository = Path(spec['repository']).resolve(strict=True)
    runner_source = source_identity(repository, spec['runnerCommit'])
    product_source = source_identity(repository, spec['candidateCommit'])
    selector = module('final_plan_selector', spec['selector'], SELECTOR_SHA)
    identity(spec['generator'], selector.GENERATOR_SHA256)
    identity(spec['arithmeticAnalyzer'])
    for name in ('strict_io.py', 'raw_metrics.py'):
        relative = 'benchmarks/db-perf/analysis/' + name
        source_file(repository, spec['runnerCommit'], relative, repository / relative)
    relative = 'benchmarks/db-perf/query-phases/summarize.py'
    source_file(repository, spec['runnerCommit'], relative, repository / relative)
    reader = module('final_consumer_reader', spec['consumerReader'], CONSUMER_READER_SHA)
    reader.load_helpers(repository)
    need(set(spec['plans']) == set(spec['consumers']) == set(PROVIDERS), 'Exactly both providers required')
    plans, consumers = {}, {}
    for provider in PROVIDERS:
        plan_path = Path(spec['plans'][provider]).resolve(strict=True)
        plan = read(plan_path)
        parent = plan['derivedFrom']
        need(parent['selector'] == identity(spec['selector']) and parent['generator'] == identity(spec['generator'])
             and parent['runnerSourceCommit'] == runner_source['commit'] and parent['runnerSourceTree'] == runner_source['tree'],
             'Derived source/tool identity differs')
        original = read(parent['plan']['path'], parent['plan']['sha256'])
        details = selector.validate_source_plan(original, Path(parent['plan']['path']), 'final')
        for name in ('runner', 'manifest'):
            source_file(repository, spec['runnerCommit'], str(details[name].relative_to(repository)), details[name])
        output = Path(plan['runnerCommand'][-1])
        need(not require_fresh or not output.exists(), 'Freeze must precede measured output creation')
        expected = selector.derive(original, details, 'final', plan_path, output, parent)
        need(plan == expected and plan['provider'] == provider, 'Derived final plan differs from exact selector transformation')
        reader.bind_tree(plan['inputs'])
        for path, expected_sha in reader.FILES.items():
            identity(path, expected_sha)
        need(set(spec['consumers'][provider]) == set(COHORTS), 'Exactly candidate and Dapper producer descriptors required')
        consumers[provider] = {cohort: consumer_binding(repository, provider, cohort, spec['consumers'][provider][cohort],
                                plan, reader, spec['candidateCommit']) for cohort in COHORTS}
        plans[provider] = {'identity': identity(plan_path), 'output': str(output), 'plan': plan}
    return {'specification': identity(spec_path), 'repository': str(repository), 'runnerSource': runner_source,
            'candidateSource': product_source, 'generator': identity(spec['generator']), 'selector': identity(spec['selector']),
            'consumerReader': identity(spec['consumerReader']), 'arithmeticAnalyzer': identity(spec['arithmeticAnalyzer']),
            'plans': plans, 'consumers': consumers}


def verify_owners_and_image(raw, binding, plan):
    role, provider, consumer = binding['cohort'], binding['provider'], binding['consumer']
    need(raw['NativeAot'] is True and raw['ExecutableSha256'] == consumer['executable']['sha256'], 'Actual AOT executable differs')
    elf(consumer['executable']['path'], raw['ExecutableSha256'])
    drained = raw['Drained']
    if role == 'candidate':
        need(raw['Route'] == 'korda-public-fluent' and raw['PackageVersion'] == consumer['receiptData']['version'], 'Actual Korda route/package differs')
        need(raw['OwnersReturnedToZero'] is True, 'Korda owner-zero declaration is false')
        counters = {name: drained[name] for name in OWNERS}
        need(all(type(value) is int and value == 0 for value in counters.values()), 'Korda owner leak or malformed owner counter')
        native = next(iter(consumer['nativeImages'].values()))
    else:
        need(raw['Route'] == 'independent-csharp-micro-orm-dapper-aot', 'Actual Dapper route differs')
        versions = consumer['packages']
        expected_versions = {name for name in versions if name.split('/')[0] in
                             ('Dapper', 'Dapper.AOT', 'Npgsql', 'Microsoft.Data.Sqlite.Core')}
        need(set(raw['PackageVersion'].split(';')) == expected_versions, 'Actual Dapper/provider package versions differ')
        need(raw['ApplicationConnectionsReturnedToZero'] is True and type(drained['ApplicationConnections']) is int
             and drained['ApplicationConnections'] == 0, 'Dapper application connections did not drain')
        counters = {'ApplicationConnections': drained['ApplicationConnections']}
        native = plan['inputs']['sqliteLibrary'] if provider == 'sqlite' else None
    if native is None:
        need(raw['LoadedNativePath'] is None and raw['LoadedNativeSha256'] is None, 'Npgsql falsely declares a native image')
    else:
        need(raw['LoadedNativePath'] == native['path'] and raw['LoadedNativeSha256'] == native['sha256'], 'Actual loaded native differs')
        elf(native['path'], native['sha256'])
    return {'ownerCounters': counters, 'executable': consumer['executable'], 'loadedNative': native}


def verify_arithmetic_report(report, bindings):
    source = bindings['arithmeticAnalyzer']
    arithmetic = module('frozen_final_arithmetic', source['path'], source['sha256'])
    helpers = arithmetic.Helpers(Path(bindings['repository']))
    observed = arithmetic.Analyzer(Path(report['index']['path']), helpers).analyze()
    need(observed == {key: report[key] for key in observed}, 'Arithmetic report differs from independent reread of its original inputs')


def audit(freeze_path, expected_sha, analysis_path):
    frozen = read(freeze_path, expected_sha)
    need(frozen['status'] == 'frozen' and frozen['schemaVersion'] == 1
         and frozen['auditor'] == identity(__file__), 'Freeze/auditor identity differs')
    for path, expected in frozen['inputFiles'].items():
        identity(path, expected)
    bindings = make_bindings(frozen['bindings']['specification']['path'], require_fresh=False)
    need(bindings == frozen['bindings'], 'Revalidated producer/source/plan bindings differ from freeze')
    report = read(analysis_path)
    need(report['analyzerSha256'] == bindings['arithmeticAnalyzer']['sha256'] and report['inputsChangedDuringAnalysis'] == [],
         'Arithmetic analyzer source/inputs differ')
    need(report['finalFour']['fourCompleteRawReceipts'] is True
         and report['finalFour']['sameHostAndSerialIncludingRecordedIdle'] is True, 'Existing arithmetic final-four checks failed')
    report_inputs = {entry['path']: entry['storedSha256'] for entry in report['inputFiles']}
    need(len(report_inputs) == len(report['inputFiles']), 'Duplicate arithmetic input paths')
    for path, expected in report_inputs.items():
        identity(path, expected)
    verify_arithmetic_report(report, bindings)
    finals = [entry for entry in report['observations'] if entry.get('final')]
    need(len(finals) == 4 and {(x['provider'], x['cohort']) for x in finals} == {(p, c) for p in PROVIDERS for c in COHORTS},
         'Final observations are missing or duplicated')
    segments = []
    for entry in finals:
        need(entry['timingCredit'] is True, 'Final observation lacks arithmetic timing eligibility')
        provider, cohort = entry['provider'], entry['cohort']
        bound_plan = bindings['plans'][provider]
        plan, output = bound_plan['plan'], Path(bound_plan['output'])
        measured = [x for x in plan['commands'] if x['timingRequested'] and x['cohort'] == cohort]
        need(len(measured) == 1, 'Frozen measured command differs')
        item = measured[0]
        raw_path, command_path = output / (item['name'] + '.json'), output / (item['name'] + '.command.json')
        need(entry['input']['path'] == str(raw_path) and entry['invocation']['input']['path'] == str(command_path),
             'Arithmetic report points to another command or receipt')
        raw = read(raw_path, entry['input']['storedSha256'])
        command = read(command_path, entry['invocation']['input']['storedSha256'])
        need(read(output / 'plan.json', bound_plan['identity']['sha256']) == plan, 'Executed plan differs from frozen plan')
        runner = read(output / 'runner.json')
        need(runner['planSha256'] == bound_plan['identity']['sha256'] and runner['runnerSha256'] == plan['inputs']['runner']['sha256'],
             'Executed runner source/plan differs')
        need(command['success'] is True and command['exitCode'] == 0 and command['timedOut'] is False
             and command['observerErrors'] == [], 'Final command or observer failed')
        argv = command['argv']
        need(argv[:4] == ['taskset', '-c', item['cpus'], plan['inputs']['consumers'][cohort]['path']], 'Executed consumer/affinity differs')
        connection = argv[argv.index('--connection') + 1]
        if provider == 'sqlite':
            need(connection == plan['connection'], 'Executed SQLite database differs')
        else:
            server = read(output / 'postgres-owner.json')
            server_argv = server['argv']
            need(server['exitCode'] == 0 and not any(key in server for key in ('error', 'shutdownError', 'finalSampleError', 'cpuGroupError')),
                 'PostgreSQL owner failed')
            need(server_argv[:4] == ['taskset', '-c', plan['postgres']['cpus'], plan['inputs']['postgresTools']['postgres']['path']]
                 and server_argv[server_argv.index('-D') + 1] == plan['postgres']['data'], 'Executed PostgreSQL identity differs')
            port = server_argv[server_argv.index('-p') + 1]
            need(connection == 'postgresql://korda@127.0.0.1:' + port + '/db_perf_01', 'Executed PostgreSQL connection differs')
        need(argv == ['taskset', '-c', item['cpus'], *[x.replace('{connection}', connection).replace('{output}', str(output))
                                                     for x in item['argv']]], 'Executed options differ from frozen command')
        image = verify_owners_and_image(raw, bindings['consumers'][provider][cohort], plan)
        segments.append({'provider': provider, 'cohort': cohort, 'receipt': identity(raw_path), 'commandReceipt': identity(command_path),
                         **image, 'commandStartedUtc': command['startedUtc'], 'commandFinishedUtc': command['finishedUtc'],
                         'commandStartedMonotonicNs': command['startedMonotonicNs'], 'commandFinishedMonotonicNs': command['finishedMonotonicNs'],
                         'steadyStartMonotonicNs': raw['SteadyStartMonotonicNs'], 'steadyEndMonotonicNs': raw['SteadyEndMonotonicNs'],
                         'consumerStartedUtc': raw['StartedUtc'], 'consumerFinishedUtc': raw['FinishedUtc'],
                         'idleFinishedUtc': raw['Idle']['FinishedUtc']})
    return {'status': 'passed', 'freeze': identity(freeze_path, expected_sha), 'arithmeticReport': identity(analysis_path),
            'bindings': bindings, 'segments': segments, 'ownersAndProducerImagesVerified': True,
            'scope': 'Final four-cell identity/owner supplement only; arithmetic report retains duration/business/serial decisions.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    freeze = sub.add_parser('freeze')
    freeze.add_argument('--spec', type=Path, required=True)
    check = sub.add_parser('audit')
    check.add_argument('--freeze', type=Path, required=True)
    check.add_argument('--freeze-sha256', required=True)
    check.add_argument('--analysis', type=Path, required=True)
    for command in (freeze, check):
        command.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), 'Fresh output required')
    program = identity(__file__)
    try:
        if args.action == 'freeze':
            result = {'status': 'frozen', 'bindings': make_bindings(args.spec, require_fresh=True)}
        else:
            result = audit(args.freeze, args.freeze_sha256, args.analysis)
        for path, expected in FILES.items():
            need(digest(Path(path).read_bytes()) == expected, 'Input changed during supplement: ' + path)
        result.update(schemaVersion=1, auditor=program, inputFiles=dict(FILES), inputsUnchanged=True,
                      recordedUtc=datetime.now(timezone.utc).isoformat(),
                      workloadProcessesStarted=0)
        code = 0
    except (ValueError, KeyError, TypeError, IndexError, OSError, subprocess.SubprocessError, zipfile.BadZipFile, ET.ParseError) as error:
        result = {'schemaVersion': 1, 'status': 'failed', 'action': args.action, 'auditor': program,
                  'recordedUtc': datetime.now(timezone.utc).isoformat(),
                  'errorType': type(error).__name__, 'message': str(error), 'checkedInputFiles': dict(FILES), 'workloadProcessesStarted': 0}
        code = 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'output': str(args.output), 'sha256': digest(args.output.read_bytes())}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
