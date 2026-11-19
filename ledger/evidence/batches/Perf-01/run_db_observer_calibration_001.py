"""Execute the exact reviewed DB calibration commands and preserve actual exits."""
import argparse
import importlib.util
import datetime
import re
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def save(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    temporary.replace(path)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def confined(root, value):
    value = Path(value)
    result = (value if value.is_absolute() else root / value).resolve()
    assert result.is_relative_to(root), 'Path escapes the declared workspace root'
    return result


def fresh(root, value):
    value = Path(value)
    candidate = value if value.is_absolute() else root / value
    assert not os.path.lexists(candidate), 'Never reuse an existing output, receipt or log path'
    return confined(root, candidate)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--document', type=Path, required=True)
    parser.add_argument('--document-sha256', required=True)
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    if sys.flags.optimize != 0:
        raise RuntimeError('Calibration supervision requires Python assertions enabled')
    assert digest(__file__) == args.source_sha256
    ROOT = args.root.resolve(strict=True)
    PLAN = ROOT / '.worktree/Perf-01-linux/Plan/ledger/evidence/batches/Perf-01'
    DOCUMENT = confined(ROOT, args.document)
    RECEIPT = ROOT / 'perf01-run/database-observer-before-calibration-001-execution.json'
    document_sha256 = args.document_sha256
    assert re.fullmatch(r'[0-9a-f]{64}', document_sha256) is not None
    assert 'NW_PERF01_GC_CONFIG' not in os.environ
    assert digest(DOCUMENT) == document_sha256
    doc = json.loads(DOCUMENT.read_text())
    assert doc['status'] == 'prepared-current-pair-adopted'
    assert os.sched_getaffinity(0) == {8}
    for path, expected in doc['required_source_and_metadata_sha256'].items():
        assert digest(confined(ROOT, path)) == expected, path
    actual_python = Path(sys.executable).resolve(strict=True)
    assert actual_python == Path(doc['python']['executable']).resolve(strict=True)
    assert '.'.join(map(str, sys.version_info[:3])) == doc['python']['version']
    assert digest(actual_python) == doc['python']['recorded_executable_sha256']
    policy_path = confined(ROOT, ROOT / '.worktree/Perf-01-linux/Plan' / doc['database_amendment']['repository_path'])
    assert digest(policy_path) == doc['database_amendment']['sha256']
    policy = json.loads(policy_path.read_text())
    assert digest(__file__) == policy['supervisor_source_sha256']
    assert digest(PLAN / 'database_observer_calibrate.py') == policy['controller_source_sha256']
    spec = importlib.util.spec_from_file_location('perf01_observer_calibration_guard', PLAN / 'database_observer_calibrate.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.require_adoption(policy, ROOT)
    driver = guard.confined(ROOT, doc['driver_root_relative'])
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=driver, text=True).strip() == doc['driver_commit']
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}'], cwd=driver, text=True).strip() == policy['driver_tree']
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=driver)
    RECEIPT = fresh(ROOT, RECEIPT)
    for command in doc['commands']:
        fresh(ROOT, command['output'])
        fresh(ROOT, Path('perf01-run') / (command['id'] + '.log'))
        guard.confined(ROOT, command['working_directory'])
        guard.confined(ROOT, command['controller_future'])
        guard.confined(ROOT, command['selection_future'])
    result = {'task': 'Perf-01', 'state': 'running', 'started_utc': utc(),
              'document': str(DOCUMENT), 'document_sha256': document_sha256,
              'supervisor_source_sha256': digest(__file__), 'pid': os.getpid(),
              'cpu_affinity': sorted(os.sched_getaffinity(0)), 'commands': [], 'duration_credit_seconds': 0}
    save(RECEIPT, result)
    for command in doc['commands']:
        log = confined(ROOT, Path('perf01-run') / (command['id'] + '.log'))
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
            selection.get('scheduler_gc_policy', {}).get('mode') == policy['scheduler_gc_mode'] and
            selection.get('resource_sampling_policy_sha256') == policy['resource_sampling_policy_sha256'] and
            selection.get('resource_sampling_policy', {}).get('mode') == policy['resource_sampling_mode'] and
            controller.get('resource_sampling_policy_sha256') == policy['resource_sampling_policy_sha256'] and
            controller.get('resource_sampling_policy', {}).get('mode') == policy['resource_sampling_mode'] and
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
