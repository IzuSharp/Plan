#!/usr/bin/env python3
"""DB-Go-01 cleanup: read-only by default; explicit archival gate for deletion.

The executable copy must be /tmp/DB-Go-01-final-cleanup.py.  It accepts no
arbitrary deletion command or shell fragment.  See final-cleanup-design.md.
"""

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import select
import shutil
import signal
import stat
import subprocess
import sys
from urllib.parse import urlparse

TASK = 'DB-Go-01'
OLD = '/workspace/scratch/4a65d70f0fe1'
MID = '/workspace/scratch/fd78534029f7'
CURRENT = '/workspace/scratch/166b48a091b9'
ROOTS = (MID, OLD, CURRENT)
BARES = tuple(OLD + '/repos/' + name + '.git' for name in ('Korda', 'Korda-Design', 'Plan'))
INVENTORY = CURRENT + '/go-comparison-01/cleanup-inventory.json'
EXECUTABLE = '/tmp/DB-Go-01-final-cleanup.py'
ACCEPTANCE = '/tmp/DB-Go-01-final-cleanup-acceptance.json'
STATE = '/tmp/DB-Go-01-final-cleanup-state.json'
STATE_TMP = STATE + '.tmp'
SHA = re.compile(r'[0-9a-f]{64}')
TEMP_NAME = re.compile(
    r'(?:DB-Exec-[A-Za-z0-9._-]+|DB-Go-01-[A-Za-z0-9._-]+|'
    r'korda-(?:b04|pull-scheduler)-[0-9a-f]{32}|'
    r'nw-b(?:13|14)-[0-9a-f]{32}(?:\.db)?)'
)


