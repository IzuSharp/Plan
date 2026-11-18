#!/usr/bin/env python3
"""Bounded SQLite thread-owner diagnosis; never a soak acceptance or cap change."""
from pathlib import Path
import concurrent.futures
import json
import os
import signal
import subprocess
import sys
import time
import types

ROOT = Path('/workspace/scratch/58d2a6adf1c3')
SOURCE = ROOT / '.worktree/Task-07-B22-idle-f889-linux/NativeWeave'
sys.path.insert(0, str(SOURCE / 'tests/Verification.EndToEnd'))
import soak
from descriptor_profile import process_identity, snapshot as descriptor_snapshot
from harness import Database, Service, configuration, require, sha, write_json


def thread_snapshot(target):
    require(process_identity(target['pid']) == target, 'Target process identity changed')
    started = time.monotonic_ns()
    entries = sorted((Path('/proc') / str(target['pid']) / 'task').iterdir(), key=lambda path: int(path.name))
    inventory, vanished = [], []
    for entry in entries:
        try:
            first = (entry / 'stat').read_text().rsplit(')', 1)[1].split()
            name = (entry / 'comm').read_text().strip()
            wait_channel = (entry / 'wchan').read_text().strip()
            second = (entry / 'stat').read_text().rsplit(')', 1)[1].split()
        except FileNotFoundError:
            vanished.append(int(entry.name))
            continue
        require(first[19] == second[19], 'Thread identifier reused within snapshot')
        inventory.append({'tid': int(entry.name), 'startTicks': int(first[19]), 'name': name,
                          'stateBefore': first[0], 'stateAfter': second[0], 'waitChannel': wait_channel})
    names = {}
    for item in inventory:
        names[item['name']] = names.get(item['name'], 0) + 1
    require(process_identity(target['pid']) == target, 'Target changed during thread snapshot')
    return {'target': target, 'startedMonotonicNs': started, 'endedMonotonicNs': time.monotonic_ns(),
            'enumerated': len(entries), 'resolved': len(inventory), 'vanishedDuringRead': vanished,
            'countsByName': names, 'inventory': inventory}


