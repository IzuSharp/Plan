"""Run the exact prospective DB policy pair, retaining actual command exits."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path('/workspace/scratch/01c249676f47')
PLAN = ROOT / '.worktree/Perf-01-linux/Plan/ledger/evidence/batches/Perf-01'
DOCUMENT = PLAN / 'database-gc-fixed-before-pair-001.json'
EXPECTED = '21b8f09254b41cbfe46f817d3fb61c0360b1470323b5191ef56c92e73c7d22a9'
RECEIPT = ROOT / 'perf01-run/database-gc-fixed-before-pair-001-execution.json'

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
    finite_gate = doc['passed_finite_gate']
    assert digest(ROOT / '.worktree/Perf-01-linux/Plan' / finite_gate['repository_path']) == finite_gate['sha256']
    for path, expected in doc['required_source_and_metadata_sha256'].items():
        assert digest(path) == expected, path
    assert digest(doc['python']['executable']) == doc['python']['recorded_executable_sha256']
    driver = doc['immutable_measurement_driver']
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=driver['path'], text=True).strip() == driver['commit']
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=driver['path'])
    assert not RECEIPT.exists()
    for command in doc['commands']:
        assert not Path(command['output']).exists(), command['output']
    result = {'task': 'Perf-01', 'state': 'running', 'started_utc': utc(),
              'document': str(DOCUMENT), 'document_sha256': EXPECTED,
              'supervisor_source_sha256': digest(__file__), 'pid': os.getpid(),
              'cpu_affinity': sorted(os.sched_getaffinity(0)), 'commands': [],
              'formal_timing_eligible': False, 'duration_credit_seconds': 0}
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
        summary_path = Path(command['output']) / 'summary.json'
        summary = json.loads(summary_path.read_text())
        entry['summary_sha256'] = digest(summary_path)
        entry['summary_gate_passed'] = (summary.get('valid') is True and
                                        summary.get('qualifies_service_standard') is True and
                                        summary.get('scheduler_gc_policy_valid') is True and
                                        summary.get('scheduler_gc_policy', {}).get('mode') == command['policy'])
        save(RECEIPT, result)
        if not entry['summary_gate_passed']:
            result.update(state='failed-summary-gate', ended_utc=utc(), failed_command=command['id'])
            save(RECEIPT, result)
            return 1
    result.update(state='commands-completed-validation-pending', ended_utc=utc())
    save(RECEIPT, result)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
