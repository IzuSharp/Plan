#!/usr/bin/env python3
"""Serial, fail-closed orchestration of independently validated local cells."""
from pathlib import Path
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import shutil
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / 'experiments/recovery/run_verified_mixed_cell.py'

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()

def save(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)

def main():
    plan_path = Path(sys.argv[1]).resolve()
    plan = json.loads(plan_path.read_text())
    assert plan_path.is_relative_to(ROOT)
    state_path = plan_path.with_suffix('.resume.json')
    assert not state_path.exists(), 'A new series needs a fresh identity; never overwrite prior attempts'
    state = {'task': 'DB-Exec-Parity-01', 'startedUtc': now(), 'stage': 'created',
             'planSha256': sha(plan_path), 'controllerSha256': sha(__file__),
             'cells': [], 'finalCredit': False, 'quietAcknowledged': plan['quietAcknowledged']}
    save(state_path, state)
    child = None
    def interrupted(signum, frame):
        raise InterruptedError('Series received signal ' + str(signum))
    previous = signal.signal(signal.SIGTERM, interrupted)
    lock = (ROOT / 'experiments/recovery/verified-series.lock').open('a+')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for entry in plan['cells']:
            assert sha(plan_path) == state['planSha256']
            assert sha(__file__) == state['controllerSha256']
            assert sha(WRAPPER) == plan['wrapperSha256']
            output = Path(entry['output']).resolve()
            assert output.is_relative_to(ROOT)
            record = {'id': entry['id'], 'output': str(output), 'startedUtc': now()}
            state.update(stage='cell', currentCell=entry['id'])
            state['cells'].append(record)
            save(state_path, state)
            if entry.get('completedValidationSha256'):
                assert sha(output / 'validation.json') == entry['completedValidationSha256']
                record.update(reusedCompletedEvidence=True, exitCode=0)
            else:
                assert not output.exists()
                assert shutil.disk_usage(ROOT).free >= plan.get('minimumFreeBytes', 300_000_000), 'Insufficient free space for the next cell'
                argv = [sys.executable, str(WRAPPER), entry['provider'], entry['variant'],
                        '--kind', entry['kind'], '--seconds', str(entry['seconds']),
                        '--rate', str(entry['rate']), '--queue', str(entry.get('queue', 64)),
                        '--idle', str(entry.get('idle', 5)), '--output', str(output)]
                if entry.get('freeze'):
                    argv += ['--freeze', entry['freeze']]
                record['argv'] = argv
                save(state_path, state)
                log_path = plan_path.parent / (entry['id'] + '.controller.log')
                with log_path.open('x') as log:
                    child = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                    record['wrapperPid'] = child.pid
                    save(state_path, state)
                    record['exitCode'] = child.wait()
                child = None
                record.update(log=str(log_path), logSha256=sha(log_path))
                assert record['exitCode'] == 0, 'Cell failed; raw evidence retained: ' + entry['id']
            validation_path = output / 'validation.json'
            result = json.loads(validation_path.read_text())
            assert sha(plan_path) == state['planSha256']
            assert sha(__file__) == state['controllerSha256']
            assert sha(WRAPPER) == plan['wrapperSha256']
            snapshot_path = output / 'snapshot-before.json'
            assert sha(snapshot_path) == result['snapshotBeforeSha256']
            snapshot = json.loads(snapshot_path.read_text())
            assert snapshot['identity']['variant'] == entry['variant']
            assert snapshot['identity']['provider'] == entry['provider']
            identity_hash = hashlib.sha256(json.dumps(snapshot['identity'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            assert identity_hash == snapshot['identitySha256'] == result['inputIdentitySha256']
            assert result['passed'] is True and result['kind'] == entry['kind']
            assert result['conditions']['provider'] == entry['provider']
            assert result['conditions']['seconds'] == entry['seconds'] and result['conditions']['rate'] == entry['rate']
            assert result['conditions']['queue'] == entry.get('queue', 64)
            assert result['conditions']['idle'] == entry.get('idle', 5)
            assert result['prePostInputIdentitiesEqual'] is True
            counts = result['normalized']['counts']
            assert counts['failed'] == 0 and result['normalized']['fullCaseCoverage'] is True
            record.update(finishedUtc=now(), passed=True, validationSha256=sha(validation_path), counts=counts,
                          successOpsPerSecond=result['normalized']['successOpsPerSecond'],
                          cpuSecondsPerSuccess=result['resources']['clientCpuSecondsPerSuccess'],
                          managedBytesPerSuccess=result['resources']['managedBytesPerSuccess'])
            save(state_path, state)
            print(json.dumps(record), flush=True)
        state.update(stage='completed', passed=True, finishedUtc=now())
        save(state_path, state)
        return 0
    except BaseException as error:
        if child is not None and child.poll() is None:
            child.send_signal(signal.SIGTERM)
            try:
                child.wait(timeout=55)
            except subprocess.TimeoutExpired:
                state['cleanupUnproven'] = True
        state.update(stage='failed', passed=False, finishedUtc=now(), error={'type': type(error).__name__, 'message': str(error)})
        save(state_path, state)
        raise
    finally:
        signal.signal(signal.SIGTERM, previous)
        lock.close()

if __name__ == '__main__':
    raise SystemExit(main())
