#!/usr/bin/env python3
"""Prepare eight actual inputs and two six-process plans; never run a workload."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

import run_ordinary_screen as screen

cell = screen.cell
PROVIDERS = ('sqlite', 'postgresql')
VARIANTS = ('before', 'ownership05', 'candidate', 'dapper')
EXPECTED = {
    'controller': '4801dcf544b850b3a8fe2c2a3b869d58e8602811c6547c304081bdc70c30b09b',
    'wrapper': '8c73d6eadc607308af71416427c5b8989fa3a7deca2600117254458aea32f643',
    'driver': 'ac7750f1ac24f77ef877e71a5e7eb4d137272313fc6e9cd1432fba233d8cbc43',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = cell.contained(args.output)
    cell.require(not output.exists(), 'Fresh preparation output required')
    output.mkdir(parents=True)
    state = {'task': 'DB-Exec-Parity-01', 'stage': 'created', 'passed': False,
             'workloadExecuted': False, 'databaseStarted': False, 'buildStarted': False,
             'formalFreezeCreated': False, 'ordinaryTimingCredit': False, 'finalCredit': False,
             'inputs': {}, 'plans': {}, 'scope': 'Preparation only; the actual controller repeats pre/post input snapshots.'}
    cell.atomic(output / 'resume.json', state)
    try:
        sources = {'controller': Path(screen.__file__), 'wrapper': Path(cell.__file__), 'driver': screen.DRIVER}
        for name, path in sources.items():
            cell.require(cell.sha(path) == EXPECTED[name], 'Reviewed source changed: ' + name)
        state['sourceSha256'] = {name: cell.sha(path) for name, path in sources.items()}
        state['prepareHelperSha256'] = cell.sha(__file__)
        cell.runtime_identity()
        for provider in PROVIDERS:
            snapshots = {variant: cell.input_snapshot(provider, variant) for variant in VARIANTS}
            cell.require(snapshots['candidate']['identity']['family'] == 'frame-pool08', 'Wrong candidate family')
            for variant, version in [('ownership05', '0.1.0-parity05.2'), ('candidate', '0.1.0-parity08.1')]:
                cell.require(snapshots[variant]['identity']['expectedResultIdentity']['packageVersion'] == version,
                             'Unexpected provider package version: ' + provider + '/' + variant)
            cell.require(snapshots['ownership05']['identity']['expectedResultIdentity']['native']['sha256'] ==
                         snapshots['candidate']['identity']['expectedResultIdentity']['native']['sha256'],
                         'The causal screen requires the same native image')
            cell.atomic(output / (provider + '-inputs.json'), snapshots)
            state['inputs'][provider] = {key: value['identitySha256'] for key, value in snapshots.items()}
            state['stage'] = 'inputs-' + provider
            cell.atomic(output / 'resume.json', state)
        for provider in PROVIDERS:
            target = output / provider
            argv = [sys.executable, str(screen.DRIVER), '--prepare-only', '--provider', provider,
                    '--baseline', str(cell.app_path(provider, 'ownership05') / 'out/DbPerf.Korda'),
                    '--candidate', str(cell.app_path(provider, 'candidate') / 'out/DbPerf.Korda'),
                    '--dapper', str(cell.app_path(provider, 'dapper') / 'out/DbPerf.Dapper'),
                    '--scenario', 'related:32:prepared', '--operations', '2048', '--warmup', '128',
                    '--rounds', '2', '--output', str(target)]
            with (output / (provider + '-prepare.log')).open('x') as stream:
                subprocess.run(argv, check=True, stdout=stream, stderr=subprocess.STDOUT)
            plan_path = target.with_suffix('.plan.json')
            plan = cell.read(plan_path)
            cell.require(not target.exists(), 'Prepare-only unexpectedly created a measurement directory')
            commands = plan['commands']
            cell.require(len(commands) == 7 and commands[0]['name'] == 'initialize', 'Expected six measured processes plus initializer')
            cell.require(commands[0]['argv'][0] == str(cell.app_path(provider, 'before') / 'out/DbPerf.Korda'),
                         'Actual initializer must be the before consumer')
            order = [(item['round'], item['route'], item['case'], item['rows'], item['mode']) for item in commands[1:]]
            expected_order = [(round_, route, 'related', 32, 'prepared') for round_, routes in
                              [(1, ['baseline', 'candidate', 'dapper']), (2, ['dapper', 'candidate', 'baseline'])]
                              for route in routes]
            cell.require(order == expected_order, 'Related32 two-round reversed order changed')
            for item in commands[1:]:
                args_ = item['argv']
                for flag, value in [('--operations', '2048'), ('--warmup', '128'), ('--concurrency', '1'),
                                    ('--session', 'persistent'), ('--batch-rows', '32'), ('--idle-seconds', '5')]:
                    cell.require(args_[args_.index(flag) + 1] == value, 'Prepared configuration differs: ' + flag)
                cell.require(item['phase'] == 'ordinary-causal-ab' and item['cpus'] == '0-3'
                             and '--allocation-profile' not in args_ and args_.count('--verify') == 1,
                             'Expected unchanged related32 mixed-contract preflight and ordinary mode')
            state['plans'][provider] = {'path': str(plan_path), 'sha256': cell.sha(plan_path),
                                        'businessProcesses': 6, 'initializers': 1}
            cell.atomic(output / 'resume.json', state)
        for name, path in sources.items():
            cell.require(cell.sha(path) == state['sourceSha256'][name], 'Source changed during prepare-only: ' + name)
        state.update(stage='completed', passed=True, actualInputIdentities=8, businessProcesses=12, initializers=2)
        cell.atomic(output / 'resume.json', state)
        print(json.dumps(state))
    except BaseException as error:
        state.update(stage='failed', passed=False, error={'type': type(error).__name__, 'message': str(error)})
        cell.atomic(output / 'resume.json', state)
        raise


if __name__ == '__main__':
    main()
