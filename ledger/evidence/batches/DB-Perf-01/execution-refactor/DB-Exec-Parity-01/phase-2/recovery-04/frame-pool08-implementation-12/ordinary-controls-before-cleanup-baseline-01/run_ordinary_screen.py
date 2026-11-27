#!/usr/bin/env python3
"""Finite local frame-pool08 related32 screen with actual input binding and a retained failure lease."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/recovery'))
import run_verified_mixed_cell08 as cell

DRIVER = ROOT / 'local-tools/run_causal_ab08.py'
SCENARIOS = ['related:32:prepared']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--quiet', type=Path, required=True)
    args = parser.parse_args()
    output = cell.contained(args.output)
    cell.require(not output.exists(), 'Fresh screen output required')
    quiet = cell.read(args.quiet)
    cell.require(quiet.get('quietAcknowledged') is True, 'Explicit peer quiet acknowledgment required')
    output.mkdir(parents=True)
    state = {'task': 'DB-Exec-Parity-01', 'startedUtc': cell.utc(), 'stage': 'created',
             'quiet': quiet, 'quietSha256': cell.sha(args.quiet), 'controllerSha256': cell.sha(__file__),
             'driverSha256': cell.sha(DRIVER), 'wrapperSha256': cell.sha(cell.__file__),
             'ordinaryTiming': True, 'finalCredit': False, 'providers': []}
    child = None
    lease = None
    lock = (cell.LOCAL / 'verified-mixed-cell.lock').open('a+')
    previous_term = signal.signal(signal.SIGTERM, cell.interrupt_signal)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        cell.require_unblocked()
        for provider in ('sqlite', 'postgresql'):
            out = output / provider
            record = {'provider': provider, 'startedUtc': cell.utc(), 'stage': 'snapshot-before'}
            state['providers'].append(record)
            cell.atomic(output / 'resume.json', state)
            # before is the actual fixture initializer, not an extra measured route.
            before = {variant: cell.input_snapshot(provider, variant)
                      for variant in ('before', 'integrated05', 'candidate', 'dapper')}
            cell.atomic(output / (provider + '-inputs-before.json'), before)
            scenarios = SCENARIOS
            argv = [sys.executable, str(DRIVER), '--provider', provider,
                    '--baseline', str(cell.app_path(provider, 'integrated05') / 'out/DbPerf.Korda'),
                    '--candidate', str(cell.app_path(provider, 'candidate') / 'out/DbPerf.Korda'),
                    '--dapper', str(cell.app_path(provider, 'dapper') / 'out/DbPerf.Dapper'),
                    '--operations', '2048', '--warmup', '128', '--rounds', '2', '--output', str(out)]
            for scenario in scenarios:
                argv += ['--scenario', scenario]
            record.update(stage='running', argv=argv)
            lease = {'task': 'DB-Exec-Parity-01', 'attemptOutput': str(output), 'provider': provider,
                     'stage': 'causal-screen-launch-intent', 'createdUtc': cell.utc(),
                     'controllerIdentity': cell.current_process_identity(os.getpid()),
                     'reason': 'Retain until exact observer/command/server retirement is proven; no automatic recovery deletion'}
            cell.atomic(cell.BLOCKER, lease)
            with (output / (provider + '.controller.log')).open('x') as log:
                child = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                lease.update(stage='causal-screen-running', driverIdentity=cell.current_process_identity(child.pid))
                cell.atomic(cell.BLOCKER, lease)
                cell.atomic(output / 'resume.json', state)
                record['exitCode'] = child.wait()
            child = None
            cell.require(record['exitCode'] == 0, 'Causal driver failed; preserve its evidence and lease')
            plan = cell.read(out.with_suffix('.plan.json'))
            runner = cell.read(out / 'runner.json')
            retired = cell.read(out / 'observer-adapter-retirement.json')
            cell.require(plan['driverSha256'] == state['driverSha256'], 'Driver changed before launch')
            cell.require(plan['observerSha256'] == cell.ADAPTER_SHA == runner['observerAdapter']['adapterSha256'],
                         'Actual observer differs from the planned reviewed observer')
            cell.require(runner['planSha256'] == cell.sha(out.with_suffix('.plan.json')),
                         'Executed plan identity mismatch')
            cell.require(retired['passed'] and retired['completed'] and retired['sourceIdentitiesUnchanged'],
                         'Observer did not retire cleanly')
            for item in plan['commands']:
                command = cell.read(out / (item['name'] + '.command.json'))
                cell.require(command['success'] and command['exitCode'] == 0 and not command['timedOut']
                             and command['observerErrors'] == [], 'A command did not retire cleanly')
            if provider == 'postgresql':
                owner = cell.read(out / 'postgres-owner.json')
                cell.require(owner['exitCode'] == 0 and not any(k in owner for k in
                             ('error', 'finalSampleError', 'shutdownError', 'cpuGroupError')),
                             'PostgreSQL retirement is unproven')
            cell.require(cell.read(cell.BLOCKER)['attemptOutput'] == str(output), 'Lease identity changed')
            cell.atomic(output / (provider + '-retirement-lease.json'), dict(lease, stage='clean-retirement-confirmed'))
            cell.BLOCKER.unlink()
            lease = None
            after = {variant: cell.input_snapshot(provider, variant) for variant in before}
            cell.atomic(output / (provider + '-inputs-after.json'), after)
            for variant in before:
                cell.require(before[variant]['identity'] == after[variant]['identity']
                             and before[variant]['identitySha256'] == after[variant]['identitySha256'],
                             'Input changed during the ordinary screen')
            cell.require(cell.sha(__file__) == state['controllerSha256']
                         and cell.sha(DRIVER) == state['driverSha256']
                         and cell.sha(cell.__file__) == state['wrapperSha256']
                         and cell.sha(args.quiet) == state['quietSha256'], 'Screen control identity changed')
            summary = cell.read(out / 'summary.json')
            cell.require(summary['passed'] and summary['ordinaryTiming'] and not summary['newFinalCellCredit'],
                         'Ordinary business validation did not pass')
            record.update(stage='completed', passed=True, finishedUtc=cell.utc(),
                          summarySha256=cell.sha(out / 'summary.json'), processes=len(summary['records']))
            cell.atomic(output / 'resume.json', state)
            print(json.dumps(record), flush=True)
        state.update(stage='completed', passed=True, finishedUtc=cell.utc())
        cell.atomic(output / 'resume.json', state)
    except BaseException as error:
        if child is not None and child.poll() is None:
            try:
                os.killpg(child.pid, signal.SIGINT)
                child.wait(timeout=45)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                pass
        if lease is not None:
            cell.atomic(cell.BLOCKER, dict(lease, stage='blocked-pending-independent-review',
                        failure={'type': type(error).__name__, 'message': str(error)}))
        state.update(stage='failed', passed=False, finishedUtc=cell.utc(),
                     error={'type': type(error).__name__, 'message': str(error)})
        cell.atomic(output / 'resume.json', state)
        raise
    finally:
        signal.signal(signal.SIGTERM, previous_term)
        lock.close()


if __name__ == '__main__':
    main()
