"""Execute the exact reviewed DB calibration commands and preserve actual exits."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path('/workspace/scratch/01c249676f47')
PLAN = ROOT / '.worktree/Perf-01-linux/Plan/ledger/evidence/batches/Perf-01'
DOCUMENT = PLAN / 'database-gc-before-calibration-001.json'
EXPECTED = '06862edded915cc404d893972ce6b020088c6808ad9923c0fc74495921e32355'
RECEIPT = ROOT / 'perf01-run/database-gc-before-calibration-001-execution.json'

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def save(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    temporary.replace(path)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    assert 'NW_PERF01_GC_CONFIG' not in os.environ
    assert digest(DOCUMENT) == EXPECTED
    doc = json.loads(DOCUMENT.read_text())
    for path, expected in doc['required_source_and_metadata_sha256'].items():
        assert digest(path) == expected, path
    assert digest(doc['python']['executable']) == doc['python']['recorded_executable_sha256']
    policy = json.loads((ROOT / '.worktree/Perf-01-linux/Plan' / doc['database_amendment']['repository_path']).read_text())
    driver = policy['driver_path']
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=driver, text=True).strip() == doc['driver_commit']
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=driver)
    assert not RECEIPT.exists()
    for command in doc['commands']:
        assert not Path(command['output']).exists(), command['output']
    result = {'task': 'Perf-01', 'state': 'running', 'started_utc': utc(),
              'document': str(DOCUMENT), 'document_sha256': EXPECTED,
              'supervisor_source_sha256': digest(__file__), 'pid': os.getpid(),
              'cpu_affinity': sorted(os.sched_getaffinity(0)), 'commands': [], 'duration_credit_seconds': 0}
    save(RECEIPT, result)
    for command in doc['commands']:
        log = ROOT / 'perf01-run' / (command['id'] + '.log')
        entry = {'id': command['id'], 'argv': command['argv'], 'cwd': command['working_directory'],
                 'output': command['output'], 'started_utc': utc(), 'log': str(log), 'state': 'running'}
        result['commands'].append(entry)
        save(RECEIPT, result)
        print(json.dumps({'event': 'command-started', **entry}), flush=True)
        started = time.monotonic()
        with log.open('xb') as handle:
            child = subprocess.Popen(command['argv'], cwd=command['working_directory'], stdout=handle, stderr=subprocess.STDOUT)
            entry['pid'] = child.pid
            save(RECEIPT, result)
            while child.poll() is None:
                try:
                    child.wait(timeout=40)
                except subprocess.TimeoutExpired:
                    print(json.dumps({'event': 'supervision', 'id': command['id'], 'utc': utc(),
                                      'elapsed_seconds': time.monotonic() - started, 'pid': child.pid}), flush=True)
        entry.update(state='completed', ended_utc=utc(), exit_code=child.returncode,
                     elapsed_seconds=time.monotonic() - started, log_sha256=digest(log))
        save(RECEIPT, result)
        print(json.dumps({'event': 'command-ended', 'id': command['id'], 'exit_code': child.returncode}), flush=True)
        if child.returncode != 0:
            result.update(state='failed', ended_utc=utc(), failed_command=command['id'])
            save(RECEIPT, result)
            return child.returncode or 1
        selection_path = Path(command['selection_future'])
        controller_path = Path(command['controller_future'])
        selection = json.loads(selection_path.read_text())
        controller = json.loads(controller_path.read_text())
        entry.update(selection_sha256=digest(selection_path), controller_sha256=digest(controller_path))
        entry['selection_gate_passed'] = (controller.get('state') == 'completed' and
            selection.get('controller_sha256') == entry['controller_sha256'] and
            selection.get('database_amendment_sha256') == doc['database_amendment']['sha256'] and
            selection.get('scheduler_gc_policy_sha256') == policy['scheduler_gc_policy_sha256'] and
            selection.get('scheduler_gc_policy') == policy['scheduler_gc_policy'] and
            selection.get('fixed_long_rate_within_confirmed_capacity') is True and
            selection.get('long_rate') == policy['paired_long_rates_per_second'][command['provider']])
        save(RECEIPT, result)
        if not entry['selection_gate_passed']:
            result.update(state='failed-selection-gate', ended_utc=utc(), failed_command=command['id'])
            save(RECEIPT, result)
            return 1
    result.update(state='calibration-completed-noise-pending', ended_utc=utc())
    save(RECEIPT, result)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