def main():
    output = Path(sys.argv[1]).resolve()
    output.mkdir(parents=True, exist_ok=False)
    args = types.SimpleNamespace(
        artifact_directory=ROOT / 'task07-runs/b22-observer-build-007-f889/artifacts/aot',
        trace_reader=ROOT / '.worktree/Task-07-B22-recovery-6b7401-linux/NativeWeave/src/Verification.EndToEnd/TraceReader/bin/Release/net11.0/NativeWeave.Verification.EndToEnd.TraceReader.dll',
        mode='aot', provider='sqlite', dotnet='dotnet', postgres_bin=None,
        certificate=ROOT / 'task07-package-probe/final-002/tls/localhost.pem',
        private_key=ROOT / 'task07-package-probe/final-002/tls/localhost.private.pem')
    command, identity, providers = soak.identity(args)
    require(providers == {'sqlite'}, 'Diagnostic provider inventory changed')
    receipt = {
        'schemaVersion': 1, 'task': 'B22', 'status': 'running',
        'purpose': 'Classify task-owned live process threads after the original frozen SQLite thread band failed; no cap adjustment or acceptance.',
        'sourceCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=SOURCE, text=True).strip(),
        'diagnosticScriptSha256': sha(Path(__file__)), 'identity': identity,
        'settings': {'loadSeconds': 120, 'idleSeconds': 60, 'rate': 4, 'concurrency': 4, 'seed': 2200261118, 'sampleSeconds': 1.1},
        'startedUnixNs': time.time_ns(), 'performanceMeasurement': False,
        'fullB22Acceptance': False, 'resourceProfileFreeze': False,
        'sharedHost': 'Independent PostgreSQL B22 steady stage continues; no B23 performance workload.'}
    write_json(output / 'request.json', receipt)
    operations = soak.Journal(output / 'operations.jsonl')
    resources = soak.Journal(output / 'thread-owners.jsonl')
    control = output / 'observer-control.json'
    trace = output / 'runtime.nettrace'
    command = ['env', *[key + '=' + value for key, value in soak.TRACE_ENVIRONMENT.items()],
               'DOTNET_EventPipeOutputPath=' + str(trace), 'NW_B22_HANDLE_CONTROL=1',
               'NW_B22_HANDLE_CONTROL_OUTPUT=' + str(output / 'known-handles.jsonl'),
               'NW_B22_OBSERVER_CONTROL=' + str(control), *command]
    previous_handlers = {}

    def interrupt(signum, _frame):
        raise InterruptedError(f'Diagnostic interrupted by signal {signum}')

    try:
        previous_handlers = {sig: signal.signal(sig, interrupt) for sig in (signal.SIGTERM, signal.SIGINT)}
        database = str(output / 'application.sqlite')
        config, token = configuration('sqlite', database, output, tls=(args.certificate, args.private_key))
        config.update(runWorkers=True, maxBlobBytes=256 * 1024**2)
        sql = Database('sqlite', database, None)
        with Service(command, config, output / 'service', observed=True, http2=True, certificate=args.certificate) as service:
            from urllib.parse import urlsplit
            target = process_identity(service.process.pid)
            require(target['parentPid'] == os.getpid(), 'Target is not the diagnostic child')
            receipt['target'] = target
            receipt['executionConfigSha256'] = sha(output / 'service/config.private.json')
            tail = soak.Tail(output / 'service/observations.jsonl')
            tail.read()
            workload = soak.Workload(service, token, sql, config, 2200261118, operations)
            last_sample, maximum, last_names = 0, 0, None

            def snapshot(phase):
                nonlocal last_sample, maximum, last_names
                threads = thread_snapshot(target)
                descriptors = descriptor_snapshot(target, output, urlsplit(service.url).port, None, phase)
                tail.read()
                latest = tail.latest
                process = soak.process_sample(service.process.pid)
                value = {'phase': phase, 'threads': threads, 'descriptors': descriptors, 'process': process,
                         'observationSequence': latest['sequence'], 'observationPhase': latest['phase'],
                         'controlSequence': latest['controlSequence'], 'nativeOwners': latest['databaseNativeOwners'],
                         'serverMeter': latest['serverMeter'], 'observerFailures': latest['observerFailures']}
                resources.write(value)
                write_json(output / 'progress.json', {'status': 'running', 'phase': phase,
                    'observedUnixNs': time.time_ns(), 'target': target,
                    'threadCount': threads['enumerated'], 'countsByName': threads['countsByName'],
                    'fdCount': descriptors['enumerated'], 'observationSequence': latest['sequence']})
                if threads['enumerated'] > maximum or threads['countsByName'] != last_names:
                    maximum = max(maximum, threads['enumerated'])
                    last_names = threads['countsByName']
                    print(json.dumps({'phase': phase, 'maximumThreads': maximum, 'countsByName': last_names}), flush=True)
                last_sample = time.monotonic()
                return value

            snapshot('startup')
            begun = time.monotonic_ns()
            futures = set()
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                for sequence in range(480):
                    offered = begun + sequence * 250000000
                    while time.monotonic_ns() < offered:
                        if time.monotonic() - last_sample >= 1.1:
                            snapshot('load')
                        time.sleep(min(.05, max(0, (offered - time.monotonic_ns()) / 1e9)))
                    ready = {future for future in futures if future.done()}
                    for future in ready:
                        future.result()
                    futures -= ready
                    require(len(futures) < 4, 'Fixed diagnostic generator outstanding slots exhausted')
                    require(time.monotonic_ns() - offered <= 1000000000, 'Diagnostic generator lag exceeded 1s')
                    require(workload.reserve() == sequence, 'Diagnostic operation identity drift')
                    futures.add(executor.submit(workload.cancel_upload, sequence) if sequence == 0 else
                                executor.submit(workload.perform, sequence, offered))
                    if time.monotonic() - last_sample >= 1.1:
                        snapshot('load')
                for future in futures:
                    future.result(timeout=90)
            while time.monotonic_ns() < begun + 120000000000:
                if time.monotonic() - last_sample >= 1.1:
                    snapshot('load')
                time.sleep(.05)
            receipt['loadElapsedSeconds'] = (time.monotonic_ns() - begun) / 1e9
            receipt['durable'] = workload.reconcile()
            write_json(control, {'sequence': 1, 'collect': True, 'expectedSources': {'sqlite': 2},
                                 'nativeBaseline': {'sqlite': [2, 0, 0, 0, 0, 6]}})
            idle_started = time.monotonic()
            while time.monotonic() - idle_started < 60:
                snapshot('idle')
                time.sleep(min(1.1, max(0, 60 - (time.monotonic() - idle_started))))
            receipt['idleElapsedSeconds'] = time.monotonic() - idle_started
            receipt['maximumEnumeratedThreads'] = maximum
            receipt['ordinaryProtocols'] = sorted(service.protocols)
            receipt['workloadCounts'] = workload.counts
            receipt['finalLiveSnapshot'] = snapshot('final-live-idle')
        tail.read()
        receipt['finalObservation'] = tail.latest
        receipt['finalShutdown'] = service.shutdown
        soak.revalidate_inputs(args, identity)
        receipt['traceObservation'] = soak.trace_analyze(args, output)
        receipt['idleGcHandleObservations'] = soak.idle_trace_windows(output / 'trace-receipt.json.samples.jsonl', 1)
        receipt['status'] = 'diagnostic-completed'
    except BaseException as error:
        receipt['status'] = 'diagnostic-interrupted' if isinstance(error, (InterruptedError, KeyboardInterrupt)) else 'diagnostic-failed'
        receipt['error'] = {'type': type(error).__name__, 'message': str(error) if isinstance(error, (AssertionError, RuntimeError, InterruptedError)) else None}
        raise
    finally:
        operations.close()
        resources.close()
        receipt['endedUnixNs'] = time.time_ns()
        receipt['rawHashes'] = {path.relative_to(output).as_posix(): sha(path) for path in output.rglob('*')
                                if path.is_file() and path.name not in ('receipt.json', 'config.private.json')
                                and path.suffix not in ('.sqlite', '.pem') and not path.name.endswith(('-wal', '-shm'))}
        write_json(output / 'receipt.json', receipt)
        for sig, handler in previous_handlers.items():
            signal.signal(sig, handler)
        print(json.dumps({'status': receipt['status'], 'receipt': str(output / 'receipt.json')}), flush=True)


if __name__ == '__main__':
    main()
