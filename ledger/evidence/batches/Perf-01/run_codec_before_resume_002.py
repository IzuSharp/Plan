"""One output-only codec resume; no workload or acceptance-policy changes."""
import argparse
import copy
import datetime
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path('/workspace/scratch/01c249676f47')
PLAN = ROOT / '.worktree/Perf-01-linux/Plan/ledger/evidence/batches/Perf-01'
DOCUMENT = PLAN / 'codec-before-resume-002.json'
EXPECTED_DOCUMENT = '225c9295a102de22a59e2bea01f2bb3f3abecbea98313f5b7c157322916a9e12'
EXPECTED_FREEZE = '85061c4e01b28fc72a5b20519ce2d8c01d79cae271238ba36e0a3465b0b8f4a3'
OUTPUT = ROOT / 'perf01-evidence/long/before/codec-002'
VERIFICATION = Path(str(OUTPUT) + '-verification.json')
RECEIPT = ROOT / 'perf01-run/before-codec-long-002-execution.json'
JOURNAL = ROOT / 'perf01-run/before-codec-long-002-supervision.jsonl'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def read_json(path, limit=1024 * 1024):
    with Path(path).open('rb') as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, 'Bounded JSON limit exceeded: ' + str(path))
    return json.loads(data)


def checked(reference):
    require(digest(reference['path']) == reference['sha256'], 'Hash mismatch: ' + reference['path'])
    return read_json(reference['path'])


def fresh(path):
    require(not os.path.lexists(path), 'Refuse existing output: ' + str(path))


def derived_commands(original):
    commands = copy.deepcopy(original['commands'])
    require(len(commands) == 2, 'Unexpected original command count')
    for index, command in enumerate(commands):
        argv = command['argv']
        require(argv.count('--output') == 1, 'Output selector must be unique')
        argv[argv.index('--output') + 1] = str(OUTPUT)
        if index == 0:
            require(command['kind'] == 'measurement', 'Unexpected measurement selector')
            command.update(id='codec-before-r241-long-002', output=str(OUTPUT))
        else:
            require(command['kind'] == 'post_run_verification' and argv.count('--receipt') == 1,
                    'Unexpected verification selector')
            argv[argv.index('--receipt') + 1] = str(VERIFICATION)
            command.update(id='codec-before-r241-long-verify-002', receipt=str(VERIFICATION))
    return commands


def preflight(source_hash, step, receipt):
    require(digest(__file__) == source_hash, 'Supervisor source changed')
    require(digest(DOCUMENT) == EXPECTED_DOCUMENT, 'Resume document changed')
    document = read_json(DOCUMENT)
    require(document['global_freeze']['sha256'] == EXPECTED_FREEZE, 'Unexpected freeze identity')
    freeze = checked(document['global_freeze'])
    original = checked(document['original_command_document'])
    publication = checked(document['global_publication_readback'])
    require(publication['publication_gate_satisfied'] is True and publication['remote_and_local_bytes_equal'] is True
            and publication['configuration_sha256'] == EXPECTED_FREEZE, 'Original freeze publication gate failed')
    require(freeze['reviewed_long_command_documents']['codec']['sha256'] == document['original_command_document']['sha256'],
            'Original command is not the frozen codec command')
    require(digest(document['original_supervisor']['path']) == document['original_supervisor']['sha256'],
            'Original supervisor changed')
    previous = checked(document['interrupted_attempt']['execution_receipt'])
    require(previous['commands'][0]['argv'] == original['commands'][0]['argv']
            and previous['long_duration_credit_seconds'] == 0, 'Interrupted attempt identity changed')
    require(document['commands'] == derived_commands(original), 'Changes exceed allowed output/receipt paths and command IDs')
    for name in ('configuration', 'selection', 'expected_result_checks'):
        require(document['unchanged_' + name] == original[name], 'Inherited configuration changed: ' + name)
    require(document['working_directory'] == original['working_directory']
            and document['timing_lock'] == original['timing_lock']['path']
            and document['output'] == str(OUTPUT) and document['verification_receipt'] == str(VERIFICATION)
            and document['supervisor_receipt'] == str(RECEIPT) and document['supervision_log'] == str(JOURNAL),
            'Unexpected execution paths')
    for name in ('required_source_and_metadata_sha256', 'required_final_selection_sha256'):
        for path, expected in original[name].items():
            require(digest(path) == expected, 'Source/metadata hash mismatch: ' + path)
    python = freeze['toolchain']['python']
    require(Path(sys.executable).resolve() == Path(python['executable']).resolve()
            and '.'.join(map(str, sys.version_info[:3])) == python['version']
            and digest(sys.executable) == python['recorded_executable_sha256'], 'Python identity mismatch')
    machine = freeze['machine_and_isolation']
    boot = hashlib.sha256(Path('/proc/sys/kernel/random/boot_id').read_text().strip().encode()).hexdigest()
    require(boot == machine['recorded_kernel_boot_sha256'], 'Boot identity mismatch')
    require(os.uname().sysname == 'Linux' and os.uname().machine == 'x86_64'
            and os.uname().release == machine['recorded_host_snapshot']['kernel'], 'Platform/kernel mismatch')
    require(os.sched_getaffinity(0) == {8}, 'Supervisor must run on CPU8')
    fresh(VERIFICATION)
    if step == 0:
        fresh(OUTPUT)
        for command in document['commands']:
            fresh(RECEIPT.parent / (command['id'] + '.log'))
    else:
        require(len(receipt['commands']) == 1 and receipt['commands'][0]['exit_code'] == 0,
                'Verifier requires an actually observed successful measurement exit')
        require((OUTPUT / 'result.json').is_file() and (OUTPUT / 'summary.json').is_file(),
                'Completed codec result/summary missing')
    return document, original, boot