class Refusal(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise Refusal(message)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def digest_file(path):
    value = hashlib.sha256()
    with open(path, 'rb') as stream:
        while chunk := stream.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def within(path, root):
    return path == root or path.startswith(root + '/')


def under_roots(path):
    return any(within(path, root) for root in ROOTS)


def exact_path(path):
    require(isinstance(path, str) and os.path.isabs(path), 'An absolute path is required')
    require(os.path.normpath(path) == path, 'Non-canonical path rejected: ' + path)
    return path


def identity(path):
    try:
        value = os.lstat(path)
        return {'device': value.st_dev, 'inode': value.st_ino, 'mode': stat.S_IFMT(value.st_mode)}
    except FileNotFoundError:
        return None


def read_regular(path):
    value = os.lstat(path)
    require(stat.S_ISREG(value.st_mode), 'Expected a regular file: ' + path)
    require(value.st_uid == os.geteuid(), 'Control file is not owned by the current user: ' + path)
    require(value.st_size <= 32 * 1024 * 1024, 'Control JSON exceeds the size bound')
    return Path(path).read_bytes()


def run_git(bare, *args):
    result = subprocess.run(
        ['git', '--git-dir=' + bare, *args], cwd='/tmp',
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60,
    )
    require(result.returncode == 0, 'Local Git operation failed: ' + result.stderr.decode(errors='replace')[-1500:])
    return result.stdout


def git_worktrees(bare):
    if not os.path.isdir(bare):
        return []
    result = []
    for record in run_git(bare, 'worktree', 'list', '--porcelain').decode().strip().split('\n\n'):
        fields = {}
        for line in record.splitlines():
            key, _, value = line.partition(' ')
            fields[key] = value
        if not fields or 'bare' in fields:
            continue
        path = exact_path(fields['worktree'])
        require(under_roots(path) or allowed_temp(path), 'Worktree outside the fixed task scope: ' + path)
        require('locked' not in fields, 'Locked worktree requires explicit root review before cleanup: ' + path)
        row = {'bare': bare, 'path': path, 'head': fields.get('HEAD'), 'identity': identity(path)}
        if os.path.isdir(path):
            def local(*args):
                output = subprocess.run(
                    ['git', '-C', path, *args], cwd='/tmp',
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60,
                )
                require(output.returncode == 0, 'Cannot inspect a registered worktree: ' + path)
                return output.stdout
            status_bytes = local('status', '--porcelain=v1', '-z', '--untracked-files=all')
            diff_bytes = local('diff', '--binary', 'HEAD', '--')
            untracked = []
            for relative in local('ls-files', '--others', '--exclude-standard', '-z').split(b'\0'):
                if not relative:
                    continue
                file_path = Path(path) / os.fsdecode(relative)
                if file_path.is_symlink():
                    value = digest_bytes(os.readlink(file_path).encode())
                elif file_path.is_file():
                    value = digest_file(file_path)
                else:
                    raise Refusal('Untracked path changed while inspected: ' + str(file_path))
                untracked.append({'path': os.fsdecode(relative), 'sha256': value})
            row.update({
                'dirty': bool(status_bytes), 'untrackedFileCount': len(untracked),
                'stateSha256': digest_bytes(status_bytes + b'\0' + diff_bytes + b'\0' + canonical(untracked)),
            })
        else:
            row.update({'dirty': None, 'untrackedFileCount': None, 'stateSha256': None})
        result.append(row)
    return result


def registered_paths(bare):
    """Read registrations without repeatedly hashing the remaining worktrees."""
    return {
        line.partition(' ')[2]
        for line in run_git(bare, 'worktree', 'list', '--porcelain').decode().splitlines()
        if line.startswith('worktree ') and line.partition(' ')[2] != bare
    }


def allowed_temp(path):
    return os.path.dirname(path) == '/tmp' and TEMP_NAME.fullmatch(os.path.basename(path)) is not None


def validate_inventory(inventory):
    require({item['path'] for item in inventory['taskRoots']} == set(ROOTS), 'Task roots differ from the hard-coded ownership inventory')
    paths = sorted({exact_path(item['path']) for item in inventory['taskTemporaryPaths']})
    require(all(allowed_temp(path) for path in paths), 'Unexpected temporary cleanup path')
    require(not set(paths).intersection({EXECUTABLE, ACCEPTANCE, STATE, STATE_TMP}), 'Control files must not be ordinary temporary targets')
    return paths


def mount_guard(targets):
    # Refuse a nested mount instead of crossing into a separately mounted resource.
    for line in Path('/proc/self/mountinfo').read_text().splitlines():
        mounted = line.split()[4]
        for encoded, decoded in [('\\040', ' '), ('\\011', '\t'), ('\\134', '\\')]:
            mounted = mounted.replace(encoded, decoded)
        require(not any(within(mounted, target) for target in targets), 'Mounted cleanup target requires root review: ' + mounted)


def build_plan(inventory):
    temporary = validate_inventory(inventory)
    for target in [*ROOTS, *temporary]:
        if os.path.lexists(target):
            require(not os.path.islink(target), 'Top-level target unexpectedly became a symlink: ' + target)
            require(os.path.realpath(target) == target, 'Target has a symlinked ancestor: ' + target)
    mount_guard([*ROOTS, *temporary])
    worktrees = sorted((row for bare in BARES for row in git_worktrees(bare)), key=lambda row: (row['bare'], row['path']))
    listed = set(temporary)
    for row in worktrees:
        require(under_roots(row['path']) or row['path'] in listed, 'Temporary worktree is absent from the exact inventory: ' + row['path'])
    return {
        'schemaVersion': 1, 'task': TASK, 'rootRemovalOrder': list(ROOTS),
        'temporaryTargets': temporary, 'bareRepositories': list(BARES),
        'targetIdentities': {path: identity(path) for path in [*ROOTS, *temporary]},
        'worktrees': worktrees,
    }


def durable_url(value):
    parsed = urlparse(value if isinstance(value, str) else '')
    return (parsed.scheme == 'https' and parsed.netloc == 'github.com'
            and not parsed.query and not parsed.fragment
            and re.match(r'^/IzuSharp/(?:Korda|Korda-Design|Plan)/(?:blob|tree|commit)/[0-9a-f]{40}(?:/|$)', parsed.path) is not None)


def mutation_covers(path, state):
    return bool(state) and any(within(path, started) for started in state.get('startedDeletionPaths', []))


def verify_file_check(row, state=None):
    path = exact_path(row['path'])
    require(under_roots(path) or allowed_temp(path), 'Source check outside task scope: ' + path)
    require(SHA.fullmatch(row['sha256']) is not None, 'Invalid SHA-256 for ' + path)
    if not os.path.lexists(path):
        require(mutation_covers(path, state), 'Required archived source is missing: ' + path)
        return {'path': path, 'sha256': row['sha256'], 'status': 'verified-before-recorded-deletion'}
    require(os.path.isfile(path) and not os.path.islink(path), 'Source check requires a regular non-symlink file: ' + path)
    require(digest_file(path) == row['sha256'], 'Archived source bytes changed: ' + path)
    return {'path': path, 'sha256': row['sha256'], 'status': 'verified-now'}


def validate_gate(gate, helper_sha, inventory, inventory_sha, state):
    require(gate.get('schemaVersion') == 1 and gate.get('task') == TASK, 'Unknown acceptance schema/task')
    require(gate.get('accepted') is True and gate.get('allTaskDataReviewed') is True, 'Root archival acceptance has not been granted')
    require(gate.get('helperSha256') == helper_sha, 'Cleanup helper differs from the reviewed source hash')
    require(gate.get('cleanupInventorySha256') == inventory_sha, 'Cleanup inventory differs from the accepted file')
    require(gate.get('cleanupInventory') == inventory, 'Embedded cleanup inventory differs from its checked source')
    workloads = gate.get('completedWorkloads', [])
    require(len(workloads) == 2 and {row.get('provider') for row in workloads} == {'sqlite', 'postgresql'}, 'Both Go database cells must be recorded')
    require(all(row.get('completed') is True and row.get('nominalSeconds') == 1800
                and row.get('fullDurationObserved') is True for row in workloads), 'Both complete 1800-second Go cells are required')
    require(gate.get('legacyRetentionResolved') is True, 'Legacy evidence dispositions have not been resolved')
    report = gate.get('report', {})
    require(report.get('reportedToUser') is True and durable_url(report.get('url')), 'A fixed-commit report must be archived and reported first')
    archives = gate.get('archives', [])
    require(bool(archives), 'No durable archives supplied')
    covered = set()
    checked = []
    for archive in archives:
        require(durable_url(archive.get('url')), 'Archive URL must identify an immutable approved repository commit')
        require(archive.get('readbackVerified') is True and archive.get('readbackSha256') == archive.get('sha256'), 'Archive byte readback is unverified')
        covered.update(archive.get('covers', []))
        checked.append(verify_file_check(archive, state))
    require({'go-source', 'go-results', 'legacy-dispositions', 'cleanup-inventory'}.issubset(covered), 'Archive coverage is incomplete')
    sources = gate.get('sourceChecks', [])
    require(bool(sources), 'Critical source hash checks are required')
    checked.extend(verify_file_check(row, state) for row in sources)
    return checked


def process_info(pid):
    proc = Path('/proc') / str(pid)
    try:
        raw = (proc / 'stat').read_text()
        rest = raw[raw.rfind(')') + 2:].split()
        argv = (proc / 'cmdline').read_bytes().split(b'\0')
        argv = [os.fsdecode(value) for value in argv if value]
        exe = os.readlink(proc / 'exe').removesuffix(' (deleted)')
        cwd = os.readlink(proc / 'cwd').removesuffix(' (deleted)')
        script = None
        if Path(exe).name.startswith(('python', 'bash', 'sh', 'node')):
            for arg in argv[1:]:
                if arg in {'-c', '-m', '-e', '--eval'}:
                    break
                if arg.startswith('-'):
                    continue
                candidate = os.path.normpath(arg if os.path.isabs(arg) else os.path.join(cwd, arg))
                if Path(candidate).suffix in {'.py', '.sh', '.js'} and under_roots(candidate):
                    script = candidate
                break
        owned = under_roots(exe) or script is not None
        related = owned or under_roots(cwd)
        if not related:
            # A shared executable holding a task file is a blocker, never a kill target.
            for fd in (proc / 'fd').iterdir():
                try:
                    if under_roots(os.readlink(fd).removesuffix(' (deleted)')):
                        related = True
                        break
                except OSError:
                    pass
        return {'pid': pid, 'parentPid': int(rest[1]), 'startTicks': int(rest[19]),
                'exe': exe, 'cwd': cwd, 'commandName': (proc / 'comm').read_text().strip(),
                'taskOwned': owned, 'related': related}
    except (OSError, ValueError):
        return None


def process_snapshot():
    protected = {1, 2, 5, os.getpid()}
    parent = os.getppid()
    while parent > 0 and parent not in protected:
        protected.add(parent)
        info = process_info(parent)
        parent = info['parentPid'] if info else 0
    rows = []
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        row = process_info(int(entry.name))
        if row and row['related']:
            row['protected'] = row['pid'] in protected or within(row['exe'], '/opt/codex')
            rows.append(row)
    return rows


def stop_owned_process(row):
    current = process_info(row['pid'])
    if current is None:
        return dict(row, action='already-exited')
    require(current['startTicks'] == row['startTicks'] and current['exe'] == row['exe'], 'PID identity changed before signaling')
    require(current['taskOwned'] and not row['protected'], 'Refusing to signal a process without task ownership')
    require(hasattr(os, 'pidfd_open') and hasattr(signal, 'pidfd_send_signal'), 'PID-safe signaling is unavailable; stop task processes separately')
    try:
        fd = os.pidfd_open(row['pid'])
    except ProcessLookupError:
        return dict(row, action='already-exited')
    try:
        current = process_info(row['pid'])
        if current is None:
            return dict(row, action='already-exited')
        require(current['startTicks'] == row['startTicks'] and current['exe'] == row['exe'], 'PID identity changed after pidfd acquisition')
        signal.pidfd_send_signal(fd, signal.SIGTERM)
        action = 'terminated-owned-process'
        if not select.select([fd], [], [], 10)[0]:
            signal.pidfd_send_signal(fd, signal.SIGKILL)
            require(bool(select.select([fd], [], [], 5)[0]), 'Task process did not exit')
            action = 'killed-owned-process-after-term-timeout'
        return dict(row, action=action)
    except ProcessLookupError:
        return dict(row, action='already-exited')
    finally:
        os.close(fd)


def save_state(state):
    if os.path.lexists(STATE_TMP):
        value = os.lstat(STATE_TMP)
        require(stat.S_ISREG(value.st_mode) and value.st_uid == os.geteuid(), 'Unexpected state staging file identity')
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW
    descriptor = os.open(STATE_TMP, flags, 0o600)
    with os.fdopen(descriptor, 'wb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(canonical(state) + b'\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(STATE_TMP, STATE)


def begin_deletion(state, path):
    if path not in state['startedDeletionPaths']:
        state['startedDeletionPaths'].append(path)
    save_state(state)


def remove_exact(path, state):
    if not os.path.lexists(path):
        state['actions'].append({'path': path, 'action': 'already-absent'})
        save_state(state)
        return
    require(not os.path.islink(path), 'Top-level target became a symlink before deletion: ' + path)
    require(identity(path) == state['plan']['targetIdentities'][path], 'Top-level target inode changed before deletion: ' + path)
    mount_guard([path])
    begin_deletion(state, path)
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.unlink(path)
    state['actions'].append({'path': path, 'action': 'removed'})
    save_state(state)


def check_resume_plan(plan, current, state):
    require(plan['rootRemovalOrder'] == current['rootRemovalOrder'] and plan['temporaryTargets'] == current['temporaryTargets'], 'Cleanup target list changed during resume')
    for path, previous in plan['targetIdentities'].items():
        now = identity(path)
        require(now == previous or (now is None and mutation_covers(path, state)), 'Cleanup target identity changed: ' + path)
    expected = {row['path']: row for row in plan['worktrees']}
    actual = {row['path']: row for row in current['worktrees']}
    require(set(actual).issubset(expected), 'New unreviewed worktree appeared during cleanup')
    for path, row in expected.items():
        if path in actual:
            require(actual[path] == row, 'Remaining worktree changed during cleanup: ' + path)
        else:
            require(mutation_covers(path, state), 'Worktree registration disappeared without a recorded cleanup action: ' + path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', default=INVENTORY)
    parser.add_argument('--acceptance', default=ACCEPTANCE)
    parser.add_argument('--execute', action='store_true', help='Execute only after immutable archives, readback, source hashes, full Go runs and report acceptance')
    args = parser.parse_args()
    receipt = {'schemaVersion': 1, 'task': TASK, 'startedAtUtc': utc(), 'executed': False}
    state = None
    try:
        helper_sha = digest_file(__file__)
        acceptance_bytes = read_regular(args.acceptance) if os.path.lexists(args.acceptance) else None
        gate = json.loads(acceptance_bytes) if acceptance_bytes else None
        if os.path.lexists(args.inventory):
            inventory_bytes = read_regular(args.inventory)
            inventory = json.loads(inventory_bytes)
            inventory_sha = digest_bytes(inventory_bytes)
        else:
            require(bool(gate), 'Inventory is missing and no acceptance contains the frozen inventory')
            inventory = gate['cleanupInventory']
            inventory_sha = gate['cleanupInventorySha256']
        current_plan = build_plan(inventory)
        processes = process_snapshot()
        receipt.update({'helperSha256': helper_sha, 'cleanupInventorySha256': inventory_sha,
                        'plan': current_plan, 'planSha256': digest_bytes(canonical(current_plan)),
                        'processes': processes})
        if not args.execute:
            receipt.update({'status': 'dry-run-no-mutation', 'executionCopyRequired': EXECUTABLE,
                            'acceptanceRequired': ACCEPTANCE,
                            'note': 'No source, worktree, process, cache or directory was changed.'})
            print(json.dumps(receipt, indent=2))
            return 0

        require(os.path.abspath(__file__) == EXECUTABLE and not os.path.islink(EXECUTABLE), 'Execution must use the reviewed external helper copy')
        require(os.path.abspath(args.acceptance) == ACCEPTANCE, 'Execution acceptance path must be the exact external task file')
        require(os.path.abspath(args.inventory) == INVENTORY, 'Execution inventory path must be the exact task inventory')
        require(bool(gate), 'No archival acceptance file exists')
        require(shutil.rmtree.avoids_symlink_attacks, 'Symlink-resistant recursive deletion is required')
        gate_sha = digest_bytes(acceptance_bytes)
        if os.path.lexists(STATE):
            state = json.loads(read_regular(STATE))
            require(state.get('archivalChecksPassed') is True and state.get('task') == TASK,
                    'Incomplete or foreign cleanup state')
            require(state.get('acceptanceSha256') == gate_sha and state.get('helperSha256') == helper_sha,
                    'Resume acceptance/helper differs from the initial verified cleanup')
            plan = state['plan']
            check_resume_plan(plan, current_plan, state)
        else:
            plan = current_plan
        require(gate.get('planSha256') == digest_bytes(canonical(plan)), 'Removal plan differs from the reviewed dry run')
        verified = validate_gate(gate, helper_sha, inventory, inventory_sha, state)
        blockers = [row for row in processes if not row['protected'] and not row['taskOwned']]
        require(not blockers, 'Unknown process holds a task path; inspect dry-run process metadata before deletion')
        os.chdir('/tmp')
        before = os.statvfs('/workspace/scratch')
        if state is None:
            state = {'schemaVersion': 1, 'task': TASK, 'startedAtUtc': utc(),
                     'acceptanceSha256': gate_sha, 'helperSha256': helper_sha,
                     'archivalChecksPassed': True, 'verifiedFiles': verified, 'plan': plan,
                     'startedDeletionPaths': [], 'actions': [], 'processActions': [],
                     'filesystemAvailableBytesBefore': before.f_bavail * before.f_frsize}
            save_state(state)
        receipt['executed'] = True
        for row in processes:
            if not row['protected'] and row['taskOwned']:
                state['processActions'].append(stop_owned_process(row))
                save_state(state)
        require(not [row for row in process_snapshot() if not row['protected']], 'A task-related process remains or appeared before cleanup')

        for row in plan['worktrees']:
            bare, path = row['bare'], row['path']
            if not os.path.isdir(bare):
                require(mutation_covers(bare, state), 'Owning bare repository unexpectedly missing')
                continue
            listed = registered_paths(bare)
            if path not in listed:
                state['actions'].append({'path': path, 'action': 'worktree-already-unregistered'})
                save_state(state)
                continue
            require(identity(path) == row['identity'], 'Worktree inode changed before unregistering: ' + path)
            begin_deletion(state, path)
            # --force handles reviewed dirty/ignored task files; locks were refused above.
            run_git(bare, 'worktree', 'remove', '--force', '--', path)
            state['actions'].append({'path': path, 'action': 'git-worktree-removed-and-unregistered'})
            save_state(state)
        for bare in BARES:
            if os.path.isdir(bare):
                require(not registered_paths(bare), 'Registered worktrees remain before bare repository deletion')
        for path in plan['temporaryTargets']:
            remove_exact(path, state)
        for path in plan['rootRemovalOrder']:
            remove_exact(path, state)
        require(not any(os.path.lexists(path) for path in [*ROOTS, *plan['temporaryTargets']]), 'A task target remains after cleanup')
        after = os.statvfs('/workspace/scratch')
        receipt.update({'executed': True, 'status': 'completed', 'finishedAtUtc': utc(),
                        'acceptanceSha256': gate_sha, 'verifiedFiles': state['verifiedFiles'],
                        'actions': state['actions'], 'processActions': state['processActions'],
                        'filesystemAvailableBytesBefore': state['filesystemAvailableBytesBefore'],
                        'filesystemAvailableBytesAfter': after.f_bavail * after.f_frsize,
                        'filesystemAvailableBytesDelta': after.f_bavail * after.f_frsize - state['filesystemAvailableBytesBefore'],
                        'byteAccounting': 'Observed filesystem availability delta only; no claimed freed bytes from file-size sums or previously removed caches.',
                        'allTaskTargetsAbsent': True,
                        'sharedPlatformRuntimePreserved': True})
        # Emit no local receipt into a deleted task root. The caller must capture stdout.
        for path in (STATE_TMP, STATE, ACCEPTANCE, EXECUTABLE):
            if os.path.lexists(path):
                value = os.lstat(path)
                require(stat.S_ISREG(value.st_mode) and value.st_uid == os.geteuid(), 'Control path changed identity: ' + path)
        removed_controls = []
        for path in (STATE_TMP, STATE, ACCEPTANCE, EXECUTABLE):
            if os.path.lexists(path):
                require(stat.S_ISREG(os.lstat(path).st_mode), 'Control path changed type: ' + path)
                os.unlink(path)
                removed_controls.append(path)
        receipt['removedExternalControlFiles'] = removed_controls
        receipt.pop('plan', None)
        print(json.dumps(receipt, indent=2))
        return 0
    except Exception as error:
        receipt.update({'status': 'refused-or-partially-completed', 'finishedAtUtc': utc(),
                        'errorType': type(error).__name__, 'error': str(error),
                        'resumeStateRetained': os.path.isfile(STATE),
                        'note': 'No unverified workaround is attempted. If deletion had begun, retain this receipt and resume only with the same reviewed helper and acceptance.'})
        if state:
            receipt['actions'] = state.get('actions', [])
            receipt['processActions'] = state.get('processActions', [])
        print(json.dumps(receipt, indent=2))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
