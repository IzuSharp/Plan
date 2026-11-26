#!/usr/bin/env python3
"""Derive fresh local plans from the pinned continuation-4 plan generator.

baseline: original offered/30-second input -> before/candidate at 120 seconds.
final: original final/1800-second input -> candidate/Dapper at 1800 seconds.
The ordinary candidate fixture remains first, outside timing. No execution.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shlex
import subprocess
import sys

GENERATOR_SHA256 = '68deb860bd8ae1f0f268220e5c3b72606ff666b08a7511e1245d750b3fb1cc78'
COHORTS = ('before', 'candidate', 'dapper')
DATASET = {'tenants': 8, 'ordersPerTenant': 1024, 'requestedRows': 32, 'batchRows': 32}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def strict_json(data):
    return json.loads(data, object_pairs_hook=strict_object,
                      parse_constant=lambda token: (_ for _ in ()).throw(ValueError('Non-finite JSON: ' + token)))


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def identity(entry):
    require(isinstance(entry, dict) and set(entry) == {'path', 'sha256'}, 'Malformed input identity')
    path = Path(entry['path'])
    require(path.is_absolute() and path.is_file() and digest(path) == entry['sha256'], 'Changed/missing input: ' + str(path))
    return path


def option(argv, key):
    require(argv.count(key) == 1 and argv.index(key) + 1 < len(argv), 'Missing/duplicate option: ' + key)
    return argv[argv.index(key) + 1]


def validate_source_plan(plan, input_path, kind):
    provider = plan.get('provider')
    require(provider in ('sqlite', 'postgresql'), 'Unknown provider')
    lane = 'offered' if kind == 'baseline' else 'final'
    seconds = 30 if kind == 'baseline' else 1800
    base_keys = {'schemaVersion', 'provider', 'lane', 'scope', 'longRunAcceptance', 'sourceDirectory',
                 'inputs', 'manifestCaseNames', 'mixedDataset', 'phaseDataset', 'affinity', 'hostAdmission',
                 'commands', 'runnerCommand'}
    require(set(plan) == base_keys | ({'postgres'} if provider == 'postgresql' else {'connection'}),
            'Plan is not the unchanged pinned generator format')
    require(type(plan['schemaVersion']) is int and plan['schemaVersion'] == 1 and plan['lane'] == lane
            and plan['longRunAcceptance'] is False, 'Wrong source lane/schema/credit')
    require(plan['mixedDataset'] == DATASET
            and plan['phaseDataset'] == {'tenants': 2, 'rowsPerTenant': 1000, 'batchRows': 32}, 'Dataset changed')
    require(plan['affinity'] == {'client': '0-3', 'postgres': '4-7', 'observer': '8'}, 'Affinity changed')
    require(plan['scope'] == 'Local serial observations; before is baseline; existing analyzer decides final four-cell credit'
            and plan['hostAdmission'] == 'not established by plan generation; observe actual host and cgroup visibility',
            'Original scope/admission declaration changed')
    inputs = plan['inputs']
    require(set(inputs) == {'runner', 'manifest', 'consumers', 'sqliteLibrary'} |
            ({'postgresTools'} if provider == 'postgresql' else set()), 'Unexpected input set')
    source = Path(plan['sourceDirectory'])
    require(source.is_absolute(), 'Source checkout must be absolute')
    runner, manifest_path = identity(inputs['runner']), identity(inputs['manifest'])
    require(runner == source / 'benchmarks/db-perf/run.py'
            and manifest_path == source / 'benchmarks/db-perf/workload/queries-v3.json', 'Source paths differ')
    manifest = strict_json(manifest_path.read_bytes())
    names = [x['name'] for x in manifest['queries']]
    require(len(names) == len(set(names)) == 35 and manifest['schemaVersion'] == 3
            and all(isinstance(name, str) and name and ',' not in name for name in names)
            and plan['manifestCaseNames'] == names and all(manifest['dataset'][k] == v for k, v in DATASET.items()),
            'Manifest/cases differ')
    require(set(inputs['consumers']) == set(COHORTS), 'Source plan must declare all three distinct cohorts')
    binaries = {name: identity(inputs['consumers'][name]) for name in COHORTS}
    require(all(path.name == ('DbPerf.Dapper' if name == 'dapper' else 'DbPerf.Korda')
                for name, path in binaries.items()), 'Unexpected workload executable')
    require(len({str(x.resolve()) for x in binaries.values()}) == 3, 'Cohorts alias one executable path')
    native_args = []
    if provider == 'sqlite':
        native_args = ['--native-library', str(identity(inputs['sqliteLibrary']))]
    else:
        require(inputs['sqliteLibrary'] is None and set(inputs['postgresTools']) == {'initdb', 'postgres', 'pg_isready', 'psql'},
                'Unexpected PostgreSQL tool/native set')
        pg = plan['postgres']
        require(set(pg) == {'bin', 'data', 'cpus', 'maxConnections', 'maxClientConcurrency'}, 'Unexpected PostgreSQL controls')
        for name, entry in inputs['postgresTools'].items():
            require(identity(entry) == Path(pg['bin']) / name, 'PostgreSQL tool path differs')
    commands = plan['commands']
    require(isinstance(commands, list) and len(commands) == 4, 'Exactly one fixture and three source commands required')
    require([x['cohort'] for x in commands] == ['candidate', *COHORTS], 'Missing/duplicate/reordered cohorts')
    concurrency_text = option(commands[1]['argv'], '--concurrency')
    concurrency = int(concurrency_text)
    require(str(concurrency) == concurrency_text and 1 <= concurrency <= 256, 'Invalid concurrency')
    rate_text = option(commands[1]['argv'], '--rate')
    rate = float(rate_text)
    require(math.isfinite(rate) and 0 < rate <= 1_000_000 and str(rate) == rate_text, 'Invalid rate')
    queue_text = option(commands[1]['argv'], '--queue-capacity')
    queue = int(queue_text)
    require(str(queue) == queue_text and 1 <= queue <= 65536, 'Invalid queue capacity')
    for index, item in enumerate(commands):
        require(set(item) == {'name', 'cohort', 'phase', 'timingRequested', 'longRunAcceptance',
                             'comparisonRole', 'argv', 'cpus', 'timeoutSeconds'}, 'Unexpected command fields')
        cohort = item['cohort']
        fixture = index == 0
        name = 'fixture-mixed' if fixture else cohort + '-c' + concurrency_text
        expected = [str(binaries[cohort]), '--connection', '{connection}', '--case', 'mixed',
                    '--cases', ','.join(names), '--mode', 'prepared', '--session', 'persistent',
                    '--concurrency', '1' if fixture else concurrency_text, '--rows', '32', '--batch-rows', '32',
                    '--tenants', '8', '--orders-per-tenant', '1024', '--warmup', '64', '--queue-capacity', queue_text]
        if cohort == 'dapper':
            expected += native_args
        if fixture:
            expected += ['--initialize', '--operations', '0']
        else:
            expected += ['--verify', '--seconds', str(seconds), '--idle-seconds', '15' if lane == 'final' else '0',
                         '--output', '{output}/' + name + '.json', '--rate', rate_text]
        require(item['argv'] == expected and item['name'] == name, 'Unexpected command arguments or name')
        require(item['phase'] == ('fixture' if fixture else lane) and item['timingRequested'] is (not fixture)
                and item['longRunAcceptance'] is False and item['cpus'] == '0-3'
                and item['comparisonRole'] == ('baseline' if cohort == 'before' else cohort)
                and type(item['timeoutSeconds']) is int and item['timeoutSeconds'] == max(600, (0 if fixture else seconds) + 315),
                'Command boundary/credit/timeout differs')
    invocation = plan['runnerCommand']
    require(isinstance(invocation, list) and len(invocation) == 8, 'Unexpected runner command')
    original_output = Path(invocation[-1])
    require(original_output.is_absolute() and invocation == ['taskset', '-c', '8', 'python3', str(runner),
            str(input_path), '--output', str(original_output)], 'Runner identity/path differs')
    if provider == 'sqlite':
        require(plan['connection'] == str(original_output / 'fixture.sqlite'), 'SQLite output identity differs')
    else:
        require(pg['data'] == str(original_output / 'pgdata') and pg['cpus'] == '4-7'
                and type(pg['maxClientConcurrency']) is int and pg['maxClientConcurrency'] == concurrency
                and type(pg['maxConnections']) is int and pg['maxConnections'] == max(64, concurrency + 8),
                'PostgreSQL output/pool identity differs')
    return {'provider': provider, 'lane': lane, 'seconds': seconds, 'source': source,
            'runner': runner, 'manifest': manifest_path, 'originalOutput': original_output,
            'concurrency': concurrency, 'rate': rate, 'queueCapacity': queue}


def derive(plan, details, kind, new_plan, new_output, derived_from):
    selected = ('before', 'candidate') if kind == 'baseline' else ('candidate', 'dapper')
    seconds = 120 if kind == 'baseline' else 1800
    result = copy.deepcopy(plan)
    result['commands'] = [x for x in result['commands'] if x['phase'] == 'fixture' or x['cohort'] in selected]
    require(len(result['commands']) == 3 and [x['cohort'] for x in result['commands'][1:]] == list(selected),
            'Derived cohorts differ')
    for item in result['commands'][1:]:
        item['argv'][item['argv'].index('--seconds') + 1] = str(seconds)
        item['timeoutSeconds'] = max(600, seconds + 315)
    if details['provider'] == 'sqlite':
        result['connection'] = str(new_output / 'fixture.sqlite')
    else:
        result['postgres']['data'] = str(new_output / 'pgdata')
    result['runnerCommand'][-3] = str(new_plan)
    result['runnerCommand'][-1] = str(new_output)
    result['scope'] = 'Derived local ' + kind + ' plan; no execution, host admission or acceptance is granted'
    result['derivedFrom'] = derived_from
    result['selection'] = {'kind': kind, 'measuredCohorts': list(selected), 'measuredSecondsPerCohort': seconds,
                           'fixturePreservedFirst': True, 'fixtureTimingCredit': False,
                           'sourceInputCohortsRetainedForIdentity': list(COHORTS),
                           'concurrency': details['concurrency'], 'rate': details['rate'],
                           'queueCapacity': details['queueCapacity'],
                           'finalCreditRequestedFor': list(selected) if kind == 'final' else [],
                           'transformations': ['Select explicitly named measured cohorts while retaining the original fixture',
                                               'Set measured duration to ' + str(seconds) + ' seconds',
                                               'Rebind plan, result and database locations to a fresh output directory']}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--input-sha256', required=True)
    parser.add_argument('--generator', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--kind', choices=('baseline', 'final'), required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    input_path, new_plan, output = args.input.resolve(strict=True), args.plan.resolve(), args.output.resolve()
    require(not new_plan.exists() and not output.exists() and not new_plan.is_relative_to(output), 'Fresh separate plan/output required')
    require(new_plan != input_path and len(args.input_sha256) == 64 and digest(input_path) == args.input_sha256,
            'Original input SHA-256 differs')
    generator = args.generator.resolve(strict=True)
    require(digest(generator) == GENERATOR_SHA256, 'Generator source is not the pinned continuation-4 version')
    plan = strict_json(input_path.read_bytes())
    details = validate_source_plan(plan, input_path, args.kind)
    require(output != details['originalOutput'] and not output.is_relative_to(details['originalOutput'])
            and not new_plan.is_relative_to(details['originalOutput']), 'Derived output overlaps original evidence')
    source = details['source']
    commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', '--verify', args.source_commit + '^{commit}'], text=True).strip()
    require(commit == args.source_commit and len(commit) == 40, 'Use one exact full source commit')
    head = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    require(head == commit, 'Source checkout is not at the declared commit')
    tree = subprocess.check_output(['git', '-C', str(source), 'rev-parse', commit + '^{tree}'], text=True).strip()
    for path in (details['runner'], details['manifest']):
        relative = str(path.relative_to(source))
        content = subprocess.check_output(['git', '-C', str(source), 'show', commit + ':' + relative])
        require(hashlib.sha256(content).hexdigest() == digest(path), 'Working source differs from the committed input: ' + relative)
    derived_from = {'plan': {'path': str(input_path), 'sha256': args.input_sha256},
                    'generator': {'path': str(generator), 'sha256': GENERATOR_SHA256},
                    'selector': {'path': str(Path(__file__).resolve()), 'sha256': digest(__file__)},
                    'runnerSourceCommit': commit, 'runnerSourceTree': tree,
                    'consumerIdentityScope': 'Consumer/native/package freeze is separate; binary hashes are inherited unchanged from the input plan',
                    'originalLane': plan['lane'], 'originalSecondsPerCohort': details['seconds']}
    result = derive(plan, details, args.kind, new_plan, output, derived_from)
    # Import the already hash-verified runner only for its pure plan validator.
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('frozen_local_runner', details['runner'])
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.validate_plan(result, output)
    # Recheck every bound executable/native/tool/source after validation. The
    # original plan and generator are immutable even when validation fails.
    validate_source_plan(plan, input_path, args.kind)
    require(digest(input_path) == args.input_sha256 and digest(generator) == GENERATOR_SHA256,
            'Original inputs changed during derivation')
    require(digest(__file__) == derived_from['selector']['sha256'], 'Selector changed during derivation')
    require(subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() == commit,
            'Source checkout moved during derivation')
    new_plan.parent.mkdir(parents=True, exist_ok=True)
    with new_plan.open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'plan': str(new_plan), 'sha256': digest(new_plan),
                      'cohorts': result['selection']['measuredCohorts'],
                      'seconds': result['selection']['measuredSecondsPerCohort'], 'workloadProcessesStarted': 0}))
    print(shlex.join(result['runnerCommand']))


if __name__ == '__main__':
    main()