def save(value):
    temporary = RECEIPT.with_suffix('.json.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    temporary.replace(RECEIPT)


def event(stream, value):
    value = {'utc': utc(), 'monotonic_ns': time.monotonic_ns(), **value}
    stream.write(json.dumps(value, sort_keys=True) + '\n')
    stream.flush(); os.fsync(stream.fileno())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-sha256', required=True, help='Exact reviewed supervisor SHA-256')
    args = parser.parse_args()
    fresh(RECEIPT); fresh(JOURNAL)
    # Claim this one attempt before preflight; a failed claim is never overwritten.
    with RECEIPT.open('x') as stream:
        stream.write('{}\n'); stream.flush(); os.fsync(stream.fileno())
    receipt = {'task': 'Perf-01', 'group': 'codec', 'variant': 'before', 'attempt': 2,
               'state': 'preflight', 'started_utc': utc(), 'supervisor_pid': os.getpid(),
               'supervisor_source_sha256': digest(__file__), 'document_sha256': EXPECTED_DOCUMENT,
               'freeze_sha256': EXPECTED_FREEZE, 'output': str(OUTPUT),
               'verification_receipt': str(VERIFICATION), 'commands': [],
               'accepted': False, 'long_duration_credit_seconds': 0}
    child = entry = None
    with JOURNAL.open('x') as journal:
        save(receipt)
        try:
            for step in range(2):
                # Measurement owns its original argv flock. Only verification is locked here.
                lock = None
                try:
                    if step == 1:
                        lock = (ROOT / 'perf01-evidence/timing.lock').open('a+b')
                        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    document, original, boot = preflight(args.source_sha256, step, receipt)
                    command = document['commands'][step]
                    log = RECEIPT.parent / (command['id'] + '.log')
                    fresh(log)
                    entry = {'id': command['id'], 'argv': command['argv'], 'cwd': document['working_directory'],
                             'started_utc': utc(), 'state': 'running', 'exit_code': None, 'log': str(log)}
                    receipt['commands'].append(entry)
                    receipt.update(state='running', active_command=entry['id'], kernel_boot_sha256=boot)
                    save(receipt); event(journal, {'event': 'command-started', **entry})
                    started = time.monotonic()
                    with log.open('xb') as handle:
                        child = subprocess.Popen(command['argv'], cwd=document['working_directory'],
                                                 stdout=handle, stderr=subprocess.STDOUT)
                        entry['pid'] = child.pid; save(receipt)
                        event(journal, {'event': 'child-started', 'command': entry['id'], 'pid': child.pid})
                        while True:
                            try:
                                code = child.wait(timeout=45)
                                break
                            except subprocess.TimeoutExpired:
                                progress = {'event': 'supervision', 'command': entry['id'], 'pid': child.pid,
                                            'elapsed_seconds': time.monotonic() - started}
                                for name in ('phase-progress.json', 'progress.json'):
                                    path = OUTPUT / name
                                    if path.is_file():
                                        try:
                                            progress[name] = read_json(path, 65536)
                                        except (OSError, ValueError) as error:
                                            progress[name + '_read_error'] = type(error).__name__ + ': ' + str(error)
                                event(journal, progress)
                                receipt['last_progress'] = progress; save(receipt)
                    entry.update(ended_utc=utc(), state='completed', exit_code=code,
                                 elapsed_seconds=time.monotonic() - started, log_sha256=digest(log))
                    save(receipt); event(journal, {'event': 'command-ended', **entry})
                    child = None
                    if code != command['expected_exit_code']:
                        receipt.update(state='failed-command', ended_utc=utc(), failed_command=entry['id'])
                        save(receipt); event(journal, {'event': 'attempt-failed', 'command': entry['id'], 'actual_exit_code': code})
                        return code if code > 0 else 1
                finally:
                    if lock is not None:
                        lock.close()
            actual = read_json(VERIFICATION)
            credit = actual.get('duration_credit_seconds')
            identity = actual.get('original_checked_identities', {})
            expected = original['required_source_and_metadata_sha256']
            expected_identity = {
                'route': 'nativeweave',
                'manifest_sha256': expected[str(ROOT / 'perf01-codec-checks/package-before-004/manifest.json')],
                'corpus_manifest_sha256': expected[str(ROOT / 'perf01-codec-checks/corpus/manifest.json')],
                'controller_sha256': expected[str(ROOT / '.worktree/Perf-01-linux/NativeWeave/tests/Perf01.Codec/driver.py')],
                'a21_sha256': expected[str(ROOT / '.worktree/Perf-01-linux/NativeWeave/src/Benchmarks.Harness/nativeweave_bench.py')]}
            receipt.update(domain_verifier_accepted=actual.get('accepted'), verification_sha256=digest(VERIFICATION))
            accepted = (actual.get('accepted') is True and actual.get('group') == 'codec'
                        and actual.get('output_directory') == str(OUTPUT)
                        and actual.get('verifier_sha256') == original['post_run_verifier']['sha256']
                        and all(identity.get(k) == v for k, v in expected_identity.items())
                        and len(receipt['commands']) == 2 and all(c['exit_code'] == 0 for c in receipt['commands'])
                        and type(credit) in (int, float) and math.isfinite(credit) and credit >= 1800)
            receipt.update(state='completed' if accepted else 'failed-final-gate', ended_utc=utc(),
                           accepted=accepted, long_duration_credit_seconds=credit if accepted else 0)
            save(receipt); event(journal, {'event': 'attempt-ended', 'accepted': accepted,
                                         'long_duration_credit_seconds': receipt['long_duration_credit_seconds']})
            return 0 if accepted else 1
        except BaseException as error:
            # Runtime loss cannot be caught. If this handler runs, only poll/wait is exit evidence.
            observed = child.poll() if child is not None else None
            if child is not None and observed is not None and entry is not None:
                entry.update(exit_code=observed, ended_utc=utc(), state='completed')
            receipt.update(state='orchestration-failed', ended_utc=utc(), accepted=False,
                           long_duration_credit_seconds=0,
                           error=type(error).__name__ + ': ' + str(error),
                           cleanup_required=child is not None and observed is None)
            save(receipt); event(journal, {'event': 'orchestration-failed', 'error': receipt['error'],
                                         'cleanup_required': receipt['cleanup_required']})
            return 130 if isinstance(error, KeyboardInterrupt) else 1


if __name__ == '__main__':
    raise SystemExit(main())
