"""Supervise exact prospective commands without changing timed drivers."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import time

ROOT = pathlib.Path('/workspace/scratch/01c249676f47')
PLAN = ROOT / '.worktree/Perf-01-linux/Plan/ledger/evidence/batches/Perf-01'

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    temp.replace(path)

def main():
    amend_path = PLAN / 'frozen-execution-grpc-long-amendment-001.json'
    amendment = json.loads(amend_path.read_text())
    publication = json.loads((PLAN / 'checks/grpc-long-amendment-001/publication-readback.json').read_text())
    assert publication['remote_and_local_bytes_equal'] is True
    assert publication['amendment_sha256'] == digest(amend_path)
    assert digest(PLAN / 'frozen-execution.json') == amendment['parent_freeze_sha256']
    assert digest(pathlib.Path(__file__)) == amendment['supervisor']['sha256']
    doc_ref = amendment['before_command_document']
    assert digest(pathlib.Path(doc_ref['path'])) == doc_ref['sha256']
    doc = json.loads(pathlib.Path(doc_ref['path']).read_text())
    output = pathlib.Path(amendment['before_output'])
    verification = pathlib.Path(amendment['before_verification_receipt'])
    assert not output.exists() and not verification.exists()
    record_path = ROOT / 'perf01-run/before-grpc-r115-002-execution.json'
    assert not record_path.exists(), 'One prospectively declared attempt only'
    record = {'task': 'Perf-01', 'group': 'grpc', 'variant': 'before', 'state': 'running',
              'started_utc': utc(), 'supervisor_pid': os.getpid(),
              'parent_freeze_sha256': amendment['parent_freeze_sha256'],
              'amendment_sha256': digest(amend_path), 'published_amendment_commit': publication['commit'],
              'supervisor_sha256': digest(pathlib.Path(__file__)), 'commands': [],
              'output': str(output), 'verification_receipt': str(verification),
              'long_duration_credit_seconds': 0}
    save(record_path, record)
    for command in doc['commands']:
        log = record_path.with_name(command['id'] + '.log')
        assert not log.exists()
        entry = {'id': command['id'], 'argv': command['argv'], 'cwd': doc['working_directory'],
                 'started_utc': utc(), 'log': str(log), 'state': 'running'}
        record['commands'].append(entry)
        record['active_command'] = command['id']
        save(record_path, record)
        print(json.dumps({'event': 'command-started', **entry}), flush=True)
        start = time.monotonic()
        with log.open('xb') as handle:
            child = subprocess.Popen(command['argv'], cwd=doc['working_directory'], stdout=handle, stderr=subprocess.STDOUT)
            entry['pid'] = child.pid
            save(record_path, record)
            while child.poll() is None:
                try:
                    child.wait(timeout=45)
                except subprocess.TimeoutExpired:
                    print(json.dumps({'event': 'supervision', 'group': 'grpc', 'rate': 115,
                                      'command': command['id'], 'utc': utc(), 'pid': child.pid,
                                      'command_elapsed_seconds': round(time.monotonic() - start, 2)}), flush=True)
        entry.update({'ended_utc': utc(), 'state': 'completed', 'exit_code': child.returncode})
        save(record_path, record)
        print(json.dumps({'event': 'command-ended', 'id': command['id'], 'exit_code': child.returncode}), flush=True)
        # A completed domain failure still receives the exact independent verifier.
        if child.returncode != 0 and not (command['kind'] == 'measure' and (output / 'result.json').is_file()):
            record.update({'state': 'failed', 'ended_utc': utc(), 'failed_command': command['id']})
            save(record_path, record)
            return child.returncode or 1
    verdict = json.loads(verification.read_text())
    record.update({'state': 'completed' if verdict['accepted'] else 'failed',
                   'ended_utc': utc(), 'accepted': verdict['accepted'],
                   'verification_sha256': digest(verification),
                   'long_duration_credit_seconds': verdict['duration_credit_seconds']})
    save(record_path, record)
    print(json.dumps({'event': 'group-verdict', 'accepted': verdict['accepted'],
                      'duration_credit_seconds': verdict['duration_credit_seconds'],
                      'receipt': str(record_path)}), flush=True)
    return 0 if verdict['accepted'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
