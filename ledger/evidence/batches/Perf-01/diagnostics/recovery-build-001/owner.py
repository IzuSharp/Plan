"""Finite build-only ownership; reuses the public B23 pidfd tree primitive.

This is new recovery source, not the lost private owner/guard. It runs no
measurement algorithm and never assigns functional or performance credit.
"""
from __future__ import annotations

import asyncio
import ctypes
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from types import SimpleNamespace


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    temporary.replace(path)


def utc():
    return datetime.now(timezone.utc).isoformat()


def proc(pid):
    try:
        fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
    except (FileNotFoundError, ProcessLookupError):
        return None
    # Permission/parse failures refuse admission or retirement; not "absent".
    return dict(pid=pid, ppid=int(fields[1]), start_ticks=int(fields[19]), state=fields[0])


def direct_children():
    # This executor exposes procfs stat/PPid but omits task/PID/children.
    # Only disappearance races are skipped by proc(); other read/parse errors
    # refuse admission/retirement, preserving the complete adopted-child gate.
    result = []
    for path in Path('/proc').iterdir():
        if path.name.isdigit():
            item = proc(int(path.name))
            if item is not None and item['ppid'] == os.getpid():
                result.append(item)
    return result


def public_tree(driver):
    directory = Path(driver) / 'src/Benchmarks.Domain'
    sys.path.insert(0, str(directory))
    spec = importlib.util.spec_from_file_location('recovery_public_supervision', directory / 'supervision.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class BuildTree(module.OwnedTree):
        def __init__(self, root, registry, token):
            # A finite command may exit between spawn and the first procfs
            # read. Its wait status remains authoritative; orphan adoption
            # still discovers any descendants after that fast leader exit.
            self.root, self.registry, self.token = root, Path(registry), token
            initial = proc(root)
            self.known = {root: dict(initial, role='build-worker')} if initial else {}
            self.signals, self.registry_errors = [], []

        def refresh(self):
            super().refresh()
            # The owner is a Linux subreaper and has no unrelated concurrent
            # subprocesses. An escaped-session orphan becomes its direct child.
            for item in direct_children():
                self.known[item['pid']] = dict(item, role='owned-or-adopted-build-child')

        def live(self):
            result = []
            for pid, expected in self.known.items():
                item = proc(pid)
                if item is not None and item['start_ticks'] == expected['start_ticks'] and item['state'] != 'Z':
                    result.append(item)
            return result

        def reap_adopted(self, worker_pid):
            for pid in list(self.known):
                if pid == worker_pid:
                    continue  # Popen owns the direct worker wait status.
                item = proc(pid)
                if item is not None and item['ppid'] == os.getpid() and item['state'] == 'Z':
                    try:
                        os.waitpid(pid, os.WNOHANG)
                    except ChildProcessError:
                        pass

    return BuildTree


def enable_subreaper():
    if sys.platform != 'linux' or not hasattr(os, 'pidfd_open') or not hasattr(signal, 'pidfd_send_signal'):
        raise RuntimeError('Linux procfs and pidfd signalling are required')
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER
        raise OSError(ctypes.get_errno(), 'PR_SET_CHILD_SUBREAPER')
    value = ctypes.c_int()
    if libc.prctl(37, ctypes.byref(value), 0, 0, 0) != 0 or value.value != 1:
        raise RuntimeError('Subreaper state could not be verified')
    if direct_children():
        raise RuntimeError('Build owner already has children before admission')


async def command(spec, environment, directory, tree_type):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    row = dict(spec, status='running', started_utc=utc(), started_monotonic_ns=time.monotonic_ns(),
               ownership='public B23 pidfd tree plus explicit recovery subreaper adoption')
    receipt = directory / 'receipt.json'
    save(receipt, row)
    worker = tree = None
    failure = None
    try:
        with (directory / 'stdout.log').open('wb') as stdout, (directory / 'stderr.log').open('wb') as stderr:
            # No await between spawn and ownership registration: task
            # cancellation cannot interrupt that registration window.
            worker = subprocess.Popen(spec['argv'], cwd=spec['cwd'], env=environment,
                stdout=stdout, stderr=stderr, start_new_session=True)
            tree = tree_type(worker.pid, directory / 'unused-registration.jsonl', 'build-only')
            row['worker'] = proc(worker.pid)
            row['spawned_pid'] = worker.pid
            save(receipt, row)
            limit = time.monotonic() + spec['timeout_seconds']
            while worker.poll() is None:
                tree.refresh(); tree.reap_adopted(worker.pid)
                if tree.registry_errors:
                    raise RuntimeError('Public ownership registry failed validation')
                if time.monotonic() >= limit:
                    raise TimeoutError('Finite producer deadline exceeded')
                await asyncio.sleep(.1)
            worker.wait(timeout=3)
            # A successful leader exit is insufficient: separately sessioned
            # compilers and adopted grandchildren must also have retired.
            deadline = time.monotonic() + 2
            while True:
                tree.refresh(); tree.reap_adopted(worker.pid)
                if not tree.live() or time.monotonic() >= deadline:
                    break
                await asyncio.sleep(.05)
            if tree.live():
                raise RuntimeError('Producer exited with live owned/adopted descendants')
            if direct_children():
                raise RuntimeError('Producer exited with unreaped/adopted children')
            if worker.returncode != 0:
                raise RuntimeError('Producer exit ' + str(worker.returncode))
    except BaseException as error:
        failure = type(error).__name__ + ': ' + str(error)
        if tree is not None:
            try:
                await tree.stop(10, SimpleNamespace(time=time))
                if worker is not None:
                    worker.wait(timeout=3)
                tree.refresh(); tree.reap_adopted(worker.pid)
            except BaseException as cleanup:
                row['cleanup_failure'] = type(cleanup).__name__ + ': ' + str(cleanup)
    finally:
        row.update(ended_utc=utc(), ended_monotonic_ns=time.monotonic_ns(),
                   exit_code=worker.returncode if worker else None, failure=failure)
        try:
            if tree is not None:
                tree.refresh(); tree.reap_adopted(worker.pid)
            remaining = direct_children()
            row.update(owned_processes=list(tree.known.values()) if tree else [],
                       signals=tree.signals if tree else [],
                       live_owned_after=tree.live() if tree else [], owner_children_after=remaining)
            row['retired'] = not row['live_owned_after'] and not remaining and 'cleanup_failure' not in row
        except BaseException as error:
            row.update(retired=False, retirement_failure=type(error).__name__ + ': ' + str(error))
        row['status'] = 'completed' if failure is None and row['retired'] else 'failed'
        row['logs_sha256'] = {name: sha(directory / name) for name in ('stdout.log', 'stderr.log') if (directory / name).is_file()}
        save(receipt, row)
    if row['status'] != 'completed':
        raise RuntimeError('Build command failed; preserve ' + str(receipt))
    return {'path': str(receipt), 'sha256': sha(receipt), 'label': spec['label'], 'exit_code': row['exit_code'], 'retired': True}
