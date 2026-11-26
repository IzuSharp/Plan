#!/usr/bin/env python3
"""Finite offline plan controls; never execute a consumer or database.

The C=2, R=123 values are synthetic validation inputs, not a campaign choice.
Original plans are produced by the unchanged generator and never overwritten.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'source', 'generator', 'selector', 'work', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists(), 'Fresh control locations required'
    args.work.mkdir(parents=True)
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('load_selector', args.selector)
    selector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(selector)
    source = args.source.resolve()
    commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    tracked = {str(p.resolve()): sha(p) for p in (args.selector, args.generator, Path(__file__))}
    controls, invocations, observations = [], [], []

    def run(argv, expected_success=True):
        process = subprocess.run([str(x) for x in argv], capture_output=True, text=True)
        invocations.append({'argv': [str(x) for x in argv], 'exitCode': process.returncode,
                            'stdout': process.stdout, 'stderr': process.stderr})
        assert (process.returncode == 0) is expected_success, invocations[-1]
        return process

    def rejected(label, call):
        try:
            call()
        except (ValueError, KeyError, TypeError, IndexError, OSError):
            controls.append({'name': label, 'expected': 'rejected', 'passed': True})
            return
        raise AssertionError('Accepted negative control: ' + label)

    for provider in ('sqlite', 'postgresql'):
        for kind in ('baseline', 'final'):
            stem = provider + '-' + kind
            original = (args.work / (stem + '-original.json')).resolve()
            original_output = (args.work / (stem + '-original-never-executed')).resolve()
            derived = (args.work / (stem + '-derived.json')).resolve()
            derived_output = (args.work / (stem + '-derived-never-executed')).resolve()
            generate = [sys.executable, args.generator.resolve(), '--source', source, '--provider', provider,
                        '--lane', 'offered' if kind == 'baseline' else 'final',
                        '--before-dir', args.root / 'consumers' / ('row-' + provider + '-workload') / 'out',
                        '--candidate-dir', args.root / 'consumers' / ('command-' + provider + '-workload-01') / 'out',
                        '--dapper-dir', args.root / 'consumers' / ('dapper-matched-' + provider + '-01') / 'out',
                        '--concurrency', '2', '--rate', '123', '--queue-capacity', '64',
                        '--plan', original, '--output', original_output]
            generate += ['--sqlite-library', args.root / 'consumers/direct-native/libsqlite3.so'] if provider == 'sqlite' else [
                        '--postgres-bin', args.root / 'tools/postgres/install/bin']
            run(generate)
            tracked[str(original)] = sha(original)
            select = [sys.executable, args.selector.resolve(), '--input', original, '--input-sha256', sha(original),
                      '--generator', args.generator.resolve(), '--source-commit', commit, '--kind', kind,
                      '--plan', derived, '--output', derived_output]
            run(select)
            plan, result = selector.strict_json(original.read_bytes()), selector.strict_json(derived.read_bytes())
            details = selector.validate_source_plan(plan, original, kind)
            expected_cohorts = ['before', 'candidate'] if kind == 'baseline' else ['candidate', 'dapper']
            seconds = '120' if kind == 'baseline' else '1800'
            assert result['commands'][0] == plan['commands'][0]
            assert result['commands'][0]['timingRequested'] is False
            assert [x['cohort'] for x in result['commands'][1:]] == expected_cohorts
            assert all(selector.option(x['argv'], '--seconds') == seconds for x in result['commands'][1:])
            assert all(selector.option(x['argv'], '--rate') == '123.0' for x in result['commands'][1:])
            assert all(selector.option(x['argv'], '--concurrency') == '2' for x in result['commands'][1:])
            assert result['inputs'] == plan['inputs'] and result['longRunAcceptance'] is False
            assert result['derivedFrom']['plan']['sha256'] == sha(original)
            assert result['derivedFrom']['selector']['sha256'] == sha(args.selector)
            assert result['derivedFrom']['runnerSourceCommit'] == commit
            assert result['selection']['fixtureTimingCredit'] is False
            assert result['selection']['finalCreditRequestedFor'] == (expected_cohorts if kind == 'final' else [])
            assert not original_output.exists() and not derived_output.exists()
            controls.append({'name': stem + '/unchanged-generator-and-cli-positive', 'expected': 'accepted', 'passed': True})
            tracked[str(derived)] = sha(derived)
            observations.append({'kind': kind, 'provider': provider,
                                 'original': {'path': str(original), 'sha256': sha(original)},
                                 'derived': {'path': str(derived), 'sha256': sha(derived)},
                                 'measuredCohorts': expected_cohorts, 'seconds': int(seconds)})

            def mutate(label, fn):
                value = copy.deepcopy(plan)
                fn(value)
                rejected(stem + '/' + label, lambda: selector.validate_source_plan(value, original, kind))

            mutate('unknown-provider', lambda x: x.update(provider='other'))
            mutate('schema-boolean', lambda x: x.update(schemaVersion=True))
            mutate('wrong-lane', lambda x: x.update(lane='calibration'))
            mutate('invented-credit', lambda x: x.update(longRunAcceptance=True))
            mutate('extra-top-level-field', lambda x: x.update(extra='unbound'))
            mutate('missing-command', lambda x: x['commands'].pop())
            mutate('duplicate-command', lambda x: x['commands'].append(copy.deepcopy(x['commands'][-1])))
            mutate('wrong-order', lambda x: x['commands'].__setitem__(slice(1, 3), list(reversed(x['commands'][1:3]))))
            mutate('duplicate-cohort', lambda x: x['commands'][2].update(cohort='before'))
            mutate('unknown-cohort', lambda x: x['commands'][2].update(cohort='unknown'))
            mutate('fixture-counted', lambda x: x['commands'][0].update(timingRequested=True))
            mutate('fixture-phase', lambda x: x['commands'][0].update(phase='final'))
            mutate('fixture-invented-credit', lambda x: x['commands'][0].update(longRunAcceptance=True))
            mutate('fixture-loses-initialize', lambda x: x['commands'][0]['argv'].remove('--initialize'))
            mutate('fixture-wrong-binary', lambda x: x['commands'][0]['argv'].__setitem__(0, x['inputs']['consumers']['before']['path']))
            mutate('missing-consumer', lambda x: x['inputs']['consumers'].pop('before'))
            mutate('aliased-consumer', lambda x: x['inputs']['consumers'].update(before=x['inputs']['consumers']['candidate']))
            mutate('changed-executable-hash', lambda x: x['inputs']['consumers']['candidate'].update(sha256='0' * 64))
            mutate('changed-runner-hash', lambda x: x['inputs']['runner'].update(sha256='0' * 64))
            mutate('changed-manifest-hash', lambda x: x['inputs']['manifest'].update(sha256='0' * 64))
            mutate('extra-input-field', lambda x: x['inputs'].update(extra={'path': 'unbound'}))
            mutate('different-workload-case', lambda x: x['manifestCaseNames'].__setitem__(0, 'other'))
            mutate('different-row-count', lambda x: x['mixedDataset'].update(requestedRows=1))
            mutate('different-affinity', lambda x: x['affinity'].update(client='0-8'))
            mutate('different-source-directory', lambda x: x.update(sourceDirectory=str(args.work)))
            mutate('different-runner-argv', lambda x: x['runnerCommand'].__setitem__(0, 'other'))
            mutate('different-runner-input', lambda x: x['runnerCommand'].__setitem__(-3, str(args.work / 'other.json')))
            mutate('different-comparison-role', lambda x: x['commands'][1].update(comparisonRole='candidate'))
            mutate('different-timeout', lambda x: x['commands'][1].update(timeoutSeconds=100))
            mutate('extra-command-field', lambda x: x['commands'][1].update(extra=True))
            mutate('different-command-name', lambda x: x['commands'][1].update(name='renamed'))
            mutate('different-command-cpus', lambda x: x['commands'][1].update(cpus='0-8'))
            for key, values in (('--seconds', ['0', '120', '1801']), ('--rate', ['NaN', '0', '-1', '1000001', '123']),
                                ('--concurrency', ['0', '257', '02']), ('--queue-capacity', ['0', '65537']),
                                ('--rows', ['1']), ('--warmup', ['0']), ('--idle-seconds', ['1'])):
                for value in values:
                    mutate(key + '=' + value, lambda x, k=key, v=value:
                           x['commands'][1]['argv'].__setitem__(x['commands'][1]['argv'].index(k) + 1, v))
            mutate('extra-argv', lambda x: x['commands'][1]['argv'].extend(['--unknown', 'yes']))
            mutate('different-second-cohort-rate', lambda x:
                   x['commands'][2]['argv'].__setitem__(x['commands'][2]['argv'].index('--rate') + 1, '124.0'))
            if provider == 'sqlite':
                mutate('changed-native-hash', lambda x: x['inputs']['sqliteLibrary'].update(sha256='0' * 64))
                mutate('different-database-path', lambda x: x.update(connection=str(args.work / 'shared.sqlite')))
            else:
                mutate('changed-postgres-tool-hash', lambda x: x['inputs']['postgresTools']['postgres'].update(sha256='0' * 64))
                mutate('different-database-path', lambda x: x['postgres'].update(data=str(args.work / 'shared-pg')))
                mutate('different-postgres-concurrency', lambda x: x['postgres'].update(maxClientConcurrency=4))
                mutate('different-postgres-connections', lambda x: x['postgres'].update(maxConnections=3))

            # CLI rejection paths are checked with fresh targets. They do not
            # alter the original/derived positive plans or create evidence dirs.
            run(select, expected_success=False)
            controls.append({'name': stem + '/refuse-existing-plan', 'expected': 'rejected', 'passed': True})
            for label, option, replacement in [('wrong-plan-sha', '--input-sha256', '0' * 64),
                                               ('wrong-source-commit', '--source-commit', 'HEAD')]:
                bad = list(select)
                bad[bad.index('--plan') + 1] = args.work / (stem + '-' + label + '.json')
                bad[bad.index(option) + 1] = replacement
                run(bad, expected_success=False)
                assert not Path(bad[bad.index('--plan') + 1]).exists()
                controls.append({'name': stem + '/' + label, 'expected': 'rejected', 'passed': True})
            existing_output = args.work / (stem + '-existing-output')
            existing_output.mkdir()
            bad = list(select)
            bad[bad.index('--plan') + 1] = args.work / (stem + '-existing-output.json')
            bad[bad.index('--output') + 1] = existing_output
            run(bad, expected_success=False)
            assert not Path(bad[bad.index('--plan') + 1]).exists() and list(existing_output.iterdir()) == []
            controls.append({'name': stem + '/refuse-existing-output', 'expected': 'rejected', 'passed': True})

    rejected('strict-json/duplicate-key', lambda: selector.strict_json('{"lane":"final","lane":"offered"}'))
    for token in ('NaN', 'Infinity', '-Infinity'):
        rejected('strict-json/nonfinite-' + token, lambda x=token: selector.strict_json('{"rate":' + x + '}'))
    for path, expected in tracked.items():
        assert sha(path) == expected, 'Changed input/plan: ' + path
    receipt = {'schemaVersion': 1, 'scope': __doc__, 'sourceCommit': commit, 'sourceHashes': tracked,
               'workloadProcessesStarted': 0, 'originalPlansUnchanged': True, 'passed': True,
               'count': len(controls), 'controls': controls, 'plans': observations, 'offlineInvocations': invocations}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'passed': True, 'count': len(controls), 'output': str(args.output)}))


if __name__ == '__main__':
    main()
