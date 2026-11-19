"""Execute exactly the published Perf-01 selectors, with supervision only."""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import time

ROOT = pathlib.Path('/workspace/scratch/01c249676f47')
PLAN = ROOT / '.worktree/Perf-01-linux/Plan/ledger/evidence/batches/Perf-01'
EXPECTED_FREEZE = '85061c4e01b28fc72a5b20519ce2d8c01d79cae271238ba36e0a3465b0b8f4a3'

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def save(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    temp.replace(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('group', choices=['http', 'grpc', 'postgresql', 'sqlite', 'codec'])
    args = parser.parse_args()
    freeze_bytes = (PLAN / 'frozen-execution.json').read_bytes()
    assert hashlib.sha256(freeze_bytes).hexdigest() == EXPECTED_FREEZE
    freeze = json.loads(freeze_bytes)
    publication = json.loads((PLAN / 'checks/final-freeze-001/publication-readback.json').read_text())
    assert publication['publication_gate_satisfied'] and publication['remote_and_local_bytes_equal']
    assert publication['configuration_sha256'] == EXPECTED_FREEZE
    group = next(g for g in freeze['long_acceptance']['groups'] if g['group'] == args.group)
    out = pathlib.Path(group['before_output'])
    verification = pathlib.Path(group['before_verification_receipt'])
    assert not out.exists(), 'Refuse to overwrite prior measurement output'
    assert not verification.exists(), 'Refuse to overwrite prior verification'
    doc_name = group['command_document']
    doc_ref = freeze['reviewed_long_command_documents'][doc_name]
    doc_bytes = pathlib.Path(doc_ref['path']).read_bytes()
    assert hashlib.sha256(doc_bytes).hexdigest() == doc_ref['sha256']
    doc = json.loads(doc_bytes)
    selectors = [s for s in freeze['long_acceptance']['before_global_command_order']
                 if s['document'] == doc_name and (s['selector'].get('group') == args.group or args.group in s['id'] or (args.group == 'codec'))]
    commands = []
    for s in selectors:
        if doc_name == 'protocols':
            candidates = [c for g in doc['groups'] if g['group'] == args.group for c in g['commands'] if c['kind'] == s['selector']['kind']]
        else:
            candidates = [c for c in doc['commands'] if c['id'] == s['selector']['id']]
        assert len(candidates) == 1
        commands.append((s['id'], candidates[0]))
    assert len(commands) == (3 if doc_name == 'protocols' else 2)
    receipt_path = ROOT / 'perf01-run' / ('before-' + args.group + '-long-001-execution.json')
    assert not receipt_path.exists()
    receipt = {'task': 'Perf-01', 'group': args.group, 'variant': 'before', 'state': 'running',
               'started_utc': utc(), 'freeze_sha256': EXPECTED_FREEZE,
               'published_freeze_commit': publication['commit'], 'supervisor_pid': os.getpid(),
               'supervisor_source_sha256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
               'document_sha256': doc_ref['sha256'], 'output': str(out),
               'verification_receipt': str(verification), 'commands': [], 'long_duration_credit_seconds': 0}
    save(receipt_path, receipt)
    for identifier, command in commands:
        log = receipt_path.with_name(identifier + '.log')
        assert not log.exists()
        entry = {'id': identifier, 'argv': command['argv'], 'cwd': doc['working_directory'],
                 'started_utc': utc(), 'log': str(log), 'state': 'running'}
        receipt['commands'].append(entry)
        receipt['active_command'] = identifier
        save(receipt_path, receipt)
        print(json.dumps({'event': 'command-started', 'group': args.group, **entry}), flush=True)
        started = time.monotonic()
        with log.open('xb') as handle:
            child = subprocess.Popen(command['argv'], cwd=doc['working_directory'], stdout=handle, stderr=subprocess.STDOUT)
            entry['pid'] = child.pid
            save(receipt_path, receipt)
            while child.poll() is None:
                try:
                    child.wait(timeout=45)
                except subprocess.TimeoutExpired:
                    progress = {'event': 'supervision', 'group': args.group, 'command': identifier,
                                'utc': utc(), 'command_elapsed_seconds': round(time.monotonic() - started, 2), 'pid': child.pid}
                    for name in ['phase-progress.json', 'progress.json']:
                        p = out / name
                        if p.is_file() and p.stat().st_size < 65536:
                            try:
                                progress[name] = json.loads(p.read_text())
                            except (ValueError, OSError):
                                pass
                    print(json.dumps(progress), flush=True)
        entry.update({'ended_utc': utc(), 'state': 'completed', 'exit_code': child.returncode,
                      'elapsed_seconds': time.monotonic() - started})
        save(receipt_path, receipt)
        print(json.dumps({'event': 'command-ended', 'group': args.group, 'id': identifier, 'exit_code': child.returncode, 'ended_utc': entry['ended_utc']}), flush=True)
        if child.returncode != command.get('expected_exit_code', 0):
            receipt.update({'state': 'failed', 'ended_utc': utc(), 'failed_command': identifier})
            save(receipt_path, receipt)
            return child.returncode or 1
    actual = json.loads(verification.read_text())
    assert actual['accepted'] is True, actual.get('failure_reasons')
    receipt.update({'state': 'completed', 'ended_utc': utc(), 'accepted': True,
                    'verification_sha256': hashlib.sha256(verification.read_bytes()).hexdigest(),
                    'long_duration_credit_seconds': actual['duration_credit_seconds']})
    save(receipt_path, receipt)
    print(json.dumps({'event': 'group-accepted', 'group': args.group, 'receipt': str(receipt_path),
                      'duration_credit_seconds': receipt['long_duration_credit_seconds']}), flush=True)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
